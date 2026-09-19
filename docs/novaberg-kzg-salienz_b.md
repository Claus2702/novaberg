# Novaberg — KZG-Salienz: Neubau als abgeleiteter Wert (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-kzg-salienz_k.md`](novaberg-kzg-salienz_k.md) · Ausarbeitung: [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md) · Diskussion und Ergänzungen: [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen.

---

## 10. Migration — entfällt

`salienz_eingang` fehlte dem Bestand, und der alte `salienz`-Wert taugte nicht zur Rückrechnung: Der Akkumulator ist pfadabhängig, die Eingangsbewertung war überschrieben. Genau der Verlust, den die Konvention beschreibt — die alte Bauart konnte ihre eigene Migration nicht tragen.

~~**Aufgelöst durch den Reset am 27.07.2026, 09:13 UTC.** Die KZG-Partition wurde vollständig geleert (864 Schlüssel). Es gibt keinen Altbestand mehr, der zu migrieren wäre.~~ — **überholt am 28.07.2026.** Der Reset lag einen Tag zurück, als Bauteil 1 gebaut wurde; in dieser Zeit sind **192 neue Einträge** entstanden, 71 davon bereits über 1.0. Der Satz war zum Zeitpunkt seiner Niederschrift richtig und hatte ein Verfallsdatum, das er nicht nannte: **Ein leerer Bestand bleibt nur so lange leer, wie das System steht.**

Der im nächsten Absatz formulierte Vorbehalt griff damit wörtlich — nur nicht aus einem Backup, sondern aus dem laufenden Betrieb.

Damit entfällt auch die Frage nach einem Herkunftsfeld, das *gesetzt* von *gemessen* trennt. Sie wäre nötig gewesen, wenn Alteinträge eine erfundene Eingangsbewertung bekommen hätten — nach der Regel, dass ein Default nie aussehen darf wie ein echter Wert. **Kommt jemals ein Bestand ohne `salienz_eingang` hinzu — etwa aus einem Backup —, gilt die Regel wieder.**

### Die Migration, wie sie stattgefunden hat (28.07.2026)

`scripts/migration_kzg_salienz_eingang.py`, idempotent, zweimal gelaufen. Zwei Fälle, getrennt nach Rekonstruierbarkeit:

| Fall | Einträge | `salienz_eingang` | Herkunft |
|---|---|---|---|
| `haeufigkeit = 1` | 87 | `= salienz` — nie verstärkt, also unverändert die Modellbewertung | `gemessen` |
| `haeufigkeit > 1` | 107 | `= 0.6`, gesetzt | `geschaetzt` |

Der Akkumulator war pfadabhängig; für verstärkte Einträge existiert die Eingangsbewertung nirgends mehr. Das Feld `salienz_eingang_herkunft` trennt beide Fälle dauerhaft — es ist die Vorkehrung, die der Absatz oben verlangt, und es steht auch an jedem neu angelegten Eintrag (`gemessen`).

**Wirkung der Setzung 0.6:** Unter der neuen Kurve liegt sie zwischen MID und HIGH. Die Masse der geschätzten Einträge (70 mit zwei oder drei Verstärkungen) bleibt bei 0.9142 bzw. 0.9278 knapp unter dem Promotionstor; 32 mit vier und mehr Verstärkungen gehen durch. Wer oft wiederkam, wird promotet — der Ansammlungspfad wirkt rückwirkend so, wie er soll.

**Der LZG-Altbestand bleibt unberührt.** 126 aktive Knoten tragen weiter `gewicht_roh` bis 2.574 — sie wurden vor dem Umbau aus der gebrochenen Skala promotet. Für neue Knoten kann `roh > 1.0` nicht mehr auftreten (§9); der Altbestand trägt `KZG-GEWICHT-ABSOLUT-CEILING` weiter, bis er verfällt.

## 11. ZIEL / TEST / MESSUNG

### Bauteil 0 — die Salienz wird beobachtbar

**Zuerst, vor jeder Formeländerung.** `graph/nodes/salience.py` schreibt in keinem Graphen eine Zeile ins `pipeline_log` (`SALIENZ-OHNE-PIPELINE-LOG`). Der Wert, der über Erinnern entscheidet, existiert damit nur flüchtig im Container-Log.

Ohne diesen Schritt nähme der Neubau seine eigene Abnahme ohne Messgerät ab. Genau daran lag es, dass `bewertungs_laenge=0` im AgentGraph seit Einführung des Graphen unbemerkt blieb: Der Fehler war da, aber nichts hielt ihn fest.

| | |
|---|---|
| **ZIEL** | Für jeden Turn ist im Nachhinein aus der Datenbank beantwortbar: Welcher Text wurde bewertet, welcher lag nur als Hintergrund an, in wie viele Segmente wurde geschnitten, und welchen Salienzwert bekam jedes Segment. Ohne Container-Log. |
| **TEST** | Ein Testlauf über `analyze()` mit einem Fake-Buffer sammelt die Einträge: erwartet werden `span_start`, ein `switch` mit `graph_rolle` und beiden Textlängen, je Segment eine `berechnung` mit dem Salienzwert, und `span_end` mit Segment- und `pending_writes`-Zahl. Zweiter Test für den Fehlerpfad: leeres Bewertungsobjekt erzeugt einen `fehler`-Eintrag und **kein** `pending_write`. |
| **Positiver Zwilling** | Die Zusicherung „kein `pending_write` bei leerem Bewertungsobjekt" kann die Gegenprobe allein nicht bestehen. Derselbe Test prüft deshalb zusätzlich, dass ein gefüllter Text **genau ein** `pending_write` und **eine** `berechnung` erzeugt. |
| **Gegenprobe** | Die `log_berechnung`-Zeile testweise entfernen — der Segment-Test muss rot werden. Danach zurücknehmen. |
| **MESSUNG** | Ein Live-Turn zu einem Wissenschaftsthema, danach `SELECT art, quelle, inhalt FROM pipeline_log WHERE turn_id = '<turn>' AND node = 'salienz' ORDER BY id;`. Der Salienzwert muss dort stehen, ohne dass ein Container-Log gelesen wird. Gegenprobe zum Chat-110-Befund: Ein Impuls-Turn muss `quelle='agent'` tragen und ein Bewertungsobjekt mit Länge > 0. |

**Abgrenzung:** Bauteil 0 ändert **keinen** Wert und **keine** Formel. Es macht nur sichtbar, was ohnehin geschieht. Damit ist es vor dem Umbau messbar und liefert die Vergleichsbasis für danach.

### Bauteil 1a — das Segment erreicht den Verdichter

**Vor dem Formel-Umbau.** Gemessen am Turn `975ec093…` (27.07.2026, mit dem Messgerät aus Bauteil 0):

Der Segmentierer schneidet richtig — 137 / 487 / 222 Zeichen, genau die drei Absätze einer Antwort: Novas Reaktion auf den Themenwechsel, der Sachkern, Novas Selbstbezug. Gespeichert wurden aber **drei Paraphrasen desselben Sachkerns**. Die anderen beiden Segmente sind verloren.

**Ursache, im Code belegt.** Der `pending_write` trägt in `daten` nur `salienz_obj` — das Segment selbst wird verworfen. `agents/kzg/dispatch.py:111-115` füllt `parameter` aus dem State mit `user_prompt` und `response`, also dem ganzen Turn. `verdichtung.py:93-94` liest genau die. Drei Segmente ergeben damit drei LLM-Aufrufe mit **bitgleicher Eingabe**; bei `temperature: 0.1` entstehen drei Paraphrasen.

Das ist ein **Datenpfad**-Defekt, kein Prompt-Defekt. Der Verdichter zieht nicht den Gesamtzusammenhang dem Segment vor — er hat kein Segment, aus dem er wählen könnte. Am Prompt zu drehen hätte beliebig lange nichts geändert.

**Warum vor Bauteil 1.** Der Neubau kalibriert die Skala. Solange ein Turn dreifaches Gewicht für einen Gedanken erzeugt, kalibriert er auf einer verfälschten Mengenbasis. Und für Bauteil 3 wiegt es schwerer: Verloren gehen ausgerechnet die Segmente mit Selbstbezug und Regung — die assistant-Partition behält das Lexikon und wirft weg, was über Nova etwas sagt.

| | |
|---|---|
| **ZIEL** | Ein Turn mit drei Segmenten erzeugt drei Gedächtnis-Einträge mit drei **verschiedenen** Inhalten, jeder erkennbar zu seinem Segment gehörend. Fehlt ein Segment, wird der Volltext verdichtet und das ausdrücklich protokolliert. |
| **TEST** | `pending_write["daten"]` trägt `segment`, `segment_index`, `segment_gesamt`; `dispatch_kzg` reicht sie in `parameter`. Verdichtung mit Segment nimmt das Segment ins `[BEWERTUNGSOBJEKT]`, nicht den Volltext. Ohne Segment fällt sie auf den Volltext zurück **und** schreibt eine Zeile, die das benennt — ein Rückfall darf nicht aussehen wie ein Normalfall. |
| **Gegenprobe** | Die Segment-Bevorzugung in `verdichtung.py` entfernen — der Test, der drei verschiedene `[BEWERTUNGSOBJEKT]`-Inhalte erwartet, muss rot werden. |
| **MESSUNG** | Live-Turn mit drei Absätzen zu einem Wissenschaftsthema. Über `verbindung` die drei Keys holen, `HGET <key> inhalt` für alle drei: **drei verschiedene MD5**, und jeder Inhalt gehört erkennbar zu seinem Absatz. Vollständig ausgeben, nicht abschneiden — ein `cut` hat bei genau dieser Frage schon einmal Gleichheit vorgetäuscht. |

**Offenes Risiko, bewusst nicht vorweggenommen.** Ein Segment kann ohne seine Nachbarn unauflösbar sein — Segment 2 begann mit *„In gewisser Weise ist es genau das…"*, und worauf „das" zeigt, steht in Segment 1. Das `[LAGEBILD]` bleibt deshalb unverändert die andere Turn-Hälfte; es wird **nicht** um den Volltext erweitert. Sonst stünde der ganze Text wieder im Prompt und wir hätten die Ursache reproduziert, die wir gerade beseitigen. Zeigt die Messung unauflösbare Kerne, wird das Lagebild danach **gezielt** erweitert — als eigene Änderung mit eigener Messung, nicht auf Verdacht zusammen mit dieser.

**Abnahme — Turn `cb8f02e5…`, 27.07.2026 11:14 UTC.** Drei Segmente von 118 / 375 / 699 Zeichen, drei Einträge mit **drei verschiedenen MD5**, jeder Kern erkennbar zu seinem Absatz: die Rahmung („eine funktionale Hierarchie der Kohärenz"), der lokale Teil („spezialisierte neuronale Ensembles… lokale Oszillationen"), der globale Teil („Communication Through Coherence… Phasenlagen"). Die Kernlängen skalieren mit den Segmentlängen: 101 / 210 / 353 Zeichen.

Gegenprüfung am Log: viermal `quelle=segment`, **null** Rückfall-Warnungen, `bewertungs_laenge` je 118 / 375 / 699 statt der 1192 des Volltexts — der Verdichter hat das Segment gelesen, nicht den Turn. `lagebild_laenge=165` ist der Nutzerprompt; das Lagebild ist die andere Turn-Hälfte geblieben.

**Zum offenen Risiko, erster Datenpunkt:** Segment 0 begann mit *„Das ist genau das Paradoxon…"* — ein Rückverweis ohne eigenen Bezug. Der Kern wurde trotzdem sinnvoll; das Lagebild hat gereicht. Das belegt **einen Fall, nicht die Klasse.** Der Vorbehalt bleibt bestehen, bis mehrere Turns mit rückverweisenden Segmenten gemessen sind.

**Nicht behoben:** Alle drei Segmente erhielten erneut Salienz **0.3**, bei drei inhaltlich völlig verschiedenen Absätzen. Der Durchstich hat den Verdichter repariert, die Bewertung nicht. Der Verdacht, dass auch sie den Gesamtzusammenhang statt des Segments liest, steht weiter in der Fundliste und ist vor Bauteil 1 zu klären — eine Skala neu zu kalibrieren, deren Eingangswert womöglich das Falsche misst, wäre verfrüht.

### Bauteil 1b — die Salienz von Novas Äußerung wird gerechnet, nicht gefragt

**Befund (`SALIENZ-PROMPT-NUTZER-SCHABLONE`, Chat 111).** `_build_salienz_prompt()` kennt keinen Rollen-Parameter — derselbe Prompt geht an alle drei Graphen. Und er ist durchgehend aus der Nutzerperspektive geschrieben. `salienz.rules.txt` weist an:

> Bewerte die Salienz AUSSCHLIESSLICH anhand der EINGABE DES NUTZERS. Die Antwort des Assistenten ist Hintergrund-Kontext und darf die Bewertung NICHT beeinflussen.

Im CharacterGraph steht die Nutzereingabe im `[LAGEBILD]` und Novas Äußerung im `[BEWERTUNGSOBJEKT]`. **Die Anweisung ist exakt invertiert.** Im AgentGraph ist das Lagebild leer — dort wird angewiesen, etwas zu bewerten, das nicht existiert.

Dieselbe Fehlerklasse hat Chat 110 beim Verdichter behoben (drei Aufgaben-Blöcke nach Rolle, `DESTILLAT-SUBJEKT-SCHABLONE`). Der Salienz-Node eine Ebene höher wurde nicht mitgeprüft. Auf der Platte steht es nebeneinander: `kzg_verdichtung.{task,assistant_task,impuls_task}.txt` gegen ein einzelnes `salienz.task.txt`.

**Belegt an zwei Turns:** Alle Segmente erhielten 0.3 — auch eines mit dem Wort „liebe", für das die Regeln 0.7–0.8 vorsehen. Themen wurden wörtlich aus dem Lagebild übernommen.

> **Hinweis zur Aufteilung (19.09.2026):** Die Unterabschnitte *Was Salienz für Novas Äußerung bedeutet*, *Das neue Feld*, *Das Charakter-Rad* und *Zusammenspiel mit der Kurve* standen hier; sie arbeiten die Formel aus und stehen in [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md), *Aus §11 — Bauteil 1b*.

#### Der Prompt bleibt trotzdem zu reparieren — erledigt Chat 112

Die Salienz wird gerechnet, die übrigen Felder nicht: `themen`, `dimension`, `gedaechtnistyp`, `intentionen`, `emotion`, `modus`, `entitaeten_roh`, `zeitausdruck_roh` kommen weiter aus dem LLM-Call — und deren Kontamination aus dem Lagebild ist gemessen. Der Rollen-Switch nach dem Vorbild von `_build_verdichtung_prompt` wird also gebraucht, ~~nur nicht mehr für die Salienz-Skala~~ — **und zwar samt Skala**: Sie bleibt als vierter Antrieb des Eigen-Pfads, und jede Lage braucht ihre eigene.

**Gebaut und abgenommen.** Drei Aufgaben-Blöcke, geteilter Dimensionen-Block, beide `rules`-Dateien auf rollenneutrale Ausgaberegeln reduziert. Der invertierte Satz lag zweimal auf der Platte — auch im gemma4-Override, der die ganze Nutzer-Skala mitgeschleppt hatte. Details und Messung: `SALIENZ-PROMPT-NUTZER-SCHABLONE` in `novaberg-bugs.md`.

| | |
|---|---|
| **ZIEL** | Zwei Segmente derselben Antwort mit verschiedener Nähe zu Novas Zielen erhalten **verschiedene** Salienzwerte. Ein Segment ohne Zielbezug erhält die gewichtete Nutzer-Salienz als Boden. Kein Wert überschreitet 1.0. |
| **TEST** | Reine Funktion, ohne LLM prüfbar: `max(0.5 × 0.9, 0.0) = 0.45`; `max(0.5 × 1.5, 0.0) = 0.75`; `max(0.2 × 0.9, 0.8) = 0.8` — der Eigen-Pfad gewinnt. Idempotenz: zweimal rechnen liefert bitgleich. Feld-Test: frisch angelegter `charakter_hash` trägt `quelle='default'`, nach Destillation `'destilliert'` mit Zeitstempel. |
| **Gegenprobe** | `nutzer_gewichtung` testweise fest auf 1.0 — der Test, der 0.45 erwartet, muss rot werden. |
| **MESSUNG** | Live-Turn, dessen Antwort ein Segment mit Zielbezug und eines ohne enthält. Über `pipeline_log` beide Salienzwerte lesen: sie müssen sich unterscheiden. Zusätzlich `SELECT nutzer_gewichtung, nutzer_gewichtung_quelle FROM charakter_hash` — nach der ersten Destillation muss die Quelle `'destilliert'` lauten. |

#### Abnahme (Chat 112, 27.07.2026)

**Gebaut in zwei Teilen.** Erst der Transport: `salienz_human` erreicht den CharacterGraph desselben Turns. Dann die Formel.

Der Transport war die unbemerkte Vorbedingung. Der Wert wurde im HumanGraph gemessen und danach fallengelassen — er stand vierzig Sekunden vor dem CharacterGraph-Lauf unter derselben `turn_id` im `pipeline_log`, und der CharacterGraph fragte das Modell erneut. Ohne ihn gibt es keinen Pflicht-Pfad und die Formel fällt auf den Eigen-Pfad zusammen.

**Messturn 21:11 UTC**, zwei Nutzer-Segmente (0.7 / 0.3) → `salienz_human = 0.7`, `nutzer_gewichtung = 1.04` (`destilliert`):

| Segment | sprachlich | Eigen-Pfad | Pflicht-Pfad | effektiv | Gewinner |
|---|---|---|---|---|---|
| 1 | 0.75 | 0.885 | 0.728 | **0.885** | eigen |
| 2 | 0.40 | 0.472 | 0.728 | **0.728** | pflicht |

Drei Zusicherungen des ZIELs sind damit belegt: Die beiden Segmente erhalten **verschiedene** Werte. Das Segment ohne eigenen Zug bekommt die gewichtete Nutzer-Salienz als **Boden** — ohne ihn stünde es bei 0.472. Und kein Wert überschreitet 1.0.

**Beide Pfade gewinnen je einmal in einem einzigen Turn.** Das `max()` ist damit als echte Wahl belegt und nicht als Formalität.

`ziel_gravitation` stand auch hier bei 0.0. Seiteneffekte des Messturns: `timeline` 0 · `notizen` 0 · `fakten` 0.

**Gegenprobe, zweifach.** `(1 + z)` durch einen nackten Multiplikator `z` ersetzt → 10 Tests rot, darunter alle vier Auslöschungs-Tests. Leserichtung auf `charakter_hash` vertauscht → 1 Test rot; er legt beide Richtungen mit verschiedenen Faktoren an, damit die Verwechslung überhaupt bemerkbar ist. Beides zurückgenommen.

**Suite:** 173 → 222 Tests, grün, 0 übersprungen.

**Offen aus diesem Bauteil:** Der Rollen-Switch am Prompt (Bauteil unten) wird jetzt dringender, nicht weniger dringend — die sprachliche Lesung ist der einzige tragende Antrieb des Eigen-Pfads, und sie läuft weiterhin gegen die Nutzer-Schablone.

> **Hinweis zur Aufteilung (19.09.2026):** Der Unterabschnitt *Offen* (der AgentGraph) stand hier; er steht in [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md), Abschnitt C.

### Bauteil 1 — Salienz als abgeleiteter Wert ✅ Chat 113, live gemessen

**Abgenommen 28.07.2026.** Korpusweit: 194 Einträge, **kein einziger über 1.0**, Maximum exakt 1.0000 (vorher 5.636 bei 38 % über der Skala). Live-Turn 09:28 UTC: Anlegen mit `salienz=0.9170 (Eingang 0.64)`, TTL 14 Tage; vier Verstärkungen, jede aus `salienz_eingang` und `haeufigkeit` neu gerechnet, von Hand nachgeprüft (`0.6 + 4×0.03 = 0.72 → sin(0.72·π/2)^0.5 = 0.9512`); zwei Einträge bei `haeufigkeit` 16→17 stehen auf 1.0000 und bewegen sich nicht mehr — der Deckel hält, ohne dass ein Wert ihn überschreitet.

**Zwei Befunde aus der Abnahme**, beide oben eingearbeitet: die Rundungsrichtung der Tore (§5) und die überholte Migrationslage (§10). Der erste kam aus einem echten Turn, nicht aus einem Test — er betraf genau den Grenzwert, den kein Unit-Test traf, weil er die Konstante gegen sich selbst geprüft hätte.

| | |
|---|---|
| **ZIEL** | Ein Eintrag mit der Bewertung 0.5 erreicht die Promotionsschwelle nach genau sieben thematischen Verstärkungen — nach sechs noch nicht. Ein Eintrag mit 0.7 erreicht sie beim Anlegen. Kein Eintrag trägt je einen Wert über 1.0. |
| **TEST** | Unit-Test über die Salienz-Funktion: `(0.5, 6)` liegt unter `KZG_SALIENZ_HIGH`, `(0.5, 7)` erreicht sie, `(0.7, 0)` erreicht sie, `(1.0, 100)` ergibt exakt 1.0. Positiver Zwilling zur Deckel-Zusicherung: `(0.5, 0)` ergibt 0.8409, also einen Wert echt zwischen 0 und 1. Zweiter Test auf Idempotenz: zweimaliges Berechnen über denselben Eingaben liefert bitgleiche Werte. |
| **Gegenprobe** | `KZG_SALIENZ_BOOST` testweise auf 0.015 setzen — der Sieben-Verstärkungs-Test muss rot werden. Danach zurücknehmen. |
| **MESSUNG** | Ein Live-Turn zu einem Wissenschaftsthema. Über die `verbindung`-Brücke die KZG-Keys des Turns holen, `salienz_eingang`, `haeufigkeit` und `salienz` lesen und die Formel von Hand nachrechnen. Anschließend korpusweit: kein Key der Partition trägt `salienz > 1.0`. |

### Bauteil 2 — Promotion entfernt den Eintrag

| | |
|---|---|
| **ZIEL** | Ein Eintrag, der zu einem neuen LZG-Knoten geführt hat, existiert danach nicht mehr im KZG. Ein Eintrag, der nur einen bestehenden Knoten verstärkt oder reaktiviert hat, bleibt. |
| **TEST** | Nach einem Promotions-Lauf über den Neuanlage-Pfad: `exists(kzg_key)` ist falsch. Positiver Zwilling: derselbe Test vor dem Lauf ist wahr, und nach dem Reinforcement-Pfad bleibt der Key bestehen. Fehlerpfad mit `assertLogs`: Scheitert `knoten_anlegen`, wird nicht gelöscht und die Fehlerzeile erscheint. |
| **Gegenprobe** | Den Löschschritt entfernen — beide Zusicherungen müssen rot werden. |
| **MESSUNG** | Vollabgleich aller Keys der Partition gegen `lzg_knoten.kzg_quell_key`. Die Schnittmenge muss leer sein. Vorher die Spalte per `\d` verifizieren, nicht aus Log-Zeilen übernehmen. Dieselbe Messung beantwortet `PROMOTION-ENTFERNT-KZG-NICHT` und liefert die Datenbasis für `KZG-TTL-UNSTERBLICH`. |
