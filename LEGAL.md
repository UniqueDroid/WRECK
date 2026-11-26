# Rechtlicher Rahmen

> **Keine Rechtsberatung.** Diese Seite fasst zusammen, woran sich WRECK hält, und nennt die Vorschriften, auf
> die sich das stützt (Stand November 2026, Deutschland/EU). Im Zweifel eine Anwältin oder einen Anwalt fragen.
> Außerhalb der EU gelten andere Regeln (z. B. in den USA DMCA § 1201 mit eigenen Ausnahmen).

## Kurz

WRECK hilft, **das eigene, rechtmäßig erworbene Gerät** zu verstehen, Fehler zu beheben und es mit **selbst
geschriebener Software** zusammenarbeiten zu lassen. Herstellermaterial bleibt privat, veröffentlicht werden nur
eigene Werkzeuge, eigene Texte und die für die Zusammenarbeit nötigen Fakten.

## Worauf sich das stützt

| Vorschrift | Inhalt (vereinfacht) | Bedeutung für WRECK |
| --- | --- | --- |
| § 69d Abs. 3 UrhG | Wer ein Programm berechtigt nutzt, darf sein Funktionieren beobachten, untersuchen und testen, um die zugrunde liegenden Ideen und Grundsätze zu ermitteln. | Strings, Entropie, Laufzeitverhalten, Bluetooth-Verkehr der eigenen Uhr ansehen. |
| § 69d Abs. 1 UrhG | Vervielfältigung und Umarbeitung, soweit für die bestimmungsgemäße Nutzung einschließlich Fehlerberichtigung nötig. Der EuGH hat 2021 (C‑13/20, *Top System*) entschieden, dass dazu auch Dekompilieren gehören kann. | Fehler in der eigenen Firmware/App finden und beheben. |
| § 69e UrhG | Dekompilieren ist ohne Zustimmung erlaubt, wenn es unerlässlich ist, um Informationen für die **Interoperabilität eines unabhängig geschaffenen Programms** zu bekommen; nur durch Berechtigte, nur soweit die Informationen nicht schon zugänglich sind, nur für die nötigen Teile. Die Informationen dürfen nicht für andere Zwecke genutzt, nur soweit für die Interoperabilität nötig an Dritte gegeben und nicht für ein im Wesentlichen ähnliches Programm verwendet werden. | Schnittstellen, Dateiformate, Update-Weg für eigene Apps, eigene Zifferblätter, eigene Firmware. |
| § 69g Abs. 2 UrhG | Diese Rechte lassen sich vertraglich nicht ausschließen. | Ein „Reverse Engineering verboten“ in AGB hebelt § 69d Abs. 3 und § 69e nicht aus. |
| § 3 Abs. 1 Nr. 2 GeschGehG | Beobachten, Untersuchen, Rückbauen oder Testen eines Produkts ist erlaubt, wenn es öffentlich verfügbar gemacht wurde oder rechtmäßig im eigenen Besitz ist und keine Pflicht zur Beschränkung besteht. | Hardware-Untersuchung der gekauften Uhr. Kein NDA/Entwicklervertrag unterschrieben? Dann gilt das. |
| § 69a Abs. 5 UrhG | Die Regeln zu technischen Schutzmaßnahmen (§§ 95a–95d) gelten nicht für Computerprogramme. | Trotzdem umgeht WRECK keine Kopierschutz- oder Bezahlsperren (siehe unten) – das ist unsere Regel, nicht nur das Gesetz. |

## Verbindliche Regeln für dieses Repo (strenger als das Gesetz)

**Nie ins Repo** – `wreck guard` und der pre-commit-Hook prüfen das:

1. Herstellerfirmware, Update-Dateien, Flash-Dumps, Begleitapps (`.bin`, `.ufw`, `.apk`, …), auch nicht teilweise.
2. Hersteller-SDKs oder Quelltext ohne freie Lizenz („All Rights Reserved“).
3. Decompiler-Ausgaben (Smali, Ghidra-C, Jadx-Java) von Herstellercode. Erkenntnisse daraus in **eigenen Worten**
   als Formatbeschreibung oder Faktentabelle.
4. Schlüssel, Zertifikate, Signatur-Keystores, Zugangsdaten, Tokens – auch nicht „nur zum Test“.
5. Persönliche Daten: MAC-Adressen, Seriennummern, Gesundheitsdaten, Fotos mit Personen, Kontodaten der App.

**Nicht Ziel von WRECK** – Agenten lehnen solche Aufgaben ab:

- Bezahlfunktionen, Lizenzprüfungen oder Abo-Sperren umgehen; kostenpflichtige Zifferblätter kopieren oder verteilen.
- Fremde Geräte angreifen, Kopplungen kapern, fremden Bluetooth-Verkehr mitschneiden.
- Server des Herstellers massenhaft abfragen, Zugänge anderer nutzen, Kataloge „spiegeln“.
- Klone bauen: eine Firmware oder App, die im Wesentlichen das Herstellerprodukt nachbildet (§ 69e Abs. 2 Nr. 3).
- Funkparameter verändern (Sendeleistung, Kanäle, Frequenzen). Das kann die Konformität nach der
  Funkanlagenrichtlinie 2014/53/EU (in Deutschland FuAG) aufheben.
- Gesundheitsfunktionen als medizinisch ausgeben. Eine Bastel-Uhr ist kein Medizinprodukt.
- Marken oder Logos des Herstellers so nutzen, dass man eigene Builds für Originale halten könnte.

## Was veröffentlicht werden darf

| Darf ins Repo | Bleibt in `private/` |
| --- | --- |
| eigene Werkzeuge, Skripte, Tests | Firmware, Dumps, APKs, Ressourcen des Herstellers |
| eigene Apps, Zifferblätter, Schriften mit freier Lizenz | daraus ausgeschnittene Bilder, Texte, Schriften |
| Formatbeschreibungen in eigenen Worten (`docs/formats/`) | Decompiler-Projekte, Disassembly-Listen |
| Hardware-Fakten: Chip, Display, Pins, Busse, Adressen | Adressen *innerhalb* der Herstellerfirmware, Patchstellen |
| Prüfsummen von Herstellerdateien (zur Wiedererkennung) | eigene Builds, die Herstellercode enthalten |

Eigene Builds, die Herstellercode enthalten (gepatchte Firmware), sind für **das eigene Gerät**. Weitergabe nur,
wenn klar ist, dass das erlaubt ist – im Zweifel nicht.

## Für KI-Agenten

Bevor du etwas auf eine Uhr schreibst, etwas veröffentlichst oder Herstellerdateien anfasst: `wreck next <gerät>`
ausführen und die Phase beachten. Wenn eine Aufgabe unter „Nicht Ziel von WRECK“ fällt, sag das klar und biete
die erlaubte Variante an (z. B. eigenes Zifferblatt statt Kopie eines Bezahl-Zifferblatts).
