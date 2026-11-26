"""Gerätearbeitsplatz: Profil, Belegbuch, Berichte, Herkunftsnachweise und der nächste Schritt.

Aufteilung (siehe docs/EVIDENCE.md):

    devices/<id>/          veröffentlichbar: Profil, Belegbuch, Berichte (nur eigene Worte und Fakten)
    private/<id>/          nie im Repo: Firmware, Dumps, APKs, Decompiler-Ausgaben, eigene Builds
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from pathlib import Path

STATUSES = ["offen", "vermutet", "am-rechner-geprueft", "am-geraet-bestaetigt", "widerlegt"]
RANK = {s: i for i, s in enumerate(STATUSES)}

FACT_KEYS = {
    "companion_app": "Begleitapp (Name, Paketname, Version)",
    "chip": "SoC / Chipfamilie",
    "flash_layout": "Flash-Aufteilung (intern/extern, Bänke, Bereiche)",
    "update_path": "Wie kommt eine Firmware auf die Uhr (DFU/OTA-Ablauf)",
    "recovery": "Nachgewiesener Rückweg, falls ein Experiment schiefgeht",
    "display": "Display (Auflösung, Schnittstelle, Controller)",
    "touch": "Touch-Controller (Bus, Adresse, Pins)",
    "buttons": "Tasten, Krone, Reset",
    "sensors": "Sensoren (Beschleunigung, Puls, ...)",
    "factory_menu": "Werkstest-/Servicemenü",
    "app_layer": "Eigene App-Schicht (z. B. Skript-Apps)",
}

PHASES = [
    ("0-recht", "Rechtlichen Rahmen bestätigen", "LEGAL.md lesen; in devices/<id>/LEGAL-ACK.md `bestaetigt: ja` setzen."),
    ("1-erkennen", "Gerät und Begleitapp erkennen", "companion_app und chip mindestens auf 'vermutet'. Werkzeuge: wreck apk, wreck identify, Werkstestmenü, Typenschild/FCC-ID."),
    ("2-beschaffen", "Eigene Firmware legal beschaffen", "Mindestens ein Herkunftsnachweis (wreck provenance) für eine Datei vom eigenen Gerät oder aus der eigenen App-Installation."),
    ("3-rueckweg", "Rückweg nachweisen – VOR jedem Schreibzugriff", "update_path >= am-rechner-geprueft und recovery = am-geraet-bestaetigt. Ohne das: nichts auf die Uhr spielen."),
    ("4-verstehen", "Hardware und Formate verstehen", "display, touch, buttons mindestens 'am-rechner-geprueft'; Belege im ledger."),
    ("5-anpassen", "Kleinste mögliche Änderung bauen und prüfen", "Eine Änderung pro Build, Byte-Diff-Prüfung, Testprotokoll (templates/test-protocol.md)."),
    ("6-app-schicht", "Eigene App-Schicht aufbauen", "app_layer mindestens 'am-rechner-geprueft' (docs/APP-LAYER.md)."),
]


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not s:
        raise ValueError("Leere Kennung")
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
        "facts": {k: {"value": None, "status": "offen", "evidence": [], "label": label} for k, label in FACT_KEYS.items()},
        "notes": [],
    }


def init(root: Path, name: str) -> Path:
    device_id = slug(name)
    dev = root / "devices" / device_id
    if dev.exists():
        raise FileExistsError(f"{dev} existiert bereits")
    for d in ("reports",):
        (dev / d).mkdir(parents=True)
    priv = root / "private" / device_id
    for d in ("inbox", "firmware", "apk", "dumps", "decompiled", "builds"):
        (priv / d).mkdir(parents=True, exist_ok=True)
    (dev / "profile.json").write_text(json.dumps(empty_profile(device_id, name), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dev / "ledger.jsonl").write_text("", encoding="utf-8")
    (dev / "provenance.jsonl").write_text("", encoding="utf-8")
    (dev / "LEGAL-ACK.md").write_text(
        "# Rechtlicher Rahmen für dieses Gerät\n\n"
        "Vor der Arbeit lesen: ../../LEGAL.md. Dann jede Zeile ehrlich beantworten.\n\n"
        "- Gerät rechtmäßig erworben und in meinem Besitz: ja/nein\n"
        "- Kein Vertrag/NDA, der die Untersuchung verbietet: ja/nein\n"
        "- Ziel ist Interoperabilität, Fehlerbehebung oder eigene Nutzung (kein Nachbau, kein Umgehen von Bezahlfunktionen): ja/nein\n"
        "- Herstellerdateien bleiben in private/ und werden nicht veröffentlicht: ja/nein\n"
        "- Funkparameter (Sendeleistung, Frequenzen) werden nicht verändert: ja/nein\n\n"
        "bestaetigt: nein\n",
        encoding="utf-8")
    (dev / "README.md").write_text(
        f"# {name}\n\nGeräteprofil für WRECK. Status aller Fakten: `profile.json`. Belege: `ledger.jsonl`.\n"
        f"Nächster Schritt: `wreck next {device_id}`.\n", encoding="utf-8")
    return dev


def device_dir(root: Path, device_id: str) -> Path:
    d = root / "devices" / device_id
    if not (d / "profile.json").exists():
        raise FileNotFoundError(f"Kein Profil unter {d}. Erst `wreck init`.")
    return d


def load_profile(dev: Path) -> dict:
    return json.loads((dev / "profile.json").read_text(encoding="utf-8"))


def save_profile(dev: Path, profile: dict) -> None:
    (dev / "profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_profile(profile: dict) -> list[str]:
    errs = []
    if profile.get("schema") != "wreck-profile/1":
        errs.append("schema muss 'wreck-profile/1' sein")
    for k in ("id", "name", "facts"):
        if k not in profile:
            errs.append(f"Feld fehlt: {k}")
    facts = profile.get("facts", {})
    for k in FACT_KEYS:
        if k not in facts:
            errs.append(f"Fakt fehlt: {k}")
    for k, f in facts.items():
        st = f.get("status")
        if st not in STATUSES:
            errs.append(f"{k}: ungültiger Status {st!r} (erlaubt: {', '.join(STATUSES)})")
        if st in ("am-rechner-geprueft", "am-geraet-bestaetigt") and not f.get("evidence"):
            errs.append(f"{k}: Status {st} braucht mindestens einen Beleg (evidence)")
        if st != "offen" and f.get("value") in (None, ""):
            errs.append(f"{k}: Status {st} ohne value")
    return errs


def set_fact(dev: Path, key: str, value, status: str, evidence: str | None) -> dict:
    if status not in STATUSES:
        raise ValueError(f"Status muss einer von {STATUSES} sein")
    p = load_profile(dev)
    f = p["facts"].setdefault(key, {"value": None, "status": "offen", "evidence": [], "label": key})
    f["value"] = value
    f["status"] = status
    if evidence:
        f["evidence"].append(evidence)
    save_profile(dev, p)
    return f


def add_ledger(dev: Path, claim: str, status: str, source: str, fact: str | None = None) -> dict:
    if status not in STATUSES:
        raise ValueError(f"Status muss einer von {STATUSES} sein")
    lines = (dev / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    entry = {"id": f"B{len(lines) + 1:04d}", "time": now(), "claim": claim, "status": status, "source": source}
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
    all_yes = bool(answers) and all(re.search(r":\s*ja\s*$", l, re.I) for l in answers)
    return all_yes and bool(re.search(r"^bestaetigt:\s*ja\s*$", text, re.M | re.I))


def _at_least(profile: dict, key: str, status: str) -> bool:
    st = profile["facts"].get(key, {}).get("status", "offen")
    return st != "widerlegt" and RANK.get(st, 0) >= RANK[status]


def next_step(dev: Path) -> dict:
    p = load_profile(dev)
    pf = dev / "provenance.jsonl"
    prov = [l for l in pf.read_text(encoding="utf-8").splitlines() if l.strip()] if pf.exists() else []
    gates = [
        _acked(dev),
        _at_least(p, "companion_app", "vermutet") and _at_least(p, "chip", "vermutet"),
        len(prov) > 0,
        _at_least(p, "update_path", "am-rechner-geprueft") and _at_least(p, "recovery", "am-geraet-bestaetigt"),
        all(_at_least(p, k, "am-rechner-geprueft") for k in ("display", "touch", "buttons")),
        any((dev / "reports").glob("*test*")) or _at_least(p, "app_layer", "vermutet"),
        _at_least(p, "app_layer", "am-rechner-geprueft"),
    ]
    done = [PHASES[i][0] for i, ok in enumerate(gates) if ok]
    for i, ok in enumerate(gates):
        if not ok:
            code, title, todo = PHASES[i]
            open_facts = [k for k, f in p["facts"].items() if f["status"] in ("offen", "vermutet")]
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
    return {"device": p["id"], "phase": "fertig", "title": "Alle Phasen erfüllt", "write_to_device_allowed": True, "done": done}
