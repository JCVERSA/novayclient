#!/usr/bin/env python3
"""
Novayclient pack builder + validator.

    python3 tools/build.py           validate sources, then build
    python3 tools/build.py --check   validate only (CI friendly, no output)

Validation performed (blueprint §8):
  1. every JSON / JSON-with-comments file parses
  2. no duplicate keys inside any JSON object
  3. manifest structure, module types and min_engine_version
  4. header/module UUIDs are valid and different
  5. UUID stability: no UUID is reused by another pack in this repo
  6. every `textures/...` path referenced by pack/ui/*.json exists in pack/
     or is provided by vanilla (reported as an explicit allow-list count)
  7. every texture ships at the vanilla canvas size (AUDIT table below)
  8. nine-slice sidecars exist and match vanilla base_size values
  9. .mcpack archive has manifest.json at its root

Exit code 1 on any failure.
"""

from __future__ import annotations

import io
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
BUILD = ROOT / "build"
TARGET = [1, 19, 50]

errors: list[str] = []
warnings: list[str] = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# ---------------------------------------------------------------------------
# JSON with // comments (vanilla UI files use them; our sources may too)
# ---------------------------------------------------------------------------
_STRING = re.compile(r'"(?:\\.|[^"\\])*"')


def strip_comments(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        m = _STRING.match(text, i)
        if m:
            out.append(m.group(0))
            i = m.end()
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _no_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError(f"duplicate key {k!r}")
        seen[k] = v
    return seen


def load_json(path: Path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(strip_comments(raw), object_pairs_hook=_no_dupes)


# ---------------------------------------------------------------------------
# Ground truth from the 1.19.50.2 source tree (see docs/REFERENCES.md).
# Only geometry is stored here; no vanilla artwork is redistributed.
# ---------------------------------------------------------------------------
VANILLA_SIZES = {
    "heart": (9, 9), "heart_half": (9, 9), "heart_background": (9, 9),
    "heart_flash": (9, 9), "heart_flash_half": (9, 9), "heart_blink": (9, 9),
    "heart_new": (9, 9), "poison_heart": (9, 9), "poison_heart_half": (9, 9),
    "wither_heart": (9, 9), "wither_heart_half": (9, 9),
    "absorption_heart": (9, 9), "absorption_heart_half": (9, 9),
    "freeze_heart": (9, 9), "freeze_heart_half": (9, 9),
    "freeze_heart_flash": (9, 9), "freeze_heart_flash_half": (9, 9),
    "hunger_full": (9, 9), "hunger_half": (9, 9), "hunger_background": (9, 9),
    "hunger_blink": (9, 9), "hunger_flash_full": (9, 9), "hunger_flash_half": (9, 9),
    "hunger_effect_full": (9, 9), "hunger_effect_half": (9, 9),
    "hunger_effect_background": (9, 9), "hunger_effect_flash_full": (9, 9),
    "hunger_effect_flash_half": (9, 9),
    "armor_empty": (9, 9), "armor_full": (9, 9), "armor_half": (9, 9),
    "bubble": (9, 9),
    "bubbles_full": (12, 30), "bubbles_empty": (12, 30),
    "experiencebarempty": (13, 5), "experiencebarfull": (13, 5), "experiencenub": (11, 5),
    "experience_bar_empty_blue": (13, 5), "experience_bar_full_blue": (13, 5),
    "experience_bar_full_white": (13, 5),
    "cell_image": (5, 5), "cell_image_normal": (5, 5), "cell_image_darkgrey": (5, 5),
    "cell_image_invert": (5, 5), "cell_image_red": (5, 5), "cell_image_lock": (5, 5),
    "highlight_slot": (1, 1),
    "dialog_background_opaque": (16, 16),
    "pause_screen_border": (5, 5),
    "hud_tip_text_background": (6, 6),
    "hotbar_start_cap": (1, 22), "hotbar_end_cap": (1, 22),
    "selected_hotbar_slot": (24, 24),
    **{f"hotbar_{i}": (20, 22) for i in range(9)},
}

NINESLICE = {
    "cell_image": {"nineslice_size": 1, "base_size": [5, 5]},
    "cell_image_normal": {"nineslice_size": 1, "base_size": [5, 5]},
    "dialog_background_opaque": {"nineslice_size": 4, "base_size": [16, 16]},
    "pause_screen_border": {"nineslice_size": 1, "base_size": [5, 5]},
    "hud_tip_text_background": {"nineslice_size": [2, 2, 2, 2], "base_size": [6, 6]},
    "experiencebarempty": {"nineslice_size": [6, 1, 6, 1], "base_size": [13, 5]},
    "experiencebarfull": {"nineslice_size": [1, 0, 1, 0], "base_size": [13, 5]},
}

# Textures that legitimately live in the vanilla pack and are only referenced
# by our UI JSON (never overridden).
VANILLA_TEXTURES_OK = {
    "textures/ui/Black", "textures/ui/White", "textures/ui/control",
    "textures/ui/dialog_background_hollow_4", "textures/ui/tooltip_default_background",
}


def png_size(path: Path):
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")
    return w, h


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check_json_files():
    files = [p for p in PACK.rglob("*.json")]
    if not files:
        err("no JSON files found in pack/")
    for p in files:
        try:
            load_json(p)
        except Exception as e:  # noqa: BLE001
            err(f"JSON: {p.relative_to(ROOT)}: {e}")
    return len(files)


def check_manifest():
    path = PACK / "manifest.json"
    if not path.exists():
        err("manifest.json is missing")
        return
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"manifest.json: {e}")
        return

    if m.get("format_version") != 2:
        err(f"manifest format_version must be 2, got {m.get('format_version')!r}")

    header = m.get("header", {})
    if not header.get("name"):
        err("manifest header.name missing")
    if not header.get("description"):
        err("manifest header.description missing")
    if header.get("min_engine_version") != TARGET:
        err(f"min_engine_version must be {TARGET}, got {header.get('min_engine_version')!r}")
    if not isinstance(header.get("version"), list) or len(header["version"]) != 3:
        err("header.version must be [major, minor, patch]")

    uuids = []
    for key, val in (("header", header.get("uuid")),):
        try:
            uuids.append(str(uuid.UUID(val)))
        except Exception:  # noqa: BLE001
            err(f"manifest {key}.uuid is not a valid UUID: {val!r}")

    modules = m.get("modules") or []
    if not modules:
        err("manifest has no modules")
    types = []
    for i, mod in enumerate(modules):
        types.append(mod.get("type"))
        try:
            uuids.append(str(uuid.UUID(mod.get("uuid"))))
        except Exception:  # noqa: BLE001
            err(f"manifest modules[{i}].uuid is not a valid UUID: {mod.get('uuid')!r}")
    if types != ["resources"]:
        err(f"release must contain exactly one 'resources' module, got {types}")
    if len(set(uuids)) != len(uuids):
        err("manifest UUIDs must all be different")

    # UUID stability: same UUID must not appear in any other manifest here.
    for other in ROOT.rglob("manifest.json"):
        if other.resolve() == path.resolve() or "build" in other.parts:
            continue
        try:
            om = json.loads(strip_comments(other.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            continue
        ids = {om.get("header", {}).get("uuid")} | {x.get("uuid") for x in om.get("modules", [])}
        if ids & set(uuids):
            err(f"UUID collision with {other.relative_to(ROOT)}")

    return m


def check_textures():
    ui_dir = PACK / "textures" / "ui"
    gui_dir = PACK / "textures" / "gui"
    if not (gui_dir / "icons.png").exists():
        err("textures/gui/icons.png (crosshair atlas) is missing")
    else:
        if png_size(gui_dir / "icons.png") != (16, 16):
            err("crosshair atlas must be 16x16")

    for name, expect in VANILLA_SIZES.items():
        p = ui_dir / f"{name}.png"
        if not p.exists():
            err(f"missing texture textures/ui/{name}.png")
            continue
        try:
            size = png_size(p)
        except Exception as e:  # noqa: BLE001
            err(f"{p.name}: {e}")
            continue
        if size != expect:
            err(f"{p.name}: {size[0]}x{size[1]} must match vanilla {expect[0]}x{expect[1]}")

    for name, expect in NINESLICE.items():
        side = ui_dir / f"{name}.json"
        if not side.exists():
            err(f"missing nine-slice sidecar textures/ui/{name}.json")
            continue
        try:
            data = json.loads(side.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            err(f"{side.name}: {e}")
            continue
        if data.get("base_size") != expect["base_size"]:
            err(f"{side.name}: base_size {data.get('base_size')} != vanilla {expect['base_size']}")


def check_ui_references():
    """Every textures/... reference in our UI files must resolve."""
    refs = set()
    for p in (PACK / "ui").rglob("*.json"):
        text = strip_comments(p.read_text(encoding="utf-8"))
        for m in re.finditer(r'"(textures/[^"$]+)"', text):
            refs.add(m.group(1).removesuffix(".png"))
        for m in re.finditer(r"'(textures/[^'$]+)'", text):
            refs.add(m.group(1).removesuffix(".png"))

    missing = []
    for r in sorted(refs):
        rel = r.removeprefix("textures/")
        cand = PACK / "textures" / rel
        if cand.with_suffix(".png").exists() or cand.with_suffix(".json").exists():
            continue
        if r in VANILLA_TEXTURES_OK:
            continue
        missing.append(r)
    if missing:
        err("UI references missing textures: " + ", ".join(missing))
    return len(refs)


def find_control(node, name, depth=0):
    """Depth-limited search for a named child control anywhere in an element."""
    if not isinstance(node, dict) or depth > 12:
        return None
    if name in node:
        return node[name]
    for key, val in node.items():
        if key == "controls" and isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    for cname, cval in item.items():
                        if cname == name:
                            return cval
                        found = find_control(cval, name, depth + 1)
                        if found is not None:
                            return found
        elif isinstance(val, dict):
            found = find_control(val, name, depth + 1)
            if found is not None:
                return found
    return None


def check_ui_targets():
    """
    If a vanilla 1.19.50 reference tree is available, prove that every element
    this pack merges (including a/b/c nested paths) really exists there and
    that array targets exist. Skipped when the reference tree is absent.
    """
    ref = Path("/tmp/vanilla")
    if not ref.exists():
        warn("vanilla reference tree not found; UI target check skipped")
        return 0
    checked = 0
    for ui_file in (PACK / "ui").glob("*.json"):
        if ui_file.name.startswith("_"):
            continue
        ref_file = ref / ui_file.name
        if not ref_file.exists():
            err(f"ui/{ui_file.name} has no vanilla counterpart in the reference tree")
            continue
        try:
            van = load_json(ref_file)
            mine = load_json(ui_file)
        except Exception as e:  # noqa: BLE001
            err(f"ui target check could not load {ui_file.name}: {e}")
            continue
        for key, val in mine.items():
            if key == "namespace":
                continue
            node = van
            for part in key.split("/"):
                node = find_control(node, part)
                if node is None:
                    err(f"ui/{ui_file.name}: element '{key}' not found in 1.19.50 vanilla")
                    break
            if node is None:
                continue
            checked += 1
            if not isinstance(val, dict):
                continue
            for mod in val.get("modifications", []):
                arr = mod.get("array_name")
                if not isinstance(arr, str):
                    continue
                if arr in ("controls",):
                    target = node.get(arr) if isinstance(node, dict) else None
                    if target is None:
                        err(f"ui/{ui_file.name}: '{key}' has no '{arr}' array")
                        continue
                    existing = {c for item in target if isinstance(item, dict) for c in item}
                    for item in mod.get("value", []):
                        for name in item:
                            if name in existing:
                                err(f"ui/{ui_file.name}: control name '{name}' already exists in '{key}'")
    return checked


def check_ui_defs():
    path = PACK / "ui" / "_ui_defs.json"
    if not path.exists():
        return
    try:
        data = load_json(path)
    except Exception as e:  # noqa: BLE001
        err(f"_ui_defs.json: {e}")
        return
    for entry in data.get("ui_defs", []):
        if not (PACK / entry).exists():
            err(f"_ui_defs.json references missing file {entry}")


def check_scope_rules():
    """Guard rails that keep the release honest (blueprint §2, §4)."""
    banned = {
        "particles": "no particles in the client pack",
        "animation_controllers": "no behaviour animation controllers",
        "render_controllers": "no render controllers",
    }
    for folder, why in banned.items():
        if (PACK / folder).exists():
            warn(f"pack/{folder} exists but {why}")
    if any(PACK.rglob("*.mcfunction")):
        err("behavior-pack content found in a resource pack")
    for p in PACK.rglob("*.json"):
        text = strip_comments(p.read_text(encoding="utf-8", errors="ignore"))
        low = text.lower()
        for fake in ("cps", "fps", "ping_ms"):
            if re.search(rf'"#{fake}\b', low):
                err(f"{p.relative_to(ROOT)} binds a fabricated #{fake} value")


def check_assets_exist():
    for p in (PACK / "pack_icon.png",):
        if not p.exists():
            err(f"{p.relative_to(ROOT)} is missing")
        elif png_size(p) != (256, 256):
            err("pack_icon.png must be 256x256")


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------
def build_pack(manifest):
    BUILD.mkdir(parents=True, exist_ok=True)
    version = ".".join(str(v) for v in manifest["header"]["version"])
    out = BUILD / f"Novayclient_{version}.mcpack"

    files = sorted(p for p in PACK.rglob("*") if p.is_file())
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, p.relative_to(PACK).as_posix())
    buf.seek(0)
    out.write_bytes(buf.read())

    # verify archive root
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        if "manifest.json" not in names:
            err("built archive has no manifest.json at the root")
        if any(n.startswith("pack/") for n in names):
            err("built archive nests contents under pack/")
        bad = z.testzip()
        if bad:
            err(f"archive entry is corrupt: {bad}")

    size = out.stat().st_size
    print(f"\nbuilt  {out.relative_to(ROOT)}  ({size/1024:.1f} KiB, {len(files)} files)")
    return out


# ---------------------------------------------------------------------------
def main(argv):
    check_only = "--check" in argv
    print("Novayclient validation")
    n = check_json_files()
    print(f"  json files parsed ......... {n}")
    manifest = check_manifest()
    print("  manifest .................. checked")
    check_textures()
    print(f"  texture sizes ............. {len(VANILLA_SIZES)} sprites checked")
    refs = check_ui_references()
    print(f"  ui texture refs ........... {refs} checked")
    targets = check_ui_targets()
    print(f"  ui merge targets .......... {targets} verified")
    check_ui_defs()
    check_assets_exist()
    check_scope_rules()

    for w in warnings:
        print(f"  WARN  {w}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("  scope rules ............... ok")

    if not check_only and manifest:
        build_pack(manifest)
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
