# Evidence, profiles, reports

## Layout

```
devices/<device>/
  profile.json       facts with status and evidence (schema wreck-profile/1)
  ledger.jsonl       evidence ledger: one statement per line, with status and source
  provenance.jsonl   origin of private files (name, size, SHA-256, where from, how)
  LEGAL-ACK.md       confirmation of the legal framework
  reports/           reports (own words)
private/<device>/    NEVER in the repo: inbox, firmware, apk, dumps, decompiled, builds
```

## Status values

| Status | Meaning | Who may set it |
| --- | --- | --- |
| `open` | unknown | – |
| `suspected` | hint, not verified (strings, teardown of a sibling model) | human, agent |
| `verified-on-pc` | backed by analysis/model/test on the PC | human, agent (with evidence) |
| `confirmed-on-device` | observed on the real watch | **only** after feedback from the human with the watch |
| `refuted` | checked and wrong | human, agent (with evidence) |

`wreck check` rejects profiles whose status is ≥ `verified-on-pc` without evidence.

## Ledger

```
wreck ledger <device> "Touch controller answers on I²C 0x2E" --status confirmed-on-device --source "diagnostic app, photo 2" --fact touch
```

Sources in your own words. Addresses inside the vendor firmware belong in private notes only, not in the public ledger.

## Reports

`wreck report <device> "<title>"` creates a report from `templates/report.md`. Structure: result first, then
verified / suspected / open, then downloads (own files only), then the way back. A report never ends with "works" if no
device test took place.
