# Handoff - begonia recovery browser / OrangeFox / AERA

Last updated: 2026-10-23 07:20 UTC.

All builds run on GitHub Actions. Do not build locally: the sandbox has 2 cores,
and every result here comes from a workflow run.

## Repositories

| repo | branch | head | notes |
|---|---|---|---|
| `methylphetamine/device_xiaomi_begonia-orangefox` | `net-fix` | see `git log` | recovery WiFi + Links2 + musl curl + `foxkbd` payload |
| `methylphetamine/orangefox-begonia-build` | `wifi-browser` | see `git log` | `build.yml` (full build) + `foxkbd.yml` (1 min check) |
| `methylphetamine/aera-begonia-build` | `main` | see `git log` | Android 16 / AERA recovery |

The account is **`methylphetamine`** (15 chars, id `328056449`). A misspelled
owner resolves to *Repository not found* and looks like an auth failure.

## foxkbd: prebuilt (fixed 2026-10-23)

Run `39915624600` failed in *Install build dependencies*:

```
gcc-11-aarch64-linux-gnu : Conflicts: gcc-multilib but 4:11.2.0-1ubuntu1 is to be installed
gcc-multilib : Conflicts: gcc-11-aarch64-linux-gnu but 11.4.0-1ubuntu1~22.04.3cross1 is to be installed
E: Unable to correct problems, you have held broken packages.
```

The OrangeFox host tools need `gcc-multilib`, so the distro aarch64 cross
compiler cannot be installed in the same job. `foxkbd` is therefore committed as
a **prebuilt** at `recovery/root/system/bin/foxkbd` (559,888 B, static AArch64,
sha256 `9b198d96…`), and the full build only verifies it. See
`tools/FOXKBD.md` in the device tree for provenance and the rebuild recipe.

Rebuilds go through `.github/workflows/foxkbd.yml`, which installs only
`clang` + `libc6-dev-arm64-cross` + `libgcc-11-dev-arm64-cross` and uses
`clang --target=aarch64-linux-gnu --sysroot=/usr/aarch64-linux-gnu`
(`tools/build-foxkbd.sh`). That path produces an equivalent static binary. The
full build's apt list is back to the known-good set that produced the green
`39908261882`.

## Status

- OrangeFox full build `39915624600` (device tree `net-fix`, `jobs=2`): failed in
  11 s at apt, cause above. Nothing was synced or compiled.
- OrangeFox `39908261882` (pre-keyboard, `net-fix`) was green. Verified in the
  artifact: dark theme default, status bar kept at top, MT6360 torch paths
  `torch-light0`/`torch-light1`, `foxbrowse` + Links2 + musl curl payload.
- AERA `39915596506` (`3e2b1d0`, `jobs=1`, `GOMEMLIMIT=4GiB`): running.
- AERA `39902833430` (`59b50d6`) lost the runner again during Compile: the step
  stayed `in_progress`, the run was only finalized as failure after ~2 h, and no
  compile diagnostic was produced. Memory pressure, not the compiler.

## Pending

1. Confirm `foxkbd.yml` is green on the new toolchain path.
2. Dispatch the full OrangeFox build (`device_branch=net-fix`, `jobs=2`) and
   verify `foxkbd` is in the ramdisk and that the ZIP stays within the 64 MB
   recovery partition.
3. Watch AERA `39915596506`; if the runner dies again, reduce further
   (GOMEMLIMIT 3 GiB, no ccache) and treat 16 GB hosted runners as unsuitable
   for AOSP 16.
4. No device testing available (no adb/fastboot) - the on-device checklist in
   the handoff repo still applies.
