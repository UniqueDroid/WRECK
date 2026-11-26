# Format: JieLi watch face "JL" (368 × 448)

Description in our own words, obtained for interoperability (own watch faces for your own watch). Checked against the
watch faces of an M78 (JieLi JL701N); status per part below. Reader: `wreck watchface <file>`.

## Layout

| Position | Content |
| --- | --- |
| byte 0 | number of elements (the watch reads at most 88) |
| byte 1 | 0 |
| bytes 2–3 | ASCII `JL` |
| from byte 4 | 24 bytes per element |
| after that | image data referenced by the elements |

## Element (24 bytes, little endian)

| Offset | Size | Content |
| --- | --- | --- |
| 0 | 1 | type (table below) |
| 1 | 1 | visibility: 0 normal, 1 skipped, 2 only in dimmed always-on mode |
| 2 | 2 | x |
| 4 | 2 | y |
| 6 | 1 | number of images in the image block |
| 7 | 1 | image format: 2 = run-length-encoded RGB565, 8 = with alpha |
| 8 | 2 | colour or start angle (depends on type) |
| 10 | 2 | width |
| 12 | 2 | height |
| 14–15 | 2 | group id or end angle |
| 16 | 4 | offset of the image data in the file |
| 20 | 1 | per type: digit spacing, number of steps, pivot x, action of a tap area |
| 21 | 1 | alignment: 0 left, 1 centre, 2 right |
| 22 | 1 | per type: vertical offset, pivot y, frame interval |
| 23 | 1 | variant (language, day/night) |

## Image block

`(n + 1)` 32-bit values (first = `4 × (n + 1)`, last = block size), then `n` images.

- **Format 2:** one 32-bit entry per row (position in bits 0–20, length in bits 21–31); rows run-length encoded
  (count byte: bit 7 set = one pixel repeated n times, otherwise n literal pixels); pixels RGB565, **high byte first**.
- **Format 8:** 3 bytes per pixel (alpha, then RGB565), either with a row table and run lengths like format 2, or raw
  with rows padded to 4 bytes (rotated images such as hands).

## Types (selection)

| Area | Types |
| --- | --- |
| Images | `01` image, `02` image sequence, `03` style image |
| Digital time | `32` hour, `33` minute, `3B` second, `3E/3F` hour tens/units, `40/41` minute tens/units, `67` AM/PM |
| Analogue time | `36` hour hand, `37` minute hand, `38/39/3D` second hands, `42` 24-hour hand |
| Date | `34` month, `35` day, `3C` year, `63/64` weekday |
| Device | `65` Bluetooth, `66/68` battery, `9C` unread notifications |
| Activity/health | `96` steps, `97` calories, `98` heart rate, `99` distance, `9E` blood oxygen, `A0–A2` progress |
| Interaction | `B4` tap area, `E6` tap area around the following element |

Full list of names: `wreck/formats/jl_watchface.py`.

## Status

| Part | Status |
| --- | --- |
| Header, element, types of the vendor watch faces | verified on PC (all market files of an M78 readable, previews match the market images) |
| Image formats 5 and 6, types `06`, `14`, `E7–E9` | open |
| Self-made watch face on the watch | open |
