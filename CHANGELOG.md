# Changelog

All notable changes to Novayclient are recorded here. The pack follows
[Semantic Versioning](https://semver.org/); the version in `pack/manifest.json`
must match the released `.mcpack`.

## [1.0.0] — unreleased

First Resource-Pack-only build for Minecraft Bedrock **1.19.50.02**.

### Added
- Resource pack manifest (`format_version` 2, `min_engine_version` `[1,19,50]`,
  single `resources` module, fresh stable UUIDs).
- Original identity: 256x256 pack icon, wordmark plate, cyan/ink palette.
- Hotbar artwork: 9 slot textures, HUD-only selection frame, end caps.
- Full HUD status sprite set at vanilla canvas sizes: hearts (incl. half, flash,
  blink, poison, wither, absorption, freeze), hunger (incl. effect family),
  armor, air bubbles, XP bar (incl. blue/white variants). Only textures that
  a 1.19.50 UI file actually references are shipped.
- Inventory and container surfaces: nine-sliced slot cells, dialog backdrop,
  slot highlight, pause frame, tip/effect backdrops.
- `hud_screen.json`: chat row tint + accent edge, in-game identity chip.
- `pause_screen.json`: appended brand plate on the existing menu stack.
- `_global_variables.json`: documented `$novay_*` palette and tuning values.
- `tools/gen_assets.py` — all artwork regenerates from code.
- `tools/build.py` — JSON/duplicate-key validation, manifest and UUID checks,
  texture-size and nine-slice checks, UI merge-target verification against the
  1.19.50 reference tree, and `.mcpack` packaging with root-manifest assertion.
- `tools/make_low_fire.py` — optional Low Fire pack built from the user's own
  game files (never redistributed).
- Documentation: feasibility audit, feature status, compatibility, on-device
  test plan, bindings, asset provenance, references.

### Known limitations
- Crosshair replacement is **Experimental** (icons-atlas cell route).
- JSON UI merges (chat, identity chip, pause plate) are **Experimental** until
  confirmed on 1.19.50.02.
- No in-game settings menu, no subpacks.
- No FPS/CPS/ping/keystroke/coordinate counters by design.

### Not included
- Behaviour pack, scripts, Beta APIs, particles, sounds.
- Any vanilla or third-party artwork.
