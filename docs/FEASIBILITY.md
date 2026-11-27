# Feasibility audit — Minecraft Bedrock 1.19.50.02

This document records **what was actually checked** in the vanilla 1.19.50.2
files before any feature was promised. Where a claim could not be verified, the
feature is labelled Experimental and the open question is written down.

Reference tree: `Mojang/bedrock-samples`, tag `v1.19.50.2`, `resource_pack/`
(198 UI JSON files, full texture manifest). See [REFERENCES.md](REFERENCES.md).

## 1. How the UI layer actually merges

Four questions had to be answered before writing a single line of JSON.

| Question | Finding | Evidence |
|---|---|---|
| Do `pack/ui/<vanilla>.json` files replace or merge with vanilla? | **Merge, per element.** An override file only needs the elements it changes. | Working packs: Sidebar-HUD ships an 86-line `hud_screen.json` with 3 elements; Nova Client patches `hud_content` by name. Bedrock Wiki "Intro to JSON UI". |
| Can an element at `a/b/c` be addressed directly? | **Yes.** `"hud_title_text/title_frame/title": { modifications: [...] }` is documented and used by Nova Client (`hud_title_text/subtitle_frame`). | Wiki example + Nova `ui/hud_screen.json`. |
| Can `modifications` insert a new control? | **Yes** — `insert_front`, `insert_back`, `replace`. | holoprint `pause_screen.json`, Nova `hud_content`, BetMC `item_text_aligner`. |
| Is a partial `_global_variables.json` safe? | **Yes.** Published packs ship one or two variables only. | NSPC911/Modules-Plus, MrGalletaYT/ScoreboardJavaPM, AstralClient `ui/_global_variables.json`. |

Consequence: the pack's UI surface is 3 small files and ~120 lines total. Every
merge target is machine-verified against the reference tree in
`tools/build.py` (`check_ui_targets`), including nested `a/b/c` paths.

## 2. The crosshair

| Check | Result |
|---|---|
| Is there a crosshair texture? | **No.** No `crosshair`/`reticle` texture exists in the 1.19.50 tree except `textures/ui/thumbnail_crosshair.png`, a settings thumbnail. |
| Is there a JSON UI control for it? | **No.** No `crosshair` control, binding or renderer name appears in any of the 198 UI files. |
| What draws it? | The `(0,0)`–`(15,15)` cell of `textures/gui/icons.png`. Pixel audit of that atlas shows a 10x10 plus at exactly that cell; the rest of the atlas holds unused legacy HUD art and is not referenced by any 1.19.50 UI file. |
| Is there a font-atlas route? | **No.** 1.19.50 ships no `font/default8.png`; the only font assets are per-language CJK glyph pages. |
| Can UI read "am I aiming at an entity"? | **No.** `#look_at_cursor` is documented as valid only for `type[custom] renderer[hud_player_renderer]`, i.e. the paper doll. |

**Decision:** ship a 16x16 `textures/gui/icons.png` override holding only the
crosshair cell. This cannot disturb other HUD art because no UI file samples
that atlas. **Status: Experimental** — it is the documented community route but
could not be confirmed on a device from this environment (test C1).

## 3. Feature matrix for this build

| Feature | Verdict | Notes |
|---|---|---|
| Custom crosshair artwork | Experimental | see §2 |
| Custom hotbar art + selection frame | Verified asset | `selected_hotbar_slot.png` is used **only** by the HUD hotbar (`hud_screen.json:545`); inventory uses a tinted `cell_image`, so a 24x24 frame is safe |
| Heart / hunger / armor / air / XP restyle | Verified asset | every canvas size matched to vanilla (9x9, 13x5, 12x30) |
| Inventory + container surfaces | Verified asset | `cell_image*` (5x5, nine-slice 1) and `dialog_background_opaque` (16x16, nine-slice 4) |
| Pause menu frame | Verified asset | `pause_screen_border.png` (5x5, nine-slice 1) |
| Chat readability | Experimental | JSON merge sets tint + alpha on `chat_grid_item/chat_background` |
| Identity chip in HUD / pause menu | Experimental | appended via `insert_back` on `hud.root_panel` / `pause.pause_screen_menu` |
| Coordinates / armor HUD / potion HUD widgets | **Not implemented** | would need readable live values in this build; see §4 |
| FPS, CPS, ping, keystrokes, speed | **Unsupported** | no binding exposes these to JSON UI |
| Damage numbers / hit markers | **Unsupported** | no combat event data reaches UI |
| Low fire | Optional external build | see [FEATURES.md](FEATURES.md#low-fire) |
| Subpacks | Deferred | not validated on 1.19.50.02; 1.0 ships single-config |

## 4. Why dynamic HUD modules are not in 1.0

Blueprint §4.2/§4.3 require a prototype to update from **real** data. What the
1.19.50 UI layer actually exposes to arbitrary HUD controls:

* `#hud_visible*` visibility family, `#hud_alpha`
* hotbar collection bindings (the pack already inherits them untouched)
* `#gamertag` (splitscreen only)
* title/subtitle/actionbar string factories

What it does **not** expose: player coordinates, armor slots, potion lists,
frame rate, input counts, or latency. Modern client packs that show these rely
on much newer builds (and frequently on a behaviour pack or script module).
The `@minecraft/server` 1.0.0 API only starts at **1.19.70**, so a scripted
module cannot be a dependency here.

Therefore the honest 1.0 release ships no counters. Armor/potion/coordinate
prototypes stay in the backlog until a test proves the data is real.

## 5. Version hygiene

* `min_engine_version` is `[1, 19, 50]`, matching the tested target.
* No manifest `capabilities` block, no `pbr`, no Beta APIs.
* Nothing in the pack requires experimental toggles or a behaviour pack.
* UI files are edited against the **1.19.50.2** release line only. Newer
  versions (1.21+, 1.26+) were used for *structure* research only; none of
  their file contents or bindings were copied.
