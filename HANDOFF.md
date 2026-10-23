# Handoff - begonia recovery browser / OrangeFox / AERA

Last updated: 2026-10-23.

## Repositories
- Device tree: `methylphetamine/device_xiaomi_begonia-orangefox` (branch `net-fix`)
- OrangeFox builder: `methylimpse/orangefox-begonia-build` (branch `wifi-browser`)
- AERA builder: `methylimpse/aera-begonia-build` (branch `main`)

## Current heads
- Device `net-fix`: `690d28f` - browser: pass target sysroot when using distro cross compiler
- OrangeFox builder `wifi-browser`: `a11c5c6` - ci: install aarch64 glibc headers for foxkbd
- AERA builder `main`: `3e2b1d0` - ci: lower AERA memory pressure for 16 GB runner

## Active runs
- OrangeFox: `39915624600` (in progress) - builds keyboard payload + full image.
- AERA: `39915596506` (in progress) - jobs=1, recoveryimage, GOMEMLIMIT=4GiB.
- foxkbd quick check: `39914843578` (success) - static aarch64 binary uploaded.

## Verified
- OrangeFox artifact `39908261882` (pre-keyboard, successful) has:
  - Dark theme default (`style.xml` == `Dark.xml`).
  - Status bar 6 placements of `%status_info_y%+8`.
  - MT6360 torch paths `torch-light0`/`torch-light1` in recovery binary.
  - `foxbrowse`, Links2, musl curl payloads.
- `foxkbd` quick build produced a 547 KB static AArch64 binary.

## Pending
- Wait for OrangeFox `39915624600`; download and verify `foxkbd` in payload + Dark/status/torch.
- Wait for AERA `39915596506`; if runner loses communication again, reduce further (GOMEMLIMIT 3GiB, jobs 1, maybe disable ccache).
- No device testing available (no adb/fastboot).

## Notes
- Builds are performed on GitHub Actions only.
- AERA previous run `39902833430` lost runner communication (memory starvation).
