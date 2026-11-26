"""Kommandozeile `wreck`. Jede Ausgabe ist mit --json maschinenlesbar (für KI-Agenten)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, analyze, guard, workspace
from .formats import jl_watchface


def _out(args, obj, human=None):
    if args.json or human is None:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        human(obj)


def _root(args) -> Path:
    return Path(args.root).resolve()


# --- Analyse -----------------------------------------------------------------

def cmd_identify(args):
    r = analyze.identify(Path(args.file))

    def show(r):
        print(f"{r['file']}  {r['size']} Byte  sha256 {r['sha256'][:16]}…")
        print(f"Typ: {r['magic']['label'] if r['magic'] else 'unbekannt'}   Entropie: {r['entropy_overall']}")
        for c in r["chip_hints"][:5]:
            print(f"Chip-Hinweis: {c['family']} ({c['confidence']}): " + ", ".join(h['pattern'] for h in c['hits']))
        for d in r["display_init"][:3]:
            print(f"Display-Init? 0x{d['offset']:x}: {d['width']} x {d['height']}")
        print(f"Eingebettete Bilder: {r['embedded_images']}")
        print("Bereiche:")
        for g in r["regions"][:20]:
            print(f"  0x{g['offset']:08x}  {g['size']:>9}  {g['class']}")
        for v in r["verdict"]:
            print("→ " + v)
    _out(args, r, show)


def cmd_strings(args):
    data = Path(args.file).read_bytes()
    res = analyze.strings(data, args.min, utf16=not args.no_utf16, gbk=not args.no_gbk)
    if args.grep:
        g = args.grep.lower()
        res = [s for s in res if g in s["text"].lower()]
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for s in res:
            print(f"0x{s['offset']:08x} {s['enc']:<8} {s['text']}")


def cmd_entropy(args):
    data = Path(args.file).read_bytes()
    emap = analyze.entropy_map(data, args.block)
    res = analyze.summarize_regions(emap) if not args.blocks else emap
    if args.json:
        print(json.dumps(res, indent=1))
    else:
        for b in res:
            bar = "#" * int(b.get("entropy", 0) * 4) if args.blocks else ""
            print(f"0x{b['offset']:08x} {b['size']:>9} {b['class']:<26} {bar}")


def cmd_scan(args):
    data = Path(args.file).read_bytes()
    res = {
        "images": analyze.find_images(data),
        "display_init": analyze.find_display_init(data),
        "ble_uuids": analyze.find_ble_uuids(data),
        "urls": analyze.find_urls(data)[:200],
        "chip_hints": analyze.chip_hints(data),
    }
    if args.extract:
        out = Path(args.extract)
        out.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(res["images"]):
            p = out / f"{i:03d}_{img['offset']:08x}.{img['kind'] if img['kind'] != 'jpeg' else 'jpg'}"
            p.write_bytes(data[img["offset"]:img["offset"] + img["size"]])
        res["extracted_to"] = str(out)

    def show(r):
        print(f"Bilder: {len(r['images'])}  Display-Init-Kandidaten: {len(r['display_init'])}  "
              f"BLE-UUIDs: {len(r['ble_uuids'])}  URLs: {len(r['urls'])}")
        for d in r["display_init"][:5]:
            print(f"  Display 0x{d['offset']:x}: {d['width']} x {d['height']}  [{d['context_hex']}]")
        for u in r["ble_uuids"][:20]:
            print(f"  UUID {u['uuid']}  {u['meaning'] or ''}")
        for u in r["urls"][:20]:
            print(f"  URL {u}")
    _out(args, res, show)


def cmd_apk(args):
    r = analyze.apk_inventory(Path(args.file))

    def show(r):
        print(f"{r['file']}: {r['entries']} Einträge, DEX {r['dex_bytes']} Byte")
        for p in r["sdk_packages"]:
            print(f"SDK: {p['prefix']} → {p['meaning']} ({p['confidence']})")
        print("Native Bibliotheken:", ", ".join(r["native_libs"]) or "–")
        if r["firmware_like_files"]:
            print("Firmware-artige Dateien:", *r["firmware_like_files"][:15], sep="\n  ")
        for u in r["ble_uuids"][:25]:
            print(f"UUID {u['uuid']} {u['meaning'] or ''}")
        print("Server:", ", ".join(r["hosts"][:30]) or "–")
        print("→ " + r["note"])
    _out(args, r, show)


def cmd_watchface(args):
    try:
        r = jl_watchface.parse(Path(args.file).read_bytes())
    except jl_watchface.FormatError as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 2

    def show(r):
        print(f"JL-Zifferblatt: {r['elements']} Elemente, {r['size']} Byte")
        for e in r["items"]:
            print(f"  {e['index']:>2} 0x{e['type']:02x} {e['type_name']:<28} ({e['x']},{e['y']}) "
                  f"{e['width']}x{e['height']} Bilder {e['images']} {e['image_format']}")
        for w in r["warnings"]:
            print("  ! " + w)
    _out(args, r, show)


# --- Recht und Hygiene -------------------------------------------------------------

def cmd_guard(args):
    findings = guard.check(_root(args), staged=args.staged, use_git=not args.no_git)
    if args.json:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print(f"BLOCK {f['file']}: {f['reason']} [{f['rule']}]")
        print("OK – nichts Verdächtiges." if not findings else
              f"{len(findings)} Fund(e). Dateien nach private/ verschieben oder begründet in .wreckallow eintragen (LEGAL.md).")
    return 1 if findings else 0


# --- Arbeitsplatz -----------------------------------------------------------------

def cmd_init(args):
    dev = workspace.init(_root(args), args.name)
    print(f"Angelegt: {dev} und private/{dev.name}/ (nicht im Repo).")
    print(f"Weiter: devices/{dev.name}/LEGAL-ACK.md ausfüllen, dann `wreck next {dev.name}`.")


def cmd_next(args):
    r = workspace.next_step(workspace.device_dir(_root(args), args.device))

    def show(r):
        print(f"Gerät {r['device']}: Phase {r['phase']} – {r['title']}")
        if "todo" in r:
            print(f"Zu tun: {r['todo']}")
            print(f"Schreiben auf die Uhr erlaubt: {'ja' if r['write_to_device_allowed'] else 'NEIN'}")
            print(f"Offene Fakten: {', '.join(r['open_facts']) or '–'}")
            print(f"Anleitung: {r['playbook']}")
    _out(args, r, show)


def cmd_fact(args):
    dev = workspace.device_dir(_root(args), args.device)
    value = args.value
    try:
        value = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass
    f = workspace.set_fact(dev, args.key, value, args.status, args.evidence)
    if args.evidence:
        workspace.add_ledger(dev, f"{args.key}: {args.value}", args.status, args.evidence, fact=args.key)
    _out(args, f, lambda f: print(f"{args.key} = {f['value']!r} [{f['status']}]"))


def cmd_ledger(args):
    dev = workspace.device_dir(_root(args), args.device)
    e = workspace.add_ledger(dev, args.claim, args.status, args.source, args.fact)
    _out(args, e, lambda e: print(f"{e['id']} [{e['status']}] {e['claim']}"))


def cmd_provenance(args):
    dev = workspace.device_dir(_root(args), args.device)
    e = workspace.provenance(dev, Path(args.file), args.origin, args.how)
    _out(args, e, lambda e: print(f"Herkunft vermerkt: {e['name']} {e['sha256'][:16]}… ({e['origin']})"))


def cmd_report(args):
    dev = workspace.device_dir(_root(args), args.device)
    p = workspace.new_report(_root(args), dev, args.title)
    print(p)


def cmd_check(args):
    root = _root(args)
    devs = [workspace.device_dir(root, args.device)] if args.device else \
        sorted(d for d in (root / "devices").iterdir() if (d / "profile.json").exists())
    bad = 0
    for d in devs:
        errs = workspace.validate_profile(workspace.load_profile(d))
        bad += len(errs)
        print(f"{d.name}: {'OK' if not errs else ''}")
        for e in errs:
            print(f"  - {e}")
    return 1 if bad else 0


def cmd_brief(args):
    """Kurzanweisung für einen KI-Agenten, der neu ins Repo kommt."""
    root = _root(args)
    text = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
    print(text)
    if args.device:
        print("\n## Aktueller Stand\n")
        print(json.dumps(workspace.next_step(workspace.device_dir(root, args.device)), indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wreck", description="WRECK – Watch Reverse Engineering & Cracking Kit")
    p.add_argument("--version", action="version", version=f"wreck {__version__}")
    p.add_argument("--json", action="store_true", help="maschinenlesbare Ausgabe")
    p.add_argument("--root", default=".", help="Repo-Wurzel (Vorgabe: aktuelles Verzeichnis)")
    s = p.add_subparsers(dest="cmd", required=True)

    a = s.add_parser("identify", help="Datei grob einordnen: Typ, Entropie, Chip-Hinweise, Display-Init")
    a.add_argument("file"); a.set_defaults(fn=cmd_identify)
    a = s.add_parser("strings", help="Strings mit Offset (ASCII, UTF-16LE, GBK)")
    a.add_argument("file"); a.add_argument("--min", type=int, default=6); a.add_argument("--grep")
    a.add_argument("--no-utf16", action="store_true"); a.add_argument("--no-gbk", action="store_true")
    a.set_defaults(fn=cmd_strings)
    a = s.add_parser("entropy", help="Entropiekarte: Code, Tabellen, leer, verschlüsselt")
    a.add_argument("file"); a.add_argument("--block", type=int, default=4096); a.add_argument("--blocks", action="store_true")
    a.set_defaults(fn=cmd_entropy)
    a = s.add_parser("scan", help="Bilder, Display-Init, BLE-UUIDs, URLs suchen")
    a.add_argument("file"); a.add_argument("--extract", metavar="ORDNER", help="Bilder ausschneiden (nur nach private/!)")
    a.set_defaults(fn=cmd_scan)
    a = s.add_parser("apk", help="Begleitapp-Bestandsaufnahme ohne Dekompilieren")
    a.add_argument("file"); a.set_defaults(fn=cmd_apk)
    a = s.add_parser("watchface", help="JL-Zifferblatt lesen (docs/formats/jl-watchface.md)")
    a.add_argument("file"); a.set_defaults(fn=cmd_watchface)

    a = s.add_parser("guard", help="Repo auf Herstellerdateien, Schlüssel, private Daten prüfen")
    a.add_argument("--staged", action="store_true", help="nur vorgemerkte Dateien (pre-commit)")
    a.add_argument("--no-git", action="store_true"); a.set_defaults(fn=cmd_guard)

    a = s.add_parser("init", help="Neues Gerät anlegen (devices/<id>, private/<id>)")
    a.add_argument("name"); a.set_defaults(fn=cmd_init)
    a = s.add_parser("next", help="Nächster erlaubter Schritt laut Playbook")
    a.add_argument("device"); a.set_defaults(fn=cmd_next)
    a = s.add_parser("fact", help="Fakt im Profil setzen (mit Beleg → auch ins Belegbuch)")
    a.add_argument("device"); a.add_argument("key"); a.add_argument("value")
    a.add_argument("--status", required=True, choices=workspace.STATUSES); a.add_argument("--evidence")
    a.set_defaults(fn=cmd_fact)
    a = s.add_parser("ledger", help="Beleg ins Belegbuch schreiben")
    a.add_argument("device"); a.add_argument("claim")
    a.add_argument("--status", required=True, choices=workspace.STATUSES); a.add_argument("--source", required=True)
    a.add_argument("--fact"); a.set_defaults(fn=cmd_ledger)
    a = s.add_parser("provenance", help="Herkunft einer privaten Datei festhalten (Hash, Quelle)")
    a.add_argument("device"); a.add_argument("file"); a.add_argument("--origin", required=True)
    a.add_argument("--how", required=True, help="z. B. 'NOR-Dump über eigene Diagnose-App'")
    a.set_defaults(fn=cmd_provenance)
    a = s.add_parser("report", help="Neuen Bericht aus Vorlage anlegen")
    a.add_argument("device"); a.add_argument("title"); a.set_defaults(fn=cmd_report)
    a = s.add_parser("check", help="Geräteprofile gegen das Schema prüfen")
    a.add_argument("device", nargs="?"); a.set_defaults(fn=cmd_check)
    a = s.add_parser("brief", help="Einstiegsanweisung für KI-Agenten ausgeben")
    a.add_argument("device", nargs="?"); a.set_defaults(fn=cmd_brief)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rc = args.fn(args)
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 2
    return int(rc or 0)
