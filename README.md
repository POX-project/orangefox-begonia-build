<p align="center">
  <a href="https://github.com/methylphetamine">
    <img src="https://github.com/methylphetamine.png?size=200" width="120" height="120" alt="A X">
  </a>
</p>

<h3 align="center">A X</h3>

<p align="center">
  <strong>Maintainer &amp; Builder</strong><br>
  <a href="https://github.com/methylphetamine">@methylphetamine</a>
</p>

---

# OrangeFox build for begonia

GitHub Actions builder for OrangeFox Recovery on the Xiaomi Redmi Note 8 Pro
(`begonia`).

- OrangeFox sync branch: `12.1`
- Device tree: `POX-project/device_xiaomi_begonia-orangefox` (`unified`)
- Lunch target: `twrp_begonia-eng`
- Output: `recovery.img` (published as an OrangeFox image)
- Brand/model: `Randi` / `Nut 8 Pro`
- Dynamic partitions + explicit EROFS/ext4 fstab + FBEv2 decryption

The workflow uses the official OrangeFox `orangefox_sync.sh` to fetch the
12.1 minimal manifest, patch it, and clone the OrangeFox recovery and vendor
trees. The begonia unified device tree is then cloned and built.

Run it from **Actions -> OrangeFox build (begonia) -> Run workflow**.
