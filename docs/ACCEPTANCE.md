# Release acceptance checklist — 1.0.0

Mirrors blueprint §15. "Static" means proven in this repository by
`tools/build.py`; "Device" means it still needs the run in
[TESTING.md](TESTING.md).

| # | Requirement | Evidence | State |
|---|---|---|---|
| 1 | Project is a Bedrock Resource Pack, not an Android app | manifest has one `resources` module; no APK, no scripts | Static ✅ |
| 2 | Output is a valid `.mcpack` with `manifest.json` at the archive root | `build_pack()` asserts root manifest and no `pack/` nesting | Static ✅ |
| 3 | Manifest uses `format_version` 2 and `min_engine_version` `[1,19,50]` | asserted in `check_manifest()` | Static ✅ |
| 4 | UUIDs unique and stable across updates | header/module UUIDs differ, valid, collision-checked repo-wide; documented "never change" rule | Static ✅ |
| 5 | UI overrides based on the 1.19.50 release line | every merge target verified against the `v1.19.50.2` tree by `check_ui_targets()` | Static ✅ |
| 6 | No mandatory script API or experimental setting | no BP, no scripts, no `capabilities`, no Beta APIs | Static ✅ |
| 7 | No fake CPS/FPS/ping/keystroke/speed/damage values | `check_scope_rules()` rejects such bindings; none written | Static ✅ |
| 8 | All vanilla touch and menu controls still function | no vanilla control removed/reordered/rebound; merges are additive only | Device ⏳ |
| 9 | All textures match vanilla canvas + nine-slice contract | 64 sprites + 7 sidecars asserted every build | Static ✅ |
| 10 | Imported and tested on 1.19.50.02 Android | requires hardware | Device ⏳ |
| 11 | Known limitations and UI conflicts documented | [COMPATIBILITY.md](COMPATIBILITY.md) | Static ✅ |
| 12 | Third-party assets have documented licence information | [../LICENSES.md](../LICENSES.md), [ASSETS.md](ASSETS.md) | Static ✅ |
| 13 | Feature status honest (Experimental vs Verified) | [FEATURES.md](FEATURES.md), crosshair labelled Experimental | Static ✅ |
| 14 | Source and release artifact kept together | `CHANGELOG.md` + tag instruction; build reproducible from source | Static ✅ |

## Release gate

1.0.0 must **not** be published as "verified" until rows 8 and 10 pass on the
target phone and the sign-off table in TESTING.md is filled in. Until then the
release is labelled:

> **1.0.0 — experimental build.** Statically validated against the 1.19.50.2
> asset contract; not yet confirmed on device.
