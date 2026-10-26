#!/usr/bin/env python3
"""Put the begonia maintainer/builder credit on the OrangeFox About page.

The OrangeFox source tree is synced fresh for every build, so the maintainer
name, profile picture and handle are applied after the sync instead of being
committed to the upstream theme.  The recovery reads OF_MAINTAINER from the
device product makefile and shows it in Settings -> About -> Maintainer.

usage: patch_maintainer.py <path/to/aosp>
"""

import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NAME = "A X"
ROLE = "Maintainer &amp; Builder"
HANDLE = "@methylphetamine"

# The stock card ends with the translated "Maintainer" line.  Keep that line
# for the role, then add the handle one line lower (cardtxt_8 already exists
# in vars.xml for this four-card layout).
OLD_ROLE = '''\t\t\t<text style="about_info">
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="3"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="2"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="1"/>
\t\t\t\t<placement x="%card_txt_x%" y="%cardtxt_7%"/>
\t\t\t\t<text>{@abt_maintainer}</text>
\t\t\t</text>'''

NEW_ROLE = f'''\t\t\t<text style="about_info">
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="3"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="2"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="1"/>
\t\t\t\t<placement x="%card_txt_x%" y="%cardtxt_7%"/>
\t\t\t\t<text>{ROLE}</text>
\t\t\t</text>

\t\t\t<text style="about_info">
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="3"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="2"/>
\t\t\t\t<condition var1="of_maintainer" op="!=" var2="1"/>
\t\t\t\t<placement x="%card_txt_x%" y="%cardtxt_8%"/>
\t\t\t\t<text>{HANDLE}</text>
\t\t\t</text>'''


def set_maintainer(device_mk: Path) -> None:
    lines = device_mk.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith("OF_MAINTAINER") and ":=" in line:
            lines[i] = f"OF_MAINTAINER := {NAME}"
            found = True

    if not found:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([
            "# Shown in Settings -> About -> Maintainer.",
            f"OF_MAINTAINER := {NAME}",
        ])

    device_mk.write_text("\n".join(lines) + "\n")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_maintainer.py <path/to/aosp>")

    src = Path(sys.argv[1])
    repo = Path(__file__).resolve().parent.parent
    asset = repo / "assets" / "maintainer.png"
    theme = src / "bootable/recovery/gui/theme/portrait_hdpi"
    settings = theme / "pages/settings.xml"
    device_mk = src / "device/xiaomi/begonia/fox_begonia.mk"

    for path in (asset, settings, device_mk):
        if not path.is_file():
            raise SystemExit(f"missing file: {path}")

    set_maintainer(device_mk)

    shutil.copyfile(asset, theme / "images/Default/About/maintainer.png")

    xml = settings.read_text()
    if HANDLE not in xml:
        if xml.count(OLD_ROLE) != 1:
            raise SystemExit(
                f"expected exactly one maintainer card in {settings}, "
                f"found {xml.count(OLD_ROLE)}"
            )
        xml = xml.replace(OLD_ROLE, NEW_ROLE, 1)
        settings.write_text(xml)

    # A malformed theme is a boot-time failure; catch it here instead.
    ET.parse(settings)

    print(f"maintainer : {NAME}")
    print(f"role       : {ROLE.replace('&amp;', '&')}")
    print(f"handle     : {HANDLE}")
    print(f"picture    : {asset.name} -> {theme / 'images/Default/About/maintainer.png'}")
    print(f"device mk  : OF_MAINTAINER := {NAME}")


if __name__ == "__main__":
    main()
