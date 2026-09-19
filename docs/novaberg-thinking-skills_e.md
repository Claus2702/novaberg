# Novaberg — Skills (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-thinking-skills_k.md`](novaberg-thinking-skills_k.md) · Ausarbeitung: [`novaberg-thinking-skills_t.md`](novaberg-thinking-skills_t.md) · Bauplan und Umstellung: [`novaberg-thinking-skills_b.md`](novaberg-thinking-skills_b.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen wörtlich zitiert in dem Absicht-Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §6.1, das wörtliche Zitat am Anfang des Abschnitts | 1:1-Invariante: ein Aufgabentyp, ein Skill; passt der Skill nicht, wird er geändert, nicht verdoppelt | Konzeptphase, Mai 2026 — der bisherige Kopf nennt den 09.05.2026 |
| **E2** | `_k` §6.2, das wörtliche Zitat am Anfang des Abschnitts | Skills modulieren die Werkzeug-Nutzung (den Suchbegriff), nicht die Werkzeug-Auswahl | Konzeptphase, Mai 2026 — der bisherige Kopf nennt den 09.05.2026 |

**Im Text als tragende Entscheidung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_k` §2.1: die Drei-Schicht-Trennung Plugins / Frames / Skills, *„als tragende Architektur-Aussage“*.
- `_t` §5.1: Skills entstehen aus Negativ-Feedback, *„als tragende Designentscheidung“*.
- `_k` §6.2: *„Diese Disziplin ist **non-negotiable**.“* — die Folgerung aus E2.

---

## B. Offen beim Meister

| | Stelle | Frage |
|---|---|---|
| **O1** | Abschnitt D, §12.4, *Mensch-geschriebene Skills* | Dürfen Skills, die ein Mensch geschrieben hat, von Pixie geändert werden (`urheber: mensch` plus `darf_pixie_aendern: false`), oder gibt es keine Sonderbehandlung? *„Noch zu entscheiden.“* |

**Offen ohne Frage** — was das Konzept selbst als offen führt, je mit einer pragmatischen Vorgabe:

- Abschnitt D, §12.1: die Granularität der Aufgabentypen (Frame-Lager-Klassen 1:1 oder eigene Subklassen).
- Abschnitt D, §12.2: eine Verstärkung erfolgreicher Skills über `gewicht` — *„Wirkung unklar — offen“*.
- Abschnitt D, §12.3: das Teilen von Skills zwischen Charakteren (`shared/`), vermutlich nach Phase B und C.
- Abschnitt D, §12.5: was ins Embedding eines Skills eingeht.
- Abschnitt D, §12.6: die Decay-Schwelle (6 Monate *„aus der Hüfte“*).

---

## C. Diskussion und verworfene Varianten

- `_k` §2.2: Skills als Plugins, als Workflows in einer Workflow-Engine, als Code-Skills (Epic 10, Typ 2) oder als Frames — je abgegrenzt, mit Grund.
- `_k` §6.2: Skills, die ein Werkzeug auswählen oder eine URL direkt ansteuern; ausgeschlossen, weil ein solcher Skill ein Sicherheitsrisiko wäre.
- `_t` §3.3: eine feste Struktur des Hauptteils; verworfen wegen Lesbarkeit und Editierbarkeit.
- `_t` §3.4: lange Skills, die jeden Sonderfall vorwegnehmen; als Anti-Pattern benannt.
- `_t` §4.1: Skills als Datenbank-Records; verworfen, weil Dateien sich mit Standard-Werkzeugen versionieren, lesen und sichern lassen.
- `_t` §4.2: ein Embedding über den ganzen Skill-Text; verworfen, weil lange Skills die Embeddings dominierten (Varianten in Abschnitt D, §12.5).
- `_t` §5.1: Skill-Erstellung aus Vor-Audit oder bei jedem Erfolg; verworfen gegen Skill-Inflation.
- `_t` §5.3: einen Skill ersetzen statt anpassen; ausgeschlossen durch die 1:1-Invariante (E1).

---

## D. Risiken und offene Punkte aus dem Konzept

§10 und §12 stehen ganz hier: Sie sind Diskussion und offene Fragen, keine Ausarbeitung.

## 10. Risiken

**Skill-Inflation.** Trotz 1:1-Invariante könnten zu viele Aufgabentypen entstehen, jeder mit eigenem Skill. Gegenmaßnahme: Aufgabentyp-Granularität durch Frame-Klassen kontrolliert (siehe §6.1). Wenn das Frame-Lager weniger Klassen unterscheidet als nötig, wachsen Skills auch nicht.

**Skill-Drift.** Pixie könnte Skills schreiben, die im Sprachstil oder Detailgrad inkonsistent sind. Gegenmaßnahme: Skill-Format-Konvention im Pixie-Schreib-Prompt mitgeben, plus periodische Audits durch Mensch oder Pixie selbst.

**Skill-Spam in Phase C.** Pixie schreibt zu viele Entwurfs-Skills, die nie aktiv werden. Gegenmaßnahme: Erstellungs-Schwelle (z.B. nur bei `negativ_explizit` mit klarem Material; bei `negativ_implizit` erst nach n Akkumulationen).

**Kollision mit Default-Vorgehen.** Skill und Default-Vorgehen könnten unterschiedlich sein, ohne dass das LLM merkt, wann welches besser passt. Gegenmaßnahme: Vorschlags-Charakter des Skills (§6.3), plus Reflexionsmarker bei systematischer Abweichung.

**Falsch geschriebene Skills.** Pixie schreibt einen Skill mit Logik-Fehler oder Halluzination. Gegenmaßnahme: User-Feedback als Korrektur-Quelle — bei nächster Anwendung wird der Fehler durch Negativ-Feedback sichtbar, Pixie korrigiert. Plus: Status `entwurf` für die ersten n Anwendungen, bei Erfolg auf `aktiv` setzen.

**Pixie-Reflexionslauf belastet System.** Skill-Schreibung ist LLM-Call. Gegenmaßnahme: niedriges Frequenz-Setting für die Reflexions-Schleife, Aggregation mehrerer Marker zu einem Schreib-Vorgang.

**Datei-System-Korruption.** Skills sind Dateien — was, wenn Pixie eine Datei zerschießt? Gegenmaßnahme: Git-Versionierung des Skill-Verzeichnisses (5.4), plus optionaler Read-Only-Modus für hartcodierte Skills (Mensch-geschriebene als read-only markiert).

---

## 12. Offene Punkte

### 12.1 Aufgabentyp-Granularität

Wenn das Frame-Lager `anliegen_wetter` als eine Klasse führt, gibt es einen Wetter-Skill. Aber: möglicherweise wären Subklassen sinnvoller — `anliegen_wetter_lokal` vs. `anliegen_wetter_termine_einbeziehend`. Aktuell offen, ob Skills ein eigenes Granularitäts-Schema brauchen oder ob die Frame-Lager-Klassen reichen.

Pragmatisch: zunächst Frame-Lager-Klassen 1:1 nutzen. Wenn sich zeigt, dass mehrere Skills denselben Aufgabentyp betreffen würden, ist das ein Hinweis, dass die Klasse zu grob ist — entweder Frame-Lager-Klasse splitten oder Skill-Subklassen einführen.

### 12.2 Skill-Verstärkung bei Erfolg

Heute: Skills entstehen aus Negativ-Feedback, werden bei Negativ-Feedback geändert. Kein Mechanismus, der Skills *verstärkt*, wenn sie erfolgreich sind.

Alternative: bei jedem `erfolgs_zaehler++` das `gewicht` leicht erhöhen (z.B. 0.01). Damit driften erfolgreiche Skills im Gewicht nach oben, und beim Lookup kann Gewicht als Tiebreaker dienen, wenn Themen-Tag-Treffer mehrdeutig sind. Implementierung trivial, Wirkung unklar — offen.

### 12.3 Skill-Sharing zwischen Charakteren

Wenn ein Nutzer mehrere Charaktere hat (Nova, anderer), sollen Skills geteilt werden? Ein "Liste-Verwaltung"-Skill ist wahrscheinlich charakter-unabhängig — er beschreibt Plugin-Nutzung, nicht Persönlichkeit. Ein "Wetter-Anfragen"-Skill mit Wohnort-Default ist nutzer-spezifisch, aber charakter-unabhängig.

Schema-Vorschlag (§4.1) sah einen `shared/` -Ordner vor. Implementierung der Sharing-Logik offen — vermutlich nicht in Phase B/C, sondern später.

### 12.4 Mensch-geschriebene Skills

Phase B startet mit drei bis fünf manuell geschriebenen Skills. Sind die ungesetzlich für Pixie? Pragmatisch: Front-Matter-Feld `urheber: mensch` plus `darf_pixie_aendern: false` als Schutz. Pixie liest, befolgt, aber editiert nicht. Bei Negativ-Feedback markiert Pixie das als Hinweis für menschliches Edit, schreibt aber nicht selbst.

Alternative: keine Sonderbehandlung, Pixie editiert auch Mensch-Skills. Risiko: Mensch-Intent geht verloren. Noch zu entscheiden.

### 12.5 Skill-Embeddings — was indexieren?

Aus §4.2: Embedding aus Themen-Tags und erster Hauptteil-Zeile. Alternative: ganzer Hauptteil. Kompromiss: erste 500 Zeichen.

Performance-Frage in der Implementierung. Pragmatisch: kurze Embeddings reichen für Themen-Lookup, lange Embeddings für Detail-Match. Hot-Path braucht keine Detail-Match, also kurz.

### 12.6 Decay-Schwellwerte

Wann ist ein Skill "lange inaktiv"? 6 Monate ist eine Zahl aus der Hüfte. Pragmatisch: konservativ kalibrieren (eher länger), bei Bedarf nachjustieren.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. Alle fünf stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_k` §6.1, letzter Absatz | Verweist für die offene Designfrage auf *„(siehe §10)“*; §10 sind die Risiken, die Frage steht in §12.1 (Abschnitt D) | `[gelesen 19.09.2026]` |
| **B2** | Abschnitt D, §10, *Datei-System-Korruption* | *„Git-Versionierung des Skill-Verzeichnisses (5.4)“*; §5.4 ist *Decay und Tod*, die Git-Versionierung steht in `_t` §8.4 | `[gelesen 19.09.2026]` |
| **B3** | `_t` §9 (auch §3.1) | Die Beispiel-Skills tragen Zähler (`anwendungs_zaehler`, `erfolgs_zaehler`) und Daten, die wie echte Erfahrung wirken; das Konzept hat keinen Baustand, die Featureliste führt das Skill-System ohne Code | `[gelesen 19.09.2026]` |
| **B4** | `_k` §2.3 | Die Aussage, Anthropic verwende beim Training seiner Modelle ein Skills-Pattern, ist unbelegt | `[gelesen 19.09.2026]` |
| **B5** | das ganze Konzept; `_k` §14 | Kein Bezug zum Lage-Konzept (`novaberg-thinking-lage_k.md`), das die Pipeline inzwischen trägt | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Schluss

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Skills — Selbst-editierbare Arbeitsanweisungen für wiederkehrende Anliegen (Konzept)
**Stand:** 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-skills_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (Skill-Konzept entstanden aus dem Self-Learning-Strang nach dem Wetter-Korrektur-Beispiel; klare Positionierung gegen Plugins/Agents und gegen Frames; tragende Disziplinen aus Meisters direkten Antworten)

Die Schlusszeile des ungeteilten Konzepts, ungekürzt:

*Stand 09.05.2026 — Chat 81. Skills als selbst-editierbare Markdown-Dateien für wiederkehrende Anliegen. 1:1-Invariante (Aufgabentyp ↔ Skill). Modulation statt Werkzeug-Auswahl. Fehler-getrieben entstehend, autonom editiert durch Pixie, Vorschlags-Charakter im Executor. Phase A funktioniert ohne Skills — sie sind die Verfeinerung, nicht die Grundlage.*
