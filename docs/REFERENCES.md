# References and how each was used

| # | Source | Used for | Not used for |
|---|---|---|---|
| 1 | [Minecraft 1.19.50 release notes](https://feedback.minecraft.net/hc/en-us/articles/10833168748557-Minecraft-1-19-50-Bedrock) | Confirming the release baseline | — |
| 2 | [Mojang/bedrock-samples — tag `v1.19.50.2`](https://github.com/Mojang/bedrock-samples/tree/v1.19.50.2) | **Primary source.** All 198 `resource_pack/ui/*.json` files and the full texture manifest were read to audit control names, paths, bindings, canvas sizes and nine-slice values | No file contents copied into this repository |
| 3 | [bedrock.dev 1.19.50.25 add-on docs](https://bedrock.dev/docs/1.19.0.0/1.19.50.25/Addons) | Manifest-era field expectations | — (preview build) |
| 4 | [Microsoft — Script module versioning](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/versioning) | Establishing that `@minecraft/server` 1.0.0 maps to 1.19.70, so scripts cannot be a 1.19.50 dependency | — |
| 5 | [Bedrock Wiki — Intro to JSON UI](https://wiki.bedrock.dev/json-ui/json-ui-intro.html) | Merge-per-element behaviour, `modifications` operations, nested element paths, `_ui_defs.json` rules, global variables | — |
| 6 | [Bedrock Wiki — JSON UI documentation](https://wiki.bedrock.dev/json-ui/json-ui-documentation.html) | Property bag and renderer-scoped bindings (`#look_at_cursor` is paper-doll only), animation fields, global variables list | Treating current-version properties as present in 1.19.50 without checking the files |
| 7 | [Bedrock Wiki — Manifest](https://wiki.bedrock.dev/concepts/manifest.html) | Version 2 resource-pack structure, pack identity rules | — |
| 8 | [TrippleAWap/Sidebar-HUD](https://github.com/TrippleAWap/Sidebar-HUD) | Confirming that a 1.19.50 manifest (`format_version` 2, `resources` module, `min_engine_version` `[1,19,50]`) and a *tiny* `hud_screen.json` override are a working combination | Its artwork, identity, or its full-file override style |
| 9 | [Nova-Client-MCBE/Nova-Client](https://github.com/Nova-Client-MCBE/Nova-Client) (modern, 1.26.x) | Evidence for nested-path targeting, `insert_front` injection, `hud_crosshair_screen` existing only on newer builds, partial-file overrides | Any code or asset — it targets a much newer build |
| 10 | [SuperLlama88888/holoprint](https://github.com/SuperLlama88888/holoprint) | Confirming the `insert_back` + named-control pattern on `pause_screen_menu` | Its code |
| 11 | [BetMC2411/BetMC_UI](https://github.com/BetMC2411/BetMC_UI) | Confirming nested `element/child` patch syntax and `replace` on `controls` | Its code |
| 12 | [AstralClient / Modules-Plus / ScoreboardJavaPM `_global_variables.json`](https://github.com/NSPC911/Modules-Plus) | Confirming a partial globals file is valid and common | Their variable names |
| 13 | OS CLIENT, SATURN Client, Ender UI (CurseForge) | Feature *inspiration* only (organisation, what a client pack feels like) | No files were read or reused |

## How the reference tree was used

```bash
# release-line UI files
gh api "repos/Mojang/bedrock-samples/git/trees/v1.19.50.2?recursive=1"
# e.g. ui/hud_screen.json, ui/pause_screen.json, ui/ui_common.json
```

Then, for every claim in this repository:

* control names and nesting were read from those files;
* canvas sizes for all 64 overridden sprites were measured from the vanilla PNGs;
* nine-slice `base_size` / `nineslice_size` values were copied as *values only*
  (a nine-slice sidecar is geometry, not artwork);
* the crosshair cell location was established by pixel-auditing
  `textures/gui/icons.png` and confirming no UI file references that atlas.

`tools/build.py` re-runs those comparisons on every build, so a future edit
cannot quietly break the contract.

## Deliberately unused sources

* Newer `hud_screen.json` revisions (1.20/1.21/1.26) — structure research only;
  their bindings and layout differ from 1.19.50.
* Any paid or proprietary client pack — no code, artwork or font is reused.
