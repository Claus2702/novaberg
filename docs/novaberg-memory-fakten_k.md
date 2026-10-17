# Novaberg — Faktengedächtnis: der Speicher dessen, was der Fall ist

**Absicht:** Nova hält je Paar fest, was über eine Entität der Fall ist, als Tripel zwischen zwei Entitäten oder zwischen einer Entität und einem Wert, mit Herkunft. Ein neuer Wert löst den alten bi-temporal ab, statt ihn zu überschreiben, und Zeit hängt nur an der Timeline. Zu einer Entität holt Nova die Mappe ihrer Fakten bis zum zweiten Grad in beide Richtungen. Schreiben darf allein die Fachabteilung, der Fakten-Agent.
**Stand:** 17. Oktober 2026, 17:05 UTC (`date -u`; §3.1 berichtigt: Die Leser von `fakten` sind gezählt, sechs statt vier). Davor 17. Oktober 2026, 15:40 UTC (`date -u`; umgebaut nach den Entscheidungen des Meisters vom 17.10.2026: Dieses Konzept beschreibt den Speicher. Hereinholen und Lernen in der Sachlage stehen als Scheibe 13 in [`novaberg-thinking-lage_k.md`](novaberg-thinking-lage_k.md), das Bestimmen einer Entität in [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3). Davor 17. Oktober 2026, 14:07 UTC (Erstfassung, nicht veröffentlicht)
**Umsetzung:** Featureliste §3.1 *Faktengedächtnis* mit ↳ *F1* bis *F7*, je ⚫ — der Zustand steht dort, nicht hier
**Teile:** `_t`: keiner (die Ausarbeitung entsteht mit der Bauart, §5) · [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) · [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) · `_m`: keiner (die beiden Messungen vor dem Bau stehen als Messpunkte in `_b`)
**Entschieden:** 12 · **Offen beim Meister:** 0 (Liste in [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md); offen sind Fragen der Bauart, §5)
**Herkunft:** der Ausblick in [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2: *„Das Faktengedächtnis-Konzept entsteht als eigenes Konzeptpapier, sobald der LZG-Kern dieses Konzepts steht.“* Der Kern steht seit dem 02.08.2026 (P1–P10). Am 17.10.2026 ist die Voraussetzung als erfüllt entschieden. Das Schema des Speichers stammt aus [`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md).

**§ → Datei.** Die Abschnitte §1 bis §5 stehen in dieser Datei. §6, die Bauteile mit `ZIEL` / `TEST` / `MESSUNG` und die zwei Messpunkte vor dem Bau, steht in [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md). Die Entscheidungen, die offenen Fragen der Bauart, die verworfenen Fassungen und die Befunde stehen in [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md).

| Abschnitt der Erstfassung (14:07 UTC) | heute |
|---|---|
| §1 Was ein Fakt ist | §1, berichtigt in Punkt 4 |
| §2 Die Sachlage als Umschlagplatz (2.1 Hinein, 2.2 Klären, 2.3 Heraus) | Scheibe 13 der Lage: [`novaberg-thinking-lage_k.md`](novaberg-thinking-lage_k.md), *Aus §4*, und [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) §4. Das Klären einer Entität steht in [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3. Hier bleibt §3.3 als Anschluss |
| §3 Was entschieden ist | `_e` A |
| §4 Was ausdrücklich nicht dazugehört | §4 |
| §5 Was offen ist | §5, nur noch was offen ist. Die beantworteten Fragen stehen in `_e` A |
| §6 Die Bauteile | `_b` §6 |

---

## 1. Was ein Fakt ist

**Ein Fakt ist ein Tripel:** Subjekt → Beziehung → Objekt. Das Subjekt ist eine Entität. Das Objekt ist eine Entität (eine *Referenz*, rückwärts suchbar) oder ein Wert (nur vorwärts). Das ist dieselbe Unterscheidung wie Typ 1 und Typ 2 in [`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md) §4; die Tabelle `fakten` erzwingt sie mit einer Prüfbedingung. Beispiele, synthetisch:

- *Kassel liegt in Deutschland.*
- *Lena lebt in Kassel.*
- *Lena hat einen Hund.*
- *Der Mensch hat Winterreifen* (Objekt ein Wert).

Was daraus folgt:

1. **Die Fakten bilden einen Graphen.** Das Objekt des einen Fakts ist das Subjekt des nächsten: Lena → Kassel → Deutschland. Ein Fakt ist eine **Kante zwischen zwei Entitäten**, und jede Entität hat wieder eigene Fakten. Die Substanz liegt in der Kante, umgekehrt als im Erinnerungsgedächtnis ([`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2).
2. **Wissen, das aus der Kette folgt, wird nicht gespeichert.** *Lena lebt in Deutschland* ergibt sich aus *Lena lebt in Kassel* und *Kassel liegt in Deutschland*. Es wird beim Lesen geschlossen. Ein berechneter Wert ist eine Funktion seiner Eingaben, kein abgelegter Zweitbestand ([`novaberg-convention-abgeleitete-werte.md`](novaberg-convention-abgeleitete-werte.md)).
3. **Weltwissen und Persönliches haben dieselbe Form und hängen ineinander.** Das Persönliche (*Lena*, der Mensch) hängt sich an das Weltwissen (*Kassel*, *Deutschland*). Beides steht im selben Graphen und gehört demselben Paar (§2.1).
4. **„ist ein …“ gibt der Entität ihren Typ:** Stadt, Land, Person, Tier. ~~Seit dem Rückbau des alten Langzeitgedächtnisses (P9) entstehen Entitäten ohne Typ.~~ → **Berichtigt am 17.10.2026:** Entitäten entstehen heute mit dem Typ `sonstiges`, und das liegt nicht an P9. Seit P3 legt der Magnet-Pfad des Kurzzeitgedächtnisses jede Entität so an `[Code, gelesen 17.10.2026: agents/kzg/magnete.py]`. Die Tripel-Extraktion der alten Promotion, die Typen vergab, endete mit P4. Die Fakten können den Typ zurückbringen. Welches der drei vorhandenen Typsysteme dann gilt, ist offen (§5, Punkt 3).
5. **Ein Fakt hat eine Herkunft und kann falsch sein.** *„Das Mittelmeer ist ein Ozean“* ist falsch, es ist ein Nebenmeer. Ein Fakt trägt, woher er stammt: vom Menschen, von Nova, aus dem Modell oder aus einer Recherche. Er lässt sich berichtigen (§2.4). Für Mensch und Nova gibt es die Unterscheidung schon, als Schreiber eines Eintrags ([`novaberg-convention-paar-schema.md`](novaberg-convention-paar-schema.md) §2) und als Sprecher einer Eigenschaft der Sachlage. Die Tabelle `fakten` trägt dafür heute keine Spalte. Eine neue Spalte ist eine Schemaänderung und wird vor dem Bau angekündigt.
6. **Nicht alles ist ein Fakt.** Was erlebt wurde, bleibt Erinnerung im Langzeitgedächtnis. Eine triviale Aussage erzeugt keinen Fakt, sondern eine Erinnerung mit Magneten. Mindestens eine Seite muss eine echte Welt-Referenz sein (*„Kann man es auf ein Namensschild schreiben?“*), und die Aussage muss Gewicht haben ([`novaberg-convention-magneten.md`](novaberg-convention-magneten.md) §7).

---

## 2. Was für jeden Fakt gilt

### 2.1 Fakten gehören dem Paar

**Entschieden am 17.10.2026:** Alle Fakten gehören dem Paar aus Mensch und Figur, auch das Weltwissen. Das Faktengedächtnis ist Novas Gedächtnis wie ihre Erinnerungen. Was sie selbst ablegt, ist ihres, und was der Mensch ihr sagt, auch. Jede Figur hat ihr eigenes Faktengedächtnis.

Das bestätigt die Trennung der Magneten-Konvention: Die Entitäten sind global je Mensch, alles daran Hängende gehört dem Paar ([`novaberg-convention-magneten.md`](novaberg-convention-magneten.md) §6, *„Welt geteilt, Erinnerungen perspektivisch“*). Dieselbe Entität *Kassel* kann in zwei Paaren verschiedene Fakten tragen. Das ist gewollt: Paare dürfen verschieden sein. Die Spalte `character_id` steht in `fakten`. Das Repository liest sie heute nicht (`FAKTEN-PAIR-IGNORED`); mit dem Fakten-Agenten wird sie gelesen.

### 2.2 Weltwissen kommt aus dem Modell und aus dem Internet

**Entschieden am 17.10.2026:** Weltwissen kommt aus dem Modell. Weiß das Modell es nicht, kommt es aus einer Recherche im Internet; die Sachlage hat dafür schon die Suche ihrer Scheibe 8 (*„Nachgeschlagen zu …“*). Nova darf Weltwissen als Fakt lernen und speichern, je Paar (§2.1), mit der Herkunft *Modell* oder *Recherche*.

Damit ist die Grenze zu Novas Bibliothek gezogen ([`novaberg-autonomous-wissen_k.md`](novaberg-autonomous-wissen_k.md)). Die Bibliothek hält erarbeitete Texte zu einem Thema, das Faktengedächtnis einzelne Aussagen über Entitäten.

### 2.3 Zeit steht nur in der Timeline

**Entschieden am 17.10.2026:**

- **Ein Monat ist keine Entität.** *November* ist ein Zeitraum für alle. Ihn liest die Timeline als benannten Zeitraum über den ganzen Monat ([`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) §4.2).
- **Ein Termin oder Ereignis im Monat ist ein Eintrag der Timeline.** Eine Spanne (*den ganzen November das Haus der Nachbarn hüten*, synthetisch) ist ein Termin mit Anfang und Ende und damit eine Referenz auf den Monat.
- **Ein Ereignis mit unklarem Zeitraum klärt die Sachlage** (*Lena zieht im November nach Kassel*, synthetisch). Aus dem Weltwissen bildet sie eine Annahme: Ein privater Umzug dauert ein bis zwei Tage, fällt also vermutlich auf ein Wochenende. Die Annahme bleibt eine offene Eigenschaft, bis sie geklärt ist, und Nova baut nicht darauf ([`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3).
- **Ein Fakt, der durch ein Ereignis entsteht, gilt ab dem Ereignis.** *Lena lebt in Kassel* beginnt mit dem Umzug. Sein Beginn ist die bi-temporale Gültigkeit und verweist auf den Eintrag der Timeline; der Fakt trägt den Monat nicht als Wert.

Der Grund ist die Regel *eine Achse, eine Quelle*. Zeit lebt in der Timeline, und kein anderer Speicher dupliziert Zeit-Logik ([`novaberg-convention-magneten.md`](novaberg-convention-magneten.md) §2.2, §8). Das Eigenschaftsgedächtnis der Sachlage hält es schon so: Eine Eigenschaft mit Tag oder Uhrzeit bekommt einen Verweis auf die Timeline, keinen Zeitwert ([`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md), Scheibe 11, *Der Zeitanker*). Die Timeline kennt heute kein Ereignis einer dritten Person (§5, Punkt 4).

### 2.4 Ablösen, nicht überschreiben

**Entschieden am 17.10.2026:** Es gilt das bestehende Schema, die bi-temporale Versionierung ([`novaberg-mem-knowledge-graph.md`](novaberg-mem-knowledge-graph.md) §7). Kommt zu Subjekt und Beziehung ein neuer Wert, wird der alte invalidiert (`t_invalid`, `aktiv = FALSE`) und der neue angelegt. Das geschieht ohne Rückfrage. Beide bleiben stehen:

- Die aktiven beantworten *„Wo lebt Lena?“*.
- Alle zusammen beantworten *„Wo hat Lena früher gelebt?“*.
- Derselbe Wert legt keine neue Zeile an.

Das Konzept wählt dabei **Struktur statt Konfidenzwerte**: Nicht ein Gewicht entscheidet, welcher Wert gilt, sondern die Gültigkeit. Das Eigenschaftsgedächtnis der Sachlage folgt seit dem 13.09.2026 demselben Schema.

**Zur Klärung:** Die Ablösung erfüllt die stillen Stufen der Klärung. Der alte Wert verschwindet nicht, und nichts wird stillschweigend überschrieben ([`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.1). Ob Nova bei einem Widerspruch nachfragt, entscheidet dort ihr Charakter; geschrieben wird ohne Rückfrage.

### 2.5 Der Verfall sitzt an der Kante

Die Verfallsregel gilt seit dem 16.08.2026 ([`novaberg-convention-verfall.md`](novaberg-convention-verfall.md) §1): Im Faktengedächtnis sitzt der Verfall dort, wo gesucht wird, an der Kante. Eine Entität, auf die anderswo verwiesen wird, verfällt nicht; die Bindung daran darf verfallen. Der Verfall ist von der Ablösung unabhängig: Er regelt die Stärke eines aktiven Fakts, nicht welcher Fakt gilt. `fakten` trägt heute keine Verfallsgröße (`FAKTEN-BINDUNG-OHNE-VERFALL`).

Das Eigenschaftsgedächtnis der Sachlage ist dagegen ein protokolliertes Faktum und verfällt nicht. Wie beides zusammengeht, ist offen (§5, Punkt 2).

---

## 3. Lesen und Schreiben

### 3.1 Die Mappe einer Entität

**Die Mappe einer Entität sind ihre Fakten.** Zu einer Entität holt Nova die Mappe über deren Kennung (`fakten.subjekt_id`, `fakten.objekt_id` → `entitaeten`), entschieden am 17.10.2026. Die Mappe enthält:

- **beide Richtungen:** die Fakten, in denen die Entität Subjekt ist, und die, in denen sie Objekt ist;
- **den zweiten Grad:** von jedem Nachbarn noch einmal seine Fakten, in beide Richtungen. Beispiel, synthetisch: Lena → ihr Hund → *der Hund kommt mit, wenn Lena zu Besuch kommt*. Der zweite Grad ist der Ausgangswert. Ob er reicht, wird gemessen, bevor er fest wird (§5, Punkt 7);
- **Referenz- und Wert-Fakten.** Ein Lesen, das nur Entität→Entität verbindet, ließe die Wert-Fakten aus (`GV-WERT-FAKTEN-BLIND`);
- **nur aktive Fakten, nur die des Paares, gekappt.** Die alte Anreicherung lud alle Entitäten des Menschen mit allen Fakten, ohne Kappung, und erzeugte damit das Rauschen, wegen dem sie abgeschaltet ist (`FAKTEN-RAUSCH`, `FAKTENPLUGIN-OHNE-KAPPUNG`).

**Ein Bestand, eine Lesefunktion.** ~~Heute lesen vier Stellen dieselbe Tabelle: die Anreicherung des Plugins, `fakten_abfragen`, `fakten_historie` und `_entity_kontext_laden` im Gesprächsvektor.~~ → **Heute lesen sechs Stellen dieselbe Tabelle** (berichtigt am 17.10.2026, gezählt gegen `7b65297` mit einem Grep über `server/` ohne Tests auf die Tabelle und auf `FaktenRepository`): im Plugin die Anreicherung (`enrich_entries`, abgeschaltet), `fakten_abfragen` (nur über `execute` erreichbar, das keinen Auftrag bekommt) und `fakten_historie` (ohne Aufrufer); `_entity_kontext_laden` im Gesprächsvektor (eigenes SQL, ohne Aufrufer); `api/gedaechtnis.py::fakten_abrufen` (eigenes SQL, ohne Paar) und die Wiedervorlage (`agents/wiedervorlage/agent.py`, `find_wiedervorlage_faellig`). Nicht mitgezählt sind das Lesen im Schreibweg (`fakten_verarbeiten` prüft mit `find_aktiv`, ob schon ein Wert steht) und das Wartungswerkzeug `tools/reembed_all.py`, das jede Zeile neu einbettet. Ein Silo hat einen Dienst; zwei Suchen über denselben Bestand ergeben zwei Rangfolgen ([`novaberg-convention-nmcp.md`](novaberg-convention-nmcp.md) §6a.1). Die Mappe wird deshalb einmal gebaut und von allen Lesern benutzt.

**Die Mappe stößt die Erinnerung an** (entschieden am 17.10.2026). Die Mappe einer Entität aus der Sachlage stößt eine gezielte Suche im Erinnerungsgedächtnis an, mit der Mappe als Anker. Das ist der zweite Schritt der Sequenz aus [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2. Dort war der Enricher der Ort; der Ort hat sich geändert (Scheibe 13 der Lage), der Gedanke nicht. Heute läuft die Erinnerungssuche vor der Sachlage (§5, Punkt 5).

**`verbindung` bleibt, was sie ist** (entschieden am 17.10.2026). Die Tabelle hält die Gedächtnis-Achse Turn → KZG → LZG und trägt keine Fakten, ohne neue Spalte. Fakten hängen über die Entität. Die Verbindungen einer Entität insgesamt abzufragen, also Erinnerungen, Termine und Fakten zusammen, ist ein späterer Schritt ([`novaberg-charakter-resonanz_t.md`](novaberg-charakter-resonanz_t.md) §4.2).

### 3.2 Wer schreibt

**Entschieden am 17.10.2026:** Ein Fakt wird nur vom **Fakten-Agenten** geschrieben, der Fachabteilung für Fakten, so wie der Timeline-Agent die Termine schreibt. Er bekommt den Auftrag über den Empfang, prüft ihn gegen seinen Bestand und hat Zugriff auf die Tabellen. Er kann Rückfragen veranlassen, über den Klärfall am Objekt der Sachlage ([`novaberg-klaerung_e.md`](novaberg-klaerung_e.md) A, M0). Er antwortet auf einem der vier Ausgänge, schreibt verifiziert und belegt sein Audit selbst ([`novaberg-convention-nmcp.md`](novaberg-convention-nmcp.md) §6, §8.4). Das Plugin `FaktenManager` wird zu diesem Agenten umgebaut (Backlog M2.5b).

**Die Sachlage schreibt keine Fakten.** Sie reichert an und klärt. Das Speichern beauftragt sie nicht selbst; es läuft über den Empfang, wie bei Terminen und Notizen.

**Auch ohne ausdrücklichen Auftrag** (entschieden am 17.10.2026):

- **Die Grenze ist die Salienz der Aussage**, zusammen mit ihrer Nähe zum Thema des Gesprächs.
- **Über der Grenze** ist das Thema wichtig. Nova stellt dem Fakten-Agenten zu, ohne dass der Mensch darum bittet, und je wichtiger, desto öfter.
- **Darunter** entscheiden Novas Pflichtbewusstsein und ihre Nähe zum Menschen, ob sie anbietet oder fragt (*„Soll ich mir das merken?“*). Das ist dasselbe Angebot wie bei Terminen und Notizen (Scheibe 12, Teil E). Wer mehr prüfen will, prüft mehr.
- **Vor dem Setzen der Grenze wird gemessen**, ob Aussagen über Menschen, die dem Menschen nahestehen, heute eine hohe Salienz bekommen (§5, Punkt 6). Sie sollen durch die emotionale Bindung als wichtig erkannt werden.

Das deckt sich mit der Entscheidung vom 18.05.2026: Der Fakten-Agent ist eine Fachabteilung wie die Timeline, *Router-getrieben mit Salienz-Fallback* ([`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md) G, K2).

### 3.3 Wo das Konzept an andere anschließt

| Anschluss | Wo es steht |
|---|---|
| Die Sachlage holt Fakten, Termine und Weltwissen herein und gibt Neues über den Empfang weiter | [`novaberg-thinking-lage_k.md`](novaberg-thinking-lage_k.md), *Aus §4*, Scheibe 13 |
| Ist ein Name mehrdeutig, klärt Nova, welche Entität gemeint ist | [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) §2.3 |
| Die Mappe als Anker der Erinnerung | [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2 |
| Die Termine selbst | [`novaberg-agent-timeline.md`](novaberg-agent-timeline.md) |

---

## 4. Was ausdrücklich nicht dazugehört

- **Keine neuen Spalten an `verbindung`** und keine Tripel-ID dort.
- **Kein gespeichertes abgeleitetes Wissen.** Was aus der Kette folgt, wird beim Lesen geschlossen (§1, Punkt 2).
- **Kein Ersatz für das Erinnerungsgedächtnis.** Das Langzeitgedächtnis bleibt episodisch: *was wurde erlebt*. Das Faktengedächtnis ist semantisch: *was ist der Fall* ([`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) §3.2).
- **Keine Zeit im Fakt.** Monat, Tag und Zeitraum stehen in der Timeline (§2.3).
- **Kein Schreiben durch die Sachlage**, den Enricher oder die Salienz. Geschrieben wird nur vom Fakten-Agenten (§3.2).
- **Keine Anweisung an die Figur als Fakt über den Menschen**, kein Rollenspiel und keine Metapher als Fakt. Abgelegt wird, was neu und dauerhaft ist. Die alte Extraktion legte beides ab (`FAK-LECK`, `FAKTEN-RAUSCH`, archiviert). Ob eine Aussage dauerhaft oder situativ ist (`FAK1`), beurteilt der Fakten-Agent gegen seinen Bestand.
- **Nicht in dieses Konzept:** die Termine selbst (Timeline), die Notizen und die Bibliothek. Sie bleiben eigene Speicher.

---

## 5. Was offen ist

Offen sind nur Fragen der Bauart und zwei Messungen. Die Absicht ist entschieden (`_e` A). Die Fragen stehen mit ihrem Anlass in `_e` B.

**Vor dem Bau zu entwerfen:**

1. **Zwei Lesewege der Timeline und das Lesen ohne Router.** Die Sachlage liest Kalenderzeilen schon selbst, über `TimelineRepository.find_by_keyword` im Frame-Auflöser (Scheibe 6). Der Turn liest Termine hinter dem Router, über `memory/timeline_reading.py::read_appointments` mit dem Fenster aus `graph/appointments.py`. Das sind zwei Wege über einen Bestand. Entschieden ist, dass die Sachlage über das ausgelagerte Lesewerkzeug liest, ohne den Router (`_e` A, Nr. 4). Offen ist, wie das Fenster aus dem Objekt der Sachlage entsteht und ob der Kalenderweg des Auflösers im gemeinsamen Leseweg aufgeht.
2. **Verfall der Kante gegen das Eigenschaftsgedächtnis.** Die Kante eines Fakts verfällt (§2.5), eine Eigenschaft der Sachlage nicht. Beide halten Objekt → Eigenschaft → Wert mit Ablösung, und das Eigenschaftsgedächtnis bindet sein Objekt später an eine Entität. Offen ist, ob Eigenschaft und Fakt zusammengelegt werden oder getrennt bleiben, und wie dann keiner dasselbe zweimal hält. Das Frame-Konzept sieht zwei Schichten vor, Lager und Tripel ([`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md) §9.3).
3. **Drei Typsysteme.** `entitaeten.typ` (eine geschlossene Liste, heute fast nur `sonstiges`), die Klasse eines Objekts der Sachlage (der Kanon der Frames) und die freie Klasse aus *„ist ein“* (Stadt, Planet). Offen ist, welches F7 setzt.
4. **Ein Ereignis einer dritten Person in der Timeline.** Die Timeline kennt die Typen `termin`, `geburtstag`, `deadline`, `jahrestag`, `erinnerung` und den Erinnerungs-Anker, aber kein Ereignis, das einem anderen Menschen geschieht (*Lenas Umzug*). Ein neuer Typ samt seinen Verhaltensmerkmalen ist eine Bauart-Frage.
5. **Die gezielte Erinnerungssuche nach der Sachlage.** Das Erinnerungsgedächtnis wird heute im Enricher gelesen, vor der Sachlage (`reducer → sachlage_node → router`). Die Mappe einer Entität der Sachlage gibt es erst danach. Für die Suche mit der Mappe als Anker braucht es einen Schritt hinter der Sachlage.

**Vor dem Festlegen zu messen** (Messpunkte in `_b`):

6. **Die Salienz von Aussagen über nahe Menschen.** Bekommen Aussagen über Menschen, die dem Menschen nahestehen (Familie, enge Bindung), heute eine hohe Salienz? Gemessen an der bestehenden Salienz, bevor die Grenze aus §3.2 gesetzt wird.
7. **Die Tiefe der Mappe.** Reicht der zweite Grad, und was kostet er im Prompt?

---

## 6. Die Bauteile

Sie stehen mit `ZIEL`, `TEST`, `MESSUNG` und Gegenprobe in [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6. Jedes ist eine Zeile der Featureliste mit ⚫:

- **F1** — die Mappe lesen
- **F2** — der Fakten-Agent
- **F3** — Entitäten klären
- **F4** — lernen ohne Auftrag
- **F5** — ablösen statt überschreiben
- **F6** — Zeit über die Timeline
- **F7** — typisieren

Dazu zwei Messpunkte vor dem Bau: **M1**, die Salienz bei nahen Menschen, und **M2**, die Tiefe der Mappe.
