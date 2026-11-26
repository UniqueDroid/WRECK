# Format: JieLi-Zifferblatt „JL“ (368 × 448)

Beschreibung in eigenen Worten, gewonnen zur Interoperabilität (eigene Zifferblätter für die eigene Uhr). Geprüft an
den Zifferblättern einer M78 (JieLi JL701N); Status je Teil unten. Parser: `wreck watchface <datei>`.

## Aufbau

| Stelle | Inhalt |
| --- | --- |
| Byte 0 | Anzahl der Elemente (die Uhr liest höchstens 88) |
| Byte 1 | 0 |
| Byte 2–3 | ASCII `JL` |
| ab Byte 4 | je Element 24 Bytes |
| danach | Bilddaten, auf die die Elemente verweisen |

## Element (24 Bytes, little endian)

| Offset | Größe | Inhalt |
| --- | --- | --- |
| 0 | 1 | Typ (Tabelle unten) |
| 1 | 1 | Sichtbarkeit: 0 normal, 1 übersprungen, 2 nur im gedimmten Always-On |
| 2 | 2 | x |
| 4 | 2 | y |
| 6 | 1 | Anzahl Bilder im Bildblock |
| 7 | 1 | Bildformat: 2 = RGB565 lauflängenkodiert, 8 = mit Deckkraft |
| 8 | 2 | Farbe oder Startwinkel (je nach Typ) |
| 10 | 2 | Breite |
| 12 | 2 | Höhe |
| 14–15 | 2 | Gruppenkennung bzw. Endwinkel |
| 16 | 4 | Offset der Bilddaten in der Datei |
| 20 | 1 | je Typ: Ziffernabstand, Stufenzahl, Drehpunkt x, Aktion einer Tippfläche |
| 21 | 1 | Ausrichtung: 0 links, 1 mittig, 2 rechts |
| 22 | 1 | je Typ: Höhenversatz, Drehpunkt y, Takt |
| 23 | 1 | Variante (Sprache, Tag/Nacht) |

## Bildblock

`(n + 1)` 32-Bit-Werte (erster = `4 × (n + 1)`, letzter = Blockgröße), dann `n` Bilder.

- **Format 2:** je Zeile ein 32-Bit-Eintrag (Lage Bit 0–20, Länge Bit 21–31); Zeilen lauflängenkodiert
  (Zählbyte: Bit 7 gesetzt = ein Pixel n-mal, sonst n einzelne Pixel); Pixel RGB565, **höherwertiges Byte zuerst**.
- **Format 8:** Pixel zu 3 Bytes (Deckkraft, dann RGB565), mit Zeilentabelle wie Format 2 oder roh mit auf 4 Bytes
  aufgefüllten Zeilen (gedrehte Bilder wie Zeiger).

## Typen (Auswahl)

| Bereich | Typen |
| --- | --- |
| Bilder | `01` Bild, `02` Bildfolge, `03` Stilbild |
| Zeit digital | `32` Stunde, `33` Minute, `3B` Sekunde, `3E/3F` Stunde Zehner/Einer, `40/41` Minute Zehner/Einer, `67` AM/PM |
| Zeit analog | `36` Stunden-, `37` Minuten-, `38/39/3D` Sekundenzeiger, `42` 24-h-Zeiger |
| Datum | `34` Monat, `35` Tag, `3C` Jahr, `63/64` Wochentag |
| Gerät | `65` Bluetooth, `66/68` Akku, `9C` ungelesene Nachrichten |
| Aktivität/Gesundheit | `96` Schritte, `97` Kalorien, `98` Puls, `99` Strecke, `9E` Blutsauerstoff, `A0–A2` Fortschritt |
| Bedienung | `B4` Tippfläche, `E6` Tippbereich um das Folgeelement |

Vollständige Liste der Namen: `wreck/formats/jl_watchface.py`.

## Status

| Teil | Status |
| --- | --- |
| Kopf, Element, Typen der Hersteller-Zifferblätter | am Rechner geprüft (alle Marktdateien einer M78 lesbar, Vorschau stimmt mit Marktbildern überein) |
| Bildformate 5 und 6, Typen `06`, `14`, `E7–E9` | offen |
| Selbst erzeugtes Zifferblatt auf der Uhr | offen |
