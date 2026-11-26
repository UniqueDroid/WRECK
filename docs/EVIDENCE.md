# Belege, Profile, Berichte

## Ablage

```
devices/<gerät>/
  profile.json       Fakten mit Status und Belegen (Schema wreck-profile/1)
  ledger.jsonl       Belegbuch: eine Aussage je Zeile, mit Status und Quelle
  provenance.jsonl   Herkunft privater Dateien (Name, Größe, SHA-256, woher, wie)
  LEGAL-ACK.md       Bestätigung des rechtlichen Rahmens
  reports/           Berichte (eigene Worte)
private/<gerät>/     NIE im Repo: inbox, firmware, apk, dumps, decompiled, builds
```

## Statuswerte

| Status | Bedeutung | Wer darf ihn setzen |
| --- | --- | --- |
| `offen` | unbekannt | – |
| `vermutet` | Hinweis, nicht geprüft (Strings, Teardown eines Geschwistermodells) | Mensch, Agent |
| `am-rechner-geprueft` | durch Analyse/Modell/Test am Rechner belegt | Mensch, Agent (mit Beleg) |
| `am-geraet-bestaetigt` | an der echten Uhr beobachtet | **nur** nach Rückmeldung des Menschen mit der Uhr |
| `widerlegt` | geprüft und falsch | Mensch, Agent (mit Beleg) |

`wreck check` lehnt Profile ab, deren Status ≥ `am-rechner-geprueft` keinen Beleg hat.

## Belegbuch

```
wreck ledger <gerät> "Touch-Controller antwortet auf I²C 0x2E" --status am-geraet-bestaetigt --source "Diagnose-App, Foto 2" --fact touch
```

Quellen in eigenen Worten. Herstellerinterne Adressen nur in privaten Notizen, nicht im öffentlichen Belegbuch.

## Berichte

`wreck report <gerät> "<titel>"` legt einen Bericht aus `templates/report.md` an. Aufbau: Ergebnis zuerst, dann
belegt / vermutet / offen, dann Downloads (nur eigene Dateien), dann Rückweg. Ein Bericht endet nie mit „funktioniert“,
wenn kein Gerätetest stattgefunden hat.
