# UI bindings — used, inherited, and deliberately avoided

Scope: Minecraft Bedrock **1.19.50.02**, namespace `hud`, `pause`, globals.
Every name below was checked against the 1.19.50.2 files, not against current
documentation.

## 1. What this pack writes

### `ui/_global_variables.json`

Variables are **constant** in JSON UI — you cannot change them at runtime, and
a partial file is safe (other packs ship 1–2 variables). Only own-namespace
variables are declared:

| Variable | Purpose |
|---|---|
| `$novay_accent`, `$novay_accent_dark`, `$novay_ink`, `$novay_text`, `$novay_muted` | palette |
| `$novay_chat_alpha` | chat row opacity (vanilla 0.7) |
| `$novay_hud_chip_size`, `$novay_hud_chip_offset`, `$novay_hud_chip_alpha` | HUD identity chip |
| `$novay_pause_chip_size`, `$novay_pause_chip_alpha` | pause menu plate |

No vanilla variable is redefined, so other screens cannot be affected by a
typo in ours.

### `ui/hud_screen.json`

| Target | Operation | Why it is safe |
|---|---|---|
| `chat_grid_item/chat_background` | set `alpha`, `color`; `insert_front` one 1px image | Row is a plain `image` with a `controls` array; text, sizes and `anim_chat_bg_wait` untouched |
| `root_panel` | `insert_back` one `image` | `hud.root_panel` only anchors children absolutely (verified: 23 controls, none stack-dependent), so appending cannot shift anything |

### `ui/pause_screen.json`

| Target | Operation | Why it is safe |
|---|---|---|
| `pause_screen_menu` | `insert_back` one `image` | This element *is* a `stack_panel`; the menu column grows by one small row, nothing is displaced or covered |

All three targets, including the nested path, are re-checked on every build by
`tools/build.py::check_ui_targets`.

## 2. Bindings we rely on (read-only)

| Binding | Type | Source | Use |
|---|---|---|---|
| `#hud_visible_not_centered` | global | `hud.root_panel` children | hide the identity chip whenever the vanilla HUD is hidden (F1, menus, screenshots) |
| `#hud_visible`, `#hud_alpha`, `#hud_propagate_alpha` | global | inherited from `root_panel` | the chip fades with HUD opacity because it is a child; no extra binding written |

We deliberately add **no** bindings of our own beyond `#visible`, which keeps
the pack immune to binding-name drift between versions.

## 3. Bindings we do **not** use, and why

| Binding / feature | Status on 1.19.50.02 | Consequence |
|---|---|---|
| `#look_at_cursor` | only valid for `renderer[hud_player_renderer]` (paper doll) | cannot build a "targeting entity" reticle colour change |
| Coordinates (`#position`, `#x/#y/#z`) | not exposed to arbitrary HUD controls | no coordinate widget |
| Armor slots in HUD | only via `armor_renderer` (vanilla bars) | no custom armor HUD |
| Potion list | only via `mob_effects_renderer` (vanilla icons) | no custom potion HUD |
| FPS / CPS / ping / keystrokes | no binding exists | unsupported, never faked |
| Pack settings / subpack toggles | not exposed to resource packs in this build | no in-game settings menu |
| `#hud_title_text_string` etc. | available, but only used by vanilla title factory | left alone |

Modern packs that show these values target much newer builds, and several also
ship a behaviour pack or script module. `@minecraft/server` 1.0.0 starts at
1.19.70, so scripts are not an option here — documented in
[FEASIBILITY.md](FEASIBILITY.md#4-why-dynamic-hud-modules-are-not-in-10).

## 4. Merge mechanics reference

* UI files merge **per element**. An override only needs the elements it
  changes; everything else stays vanilla.
* `"element/path/child": {...}` addresses nested controls directly.
* `modifications[].array_name` must name an array that exists on that element.
* `operation` supports `insert_front`, `insert_back`, `replace`.
* `_ui_defs.json` must list **only new files**. Vanilla namespaces are loaded
  and merged automatically; listing them would load them twice. This pack adds
  no new UI files, so it ships no `_ui_defs.json` at all.
