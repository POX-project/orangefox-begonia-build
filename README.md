# OrangeFox build for begonia

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/328056449?v=4" width="100" height="100" alt="Builder" style="border-radius: 50%;">
</p>

<p align="center">
  <strong>Builder & Maintainer:</strong> <a href="https://github.com/${ghuser}">${ghuser}</a>
</p>

GitHub Actions builder for OrangeFox Recovery on the Xiaomi Redmi Note 8 Pro
(`begonia`).

- OrangeFox sync branch: `12.1`
- Device tree: `${ghuser}/device_xiaomi_begonia-orangefox` (`wifi-browser`)
- Lunch target: `twrp_begonia-eng`
- Outputs: `recovery.img` and the official OrangeFox installer ZIP
  `OrangeFox-R12.0-Unofficial-begonia.zip` (includes the default `sdcard/Fox`
  tools/extras)
- Brand/model: `Randi` / `Nut 8 Pro`
- Dynamic partitions + explicit EROFS/ext4 fstab + runtime FBE v1/v2
  decryption (the installed ROM's vendor fstab and the actual `/data/misc`
  policy are detected, including metadata/wrapped-key ROMs)

The workflow uses the official OrangeFox `orangefox_sync.sh` to fetch the
12.1 minimal manifest, patch it, and clone the OrangeFox recovery and vendor
trees. The begonia unified device tree is then cloned and built.

Run it from **Actions -> OrangeFox build (begonia) -> Run workflow**.

## `wifi-browser` branch

This branch builds the `wifi-browser` device tree, which adds MediaTek WiFi
and a browser dashboard to recovery:

- `wpa_supplicant`/`wpa_cli` are built from the 12.1 tree and copied into the
  recovery ramdisk.
- The workflow disables `CONFIG_CTRL_IFACE_HIDL` in
  `external/wpa_supplicant_8/wpa_supplicant/android.config` so `wpa_cli` can
  use the unix control socket.
- MediaTek WMT firmware, `wmt_loader`, `wmt_launcher`, `wlan_assistant`,
  `dhcpcd`, a static BusyBox and the dashboard are packed from the device
  tree's `recovery/root`.
- `wget` is exposed from BusyBox, and the workflow clones `external/curl`
  (removed by the minimal manifest) so the recovery build can relink a real
  `curl` into `/system/bin`. HTTPS curl traffic validates against the CA
  bundle packed at `/system/etc/security/cacert.pem`.
- The image is rejected if it exceeds the 64 MB (`67108864` byte) recovery
  partition.
- The build's official OrangeFox installer ZIP is published unchanged. It
  contains the installer `META-INF`, `recovery.img`, and the default
  `sdcard/Fox` tools/extras (`FoxFiles`, Magisk/uninstall zips, and AromaFM).
  The workflow checks the ZIP integrity and required entries, confirms the
  tools are present, and verifies that the embedded `recovery.img` is
  byte-identical to the image checked above. The ZIP is uploaded as the
  `orangefox-begonia-flashable` artifact alongside the
  `orangefox-begonia-recovery` image artifact. Only the embedded image needs to
  fit the 64 MiB partition; the installer ZIP is about 74 MB, so Telegram falls
  back to a download link.

## Decryption (FBE v1 and v2)

The recovery no longer hard-codes one FBE generation:

1. TWRP parses the installed ROM's `/vendor/etc/fstab.<hardware>` for `/data`
   and `/metadata`. That ROM-side fstab is the authoritative source for the
   policy version, metadata encryption, key directory and wrapped-key flags.
   The `recovery.fstab` userdata lines are only a fallback.
2. The build patches vold to prefer `/etc/additional.fstab` (TWRP's copy of
   the vendor fstab) when installing the DE/CE keys.
3. As a safety net, vold reads the policy actually installed on `/data/misc`.
   If it is v1, vold overrides the fstab version and disables v2-only
   hardware-wrapped keys / `IV_INO_LBLK_32`; if it is v2, the ROM's v2 options
   are kept. The detected version is cached for the rest of the recovery
   session.

This supports the legacy v1 data on the stock/current begonia ROMs and modern
v2 data, including Android 16 custom ROMs that use metadata encryption. A
ROM's vendor fstab still has to describe its own crypto layout correctly; the
recovery cannot recover a key that neither the keymaster nor the ROM metadata
provides.

The device tree can still be overridden with the `device_branch` workflow
input; use `unified` for the previous non-WiFi build.
