# Chipfamilien in China-Uhren

Startpunkt, kein Lexikon. Spalte „Sicherheit“: **sicher** = an einem Gerät in diesem Repo belegt,
**Hinweis** = verbreitete Annahme, am eigenen Gerät prüfen. Neue Einträge nur mit Quelle (Gerät, Teardown, Datenblatt).
Die gleichen Muster stehen maschinenlesbar in `wreck/data/hints.json` und werden von `wreck identify` genutzt.

| Familie | Typische Merkmale | Öffentliche Ressourcen | Sicherheit |
| --- | --- | --- | --- |
| **JieLi BR28** (AC701N / JL701N) | Strings `JL701N`, `isd_config`, `uboot.boot`, `ota.bin` im Update; CPU-Architektur pi32v2; QSPI-AMOLED; großer Teil des Updates verschlüsselt (hohe Entropie) | GitHub-Organisation *Jieli-Tech* (SDKs, Android-OTA-Bibliotheken); Community: *kagaimiq/jl-misctools* (Formate, Werkzeuge), *quarkslab/ghidra-jieli* (Prozessormodul, unvollständig) | sicher (M78) |
| JieLi BR23/BR25/BR35 | ähnliche Container und Strings, andere Chipnamen | wie oben | Hinweis |
| Realtek Bee (RTL876x) | `realsil`-Pakete in der App, Realtek-OTA | SDK teils nur über Händler | Hinweis |
| Actions (ATS30xx) | Strings `ATS30…`; eigene OTA-Formate | wenig öffentlich | Hinweis |
| SiFli (SF32LB5x) | Strings `SF32LB`, `sifli` | offenes SDK des Herstellers | Hinweis |
| Nordic nRF52 | `SoftDevice`, Nordic-DFU (`FE59`) | vollständig dokumentiert | Hinweis (eher ältere Bänder) |
| Bluetrum, Telink, BES | Chipnamen in Strings | unterschiedlich | Hinweis |

## Wichtig

- **Begleitapps sind Mehrchip-Apps.** Die M78-App enthält ein Realtek-SDK, obwohl die Uhr einen JieLi-Chip hat.
  Ein SDK-Paket in der APK ist nur ein Hinweis.
- **Gleiche Platine, viele Namen.** Modellnummern auf der Verpackung sagen wenig. Aussagekräftiger: Firmware-Präfix
  (z. B. `M78_4.10.62`), Bootloader-Hash, Display-Init-Tabelle, Tastentabelle.
- **Verschlüsselte Updates** sind normal. Die Entschlüsselung ist Formatwissen; WRECK liefert dafür bewusst keinen
  Code und keine Schlüssel. Wer sie für das eigene Gerät braucht, nutzt öffentliche Community-Werkzeuge nach eigener
  Prüfung von Lizenz und Rechtslage, lokal in `private/`.
