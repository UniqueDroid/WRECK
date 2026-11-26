# AGENTS.md – instructions for AI agents

You are helping a human understand and customise **their own Chinese smartwatch**. This repo is your blueprint. It
applies to every agent (Claude, Codex, Gemini, Copilot, Cursor, local models).

## Start (always)

```sh
pip install -e .            # or: python3 -m wreck …  (standard library only)
wreck brief <device>        # this file + current state
wreck --json next <device>  # current phase, open facts, whether writing to the watch is allowed
```

No device yet? `wreck init "<model name>"` and ask the human to fill in `devices/<id>/LEGAL-ACK.md`.

## Hard rules

1. **LEGAL.md applies.** Vendor firmware, APKs, dumps, SDK source, decompiler output, keys and personal data belong in
   `private/` and **never** in a commit. Run `wreck guard` before every commit.
2. **Do not support:** bypassing paywalls/licence checks, attacking other people's devices, mass-querying vendor
   servers, building clones, changing radio parameters. Say so briefly and offer the permitted alternative.
3. **Way back before experiment.** While `write_to_device_allowed` is false, offer nothing for flashing – only analysis
   and preparation. See `docs/RECOVERY.md`.
4. **One change per build**, with a byte-diff verifier and a test protocol (`templates/test-protocol.md`).
5. **Honest evidence levels** (`docs/EVIDENCE.md`). `confirmed-on-device` only after feedback from the human wearing
   the watch. Never write "works" when only the PC has checked it.
6. **Agree on major steps first:** flashing, publishing, pushing to `main`, deleting – ask before doing it.

## Workflow

| Phase | Goal | Main tools |
| --- | --- | --- |
| 0-legal | framework confirmed | `LEGAL.md`, `LEGAL-ACK.md` |
| 1-identify | chip, companion app | `wreck apk`, `wreck identify`, factory menu |
| 2-acquire | own firmware as a file | `wreck provenance` |
| 3-recovery | way back proven | `docs/RECOVERY.md` |
| 4-understand | hardware, formats | `wreck entropy/strings/scan/watchface`, `docs/TOOLS.md` |
| 5-modify | smallest change, verified | verifier, `wreck report` |
| 6-app-layer | own apps without new firmware | `docs/APP-LAYER.md` |

In detail: `docs/PLAYBOOK.md`. Example device with real results: `devices/m78-jl701n/`.

## Recording results

```sh
wreck fact <device> display '{"w":368,"h":448,"bus":"QSPI"}' --status verified-on-pc --evidence "wreck scan"
wreck ledger <device> "<statement>" --status suspected --source "<where from>"
wreck report <device> "<title>"
wreck check                 # profiles valid?
wreck guard                 # nothing forbidden in the repo?
python3 -m unittest discover -s tests
```

## Style

- Everything in this repo is written in English: docs, code, comments, profiles, reports, commit messages. Talk to
  the human in their language, but write repo content in English.
- Plain words, result first.
- For downloads/test builds always state: what it is, what it changes, how to test it, how to get back.
- New findings about chips or formats → `wreck/data/hints.json`, `docs/CHIPS.md`, `docs/formats/` (with a source).
