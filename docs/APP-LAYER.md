# Eigene App-Schicht

Jede neue Funktion als Firmware-Patch zu bauen ist teuer und riskant. Besser: **einmal** eine kleine
Laufzeitumgebung in die (gepatchte) Herstellerfirmware bringen, die eigene Apps aus Dateien lädt. Danach braucht eine
neue App keinen Firmware-Build mehr.

Bei der M78 wurde das mit einer kleinen JavaScript-Engine (MicroQuickJS, etwa ES5) umgesetzt; Apps kommen als Paket
über die Begleitapp und landen als Textdatei auf der Uhr. Das Muster lässt sich auf andere Uhren übertragen.

## Bausteine

| Baustein | Aufgabe | Hinweis |
| --- | --- | --- |
| Engine | Skript ausführen, Speicher begrenzen | klein halten (M78: 64 KB RAM je App) |
| Einstieg | Liste „Apps“ in der Uhr, App öffnen/schließen | vorhandenes Menü wiederverwenden |
| Zeichnen/Eingabe | `draw()`, `tap(x, y)`, Tasten | über die Grafikroutinen der Firmware |
| Transport | Dateien von der Begleitapp zur Uhr | vorhandenen Weg nutzen (M78: Weg der E-Books) |
| Begleitteil | Handy-Seite einer App (Internet, Einstellungen) | Uhr hat kein Internet; Schlüssel bleiben auf dem Handy |
| Berechtigungen | was eine App darf | von der Uhr bei jedem Aufruf geprüft |

## Paketformat (Vorschlag, wie bei der M78 erprobt)

```
meine-app/
  app.json              id, name, version, permissions, companion
  app.js                Programm für die Uhr
  icon.png
  i18n/de.json, en.json
  CompanionActivity.js  optional: Teil auf dem Handy
```

```json
{
  "id": "de.beispiel.wetter",
  "name": "Wetter",
  "version": "1.0.0",
  "type": "app",
  "permissions": ["phone.message", "timer"],
  "companion": { "main": "CompanionActivity.js", "hosts": ["api.example.org"] }
}
```

## Regeln, die sich bewährt haben

- **Berechtigungen als feste Bitnummern**, die sich nie ändern (alte Firmware + neue Pakete passen zusammen).
- **Internet nur über den Handy-Teil** und nur zu den in `hosts` genannten Servern, nur HTTPS, keine Weiterleitungen.
- **Kurze Nachrichten** Uhr ↔ Handy (M78: 200 Bytes), Antworten der Server bleiben auf dem Handy.
- **Packer lehnt Unbekanntes ab** (unbekannte Felder, Berechtigungen, zu große Pakete) – Tippfehler fallen sofort auf.
- **Gleiche Eingabe, gleiche Bytes:** Pakete reproduzierbar bauen.
- **Diagnose-Berechtigung** (`debug`: Speicher nur lesen) – damit werden Pin- und Tastenfragen am Gerät geklärt.
- Apps laufen in der Firmware-Task, die sie startet; **nicht dauerhaft die Oberflächen-Task belegen**, sonst laufen
  Mitteilungen, Synchronisation und Updates nicht mehr (M78-Befund).

## Grenzen dokumentieren

Jede Uhr hat andere Grenzen (Dateigröße, RAM, Texte je Bild, Symbolgröße). Sie gehören ins Geräteprofil unter
`app_layer`, mit Belegstufe.
