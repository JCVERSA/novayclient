# Compatibility and known limitations

## Target contract

| Item | Value |
|---|---|
| Minecraft edition | Bedrock |
| Test target | **1.19.50.02** (Android) |
| Manifest | `format_version` 2, `min_engine_version` `[1, 19, 50]` |
| Module | single `resources` module |
| Scripts / experiments | none |
| UI mode | Pocket UI and Classic UI both left intact; only touch-safe visuals are changed |
| Language | `en_US` |

The pack is game content, not an APK: the phone's CPU ABI is irrelevant.
Behaviour depends on Bedrock's resource-pack and JSON UI systems only.

## Version assumptions

* The UI overrides were written **only** against the 1.19.50.2 release line.
  File contents and bindings from newer versions were used for research about
  *structure*, never copied.
* Because `min_engine_version` is `[1, 19, 50]`, Minecraft will also offer the
  pack on later builds. Textures will keep working; the three JSON UI merges
  are version-sensitive and have **not** been validated above 1.19.50.
  If a later version changes `hud.root_panel`, `pause_screen_menu` or
  `chat_grid_item/chat_background`, those merges may silently stop applying.
  That is a cosmetic failure, not a crash — textures still load.

## Known limitations

1. **Crosshair is Experimental.** It depends on the engine drawing the reticle
   from cell `(0,0)` of `textures/gui/icons.png`. The 16x16 atlas ships only
   that cell, so no other HUD art can break even if the assumption is wrong —
   the worst case is a vanilla-looking crosshair.
2. **No in-game toggle menu.** 1.19.50 resource packs cannot expose pack
   settings. Turning the identity chip off means editing one variable (see
   [FEATURES.md](FEATURES.md#8-in-game-identity-chip)) and rebuilding.
3. **Crosshair styles are build-time.** Four designs are generated; only the
   compiled one is active. No subpacks are shipped because subpack behaviour on
   1.19.50.02 is unverified.
4. **Chat restyle is a JSON merge.** If another pack overrides
   `chat_grid_item/chat_background`, one of the two wins depending on pack
   order.
5. **Textures win over JSON, always.** Two packs cannot both own
   `textures/ui/heart.png`.
6. **No performance claim.** Reduced visual noise is not a measured FPS gain.

## Conflicts

| Conflict | Result | Fix |
|---|---|---|
| Another pack also changes `textures/ui/*` HUD sprites | Only the top pack's sprite is used | Put Novayclient above it (or below, if you prefer the other HUD) |
| Another pack changes `hud.root_panel` / `pause_screen_menu` | Both append independently; items stack | Usually harmless; if the pause column overflows, move one pack down |
| Another pack changes chat rendering | One chat style wins | Reorder packs |
| A pack with a **behaviour** pack attached | No interaction; Novayclient is resource-only | none |
| Server resource pack pushes a HUD | Server pack can override the client pack | Keep Novayclient above; some servers force their pack |

Novayclient never modifies gameplay data, so it cannot desync, break
anti-cheat, change reach/hitboxes, or alter server rules.

## Pack ordering

Higher pack = higher priority. Recommended when mixing with HUD packs:

```text
1. Novayclient                (UI + HUD artwork)
2. Your other HUD pack
3. Texture packs / shaders
   vanilla                    (always keep available)
```

## Tested combinations

| Combination | Result |
|---|---|
| No other packs | Not yet recorded on device — see TESTING.md |
| With a texture pack that changes blocks only | Expected compatible (no shared files) |
| With another HUD pack | Expected: pack order decides, both may append to menus |

Nothing in this table should be read as "verified" until TESTING.md is filled
in with real device results.
