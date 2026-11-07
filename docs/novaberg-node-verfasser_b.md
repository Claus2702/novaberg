# Novaberg — Der Verfasser: Inhalt und Wesen werden getrennt (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-node-verfasser_k.md`](novaberg-node-verfasser_k.md) · Ausarbeitung: [`novaberg-node-verfasser_t.md`](novaberg-node-verfasser_t.md) · Diskussion und Ergänzungen: [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md) · Messungen: [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Nachträge am bisherigen Kopf

Im ungeteilten Konzept standen diese Nachträge zwischen dem Stands-Kopf und §1. Sie berichten, was am Knoten nach der Erstfassung gebaut wurde, und tragen die Messungen dazu mit; der Stands-Kopf selbst steht in [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md).

> **Nachgetragen am 04.08.2026 — was seit der Erstfassung dazukam.**
>
> Der Verfasser liefert nicht mehr nur Prosa, sondern **erst ein Urteil, dann den Text**. Vor der Antwort steht ein Kopfblock aus fünf Zeilen — Prüfung, dreiwertige Bewertung (`trifft_zu` / `trifft_nicht_zu` / `abweichend`), Stärke, Quelle — abgeschlossen durch eine Trennlinie. Ein Sprachmodell legt sich mit dem ersten Token fest; steht die Prüfung vor dem Urteil und das Urteil vor dem Text, kann die Zustimmung nicht mehr vor der Prüfung fallen.
>
> **Kein JSON, mit Grund.** Der Verfasser liefert Prosa bis über 3800 Zeichen; in JSON gepresst hinge der ganze Turn daran, dass das Modell einen langen Freitext fehlerfrei maskiert — ein Ausfall, der im Bestand belegt ist. Misslingt der Kopfblock, ist nur das Urteil weg, nicht die Antwort. Er erzeugt dann **keinen Vorgabewert**, sondern `geliefert=False` samt Fehlerzeile.
>
> Der Aufbau steht in `graph/einwand.py`, die gültigen Werte stehen **nur dort** und werden dem Prompt zur Laufzeit eingesetzt. Konzept des Bauteils: `novaberg-sykophanz-eindaemmung_k.md` §7 B1; übergeordnet `novaberg-klaerung_k.md`.
>
> **Nachgetragen am 05.08.2026 — der Knoten zählt jetzt auch.** Unmittelbar nachdem der Kopfblock gelesen ist, läuft die **Vorzeichenprüfung** (`graph/vorzeichen.py`, `SYK-B4` Stufe 1): Bei Urteil `abweichend` werden die Zahlenwerte der Nutzeräußerung gegen den erzeugten Text gehalten, und der Befund geht als `vorzeichenpruefung` ins `pipeline_log`. **Kein Modellaufruf, keine Verhaltensänderung** — der Knoten antwortet wie zuvor.
>
> Sie steht hier, weil hier zum ersten und einzigen Mal drei Dinge zusammen vorliegen: das Urteil, die Nutzeräußerung und Novas Text. Nachgelagert wäre sie nicht baubar, denn **das Urteil wird nirgends persistiert**.
>
> ⚠ **Der Zähler ist an diesem Korpus zu 85 % blind** — gemessen am Tag des Baus. Die strittigen Werte sind meist keine Ziffern („vierzig Jahren", „Hannover"). Er bleibt stehen, taugt aber nicht als Grundlage einer Rate; der Weg steht als `SYK-B4-STUFE-2-OHNE-FILTER` im Backlog.
>
> **Und die Wirkung des Kopfblocks ist gemessen: keine.** Zweiter Batterielauf, dieselben 25 Items — Kapitulationsrate 87 %, exakt wie ohne ihn. Der Knoten ist richtig gebaut; die Reihenfolge im Text ist kein Hebel gegen die Übernahme.

> **Nicht abgedeckt:** der Aufgabenpfad. Bei `task_context_cut` wird der Knoten übersprungen (§5.1), dort entsteht kein Urteil — und der HumanGraph hat ihn ohnehin nicht.

> **Der Kopfblock fällt aus, und eine hinreichende Ursache ist seit dem 22.08.2026 behoben.** Der Prompt verlangt `GEPRUEFT` und `STAERKE`; das Modell schreibt `GEPRÜFT` und `STÄRKE`. Ein Feldname außerhalb der erwarteten Menge ließ `_kopf_deuten` das **ganze** Urteil verwerfen — ein Umlaut kostete alle fünf Felder. `_feldname` normalisiert jetzt Umlaute und Kleinschreibung.
>
> **Ob das die Ursache der gemessenen Ausfälle war, ~~ist offen~~** — und der Grund gehört zum Befund: Der Logauszug war bei 120 Zeichen gekappt und endete im zweiten von fünf Feldern; gegen die fünf echten Ausfälle des Bestands gehalten blieben **0 von 5** lesbar, weil drei Felder im Auszug fehlen. Belegt ist eine Korrelation (4 von 5 trugen den Umlaut), nicht die Ursache. Der Auszug trägt jetzt 500 Zeichen. → **Für die Ausfälle danach beantwortet am 26.10.2026: Sie hatten eine zweite Ursache** — der Wert stand mit einer Erläuterung dahinter (Nachtrag unten); für die fünf davor bleibt es offen, weil ihr Auszug drei Felder nicht trägt.
>
> **Und die 54 % vom 13.08.2026 sind ohne Vergleichsgröße.** Der Zähllauf vom 22.08.2026 ergab 55 Ausfälle in 36 Stunden — **50 davon aus Suite-Läufen**, deren Zeugentexte im selben kumulativen Log stehen. Aus dem Betrieb stammen 5 Ausfälle und 1 gefälltes Urteil.

> **Nachgetragen am 26.10.2026 — die zweite Ursache ist behoben, und jeder Ausfall trägt seinen Grund.** Der Prompt formuliert die Zeile `EINWAND` als Frage, und das Modell schreibt die Erläuterung hinter den Wert (`nein — …`); `_kopf_deuten` verlangte den nackten Wert und verwarf das ganze Urteil. Am 28.08.2026 fiel der Kopfblock in 7 von 9 Turns aus, alle sieben mit `EINWAND: nein — …`; die Durchsicht vom 05.10.2026 nannte diese Ursache und zählte 47 Ausfallzeilen auf 74 erzeugte Antworten. Seither, in `graph/einwand.py`, der Prompt unverändert:
>
> - **Gelesen wird das erste Wort.** `EINWAND`, `BEWERTUNG` und `QUELLE` gelten, wenn ihr erstes Wort — nach führenden Satzzeichen, Gedankenstrichen und Anführungszeichen, ohne Groß- und Kleinschreibung — ein Wert der Menge ist; die Erläuterung dahinter wird verworfen (`_aufzaehlung_lesen`).
> - **Zwei Werte sind keine Wahl.** Nennt ein Feld mehr als einen verschiedenen Wert seiner Menge als ganzes Wort, gleich wo und mit welchem Trenner (`ja oder nein`, `ja / nein`, `fakt, haltung`, die Wertliste der Vorlage), fällt es als `mehrdeutig:<FELD>` aus. Derselbe Wert zweimal ist ein Wert, ein Wert einer anderen Menge zählt nicht, ein Wort, das einen Wert nur enthält, ist nicht der Wert.
> - **`STAERKE` nach derselben Regel, die Zahl selbst streng.** Gelesen wird eine führende Zahl in [0.0, 1.0], Komma oder Punkt; ein Exponent (`1e-1`) ist ein Ausfall, ein Minus wird nicht abgeschnitten (`_staerke_lesen`).
> - **Jeder Ausfall trägt seinen Grund.** Jeder Weg zu `geliefert=False` aus `urteil_lesen` setzt `Einwandsurteil.ausfall` auf einen Grund aus `AUSFALLGRUENDE` — `antwort_leer`, `trenner_fehlt`, `feld_fehlt`, `wert_ausserhalb`, `mehrdeutig`, `staerke_keine_zahl`, `staerke_ausserhalb`, `prosa_fehlt`; die Feldgründe tragen den Feldnamen hinter einem Doppelpunkt, gemeldet wird das erste unbrauchbare Feld in Prompt-Reihenfolge. Die Ausfallzeile des Verfassers nennt den Grund vor dem Auszug (*„kein lesbares Urteil im Kopfblock (Grund: …)“*), damit die Zeilen nach Ursache zählbar sind, ohne den Auszug zu lesen; die Zeile des Urteils trägt `Ausfall=`. Eine leere Antwort und fehlende Prosa nach dem Kopfblock meldet der Verfasser wie bisher mit eigener ERROR-Zeile.
> - **Was dieses Lesen nicht fasst (06.11.2026):** Mehrere Formen, die keine Wahl treffen, liest es als Wahl — `EINWAND-KOPFBLOCK-LIEST-KEINE-WAHL` ([`novaberg-bugs-antwortpfad.md`](novaberg-bugs-antwortpfad.md)), niedrig, offen.
>
> **Gemessen vor dem Commit** `[gemessen 26.10.2026]`, an den Auszügen der 22 Ausfallzeilen im Serverlog seit dem 21.10.2026: Der Code davor liest **0**, der Bau **21** (20 ohne, 1 mit Einwand) und weist 1 als `mehrdeutig:QUELLE` ab — das einzige Echo der Wertliste. In denselben 22 trägt kein `EINWAND` und kein `BEWERTUNG` einen zweiten Wert, keiner eine Auszeichnung mit Unterstrich oder Stern, keiner ein Feld mit Folgezeile. Zeugen in `server/tests/test_einwandsurteil.py` und `server/tests/test_verfasser.py`, Server-Suite `Ran 5563 tests` · `OK (expected failures=2)`; Code-Tree `3806695`, Kennung wird nachgetragen → committet als `a6e46c2`, die Doku dazu als `b87cc49`. **Im Betrieb nicht gemessen** — die Rate der Ausfallzeilen nach Grund gegen die beendeten Turns steht aus. `VERFASSER-KOPFBLOCK-FAELLT-AUS` ist geschlossen (`novaberg-bugs-archiv-antwortpfad.md`).
>
> **Grenzen, benannt** (Fundliste, 26.10.2026): Ein zweiter Wert mit Unterstrich-Auszeichnung (`ja oder _nein_`) wird als erster gelesen, weil der Unterstrich zum Wort gehört; ein Feld, das auf der Folgezeile weitergeht, wird als seine erste Zeile gelesen — der Leser geht zeilenweise, und die Vorlage des Prompts bricht `EINWAND` selbst um; bei einem doppelten Feld gewinnt still die letzte Zeile. Ein zweiter Wert als gewöhnliches Wort der Erläuterung (*„ja“* als Partikel, *„nicht abweichend“*, *„keine Haltung“*) macht das Feld laut zum Ausfall `mehrdeutig`; ein zweiter Wert in anderer Schreibweise (`trifft nicht zu`) zählt nicht, gelesen wird der erste.

---

## 5. Der Bauteil

> **Hinweis zur Aufteilung (19.09.2026):** Der Abschnitt ist der Bauteil mit `ZIEL` / `TEST` / `MESSUNG` und steht deshalb hier, mit seinen Festlegungen §5.1 bis §5.4. §5.2 und §5.3 sind am 31.07.2026 entschieden (Versionshistorie v0.2 in [`novaberg-node-verfasser_e.md`](novaberg-node-verfasser_e.md)).

| Zeile | Inhalt |
|---|---|
| **ZIEL** | Der Responder erzeugt keinen Inhalt mehr: Er erhält den fachlichen Inhalt fertig und gibt ihm Novas Form. |
| **TEST** | Der System-Prompt des Responders enthält weder `[GEDAECHTNIS]` noch `[WEB-RECHERCHE]`. Das Ergebnis des Verfassers liegt nach dem Lauf im State. Bei `task_context_cut=True` läuft der Verfasser nicht. |
| **MESSUNG** | Live-Turns über wissenschaftliche Themen: Zeit bis zum ersten Token vor und nach der Änderung, und ein Abgleich, ob die Endantwort Aussagen trägt, die im Verfasser-Ergebnis nicht standen. |
| **Gegenprobe** | Den State-Kanal aus `graph/state.py` entfernen: Der Schreibvorgang des Verfassers wird wirkungslos, der Responder bekommt einen leeren Inhalt — die Tests, die den Kanal prüfen, müssen rot werden. |

### 5.1 Der Kontext-Schnitt bleibt gültig

Bei `task_context_cut=True` sieht der Responder heute absichtlich fast nichts — kein Gedächtnis, kein Web, nur Identität, Stil und das Ergebnis der Aufgabe. Das war die Lösung nach vier Iterationen.

**Ein Verfasser, der in dieser Lage Gedächtnis und Web zusammenfasst, holt genau den Input zurück, der entfernt wurde** — nur einen Node früher und in verdichteter Form. Der Verfasser läuft in diesem Fall deshalb **nicht**; der Responder verarbeitet den `[AUFGABE]`-Block wie bisher.

### 5.2 Der Thinker bewertet weiterhin die Endantwort

Nach der Trennung gibt es zwei Texte. Der Thinker sitzt hinter dem Responder und bewertet **das, was Nova gesagt hat** — nicht das, was der Verfasser vorgelegt hat.

**Der Grund ist nicht Bequemlichkeit, sondern §2.3:** Das Verfasser-Ergebnis trägt die Fakten, aber nicht die vollständige Mitteilung. Wer den Inhalt allein bewertet, bewertet eine unfertige Nachricht — und übersähe genau den Teil, den die zweite Stufe beiträgt.

Der Thinker wird deshalb **nicht angefasst**.

### 5.3 Kein Rückfallpfad für den Verfasser

**Es wird kein Weg gebaut, auf dem der Responder in seine heutige Bauart zurückfällt.** Ein Rückfall wäre eine zweite, selten gelaufene Architektur im selben Graphen — und die Erfahrung mit selten gelaufenen Zweigen steht im Bestand.

Der zu erwartende Fehlerfall ist auch ein anderer: Der Verfasser wird kaum ausfallen, er wird **falsch liegen**. Gegen inhaltlichen Unsinn hilft kein Rückfallpfad, sondern nur die Messung am laufenden System.

**Was ein technischer Ausfall trotzdem nicht darf:** wie eine Antwort aussehen. Bleibt das Ergebnis leer, wird das laut gemeldet und der Turn scheitert sichtbar — er wird nicht mit einer Antwort überdeckt, die auf nichts steht. Das folgt aus der allgemeinen Regel gegen stille Fehler und ist keine eigene Entscheidung.

### 5.4 Der Kanalzwang

Das neue State-Feld muss in `graph/state.py` deklariert **und** in `graph/base.py` initialisiert werden. Ein Schreibvorgang in einen nicht deklarierten Kanal ist stillschweigend wirkungslos — die Belegstelle dafür liegt als eigene Lesson im Bestand.

---

## 7. Die Regeln sind zur Probe ausgesetzt (31.07.2026)

`[REGELN]` läuft nicht mehr — Antwortkürze, verbotene Floskeln, Butler-Prinzip, Tag-Unterdrückung, das Verbot falscher Erfolgsmeldungen.

**Der Grund ist nicht Aufräumen.** Jede dieser Regeln ist gegen ein Verhalten gewachsen, das der überladene Prompt hervorbrachte: Ein Modell, das gleichzeitig Wissen sichten, Inhalt bestimmen und Form finden soll, greift zu Floskeln. Seit der Trennung ist diese Ursache weg — ob die Narben noch gebraucht werden, ist damit eine offene Frage, und sie ist nur zu beantworten, indem man sie einmal weglässt.

**Belegt ist bereits, dass mindestens eine widersprach:** Die Regeln untersagten Rückfragen (*„Soll ich…?", „Möchtest du…?"*), während der Gesprächsvektor im selben Turn `Vehikel: Frage` und eine Landschaft mit *„Fragen: Mittel, neckisch, oft rhetorisch"* gewählt hatte. Ein pauschales Verbot schlug eine gemessene Vorgabe.

**Der Prompt-Baustein bleibt bestehen; nur der Aufruf entfällt.** Zurückgeholt wird die einzelne Zeile, die sich als nötig zeigt — nicht der Block.

> **Hinweis zur Aufteilung (19.09.2026):** Die beiden Absätze *„Erster Befund aus dem Betrieb“* (die Kürze fehlt) und *„Zweiter Befund, am Bestand gemessen am 15.09.2026“* (falsche Erfolgsmeldungen, 24 von 928 Antworten) standen hier; sie stehen in [`novaberg-node-verfasser_m.md`](novaberg-node-verfasser_m.md), *Aus §7*.
