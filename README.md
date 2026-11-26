# WRECK – Watch Reverse Engineering & Cracking Kit

**Bauplan und Werkzeugkasten, um die eigene China-Smartwatch zu verstehen und anzupassen – mit einer KI als Helfer.**

Gib einer KI (Claude, Codex, Gemini, …) dieses Repo und deine Uhr: Sie findet hier die Regeln, den Ablauf in Phasen,
eine CLI für die Analyse und ein durchgearbeitetes Beispielgerät. Alles so gebaut, dass es **legal** bleibt und
**nichts kaputtgeht**, was sich nicht reparieren lässt.

> *English:* WRECK is a blueprint + CLI that lets humans and AI agents reverse-engineer and customise cheap Chinese
> smartwatches they own, within EU interoperability law. Docs are in German; the CLI is plain Python 3.9+, no dependencies.

## Was es kann

- **Bauplan in Phasen** mit Toren: erkennen → beschaffen → **Rückweg nachweisen** → verstehen → anpassen → eigene Apps
  (`docs/PLAYBOOK.md`). `wreck next` sagt, was als Nächstes erlaubt ist – auch, ob schon etwas auf die Uhr darf.
- **Analyse ohne Risiko:** Dateityp, Entropiekarte, Strings (auch chinesisch/GBK), Chip-Hinweise, Display-Init-Tabellen,
  eingebettete Bilder, BLE-UUIDs, Begleitapp-Bestandsaufnahme, JieLi-Zifferblätter.
- **Rechtliche Leitplanken:** `LEGAL.md` plus `wreck guard` (pre-commit), der Firmware, APKs, Decompiler-Ausgaben,
  Schlüssel und MAC-Adressen aus dem Repo fernhält.
- **Belegführung:** Geräteprofil mit Statuswerten, Belegbuch, Herkunftsnachweise, Berichtsvorlagen.

## Schnellstart

```sh
git clone https://github.com/UniqueDroid/WRECK && cd WRECK
pip install -e .                 # oder ohne Installation: python3 -m wreck …
git config core.hooksPath hooks  # wreck guard vor jedem Commit

wreck init "Meine Uhr X9"        # legt devices/meine-uhr-x9 und private/meine-uhr-x9 an
# devices/meine-uhr-x9/LEGAL-ACK.md ausfüllen
wreck next meine-uhr-x9          # nächster Schritt laut Playbook
wreck apk private/meine-uhr-x9/apk/app.apk
wreck identify private/meine-uhr-x9/firmware/update.bin
```

Mit einer KI: Repo öffnen und sagen *„Lies AGENTS.md und hilf mir mit meiner Uhr“*. Der Agent startet mit
`wreck brief <gerät>`.

## Befehle

| Befehl | Zweck |
| --- | --- |
| `wreck identify DATEI` | Typ, Entropie, Chip-Hinweise, Display-Auflösung, Einschätzung |
| `wreck entropy DATEI` | Bereiche: Code, Tabellen, leer, verschlüsselt/komprimiert |
| `wreck strings DATEI [--grep X]` | ASCII-, UTF-16- und GBK-Strings mit Offset |
| `wreck scan DATEI [--extract DIR]` | JPEG/PNG, MIPI-Display-Init, BLE-UUIDs, URLs |
| `wreck apk APK` | SDKs, UUIDs, Server, mitgelieferte Firmware einer Begleitapp |
| `wreck watchface DATEI` | JieLi-Zifferblatt („JL“) lesen |
| `wreck init / next / fact / ledger / provenance / report / check` | Geräteprofil und Belege |
| `wreck guard [--staged]` | nichts Verbotenes im Repo? |
| `wreck brief [GERÄT]` | Einstiegsanweisung für KI-Agenten |

Alle Befehle mit `wreck --json …` für maschinenlesbare Ausgabe.

## Aufbau

```
AGENTS.md / CLAUDE.md / llms.txt   Einstieg für KI-Agenten
LEGAL.md                           Rechtsrahmen und Repo-Regeln
docs/                              Playbook, Rückweg, Chips, App-Schicht, Belege, Werkzeuge, Formate
wreck/                             CLI (Python, nur Standardbibliothek)
devices/_template/                 leeres Profil
devices/m78-jl701n/                Beispiel: M78 mit JieLi JL701N
templates/                         Bericht, Testprotokoll
hooks/pre-commit                   ruft wreck guard
private/                           deine Rohdaten – per .gitignore ausgeschlossen
```

## Herkunft

Entstanden aus der Arbeit an einer M78-Uhr (JieLi JL701N): angepasste Firmware, eigene Rettungswege, eine eigene
JavaScript-App-Schicht. WRECK enthält davon **nur** die Methode, eigene Werkzeuge und Hardware-Fakten – keine
Herstellerdateien.

## Lizenz und Haftung

MIT (siehe `LICENSE`). Eingriffe in Firmware können Geräte unbrauchbar machen und Garantie kosten. Keine
Rechtsberatung – siehe `LEGAL.md`.
