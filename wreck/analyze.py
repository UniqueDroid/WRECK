"""Rein lesende Analyse von Dateien: Typ, Strings, Entropie, bekannte Strukturen.

Nichts hier verändert, entschlüsselt oder verschickt Dateien. Alle Funktionen
liefern einfache dicts/lists, damit Menschen und KI-Agenten die Ergebnisse als
JSON weiterverarbeiten können.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import zipfile
from importlib import resources
from pathlib import Path

MAGIC = [
    (b"PK\x03\x04", "zip", "ZIP-Archiv (auch APK, .oapps-ähnliche Pakete, OTA-ZIP)"),
    (b"\x7fELF", "elf", "ELF-Programm/Objekt"),
    (b"\xff\xd8\xff", "jpeg", "JPEG-Bild"),
    (b"\x89PNG\r\n\x1a\n", "png", "PNG-Bild"),
    (b"GIF8", "gif", "GIF-Bild"),
    (b"\x1f\x8b", "gzip", "gzip"),
    (b"\x04\x22\x4d\x18", "lz4", "LZ4-Frame"),
    (b"BZh", "bzip2", "bzip2"),
    (b"\xfd7zXZ\x00", "xz", "xz"),
    (b"7z\xbc\xaf\x27\x1c", "7z", "7-Zip"),
    (b"dex\n", "dex", "Android-DEX"),
    (b"ustar", "tar", "tar (Kennung bei Offset 257)"),
]


def load_hints() -> dict:
    with resources.files("wreck").joinpath("data/hints.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def magic(data: bytes) -> dict | None:
    for sig, kind, label in MAGIC:
        if kind == "tar":
            if data[257:262] == sig:
                return {"kind": kind, "label": label}
        elif data.startswith(sig):
            return {"kind": kind, "label": label}
    return None


def entropy(block: bytes) -> float:
    if not block:
        return 0.0
    counts = [0] * 256
    for b in block:
        counts[b] += 1
    n = len(block)
    return -sum(c / n * math.log2(c / n) for c in counts if c)


def entropy_map(data: bytes, block: int = 4096) -> list[dict]:
    out = []
    for off in range(0, len(data), block):
        chunk = data[off:off + block]
        e = entropy(chunk)
        if chunk.count(0xFF) == len(chunk):
            cls = "leer (0xFF)"
        elif chunk.count(0) == len(chunk):
            cls = "leer (0x00)"
        elif e > 7.9:
            cls = "verschlüsselt/komprimiert"
        elif e > 6.5:
            cls = "Code/Bilddaten"
        else:
            cls = "Tabellen/Text"
        out.append({"offset": off, "size": len(chunk), "entropy": round(e, 3), "class": cls})
    return out


def summarize_regions(emap: list[dict]) -> list[dict]:
    """Fasst gleich klassifizierte, aufeinanderfolgende Blöcke zusammen."""
    regions: list[dict] = []
    for b in emap:
        if regions and regions[-1]["class"] == b["class"]:
            regions[-1]["size"] += b["size"]
        else:
            regions.append({"offset": b["offset"], "size": b["size"], "class": b["class"]})
    return regions


_ASCII = re.compile(rb"[\x20-\x7e]{%d,}")
_UTF16 = re.compile(rb"(?:[\x20-\x7e]\x00){%d,}")


def strings(data: bytes, min_len: int = 6, utf16: bool = True, gbk: bool = True) -> list[dict]:
    """ASCII-, UTF-16LE- und (optional) GBK-Strings mit Offset."""
    found = []
    for m in re.finditer(_ASCII.pattern % min_len, data):
        found.append({"offset": m.start(), "enc": "ascii", "text": m.group().decode("ascii")})
    if utf16:
        for m in re.finditer(_UTF16.pattern % min_len, data):
            found.append({"offset": m.start(), "enc": "utf-16le", "text": m.group().decode("utf-16le")})
    if gbk:
        # Chinesische Texte in GB2312/GBK: Folgen von Doppelbytes 0xA1-0xF7 / 0xA1-0xFE.
        for m in re.finditer(rb"(?:[\xb0-\xf7][\xa1-\xfe]){3,}", data):
            try:
                found.append({"offset": m.start(), "enc": "gbk", "text": m.group().decode("gbk")})
            except UnicodeDecodeError:
                pass
    found.sort(key=lambda s: s["offset"])
    return found


def chip_hints(data: bytes, hints: dict | None = None) -> list[dict]:
    hints = hints or load_hints()
    low = data.lower()
    out = []
    for chip in hints["chips"]:
        hits = []
        for p in chip["patterns"]:
            pos = low.find(p.lower().encode())
            if pos >= 0:
                hits.append({"pattern": p, "first_offset": pos})
        if hits:
            out.append({"family": chip["family"], "vendor": chip["vendor"], "confidence": chip["confidence"], "hits": hits})
    out.sort(key=lambda c: -len(c["hits"]))
    return out


def find_images(data: bytes, limit: int = 500) -> list[dict]:
    """Eingebettete JPEG/PNG finden (z. B. Bootlogo, Symbole)."""
    out = []
    for m in re.finditer(rb"\xff\xd8\xff[\xdb\xe0\xe1\xee\xc0\xc4]", data):
        end = data.find(b"\xff\xd9", m.start() + 4)
        if end > 0:
            out.append({"kind": "jpeg", "offset": m.start(), "size": end + 2 - m.start()})
        if len(out) >= limit:
            break
    for m in re.finditer(rb"\x89PNG\r\n\x1a\n", data):
        end = data.find(b"IEND\xaeB`\x82", m.start())
        if end > 0:
            out.append({"kind": "png", "offset": m.start(), "size": end + 8 - m.start()})
        if len(out) >= limit:
            break
    return sorted(out, key=lambda i: i["offset"])


def find_display_init(data: bytes) -> list[dict]:
    """MIPI-DCS-Fenster (CASET 0x2A / RASET 0x2B) in Init-Tabellen suchen.

    Viele Display-Treiber senden `2A 00 00 HH LL` und `2B 00 00 HH LL` beim Start.
    (HHLL + 1) ergibt Breite bzw. Höhe. Bei der M78 führte genau das zur
    Init-Tabelle des AMOLED (368 x 448).
    """
    out = []
    for m in re.finditer(rb"\x2a\x00\x00(..)", data, re.S):
        w = struct.unpack(">H", m.group(1))[0] + 1
        if not 64 <= w <= 1024:
            continue
        window = data[m.end():m.end() + 24]
        n = window.find(b"\x2b\x00\x00")
        if n < 0 or n + 5 > len(window):
            continue
        h = struct.unpack(">H", window[n + 3:n + 5])[0] + 1
        if 64 <= h <= 1024:
            out.append({"offset": m.start(), "width": w, "height": h,
                        "context_hex": data[max(0, m.start() - 16):m.start() + 32].hex(" ")})
    return out


def find_ble_uuids(data: bytes, hints: dict | None = None) -> list[dict]:
    hints = hints or load_hints()
    known = {u["uuid"]: u for u in hints["ble_uuids"]}
    pat = re.compile(rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
    seen: dict[str, dict] = {}
    for m in pat.finditer(data):
        u = m.group().decode().lower()
        if u not in seen:
            k = known.get(u)
            seen[u] = {"uuid": u, "first_offset": m.start(),
                       "meaning": k["meaning"] if k else None,
                       "confidence": k["confidence"] if k else None}
    return list(seen.values())


def find_urls(data: bytes) -> list[str]:
    urls = set()
    for m in re.finditer(rb"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]{4,200}", data):
        urls.add(m.group().decode("ascii", "replace"))
    return sorted(urls)


def identify(path: Path) -> dict:
    data = path.read_bytes()
    emap = entropy_map(data, 16384)
    total = entropy(data[: 1 << 22])
    result = {
        "file": str(path),
        "size": len(data),
        "sha256": sha256(data),
        "magic": magic(data),
        "entropy_overall": round(total, 3),
        "regions": summarize_regions(emap)[:64],
        "chip_hints": chip_hints(data),
        "display_init": find_display_init(data)[:10],
        "embedded_images": len(find_images(data)),
        "verdict": [],
    }
    v = result["verdict"]
    if result["magic"] and result["magic"]["kind"] == "zip":
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
            result["zip_entries"] = len(names)
            if "AndroidManifest.xml" in names:
                v.append("Android-App: weiter mit `wreck apk`.")
            else:
                v.append("ZIP: Inhalt auflisten; enthält oft OTA-Dateien.")
        except zipfile.BadZipFile:
            v.append("ZIP-Kennung, aber kein lesbares ZIP.")
    if total > 7.95:
        v.append("Sehr hohe Entropie: verschlüsselt oder komprimiert. Nicht raten – Format über Begleitapp/SDK klären (docs/PLAYBOOK.md, Phase 3).")
    elif result["chip_hints"]:
        v.append("Klartext-Merkmale gefunden: Chipfamilie in devices/<gerät>/profile.json als 'vermutet' eintragen.")
    if result["display_init"]:
        d = result["display_init"][0]
        v.append(f"Display-Init-Kandidat bei 0x{d['offset']:x}: {d['width']} x {d['height']}.")
    return result


def apk_inventory(path: Path) -> dict:
    """Begleitapp untersuchen, ohne sie zu dekompilieren: Dateiliste und DEX-Strings."""
    hints = load_hints()
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        dex = b"".join(z.read(n) for n in names if re.fullmatch(r"classes\d*\.dex", n))
        native = [n for n in names if n.startswith("lib/") and n.endswith(".so")]
        assets = [n for n in names if n.startswith("assets/")]
    packages = []
    for p in hints["apk_packages"]:
        if ("L" + p["prefix"]).encode() in dex:
            packages.append(p)
    firmware_like = [n for n in names if re.search(r"\.(bin|ufw|img|hex|zip|ota|res)$", n, re.I)
                     and not n.startswith("lib/")]
    return {
        "file": str(path),
        "sha256": sha256(path.read_bytes()),
        "entries": len(names),
        "dex_bytes": len(dex),
        "sdk_packages": packages,
        "native_libs": sorted({n.split("/")[-1] for n in native}),
        "assets_count": len(assets),
        "firmware_like_files": firmware_like[:100],
        "ble_uuids": find_ble_uuids(dex, hints)[:100],
        "hosts": sorted({re.sub(r"^https?://([^/:]+).*", r"\1", u) for u in find_urls(dex)})[:200],
        "note": "Nur Bestandsaufnahme. Ein SDK in der App beweist nicht den Chip der Uhr: Begleitapps bedienen oft mehrere Chipfamilien. Dekompilierte Klassen und eingebettete Firmware nicht ins Repo legen (LEGAL.md).",
    }
