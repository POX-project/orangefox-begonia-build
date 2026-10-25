# Handoff - begonia recovery browser / OrangeFox / AERA

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/328056449?v=4" width="80" height="80" alt="Builder" style="border-radius: 50%;">
</p>

<p align="center">
  <strong>Builder & Maintainer:</strong> <a href="https://github.com/methylphetamine">methylphetamine</a>
</p>

Last updated: 2026-10-25 10:00 UTC.

All builds run on GitHub Actions. Do not build locally: the sandbox has 2 cores,
and every result here comes from a workflow run.

## Repositories

| repo | branch | notes |
|---|---|---|
| `methylphetamine/device_xiaomi_begonia-orangefox` | `net-fix` | recovery WiFi + NetSurf (`foxbrowse`) + musl curl + `foxkbd` |
| `methylphetamine/orangefox-begonia-build` | `wifi-browser` | `build.yml` (full build) + `foxkbd.yml` (1 min check) |
| `methylphetamine/aera-begonia-build` | `main` | Android 16 / AERA recovery |

The account is **`methylphetamine`** (15 chars, id `328056449`). A misspelled
owner resolves to *Repository not found* and looks like an auth failure.

## Status (2026-10-25)

- OrangeFox full build `40171521596` (`wifi-browser`, device tree `net-fix`):
  **green**. It produced `recovery.img` (fits the 64 MiB partition), the
  official installer ZIP and the enhanced NetSurf ZIP, and the build-time
  checks confirmed `netsurf-fb` is a static AArch64 binary inside the ramdisk.
- `foxkbd.yml` has not been needed since the NetSurf switch; `foxkbd` is no
  longer part of the ramdisk.
- AERA `39915596506`: see the AERA repo; not touched today.

## Browser (`foxbrowse`)

NetSurf 3.11 (static AArch64, Duktape JS, framebuffer + built-in on-screen
keyboard) replaced Links2. `foxkbd` and the Links2 payload are gone.

Fixed today, after the report that `foxbrowse` exited immediately ("crash") and
that the enhanced ZIP was missing:

1. **Resources were never found.** NetSurf's compiled-in resource path is the
   build tree (`/tmp/opencode/ns-install/share/netsurf`), so on the device it
   loaded no `Messages`, no `default.css` and no `Choices`. The launcher now
   exports `NETSURFRES=/system/etc/foxbrowse/netsurf`.
2. **`HOME` was `/tmp`**, which also holds the recovery logs. It is now a
   dedicated `/tmp/foxbrowse-home` with `$HOME/.netsurf` pre-created.
3. **Geometry is now explicit.** The launcher reads
   `/sys/class/graphics/fb0/virtual_size` and `bits_per_pixel` and passes
   `-w/-h/-b`, then retries once with auto-detection if NetSurf still fails.
   A wrong bpp/geometry makes the framebuffer surface fail instantly.
4. **Failures are visible.** `foxbrowse` writes to `/tmp/foxbrowse.log`,
   `/tmp/recovery.log` (Advanced -> View log) and `/dev/kmsg`, instead of
   letting the error die in the pty that is hidden while the GUI is stopped.
5. **Pre-flight check.** If neither `/dev/graphics/fb0` nor `/dev/fb0` exists,
   the launcher reports and exits without freezing the GUI (no more
   freeze/resume flicker that looks like a crash).
6. **Fonts.** `fonts.conf` lists `/system/etc/foxbrowse/fonts` (the shipped
   DejaVu set) before `/twres/fonts`, so the browser never depends on the
   theme font set.

New commands:

```sh
foxbrowse --diag       # framebuffer, geometry, input, resources, fonts, CA
foxbrowse --selftest   # headless 3 s run on the ram surface
```

If the browser still fails on the device, `foxbrowse --diag` plus
`/tmp/foxbrowse.log` describe the exact state; the log now survives the run.

## Enhanced ZIP

`tools/create-arorafm-zip.sh` (device tree) derives the enhanced installer from
the official ZIP: same `META-INF` and byte-identical `recovery.img`, plus the
NetSurf userspace files under `sdcard/Fox/FoxFiles/NetSurf/`, re-signed with
the AOSP testkey.

The file used to exist **only** as a 30-day Actions artifact, which is why it
looked missing. The workflow now also:

- uploads it to Gofile (`enhanced_url`),
- posts it to Telegram (document when it fits, otherwise a link),
- attaches it to the GitHub release when `publish_release` is enabled.

The stale `scripts/create-arorafm-zip.sh` in the builder repo (it used `ncp`
and a non-existent `ofox-net/` tree, and could never succeed) was deleted; the
device-tree script is the only implementation.

## Pending

1. Re-run the full build and confirm `foxbrowse` on the device (WiFi dashboard
   -> terminal: `foxbrowse --diag`, then `foxbrowse`).
2. Confirm both ZIPs land in Gofile/Telegram, and in the release when
   `publish_release` is set.
3. No device testing available (no adb/fastboot) - the on-device checklist in
   the handoff repo still applies.
