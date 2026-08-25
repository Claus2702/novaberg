# Novaberg — Backlog (Zukunftskonzepte)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Backlog — Konzipierte, noch nicht implementierte Features
**Stand:** 25. August 2026, 10:05 UTC (`FAKTEN-IN-KERN` als erledigt festgestellt; zwei Zeilenangaben nachgezogen, die Befunde selbst stehen). Davor: 24. August 2026, 13:35 UTC (der Matrix-Epic loest seine Abschaltbedingung ein — Telegram ist aus). Davor: 23. August 2026, 21:55 UTC (zwei Stellen zum Fehlversuchspfad markiert — er legt seit heute still statt zu loeschen; die Auswahl nach hoher Salienz bleibt)
**Verlauf:** [Verlauf des Standes](#verlauf-des-standes) — 38 Eintraege, juengster zuerst
**Pfad:** novaberg/docs/novaberg-backlog.md
**Quellen:** nova-08-k.md (Kognitive Anreicherung), nova-10-k-backlog.md (Skill-System), nova-01-t-c-backlog.md (Node-Konfiguration)

---

| Gegenstand | Datei | Eintraege |
|---|---|---|
| Gedaechtnis | [`novaberg-backlog-gedaechtnis.md`](novaberg-backlog-gedaechtnis.md) | 76 |
| Hintergrund | [`novaberg-backlog-hintergrund.md`](novaberg-backlog-hintergrund.md) | 66 |
| Charakter | [`novaberg-backlog-charakter.md`](novaberg-backlog-charakter.md) | 66 |
| Antwortpfad | [`novaberg-backlog-antwortpfad.md`](novaberg-backlog-antwortpfad.md) | 46 |
| Wissen | [`novaberg-backlog-wissen.md`](novaberg-backlog-wissen.md) | 71 |
| Bauart | [`novaberg-backlog-bauart.md`](novaberg-backlog-bauart.md) | 96 |

### Die Frage, in drei zerlegt

**Ist es unterscheidbar?** Erzeugt der Apparat eine sichtbare Wirkung, oder wäre das nackte Modell nicht zu trennen?

**Ist es ein Charakter?** Nicht dasselbe. Ein Charakter ist nicht „anders als das Basismodell", sondern über die Zeit derselbe und unter Störung stabil.

**Ist es kausal?** Ändert sich das Verhalten, wenn sich der Charakter ändert — in die vorhergesagte Richtung?


### Der Aufbau

**Mehrere Test-Nutzer gegen dieselbe Nova**, jeder mit einer eigenen Gesprächsart. Das Paar-Schema trägt das bereits: `charakter_hash`, KZG und LZG liegen je Paar. Damit wird die Frage schärfer und besser messbar:

> **Entwickelt Nova je Beziehung einen anderen Charakter?**

Konvergieren alle Räder auf dasselbe Profil, liest der Apparat das **Modell** und nicht die Beziehung. Divergieren sie in die Richtung, die die Gesprächsart vorgibt, ist Charakterbildung belegt.

**Der nackte Vergleich ist dabei geschenkt:** Ein frisches Paar ist in seinen ersten Turns das nackte Modell — leere Profile, Rad auf der Nabe. Turn 1 gegen Turn 100 desselben Paares ist die Ablation, ohne Gabelung und ohne das Risiko, dass ein Ablationspfad dem Produktivpfad nicht entspricht.

**Der Kontrollarm gehört dazu:** Zwei Nutzer mit **identischem** Gesprächsskript. Divergieren die, misst die Reihe Rauschen.


#### Zwei der vier Maße sind erhoben — 06.08.2026

Die Reihe lief am 02./03.08. über sechs Bögen; ausgewertet wurden damals die Sonden, der Emotionsstrang, die Räder und die Cluster. **Die beiden Maße, die die Titelfrage beantworten, blieben liegen** und sind jetzt aus demselben Material erhoben, ohne neuen Bogen.

**Profilähnlichkeit** — paarweise Kosinus-Distanz der Profiltexte, Embedding `nomic-embed-text-v2-moe`, Geräteprobe vorweg (gleicher Inhalt in anderen Worten 0.806, fremdes Thema 0.077):

| Gegenstand | Median | Spanne |
|---|---|---|
| Novas sechs Selbstprofile (`beziehungsprofil`) | **0.817** | 0.714–0.896 |
| Die sechs Menschen (`beziehungsprofil`) | 0.774 | 0.740–0.834 |
| Dieselben Menschen (`adaptive_hash`, Themen) | **0.548** | 0.448–0.642 |

Sechs Menschen, die nichts miteinander zu tun haben, liegen in ihrer Beziehungsprosa bei 0.774 und in ihren Themen bei 0.548. **Wo die Destillation Haltung in Prosa fasst, zieht sie alles ins selbe Register; wo sie Inhalt auflistet, bleibt der Unterschied stehen.** Novas Profile liegen enger als die der Menschen, fallen aber nicht zusammen — ihre Spanne ist beim Beziehungsprofil sogar breiter.

**Trennschärfe, blind** — ein Urteiler bekommt ein Profil und zwei unbeschriftete Antworten desselben Turn-Index und ordnet zu; Zufall ist 50 %. 270 Urteile, Geräteprobe 4 von 4:

| Arm | n | Quote | ~~p (exakt, zweiseitig)~~ | A-Wahl |
|---|---|---|---|---|
| `beziehung` (Beziehungsprofil) | 88 | **64,8 %** | ~~0,007~~ | 44,3 % |
| `thema` (Themenliste, Störgröße) | 88 | 63,6 % | ~~0,014~~ | 53,4 % |
| `zufall` (Profil einer Unbeteiligten) | 87 | 47,1 % | ~~0,67~~ | 51,7 % |

> **Die p-Werte sind überholt, 07.08.2026 — die Quoten nicht.** Der Test zählt jedes Urteil als eigenen Fall. Das sind sie nicht: Alle Urteile einer Persona teilen sich denselben Profiltext und dieselben Antworten. Die 88 Urteile des Arms `beziehung` verteilen sich auf **sechs** Personas mit Quoten von 35,7 % bis 100 %, und ein Permutationstest weist diese Streuung als größer aus, als Losen sie erzeugt (p = 0,010). **Die unabhängige Einheit ist die Persona, und davon gibt es sechs.**
>
> Über ganze Personas gezogen — Bootstrap, 20.000 Läufe — steht dieselbe Zahl bei **64,8 % mit einem 95-Prozent-Intervall von 49,4 % bis 80,0 %**; 96,6 % der Läufe liegen über dem Zufall. Die Gegenprobe steht im Kontrollarm: `zufall` ergibt 47,1 % mit einem Intervall von 40,7 % bis 55,0 %, also halb so breit und den Zufall einschließend. Die Verbreiterung im Messarm ist der Personeneffekt und kein Artefakt der Rechnung.

> **Der Blindtest landet nicht beim Zufall** — knapp. Damit ist die Frage aus dem Absatz darüber beantwortet: Die Kalibrierarbeit an Rädern und Beitragszahlen zielt auf etwas, das ein fremder Beurteiler sehen kann. **Ergänzt am 07.08.2026:** Die Genauigkeit der Zahl ist ±15 Punkte, nicht ±10. Eine Kalibrierung, die die Trennschärfe um zehn Punkte hebt, bewegt sich innerhalb des Intervalls — der Umfang der nächsten Reihe bemisst sich deshalb in **Personas**, nicht in Urteilen.

> **Und diese Zahl ist als Beleg vergeben.** Nach `F-KAL-1` sind die sechs Bögen vom 02./03.08.2026 **Kalibriermenge**: Auf ihnen darf beliebig oft gemessen werden, und keine ihrer Zahlen ist je ein Beleg. Die 64,8 % bleiben gültig als **Ausgangsstand des unkalibrierten Apparats auf der Kalibriermenge** — in dieser Rolle werden sie gebraucht, denn ohne sie ist später keine Richtung ablesbar. Der Bauplan der Validierungsmenge steht in `novaberg-kalibrierung_k.md` §5.

**Und das Beziehungsprofil trennt nicht besser als eine bloße Themenliste** — McNemar über die 27 diskordanten Fälle, p = 1,00. Kein knappes Ergebnis, das mehr Fälle bräuchte, sondern ein exaktes Unentschieden. Die beiden Arme sind aber auf **verschiedenen** Personas erfolgreich (Hartmut 84 % gegen 53 %, Sarah 50 % gegen 85 %) und tragen damit verschiedene Information; fallweise stimmen sie zu 68,6 % überein gegen 54,2 % bei Unabhängigkeit.

**Die Verwechslungen haben eine Richtung:** Jana verliert keine eigene Antwort (9/9), Konrad und Mehmet verlieren ihre überwiegend an sie. Die drei bilden im Profilraum ein enges Bündel (0.875–0.896). Der Apparat erzeugt **einen starken warmen Pol und zwei schwächere Kopien**, nicht drei eigene warme Beziehungen — dieselbe Stelle, auf die der Radbefund vom 03.08. zeigte.

**Der Geltungsbereich beider Maße ist enger als er aussieht.** Auf diesem Korpus sind **drei der fünf Profile leer** — `kern_hash`, `intentions_profil` und `emotions_profil` tragen für alle sechs Personas in beiden Richtungen null Zeichen. Die 64,8 % sind damit das, was die **kurzfristige Hälfte allein** leistet, nicht der ganze Apparat.

> ~~Grund: weil alle drei `lzg_knoten` lesen und eine frische Persona kein Langzeitgedächtnis hat.~~ → **Widerlegt am 08.08.2026 am Bestand.** `konrad` trägt **82** und `leon` **38** LZG-Knoten, entstanden während ihrer Bögen am 02.08.; die übrigen vier tragen keinen einzigen. Der Satz stimmt für vier von sechs Personas und wird als allgemeine Erklärung gelesen. **Die Profile waren leer, aber nicht aus diesem Grund** — die eigentliche Ursache ist ungeklärt und ein eigener Befund.
>
> **Und die Folge ist größer als die Korrektur:** Der Zustand der Langzeitschicht war über die sechs Bögen **nicht konstant**. `anker_retrieval()` speist Thinker und Gesprächsvektor aus `lzg_knoten` — zwei Personas liefen also gegen einen anderen Apparat als die vier anderen. Eine Reihe, deren Bezugspunkt zwischen den Läufen wechselt, vergleicht nicht.

**Was weiter aussteht:** Antwortlänge und Fragenanteil (Maß 1) sind unerhoben. Und **keines der Maße prüft die Passung** — die vorab festzuschreibenden Erwartungen je Person existieren nicht, gemessen ist Unterscheidbarkeit, nicht Richtung. Der Urteiler war zudem dasselbe Modell, das die Antworten erzeugt hat; ein zweiter, fremder Urteiler auf demselben Zwischenstand ist offen.


### Gesprächsvektor (Epic 9, offen)
| # | Thema | Status |
|---|-------|--------|
| GV3 | Invertierte Perzeption (Ziel → benötigter Modus) — Dreischicht-Prompt-Integration | ✅ Chat 72 |
| GV4 | Wissens-Lücken via Embedding-Nachbarschaft | 🔧 Chat 71 (Kern: LZG + KZG) |
| GV4b | Agenten als Wissensquellen (Timeline, Notizen, Fakten, Dateien) | ⬜ Epic unten |
| GV5 | Vektor-Typen (explizite Erkennung) | ⬜ Implizit durch Farbtöne abgedeckt |
| GV6 | Pixie-Vorbereitung (Vektor im Hintergrund vorbereiten) | ⬜ Nach VertiefungsAgent v2 |


### Domain-Language-Normalisierung (Epic 15, 4/6)
| # | Thema | Status |
|---|-------|--------|
| 15e | FaktenAgent (Salienz-Pipeline) | ⬜ |
| 15f | DateienAgent (geplant) | ⬜ |


### DateienAgent / ProjektAgent (Chat 45)

Aufspaltung des DateienAgenten in zwei Agenten mit unterschiedlichen Abstraktionsebenen:

**DateienAgent** — niedrige Ebene, CRUD für Dateien:
- Datei erstellen, lesen, suchen, aktualisieren, löschen
- Embedding-basierte Suche über Dateiinhalte
- Flach, keine Struktur-Annahmen

**ProjektAgent** — hohe Ebene, orchestriert Dateien:
- Projekt anlegen = Ordner + Meta-Datei (`_meta.md` mit Ziel, Status, Kontext)
- Dateien einem Projekt zuordnen
- Projektstatus verwalten (aktiv, pausiert, abgeschlossen)
- Projekt-Kontext als Block für Responder oder Claude API bereitstellen
- Automatisch Recherche-Ergebnisse dem richtigen Projekt zuordnen

ProjektAgent nutzt DateienAgent als Infrastruktur (Separation of Concerns). ProjektAgent ist das Fundament für Skill-Generierung, Recherche-Ablage und autonome Problemlösung.

---


### Fachabteilungs-Agenten (Epic, Chat 49)

**Vision:** Agenten sind keine CRUD-Masken mit LLM-Wrapper, sondern **Fachabteilungen mit Intelligenz**. Sie prüfen Input gegen den Bestand, erkennen Widersprüche, verweigern Unsinn, fragen differenziert zurück, und validieren ihre Ausgaben semantisch bevor sie zurückmelden.

**Leitmetapher:** "Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!"

**Neue generische Agent-Pipeline:**
```
Input-Validation → Semantik-Check → HITL-Gate → CRUD → Output-Validation → Antwort
```

Zwei neue Nodes pro Agent:
- **Semantik-Check (Input):** Prüft Kompatibilität der gewünschten Operation mit aktuellen Daten. Klassifiziert: Widerspruch, Ergänzung, Redundanz, identisch. Formuliert differenzierte Rückfrage.
- **Output-Validation:** Prüft nach CRUD, ob das Ergebnis semantisch Sinn macht (z. B. abfängt CRUD-DESTILL-SUBTRAKT — "Nicht mehr das kleine Mädchen sein" als Anweisung → unsinnig → zurück zum Classify).

**Differenzierte Rückfrage-Typen** (statt einfachem Ja/Nein):
- Widerspruch: "Das neue X passt nicht zum aktuellen Y. Soll ich Y deaktivieren?"
- Ergänzung: "Ich bin dann X und Y, passt das?"
- Redundanz: "Das habe ich im Kern schon. Zusammenführen?"

**Beseitigt strukturell:**
- CRUD-REACTIVATE-COEXIST (Semantik-Check fängt Widersprüche ab)
- CRUD-DESTILL-SUBTRAKT (Output-Validation erkennt unsinnige Destillation)
- Vermutlich ähnliche Fälle in DirektivenAgent, NotizenAgent, TimelineAgent

**Betrifft:** CharakterIdentitaetAgent, DirektivenAgent, NotizenAgent, TimelineAgent (gemeinsame Infrastruktur in `agents/crud_validation.py`)

**Voraussetzung:** ✅ RESUME-REJECT gelöst (Chat 50). Phase 0 abgeschlossen — Resume-Node mit Strategy-Hook implementiert.

**Inspiration:** OpenClaw, Agentic Workflows (2026-Standard für Agent-Design). Eine Aufgabe erhalten, Input normalisieren, prüfen/validieren, gegen DB verarbeiten, Ausgabe semantisch validieren, Antwort zurückgeben — gerne mit mehreren Rücksprachen.

**Konzept-Dokument:** `novaberg-agent-fachabteilung_k.md` (Chat 49)

**Aufwand:** Mehrere Sessions. Pilot-Agent: Charakter (aktueller Fokus). Rollout danach auf die anderen drei.

---


### Charakter-Hash: Fehlende Zeitstempel (Chat 71)

Die Tabelle `charakter_hash` hat nur `kern_aktualisiert_am` und `adaptive_aktualisiert_am`.
Drei Profile haben keinen eigenen Zeitstempel — man kann nicht sehen wann sie
zuletzt destilliert wurden:

| Profil | Spalte existiert | Zeitstempel |
|--------|:---:|:---:|
| kern_hash | ✅ | kern_aktualisiert_am |
| adaptive_hash | ✅ | adaptive_aktualisiert_am |
| beziehungsprofil | ❌ | fehlt |
| intentions_profil | ❌ | fehlt |
| emotions_profil | ❌ | fehlt |

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehung_aktualisiert_am TIMESTAMPTZ;
2. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentionen_aktualisiert_am TIMESTAMPTZ;
3. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotionen_aktualisiert_am TIMESTAMPTZ;
4. CharakterAgent: Beim Schreiben den jeweiligen Zeitstempel setzen
5. Charakter-Panel: Alle 5 Zeitstempel anzeigen

Priorität: Niedrig — aber wichtig für Debugging (Chat 71 hat gezeigt dass ein
veraltetes Beziehungsprofil die gesamte Antwortqualität ruiniert).

---


### Charakter-Hash schema-konform um `beobachter` erweitern (Chat 71)

**Stufe 1 erledigt (Chat 73):** `beobachter_filter` in `_kzg_laden()` + 20 Altdaten migriert. Stufe 2 (Schema-Erweiterung) und Stufe 3 (vier Tripel im CharakterAgent) noch offen.

Konzept: `novaberg-convention-paar-schema.md`. Heute mischt der Hash-Eintrag
`(nova, meister)` zwei Sichten — Nova-aus-User-Sicht (Beobachter `user`) und
Nova-aus-Selbstsicht (Beobachter `assistant`) — in einem Datensatz. Dadurch
überschreibt jede Destillation die jeweils andere Sicht.

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beobachter TEXT NOT NULL DEFAULT 'user';
2. Primärschlüssel umstellen: `(user_id, character_id)` → `(user_id, character_id, beobachter)`.
3. CharakterAgent-Loop erweitern: Statt zwei Paaren jetzt vier Tripel — `(meister, nova, user)`, `(meister, nova, assistant)`, `(nova, meister, user)`, `(nova, meister, assistant)`.
4. Destillations-Funktionen filtern KZG/LZG zusätzlich nach `beobachter`.
5. Enricher entscheidet per Kontext, welchen Hash er liest.
6. Cluster-Promotion-Guard für Nova ([promotion/agent.py:575-577](novaberg/server/agents/promotion/agent.py#L575-L577)) entschärfen, sobald genug Nova-KZG-Material da ist (sonst läuft die Promotion auf 0 Einträgen).

Priorität: Mittel. Erst sinnvoll, wenn der Sofort-Fix aus Chat 71
(`nova_gedaechtnis.py`) ein paar Tage Material gesammelt hat. Vorher fehlt
die Datengrundlage für die Beobachter-Trennung.

---


### Altdaten-Migration: `kzg:nova:nova:*` → `kzg:nova:meister:*` (Chat 71)

Konzept: `novaberg-convention-paar-schema.md`, Abschnitt 4.2. In Redis liegen aktuell
19 KZG-Einträge unter `kzg:nova:nova:*` aus der Zeit vor dem Chat-71-Fix.
Sie werden vom CharakterAgent zufällig mitgelesen (Wildcard `kzg:nova:*`),
gehören aber semantisch unter `kzg:nova:meister:*` mit `beobachter=assistant`.

Fix:

1. Tool-Skript schreiben (analog `tools/migrate_kzg_keys.py`): Iteriere alle Keys mit Pattern `kzg:nova:nova:*`.
2. Pro Eintrag den Redis-Hash auslesen, mit `beobachter=assistant` neuen Key `kzg:nova:meister:{id}` schreiben, alte TTL übernehmen, alten Key löschen.
3. Anschließend `hash_dirty:nova:meister` setzen, damit der CharakterAgent das migrierte Material direkt einliest.
4. Sicherheitscheck: Vor der Migration zählen, nach der Migration zählen, in einem Log dokumentieren.

Priorität: Niedrig. Solange der Sofort-Fix neue Einträge sauber unter
`kzg:nova:meister:*` ablegt, schadet das Altmaterial nicht — es führt nur
zu einer leichten Mischung in der Destillation. Wenn die Beobachter-
Erweiterung (siehe oben) kommt, müssen die Altdaten ohnehin migriert werden.

---


### Reducer-Umbau — Strukturierter memory_context (Hoch, Chat 74)

**Stand Chat 74:** Erst-Iteration als String-Parser implementiert (Chat 74). Architektur-Schuld erkannt: Parser auf Pre-Format-String ist brüchig (Mehrzeilen-Plugin-Blöcke werden zerlegt). Sauberer Umbau geplant.

**Ziel:** Memory-Module und Plugin-Manager liefern strukturierte `ContextEntry`-Listen statt vorformatierter Strings. Reducer arbeitet auf Dicts. Ein Formatter-Tool baut den finalen `memory_context`-String für den Responder.

**Konzept-Dokument:** `novaberg-reducer-umbau_k.md` (Chat 74, vollständige Architektur, 7-Phasen-Plan STRUCT-1 bis STRUCT-7).

**Phasen:**

1. STRUCT-1: `ContextEntry`-TypedDict + State-Erweiterung
2. STRUCT-2: KZG/LZG-Module umstellen (alte Funktionen entfernen)
3. STRUCT-3: Plugin-Inventur + Basisklasse umstellen
4. STRUCT-4: Plugin-Manager einzeln umstellen
5. STRUCT-5: Enricher umbauen (sammelt Entries statt Strings)
6. STRUCT-6: Formatter-Tool + Reducer neu
7. STRUCT-7: Verifikation

**Big Bang:** Keine 2-Methoden-Schicht. Plugin-Manager brechen während des Umbaus, werden im Nachgang einzeln nachgezogen.

**Motivation:**
- Echo-Bug bei langen Sessions (~11+ Turns)
- ENRICHER-DUP (Mehrfach-Einträge im Kontext)
- Mehrzeilen-Notizen werden vom Parser fragmentiert (latenter Bug)
- Format-Wissen über fünf Stellen verteilt (KZG, LZG, Enricher, Plugin-Manager, Reducer-Parser)

**Was unverändert bleibt:**
- Responder-Schnittstelle (`state["memory_context"]` als String)
- Format-Konvention im Output-String
- CharacterGraph + HumanGraph Knoten/Kanten
- Alle anderen Nodes

**Priorität:** Hoch — der heutige Reducer arbeitet, hat aber latente Bugs und brüchige Architektur.

---


### Assoziatives Retrieval — Kontext als Geflecht (Mittel, Chat 74)

Der Enricher liefert heute isolierte Fragmente, ausgewählt nach Embedding-Ähnlichkeit zum Prompt. Bedeutung entsteht aber aus Verbindungen zwischen Einträgen — ein KZG-Treffer "Meister hat Lumi seit März" und "Lumi schläft viel" gehören zusammen, weil sie denselben Referenten teilen, nicht weil sie zum aktuellen Prompt ähnlich sind.

**Drei Assoziations-Dimensionen:**

- **Referentiell** — selbe Entität in mehreren Einträgen. KZG/LZG haben Embeddings, aber keine Entity-Marker. Anna und Lumi werden semantisch ähnlich (beide Lebewesen + Meister), aber nicht referentiell unterschieden.
- **Temporal** — Reihenfolge und Gleichzeitigkeit. Einträge tragen `erstellt_am`, aber kein Eintrag weiß, was zur selben Episode gehört. "Streit mit Anna" und "Lumi tröstete" am selben Tag sind narrativ verbunden, im Retrieval aber entkoppelt.
- **Kausal/thematisch** — Themen-Tags existieren, werden aber nur zur Verstärkung genutzt, nicht zur Cluster-Bildung beim Retrieval. Drei Einträge mit Thema "Beziehungsende" bilden zusammen eine Geschichte, die relevanter sein kann als zehn isolierte Hochsalienz-Treffer.

**Verwandtschaft:** Epic 16 (Entity-First-Retrieval) ist die referenzielle Spitze dieses Eisbergs. Akten-basiertes Retrieval ist der konkrete Implementierungsschritt der referentiellen Dimension.

**Priorität:** Mittel — konzeptuelle Vertiefung, kein akuter Blocker.

---


### Akten-basiertes Retrieval — Entitäten als kohärente Pakete (Mittel, Chat 74)

Heute ist die Einheit der Bewertung im Retrieval = einzelner Fakt. Beobachtung: Anna ist 20 Triples, davon werden 5 gefunden, ohne Zusammenhang. Schrott im Kontext.

**Vorschlag:** Einheit der Bewertung = **Entitäten-Akte**. Pro relevanter Entität liefert der Fakten-Agent eine geschlossene Akte mit allen Fakten + Metadaten + destillierter Beschreibung. Der Reducer bewertet Akten als Ganzes — entweder die ganze Anna-Akte rein oder ganz raus. Niemals halb-Anna.

**Drei Stellen müssen sich ändern:**

1. **Fakten-Agent als Akten-Lieferant** — Funktion `entity_akte_laden(entity_id) -> EntityAkte` mit allen Fakten + Metadaten + Zusammenfassung
2. **Enricher als Akten-Sammler** — identifiziert relevante Entitäten (über Embedding oder NER), zieht pro Entität die Akte
3. **Reducer als Akten-Bewerter** — bewertet jede Akte als Block; akzeptierte Akten werden als Ganzes weitergegeben, abgelehnte komplett verworfen

**Verbindung zum Reducer-Umbau:** Der heutige Reducer (Chat 74, String-Parser) und der Umbau (strukturierter memory_context) sind Voraussetzung. Akten-Bewertung ist eine Erweiterung, keine Ersetzung. Stufe 3 im Reducer-Konzept (Akten-aware) baut auf Stufe 1+2 (Exakt + Substring) auf.

**Voraussetzungen:**
- Fakten-Tabelle bereinigt (FAKTEN-RAUSCH gelöst, Reaktivierung möglich)
- Reducer-Umbau abgeschlossen (Daten strukturiert)
- Knowledge-Graph-Erweiterung (1-Hop für gefundene Entitäten)

**Priorität:** Mittel — adressiert die "zu wenig Richtiges"-Pathologie (Anna in Nürnberg ohne Schwester-Kontext). Pendant zur "zu viel Falsches"-Pathologie, die der Reducer-Umbau adressiert.

---


### Anker-Emotion (Grundemotion pro Charakter) (Niedrig, Chat 74)

Heute ist `emotions_profil` eine Beobachtung aus dem LZG (was wurde gefühlt). Eine Anker-Emotion wäre eine Setzung — eine Charakter-Eigenschaft, gegen die der Verlauf kontinuierlich zurückdriftet.

**Mechanik:** In `ei/berechnung.py` für Novas Strang bei jeder Akkumulation den Verlauf gewichtet zum Anker zurückdriften lassen:

```
nova_emotion[t+1] = α × empathie_signal + β × verlauf[t] + γ × anker
```

Mit `α + β + γ = 1`. Bei Marvin (depremierter Roboter): `anker = traurigkeit(0.6)`, `γ = 0.3`. Bei Nova heute: `γ = 0` (kein Anker, reine Beobachtung).

**Datenmodell:** Neue Spalte `grundemotion` in `charakter_hash` oder eigene Tabelle `charakter_grundemotionen` (mehrere Anker pro Charakter, z.B. "fundamental traurig, gelegentlich sarkastisch").

**Beispiel-Charaktere mit Anker:** Marvin (Hitchhiker), eeyore-artige Trauer, festes Zen-Gleichmut.

**Priorität:** Niedrig — keine Funktion gebrochen, aber öffnet expressiven Spielraum für Charaktere.

---


### Reducer-Node — Gegenspieler zum Enricher (Hoch, Chat 71/72) ✅ Erst-Iteration Chat 74

Der Reducer fasst ältere Session-Turns zusammen, statt alle 11+ Turns wörtlich an den Responder durchzureichen. Pendant zum Enricher: wo der Enricher anreichert, dünnt der Reducer aus.

**Motivation:** Echo-Bug (Chat 72) zeigt, dass Nova ab ~11 Turns die User-Nachricht wörtlich wiederholt. Vermutete Ursache: Kontext-Sättigung durch Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag.

**Status Chat 74:** Erst-Iteration als String-Parser implementiert. Funktioniert für Exakt-Dedup von KZG/LZG-Einträgen. Architektur-Schuld erkannt — sauberer Umbau geplant (siehe oben: Reducer-Umbau).

---


### Modus-Kalibrierung: spielerisch vs. emotional (Niedrig, Chat 72)

Perzeption klassifiziert 😍-Katzen-Chat als `gespraechs_modus="emotional"` statt `"spielerisch"`. Folge: Tiefe-Achse 0.70 statt 0.40, was die Sektor-Berechnung in der Dreischicht verschiebt.

**Lösungsansatz:** Modus-Beispiele im Perzeption-LLM-Call schärfen. Spielerisch (Tier-Niedlichkeit, Quatschen, leichte Themen) klar von emotional (Beziehungsthemen, Sorgen, Tiefe) abgrenzen.

**Priorität:** Niedrig — kosmetische Verschiebung der Sektor-Verteilung, keine Funktion gebrochen.

---


## Verlauf des Standes

- **24. August 2026, 13:35 UTC** — der Matrix-Epic loest seine eigene Abschaltbedingung ein. Sie stand seit dem 23.08. als Satz da (*„Ein Kanal wird abgeschaltet, wenn der andere gemessen traegt — der Handy-Test steht noch aus"*) und war seit dem 23.08. erfuellt, weil AP 8 auf ✅ ging; **einen Tag lang hielt sich die Sperre selbst, nachdem ihr Grund entfallen war.** Telegram ist abgeschaltet, `telegram_bot/` bleibt liegen. Offen: der Token-Widerruf beim BotFather.

- **23. August 2026, 17:15 UTC** — ein Eintrag neu: `DATEIINDEX-GRAPHKANAL`. Er entsteht aus einer Messung, die gegen einen Bau entschied — die Stichwoerter des Dateienindex gegen den Entitaetenbestand aufzuloesen ergibt 10 Treffer aus 843, und 116 der 122 Kanten zeigen auf dieselbe Entitaet.
Die Fortschreibung des Standes, aus der Kopfzeile geloest am 20.08.2026. Der Wortlaut jedes Eintrags ist unveraendert; vorangestellt ist allein sein Datum.

- **21. August 2026, 09:43 UTC** — **Der benannte Rest von `SUCHSCHLUESSEL-OHNE-VERLAUF` ist gemessen und zu.** Query Rewriting traegt bei allen fuenf Lesern des Suchschluessels: 39 Sonden, rohe Aeusserung 0, Rewrite 37, Deckung mit der Referenz 39 von 39. Dabei ein eigener Fund: Zwei der Konsumenten haben keinen wirksamen Boden.
- **21. August 2026, 22:50 UTC** — **`BUGREGISTER-ZUSTAND-NICHT-LESBAR` geschlossen.** Die zwoelf fehlenden Abschnitte sind einzeln gegen HEAD `62560cf` geprueft statt uebertragen — **6 behoben, 6 offen** —, und damit traegt jeder der 82 Eintraege seinen Zustand an genau einer Stelle: **64 offen / 18 behoben**, mit `grep` zaehlbar. Die Pruefung fand nebenbei einen Widerspruch, den eine Uebertragung fortgeschrieben haette: eine Ueberschrift sagte *behoben*, waehrend derselbe Eintrag seine Schlussbedingung als ausstehend fuehrte. **Ein Eintrag kommt dabei neu hinzu:** `BUGREGISTER-ALTEBENE-OHNE-ZUSTAND` — eine Zaehlung ueber beide Ueberschriftenebenen des Registers fand **166 aeltere Eintraege ohne Zustandszeile**. Die neue Zahl deckt 82 von 248.
- **20. August 2026, 19:36 UTC** — **`BUGREGISTER-ZUSTAND-NICHT-LESBAR` zur Haelfte umgesetzt und ausdruecklich nicht geschlossen.** Die Form steht — je Eintrag eine Zeile `**Zustand:**` mit geschlossener Wertemenge, Pruefdatum und HEAD —, und 70 der 82 Abschnitte tragen sie. Die uebrigen zwoelf nicht. Ein Befund mit mehreren Stellen ist erst geschlossen, wenn jede steht.
- **20. August 2026, ~21:20 UTC** — **Ein Eintrag neu aus dem Abgleich des Verlaufs:** `BUGREGISTER-ZUSTAND-NICHT-LESBAR` — der Zustand eines Defekts steht an drei Stellen und in keiner verbindlich; von 82 Abschnitten tragen 6 ueberhaupt eine Marke. Jede Zahl ueber offene Defekte ist bis dahin eine Schaetzung.
- **20. August 2026, ~20:50 UTC** — **Ein Eintrag geschlossen:** `SUCHSCHLUESSEL-OHNE-VERLAUF` ist als Query Rewriting umgesetzt und im Betrieb belegt. Ein Rest ist benannt: Die Wirkung auf KZG und LZG ist ungemessen — gemessen wurde gegen die Bibliothek.
- **20. August 2026, ~18:30 UTC** — **48 neue Eintraege** aus der Klassifikation der Fundliste, jeder mit ID, `Was fertig waere` und einer ersten Prioritaet. **Die Prioritaet ist kein Band** — ein Band wird gegen den Code vergeben, nicht gegen den Eintrag.
- **20. August 2026, ~17:05 UTC** — **kein Eintrag bewegt.** Die Kopfzeile trug 10.512 Zeichen in einer Zeile und ist in den Abschnitt *Verlauf des Standes* geloest — 29 Eintraege, Wortlaut unveraendert.
- **20. August 2026, ~14:15 UTC** — **zwei neu: `LAENGENVORGABE-UNGEMESSEN` und `MASSBLOCK-IM-BETRIEB-UNGEMESSEN`** — die Antwortlänge hat seit heute drei Einflüsse, und der Verfasser liest die Haltung; beides ist bezeugt und im Betrieb ungemessen.
- **20. August 2026, ~13:55 UTC** — **`GLIEDERUNG-NUR-MARKDOWN` umgesetzt** — der Index versteht seit heute alle fünf Textformate, die er annimmt; `.txt` ist dabei ausdrücklich als leere Gliederung registriert und nicht als Lücke.
- **20. August 2026, ~13:15 UTC** — **`MARKDOWN-ERKENNER-IST-HANDARBEIT` umgesetzt** — die Gliederung von Markdown macht seit heute `markdown-it-py`; die Zaunbilanz bleibt davor stehen, weil der Parser den unpaarigen Zaun ebenfalls falsch liest (45 statt 83 Überschriften). `GLIEDERUNG-NUR-MARKDOWN` bleibt offen.
- **20. August 2026, ~12:30 UTC** — **zwei neu: `GLIEDERUNG-NUR-MARKDOWN` und `MARKDOWN-ERKENNER-IST-HANDARBEIT`** — der Dateien-Index nimmt fünf Textformate an und versteht eines, und der eine Erkenner ist ein Regex-Automat mit zwei von vielen CommonMark-Regeln. Beides ist seit heute laut statt still, aber nicht gebaut.
- **20. August 2026, ~09:45 UTC** — **neu: `BIBLIOTHEK-BLIND-AUF-INHALTSHOEHE`** — die Bibliothek findet auf Themenhöhe (Rang 1, Kosinus bis 0,7375) und ist auf Inhaltshöhe blind (Rang 142 bei 0,1768, dieselbe Ausarbeitung). Die Schwelle 0,50 schneidet 9 von 10 richtigen ab, ist aber nicht der Fehler: Sie ist an Themenfragen kalibriert, während der Enricher mit dem Vektor des Turns sucht. Das erklärt 2 echte Treffer in 142 Nutzerturns.
- **20. August 2026, ~09:05 UTC** — **`EMBED-LISTE-DATEIENINDEX` gebaut, gemessen und verworfen** — der Umbau stand vollständig (Tabelle, Schreibweg, drei Lesewege, 1456 nachgebettete Vektoren) und brachte **keine** Verbesserung: Rang 1 unverändert 8/12, Top 3 von 10 auf 9, und die Trennung wird schlechter. Zurückgebaut. Die Analogie zur Bibliothek trägt nicht — dort standen mehrere Gegenstände in einem Feld, hier beschreiben Thema und Stichwörter denselben.
- **20. August 2026, ~08:30 UTC** — **`AUFZEICHNUNGEN-BODEN-NACHZIEHEN` beantwortet, ein neuer Eintrag daraus** — 24 Sonden gegen 174 Indexzeilen: Der Boden 0,30 trägt (Lücke der Mediane 0,177 gegen 0,038 am 18.08.), und der eine richtige Fall, den er abschneidet, wird vom scharfen Kanal aufgefangen. Der verbleibende Fehler ist die **Rangfolge**: `EMBED-LISTE-DATEIENINDEX` ist die dritte Stelle, an der ein Vektor mehrere Gegenstände trägt — hier `thema` plus acht Stichwörter, mit gemessener Wirkung (Rang 1 in 8 von 12).
- **20. August 2026, ~07:35 UTC** — **zwei Einträge neu bewertet, keiner geschlossen** — `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` ist **entblockt**: Die Freigabe von `docs/` hat den Index von 14 auf 174 Zeilen gebracht, und damit existiert der Bestand, den der Eintrag seit dem 18.08. für seine Sondenmessung verlangt; die Messung selbst steht aus. `AUFZEICHNUNGEN-QUANTIL` bleibt unverändert offen, hat aber ab jetzt einen Korpus, an dem eine Verteilung entstehen kann.
- **19. August 2026, ~20:40 UTC** — **zwei Bloecke aus dem Umbau der Bibliothek** — `ein Vektor je Gegenstand` mit drei Eintraegen, davon zwei am selben Tag beantwortet und durchgestrichen (`OLLAMA-VERSION-VIER-MONATE-ALT`, `WIS-ENRICHER-UNGEMESSEN`); dazu `WIS-SCHWELLE-MESSEN` beantwortet — die Frage war falsch gestellt, nicht die Schwelle war das Problem, sondern die Rangfolge unter ihr.
- **19. August 2026** — **neuer Block: die Rollen eines Wissen-Silos** — vier Einträge aus einer gezählten Matrix. Von neun Silos trägt **genau eines alle drei Rollen** (Quelle, Zettel, Werkzeug: die Timeline); ihr eigenes erarbeitetes Wissen trägt **eine**. `WISSEN-OHNE-ZETTEL` ist der nächste Sprint und hat seinen Zuschnitt samt drei Negativfällen; `SILO-OHNE-WERKZEUG`, `ROLLENMATRIX-OHNE-PRUEFUNG` und `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` hängen daran. Der letzte ist der überraschendste: Der Recherche-Agent füllt eine Bibliothek, die er selbst nie befragt.
- **18. August 2026** — Chat 151 — **der Rückweg ins Wissen ist gebaut** (`novaberg-agent-dateien_k.md` §4b): Zuordnung über die Zusammenfassungen, Einarbeitung mit chirurgischem Schnitt, Verstärkung der Bibliothekszeile, ausgelöst von der Promotion. **Offen bleiben zwei der drei Wege** — das Einprägsame und das Zugehörige — und die Idempotenz, die heute allein am Modellaufruf hängt; beides in der Fundliste. Dazu **`WIS-8-STUFE-2` geschlossen**: Der Zoom hat seinen Aufrufer, gemessen an einem echten Turn; als Rest bleibt `zeilen_lesen` ohne Aufrufer.
- **18. August 2026** — Chat 150 — neuer Block **aus dem Bau der Enricher-Quelle** mit `AUFZEICHNUNGEN-QUANTIL`, `AUFZEICHNUNGEN-BODEN-NACHZIEHEN` und `SALIENZKURVE-UNTEN-ZU-STEIL`, alle drei ohne Band. Der dritte ist **entschieden, aber nicht gebaut**: Der Exponent der Salienzkurve geht von 0,5 auf **1,16**, roh 0,3 bildet dann auf 0,40 ab statt auf 0,674. Er steht hier statt im Dateien-Konzept, weil die Kurve drei Speicher trägt und ihre Änderung 2394 gespeicherte Werte neu bewertet — **ein eigener Sprint, ausdrücklich nicht nebenbei.** Der erste ist die nicht gebaute Hälfte der Schwelle und **nicht rechenbar, bevor die mitlaufende Verteilung existiert**; der zweite ist der Vorbehalt zum gemessenen Boden in haltbarer Form.
- **18. August 2026** — Chat 149 — **`RAUCHTEST-ANWENDUNG-IMPORT`** neu: fünf Zeilen, die die Anwendung importieren und die Route-Tabelle zählen; gemessen sind **0 von 126** Testdateien, die das heute tun, und eine Typannotation legte den Dienst deshalb unbemerkt lahm. **`WIS-8-STUFE-2` zweimal neu bewertet**: Die Leseschicht hat seit heute ihren ersten Produktivaufrufer — der Wächter ruft `struktur_analysieren` —, offen bleibt der Zoom (`block_lesen`, `zeilen_lesen`, `datei_grep`).
- **16. August 2026** — **der Engpass der Reihe 3 ist vermessen** — der Platz zu rund 93 % besetzt, 89 % der Laeufe an `recherche`, Rueckstand 583, Abfluss rund 20 verwertbare Ergebnisse am Tag; `SHADOW-QUEUE-RUECKSTAND-UNGEMESSEN` und `PIXIE-EIN-SLOT-BLOCKIERT-ALLES` haben damit ihre Zahl und bleiben trotzdem offen, weil ein Punkt keine Reihe ist. `RECHERCHE-ZWISCHENDESTILLATION-OHNE-GRUND` hat seinen Grund: eine geerbte Frist von 300 s, nicht der Inhalt des Schritts — behoben ueber `F-FRIST-1`, die Frage nach dem Sinn des Schritts bleibt offen und ist schwerer geworden. Neu als fuenfter Aspekt des Engpasses: Der Fehlversuchspfad loescht **hart** und waehlt nach *hoher* Salienz aus.
- **16. August 2026** — `SELBSTAUSKUNFT-OHNE-LESER` in den Block **die Gegenrichtung der Doku-Prüfung** aufgenommen — **das erste Fundstück genau der Klasse, die `KANAL-OHNE-GEGENSTUECK` beschreibt** — und kein Werkzeug hat es gefunden, sondern die Unterscheidung zwischen Anmeldung und Vorbedingungs-Auflösung: 14 von 14 Agenten deklarieren ihre Fähigkeiten, `AgentRegistry.beschreibungen()` baut daraus den Planner-Prompt, und kein Produktivcode ruft ihn auf.
- **16. August 2026** — neuer Block **die Gegenrichtung der Doku-Prüfung** mit `KANAL-OHNE-GEGENSTUECK` und `NAMENSREGELN-JENSEITS-DER-FORM`, beide ohne Band — die Klasse, die die drei Kriterien vom selben Tag prinzipiell nicht finden können.
- **16. August 2026** — Block **aus dem Halten der Konventionen** mit `PENDING-AGENT-INS-PAYLOAD` und `SSE-REST-IM-ENDPUNKT`, beide ohne Band.
- **16. August 2026** — Block **die Fachspeicher bekommen ihre Agenten** mit `FACHSPEICHER-AGENTEN`, `FAKTEN-BINDUNG-OHNE-VERFALL` und `REEMBED-WISSENSSPEICHER`, alle ohne Band. Die Trennlinie ist der Fremdschlüssel: Eine Fakten-Entität, auf die einer zeigt, verfällt nicht — die Bindung darauf darf.
- **16. August 2026** — neuer Block **das Messinstrument der Zustellung** mit `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` und `RIEGEL-5-7-OHNE-EINTRAG` — die zwei Reste der Protokollpflicht, die mit dem Fall der stündlichen Decke von einer Datenlücke zur Lücke im Messinstrument geworden sind.
- **16. August 2026** — `EIGENZEIT-BAUTEILE` geschlossen bis auf die benannten Reste — alle sechs Bauteile stehen, mit Riegel 2 ist die stündliche Decke gefallen.
- **16. August 2026** — Block 15.08. mit `DOKU-VOLLPRUEFUNG` und `NACHZUG-KANDIDATEN-GATE`; `EIGENZEIT-BAUTEILE` fortgeschrieben — E, F, C, A, B gebaut, von D die Voraussetzung und Riegel 1.
- **9. August 2026** — Chat 134 — **die Rangordnung steht**, siehe den gleichnamigen Abschnitt. Gemessen: 184 offene Eintraege, davon **18 mit Prioritaet und 166 ohne** — die Prioritaet ist Pflichtteil und fehlte in neun von zehn Faellen, waehrend die vorhandenen je Eintrag beim Anlegen gesetzt und nie gegeneinander gehalten wurden. Statt Einzelwerten jetzt **vier Baender und eine Tabelle**, gewichtet nach Zugehoerigkeit zu einer der vier laufenden Reihen. Band A traegt **zwei** Eintraege, und die Zahl ist die Aussage: Ein Band, das zwanzig fasst, ist dasselbe wie „hoch" mit siebenundzwanzig. Beim Aufstellen hat sich ein Eintrag selbst aus Band A herauskorrigiert — `PROFIL-HISTORIE-FEHLT` trug die Widerlegung seit dem 02.08. im eigenen Text.
- **9. August 2026** — Chat 133 - **41 Eintraege aus der klassifizierten Fundliste**, jeder mit Kennung, Prioritaet und der Zeile *Was fertig waere*: Ein Eintrag, dessen Abschluss niemand erkennen kann, wird nie geschlossen. **Vier davon beschreiben denselben Engpass von vier Seiten** - ein serieller Platz fuer alle Hintergrundarbeit, ein Lauf, der ihn ueber seine eigene Zeitgrenze haelt und danach mit vollem Anspruch zurueckkehrt, 230 Auftraege an zwei Agenten, die es nicht gibt, und ein Rueckstand von 649, dessen Abfluss nie gemessen wurde. **Wer einen davon einzeln angeht, misst die Wirkung der anderen drei mit** - das steht bei allen vieren dabei. Zwei weitere haengen an einer einzigen Zahl: sechs Dokumente rechnen mit einem achtfach falschen Kontextfenster, und ein Verarbeitungsschritt komprimiert verlustbehaftet gegen genau diese Grenze.
- **1. August 2026** — spät Epic „Client WebSocket-Umbau" aus Chat 60 **abgeschlossen** — der SSE-Kanal trägt nur noch die Bestätigung, alle Stufen gehen über den WebSocket; darüber hinaus liegt jetzt eine Eingangs-Queue vor Pfad 1. Zwei Reste benannt, beide in der Fundliste.
- **1. August 2026** — Abschnitt „Charakterbildung messen" ergänzt — der nächste Sprint, mit `PROFIL-HISTORIE-FEHLT` und `PAARLISTE-FEST` als Voraussetzungen.
- **31. Juli 2026** — abends — `HALTUNG-KNOTEN-FEHLT` geschlossen, `HALTUNG-SPANNENENDEN-OFFEN` um die erste Messung am echten Turn ergänzt.
- **31. Juli 2026** — Abschnitt „Haltungsraum — der unterbrochene Sprint" ergänzt — vier Einträge: der fehlende Knoten, das fehlende Protokoll, die offenen Spannenenden und die abzulösende Längenregel.
- **31. Juli 2026** — Abschnitt „Zeitparser und Kalibrierung" ergänzt — vier Einträge aus dem Korpus-Erstlauf und der Neuerhebung der Positions-Kontrolle.
- **31. Juli 2026** — Chat 117, zwei KZG-Einträge gegen den Code nachgezogen. Kern: Chat 111
