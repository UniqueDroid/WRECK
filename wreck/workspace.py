"""Device workspace: profile, evidence ledger, reports, provenance records and the next step.

Layout (see docs/EVIDENCE.md):

    devices/<id>/          publishable: profile, ledger, reports (own words and facts only)
    private/<id>/          never in the repo: firmware, dumps, APKs, decompiler output, own builds
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from pathlib import Path

STATUSES = ["open", "suspected", "verified-on-pc", "confirmed-on-device", "refuted"]
RANK = {s: i for i, s in enumerate(STATUSES)}

FACT_KEYS = {
    "companion_app": "Companion app (name, package, version)",
    "chip": "SoC / chip family",
    "flash_layout": "Flash layout (internal/external, banks, regions)",
    "update_path": "How firmware gets onto the watch (DFU/OTA flow)",
    "recovery": "Proven way back if an experiment fails",
    "display": "Display (resolution, interface, controller)",
    "touch": "Touch controller (bus, address, pins)",
    "buttons": "Buttons, crown, reset",
    "sensors": "Sensors (accelerometer, heart rate, ...)",
    "factory_menu": "Factory test / service menu",
    "app_layer": "Own app layer (e.g. script apps)",
}

PHASES = [
    ("0-legal", "Confirm the legal framework", "Read LEGAL.md; answer devices/<id>/LEGAL-ACK.md and set `confirmed: yes`."),
    ("1-identify", "Identify device and companion app", "companion_app and chip at least 'suspected'. Tools: wreck apk, wreck identify, factory menu, label/FCC ID."),
    ("2-acquire", "Obtain your own firmware lawfully", "At least one provenance record (wreck provenance) for a file from your own device or your own app install."),
    ("3-recovery", "Prove the way back – BEFORE any write to the watch", "update_path >= verified-on-pc and recovery = confirmed-on-device. Until then: flash nothing."),
    ("4-understand", "Understand hardware and formats", "display, touch, buttons at least 'verified-on-pc', with evidence in the ledger."),
    ("5-modify", "Build and verify the smallest possible change", "One change per build, byte-diff verifier, test protocol (templates/test-protocol.md)."),
    ("6-app-layer", "Build your own app layer", "app_layer at least 'verified-on-pc' (docs/APP-LAYER.md)."),
]


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not s:
        raise ValueError("Empty identifier")
    return s


def now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def empty_profile(device_id: str, name: str) -> dict:
    return {
        "schema": "wreck-profile/1",
        "id": device_id,
        "name": name,
        "aliases": [],
        "sold_as": [],
        "facts": {k: {"value": None, "status": "open", "evidence": [], "label": label} for k, label in FACT_KEYS.items()},
        "notes": [],
    }


LEGAL_ACK = """# Legal framework for this device

Read ../../LEGAL.md first. Then answer every line honestly (yes/no).

- The device was lawfully acquired and is in my possession: yes/no
- No contract or NDA forbids examining it: yes/no
- The goal is interoperability, bug fixing or my own use (no clone, no bypassing paid features): yes/no
- Vendor files stay in private/ and are not published: yes/no
- Radio parameters (transmit power, frequencies) will not be changed: yes/no

confirmed: no
"""


def init(root: Path, name: str) -> Path:
    device_id = slug(name)
    dev = root / "devices" / device_id
    if dev.exists():
        raise FileExistsError(f"{dev} already exists")
    (dev / "reports").mkdir(parents=True)
    priv = root / "private" / device_id
    for d in ("inbox", "firmware", "apk", "dumps", "decompiled", "builds"):
        (priv / d).mkdir(parents=True, exist_ok=True)
    (dev / "profile.json").write_text(json.dumps(empty_profile(device_id, name), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dev / "ledger.jsonl").write_text("", encoding="utf-8")
    (dev / "provenance.jsonl").write_text("", encoding="utf-8")
    (dev / "LEGAL-ACK.md").write_text(LEGAL_ACK, encoding="utf-8")
    (dev / "README.md").write_text(
        f"# {name}\n\nWRECK device profile. Status of all facts: `profile.json`. Evidence: `ledger.jsonl`.\n"
        f"Next step: `wreck next {device_id}`.\n", encoding="utf-8")
    return dev


def device_dir(root: Path, device_id: str) -> Path:
    d = root / "devices" / device_id
    if not (d / "profile.json").exists():
        raise FileNotFoundError(f"No profile in {d}. Run `wreck init` first.")
    return d


def load_profile(dev: Path) -> dict:
    return json.loads((dev / "profile.json").read_text(encoding="utf-8"))


def save_profile(dev: Path, profile: dict) -> None:
    (dev / "profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_profile(profile: dict) -> list[str]:
    errs = []
    if profile.get("schema") != "wreck-profile/1":
        errs.append("schema must be 'wreck-profile/1'")
    for k in ("id", "name", "facts"):
        if k not in profile:
            errs.append(f"missing field: {k}")
    facts = profile.get("facts", {})
    for k in FACT_KEYS:
        if k not in facts:
            errs.append(f"missing fact: {k}")
    for k, f in facts.items():
        st = f.get("status")
        if st not in STATUSES:
            errs.append(f"{k}: invalid status {st!r} (allowed: {', '.join(STATUSES)})")
        if st in ("verified-on-pc", "confirmed-on-device") and not f.get("evidence"):
            errs.append(f"{k}: status {st} needs at least one piece of evidence")
        if st != "open" and f.get("value") in (None, ""):
            errs.append(f"{k}: status {st} without a value")
    return errs


def set_fact(dev: Path, key: str, value, status: str, evidence: str | None) -> dict:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    p = load_profile(dev)
    f = p["facts"].setdefault(key, {"value": None, "status": "open", "evidence": [], "label": key})
    f["value"] = value
    f["status"] = status
    if evidence:
        f["evidence"].append(evidence)
    save_profile(dev, p)
    return f


def add_ledger(dev: Path, claim: str, status: str, source: str, fact: str | None = None) -> dict:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    lines = (dev / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    entry = {"id": f"E{len(lines) + 1:04d}", "time": now(), "claim": claim, "status": status, "source": source}
    if fact:
        entry["fact"] = fact
    with (dev / "ledger.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def provenance(dev: Path, file: Path, origin: str, how: str) -> dict:
    data = file.read_bytes()
    entry = {
        "time": now(),
        "name": file.name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "origin": origin,
        "how": how,
        "publishable": False,
    }
    with (dev / "provenance.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def new_report(root: Path, dev: Path, title: str) -> Path:
    tpl = root / "templates" / "report.md"
    body = tpl.read_text(encoding="utf-8") if tpl.exists() else "# {title}\n"
    day = _dt.date.today().isoformat()
    path = dev / "reports" / f"{day}-{slug(title)}.md"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(body.replace("{title}", title).replace("{date}", day).replace("{device}", dev.name), encoding="utf-8")
    return path


def _acked(dev: Path) -> bool:
    f = dev / "LEGAL-ACK.md"
    if not f.exists():
        return False
    text = f.read_text(encoding="utf-8")
    answers = [l for l in text.splitlines() if l.startswith("- ")]
    all_yes = bool(answers) and all(re.search(r":\s*yes\s*$", l, re.I) for l in answers)
    return all_yes and bool(re.search(r"^confirmed:\s*yes\s*$", text, re.M | re.I))


def _at_least(profile: dict, key: str, status: str) -> bool:
    st = profile["facts"].get(key, {}).get("status", "open")
    return st != "refuted" and RANK.get(st, 0) >= RANK[status]


def next_step(dev: Path) -> dict:
    p = load_profile(dev)
    pf = dev / "provenance.jsonl"
    prov = [l for l in pf.read_text(encoding="utf-8").splitlines() if l.strip()] if pf.exists() else []
    gates = [
        _acked(dev),
        _at_least(p, "companion_app", "suspected") and _at_least(p, "chip", "suspected"),
        len(prov) > 0,
        _at_least(p, "update_path", "verified-on-pc") and _at_least(p, "recovery", "confirmed-on-device"),
        all(_at_least(p, k, "verified-on-pc") for k in ("display", "touch", "buttons")),
        any((dev / "reports").glob("*test*")) or _at_least(p, "app_layer", "suspected"),
        _at_least(p, "app_layer", "verified-on-pc"),
    ]
    done = [PHASES[i][0] for i, ok in enumerate(gates) if ok]
    for i, ok in enumerate(gates):
        if not ok:
            code, title, todo = PHASES[i]
            open_facts = [k for k, f in p["facts"].items() if f["status"] in ("open", "suspected")]
            return {
                "device": p["id"],
                "phase": code,
                "title": title,
                "todo": todo,
                "write_to_device_allowed": i > 3,
                "done": done,
                "open_facts": open_facts,
                "playbook": f"docs/PLAYBOOK.md#phase-{code}",
            }
    return {"device": p["id"], "phase": "done", "title": "All phases complete", "write_to_device_allowed": True, "done": done}
