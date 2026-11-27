# On-device test plan — Novayclient 1.0

Everything in this file is **unrun** as of this release. Static validation
(`tools/build.py`) proves structure, sizes and merge targets, not runtime
behaviour. Fill in the Result column on a real device before calling 1.0
verified.

Device under test: ______________________  
Minecraft build: `1.19.50.02`  UI profile: ☐ Pocket ☐ Classic  Orientation: ☐ Portrait ☐ Landscape  
UI scale: ______  Pack order: ☐ alone ☐ above others ☐ below others

## A. Install and activation

| # | Test | Pass condition | Result |
|---|---|---|---|
| A1 | Open the `.mcpack` on Android | Minecraft imports it without "invalid pack" | |
| A2 | Settings → Global Resources | "Novayclient" listed with the Novay icon | |
| A3 | Activate the pack | No error toast; icon shows active | |
| A4 | Launch a world with the pack active | World loads; no crash or stuck loading screen | |
| A5 | Content log (Settings → Creator) | No errors about missing textures or UI | |

## B. Core HUD

| # | Test | Pass condition | Result |
|---|---|---|---|
| B1 | Hotbar | 9 slots restyled, items still render, counts/durability visible | |
| B2 | Selected slot | Cyan frame on the held slot only, moves with selection | |
| B3 | Hearts | 10 hearts, full/half states update on damage | |
| B4 | Hunger | Shank icons update while eating/sprinting | |
| B5 | Armor | Armor icons appear when armour is equipped, empty when removed | |
| B6 | Air | Bubble row appears underwater and depletes | |
| B7 | XP bar | Fills, empties and shows the level nub correctly | |
| B8 | Poison / wither / absorption / freeze | Swap to the correct recoloured hearts (drink a potion, stand in powder snow) | |
| B9 | Damage flash | Heart flash frames do not look broken | |

## C. Crosshair (Experimental)

| # | Test | Pass condition | Result |
|---|---|---|---|
| C1 | First person, looking at a wall | Cyan cross with a 2px centre gap, centred on screen | |
| C2 | Bright background (snow / sand) | Dark outline keeps the reticle readable | |
| C3 | Third person | Reticle hidden as in vanilla | |
| C4 | Hidden HUD (F1 equivalent) | Reticle disappears with the HUD | |
| C5 | Aim at an entity while mining | Block-break progress indicator still shows around the reticle | |

If C1 shows a vanilla cross, the icons-atlas route does not apply on
1.19.50.02. Mark the feature Unsupported and remove
`pack/textures/gui/icons.png` from the release rather than shipping a file that
does nothing.

## D. Touch controls and readability

| # | Test | Pass condition | Result |
|---|---|---|---|
| D1 | Movement stick, jump, sneak, attack, use, inventory buttons | All present, correctly positioned, responsive | |
| D2 | Touch a hotbar slot directly | Item is selected | |
| D3 | Open inventory by tapping the bag button | Inventory opens normally | |
| D4 | HUD opacity setting | Lowering it fades the Novay HUD too (no stuck opaque plate) | |
| D5 | Identity chip | Visible top-right, clear of hunger / bubbles / auto-save, not over chat | |
| D6 | Screen ratios: 16:9, 18:9, 20:9 and tablet | No overlap, chip stays on screen, nothing clipped by notches | |
| D7 | Pocket UI and Classic UI | Both profiles usable; no clipped panels | |

## E. Menus

| # | Test | Pass condition | Result |
|---|---|---|---|
| E1 | Pause menu | Frames restyled, brand plate sits below the buttons | |
| E2 | Resume / Settings / Save & Exit | Each button works and lands on the right screen | |
| E3 | Pause menu on a small phone in Pocket UI | No button pushed off screen by the added plate | |
| E4 | Player list on a server (if available) | List still scrolls and shows players | |
| E5 | Skin panel / character view | Still opens from pause | |

## F. Inventory and containers

| # | Test | Pass condition | Result |
|---|---|---|---|
| F1 | Player inventory | Slots, hotbar row and armour slots restyled consistently | |
| F2 | Crafting | Drag/drop, shift-place and recipe book all work | |
| F3 | Chest, furnace, crafting table, anvil, enchanting, brewing | Panel surfaces restyled, slot hit areas unchanged | |
| F4 | Creative inventory | Tabs and search still work | |
| F5 | Hover / selection on a slot | Highlight is visible and not overwhelming | |
| F6 | Item tooltips | Readable over the new panel colour | |

## G. Chat

| # | Test | Pass condition | Result |
|---|---|---|---|
| G1 | Chat rows in a bright scene | Text readable, tint not too dark or too transparent | |
| G2 | Chat fade-out | Rows still fade, accent edge fades with them | |
| G3 | Open chat and send a message | Input screen unaffected, message sends | |
| G4 | Long messages | Wrapping unchanged, no clipped accent edge | |

## H. Stability

| # | Test | Pass condition | Result |
|---|---|---|---|
| H1 | 15 minutes of normal play (survival) | No crash, no missing textures, no UI corruption | |
| H2 | Same in creative | No issues | |
| H3 | World with another resource pack active | Both load, order behaves as expected | |
| H4 | Join a server | Pack loads; no gameplay interference | |
| H5 | Deactivate the pack | Everything returns to vanilla cleanly | |

## Sign-off

| Field | Value |
|---|---|
| Tester | |
| Date | |
| Build hash / tag | |
| Overall | ☐ Pass ☐ Pass with notes ☐ Fail |

Any row that fails should also update the status in
[FEATURES.md](FEATURES.md) and the limitation in
[COMPATIBILITY.md](COMPATIBILITY.md) before release.
