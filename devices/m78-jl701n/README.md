# Beispielgerät: M78 (JieLi JL701N)

Referenzprofil aus einem echten Projekt. Es zeigt, wie ein ausgefülltes Profil aussieht und welche Wege bei dieser
Uhr funktioniert haben. Es enthält **nur Hardware-Fakten und Erfahrungen** – keine Firmware, keine Adressen innerhalb
der Herstellerfirmware, keine Patches.

Wer eine M78 oder ein Geschwistermodell (z. B. ND326) besitzt: `wreck init "<eigener Name>"` anlegen und dieses Profil
als Vorlage für die Vermutungen nutzen – Status im eigenen Profil erst nach eigener Prüfung anheben.

## Hardware auf einen Blick

| Teil | Wert | Status |
| --- | --- | --- |
| SoC | JieLi JL701N (AC701N, BR28), pi32v2, PSRAM | am Rechner geprüft |
| Flash | 2 MB intern (eine Bank), 16 MB NOR extern | am Gerät bestätigt |
| Display | AMOLED 368 × 448, QSPI, RGB565; Reset PA02, CS PA06, Strom PA05, kein TE | am Gerät bestätigt |
| Touch | CHSC6x, I²C 0x2E auf PG03/PG04, INT PG05, RESET PG06 | am Gerät bestätigt |
| Tasten | links PB01, rechts PG08, Krone PB04 (8 s = Neustart), Drehgeber PC06/PB07 | am Gerät bestätigt |
| Motor | PWM auf PB06 | am Gerät bestätigt |
| Sensoren | SC7A20 (Beschleunigung), Vcare LC09A (Puls, I²C 0x33) | am Rechner geprüft |
| Begleitapp | DeeFit Pro | am Gerät bestätigt |

## Was sich bewährt hat

1. **Werkstestmenü und Diagnose-Apps statt Raten.** Pins wurden mit einer kleinen eigenen App bestätigt, die Speicher
   und Port-Eingänge nur liest.
2. **Display über die Init-Tabelle finden:** Die MIPI-DCS-Befehle `2A 00 00 01 6F` / `2B 00 00 01 BF` (0…367, 0…447)
   führten direkt zur Init-Folge. `wreck scan` sucht genau das.
3. **Passendes Chip-SDK:** Ein öffentliches JL701N-Uhren-SDK hat dieselben Strukturen wie die Herstellerfirmware
   (Tasten- und Displaytabellen direkt hintereinander). Das SDK baut unter Linux reproduzierbar.
4. **Rückweg ohne Risiko:** Eigener Code läuft im PSRAM, gestartet von der unveränderten Herstellerfirmware. Jeder
   Neustart = Original. Später: Startprogramm nur mit gehaltener Taste beim Einschalten.
5. **Eigene App-Schicht:** kleine JavaScript-Engine in der gepatchten Firmware; Apps kommen als Paket über die
   Begleitapp. Neue Funktionen ohne neuen Firmware-Build.

## Was schiefging (und die Regel daraus)

| Ereignis | Regel |
| --- | --- |
| Build mit neuem Bootlogo **und** AOD-Änderung → Bootloop | Eine Änderung pro Build |
| Kein Bootloader-Fallback, einfache Bank | Rückweg vor Experiment (`docs/RECOVERY.md`) |
| Eigenes Programm belegte die Oberflächen-Task → keine Mitteilungen, kein Sync, kein Update | Eigene Task, Herstelleroberfläche nicht blockieren |
| Disassembler zeigte Sprungziele um die Befehlslänge verschoben | Werkzeuge an bekannten Funktionen gegenprüfen |

## Offen

Display-Controller-ID, genauer Touch-Typ, Interrupt-Pins der Sensoren, Ladeparameter, ob der Update-Loader auch
ohne Bluetooth aus einer gespeicherten Datei einspielen kann.
