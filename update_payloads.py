#!/usr/bin/env python3
"""Refresh PS5 Payload Manager metadata from official GitHub releases.

Only the two configured upstream repositories are trusted; binaries are never
committed here. A release must expose the exact expected ELF asset.
"""

import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

CATALOG = Path(__file__).with_name("payloads.json")
SOURCES = {
    "prosperomgr": ("notmaj0r/ProsperoMgr", "ProsperoMgr.elf"),
    "orbit-store": ("saawant12/orbit-store-ps5", "orbit_store.elf"),
}
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
        return json.load(response)


def sha256_for_asset(asset):
    digest = asset.get("digest") or ""
    if re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
        return digest.split(":", 1)[1].lower()

    # Older GitHub release assets may have no digest. Compute it rather than
    # publishing an unverified checksum. Streaming avoids buffering the ELF.
    url = asset["browser_download_url"]
    request = urllib.request.Request(url, headers={"User-Agent": "my-ps5-payloads-updater"})
    hasher = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(request, timeout=90) as response:
        while chunk := response.read(1024 * 1024):
            count += len(chunk)
            if count > MAX_BINARY_SIZE:
                raise ValueError(f"Release asset exceeds {MAX_BINARY_SIZE} bytes: {url}")
            hasher.update(chunk)
    if not count:
        raise ValueError(f"Empty ELF download: {url}")
    return hasher.hexdigest()


def refresh(catalog):
    payloads = catalog["payloads"]
    by_id = {item["id"]: item for item in payloads}
    if len(by_id) != len(payloads):
        raise ValueError("Duplicate payload ids in catalog")

    for ident, (repo, expected_elf) in SOURCES.items():
        if ident not in by_id:
            raise ValueError(f"Missing expected payload entry: {ident}")
        release = latest_release(repo)
        if release.get("draft") or release.get("prerelease"):
            raise ValueError(f"Unexpected draft/prerelease returned by GitHub for {repo}")
        tag = release.get("tag_name")
        if not isinstance(tag, str) or not tag:
            raise ValueError(f"Release tag missing for {repo}")
        assets = [a for a in release.get("assets", []) if a.get("name") == expected_elf]
        if len(assets) != 1:
            raise ValueError(f"Expected exactly one {expected_elf} in {repo} release {tag}")
        asset = assets[0]
        url = asset.get("browser_download_url", "")
        if not url.startswith(f"https://github.com/{repo}/releases/download/"):
            raise ValueError(f"Unexpected download URL for {repo}: {url}")
        checksum = sha256_for_asset(asset)
        item = by_id[ident]
        item.update(
            filename=expected_elf,
            url=url,
            version=tag,
            last_update=(release.get("published_at") or "")[:10],
            checksum=checksum,
        )
        print(f"{item['name']}: {tag} ({expected_elf})")
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
