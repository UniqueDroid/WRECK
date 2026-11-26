# WRECK – Watch Reverse Engineering & Cracking Kit

**Blueprint and toolkit for understanding and customising your own Chinese smartwatch – with an AI as your helper.**

Hand this repo and your watch to an AI (Claude, Codex, Gemini, …): it finds the rules, a phased workflow, a CLI for
analysis and a fully worked example device. Everything is built so that it stays **lawful** and **nothing breaks that
cannot be repaired**.

## What it does

- **Phased blueprint** with gates: identify → acquire → **prove the way back** → understand → modify → own apps
  (`docs/PLAYBOOK.md`). `wreck next` tells you what is allowed next – including whether anything may be written to
  the watch yet.
- **Risk-free analysis:** file type, entropy map, strings (including Chinese/GBK), chip hints, display init tables,
  embedded images, BLE UUIDs, companion app inventory, JieLi watch faces.
- **Legal guard rails:** `LEGAL.md` plus `wreck guard` (pre-commit), which keeps firmware, APKs, decompiler output,
  keys and MAC addresses out of the repo.
- **Evidence tracking:** device profile with status values, evidence ledger, provenance records, report templates.

## Quick start

Requires Python 3.10+, no other dependencies.

```sh
git clone https://github.com/UniqueDroid/WRECK && cd WRECK
pip install -e .                 # or without installing: python3 -m wreck …
git config core.hooksPath hooks  # run wreck guard before every commit

wreck init "My Watch X9"         # creates devices/my-watch-x9 and private/my-watch-x9
# fill in devices/my-watch-x9/LEGAL-ACK.md
wreck next my-watch-x9           # next step according to the playbook
wreck apk private/my-watch-x9/apk/app.apk
wreck identify private/my-watch-x9/firmware/update.bin
```

With an AI: open the repo and say *"Read AGENTS.md and help me with my watch"*. The agent starts with
`wreck brief <device>`.

## Commands

| Command | Purpose |
| --- | --- |
| `wreck identify FILE` | type, entropy, chip hints, display resolution, assessment |
| `wreck entropy FILE` | regions: code, tables, empty, encrypted/compressed |
| `wreck strings FILE [--grep X]` | ASCII, UTF-16 and GBK strings with offsets |
| `wreck scan FILE [--extract DIR]` | JPEG/PNG, MIPI display init, BLE UUIDs, URLs |
| `wreck apk APK` | SDKs, UUIDs, servers, bundled firmware of a companion app |
| `wreck watchface FILE` | read a JieLi ("JL") watch face |
| `wreck init / next / fact / ledger / provenance / report / check` | device profile and evidence |
| `wreck guard [--staged]` | nothing forbidden in the repo? |
| `wreck brief [DEVICE]` | briefing for AI agents |

Use `wreck --json …` for machine-readable output.

## Layout

```
AGENTS.md / CLAUDE.md / llms.txt   entry points for AI agents
LEGAL.md                           legal framework and repo rules
docs/                              playbook, recovery, chips, app layer, evidence, tools, formats
wreck/                             CLI (Python, standard library only)
devices/_template/                 empty profile
devices/m78-jl701n/                example: M78 with JieLi JL701N
templates/                         report, test protocol
hooks/pre-commit                   runs wreck guard
private/                           your raw data – excluded via .gitignore
```

## Origin

Grew out of work on an M78 watch (JieLi JL701N): customised firmware, own recovery routes, an own JavaScript app
layer. WRECK contains **only** the method, own tools and hardware facts from that work – no vendor files.

## Licence and liability

MIT (see `LICENSE`). Modifying firmware can brick devices and void warranties. Not legal advice – see `LEGAL.md`.
