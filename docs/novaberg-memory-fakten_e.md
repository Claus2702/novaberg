# Novaberg — Faktengedächtnis (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Fassungen, Befunde. Absicht und Kopfblock: [`novaberg-memory-fakten_k.md`](novaberg-memory-fakten_k.md) · Bauplan: [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) · Ausarbeitung und Messungen: keine (`_k`, Kopfblock). Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

**Stand:** 17. Oktober 2026, 15:40 UTC (`date -u`; angelegt).

---

## A. Entschieden

**Zwölf Antworten, alle am 17.10.2026, umschrieben.** Nr. 1 bis 4 gingen den Fragen voraus und setzen die Absicht. Nr. 5 bis 12 beantworten die Fragen, die eine Prüfung der Erstfassung dieses Konzepts gegen die bestehenden Konzepte aufgeworfen hat. Die Beispiele sind synthetisch.

| Nr. | Frage | Antwort | Steht in |
|---|---|---|---|
| 1 | Was wird aus dem vorhandenen Fakten-Plugin? | **Der Fakten-Manager wird der Fakten-Agent:** Das Plugin `FaktenManager` wird zum Agenten umgebaut. Das ist M2.5b | `_k` §3.2 |
| 2 | Ist die Voraussetzung *„nach dem Synapsen-Umbau“* erfüllt? | **Ja.** P1 bis P10 sind gebaut, der Rückbau des alten Langzeitgedächtnisses (P9) ist erledigt | `_k`, Kopfblock *Herkunft* |
| 3 | Was soll das Faktengedächtnis leisten? (Absicht) | **Die Sachlage klärt ihre Objekte und nimmt auf, was über sie bekannt ist**, aus dem Gespräch oder aus anderen Quellen. Weltwissen, Termine aus der Timeline und Fakten fließen in die Sachlage; was neu und dauerhaft ist, wird als Tripel abgelegt, und dann hat Nova etwas gelernt. Offene Punkte klärt Nova, damit sich die Entitäten bestimmen lassen | Scheibe 13 der Lage ([`novaberg-thinking-lage_k.md`](novaberg-thinking-lage_k.md)); [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3 |
| 4 | Wie wird gelesen? (Absicht) | **Über die ausgelagerten Lesewerkzeuge oder direkt über den Dienst, ohne den Router** | `_k` §5, Punkt 1; Scheibe 13 der Lage |
| 5 | Was trägt `verbindung`? | **Weiter nur die Gedächtnis-Achse Turn → KZG → LZG**, ohne neue Spalte. Fakten hängen über die Entität; zu ihr wird eine Mappe ihrer Fakten geholt. Die Verbindungen einer Entität insgesamt abzufragen, ist ein späterer Schritt | `_k` §3.1 |
| 6 | Wer speichert einen Fakt? | **Der Fakten-Agent**, wie der Timeline-Agent die Termine schreibt: Er ist die Fachabteilung, die weiß, wie man mit Fakten umgeht, hat Zugriff auf die Tabellen und kann Rückfragen veranlassen. Die Sachlage schreibt keine Fakten; das Speichern läuft über den Empfang | `_k` §3.2 |
| 7 | Wird auch ohne ausdrücklichen Auftrag gespeichert? | **Ja, über einer Grenze der Salienz.** Salienz und Themennähe entscheiden mit Novas Pflichtbewusstsein. Sagt die Salienz, das Thema ist wichtig, ruft Nova den Agenten öfter auf. Darunter entscheiden Pflichtbewusstsein und Nähe, ob sie vorschlägt oder fragt, etwas zu speichern. Aussagen über nahe Menschen sollen durch die emotionale Bindung eine hohe Salienz bekommen. Ob sie das heute tun, ist zu prüfen. Das deckt sich mit der Festlegung vom 18.05.2026 (*Router-getrieben mit Salienz-Fallback*) | `_k` §3.2; `_b` M1 |
| 8 | Gehören Fakten dem Paar oder dem Menschen? | **Dem Paar, auch das Weltwissen.** Das Gedächtnis gehört dem Paar, also auch die Fakten. Es ist Novas Gedächtnis, und was der Mensch ihr sagt, ist ihres | `_k` §2.1 |
| 9 | Woher kommt das Weltwissen? | **Aus dem Modell, sonst aus dem Internet.** Dass eine Stadt in ihrem Land liegt, sollte das Modell wissen; sonst wird recherchiert. Nova darf es lernen und speichern | `_k` §2.2 |
| 10 | Wie gehen Zeit, Ereignisse und Zeiträume in Fakten ein? | **Ein Monat wird keine Entität**, er bleibt für alle. Ein Termin im Monat ist ein Eintrag der Timeline. Eine Spanne über den ganzen Monat ist ein Termin mit Anfang und Ende und damit eine Referenz auf den Monat. Ein Ereignis mit unklarem Zeitraum, etwa ein Umzug *im November*, klärt die Sachlage. Ein privater Umzug dauert ein oder zwei Tage, fällt also vermutlich auf ein Wochenende; welches, ist zu klären | `_k` §2.3; [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3 |
| 11 | Was gilt, wenn ein neuer Fakt einem alten widerspricht? | **Das bestehende Schema des Ersetzens:** Der neuere Wert verdrängt den älteren, und die Historie bleibt nachvollziehbar. Nachgelesen ist es die bi-temporale Versionierung aus [`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md) §7: invalidieren und neu anlegen, ohne Rückfrage, Struktur statt Konfidenzwerte. Der Verfall der Kante ist davon unabhängig | `_k` §2.4 |
| 12 | Stößt die Mappe auch die Erinnerungen an? | **Ja, und sie reicht über die Kanten hinaus.** Zu einer Entität werden auch die Fakten ihrer Nachbarn mitgeladen. Zuerst war *bis zum dritten Grad* genannt. Noch am selben Tag ist der Ausgangswert festgelegt: **der zweite Grad in beide Richtungen**, über und unter der Entität. Die Tiefe ist zu messen, bevor sie fest wird | `_k` §3.1; `_b` M2 |

---

## B. Offen beim Meister

Keine.

---

## C. Offen in der Bauart — vor dem Bau zu entwerfen

Die Absicht ist entschieden (A). Diese fünf Fragen betreffen, **wie** sie gebaut wird, und sind vor dem ersten Bauteil zu entwerfen. Sie stehen gleichlautend in `_k` §5.

| Nr. | Frage | Anlass |
|---|---|---|
| C1 | **Zwei Lesewege der Timeline, und das Lesen ohne Router.** Wie entsteht das Fenster aus dem Objekt der Sachlage, und geht der Kalenderweg des Frame-Auflösers im gemeinsamen Leseweg auf? | Der Frame-Auflöser liest Kalenderzeilen über `TimelineRepository.find_by_keyword` (`graph/nodes/sachlage_resolver.py::_calendar_hits`). Der Turn liest hinter dem Router über `memory/timeline_reading.py::read_appointments` mit `graph/appointments.py::appointment_window`, das den Zustand des Routers liest. `range_window` und `search_window` nehmen eine Anfrage und keinen Zustand und taugen damit auch ohne Router `[Code, gelesen 17.10.2026]`. Ein Silo hat einen Dienst ([`novaberg-convention-nmcp.md`](novaberg-convention-nmcp.md) §6a.1); den Lesepfad nimmt die Konvention ausdrücklich von der Zustellung aus (§11). Entschieden: A, Nr. 4 |
| C2 | **Verfall der Kante gegen „kein Verfall“ im Eigenschaftsgedächtnis.** Werden Eigenschaft und Fakt zusammengelegt oder bleiben sie getrennt, und wie hält dann keiner dasselbe zweimal? | Die Kante eines Fakts verfällt ([`novaberg-convention-verfall.md`](novaberg-convention-verfall.md) §1.1). Eine Eigenschaft der Sachlage ist ein protokolliertes Faktum ohne Verfall ([`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md), Scheibe 11). Beide halten Objekt → Eigenschaft → Wert mit Ablösung. Das Frame-Konzept sieht Lager und Tripel als zwei Schichten ([`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md) §9.3) |
| C3 | **Drei Typsysteme.** Welches setzt ein *„ist ein“*-Fakt (F7)? | `entitaeten.typ` mit der Liste aus [`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md) §3, heute fast nur `sonstiges`; die Klasse eines Objekts der Sachlage nach dem Kanon der Frames; die freie Klasse aus *„ist ein“* |
| C4 | **Ein Ereignis einer dritten Person in der Timeline.** Welcher Typ, welche Verhaltensmerkmale? | Die Timeline kennt `termin`, `geburtstag`, `deadline`, `jahrestag`, `erinnerung` und den Erinnerungs-Anker ([`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §8), kein Ereignis, das einem anderen Menschen geschieht. A, Nr. 10 legt ein solches Ereignis in die Timeline |
| C5 | **Die gezielte Erinnerungssuche nach der Sachlage.** Wo läuft der Schritt, der mit der Mappe als Anker im Erinnerungsgedächtnis sucht? | Das Langzeitgedächtnis wird heute im Enricher gelesen, vor der Sachlage (`reducer → sachlage_node → router`, [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) Scheibe 1). Die Mappe gibt es erst danach. A, Nr. 12 |

**Zwei Messungen vor dem Festlegen**, mit Anordnung in `_b`: M1, die Salienz von Aussagen über nahe Menschen (A, Nr. 7), und M2, die Tiefe der Mappe (A, Nr. 12).

---

## D. Verworfene und überholte Fassungen

| Fassung | Wo | Warum nicht |
|---|---|---|
| *„Was im Gespräch neu und dauerhaft über eine Entität gesagt wird, legt sie [die Sachlage] als Fakt ab“* | Erstfassung, Absicht und §2.3 | Die Sachlage schreibt keine Fakten; geschrieben wird vom Fakten-Agenten über den Empfang (A, Nr. 6) |
| Der *November* als Objekt mit einer Mappe von Fakten; Bauteil *„Lage November → die Fakten zum November“* | Erstfassung, §2.1 und F2 | Ein Monat ist keine Entität. Er ist ein Zeitraum der Timeline (A, Nr. 10) |
| *„Lena zieht im November um“* als Fakt (synthetisch) | Erstfassung, §2.3 | Das ist ein Ereignis und gehört in die Timeline. Der Fakt ist das dauerhafte Ergebnis, *Lena lebt in Kassel*, und er gilt ab dem Ereignis (A, Nr. 10) |
| Die Grenze zwischen Weltwissen und Persönlichem als offene Frage *„je Paar oder je Mensch“* | Erstfassung, §5.7 | Beantwortet: je Paar, auch Weltwissen (A, Nr. 8) |
| *„Zustimmung vor dem Ablegen“* als offene Frage | Erstfassung, §5.2 | Beantwortet: über der Grenze der Salienz ohne Auftrag, darunter ein Angebot (A, Nr. 7) |
| *„Gilt die Regel der Klärung (nicht darauf bauen, nicht überschreiben, nachfragen)?“* bei einem Widerspruch | Erstfassung, §5.3 | Beantwortet: bi-temporal ablösen, ohne Rückfrage (A, Nr. 11). Die stillen Stufen der Klärung sind damit erfüllt (`_k` §2.4) |
| Ein Gewicht oder Verfall entscheidet, welcher von zwei Werten gilt | erwogen bei der Frage zu A, Nr. 11 | Das Schema wählt Struktur statt Konfidenzwerte. Der Verfall regelt die Stärke eines aktiven Fakts, nicht die Ablösung |
| Der Enricher als Ort, an dem die Akte zuerst geholt wird | [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2, *Sequenz* | Der Ort ist die Sachlage (A, Nr. 3); der zweite Schritt, die Akte als Anker der Erinnerung, bleibt (A, Nr. 12). Dort am 17.10.2026 markiert |
| Gegenprobe zu F3: *„Klärung aus → falsche Lena still gewählt“* | Erstfassung, §6 | Am Code ist es umgekehrt: Eine mehrdeutige Entität wird still übersprungen, nicht falsch gewählt (`agents/kzg/magnete.py`, `[Code, gelesen 17.10.2026]`). Die Gegenprobe in `_b` prüft deshalb das Ausbleiben von Bindung und Frage |

---

## E. Befunde

Gefunden beim Abgleich der Erstfassung gegen die bestehenden Konzepte am 17.10.2026. Was hier steht, ist nicht aufgelöst, wenn nicht anders vermerkt.

| | Stelle | Befund | Zustand |
|---|---|---|---|
| **B1** | Erstfassung §1, Punkt 4 | *„Seit dem Rückbau … (P9) entstehen Entitäten ohne Typ.“* Die Ursache ist nicht P9. Der Magnet-Pfad legt jede Entität seit P3 mit `sonstiges` an; die typisierende Extraktion endete mit P4 `[Code, gelesen 17.10.2026]` | **berichtigt** in `_k` §1, Punkt 4 |
| **B2** | Erstfassung §3, letzte Zeile | Die Entscheidungen zu den Klärfällen waren mit [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md) belegt, das sie zu diesem Zeitpunkt noch als offen führte. Am selben Tag nachgezogen; sie stehen dort in A (M0, M1, M3) | **berichtigt:** `_k` §3.2 verweist auf `novaberg-klaerung_e.md` A |
| **B3** | [`novaberg-memory.md`](novaberg-memory.md) §10.3 | Fakten *„nein, atemporal“* gegen die Verfallsregel vom 16.08.2026, nach der die Kante verfällt | **markiert** am 17.10.2026 |
| **B4** | [`novaberg-memory.md`](novaberg-memory.md) §13.2 | Der Enricher liest den Knowledge Graph als *Akte-Quelle*; das ist seit A, Nr. 3 die Sachlage | **markiert** am 17.10.2026 |
| **B5** | [`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md) §3 und §8 | Stand April 2026: Die Typenliste kennt `sonstiges` nicht, und der Enricher-Hook in §8 beschreibt einen Weg, der seit Langem abgeschaltet ist | offen |
| **B6** | [`novaberg-pattern-entity-resolution.md`](novaberg-pattern-entity-resolution.md) §5 | *„Die Entscheidung Referenz vs. Interface fällt in der Zwei-Call-Promotion (Call 1)“*. Call 1 entfiel mit P4; Eigennamen liefert heute die Salienz ([`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) §13.5) | offen |
| **B7** | Gemeinsamer Erzeuger der Mehrdeutigkeit | `EntityResolutionService` liefert bei zwei passenden Entitäten `braucht_klärung`, eine Rückfrage und die Kandidaten. Der Magnet-Pfad überspringt solche Fälle still, und die Bindung der Sachlage bindet dann nicht. Der Erzeuger steht, ein Leser fehlt `[Code, gelesen 17.10.2026]` | Bauteil F3 (`_b`) |
