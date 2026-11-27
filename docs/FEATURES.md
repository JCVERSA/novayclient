# Features — Novayclient 1.0

Status vocabulary (blueprint §9.3):

* **Verified** — checked on Minecraft 1.19.50.02 on Android.
* **Experimental** — implemented, not yet confirmed on the target device.
* **Unsupported** — known not to work on this build.
* **Not implemented** — planned only; no code exists.

Assets are all "verified" in the narrow sense that their canvas sizes,
nine-slice values and usage were checked against the vanilla 1.19.50.2 tree by
`tools/build.py`. That is *not* the same as an in-game pass — see
[TESTING.md](TESTING.md).

---

## 1. Identity

| | |
|---|---|
| Status | Verified asset / Experimental in-game |
| Files | `pack_icon.png`, `textures/ui/novay_logo.png`, `ui/_global_variables.json` |

Original icon (256x256 "N" monogram with cyan circuit corners), an original
wordmark plate, and a palette carried into every sprite. The palette lives in
one place (`_global_variables.json`) and mirrors `tools/gen_assets.py`.

## 2. Crosshair

| | |
|---|---|
| Status | **Experimental** |
| Files | `textures/gui/icons.png` (16x16) |

Replaces the first-person reticle by overriding the `(0,0)` cell of the GUI
atlas. The shipped reticle is a 1px cyan cross with a 2px centre gap and a
1px dark outline so it stays visible on snow and glowstone.

Three alternative shapes are generated as previews in `docs/preview/`
(`crosshair_plus.png`, `crosshair_dot.png`, `crosshair_bracket.png`). They are
**not** switchable at runtime — 1.19.50 has no pack-settings UI for a resource
pack, so selecting one means editing `tools/gen_assets.py` (`CROSSHAIR_SHAPE`)
and rebuilding. This is stated plainly rather than shipping a dead toggle.

Risk, stated: the reticle is engine-drawn from that atlas cell; the route is
widely used by community packs but could not be confirmed on hardware here.

## 3. Hotbar and selection highlight

| | |
|---|---|
| Status | Verified asset |
| Files | `textures/ui/hotbar_0..8.png`, `selected_hotbar_slot.png`, `hotbar_start_cap.png`, `hotbar_end_cap.png` |

Dark slot wells with a 1px steel frame and cyan corner notches; the selected
slot gets a cyan frame with 3px corner ticks. Item rendering, stack counts,
durability bars, cooldown sweeps and the touch slot buttons are untouched —
the textures are drawn *behind* those layers by vanilla.

The selection frame is HUD-only in 1.19.50: the inventory screen composes its
own highlight from `cell_image` tinting, so changing the 24x24 frame cannot
leak into the inventory.

## 4. Status HUD (hearts, hunger, armor, air, XP)

| | |
|---|---|
| Status | Verified asset |
| Files | 34 sprites under `textures/ui/` |

Every sprite is redrawn at the **exact vanilla canvas size**:

* hearts 9x9, including half, background, flash, blink and the poison / wither /
  absorption / freeze families
* hunger 9x9, including half, blink, flash and the hunger-effect family
* armor 9x9 empty / half / full
* air bubbles 9x9 plus the 12x30 rotating strips
* XP bar 13x5 empty/full, 11x5 nub, plus the blue/white bar variants

Half-hearts use a dimmed "lost" side instead of a flat grey, so a half heart
still reads as one icon at phone scale. Nine-slice sidecars for the XP bars are
copied at vanilla base sizes so the bars stretch identically.

Why all states: the engine swaps these textures for damage flashes, poison
ticks, freezing and low-hunger blink. Shipping only `heart.png` leaves those
states vanilla-red and the HUD looks broken under damage.

## 5. Inventory and container surfaces

| | |
|---|---|
| Status | Verified asset |
| Files | `cell_image*.png` + sidecars, `dialog_background_opaque.png` + sidecar, `highlight_slot.png` |

The 5x5 nine-sliced slot cell becomes a dark panel with a hairline border; the
16x16 dialog surface becomes a matching container backdrop with corner accents.
Because these are the shared surfaces, chests, furnaces, crafting tables,
enchanting, anvils, brewing and the creative inventory all restyle together
without a single screen-level override.

Nothing about grid dimensions, slot hit areas, drag/drop or the crafting
recipes is touched.

## 6. Pause menu

| | |
|---|---|
| Status | Experimental (JSON UI) + Verified asset (frame) |
| Files | `textures/ui/pause_screen_border.png`, `pack/ui/pause_screen.json` |

The 5x5 menu frame is re-skinned by texture. On top of that, one plate is
appended to the existing `pause_screen_menu` stack, so the menu column grows by
one small row instead of anything being overlapped or displaced. Resume,
Settings, Save & Exit, the player list, the skin panel and all focus
navigation keep their vanilla bindings.

## 7. Chat

| | |
|---|---|
| Status | Experimental (JSON UI) |
| Files | `pack/ui/hud_screen.json` |

The vanilla chat row is a `textures/ui/Black` image at 0.7 alpha. The pack
re-tints it to the Novay panel colour, sets alpha from `$novay_chat_alpha`
(0.72) and adds a 1px cyan edge on the left of each row. Text size, wrapping,
the chat fade animation and the input screen are untouched, so readability
rules and TTS behaviour are unchanged.

## 8. In-game identity chip

| | |
|---|---|
| Status | Experimental (JSON UI) |
| Files | `pack/ui/hud_screen.json`, `textures/ui/novay_logo.png` |

A 45x10.5 wordmark at 0.55 alpha, anchored top-right with a 44px vertical
offset. That offset is deliberate: it clears the hunger bar (top-right corner),
the bubble counters and the auto-save icon, and it is nowhere near the
crosshair, chat or touch controls.

Hiding it needs no UI edit: set `$novay_hud_chip_alpha` to `0` in
`pack/ui/_global_variables.json` and rebuild.

## 9. Low fire

| | |
|---|---|
| Status | Optional, external build |
| Files | `tools/make_low_fire.py` → `build/Novayclient_LowFire.mcpack` |

A low-fire pack must start from the game's 32-frame flame strip; redrawing it
would change what fire looks like instead of reducing it. That artwork is
Mojang's, so it is **not** in this repository. `tools/make_low_fire.py` takes
your own `fire_0.png` / `fire_1.png` (16x512 each), keeps the lower part of
each frame, softens it, and writes a separate pack with its own UUID.

```bash
python3 tools/make_low_fire.py \
    --source "/path/to/fire_0.png" \
    --source1 "/path/to/fire_1.png" --keep 0.55
```

Documented, reproducible, and free of redistributed vanilla art. **Experimental**
until measured in game.

## 10. Deliberately absent

* FPS / CPS / ping / keystrokes / speed / damage numbers — no live data reaches
  JSON UI on this build; drawing them would mean drawing fake numbers.
* Hitbox or reach changes — server-authoritative, not a client concern.
* Armor, potion and coordinate HUD modules — no verified live binding on
  1.19.50.02. Backlog, not shipped.
* Subpack presets and an in-game toggle menu — not validated on this build.
* Any FPS claim. The pack reduces visual noise; that is not the same thing as
  a measured performance gain, and it is not sold as one.
