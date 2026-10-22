# OrangeFox build for begonia

GitHub Actions builder for OrangeFox Recovery on the Xiaomi Redmi Note 8 Pro
(`begonia`).

- OrangeFox sync branch: `12.1`
- Device tree: `methylphetamine/device_xiaomi_begonia-orangefox` (`wifi-browser`)
- Lunch target: `twrp_begonia-eng`
- Output: `recovery.img` (published as an OrangeFox image)
- Brand/model: `Randi` / `Nut 8 Pro`
- Dynamic partitions + explicit EROFS/ext4 fstab + FBEv2 decryption

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

The device tree can still be overridden with the `device_branch` workflow
input; use `unified` for the previous non-WiFi build.
