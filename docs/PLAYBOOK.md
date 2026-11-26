# Playbook: from an unknown Chinese watch to your own customisation

This playbook is the blueprint. It applies to humans and AI agents alike. Every phase has a **gate**: you only move
on once it is open. `wreck next <device>` checks the gates using `devices/<device>/profile.json`, `ledger.jsonl` and
`provenance.jsonl`.

The lessons come from a real project (an M78 watch with a JieLi JL701N, see `devices/m78-jl701n`): dozens of firmware
test builds, one boot loop, a hard-won way back. The rules below are therefore not theoretical.

## The five ground rules

1. **Way back before experiment.** Nothing is written to the watch before it is proven how to get back.
2. **One change per build.** Two changes in one build = when it fails, nobody knows which one is to blame.
   (On the M78, a boot logo and an AOD change went into the same build – boot loop, cause unclear for a long time.)
3. **Keep evidence levels honest.** `suspected` → `verified-on-pc` → `confirmed-on-device`. Only the human wearing the
   watch can set `confirmed-on-device`. An agent never writes "works" when only the PC has checked it.
4. **Byte diff, not gut feeling.** Every build has a verifier that compares *all* bytes outside the intended change
   locations against the base image.
5. **Withdrawn builds stay withdrawn.** Mark them with the reason, never offer them again.

---

## Phase 0-legal

**Goal:** It is clear the work is allowed. **Gate:** `devices/<device>/LEGAL-ACK.md` answered "yes" throughout.

- Read `LEGAL.md`. Watch bought lawfully, no NDA, goal is interoperability/bug fixing/own use.
- Agents: if the request falls under "Out of scope for WRECK", decline and offer the permitted alternative.

## Phase 1-identify

**Goal:** Know the device, chip and companion app. **Gate:** `chip` and `companion_app` at least `suspected`.

Without opening the watch, in this order:

1. **Companion app** (name from the manual/QR code). Save the APK from *your own* install
   (`adb shell pm path <package>`, then `adb pull`) into `private/<device>/apk/`, record provenance with
   `wreck provenance`.
2. `wreck apk private/<device>/apk/app.apk`: SDK packages (`com/jieli/`, `com/realsil/`, …), BLE UUIDs, servers,
   bundled firmware. **Note:** companion apps often serve several chip families; an SDK inside the app is a hint, not
   proof.
3. Look for the **factory test / service menu** (often a hidden tap sequence in Settings → System). It shows
   firmware/hardware version, sensors, touch test. Photos of it are good evidence.
4. Label, FCC ID, Bluetooth name, teardown videos of similar watches (the same board is sold under many names –
   `sold_as` in the profile).
5. `docs/CHIPS.md` for typical markers of each chip family.

```
wreck init "My Watch X9"
wreck fact my-watch-x9 companion_app '{"name":"DeeFit Pro","package":"…"}' --status suspected --evidence "manual, QR code"
```

## Phase 2-acquire

**Goal:** The firmware of your own watch as a file. **Gate:** at least one entry in `provenance.jsonl`.

Lawful routes, from easiest to hardest:

1. **The update file your own app downloads for your own watch** (app cache, downloads folder, assets bundled in the
   APK). Once, for your own device – no mass downloads from the vendor server.
2. **Capture of your own Bluetooth transfer** during an official update (Android: HCI snoop log).
3. **Read-out via an existing function** (e.g. a flash read command the firmware already supports).
4. **Hardware** (UART/SWD/test points) – only if the human explicitly wants to open the watch.

Everything goes into `private/<device>/…`, never into the repo. Every file gets a provenance record:

```
wreck provenance my-watch-x9 private/my-watch-x9/firmware/ota.bin --origin "own app 2.3.1, cache" --how "adb pull"
```

## Phase 3-recovery

**Goal:** Prove how to get back after a failed experiment. **Gate:** `update_path` ≥ `verified-on-pc` **and**
`recovery` = `confirmed-on-device`. **Nothing is written to the watch before this.**

Details and patterns: `docs/RECOVERY.md`. In short, these questions must be answered:

- How many firmware slots are there (single or dual bank)? Does an old copy survive an update?
- Does the bootloader fall back when an app crashes? (On the M78: **no**.)
- Which part of the update needs the running app (Bluetooth), which only the bootloader/loader?
- Is there a hardware reset via a button (M78: crown for 8 s)? It only helps against hangs, not against broken firmware.
- Is the unmodified original firmware available as a file, checked and recorded with its hash?

The very first device test: re-install the **unmodified original firmware** via the official route. Only after that,
firmware with a single harmless change (e.g. a version string).

## Phase 4-understand

**Goal:** Know the hardware and formats as far as the customisation needs. **Gate:** `display`, `touch`, `buttons` ≥
`verified-on-pc`.

Tools in WRECK (read-only):

| Question | Command |
| --- | --- |
| Where is code, where is data, what is encrypted? | `wreck entropy file` |
| Which texts, including Chinese (GBK)? | `wreck strings file --grep test` |
| Display resolution, init table? | `wreck scan file` (looks for MIPI DCS `2A`/`2B`) |
| Embedded images (boot logo, icons)? | `wreck scan file --extract private/<device>/images` |
| Understand a watch face file? | `wreck watchface file` |

External tools (Ghidra, Jadx, Apktool, processor modules) and how to use them cleanly: `docs/TOOLS.md`.

Proven shortcuts:

- **Find the matching chip SDK.** Many Chinese watches are built with publicly available chip SDKs. The same structure
  in SDK and firmware (tables, structs, function order) saves weeks. Use the SDK locally only and respect its licence.
- **Compare sibling models.** The same board ships in many models; firmware from several of them shows what is shared
  (bootloader, drivers) and what is model-specific.
- **Diagnose instead of guessing.** A small diagnostic app of your own on the watch (read memory, log buttons) answers
  pin questions faster than any static analysis (M78: display and button pins were confirmed this way).

Every finding goes into the ledger:

```
wreck ledger my-watch-x9 "Display 368x448, init table with 2A/2B" --status verified-on-pc --source "wreck scan, offset in private report" --fact display
```

## Phase 5-modify

**Goal:** The smallest change that fulfils the wish – built, verified, tested. No fixed gate; the result is a report
with a test protocol.

Means in order of risk, lowest first:

1. **No firmware change:** your own watch face, your own texts/language packs via existing routes, your own companion
   app (interoperability over the existing Bluetooth protocol).
2. **Small firmware patch** at exactly one location, with a byte-diff verifier.
3. **Your own app layer** inside the vendor firmware (phase 6).
4. **Your own firmware** – only with a proven, independent way back.

Mandatory for every build:

- unique version name (e.g. `4.50.12_TEST`), one change, one changelog line
- verifier output (JSON) with: base hash, new hash, changed regions, "not tested on device"
- test protocol from `templates/test-protocol.md` for the human: what to do, what to expect, how to get back
- analysis by-products that must not be flashed are named `…-NOT-FLASHABLE…`

## Phase 6-app-layer

**Goal:** Instead of patching every feature into the firmware, add a small runtime once that loads your own apps.
Pattern, permission model and limits: `docs/APP-LAYER.md`.

---

## How AI agents work with this

- At the start: `wreck brief <device>` or `wreck --json next <device>`. Only work on tasks of the current phase.
- `write_to_device_allowed: false` means: offer no firmware or patch for flashing, only analysis and preparation.
- Create reports with `wreck report <device> "<title>"`; every statement gets an evidence level.
- Before every commit: `wreck guard`. Never commit vendor material, not even in subfolders.
- When the human confirms something on the device (photo, description), add it to the ledger as the source
  ("device test on 19 Nov, photo 3").
