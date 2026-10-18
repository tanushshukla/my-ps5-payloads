# My PS5 Payloads

A small, automatically updated JSON source for [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager).

## Add the source to your PS5

Open **Payload Manager → Settings → Manage Sources → Add Source** and paste:

```text
https://raw.githubusercontent.com/tanushshukla/my-ps5-payloads/main/payloads.json
```

## Included payloads

- **Prospero Manager:** [notmaj0r/ProsperoMgr](https://github.com/notmaj0r/ProsperoMgr) — `ProsperoMgr.elf`
- **Orbit Store (browser ELF):** [saawant12/orbit-store-ps5](https://github.com/saawant12/orbit-store-ps5) — `orbit_store.elf`
- **BlackBox:** [D3ATHLY/blackbox](https://github.com/D3ATHLY/blackbox) — `blackbox.elf` (listed for reference; **upstream warns not to run the ELF in Payload Manager**. Install `PPSA01453.ffpkg` with ShadowMount instead.)

The manifest contains download links to the developers' official GitHub Release assets. No ELF binaries are mirrored by this repository.

## Automatic updates

[GitHub Actions](.github/workflows/update-payloads.yml) checks all three projects' **latest stable releases** every hour (at minute 23 UTC). When a release changes, [update_payloads.py](update_payloads.py) updates `payloads.json`:

- release tag/version;
- ELF download URL and filename;
- release date;
- SHA-256 checksum (from the GitHub release asset digest, or calculated from the binary if needed).

An update is only committed when the manifest changes. If GitHub is unavailable, the expected ELF is missing, or a checksum cannot be determined, the job fails rather than replacing the valid catalog with incomplete metadata.

### Run the check immediately

1. Open the [Actions tab](https://github.com/tanushshukla/my-ps5-payloads/actions).
2. Select **Update PS5 payload releases**.
3. Choose **Run workflow** → **Run workflow** on `main`.

If an update job cannot push changes due to permissions, check **Settings → Actions → General → Workflow permissions** and allow read/write access to the `GITHUB_TOKEN` for this repository.

GitHub scheduled runs may be delayed and can be disabled after long inactivity on public repositories. Re-enable the workflow in **Actions** if GitHub pauses it.

**Note:** Updating the JSON does *not* install or run an update on your PS5. Refresh the catalog in Payload Manager and update installed payloads there. Only download and run homebrew you trust.
