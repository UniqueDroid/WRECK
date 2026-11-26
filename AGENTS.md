# AGENTS.md – Anweisungen für KI-Agenten

Du hilfst einem Menschen, **seine eigene China-Smartwatch** zu verstehen und anzupassen. Dieses Repo ist dein
Bauplan. Es gilt für jeden Agenten (Claude, Codex, Gemini, Copilot, Cursor, lokale Modelle).

## Start (immer)

```sh
pip install -e .            # oder: python3 -m wreck …  (nur Standardbibliothek)
wreck brief <gerät>         # diese Datei + aktueller Stand
wreck --json next <gerät>   # aktuelle Phase, offene Fakten, ob Schreiben auf die Uhr erlaubt ist
```

Kein Gerät vorhanden? `wreck init "<Modellname>"` und den Menschen bitten, `devices/<id>/LEGAL-ACK.md` auszufüllen.

## Harte Regeln

1. **LEGAL.md gilt.** Herstellerfirmware, APKs, Dumps, SDK-Quelltext, Decompiler-Ausgaben, Schlüssel und persönliche
   Daten gehören nach `private/` und **nie** in einen Commit. Vor jedem Commit `wreck guard`.
2. **Nicht unterstützen:** Bezahl-/Lizenzsperren umgehen, fremde Geräte angreifen, Herstellerserver massenhaft
   abfragen, Klone bauen, Funkparameter ändern. Sag das kurz und biete die erlaubte Variante an.
3. **Rückweg vor Experiment.** Solange `write_to_device_allowed` false ist, bietest du nichts zum Flashen an –
   nur Analyse und Vorbereitung. Siehe `docs/RECOVERY.md`.
4. **Eine Änderung pro Build**, mit Byte-Diff-Prüfer und Testprotokoll (`templates/test-protocol.md`).
5. **Ehrliche Belegstufen** (`docs/EVIDENCE.md`). `am-geraet-bestaetigt` nur nach Rückmeldung des Menschen mit der
   Uhr. Nie „funktioniert“ schreiben, wenn nur der Rechner geprüft hat.
6. **Wesentliche Schritte absprechen:** Flashen, Veröffentlichen, Pushen auf `main`, Löschen – vorher fragen.

## Arbeitsablauf

| Phase | Ziel | Hauptwerkzeuge |
| --- | --- | --- |
| 0-recht | Rahmen bestätigt | `LEGAL.md`, `LEGAL-ACK.md` |
| 1-erkennen | Chip, Begleitapp | `wreck apk`, `wreck identify`, Werkstestmenü |
| 2-beschaffen | eigene Firmware als Datei | `wreck provenance` |
| 3-rueckweg | Rückweg nachgewiesen | `docs/RECOVERY.md` |
| 4-verstehen | Hardware, Formate | `wreck entropy/strings/scan/watchface`, `docs/TOOLS.md` |
| 5-anpassen | kleinste Änderung, geprüft | Prüfer, `wreck report` |
| 6-app-schicht | eigene Apps ohne neue Firmware | `docs/APP-LAYER.md` |

Ausführlich: `docs/PLAYBOOK.md`. Beispielgerät mit echten Ergebnissen: `devices/m78-jl701n/`.

## Ergebnisse festhalten

```sh
wreck fact <gerät> display '{"w":368,"h":448,"bus":"QSPI"}' --status am-rechner-geprueft --evidence "wreck scan"
wreck ledger <gerät> "<Aussage>" --status vermutet --source "<woher>"
wreck report <gerät> "<Titel>"
wreck check                 # Profile gültig?
wreck guard                 # nichts Verbotenes im Repo?
python3 -m unittest discover -s tests
```

## Stil

- Antworten und Berichte in der Sprache des Menschen (Repo-Doku: Deutsch). Einfache Worte, Ergebnis zuerst.
- Für Downloads/Testbuilds immer: was ist es, was ändert es, wie testen, wie zurück.
- Neue Erkenntnisse zu Chips oder Formaten → `wreck/data/hints.json`, `docs/CHIPS.md`, `docs/formats/` (mit Quelle).
