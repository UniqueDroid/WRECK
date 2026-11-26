"""Zifferblatt-Dateien im JieLi-Format „JL“ (gesehen bei 368x448-Uhren wie der M78).

Spezifikation: docs/formats/jl-watchface.md. Nur lesen und prüfen; dieses Modul
enthält keine Herstellerdaten.
"""
from __future__ import annotations

import struct

TYPES = {
    0x01: "Bild", 0x02: "Bildfolge", 0x03: "Stilbild", 0x05: "Drehbild (Kompass)", 0x06: "Sonderanimation",
    0x07: "Drehbild (Kompass)", 0x14: "Stilfarbe",
    0x32: "Stunde", 0x33: "Minute", 0x34: "Monat", 0x35: "Tag", 0x36: "Stundenzeiger", 0x37: "Minutenzeiger",
    0x38: "Sekundenzeiger springend", 0x39: "Sekundenzeiger gleitend", 0x3A: "Stunde als Bildnummer",
    0x3B: "Sekunde", 0x3C: "Jahr", 0x3D: "Sekundenzeiger gleitend schnell", 0x3E: "Stunde Zehner",
    0x3F: "Stunde Einer", 0x40: "Minute Zehner", 0x41: "Minute Einer", 0x42: "24-Stunden-Zeiger",
    0x44: "Tageszeiger", 0x45: "Monatszeiger",
    0x63: "Wochentag", 0x64: "Wochentag", 0x65: "Bluetooth", 0x66: "Akku-Stufenbild", 0x67: "AM/PM",
    0x68: "Akku in Prozent", 0x6A: "Wetter-Symbol", 0x6B: "Temperatur", 0x6C: "Temperatur-Einheit",
    0x6D: "Temperatur", 0x6E: "Zyklusphase",
    0x94: "Kompass Grad", 0x95: "Himmelsrichtung", 0x96: "Schritte", 0x97: "Kalorien", 0x98: "Puls",
    0x99: "Strecke", 0x9A: "Schlaf Stunden", 0x9B: "Schlaf Minuten", 0x9C: "ungelesene Nachrichten",
    0x9D: "Puls-Tageskurve", 0x9E: "Blutsauerstoff", 0x9F: "Körpertemperatur (fester Wert)",
    0xA0: "Fortschritt Schritte", 0xA1: "Fortschritt Kalorien", 0xA2: "Fortschritt Strecke", 0xA3: "Puls-Skala",
    0xA4: "Blutsauerstoff-Skala", 0xA5: "Schritte je Stunde",
    0xB4: "Tippfläche", 0xB5: "Sekunden-Ausschnitt",
    0xE6: "Tippbereich (Folgeelement)", 0xE7: "wählbarer Bereich", 0xE8: "wählbarer Bereich", 0xE9: "wählbarer Bereich",
    0xEA: "Foto-Hintergrund",
}

VISIBILITY = {0: "normal", 1: "übersprungen", 2: "nur gedimmtes AOD"}
FORMATS = {2: "RGB565 RLE, deckend", 8: "ARGB (A + RGB565), transparent", 5: "unbekannt (5)", 6: "unbekannt (6)"}
ELEMENT_SIZE = 24
MAX_ELEMENTS = 88


class FormatError(ValueError):
    pass


def parse(data: bytes) -> dict:
    if len(data) < 4 or data[2:4] != b"JL" or data[1] != 0:
        raise FormatError("Kein JL-Zifferblatt (Byte 1 = 0 und Bytes 2–3 = 'JL' erwartet)")
    count = data[0]
    if count == 0 or count > MAX_ELEMENTS:
        raise FormatError(f"Unplausible Elementzahl {count}")
    end = 4 + count * ELEMENT_SIZE
    if end > len(data):
        raise FormatError("Datei kürzer als die Elementtabelle")
    elements = []
    warnings = []
    for i in range(count):
        e = data[4 + i * ELEMENT_SIZE: 4 + (i + 1) * ELEMENT_SIZE]
        typ, vis, x, y, nimg, fmt, colour, w, h, b14, b15, off, b20, align, b22, variant = struct.unpack(
            "<BBHHBBHHHBBIBBBB", e)
        el = {
            "index": i, "type": typ, "type_name": TYPES.get(typ, "unbekannt"),
            "visibility": VISIBILITY.get(vis, vis), "x": x, "y": y, "width": w, "height": h,
            "images": nimg, "image_format": FORMATS.get(fmt, fmt), "colour_or_angle": colour,
            "group_or_end_angle": b14 | (b15 << 8), "data_offset": off,
            "param20": b20, "align": align, "param22": b22, "variant": variant,
        }
        if nimg and not (end <= off < len(data)):
            warnings.append(f"Element {i}: Bilddaten-Offset 0x{off:x} außerhalb der Datei")
        if typ not in TYPES:
            warnings.append(f"Element {i}: unbekannter Typ 0x{typ:02x}")
        elements.append(el)
    return {"format": "jl-watchface", "elements": count, "size": len(data), "items": elements, "warnings": warnings}
