# Rückweg zuerst

Eine China-Uhr hat selten einen Rettungsmodus, und fast nie einen zugänglichen Datenanschluss (kontaktloses Laden).
Eine Firmware, die nicht bis zu ihrer Bluetooth-Update-Funktion startet, macht die Uhr ohne Öffnen unbrauchbar.
Deshalb ist der Rückweg eine eigene Phase mit eigenem Tor.

## 1. Den Update-Weg verstehen (am Rechner)

In drei Schritte zerlegen und für jeden festhalten, **wer** ihn ausführt:

| Schritt | Typische Frage | M78 (JieLi JL701N) |
| --- | --- | --- |
| Übertragen | Wer empfängt die Datei, wo wird sie zwischengespeichert? | Laufende Herstellerfirmware per Bluetooth, Zwischenbereich im externen NOR |
| Auslösen | Was startet das Einspielen (Übergabe im RAM, Merker im Flash, Neustart)? | Übergabe im RAM, dann Neustart; Auslöser hängt an der Oberflächen-Task |
| Schreiben | Wer schreibt die neue App in den Programmspeicher? | Bootloader startet einen Loader aus der Update-Datei; **kein Bluetooth nötig** |

Daraus folgt, welcher Teil eine kaputte App überlebt. Bei der M78: Übertragen braucht die laufende App, Schreiben nicht.

Außerdem klären:

- **Bänke:** Einfache Bank = die alte App wird überschrieben, kein automatisches Zurück. Doppelte Bank = Umschalten
  erst nach Prüfung (nur wenn der Bootloader das kann – nachweisen, nicht annehmen).
- **Prüfsummen/Signaturen:** Welche prüft der Loader? Ein Container mit falscher Prüfsumme wird oft still verworfen –
  gut als harmloser erster Test des Weges.
- **Bootloader-Fallback:** Gibt es einen? (M78: nein; letzter Ausweg wäre UART an Testpunkten.)

## 2. Muster für einen sicheren Rückweg

Vom sichersten zum riskantesten:

1. **Nichts Bleibendes ändern.** Eigener Code läuft nur im RAM/PSRAM und wird von der unveränderten Herstellerfirmware
   gestartet. Jeder Neustart führt zur Originalfirmware zurück. (Bei der M78 so umgesetzt: eigener Code aus dem PSRAM,
   gestartet durch eine eigene App.)
2. **Starter mit Notausgang.** Ein eigenes Startprogramm läuft nur, wenn beim Einschalten eine Taste gehalten wird.
   Ohne Taste: normale Firmware.
3. **Gepatchte Herstellerfirmware**, bei der Bluetooth-Update und Start **byte-gleich** zum Original bleiben
   (Prüfer vergleicht diese Bereiche ausdrücklich).
4. **Eigene Firmware** nur, wenn ein unabhängiger Rückweg *am Gerät* bestätigt ist (z. B. Update-Datei liegt geprüft im
   externen Flash und lässt sich ohne Bluetooth einspielen).

## 3. Rettungspaket vor dem ersten Test

Bevor der erste veränderte Build auf die Uhr geht, liegt bereit (privat):

- Originalfirmware mit Hash und Herkunftsnachweis
- die zuletzt **am Gerät bestätigte** eigene Version (falls vorhanden)
- eine Anleitung in einfachen Worten: welche App, welcher Knopf, wie lange warten, was tun bei kurzem Verbindungsfenster
- Hinweis auf den Hardware-Reset (falls vorhanden; ersetzt keinen Rückweg)

## 4. Testablauf am Gerät

`templates/test-protocol.md` verwenden. Immer:

1. Akku > 50 %, Handy nah, keine anderen Bluetooth-Apps verbunden.
2. Zuerst den Rückweg einmal durchspielen (Original neu einspielen), dann den Testbuild.
3. Ergebnis mit Foto/Video festhalten; ins Belegbuch mit Datum.
4. Bei Fehlverhalten: Build sofort als zurückgezogen markieren, Rückweg ausführen, erst dann Ursachen suchen.
