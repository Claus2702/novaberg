# Novaberg — Charakter-Resonanz (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen.** Absicht und Kopfblock: [`novaberg-charakter-resonanz_k.md`](novaberg-charakter-resonanz_k.md) · Ausarbeitung: [`novaberg-charakter-resonanz_t.md`](novaberg-charakter-resonanz_t.md) · Bauplan und Umstellung: [`novaberg-charakter-resonanz_b.md`](novaberg-charakter-resonanz_b.md) · Messungen: [`novaberg-charakter-resonanz_m.md`](novaberg-charakter-resonanz_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier stehen Verweis, Wortlaut und Datum. Sie tragen Buchstaben, weil E1 bis E8 in diesem Konzept die Zeilen der Tabelle in §14 sind.

| | Stelle | Gegenstand und Wortlaut | Datum |
|---|---|---|---|
| **a** | §14 unten, Zeile **E8** | Ein thematisch *verstärkter* Nachbar-Key bekommt keine `verbindung`-Zeile: *„Nur **erzeugte** Einträge. Keine `art`-Spalte, keine zweite Tabelle für Verstärkungen.“* Begründung wörtlich in der Zeile: `verbindung` ist *„das Nachschlagen im Tagebuch, wo alle Einträge hinterlegt sind“*. Daraus die vier Folgeeigenschaften unter der Tabelle | 26.07.2026 |
| **b** | `_t` §5, Absatz *„Vorgesehener Schreibort (Entwurf …, unter Audit-Vorbehalt)“* | Die `verbindung`-Zeile entsteht im Dispatcher, dort wo der Rohturn geschrieben wird: *„Ein Schreibpunkt statt zwei.“* Der Audit-Vorbehalt ist aufgelöst (`_b` §7, A1 und A2 in `_b` §15) | Juli 2026 — der Absatz nennt eine Sitzung, kein Datum |

Beide nennen den Urheber im Text.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §10 und §12: Das Subjekt sitzt in `beobachter`, nicht im gedrehten Paar — *„Variante A“*.
- `_t` §12, *Warum zwei Tabellen*: `verbindung` und `verhaltens_beleg` getrennt.
- §14 unten: *„Kein Fremdschlüssel von `verbindung.turn_id` auf die `turn_roh`-Zeile“*; dazu die vier Folgeeigenschaften aus E8.
- §6 unten, *Verhaltensweisen-Zusammenführung*: *„Variante B (Belegzahl = Gewicht) gewählt.“*
- `_t` §4.1: die Retention als Umkehrung statt als Positiv-Liste — *„Bewusst“*.

---

## B. Offen beim Meister

§14 unten führt fünf offene Entscheidungen mit einer Empfehlung, aber ohne Beschluss:

- **E1** — `verbindung`-Zeilen, deren KZG-Eintrag ohne Promotion stirbt. Empfehlung: behalten.
- **E4** — `beleg_zahl` als Spalte oder aus `COUNT(verhaltens_beleg)` gerechnet. Empfehlung: Spalte.
- **E5** — Ähnlichkeit beim Zusammenführen, themen- oder embedding-basiert. Empfehlung: pgvector-KNN. Dieselbe Frage führt §6 als offenen Designpunkt.
- **E6** — Backfill der vorhandenen Rohturns. Hängt an Audit A3 (`_b` §15, `_m` §15).
- **E7** — ob das LZG-Gate das richtige Gate für Novas Charakter ist: *„Nicht beantwortbar, solange die Skala gebrochen ist“*; vor Bauteil 3 zu entscheiden.

E8 in derselben Tabelle ist entschieden (Abschnitt A).

## 14. Offene Entscheidungen

| ID | Frage | Empfehlung |
|---|---|---|
| **E1** | `verbindung`-Zeilen, deren KZG stirbt ohne Promotion? | **Behalten** mit `lzg_id = NULL`. Harmlos: Der Lesepfad filtert auf `lzg_id IS NOT NULL` **und** joint auf `lzg_knoten.aktiv = TRUE` (§11) — verwaiste Zeilen sind deshalb doppelt unschädlich. Späterer Aufräumlauf möglich. |
| **E4** | `beleg_zahl` denormalisiert oder aus `COUNT(verhaltens_beleg)` gerechnet? | **Spalte** — billig, und jeder Charakter-Lauf braucht das Gewicht. |
| **E5** | Ähnlichkeit beim Zusammenführen: themen- oder embedding-basiert? | **pgvector-KNN** (wie `lzg_knoten` / `anker_retrieval`). Verhaltensweisen leben in Postgres. Die themen-basierte KZG-Verstärkung bleibt davon unberührt. |
| **E6** | **Backfill** der 150 vorhandenen Rohturns (Stand 25.07.2026, davon 111 verwertbar)? | Hängt an Audit A3. Wenn nicht rekonstruierbar: Charakter beginnt beim ersten Turn nach Deployment. |
| **E7** | **Ist das LZG-Gate das richtige Gate für Novas Charakter?** Die Promotion bewertet nach Fakten-Salienz *über Meister*. Ein Turn, in dem Nova viel über sich verrät, aber faktisch banal ist, wird nie promotet — sein Verhaltensbeleg geht verloren. | **Offen — und die Frage steht auf dem Kopf (Chat 109).** E7 unterstellt, das Gate filtere *zu eng*. Gemessen filtert es praktisch **gar nicht**: 527 von 775 KZG-Einträgen liegen **über 1.0**, während die Skala laut `novaberg-node-salience.md:15/:80` bei 1.0 endet; nur 7 von 775 liegen unter 0.5. `MINIMUM` 0.3, `MID` 0.5, `HIGH` 0.7 und Promotion 0.8 sind für zwei Drittel des Korpus wirkungslos — live bestätigt durch **null Ablehnungen in sieben Läufen**. Ursache: `KZG-SALIENZ-SKALENBRUCH` (backlog.md, Chat 109). **Nicht beantwortbar, solange die Skala gebrochen ist:** Wie das Gate bei intakter Skala filtern würde, ist unbekannt. Die Frage muss vor der Entscheidung **neu gestellt** werden. Die alten Optionen bleiben stehen: (a) Akzeptieren, irgendein Filter muss sein. (b) Eigenes Gate für Verhaltensbelege (z. B. emotionales Delta statt Fakten-Salienz). **Hängt an Sprint `KZG-SALIENZ-NEUBAU`; vor Bauteil 3 zu entscheiden.** |
| **E8** | **Bekommt ein thematisch *verstärkter* Nachbar-Key eine `verbindung`-Zeile?** | **Nein — entschieden Chat 109 (Meister).** Nur **erzeugte** Einträge. Keine `art`-Spalte, keine zweite Tabelle für Verstärkungen. *Begründung:* `verbindung` ist ein **Nachschlagewerk außerhalb des kognitiven Gedächtnisses** — „das Nachschlagen im Tagebuch, wo alle Einträge hinterlegt sind", kein Äquivalent zu einer Hirnfunktion. Der Text eines verstärkten Nachbarn stammt aus einem **anderen** Turn; nur sein *Gewicht* kommt aus diesem. Ihn hier zu verdrahten hieße, einen Eintrag unter ein **falsches Datum** zu schreiben. Ein Tagebuch mit falschen Daten ist als harte Rückfallebene wertlos. Assoziationen — „was hängt mit diesem Eintrag zusammen" — kommen nicht aus eingefrorener Verdrahtung, sondern **live aus dem synaptischen Speicher**. |

**Was E8 dauerhaft unbeantwortbar macht — ausdrücklich festgehalten.** Die Frage „welche Turns haben diesen Eintrag schwer gemacht" ist damit dauerhaft unbeantwortbar. Die Verstärkung hinterlässt in Redis nur die neue Zahl, keine Historie. Der synaptische Speicher beantwortet diese Frage **nicht** — er beantwortet eine andere. (Wörtlich aufgenommen, damit später niemand die Gewichtsherkunft im Graphen sucht.)

**Vier Folgeeigenschaften von `verbindung`** *(aus E8, entschieden Chat 109)* — Eigenschaften der Tabelle, keine eigenen Entscheidungspunkte:

- **KEIN Gewicht, KEIN Decay, KEINE Salienz.** Ein Tagebucheintrag verblasst nicht und wird nicht wichtiger. Alles, was nach Bewertung aussieht, gehört in eine andere Tabelle.
- **VOLLSTÄNDIGKEIT VOR SPARSAMKEIT.** Kein Schwellwert entscheidet, ob eine Zeile geschrieben wird. Entsteht ein KZG-Eintrag, entsteht die Zeile. Ein Nachschlagewerk mit unbekannten Lücken ist keines.
- **EINE Zugriffsart:** „Turns zu diesem Eintrag" und die Gegenrichtung. Kein Ranking, keine Ähnlichkeit, kein Embedding. Index auf beide Spalten.
- **`turn_id` NOT NULL.** Begründung und Blocker bei Bauteil 1b (§16).

**Kein Fremdschlüssel von `verbindung.turn_id` auf die `turn_roh`-Zeile** *(entschieden Chat 109)*. Pfad 1 schreibt seine KZG-Einträge, **bevor** die `turn_roh`-Zeile existiert — die schreibt erst Pfad 2. Ein FK würde jeden Pfad-1-Write brechen. `turn_id` bleibt eine nackte Spalte.

---

## C. Offen ohne Frage

§6 unten führt die offenen Fragen und Abhängigkeiten, *„zu verifizieren, nicht beschlossen“*. Dazu führen andere Abschnitte offene Punkte:

- `_m` §15, *A3-Teilbefund*: ob die Forensikzeilen zu den verwertbaren Turns noch existieren, ist ungemessen — A3 bleibt offen.
- `_m` §9: der Rückgang der KZG-Keys an einem Tag ohne Gespräch — *„Offene Frage.“* Dasselbe in `_t` §8 (Glossar, *KZG-Eintrag*).
- `_b` §16, Bauteil 1b: `PIXIE-TURN-ID-LEER` besteht weiter; der Fix gehört vor Bauteil 3.
- `_b` §16, Bauteil 3: der Name `TURN_ROH_STICHTAG_UTC` ist bis zum Bau ein Vorschlag.

## 6. Offene Fragen & Abhängigkeiten (zu verifizieren, nicht beschlossen)

**turn_id-Kupplungen — ✅ Chat-103-Audit bestätigt (nicht mehr offen):**
- `turn_id` am KZG-Schreib- und Boost-Punkt verfügbar (`dispatch → speicher → kzg_store`) — **auditiert Chat 103**. Achtung: Das belegt die *Verfügbarkeit*, nicht dass dort geschrieben werden *soll* (→ §5, Schreibort neu entworfen).
- KZG-ID (Redis-Key) stabil bei Verstärkung.
- Promotion kennt Herkunft (`kzg_quell_key` UNIQUE) → `lzg_id` nachtragbar, 1:1.

**Themen- vs. Embedding-Ähnlichkeit (offener Designpunkt):** Die heutige KZG-Verstärkung läuft **themen-basiert** (Mengen-Schnitt), nicht embedding-basiert. `kzg_similar_find` (Embedding-KNN) existiert, hat aber **keinen Aufrufer** (brachliegend). Für die `verbindung`-Zeile irrelevant (entsteht am Boost-Punkt unabhängig vom Auslöser). Für die **Verhaltensweisen-Zusammenführung** (Variante B) ist zu entscheiden: themen-basiert wie der Rest, das brachliegende `kzg_similar_find` aktivieren, oder auf der pgvector-Seite (`lzg_knoten`-Muster) ansetzen. Infrastruktur für alle drei vorhanden.

**Retention — ✅ implementiert Chat 104 (siehe §4.1):** Turn-Rohdaten dauerhaft (Jahre), Forensik-Arten verfallen weiter, `delete_expired_entries` schützt `art='turn_roh'`.

**Verhaltensweisen-Zusammenführung:** Variante B (Belegzahl = Gewicht) gewählt. Offen: Ähnlichkeits-Schwellwert; ob eine Verhaltensweise selbst decayt; und der Themen-vs-Embedding-Designpunkt (oben).

**Verhältnis zu bestehenden Dokumenten:**
- Saatgut (`agent-character.md`): explizite Anweisungen bleiben Modulation *über* dem destillierten Charakter. Dieses Konzept betrifft die destillierte Basis, nicht das Saatgut.
- Hash-Mechanik (`pixie-character-hash.md`): wird nach Fertigstellung dieses Moduls komplett überarbeitet.

**Sprint-Größe:** Mehrteilig, über mehrere Sessions — zwei neue Tabellen, Eingriff in KZG-Ähnlichkeits-Schreibpfad, Promotion-Nachtrag (`lzg_id`), Verhaltensweisen-Destillator mit Embedding-Dedup, umgebauter CharakterAgent-Lesepfad, Retention-Differenzierung.

---

## D. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_m` §2 — die Wurzel *„nirgends dauerhaft gespeichert“* und der Schluss *„die Quelle fehlt“*: widerlegt zweimal, durch den gebauten Rohturn und durch die Messung, dass der Verdichter die Stimme überschreibt.
- `_m` §2.1 — *„Der Prompt ist korrekt, die Eingabe ist es nicht“*: widerlegt; die Ursache ist der Verdichter, nicht das Material (`DESTILLAT-SUBJEKT-SCHABLONE`).
- `_k` §3 und `_t` §5 — die Graph-Reihenfolge, nach der der Reducer nach dem Responder schreibt: falsch; Schreibpunkt ist der Dispatcher.
- `_t` §5 — der Schreibort der `verbindung`-Zeile am KZG-Boost-Punkt: überholt durch den Dispatcher (Entscheidung b).
- `_t` §4.2 und §12 — die Beleg-Achse in `verbindung`: herausgelöst in `verhaltens_beleg`.
- `_t` §10, §12 und `_m` §A5-Befund — die gedrehte Partition als Subjekt: verworfen, weil sie nirgends existiert; das Subjekt trägt `beobachter`.
- `_t` §11, Schritt (2) — die Begründung *„und werden bei der Promotion konsumiert“*: widerlegt (`PROMOTION-ENTFERNT-KZG-NICHT`); die Regel bleibt.
- `_t` §13 — der assoziative Pfad für die Charakter-Destillation: verworfen, *„ein Schnappschuss der Tagesstimmung, kein Wesen“*; er bleibt für Novas Selbstreflexion.
- `_b` §16 — `PIXIE-TURN-ID-LEER` als Blocker für Bauteil 1b: *„war keiner“*.
- §14 unten, E7 — die Frage, ob das Gate zu eng filtert: *„die Frage steht auf dem Kopf“*.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Eigentümer prüfen — das ist ein eigener Schritt. Die Befunde tragen ein S wie in den anderen Konzepten dieser Gruppe. S1 bis S7 stammen aus der Sichtung, S8 und S9 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **S1** | Abschnitt F, bisheriger Kopf, Feld **Stand** | Der Kopf trägt den 26.07.2026; der Text trägt spätere Änderungen (die Korrektur zur Kopfzeile, der Nachtrag *„gebaut anders gelöst“* in `_b` §16, die Herkunftsvermerke vom 19.09.2026). Eine Versionshistorie gibt es nicht | `[gelesen 19.09.2026]` |
| **S2** | `_m` §2, §2.1, §9; `_b` §7; §14 unten (E6); `_b` §15 (A3) | *„150 Rohturns, Stand 25.07.2026, davon 111 verwertbar“*; nach `novaberg-metakognition_k.md` §2.5 ist dieser Bestand nicht mehr vorhanden — hier nicht nachgezogen | `[gelesen 19.09.2026]` |
| **S3** | `_m` §2, §2.1, §9 | *„das einzige `FROM pipeline_log` im ganzen Server ist das `DELETE` der Retention“*; nach `novaberg-metakognition_k.md` überholt | `[gelesen 19.09.2026]` |
| **S4** | `_t` §12 | Die Tabelle `verhaltensweisen` steht nur als Entwurf; die Featureliste (*Bauteil 3*) sagt *„Tabelle existiert nicht“*. Der Entwurf sagt das nicht | `[gelesen 19.09.2026]` |
| **S5** | `_m` §2, §2.1, §9; §14 unten; `_b` §16 | Verweise auf `backlog.md` und `bugs.md` in der alten Struktur; `novaberg-backlog.md` trägt keine Einträge mehr, und abgeschlossene Bugs stehen im Archiv | `[gelesen 19.09.2026]` |
| **S6** | Abschnitt F, bisheriger Kopf (*Abgrenzung*); §6 unten | `novaberg-pixie-character-hash.md` *„wird nach Fertigstellung dieses Moduls komplett überarbeitet“* — Bauteil 5, laut Featureliste nicht begonnen | `[gelesen 19.09.2026]` |
| **S7** | ganzes Konzept | Viele durchgestrichene Absätze stehen neben ihren Korrekturen; wer nur liest, was nicht gestrichen ist, muss die Korrekturkette selbst verfolgen | `[gelesen 19.09.2026]` |
| **S8** | `_b` §7, *Fehlt* | Führt die Tabelle `verbindung` und den `lzg_id`-Nachtrag bei der Promotion als fehlend; `_t` §11, Schritt (2) sagt *„✅ Gebaut und live gemessen“*, `_b` §16 führt Bauteil 1b als *„GEBAUT UND LIVE GEMESSEN“* | `[gelesen 19.09.2026]` |
| **S9** | `_b` §16, Bauteil 4; `_t` §5, *Lesen* | Der Lesepfad soll Verhaltensweisen lesen und den alten Pfad ersetzen; die Featureliste (*Bauteil 4*, 🟠) sagt, der CharakterAgent liest `verbindung` *„anders als geplant“* — Turn-Wortlaut statt destillierter Verhaltensweisen. Weder §7 noch §16 nennen diesen Lesepfad | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier. Sein Herkunftsvermerk und seine Regel für Zahlen gelten für alle fünf Teile.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Charakter-Resonanz — woraus Novas Charakter entsteht
**Stand:** 26. Juli 2026, Chat 109 (Audits A1/A2/A5 geschlossen; Schreib-Kardinalität gemessen; E8 entschieden; Bauteil 1a gebaut und live abgenommen — ~~Bauteil 1b blockiert durch `PIXIE-TURN-ID-LEER`~~; Verbindungstabelle/Verdichten/Lesen weiterhin offen; Ursache aus §2/§2.1 korrigiert: die Quelle trägt Novas Stimme, der Verdichter überschreibt sie)

> **Korrektur Chat 112 zur Kopfzeile:** `PIXIE-TURN-ID-LEER` **sperrt 1b nicht** — das steht seit Chat 110 im Dokument selbst (§16, „war keiner"), nur nicht hier oben. Der Schreibpfad prüft die `turn_id` vor dem Insert und überspringt den Lauf mit einer Warnung, die die Zahl der übersprungenen Keys nennt. Der Defekt besteht weiter und gehört vor **Bauteil 3**, nicht vor 1b. Ein Widerspruch zwischen Kopfzeile und Abschnitt trifft immer den, der nur oben liest.
**Herkunftsvermerk:** Jede Aussage mit Funktionsname, State-Key, Spalte oder Aufrufreihenfolge trägt *auditiert (Chat N)*, *Annahme* oder *überholt (Chat N)*. Ohne Vermerk = Annahme.
**Zahlen:** Zeitstempel und Stichtage stehen ohne Vorbehalt im Dokument — sie bleiben wahr. Zählungen tragen ihr Messdatum („150 Rohturns, Stand 25.07.2026"), denn sie sind am Tag danach falsch.
**Pfad:** novaberg/docs/novaberg-charakter-resonanz_k.md
**Abgrenzung:**
- Saatgut / explizite Anweisungen → `novaberg-agent-character.md`
- Hash-Destillations-Mechanik (fünf Profile, Loader, Trigger) → `novaberg-pixie-character-hash.md` (wird nach Fertigstellung dieses Moduls komplett überarbeitet)
- Dual-Emotion (external/internal) → `novaberg-ei-dual-emotion_k.md`
