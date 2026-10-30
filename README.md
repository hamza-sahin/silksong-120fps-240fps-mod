# Hollow Knight: Silksong 120 FPS & 240 FPS Mod for Eden (Switch Emulator)

**Unlock the 60 FPS cap in Hollow Knight: Silksong on the Eden Nintendo Switch emulator.**
Play Silksong at a smooth **120 FPS** or **240 FPS** on PC (Windows/Linux) and Android, on high
refresh rate monitors, gaming laptops and handhelds like the Retroid Pocket, AYN Odin or Steam Deck.

- Real frames, not frame generation: the game renders every frame, so there's no added input lag.
- Game speed stays correct. Physics, timers and animations run at normal speed.
- Tiny exefs IPS patch (39 bytes). No game files, no keys, works with Eden's built-in mod manager.
- Two versions: **120 FPS** for 120/144 Hz screens, **240 FPS** for 240 Hz monitors.

## Compatibility

| | |
| --- | --- |
| Game | Hollow Knight: Silksong, title ID `010013C00E930000` |
| Game version | **Update v1.0.28324** (title version v131072), main build ID `DC3E4B892043EF2345C3EAF97A177E7C` |
| Emulator | **Eden** (tested: Eden Nightly `de7e6e01d4`, October 2026) |
| Platforms | Eden for PC and Android |

Tested on Windows 11 with an RTX 4070 SUPER: **120 FPS** holds a steady 120 (8.33 ms frame time) and plays at normal
game speed, and **240 FPS** holds 237–240 (4.17 ms) on the title screen. How close you get in heavy areas depends on
your CPU and GPU. Android uses the same Eden code, so the mod should work there too; reaching 120 FPS depends on
your device.

Other game versions have different code, so this patch won't apply (Eden only loads it for the matching build ID).
Ryujinx and real Switch hardware don't support the trick this mod relies on (see *How it works*).

## Installation

1. Download this repository (green **Code** button → *Download ZIP*) or grab a release.
2. Copy **one** of the folders from `mods/` into Silksong's mod folder:
   - **PC (Windows):** right-click Silksong in Eden → *Open Mod Data Location*
     (usually `%APPDATA%\eden\load\010013C00E930000\`)
   - **Android:** `Android/data/dev.eden.eden_emulator/files/load/010013C00E930000/`
     (or use *Game settings → Add-ons → Install* in Eden)
3. The result should look like `load/010013C00E930000/120 FPS/exefs/DC3E4B892043EF2345C3EAF97A177E7C.ips`.
4. Start Silksong. Eden's status bar should show 120 (or 240) FPS after the title screen loads.

Only enable **one** of the two mods at a time. They patch the same instructions.

### Which one should I use?

- **120 FPS:** 120 Hz or 144 Hz displays, laptops, Android handhelds. Recommended for most people.
- **240 FPS:** 240 Hz monitors and fast PCs.
- **Other refresh rates (experimental, untested):** `python tools/build_patches.py --hz 144` builds a 144 FPS version.

For the smoothest result, set Eden's VSync to FIFO or Mailbox and leave *Frame Pacing Mode* on *Auto*.
Don't combine this mod with Eden's frame generation.

## Troubleshooting

- **Still 60 FPS:** check that the v1.0.28324 update is installed (*Properties → Add-ons*). Then
  check Eden's log (`log/eden_log.txt`) for `Applying IPS patch from mod "120 FPS"`. If that line is missing, the
  folder is in the wrong place or the game version doesn't match.
- **Below the target in busy areas:** your PC or phone can't keep up. Try the 120 FPS version or lower the resolution.

## How it works

Silksong is a Unity game. On Switch, Unity's NVN graphics backend creates the game window with a present interval of
`max(vSyncCount, 1)` = 1. Unity paces each frame on the console's 60 Hz display vsync signal, which caps the game at 60 FPS
regardless of `Application.targetFrameRate`.

Eden (inherited from yuzu) has an extension for high-FPS mods: a swap interval of 5 or more is read as
*speed = interval / 100* for its emulated display vsync. Handing NVN an interval of **200** makes Eden's vsync run at
2× (**120 Hz**), and **400** makes it 4× (**240 Hz**). Unity keeps its own interval of 1, so it still renders one frame per
vsync, now 120 or 240 times a second. The game measures time with the real clock, so it plays at normal speed.

An interval of 0 (Eden's other extension) doesn't work here: NVN doesn't pass 0 through, so the game stays at 60.

| Address (`main`) | Original | Patched (120 / 240 FPS) |
| --- | --- | --- |
| `0x120AF34` (window builder) | `ldr w1, [x21, #0x6f8]` | `mov w1, #200` / `#400` |
| `0x11F27A8` (interval setter) | `add x8, x8, #0xc40` | `ldr x2, [x8, #0xc40]` |
| `0x11F27AC` (interval setter) | `ldr x2, [x8]` | `mov w1, #200` / `#400` |

IPS offsets are the address + `0x100` (NSO header). Readable versions are in [`pchtxt/`](pchtxt).
`tools/build_patches.py` regenerates everything from this table.

## FAQ

**Does Silksong run faster than normal at 120 FPS?** No. Movement, physics and timers run at normal speed; only the frame rate goes up.

**Is this frame generation or interpolation?** No. Every frame is a real frame rendered by the game.

**Does it work on a real Nintendo Switch / Switch 2?** No. It relies on an Eden emulator feature.

**Does it work in Ryujinx, Citron, Sudachi or other yuzu forks?** Ryujinx: no. Other yuzu forks: possibly, if they kept
yuzu's swap-interval speed extension. Untested.

**Does it change my saves?** No. It only patches code in memory when the game starts.

## License & disclaimer

The patches, docs and tools are MIT licensed (see [LICENSE](LICENSE)). This repository contains no game code, assets
or keys. You need your own legally obtained copy of Hollow Knight: Silksong. Not affiliated with or endorsed by
Team Cherry, Nintendo or the Eden project. Hollow Knight: Silksong is a trademark of Team Cherry.
