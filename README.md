# OrangeFox build for begonia

GitHub Actions builder for OrangeFox Recovery on the Xiaomi Redmi Note 8 Pro
(`begonia`).

- OrangeFox sync branch: `12.1`
- Device tree: `methylphetamine/device_xiaomi_begonia-orangefox` (`unified`)
- Lunch target: `twrp_begonia-eng`
- Output: `recovery.img` (published as an OrangeFox image)
- Brand/model: `Randi` / `Nut 8 Pro`
- Dynamic partitions + explicit EROFS/ext4 fstab + FBEv2 decryption

The workflow uses the official OrangeFox `orangefox_sync.sh` to fetch the
12.1 minimal manifest, patch it, and clone the OrangeFox recovery and vendor
trees. The begonia unified device tree is then cloned and built.

Run it from **Actions -> OrangeFox build (begonia) -> Run workflow**.
