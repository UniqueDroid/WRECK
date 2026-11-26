# Chip families in Chinese watches

A starting point, not an encyclopedia. Column "Confidence": **confirmed** = proven on a device in this repo,
**hint** = common assumption, verify on your own device. Add entries only with a source (device, teardown, datasheet).
The same patterns are in machine-readable form in `wreck/data/hints.json` and are used by `wreck identify`.

| Family | Typical markers | Public resources | Confidence |
| --- | --- | --- | --- |
| **JieLi BR28** (AC701N / JL701N) | strings `JL701N`, `isd_config`, `uboot.boot`, `ota.bin` in the update; CPU architecture pi32v2; QSPI AMOLED; large parts of the update encrypted (high entropy) | GitHub organisation *Jieli-Tech* (SDKs, Android OTA libraries); community: *kagaimiq/jl-misctools* (formats, tools), *quarkslab/ghidra-jieli* (processor module, incomplete) | confirmed (M78) |
| JieLi BR23/BR25/BR35 | similar containers and strings, different chip names | as above | hint |
| Realtek Bee (RTL876x) | `realsil` packages in the app, Realtek OTA | SDK partly only via distributors | hint |
| Actions (ATS30xx) | strings `ATS30…`; own OTA formats | little public | hint |
| SiFli (SF32LB5x) | strings `SF32LB`, `sifli` | vendor's open SDK | hint |
| Nordic nRF52 | `SoftDevice`, Nordic DFU (`FE59`) | fully documented | hint (mostly older bands) |
| Bluetrum, Telink, BES | chip names in strings | varies | hint |

## Important

- **Companion apps are multi-chip apps.** The M78 app contains a Realtek SDK although the watch has a JieLi chip.
  An SDK package in the APK is only a hint.
- **Same board, many names.** Model numbers on the box say little. More telling: firmware prefix
  (e.g. `M78_4.10.62`), bootloader hash, display init table, button table.
- **Encrypted updates** are normal. Decryption is format knowledge; WRECK deliberately ships no code and no keys for
  it. If you need it for your own device, use public community tools after checking their licence and the legal
  situation yourself, locally in `private/`.
