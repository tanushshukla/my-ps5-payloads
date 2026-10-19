# My PS5 Payloads

A small, automatically updated JSON source for [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager).

## Add the source to your PS5

Open **Payload Manager → Settings → Manage Sources → Add Source** and paste:

```text
https://raw.githubusercontent.com/tanushshukla/my-ps5-payloads/main/payloads.json
```

## Included payloads (26 ELF entries)

All download links in [payloads.json](payloads.json) point directly to official third-party GitHub releases, with SHA-256 checksums. No ELF binaries are mirrored here.

### Original collection

- [Prospero Manager](https://github.com/notmaj0r/ProsperoMgr) — `ProsperoMgr.elf`
- [Orbit Store](https://github.com/saawant12/orbit-store-ps5) — `orbit_store.elf`
- [BlackBox](https://github.com/D3ATHLY/blackbox) — `blackbox.elf` (**Developer explicitly warns against launching the ELF with Payload Manager. Install its FFPKG with ShadowMount instead.**)
- [HyperHEN](https://github.com/Michele-M-Media/HYPERHEN) — versioned ELF; **check firmware compatibility carefully**
- [RESTORE_PM](https://github.com/KINGDKAK/RESTORE_PM) — `RESTORE_PM.elf`

### Additional releases missing from PS5 Payloads Atlas

- [LiveShell Engine](https://github.com/ZiZc3/LiveShell) — `liveshell.elf`; PS5 animated backgrounds
- [Kura Loader](https://github.com/NookieAI/kura) — `kura-loader-ps5.elf`; PS5 companion toolset
- [YetAnotherControllerEnabler](https://github.com/MegaCadeDev/YetAnotherControllerEnabler) — `YetAnotherControllerEnabler.elf`
- [Snes9x PS5](https://github.com/MisterTemaki/snes9xPS5) — versioned `Snes9xPS5-v*.elf`; installer/helper for its home-screen app
- [PS5 LAN Transfer](https://github.com/Uss15/ps5-lan-transfer) — `ps5-lan-transfer.elf`
- [PS5 Unified Autoloader](https://github.com/itsPLK/ps5-unified-autoloader) — versioned `ps5-unified-autoloader-v*.elf`; **startup-chain tool, not ordinary manual-launch payload**
- [PKG Sender Receiver](https://github.com/Loopayeh/pkg-sender) — `pkg-receiver.elf`; works with companion desktop app
- [PS5SX2 Installer](https://github.com/Swordpdf/PS5SX2) — `PS5SX2Installer.elf`; PS2 emulator installer
- [PS5SX2 Helper](https://github.com/Swordpdf/PS5SX2) — `PS5SXHelper.elf`; companion PS2 emulator helper
- [SwanStationPS5 Disc Daemon](https://github.com/darkxex/SwanStationPS5) — `SwanStationPS5-DiscDaemon.elf`; helper for external PS1 disc drive
- [Ruffle Flash PS5 Helper](https://github.com/ZiZc3/Ruffle-Flash-PS5) — `helper.elf`; companion emulator app required
- [PS5X360 AutoLog (Preview)](https://github.com/BrinooTk/PS5X360) — `PS5X360-AutoLog-v*.elf`; preview logging helper, not the main Xbox 360 emulator
- [PS5 Unified Autoloader X](https://github.com/bsk193/ps5-unified-autoloader-x) — versioned `ps5-unified-autoloader-x-v*.elf`; alternative startup-chain tool
- [Prospero Menu](https://github.com/StonedModder/Prospero-Menu) — `ProsperoMenu.elf`; PS5 ShellUI overlay menu, install after kstuff/ShadowMount (tested on FW 13.60)
- [Puckbridge PS5](https://github.com/ThisIsAkill/PuckbridgePS5) — `ghost-control-ps5.elf`; Ghostcontrol-derived controller tool with gyro and motion support for Steam Controller (2026), firmware 13.60 tested
- [RommPS](https://github.com/s0liton/RommPS) — `romm-sync.elf`; PS5 background RomM server game/save syncing payload (requires compatible HEN and RomM server)
- [PSCloud](https://github.com/bc160201983/ps5-cloud-save) — `pscloud-dashboard.elf`; cloud-save dashboard companion ELF
- [PS5 Linux Loader](https://github.com/soniciso1/ps5-linux-loader) — `ps5-linux-loader.elf`; Linux boot loader for supported PS5 firmware, with **experimental** 13.60/PS5 Pro support. Requires Linux media and upstream setup instructions. Kernel packages from [ps5-linux-patches](https://github.com/ps5-linux/ps5-linux-patches) are not ELF payloads and are not included.
- [PS5 NZB Downloader](https://github.com/lchmagKekse/PS5-NZB-Downloader) — `ps5_nzb_downloader_v*.elf`; experimental prerelease NZB/Usenet downloader with web UI on port 4202; requires a Usenet provider and jailbroken PS5. Only download content you are authorized to access.
- [PS4Mount](https://github.com/gasb07/ps4mount) — `ps4mount.elf`; run PS4 fake PKGs from exFAT USB on a jailbroken PS5; latest v0.6.0. **Experimental: may trigger PS5 database corruption/rebuild prompts; back up save data. Do not use v0.3.1 on firmware below 6.00.**
- [ezRemote Server](https://github.com/cy33hc/ps5-ezremote-server) — `ezremote-server.elf`; PS5 background payload for the separate [ezRemote Client](https://github.com/cy33hc/ps5-ezremote-client) homebrew app, enabling remote package installations. ezRemote Client can auto-start the server; avoid launching duplicate instances.

**Payload Manager catalog entries are not safety endorsements.** Some ELFs install or support separate home-screen applications, some are experimental, and others are only appropriate as jailbreak bootstrap components. Read upstream instructions and verify console/firmware compatibility.

## Automatic updates

[GitHub Actions](.github/workflows/update-payloads.yml) checks the latest stable releases for **the tracked upstream projects** every hour (at minute 23 UTC). When a release changes, [update_payloads.py](update_payloads.py) updates `payloads.json`:

- release tag/version;
- ELF download URL and filename;
- release date;
- SHA-256 checksum (from the GitHub release asset digest, or calculated from the binary if needed).

An update is only committed when the manifest changes. If GitHub is unavailable or a checksum cannot be determined, the job fails without publishing partial changes. If a new upstream release does not include an expected companion ELF, that entry is left unchanged while other projects can still update. Each run checks for duplicate filenames to prevent Payload Manager install collisions.

### Run the check immediately

1. Open the [Actions tab](https://github.com/tanushshukla/my-ps5-payloads/actions).
2. Select **Update PS5 payload releases**.
3. Choose **Run workflow** → **Run workflow** on `main`.

If an update job cannot push changes due to permissions, check **Settings → Actions → General → Workflow permissions** and allow read/write access to the `GITHUB_TOKEN` for this repository.

GitHub scheduled runs may be delayed and can be disabled after long inactivity on public repositories. Re-enable the workflow in **Actions** if GitHub pauses it.

**Note:** Updating the JSON does *not* install or run an update on your PS5. Refresh the catalog in Payload Manager and update installed payloads there. Only download and run homebrew you trust.
