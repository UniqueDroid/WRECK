# Test protocol: <build/version>

**What it is:** <one line>
**What it changes (exactly one thing):** <one line>
**Base version (last confirmed on the device):** <version, SHA-256>

## Before

- [ ] Battery above 50 %, phone nearby, no other Bluetooth apps connected
- [ ] Rescue kit ready (original firmware + last confirmed version, hashes checked)
- [ ] Way back run through once

## Procedure

| Step | Do | Expected | Observed (photo/video?) |
| --- | --- | --- | --- |
| 1 | install the build via … | progress to 100 %, reboot |  |
| 2 | … | … |  |

## If something goes wrong

1. <hardware reset, if any, e.g. hold button X for N seconds>
2. <way back: app …, file …, mind the connection window>
3. Mark the build **withdrawn**, add the observation to the ledger.

## Result

- [ ] confirmed  - [ ] partly  - [ ] failed → withdrawn

Ledger entry: `wreck ledger <device> "<statement>" --status confirmed-on-device --source "test protocol <date>"`
