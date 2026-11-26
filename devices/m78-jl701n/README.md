# Example device: M78 (JieLi JL701N)

Reference profile from a real project. It shows what a filled-in profile looks like and which routes worked on this
watch. It contains **only hardware facts and lessons learned** – no firmware, no addresses inside the vendor firmware,
no patches.

If you own an M78 or a sibling model (e.g. ND326): create your own device with `wreck init "<your name>"` and use this
profile as a source of suspicions – only raise statuses in your own profile after checking them yourself.

## Hardware at a glance

| Part | Value | Status |
| --- | --- | --- |
| SoC | JieLi JL701N (AC701N, BR28), pi32v2, PSRAM | verified on PC |
| Flash | 2 MB internal (single bank), 16 MB external NOR | confirmed on device |
| Display | AMOLED 368 × 448, QSPI, RGB565; reset PA02, CS PA06, power PA05, no TE | confirmed on device |
| Touch | CHSC6x, I²C 0x2E on PG03/PG04, INT PG05, RESET PG06 | confirmed on device |
| Buttons | left PB01, right PG08, crown PB04 (8 s = reboot), rotary encoder PC06/PB07 | confirmed on device |
| Motor | PWM on PB06 | confirmed on device |
| Sensors | SC7A20 (accelerometer), Vcare LC09A (heart rate, I²C 0x33) | verified on PC |
| Companion app | DeeFit Pro | confirmed on device |

## What worked

1. **Factory menu and diagnostic apps instead of guessing.** Pins were confirmed with a small own app that only reads
   memory and port inputs.
2. **Find the display via its init table:** the MIPI DCS commands `2A 00 00 01 6F` / `2B 00 00 01 BF` (0…367, 0…447)
   led straight to the init sequence. `wreck scan` looks for exactly that.
3. **Matching chip SDK:** a public JL701N watch SDK has the same structures as the vendor firmware (button and display
   tables right next to each other). The SDK builds reproducibly on Linux.
4. **Risk-free way back:** own code runs from PSRAM, started by the unmodified vendor firmware. Every reboot = original.
   Later: a start program that only runs when a button is held at power-on.
5. **Own app layer:** a small JavaScript engine in the patched firmware; apps arrive as packages via the companion app.
   New features without a new firmware build.

## What went wrong (and the rule it produced)

| Event | Rule |
| --- | --- |
| Build with a new boot logo **and** an AOD change → boot loop | One change per build |
| No bootloader fallback, single bank | Way back before experiment (`docs/RECOVERY.md`) |
| Own program occupied the UI task → no notifications, no sync, no update | Own task; never block the vendor UI |
| Disassembler showed branch targets shifted by the instruction length | Cross-check tools against known functions |

## Open

Display controller ID, exact touch IC, sensor interrupt pins, charging parameters, whether the update loader can also
install from a stored file without Bluetooth.
