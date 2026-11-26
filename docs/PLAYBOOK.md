# Playbook: von der unbekannten China-Uhr zur eigenen Anpassung

Dieses Playbook ist der Bauplan. Es gilt für Menschen und KI-Agenten gleichermaßen. Jede Phase hat ein
**Tor**: Erst wenn es offen ist, geht es weiter. `wreck next <gerät>` prüft die Tore anhand von
`devices/<gerät>/profile.json`, `ledger.jsonl` und `provenance.jsonl`.

Die Erfahrungen stammen aus einem echten Projekt (Uhr M78 mit JieLi JL701N, siehe `devices/m78-jl701n`):
mehrere Dutzend Firmware-Testbuilds, ein Bootloop, ein mühsamer Rückweg. Die Regeln unten sind deshalb
nicht theoretisch.

## Die fünf Grundregeln

1. **Rückweg vor Experiment.** Nichts wird auf die Uhr geschrieben, bevor nachgewiesen ist, wie man zurückkommt.
2. **Eine Änderung pro Build.** Zwei Änderungen in einem Build = bei einem Fehler weiß niemand, welche schuld ist.
   (Bei der M78 kamen Bootlogo und AOD zusammen in einen Build – Bootloop, Ursache lange unklar.)
3. **Belegstufen ehrlich führen.** `vermutet` → `am-rechner-geprueft` → `am-geraet-bestaetigt`. Nur der Mensch mit
   der Uhr am Arm kann `am-geraet-bestaetigt` setzen. Ein Agent schreibt nie „funktioniert“, wenn nur der Rechner
   geprüft hat.
4. **Byte-Diff statt Bauchgefühl.** Jeder Build hat einen Prüfer, der *alle* Bytes außerhalb der gewollten
   Änderungsstellen mit dem Ausgangsbild vergleicht.
5. **Zurückgezogene Builds bleiben zurückgezogen.** Mit Grund markieren, nie wieder anbieten.

---

## Phase 0-recht

**Ziel:** Klar, dass die Arbeit erlaubt ist. **Tor:** `devices/<gerät>/LEGAL-ACK.md` vollständig mit „ja“.

- `LEGAL.md` lesen. Uhr rechtmäßig gekauft, kein NDA, Ziel ist Interoperabilität/Fehlerbehebung/eigene Nutzung.
- Agenten: Fällt der Wunsch unter „Nicht Ziel von WRECK“, ablehnen und erlaubte Alternative anbieten.

## Phase 1-erkennen

**Ziel:** Wissen, welches Gerät, welcher Chip, welche Begleitapp. **Tor:** `chip` und `companion_app` mindestens `vermutet`.

Ohne die Uhr zu öffnen, in dieser Reihenfolge:

1. **Begleitapp** (Name aus der Anleitung/QR-Code). APK von der *eigenen* Installation sichern
   (`adb shell pm path <paket>`, dann `adb pull`) nach `private/<gerät>/apk/`, Herkunft mit `wreck provenance`.
2. `wreck apk private/<gerät>/apk/app.apk`: SDK-Pakete (`com/jieli/`, `com/realsil/`, …), BLE-UUIDs, Server,
   mitgelieferte Firmware. **Achtung:** Begleitapps bedienen oft mehrere Chipfamilien; ein SDK in der App ist ein
   Hinweis, kein Beweis.
3. **Werkstest-/Servicemenü** der Uhr suchen (oft versteckte Tippfolge in Einstellungen → System). Zeigt
   Firmware-/Hardwareversion, Sensoren, Touch-Test. Fotos davon sind gute Belege.
4. Typenschild, FCC-ID, Bluetooth-Name, Teardown-Videos gleichartiger Uhren (gleiche Platine wird unter vielen
   Namen verkauft – `sold_as` im Profil).
5. `docs/CHIPS.md` für typische Merkmale je Chipfamilie.

```
wreck init "Meine Uhr X9"
wreck fact meine-uhr-x9 companion_app '{"name":"DeeFit Pro","package":"…"}' --status vermutet --evidence "Anleitung, QR-Code"
```

## Phase 2-beschaffen

**Ziel:** Die Firmware der eigenen Uhr als Datei. **Tor:** mindestens ein Eintrag in `provenance.jsonl`.

Legale Wege, vom einfachsten zum aufwändigsten:

1. **Update-Datei, die die eigene App für die eigene Uhr lädt** (App-Cache, Downloads-Ordner, mitgelieferte
   Assets in der APK). Einmalig, für das eigene Gerät – kein Massenabruf vom Herstellerserver.
2. **Mitschnitt der eigenen Bluetooth-Übertragung** beim offiziellen Update (Android: HCI-Snoop-Log).
3. **Auslesen über eine vorhandene Funktion** (z. B. Flash-Lesebefehl, den die Firmware schon kennt).
4. **Hardware** (UART/SWD/Testpunkte) – nur, wenn der Mensch das Öffnen ausdrücklich will.

Alles landet in `private/<gerät>/…`, nie im Repo. Jede Datei bekommt einen Herkunftsnachweis:

```
wreck provenance meine-uhr-x9 private/meine-uhr-x9/firmware/ota.bin --origin "eigene App 2.3.1, Cache" --how "adb pull"
```

## Phase 3-rueckweg

**Ziel:** Nachweisen, wie man nach einem fehlgeschlagenen Experiment zurückkommt. **Tor:** `update_path` ≥
`am-rechner-geprueft` **und** `recovery` = `am-geraet-bestaetigt`. **Vorher wird nichts auf die Uhr geschrieben.**

Details und Muster: `docs/RECOVERY.md`. Kurzfassung der Fragen, die beantwortet sein müssen:

- Wie viele Firmware-Plätze gibt es (einfache oder doppelte Bank)? Bleibt beim Update eine alte Kopie?
- Fällt der Bootloader bei einer abstürzenden App zurück? (Bei der M78: **nein**.)
- Welcher Teil des Updates braucht die laufende App (Bluetooth), welcher nur den Bootloader/Loader?
- Gibt es einen Hardware-Reset per Tastendruck (M78: Krone 8 s)? Der hilft nur gegen Hänger, nicht gegen kaputte Firmware.
- Ist die unveränderte Original-Firmware als Datei vorhanden, geprüft und mit Hash vermerkt?

Erster Gerätetest überhaupt: **die unveränderte Originalfirmware** über den offiziellen Weg neu einspielen.
Erst danach eine Firmware mit einer einzigen, harmlosen Änderung (z. B. Versionstext).

## Phase 4-verstehen

**Ziel:** Hardware und Formate so weit kennen, wie die Anpassung es braucht. **Tor:** `display`, `touch`,
`buttons` ≥ `am-rechner-geprueft`.

Werkzeuge in WRECK (rein lesend):

| Frage | Befehl |
| --- | --- |
| Wo ist Code, wo sind Daten, was ist verschlüsselt? | `wreck entropy datei` |
| Welche Texte, auch Chinesisch (GBK)? | `wreck strings datei --grep test` |
| Display-Auflösung, Init-Tabelle? | `wreck scan datei` (sucht MIPI-DCS `2A`/`2B`) |
| Eingebettete Bilder (Bootlogo, Symbole)? | `wreck scan datei --extract private/<gerät>/bilder` |
| Zifferblatt-Datei verstehen? | `wreck watchface datei` |

Externe Werkzeuge (Ghidra, Jadx, Apktool, Prozessor-Module) und wie man sie sauber einsetzt: `docs/TOOLS.md`.

Bewährte Abkürzungen:

- **Passendes Hersteller-SDK suchen.** Viele China-Uhren sind mit öffentlich verfügbaren Chip-SDKs gebaut. Gleiche
  Struktur im SDK und in der Firmware (Tabellen, Strukturen, Funktionsreihenfolge) spart Wochen. SDK nur lokal
  nutzen, Lizenz beachten.
- **Geschwistermodelle vergleichen.** Dieselbe Platine steckt in vielen Modellen; Firmwares mehrerer Modelle zeigen,
  was gemeinsam (Bootloader, Treiber) und was modellspezifisch ist.
- **Diagnose statt Raten.** Eine kleine eigene Diagnose-App (Speicher lesen, Tasten protokollieren) auf der Uhr
  beantwortet Pin-Fragen schneller als jede statische Analyse (M78: Display-/Tasten-Pins so bestätigt).

Jede Erkenntnis kommt ins Belegbuch:

```
wreck ledger meine-uhr-x9 "Display 368x448, Init-Tabelle mit 2A/2B" --status am-rechner-geprueft --source "wreck scan, Offset in privatem Bericht" --fact display
```

## Phase 5-anpassen

**Ziel:** Die kleinste Änderung, die den Wunsch erfüllt, gebaut, geprüft, getestet. Kein festes Tor; Ergebnis ist
ein Bericht mit Testprotokoll.

Reihenfolge der Mittel, vom risikoärmsten zum riskantesten:

1. **Ohne Firmwareänderung:** eigenes Zifferblatt, eigene Texte/Sprachpakete über vorhandene Wege, eigene Begleitapp
   (Interoperabilität über das vorhandene Bluetooth-Protokoll).
2. **Kleiner Firmware-Patch** an genau einer Stelle, mit Byte-Diff-Prüfer.
3. **Eigene App-Schicht** in der Hersteller-Firmware (Phase 6).
4. **Eigene Firmware** – nur mit nachgewiesenem, unabhängigem Rückweg.

Pflicht je Build:

- eindeutiger Versionsname (z. B. `4.50.12_TEST`), eine Änderung, Changelog-Zeile
- Prüfer-Ausgabe (JSON) mit: Ausgangs-Hash, neuer Hash, geänderte Bereiche, „nicht am Gerät getestet“
- Testprotokoll aus `templates/test-protocol.md` für den Menschen: was tun, was erwartet, wie zurück
- Analyse-Nebenprodukte, die man nicht flashen darf, heißen `…-NOT-FLASHABLE…`

## Phase 6-app-schicht

**Ziel:** Statt jede Funktion in die Firmware zu patchen, einmal eine kleine Laufzeitumgebung einbauen, die
eigene Apps lädt. Muster, Berechtigungsmodell und Grenzen: `docs/APP-LAYER.md`.

---

## Arbeitsweise für KI-Agenten

- Zu Beginn: `wreck brief <gerät>` bzw. `wreck --json next <gerät>`. Nur Aufgaben der aktuellen Phase angehen.
- `write_to_device_allowed: false` heißt: keine Firmware/kein Patch zum Flashen anbieten, nur Analyse und Vorbereitung.
- Berichte mit `wreck report <gerät> "<titel>"` anlegen; jede Aussage bekommt eine Belegstufe.
- Vor jedem Commit: `wreck guard`. Herstellermaterial nie committen, auch nicht in Unterordnern.
- Wenn der Mensch etwas am Gerät bestätigt (Foto, Beschreibung), das als Quelle ins Belegbuch übernehmen
  („Gerätetest am 19.11., Foto 3“).
