# Externe Werkzeuge

WRECK selbst ist klein (nur Python-Standardbibliothek). Für tiefere Analyse kommen externe Werkzeuge dazu. Alle
Ausgaben davon gehören nach `private/<gerät>/decompiled/`.

| Werkzeug | Zweck | Hinweise |
| --- | --- | --- |
| Ghidra | Disassembler/Decompiler | Für exotische CPUs (z. B. JieLi pi32v2) ein Prozessormodul nötig; Community-Module sind oft unvollständig – ein erfolgreicher Build beweist keine korrekte Semantik. Kleine Testfälle gegen bekannte Funktionen prüfen. |
| pypcode / SLEIGH | Befehle in P-Code übersetzen, Mini-Emulation | gut, um einzelne Funktionen am Rechner „laufen“ zu lassen und Aussagen zu prüfen |
| Jadx / Apktool | Begleitapp lesen | nur, was für die Interoperabilität nötig ist (Protokoll, Dateiformate); keine Klassen ins Repo |
| Android HCI-Snoop-Log + Wireshark | Bluetooth-Verkehr der **eigenen** Uhr mitschneiden | Entwickleroptionen → „Bluetooth HCI-Snoop-Log“ |
| nRF Connect | GATT-Dienste/Merkmale der Uhr ansehen | nur das eigene Gerät koppeln |
| Hersteller-SDK des Chips | Strukturen, Treiber, Namen wiedererkennen | Lizenz prüfen; meist nicht weitergeben |
| Community-Formatwerkzeuge | Container, Ressourcen | Lizenz prüfen; lokal verwenden |

## Muster für eigene Prüfwerkzeuge

- **Hash-gebundene Eingaben:** Ein Werkzeug, das eine bestimmte Originaldatei erwartet, prüft deren SHA-256 und bricht
  sonst ab. So entstehen keine Builds aus der falschen Vorlage.
- **Ausgabeordner muss neu sein:** nie etwas Vorhandenes überschreiben.
- **Prüfer getrennt vom Builder:** Der Prüfer liest den fertigen Build neu ein und vergleicht unabhängig.
- **JSON-Bericht je Lauf:** Eingabe-Hashes, Ausgabe-Hashes, geänderte Bereiche, `hardware_tested: false`.
