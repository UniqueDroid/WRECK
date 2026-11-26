# Legal framework

> **Not legal advice.** This page summarises the rules WRECK follows and the provisions they rest on (as of
> November 2026, Germany/EU). If in doubt, ask a lawyer. Other rules apply outside the EU (e.g. in the US,
> DMCA § 1201 with its own exemptions).

## In short

WRECK helps you understand **your own, lawfully acquired device**, fix its bugs and make it work with **software you
wrote yourself**. Vendor material stays private; only your own tools, your own text and the facts needed for
interoperability are published.

## What this rests on

| Provision | Content (simplified) | Meaning for WRECK |
| --- | --- | --- |
| § 69d(3) UrhG (Art. 5(3) Software Directive 2009/24/EC) | A lawful user may observe, study and test how a program works to determine the ideas and principles behind it. | Look at strings, entropy, runtime behaviour and the Bluetooth traffic of your own watch. |
| § 69d(1) UrhG (Art. 5(1)) | Copying and adapting as far as needed for the intended use, including error correction. In 2021 the CJEU held (C‑13/20, *Top System*) that this can include decompiling. | Find and fix bugs in your own firmware/app. |
| § 69e UrhG (Art. 6) | Decompiling without permission is allowed if it is indispensable to obtain the information needed for the **interoperability of an independently created program**; only by lawful users, only where the information is not already readily available, only for the necessary parts. The information must not be used for other purposes, must only be given to others where necessary for interoperability, and must not be used to create a substantially similar program. | Interfaces, file formats, update path for your own apps, watch faces and firmware. |
| § 69g(2) UrhG (Art. 8) | These rights cannot be excluded by contract. | A "no reverse engineering" clause in terms of use does not override § 69d(3) and § 69e. |
| § 3(1) no. 2 GeschGehG (Art. 3(1)(b) Trade Secrets Directive 2016/943) | Observing, studying, disassembling or testing a product is lawful if it has been made available to the public or is lawfully in your possession and you are under no duty to limit acquisition of the secret. | Hardware examination of the watch you bought. No NDA/developer contract signed? Then this applies. |
| § 69a(5) UrhG | The rules on technological protection measures (§§ 95a–95d) do not apply to computer programs. | WRECK still does not bypass copy protection or paywalls (see below) – that is our rule, not just the law. |

## Binding rules for this repo (stricter than the law)

**Never in the repo** – `wreck guard` and the pre-commit hook enforce this:

1. Vendor firmware, update files, flash dumps, companion apps (`.bin`, `.ufw`, `.apk`, …), not even in part.
2. Vendor SDKs or source code without a free licence ("All Rights Reserved").
3. Decompiler output (Smali, Ghidra C, Jadx Java) of vendor code. Put the findings into **your own words** as a format
   description or a table of facts.
4. Keys, certificates, signing keystores, credentials, tokens – not even "just for testing".
5. Personal data: MAC addresses, serial numbers, health data, photos of people, app account data.

**Out of scope for WRECK** – agents decline such tasks:

- Bypassing paid features, licence checks or subscription locks; copying or distributing paid watch faces.
- Attacking other people's devices, hijacking pairings, sniffing other people's Bluetooth traffic.
- Mass-querying vendor servers, using other people's accounts, "mirroring" catalogues.
- Building clones: firmware or an app that essentially reproduces the vendor product (§ 69e(2) no. 3).
- Changing radio parameters (transmit power, channels, frequencies). This can void conformity under the Radio
  Equipment Directive 2014/53/EU.
- Presenting health features as medical. A hobby watch is not a medical device.
- Using vendor trademarks or logos in a way that makes your own builds look like originals.

## What may be published

| May go into the repo | Stays in `private/` |
| --- | --- |
| your own tools, scripts, tests | vendor firmware, dumps, APKs, resources |
| your own apps, watch faces, fonts with a free licence | images, texts, fonts carved out of those |
| format descriptions in your own words (`docs/formats/`) | decompiler projects, disassembly listings |
| hardware facts: chip, display, pins, buses, addresses | addresses *inside* the vendor firmware, patch locations |
| checksums of vendor files (for recognition) | your own builds that contain vendor code |

Your own builds that contain vendor code (patched firmware) are for **your own device**. Pass them on only if you are
sure that is allowed – when in doubt, don't.

## For AI agents

Before writing anything to a watch, publishing anything or touching vendor files: run `wreck next <device>` and respect
the phase. If a task falls under "Out of scope for WRECK", say so clearly and offer the permitted alternative (e.g. an
original watch face instead of a copy of a paid one).
