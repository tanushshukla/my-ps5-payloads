#!/usr/bin/env python3
"""Refresh official PS5 ELF release metadata in payloads.json.

Upstream binaries are never mirrored or committed here.
Each catalog entry is explicitly tied to one trusted GitHub repository and
one expected ELF filename pattern; releases without that asset are skipped.
"""

import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

CATALOG = Path(__file__).with_name("payloads.json")
SOURCES = {
    "prosperomgr": ("notmaj0r/ProsperoMgr", r"ProsperoMgr\.elf"),
    "orbit-store": ("saawant12/orbit-store-ps5", r"orbit_store\.elf"),
    "blackbox": ("D3ATHLY/blackbox", r"blackbox\.elf"),
    "hyperhen": ("Michele-M-Media/HYPERHEN", r"HyperHEN[-_]v\d+(?:[._]\d+)+\.elf"),
    "restore_pm": ("KINGDKAK/RESTORE_PM", r"RESTORE_PM\.elf"),
    "liveshell": ("ZiZc3/LiveShell", r"liveshell\.elf"),
    "kura-loader": ("NookieAI/kura", r"kura-loader-ps5\.elf"),
    "controller-enabler": ("MegaCadeDev/YetAnotherControllerEnabler", r"YetAnotherControllerEnabler\.elf"),
    "snes9x-ps5": ("MisterTemaki/snes9xPS5", r"Snes9xPS5[-_]v[\da-z._-]+\.elf"),
    "ps5-lan-transfer": ("Uss15/ps5-lan-transfer", r"ps5-lan-transfer\.elf"),
    "unified-autoloader": ("itsPLK/ps5-unified-autoloader", r"ps5-unified-autoloader-v[\da-z._-]+\.elf"),
    "pkg-receiver": ("Loopayeh/pkg-sender", r"pkg-receiver\.elf"),
    "ps5sx2-installer": ("Swordpdf/PS5SX2", r"PS5SX2Installer\.elf"),
    "ps5sx2-helper": ("Swordpdf/PS5SX2", r"PS5SXHelper\.elf"),
    "swanstation-disc-daemon": ("darkxex/SwanStationPS5", r"SwanStationPS5-DiscDaemon\.elf"),
    "ruffle-flash-helper": ("ZiZc3/Ruffle-Flash-PS5", r"helper\.elf"),
    "ps5x360-autolog": ("BrinooTk/PS5X360", r"PS5X360-AutoLog-[\da-z._-]+\.elf"),
    "unified-autoloader-x": ("bsk193/ps5-unified-autoloader-x", r"ps5-unified-autoloader-x-v[\da-z._-]+\.elf"),
    "prospero-menu": ("StonedModder/Prospero-Menu", r"ProsperoMenu\.elf"),
    "puckbridge-ps5": ("ThisIsAkill/PuckbridgePS5", r"ghost-control-ps5\.elf"),
    "romm-sync": ("s0liton/RommPS", r"romm-sync\.elf"),
    "ps5-linux-loader": ("soniciso1/ps5-linux-loader", r"ps5-linux-loader\.elf"),
}
PS_CLOUD_REPOSITORY = "bc160201983/ps5-cloud-save"
MAX_BINARY_SIZE = 512 * 1024 * 1024


def latest_release(repository):
    url = f"https://api.github.com/repos/{repository}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "my-ps5-payloads-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    if release.get("draft") or release.get("prerelease"):
        raise ValueError(f"Nonstable release returned for {repository}")
    if not release.get("tag_name"):
        raise ValueError(f"Missing release tag for {repository}")
    return release


def sha256_for_asset(asset):
    digest = asset.get("digest") or ""
    if re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
        return digest.split(":", 1)[1].lower()

    # GitHub sometimes omits asset digests; stream the binary to hash it.
    url = asset["browser_download_url"]
    request = urllib.request.Request(
        url, headers={"User-Agent": "my-ps5-payloads-updater"}
    )
    hasher = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(request, timeout=90) as response:
        while chunk := response.read(1024 * 1024):
            count += len(chunk)
            if count > MAX_BINARY_SIZE:
                raise ValueError(f"Asset exceeds 512 MB limit: {url}")
            hasher.update(chunk)
    if not count:
        raise ValueError(f"Empty ELF download: {url}")
    return hasher.hexdigest()


def version_from_asset(ident, asset_name, tag):
    if ident == "hyperhen":
        match = re.fullmatch(
            r"HyperHEN[-_]v(\d+(?:[._]\d+)+)\.elf", asset_name, re.IGNORECASE
        )
        return "v" + match.group(1).replace("_", ".")
    return tag


def refresh(catalog):
    by_id = {}
    for item in catalog["payloads"]:
        ident = item["id"]
        if ident in by_id:
            raise ValueError(f"Duplicate payload id: {ident}")
        by_id[ident] = item

    if set(SOURCES) - set(by_id):
        raise ValueError(f"Missing manifest entries: {sorted(set(SOURCES) - set(by_id))}")

    # PS5SX2 supplies two distinct payloads from the same release.
    # Cache API results per upstream repository to reduce GitHub rate usage.
    releases = {}
    for ident, (repository, pattern) in SOURCES.items():
        release = releases.get(repository)
        if release is None:
            try:
                release = latest_release(repository)
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
                print(
                    f"WARNING: {ident}: no latest stable release for "
                    f"{repository} (HTTP 404); keeping previous entry",
                    file=sys.stderr,
                )
                continue
            releases[repository] = release
        matches = [
            asset for asset in release.get("assets", [])
            if re.fullmatch(pattern, asset.get("name") or "", re.IGNORECASE)
        ]
        if len(matches) != 1:
            # A new upstream release may temporarily omit a companion helper.
            # Preserve its previous working link without blocking all updates.
            print(
                f"WARNING: {ident}: found {len(matches)} matching ELF assets "
                f"in {repository} release {release['tag_name']}; keeping previous entry",
                file=sys.stderr,
            )
            continue
        asset = matches[0]
        url = asset.get("browser_download_url", "")
        expected_prefix = f"https://github.com/{repository}/releases/download/"
        if not url.lower().startswith(expected_prefix.lower()):
            raise ValueError(f"Unexpected download URL for {ident}: {url}")
        filename = asset["name"]
        checksum = sha256_for_asset(asset)
        version = version_from_asset(ident, filename, release["tag_name"])
        item = by_id[ident]
        item.update(
            filename=filename,
            url=url,
            version=version,
            last_update=(release.get("published_at") or "")[:10],
            checksum=checksum,
        )
        print(f"{item['name']}: {version} ({filename})")

    # Include every official PSCloud ELF asset as its own catalog entry.
    release = releases.get(PS_CLOUD_REPOSITORY) or latest_release(PS_CLOUD_REPOSITORY)
    for asset in release.get("assets", []):
        filename = asset.get("name") or ""
        if not re.fullmatch(r"pscloud-[a-z0-9_-]+\.elf", filename, re.IGNORECASE):
            continue
        ident = filename[:-4].lower().replace("_", "-")
        url = asset.get("browser_download_url", "")
        prefix = f"https://github.com/{PS_CLOUD_REPOSITORY}/releases/download/"
        if not url.lower().startswith(prefix.lower()):
            raise ValueError(f"Unexpected PSCloud URL: {url}")
        checksum = sha256_for_asset(asset)
        item = by_id.get(ident)
        if item is None:
            role = ident.removeprefix("pscloud-").replace("-", " ").title()
            item = {
                "id": ident, "name": f"PSCloud {role}", "filename": filename,
                "url": url,
                "description": f"Official PSCloud {role.lower()} ELF; consult upstream documentation for usage.",
                "version": release["tag_name"],
                "last_update": (release.get("published_at") or "")[:10],
                "category": "Utilities & Tools", "checksum": checksum,
                "author": "bc160201983",
                "source": f"https://github.com/{PS_CLOUD_REPOSITORY}",
                "details_url": f"https://github.com/{PS_CLOUD_REPOSITORY}/releases",
            }
            catalog["payloads"].append(item)
            by_id[ident] = item
        else:
            item.update(filename=filename, url=url, version=release["tag_name"],
                        last_update=(release.get("published_at") or "")[:10],
                        checksum=checksum)
        print(f"{item['name']}: {release['tag_name']} ({filename})")

    filenames = [item["filename"].lower() for item in catalog["payloads"]]
    if len(filenames) != len(set(filenames)):
        raise ValueError("Filename collision across payloads; refusing to publish")
    return catalog


def main():
    original = CATALOG.read_text(encoding="utf-8")
    updated = refresh(json.loads(original))
    output = json.dumps(updated, indent=2, ensure_ascii=False) + "\n"
    if output != original:
        CATALOG.write_text(output, encoding="utf-8")
        print("payloads.json updated")
    else:
        print("Already up to date")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Update failed; catalog left unchanged: {exc}", file=sys.stderr)
        sys.exit(1)
