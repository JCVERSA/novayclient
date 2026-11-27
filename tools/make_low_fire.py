#!/usr/bin/env python3
"""
Build the optional Low Fire variant.

Why this script exists
----------------------
A low-fire pack has to start from the game's own animated flame strip, because
the flame is 32 hand-drawn frames of 16x16 and re-drawing it would change the
look of fire rather than reduce it. Novayclient therefore must NOT ship that
artwork: the vanilla assets are Mojang's.

So the release pack ships *no* fire texture. Owners who want the variant run
this script against their own installed copy of the game:

    python3 tools/make_low_fire.py --source "/path/to/fire_0.png" \
                                   --source1 "/path/to/fire_1.png"

Where to find the files
-----------------------
  Android: extract the Minecraft APK (or the installed resource pack) and read
           assets/resource_pack/textures/blocks/fire_0.png and fire_1.png
  Windows: <install>/data/resource_packs/vanilla/textures/blocks/fire_*.png

The script writes a *separate* pack next to the main one:
    build/Novayclient_LowFire.mcpack
so the honest default release stays clean and the optional extra is explicit.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gen_assets import low_fire_from_vanilla  # noqa: E402

BUILD = ROOT / "build"


def main():
    ap = argparse.ArgumentParser(description="Build the optional Novayclient Low Fire pack")
    ap.add_argument("--source", required=True, help="path to the game's fire_0.png (16x512)")
    ap.add_argument("--source1", help="optional path to fire_1.png (16x512)")
    ap.add_argument("--keep", type=float, default=0.55,
                    help="fraction of each flame frame to keep (default 0.55)")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        sys.exit(f"error: {src} does not exist")

    staging = BUILD / "_lowfire"
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(ROOT / "pack", staging)
    (staging / "textures" / "blocks").mkdir(parents=True, exist_ok=True)

    low_fire_from_vanilla(src, staging / "textures" / "blocks" / "fire_0.png", keep=args.keep)
    if args.source1:
        low_fire_from_vanilla(Path(args.source1), staging / "textures" / "blocks" / "fire_1.png", keep=args.keep)

    # Separate identity so Minecraft treats this as its own pack and the two can
    # be enabled independently.
    import json
    import uuid
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    manifest["header"]["name"] = "Novayclient Low Fire"
    manifest["header"]["description"] = "Optional low-fire flames for Novayclient (1.19.50)"
    manifest["header"]["uuid"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, "novayclient.lowfire.header"))
    manifest["modules"][0]["uuid"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, "novayclient.lowfire.module"))
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    out = BUILD / "Novayclient_LowFire.mcpack"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(staging.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(staging).as_posix())
    shutil.rmtree(staging)
    print(f"\nbuilt {out.relative_to(ROOT)} ({out.stat().st_size/1024:.1f} KiB)")
    print("Import it alongside Novayclient and enable it above the base pack.")


if __name__ == "__main__":
    main()
