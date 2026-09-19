# Novaberg — Memory-Kern: Synapsen-Modell (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) · Ausarbeitung: [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) · Diskussion und Ergänzungen: [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md) · Messungen: [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §8.5 — Wahrnehmungs-Gravitation

Die Mechanik (§8.5 bis §8.5.4) steht in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md), die erste Messung (§8.5.6) in [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md). Der Sprint dazu ist §13.12 unten.

#### 8.5.5 Implementierungs-Status und vorhandene Bausteine

Der Code-Stand zum Zeitpunkt der Konzeption (Chat 87) ist sauber zu benennen, damit der spätere Implementierungs-Sprint nicht von einer Live-Behauptung ausgeht, die nicht stimmt.

**Vorhanden im Live-Code:**

- `state["prompt_embedding"]` als rohes Anfrage-Embedding, geschrieben im Enricher (`enricher.py:201`), durchgereicht über den Dispatcher in den `session_turn_store`. Heute *unverschobene* Variante.
- `state["aktivierte_ziele"]` als `list[dict]` mit Per-Ziel-Feldern `ziel_id`, `ziel_typ`, `zielsatz`, `motivation`, `emotion`, `arousal`, `similarity`, `gravitation`. Befüllt vom Enricher (`enricher.py:271-283`) aus der PostgreSQL-Tabelle `ziele`.
- `memory/ziele.py:ziele_aktive_laden()` liest die Ziele inklusive `embedding`-Spalte aus der DB. Das Embedding wird aktuell aber *nicht* in das State-Dict `aktivierte_ziele[i]` übernommen — es ist zwar geladen, aber im State unsichtbar.
- `ei/gravitation.py:ziel_gravitation_berechnen()` berechnet pro Ziel `gravitation = similarity × motivation` — das ist die Aktivierungs-Stärke, nicht der Cluster-Faktor.
- GV-Cluster in Redis unter `gv:detail:{user_id}:{character_id}` als JSON-Payload, geschrieben vom Dispatcher nach dem GV-Node.
- Salienz-Marker `"anweisung"` in `salienz_obj["intentionen"]`, persistiert im KZG.

**Steht aus für die Implementierung:**

- Per-Ziel-Embedding zusätzlich in das State-Dict `aktivierte_ziele[i]` mit aufnehmen — entweder durch Erweiterung der Mapper-Logik im Enricher, oder über eine eigene Loader-Funktion für die Verschiebungs-Mechanik.
- Cluster-Faktor-Tabelle als neue Konstante (etwa `CLUSTER_GRAVITATION_FAKTOR` in `ei/dreischicht.py`), strukturell parallel zu den fünf bestehenden Cluster-Tabellen.
- Lese-Zugriff im Enricher auf `gv:detail:{user_id}:{character_id}` für den HumanGraph-Fallback.
- Eigene Funktion in `ei/gravitation.py` (oder einer neuen Datei) für die Embedding-Mischung nach der Formel aus 8.5.1.
- Imperativ-Marker-Prüfung: Wenn `"anweisung"` in `state["intentionen"]` (oder vergleichbarem Salienz-Feld) vorhanden, Cluster-Faktor auf 0.0 bis 0.05 dämpfen.
- Empfohlene Umbenennung `aktivierte_ziele[i]["gravitation"]` → `aktivierte_ziele[i]["aktivierungs_staerke"]`. Heute ein einziger Lese-Punkt im Dispatcher betroffen.

Diese Punkte werden in Punkt 9 (Implementierungs-Phasen) als eigene Sprint-Schritte aufgenommen, wenn der Plan steht.

**Erledigt am 02.08.2026 (P10).** Sechs von sechs, mit zwei Abweichungen:

| Offener Punkt | Umsetzung |
|---|---|
| Ziel-Embedding verfügbar machen | in `ActivatedGoal`, **nicht** im State-Dict `aktivierte_ziele` — dort hätte es keinen Leser, und der Dispatcher legt das Dict in Redis ab |
| Cluster-Faktor-Tabelle | `CLUSTER_GRAVITATION_FAKTOR` in `ei/dreischicht.py`, 14 Schlüssel |
| `gv:detail`-Lesezugriff | über das vorhandene `_vorturn_cluster_lesen()`, siehe §8.5.2 |
| Mischfunktion | `ei/gravitation.py:wahrnehmung_verschieben()` |
| Imperativ-Marker-Prüfung | `INTENTION_ANWEISUNG`, Faktor 0.0, siehe §8.5.3 |
| Umbenennung `gravitation` | durchgeführt, und zwar auch am Dataclass-Feld — fünf Fundstellen, eine Quelle |

**Zum Ablageort der Tabelle:** Dieser Abschnitt und `novaberg-memory.md` §11.4 nennen `ei/dreischicht.py`, §13.12 nennt `config.py`. Entschieden für `ei/dreischicht.py` — dort liegen die vier bestehenden Cluster-Tabellen, `config.py` führt Skalare.


---

## 11. Migration und Bestandsdaten

> **Gegenstandslos geworden am 27.07.2026, ausgeführt nie.** Der Abschnitt plante die selektive Übernahme von rund 150 Bestandseinträgen. Bevor es dazu kam, wurde das System auf einen leeren Datenbestand zurückgesetzt (`novaberg-backlog.md`, Stichtag 27.07.2026, 09:13 UTC) — die alte Tabelle stand danach bei null, und es gab nichts mehr zu übernehmen. P9 hat sie am 02.08.2026 gelöscht; das Migrationswerkzeug `tools/migrate_lzg_synapsen.py` ist mit entfernt.
>
> **Die Überlegungen bleiben lesenswert**, weil sie die Unverträglichkeit der beiden Architekturen begründen — und weil dieselbe Frage bei jeder künftigen Modell-Ablösung wiederkommt.

Beim LZG-Umbau entstehen `lzg_knoten` und `lzg_kanten` parallel zum bestehenden `langzeitgedaechtnis`. Die alte Tabelle wird nicht weitergenutzt — sie hat eine andere Architektur (aggregierte Cluster-Einträge), die mit dem Synapsen-Modell strukturell unverträglich ist. Aber die Bestandsdaten der alten Tabelle tragen wertvolle Faktenlage und Erinnerungen, die nicht verloren gehen sollen.

Beschluss aus Chat 86: **selektive manuelle Übernahme, danach alte Tabelle löschen.**

### 11.1 Selektion durch Meister

Heute existieren rund 150 Einträge im `langzeitgedaechtnis`. Aus der Cluster-Promotion sind manche von ihnen semantisch sauber, andere thematisch kontaminiert (z.B. ID 67 mit Anna+Rosa+Grillen-Vermischung — der ursprüngliche Auslöser des Umbaus). Eine grobe Schätzung: rund 120 Einträge sind übernehmenswert, etwa 30 fallen weg. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

Die Selektion macht Meister manuell. Vorteile: klare Hoheit, Einzelfall-Prüfung, kein zusätzlicher LLM-Aufwand. Bei rund 150 Einträgen ist die Hand-Selektion machbar, zumal die problematischen Einträge meist auf einen Blick erkennbar sind (Themen-Mischung, unklare Faktenlage).

Eine LLM-gestützte Vorbewertung wäre denkbar, ist aber bei dieser Datenmenge nicht nötig. Falls sich die Selektion als zeitaufwändig erweist, kann das Konzept jederzeit nachgerüstet werden.

### 11.2 Migrations-Skript

Einmaliges Python-Skript, das die ausgewählten Einträge ins neue Schema migriert. Eingabe ist Meisters Liste der zu übernehmenden Einträge (etwa als JSON oder Python-Liste mit IDs).

**Verarbeitungsschritte:**

1. **Eintrag laden** aus alter Tabelle `langzeitgedaechtnis`.
2. **Magnet-Felder nachrüsten** falls fehlend: `entitaet_ids` über EntityResolver setzen, `timeline_id` über TimeParser ableiten. Alte Einträge haben diese Felder nicht durchgängig befüllt — sie sind aber Voraussetzung für die Kantenbildung im neuen Schema.
3. **Neuen LZG-Knoten anlegen** in `lzg_knoten`. Inhalt, Embedding, Themen, Emotion-Felder werden direkt übernommen. `gewicht_roh`, `gewicht_absolut`, `gewicht_decay` werden auf eine sinnvolle Initial-Stärke gesetzt (z.B. 2.0), `verstaerkt_am` und `decay_am` auf das ursprüngliche `erstellt_am` — damit der Knoten korrekt altert.
4. **Schreibpfad ausführen:** Kandidaten suchen, Schichten prüfen (Entität, Timeline, Themen, Embedding), Kanten zu bereits migrierten Knoten ziehen.
5. **Nächster Eintrag.**

Nach erfolgreichem Durchlauf wird die alte Tabelle `langzeitgedaechtnis` gelöscht. Kein Parallelbetrieb — das neue System ist nach der Migration die einzige Quelle.

### 11.3 Reihenfolge: chronologisch

Die Migration läuft **chronologisch nach `erstellt_am`** der alten Einträge — ältester zuerst, neuester zuletzt. Damit entsteht das Netz in der gleichen Reihenfolge wie das ursprüngliche Erleben.

Phänomenologisch sauber: Annas Geburtstag von vor zwei Jahren ist ein älteres Ereignis als der Werkstatt-Termin von letzter Woche, und die Reihenfolge entspricht dem natürlichen Aufbau des Gedächtnisses. Frühe Knoten dienen als Anker für später entstehende Erinnerungen — analog zum biographischen Aufbau.

Technisch sauber: Jeder neue Knoten kann Kanten zu allen vorher migrierten Knoten ziehen, niemals zu noch nicht migrierten. Die Reihenfolge ist deterministisch, das Ergebnis bei wiederholter Migration identisch. Jeder Knoten behält außerdem sein historisches `erstellt_am` als korrekten biographischen Zeitstempel.

### 11.4 Verlustfreiheit

Die alte `langzeitgedaechtnis`-Tabelle hatte aggregierte Einträge aus mehreren KZG-Quellen. Die KZG-Quellen selbst wurden bei der alten Promotion gelöscht — sie existieren heute nicht mehr und können auch nicht zurückgeholt werden. Migriert wird also das Endergebnis der alten Aggregation, nicht die ursprünglichen Einzeleinträge.

Das ist kein neuer Verlust, sondern der Status quo: Die alte Architektur hat die Quellen verloren, der Umbau nimmt nichts mehr weg, was nicht schon weg war. Phänomenologisch passt das — Meister erlebt eine Erinnerung mit kondensierter Geschichte („Anna hat damals einen Schokoladenkuchen gemacht"), nicht die zehn KZG-Einzeleinträge, aus denen sich das einmal zusammensetzte.

Was bei der Migration aus dem alten ins neue Modell **erhalten** bleibt:

- Inhalt, Embedding, Themen, Emotion
- Erstellzeit (als historischer biographischer Anker)
- Knoten-Identität (jeder alte Eintrag wird genau ein neuer Knoten)

Was **nicht** erhalten bleibt:

- Cluster-Zugehörigkeit der alten Aggregation (gibt es im neuen Modell nicht mehr)
- Die ursprünglichen KZG-Quellen (waren schon vorher gelöscht)
- Häufigkeits-Zähler aus der alten Tabelle (semantisch ambivalent, siehe `LZG-HAEUFIGKEIT-AMBIVALENT` — wird im neuen Schema mit klarer Semantik neu aufgebaut)

---

## 12. Bug- und Backlog-Reset

Der Synapsen-Umbau erledigt eine Reihe offener Bugs und Backlog-Einträge strukturell, weil er die Aggregat-Architektur ersetzt, aus der viele dieser Probleme stammen. Dieser Abschnitt geht durch die existierende Bug-Liste (`novaberg-bugs.md`) und den Backlog (`novaberg-backlog.md`) und ordnet jeden Memory-Kern-relevanten Eintrag einer der drei Kategorien zu: **obsolet** (strukturell gelöst), **bleibt** (unabhängig vom Memory-Kern), **transformiert** (wird im neuen Modell anders ausgedrückt).

### 12.1 Obsolet durch den Umbau

Diese Einträge entfallen mit Abschluss der Synapsen-Migration vollständig. Die zugrunde liegenden Probleme existieren im neuen Modell nicht mehr — entweder weil der betroffene Code-Pfad ersetzt wird oder weil die Datenstruktur die Fehlerklasse strukturell ausschließt.

**Cluster-Promotion-Bugs (Backlog Memory-Promotion-Korrektur, Folge-Themen M4 Teil 2):**

- `PROMO-DESTILL-DEAD` — `_destillation_insert` ohne Aufrufer. Der Code wird komplett neu geschrieben, der tote Pfad entfällt restlos.
- `PROMO-INTENTIONEN-FORMAT-DRIFT` — Einzel- vs. Cluster-Pfad. Es gibt keinen Cluster-Pfad mehr; Intentionen werden nicht mehr aggregiert, sondern pro Knoten eingefroren.
- `PROMO-CLUSTER-EI-UPDATE` — UPDATE-Pfade aktualisieren keine EI-Felder. Keine Cluster-Updates mehr; jeder Knoten ist eigenständig, EI-Felder werden bei der Anlage eingefroren.
- `PROMO-CLUSTER-TIE-DETERMINISM` — Counter-Tie-Break nicht deterministisch. Keine Counter-Aggregation mehr; Klassifikation pro Knoten ist deterministisch durch den Salienz-Knoten.

**Themen-Aggregations-Bugs:**

- `CLUSTER-THEMEN-DEDUP` — semantisch redundante Themen-Strings in Cluster-Promotion. Themen werden nicht mehr aggregiert; pro Knoten eingefroren.
- `CLUSTER-META-CONTAMINATION` — Pipeline-Meta-Begriffe als Themen-Tags. Themen pro Knoten, eingefroren beim Bildungs-Moment, kein Vermischen mehr.

**Aggregations-Datenverluste:**

- `LZG-HAEUFIGKEIT-AMBIVALENT` — `haeufigkeit`-Feld hatte zweideutige Semantik. Im neuen Schema klare Semantik (siehe 4.1, Knoten-Häufigkeit zählt Aktivierungen).
- `KZG-KERN-BLIND` — Verstärkung aktualisierte Scores aber nicht den Kern. Im neuen Modell behält jeder Knoten seinen originalen Kern; Verstärkung wirkt nur auf Stärke-Felder.

### 12.2 Bleibt — unabhängig vom Memory-Kern

Diese Einträge sind orthogonal zum Memory-Kern und werden separat angegangen. Der Synapsen-Umbau berührt sie nicht.

**Responder- und Stil-Bugs:**

- `EMOTE-LOCK` — Emote-Inflation und -Wiederholung
- `TOPOS-LOCK` — Themen-/Bilder-Vorrat wird mechanisch zykeliert
- `HALL2-Reject` — bereits behoben, Referenz für historische Spur

**Recherche-Bugs:**

- `RECH-NO-PERSIST` — Recherche-Resultate verschwinden ungenutzt. Eigenes Konzept (Recherche-Akten oder Knowledge-Graph-Anreicherung) jenseits des Synapsen-Modells.
- `RECH-SPIRAL` — eigene Sprint-Linie

**Zeit-Parser:**

- `ZEIT1` — bereits gefixt (Chat 41), Referenz für historische Spur

**Routing und Classify:**

- `ROUTE-CHAR-NOTIZ` — CharacterGraph-Router dispatched Konversation an NotizenAgent. Trigger-Lücke im Router, kein Memory-Kern-Thema.
- `PENDING-RELEVANZ` — Router prüft nicht, ob neuer Prompt eine Antwort auf Pending-Rückfrage ist
- `MODUS-KALIBRIERUNG` — Perzeption klassifiziert spielerische Inhalte als „emotional"

**Notizen-Bugs (Chat 80):**

- `NOTIZEN-KONTEXT-REKONSTRUKTION`, `NOTIZEN-CONTAINER-WECHSEL`, `NOTIZEN-SKILL-MANIFEST`, `NOTIZEN-UPDATE-TARGET-LEER` — alle vier durch das Frame-Konzept (`novaberg-thinking-frames_k.md`) adressiert, nicht durch den Memory-Kern.

**Paar-Schema-Migrationen (Chat 80):**

- `TIMELINE-PAIR-MISSING`, `NOTIZEN-PAIR-MISSING`, `FAKTEN-PAIR-IGNORED`, `ZIELE-PAIR-MISSING` — alle vier unabhängige Migrations-Lücken, eigener Sprint im Backlog.

### 12.3 Transformiert

Diese Einträge werden im neuen Modell anders ausgedrückt oder rücken in einen anderen Konzeptbereich.

**`KZG-DEDUP` — Deduplizierung semantisch ähnlicher KZG-Einträge.**
In Chat 64 als Feature re-framed. Im Synapsen-Modell ist es definitiv ein Feature: Verschiedene Facetten desselben Themas werden als eigenständige Knoten behalten. Die Spreading-Activation im Lesepfad (Punkt 8) verbindet sie über Kanten, statt sie zu verdichten. Der Bug-Eintrag ist damit endgültig kein Bug mehr.

**`CHAR-HASH-FILTER` — `beobachter=assistant`-Einträge im Charakter-Hash.**
Aktueller Bug-Stand ist „behoben". Im neuen Modell läuft die Charakter-Hash-Destillation auf der Synapsen-Topologie (außerhalb des LZG-Kerns, bei Pixie verortet). Das Filter-Pattern wandert dorthin und wird im Pixie-Konzept ausgearbeitet.

**`PROMO-DROP1` — KZG-Felder werden bei Promotion stillschweigend verworfen.**
Teilweise behoben Chat 84 (M3a). Die noch offenen Felder (`entitaet_ids`, `timeline_id`) waren auf M5 blockiert. Im Synapsen-Modell sind diese Felder Voraussetzung für die Kantenbildung — sie werden im KZG-Schreibpfad nachgerüstet (Punkt 9, P3 in der Implementierungs-Phase).

**`PROMO-FAKT-LEER` — Fakt-klassifizierte Einträge ohne Fakten fallen aus dem LZG-Schreib-Pfad.**
Im Synapsen-Modell wird jeder reife KZG-Eintrag zu einem LZG-Knoten, unabhängig von der `gedaechtnistyp`-Klassifikation. Der spezielle Fakten-Pfad entfällt. Architektonische Frage damit gelöst — fakt-klassifizierte Einträge werden gleichberechtigt zu Knoten.

**`Memory-Promotion-Korrektur` (Epic, Chat 75).**
Das vorherige Epic wird durch das Synapsen-Konzept ersetzt. Phasen-Status:
- M1, M2, M3a, M4 Teil 1, M4 Teil 2, M5a — bereits erledigt, gelten weiter
- M3b — wird Teil des Synapsen-Schreibpfads (Punkt 7 des Konzepts), wandert in die Implementierungs-Phasen
- M5b (FaktenManager-Reaktivierung) — separat, hängt nicht direkt am Synapsen-Umbau
- M5c (Themen-Cluster-Promotion smarter) — strukturell obsolet, weil keine Themen-Cluster mehr aggregiert werden

**`Kognitive Anreicherung` (Backlog Epic 8) — CEM, TE, ZE, VRE, MR.**
Alle fünf Effekte sind erhaltenswert, müssen aber auf die neue Topologie übertragen werden:
- CEM (Curiosity-Enhanced Memory) — Salienz-Boost bei Entitäts-Nähe, weiterhin im Salienz-Knoten, keine Memory-Kern-Änderung
- TE (Testing Effect / Retrieval Practice) — ~~heute schreibt der Enricher abgerufene LZG-IDs in Redis, Pixie verstärkt sie~~ **[Überholt, gemessen 04.09.2026: Dieser Pfad existiert im Code nicht mehr** — `knoten_verstaerken` hat genau einen Aufrufer (die Promotion), und kein Lesepfad schreibt Verstärkungen. Der beschriebene Konflikt mit dem Leitprinzip hat sich aufgelöst, ohne dass es jemand festhielt. **Und der Testing Effect ist seit dem 04.09.2026 regelkonform gebaut:** Die Verwendungs-Verstärkung (§7.1a) verstärkt genau die abgerufenen Erinnerungen, die die Antwort hergenommen hat — Retrieval Practice mit aktivem Anstoß statt Aktivierung durch Lesen.]**
- ZE (Zeigarnik-Effekt) — Arousal auf Entitäten, kein direkter Memory-Kern-Bezug
- VRE (Von-Restorff-Effekt) — Salienz-Boost bei Kontrast, im Salienz-Knoten
- MR (Memory Reconsolidation) — Widerspruchs-Erkennung und Decay-bei-Widerspruch. Im Synapsen-Modell läuft das anders: Ein neuer Knoten mit Widerspruch zu einem alten Knoten *bildet seine eigenen Kanten*, der alte Knoten verfällt einfach durch das normale Decay. Mechanismus ist phänomenologisch näher am menschlichen Erinnern. Aktuelle Implementierung im PromotionAgent wird durch den Synapsen-Umbau ersetzt.

**`Entity-First-Retrieval` (Backlog Epic 16).**
Im Synapsen-Modell partial enthalten: Entität-Schicht ist eine der vier Schichten zur Kantenbildung. Die ursprüngliche Idee „Entität gewinnt vor Embedding" wird im Schicht-Faktor abgebildet (Entität 1.0, Embedding 0.8, siehe Punkt 7.4). Das vollständige Entity-First-Retrieval mit Knowledge-Graph-Traversal kommt mit dem Faktengedächtnis-Konzept (siehe 3.2).

**`META-KOGNITION` (Backlog Epic).**
Pipeline-Log ist Teil des LZG-Kernumbaus (Punkt 10). Vorsätze, Selbstbeobachtung und Reflexion bleiben eigenes Konzept und setzen auf das Pipeline-Log auf.

### 12.4 Konsequenzen für die Bug-Liste

Nach Abschluss des Synapsen-Umbaus werden in `novaberg-bugs.md` die Einträge aus 12.1 (obsolet) als gelöst markiert, mit Verweis auf das Synapsen-Konzept. Die Einträge aus 12.3 (transformiert) werden präzisiert oder in andere Konzepte verschoben. Die Einträge aus 12.2 (bleibt) bleiben unverändert.

Im `novaberg-backlog.md` wird das Epic `Memory-Kern-Umbau (Synapsen-Modell, Chat 86)` von „Konzept-Phase" auf „in Umsetzung" gesetzt, sobald der Brudi-Plan startet. Das ältere Epic `Memory-Promotion-Korrektur (Chat 75)` wird mit dem Vermerk geschlossen, dass die offenen Phasen M3b und M5c im Synapsen-Umbau aufgehen.

---

---

## 13. Implementierungs-Phasen

> **Stand 02.08.2026 (Chat 126): Alle zehn Sprints sind gebaut.**
>
> | Sprint | Stand | Belegt durch |
> |---|---|---|
> | P1 Pipeline-Log | ✅ | 34.832 Zeilen |
> | P2 Tabellen | ✅ | angelegt und gefüllt |
> | P3 Magnetfelder | 🔶 | themen 99 %, `entitaet_ids` 31 %, `timeline_id` 2,6 % — siehe Kopf |
> | P4 Neue Promotion | ✅ | `SynapsenPromotionAgent`, 1108 Knoten |
> | P5 Enricher liest neu | ✅ | `spreading_lesen` |
> | P6 Decay | ✅ | `SynapsenDecayAgent` materialisiert `gewicht_decay` |
> | P7 Charakter-Hash | ✅ | liest `lzg_knoten` |
> | P8 Migration | ✅ | gegenstandslos, siehe §11 |
> | P9 Codeschloss | ✅ | Tabelle gelöscht, 2172 Zeilen entfernt |
> | P10 Wahrnehmungs-Gravitation | ✅ | `wahrnehmung_verschieben`, live gemessen — **Wirkung offen, siehe §8.5.6** |
>
> **Die Sprint-Beschreibungen unten bleiben unverändert.** Sie sind die Absicht von damals und der Maßstab, an dem sich messen lässt, was daraus wurde — nicht der Zustand. Zwei Abweichungen sind beim Bauen von P9 aufgefallen und dort vermerkt: `agents/timeline/init.sql` legte die alte Tabelle bei jedem Serverstart neu an, und das in §13.11 zu entfernende Flag `SYNAPSEN_LESEPFAD_AKTIV` wurde nie gebaut. Drei weitere aus P10 stehen in §8.5.2, §8.5.3 und §13.12.


Der Synapsen-Umbau wird in zehn Sprints (P1 bis P10) umgesetzt. Jeder Sprint ist eine in sich abgeschlossene Lieferung, die für sich genommen funktioniert und vorzeigbar ist. Kein Sprint hinterlässt einen nicht-funktionierenden Zwischenzustand über seinen eigenen Lauf hinaus.

### 13.1 Leitprinzipien der Reihenfolge

**Additives vor Subtraktivem.** Die ersten acht Sprints (P1–P8) bauen das neue System parallel zum alten auf. Erst P9 entfernt die abgelöste Infrastruktur. Damit ist bis zum Codeschloss jederzeit ein Rollback möglich.

**Beobachten vor Eingreifen.** P1 (Pipeline-Log) steht ganz vorne, damit alle folgenden Sprints von Anfang an instrumentiert sind. Forensik ist Voraussetzung für jeden weiteren Schritt.

**Schreibpfad vor Lesepfad.** P4 (neue Promotion) füllt die neuen Tabellen, bevor P5 den Enricher umschaltet. Damit liest der Enricher nicht ins Leere.

**Cold-Start akzeptiert.** Zwischen P5 (Enricher liest neu) und P8 (Bestandsdaten migriert) lebt Nova mit einem dünneren Netz — nur die in der Zwischenzeit neu promotierten Erinnerungen sind verfügbar. Bewusste Designentscheidung: die alten Bestandsdaten dürfen erst dann ins neue Netz, wenn Magnet-Felder (P3), Promotion-Logik (P4) und Lesepfad (P5) stabil laufen.

**Funktional schließen, dann säubern.** P9 (altes LZG löschen, alte Promotion entfernen) kommt erst, wenn P5 bis P8 nachweislich stabil im Live-Betrieb laufen. P9 ist das Codeschloss. Mindest-Beobachtungszeit zwischen P8 und P9: eine Woche aktiver Nutzung ohne kritische Befunde im Pipeline-Log.

**Orthogonales als eigenes Stück.** P10 (Wahrnehmungs-Gravitation) ist mechanisch unabhängig vom Synapsen-Umbau. Sie betrifft die Embedding-Verschiebung im Enricher vor der pgvector-Suche, ist als eigenes Mini-Epic geschnitten und kommt ans Ende, weil sie auf einem ausgereiften neuen Lesepfad aufsetzt.

### 13.2 Zwei Stufen der Sprint-Definition

Die folgenden Abschnitte (13.3 bis 13.12) sind **Stufe 1** der Sprint-Definition: pro Phase Ziel, Abgrenzung, Voraussetzungen, Datei-Scopes und Abnahme-Tests. Sie geben das Gesamtbild — was sich ändert, was nicht, woran abgemessen wird.

**Stufe 2** ist der ausformulierte Brudi-Prompt pro Sprint. Diese entstehen *just in time*, jeweils direkt vor Sprint-Start, nicht im Voraus alle auf einmal. Begründung: zwischen den Sprints können Code-Stand und Erkenntnisse verschieben, was im konkreten Prompt steht. Stufe 1 ist die feste Architektur-Vorgabe; Stufe 2 ist die konkrete Anweisung zum konkreten Code-Stand des Tages.

**Hinweis zu Datei-Pfaden in dieser Stufe.** Die in den Datei-Scopes genannten Pfade sind die nach aktueller Code-Lage erwarteten Stellen. Bei jedem Sprint verifiziert Brudi die tatsächliche Lage im Repository, bevor editiert wird — falls eine Datei umgezogen ist oder anders heißt, gilt die tatsächliche Konvention. Stufe-2-Prompts spezifizieren die exakten Pfade auf Basis dieser Verifikation.

### 13.3 P1 — Pipeline-Log einführen

**Ziel.** Schreib-Infrastruktur für die `pipeline_log`-Tabelle aufsetzen: Buffer-Sink, asynchroner Writer-Task, Helper-API für die Nodes. Erste Anbindung im Enricher als Demonstrationspunkt. Vollständig additiv, kein Bestandscode wird semantisch verändert.

**Abgrenzung.** Keine vollständige Verkabelung aller Nodes in diesem Sprint. Die Anbindung in jedem Node erfolgt peu à peu *in der jeweiligen späteren Phase, die diesen Node ohnehin anfasst* — als Konvention, nicht als eigener Sprint. Konkret: P4 verkabelt die neue Promotion, P5 den Lesepfad-Teil des Enrichers, P6 den Decay-Job. Das nachträgliche Aufrüsten weiterer Nodes (Responder, Tribunal, Corrector, Agenten) ist Refactor-Arbeit nach P9 und liegt außerhalb des Synapsen-Umbau-Scopes. Keine Filter-Queries als ausführbare Tools — Konzept-Punkt 10.4 dokumentiert sie als Vorlagen für spätere Debug-Sitzungen. Kein eigener TTL-Cleanup-Job in dieser Phase; der Cleanup wird in P6 als kleiner Anhang am Decay-Job mit angelegt. Kein `bemerkung`-für-Client-Status-Texte-Feature in P1 — eigener Konzept-Pfad später.

**Voraussetzungen.** Konzept-Punkt 10 ist die vollständige Spezifikation: Schema, elf Art-Werte, Span-Korrelation, asynchrones Schreiben, Konstanten. Keine fachlichen Vorgänger-Phasen.

**Datei-Scopes.**

*Neu anlegen:*

- `server/memory/pipeline_log.py` — Thread-safe Buffer-Sink-Klasse, asynchroner Writer-Task, Helper-API mit elf Einstiegsfunktionen (`log_eingang`, `log_prompt`, `log_berechnung`, `log_switch`, `log_db_zugriff`, `log_ausgabe`, `log_fehler`, `log_bemerkung`, `span_start`, `span_end`, `log_token`). Jede Funktion mit deutschem Docstring und Log-Nachricht bei nennenswerten Werten.
- Datenbank-Migration mit der Tabellen-DDL aus Konzept-Punkt 10.1, inklusive Indizes auf `turn_id`, `span_id`, `(node, art)` und `erstellt_am`. Brudi verifiziert den im Repository üblichen Migrations-Mechanismus (Alembic, raw SQL, init-Skript) und legt die Migration in der dort etablierten Konvention an.

*Ergänzen:*

- `server/config.py` — zwei Konstanten `LZG_PIPELINE_LOG_VORHALTUNG_TAGE = 365` und `LZG_PIPELINE_LOG_FLUSH_SEKUNDEN = 10`, mit ausführlichem deutschem Doc-Kommentar im Stil der bestehenden Knoten-Dynamik-Konstanten.
- Zentrale Server-Lifecycle-Datei (Brudi verifiziert: vermutlich `server/main.py` oder die FastAPI-App-Definition) — Writer-Task beim Server-Start als Hintergrund-Task anhängen, beim Shutdown sauberen Flush sicherstellen.
- `server/graph/nodes/enricher.py` — drei bis fünf Pipeline-Log-Einträge an markanten Stellen (Eingang, Initial-Retrieval-Berechnung, Ausgang) als laufende Demonstration der API.

*Tabu in diesem Sprint:* Alle anderen Node-Dateien, alle anderen Memory-Dateien, alle Pixie-Agenten. Insbesondere keine Vorgriffe auf P2 — die neuen LZG-Tabellen kommen erst im nächsten Sprint.

**Abnahme-Tests.**

1. Server startet sauber. Writer-Task läuft als Hintergrund-Task. Server-Shutdown flusht den Puffer vollständig — keine pending Einträge nach Stop.
2. Nach einem normalen Konversations-Turn enthält `pipeline_log` mindestens drei Einträge aus dem Enricher mit korrekt gesetzter `turn_id`, einer pro-Lauf eindeutigen `span_id` (UUID v4), `node='enricher'`, plausibler `quelle`, einem der elf gültigen `art`-Werte und gültigem JSONB-`inhalt`.
3. Zwei simulierte Pixie-Tasks, die parallel laufen, erzeugen Einträge mit jeweils eindeutigen `span_id`s — keine vermischten Spans, kein Index-Konflikt, kein Race-Condition-Schaden.
4. Buffer-Verlust-Test: bewusster Server-Kill direkt nach einem Eintrag; nach Restart sind die bereits geflushten Einträge in der DB, der jüngste 10-Sekunden-Inhalt möglicherweise verloren — als bewusste Designentscheidung gemäß 10.3 akzeptiert.
5. Beispiel-Query 1 aus Konzept-Punkt 10.4 (letzte fünf Turns von Nova) liefert plausible Ergebnisse, sobald in der Demo-Anbindung ein paar Nova-Antworten gelaufen sind.

### 13.4 P2 — Neue Tabellen `lzg_knoten` und `lzg_kanten` anlegen

**Ziel.** Schema-Migration mit den beiden neuen Tabellen aus Konzept-Punkt 4. Leer, parallel zur bestehenden `langzeitgedaechtnis`-Tabelle. Keine Logik dahinter — reine Strukturanlage als Vorbereitung für P3 und P4.

**Abgrenzung.** Keine Schreib-Logik, kein Lese-Code. Keine Promotion-Anpassung — die kommt in P4. Bestehende `langzeitgedaechtnis`-Tabelle bleibt vollständig unangetastet. Keine Indizes über das Minimum hinaus (Primary Key, Foreign Keys, pgvector-Index auf Embedding) — Performance-Tuning kommt nach Live-Daten, spätestens nach P9. Konstanten in `config.py` werden in diesem Sprint ergänzt, soweit für das Schema relevant; bereits in P1 angelegte Konstanten werden nicht angefasst.

**Voraussetzungen.** P1 abgeschlossen. Konzept-Punkt 4 ist die vollständige Schema-Spezifikation (Spalten, Typen, Indizes). Konzept-Punkt 6 listet die Konstanten.

**Datei-Scopes.**

*Neu anlegen:* Datenbank-Migration mit den beiden Tabellen-DDLs gemäß Konzept 4.1 und 4.2. Inklusive pgvector-Index auf `lzg_knoten.embedding`. Inklusive Foreign Keys auf `lzg_knoten.id` von `lzg_kanten.knoten_a_id` und `lzg_kanten.knoten_b_id`. Migrations-Mechanismus wie in P1 etabliert.

*Ergänzen:* `server/config.py` mit allen noch nicht vorhandenen Konstanten aus Konzept-Punkt 6 (Knoten-Dynamik, Kanten-Cache-Parameter, Sinus-Geometrie, Schicht-Faktoren, Tiefe-Faktor-Parameter). Jede Konstante mit dem im Konzept dokumentierten deutschen Doc-Kommentar.

*Tabu:* Jede `*.py`-Datei außerhalb `server/config.py`. Insbesondere keine Helper-Funktionen zum Schreiben oder Lesen — das ist nicht Scope dieses Sprints.

**Abnahme-Tests.**

1. Migration läuft sauber durch, auch wiederholt — idempotenter Upgrade-Pfad. Downgrade läuft ebenfalls sauber.
2. `\d lzg_knoten` und `\d lzg_kanten` in psql zeigen das Schema exakt wie in Konzept 4.1 und 4.2 beschrieben.
3. `langzeitgedaechtnis`-Tabelle bleibt unverändert. `SELECT count(*) FROM langzeitgedaechtnis` liefert den gleichen Wert wie vor der Migration.
4. Server startet sauber, alle Konstanten aus Konzept-Punkt 6 sind in `config.py` importierbar.
5. Ein Test-Insert eines Dummy-Knotens (`INSERT INTO lzg_knoten ... RETURNING id`) und einer Dummy-Kante zwischen zwei Dummy-Knoten läuft technisch durch.

### 13.5 P3 — KZG-Schreibpfad ergänzt um `entitaet_ids` und `timeline_id`

**Ziel.** Beim Schreiben eines KZG-Eintrags werden ab dieser Phase die Magnet-Felder `entitaet_ids` und `timeline_id` mit befüllt. Ohne diese Felder kann die Promotion in P4 die Entitäts- und Timeline-Schichten nicht greifen lassen. Inhaltsgleich mit der vormaligen M5-Roadmap-Position, in den Synapsen-Sprint integriert.

**Abgrenzung.** Keine Änderung an der Promotion-Logik selbst — die kommt in P4. Keine Migration der bestehenden KZG-Einträge in Redis; nur neu entstehende Einträge tragen die Felder. EntityResolver und TimelineRepository werden nur als bestehende Tools genutzt, nicht erweitert. Salience-Prompt wird um zwei Roh-Dimensionen erweitert; die Resolution selbst geschieht in einem neuen Node im KzgAgent-Subgraphen.

**Voraussetzungen.** P1 und P2 abgeschlossen. Salience liefert die Roh-Erkennungen als Strings (`entitaeten_roh`, `zeitausdruck_roh`). EntityResolutionService (`memory/services/entity_resolution.py`) und TimelineRepository (`memory/repositories/timeline_repository.py`) sind im Live-Code vorhanden und werden vom neuen Node direkt aufgerufen.

**Architektur.** Drei-Stufen-Pipeline:

1. **Salience-Erweiterung** — Prompt `prompts/default/salienz.task.txt` bekommt zwei neue Dimensionen: `entitaeten_roh` (Liste von Eigennamen, Pronomen ausgeschlossen) und `zeitausdruck_roh` (ein Zeitausdruck pro Segment). Beides als Roh-Strings, keine Resolution im Salience-Node.

2. **Neuer Node `magnete_aufloesen`** in `server/agents/kzg/magnete.py` — sitzt im KzgAgent-Subgraph zwischen `schwelle_pruefen` und `verdichten` (defensiv: Resolver-Fehler verwerfen den teuren LLM-Call nicht). Entitäten-Pfad via `EntityResolutionService.resolve_batch` plus `create_new_entity` für neue Namen (analog zum bestehenden FaktenManager-Pattern). Timeline-Pfad via `zeit_parsen_vektor` und `TimelineRepository.find_by_date`/`insert` mit `event_type='erinnerungs_anker'` (Klasse Bezug nach `convention-magneten.md` §5).

3. **Clipboard-Pattern** (Regel seit 16.08.2026 in `novaberg-convention-planner-needs.md` §3) — der `TimelineAgent` schreibt eine im selben Turn angelegte `timeline_id` via `dispatch_timeline._build_return` flach in den `ConversationState` (`state["timeline_id"]`). Der `magnete_aufloesen`-Node übernimmt diesen Wert, wenn vorhanden, statt einen eigenen Erinnerungs-Anker für den gleichen Tag anzulegen.

**Datei-Scopes.**

*Ergänzen:*

- `server/prompts/default/salienz.task.txt` — zwei neue Dimensionen (`entitaeten_roh`, `zeitausdruck_roh`) plus JSON-Schema-Erweiterung.
- `server/graph/nodes/salience.py` — defensives Normalisieren der neuen Roh-Felder.
- `server/graph/state.py` (plus `base.py`, `builder.py`) — neuer flacher State-Key `timeline_id: int | None` als Clipboard.
- `server/agents/kzg/magnete.py` (NEU) — Node `magnete_aufloesen`.
- `server/agents/kzg/agent.py` — Subgraph-Topologie: neuer Node zwischen `schwelle_pruefen` und `verdichten`.
- `server/agents/kzg/dispatch.py` — `kontext` um `turn_id` und `timeline_id`-Clipboard erweitert.
- `server/agents/kzg/speicher.py` (`_neu_anlegen`) und `server/memory/kzg.py` (`kzg_store`) — optionale Parameter `entitaet_ids`, `timeline_id`, `turn_id`. Redis-Serialisierung: `entitaet_ids` als kommagetrennter String (TAG-Feld), `timeline_id` als Numeric — bei `None` aus dem `mapping=` ausgelassen.
- `server/memory/kzg.py` + `server/agents/kzg/speicher.py` — Pipeline-Log-Eintrag (`art='db_zugriff'`) nach erfolgreichem `rc.hset()`.
- `server/agents/timeline/dispatch.py` — `_build_return` schreibt `state["timeline_id"]` ins Clipboard.
- `server/agents/timeline/magneten.py` — neuer `event_type='erinnerungs_anker'`: `EVENT_TYPES_ERINNERUNGS_ANKER`, Flags (False, False, False), `themen_aus_event_type` liefert leere Liste.

*Tabu:* `EntityResolutionService` und `TimelineRepository` werden nur konsumiert, nicht erweitert. Alle LZG-Dateien (`memory/lzg.py`, `lzg_knoten`/`lzg_kanten`), alle Promotion-Dateien. Salience-Logik ausserhalb des Prompts und des defensive Parsing.

**Abnahme-Tests.**

1. Ein normaler Konversations-Turn, der zu einem KZG-Eintrag führt, erzeugt in Redis einen Eintrag mit befüllten Feldern `entitaet_ids` und `timeline_id`. Inhalt der Felder ist plausibel — Entitäts-IDs sind Integers, die in der `entitaeten`-Tabelle existieren; Timeline-ID ist ein Integer, der in der `timeline`-Tabelle existiert (event_type=`erinnerungs_anker`).
2. Ein Turn ohne erkannte Entitäten erzeugt einen KZG-Eintrag mit `entitaet_ids` als leerem String im Hash (TAG-Feld, kommagetrennt — leerer String entspricht „keine Tags"), kein Fehler.
3. Ein Turn ohne erkannte Zeit erzeugt einen KZG-Eintrag ohne `timeline_id`-Feld im Hash (das Feld wird aus dem `mapping=` ausgelassen, weil NumericField sich am leeren String verschluckt), kein Fehler.
4. Ein Turn, in dem der TimelineAgent zuvor einen Eintrag angelegt hat (z.B. „Merk dir den 17.10. als Annas Geburtstag"), erzeugt einen KZG-Eintrag mit `timeline_id = <dieselbe ID>` — kein doppelter `erinnerungs_anker` für denselben Tag.
5. Pipeline-Log enthält einen Eintrag des Schreibvorgangs (`art='db_zugriff'`, `node='kzg_speicher'`, `quelle=user_id`) mit `entitaet_ids` und `timeline_id` im JSONB-`inhalt`.
6. Bestehende KZG-Einträge in Redis sind unverändert — keine Migration, keine Re-Indexierung.

### 13.6 P4 — Neue Promotion-Logik schreibt in `lzg_knoten` und `lzg_kanten`

**Ziel.** Die Promotion eines KZG-Eintrags in den LZG wird vollständig auf das Synapsen-Modell umgestellt. Neue Logik schreibt `lzg_knoten` und berechnet beim Anlegen die Kanten gegen alle bereits vorhandenen Knoten gemäß Konzept-Punkt 7 (Schreibpfad-Sicht). Bisherige Cluster-Promotion in `langzeitgedaechtnis` wird über ein Feature-Flag deaktiviert, der Code bleibt bis P9 im Repository.

**Abgrenzung.** Bestehender Lesepfad bleibt unverändert auf der alten `langzeitgedaechtnis`-Tabelle — der Schalter wird erst in P5 umgelegt. Cluster-Algorithmus (Greedy-Center, Multi-Membership, LLM-Coherence-Validation) entfällt vollständig in dieser Phase — kein KZG-Eintrag durchläuft mehr die Cluster-Pipeline. Stattdessen direkter 1:1-Umzug eines reifen KZG-Eintrags in einen `lzg_knoten`. KZG-Eintrag wird nach erfolgreicher Promotion vollständig aus Redis gelöscht (Konzept 2.5). Bestehende Einträge in `langzeitgedaechtnis` bleiben unverändert.

**Voraussetzungen.** P1, P2, P3 abgeschlossen. Konzept-Punkt 7 ist die vollständige Spezifikation des Schreibpfads (Schicht-Auslösung, Stärke-Berechnung, Sinus-Geometrie, Timeline-Details, drei Trigger für Kanten-Cache-Aktualisierung). Konzept-Punkt 5 spezifiziert die Sinus-Geometrie. Konzept-Punkt 6 listet alle Konstanten.

**Datei-Scopes.**

*Neu anlegen:*

- `server/memory/lzg_knoten.py` — CRUD-Layer für die Knoten-Tabelle, mit Schreib-, Lese-, Aktualisierungs- und Such-Funktionen. Deutscher Docstring pro Funktion, Log-Nachrichten bei Schreib- und Lese-Operationen mit Knoten-IDs und Gewichtswerten.
- `server/memory/lzg_kanten.py` — CRUD-Layer für die Kanten-Tabelle, plus die Kanten-Berechnungs-Logik gemäß Konzept 7.5 (Schicht-Auslösung, Sinus-Geometrie, Tiefe-Faktor-Interpolation).
- Neuer Pixie-Agent für die Synapsen-Promotion (Brudi verifiziert die Pixie-Agent-Konvention im Repository; vermutlich `server/pixie/agents/synapsen_promotion.py`). Der Agent implementiert den 1:1-Umzugs-Pfad: KZG-Eintrag laden, Reifeprüfung, `lzg_knoten` schreiben, Kanten gegen alle bestehenden Knoten berechnen, KZG-Eintrag löschen.

*Ergänzen:* Pipeline-Log-Einträge an allen Entscheidungs-Stellen der neuen Promotion (`art='switch'` bei Reifeprüfung, `art='berechnung'` bei Sinus-Werten und Kanten-Stärken, `art='db_zugriff'` bei den Inserts, `art='ausgabe'` am Ende).

*Stilllegen, nicht löschen:* Die bisherige Cluster-Promotion (Brudi lokalisiert den genauen Pfad — vermutlich `server/pixie/agents/promotion.py` oder ähnlich). Stilllegung über Feature-Flag in `config.py` (`SYNAPSEN_PROMOTION_AKTIV = True`). Der alte Code bleibt im Repository, wird aber nicht mehr ausgeführt. Vollständige Löschung kommt in P9.

*Tabu:* Lesepfad (Enricher, Reducer, Responder). Decay-Logik. Charakter-Hash. Migration der Bestandsdaten — die kommt in P8.

**Abnahme-Tests.**

1. Ein reifer KZG-Eintrag wird vom neuen Pixie-Agenten verarbeitet, erzeugt einen Eintrag in `lzg_knoten` mit korrektem `gewicht_roh`, `gewicht_absolut`, `gewicht_decay`, allen Magnet-Feldern, dem Embedding und der Emotion. Der KZG-Eintrag ist anschließend aus Redis gelöscht.
2. Bei einem zweiten reifen KZG-Eintrag, der inhaltlich verwandt zum ersten ist (gemeinsame Themen oder hohe Embedding-Ähnlichkeit), entstehen automatisch Kanten zwischen beiden Knoten. Kanten-Stärken sind nach Konzept 7.5 berechnet — eine Sinus-Berechnung pro Kante, korrekter Schicht-Faktor und Tiefe-Faktor.
3. Drei durchgerechnete Beispiele aus Konzept 7.5 (Timeline-only, Timeline + Embedding, Entität-only) werden als Unit-Test reproduziert; die berechneten Kanten-Stärken stimmen mit den im Konzept dokumentierten Zahlen überein.
4. Bei deaktiviertem Feature-Flag (`SYNAPSEN_PROMOTION_AKTIV = False`) läuft die alte Cluster-Promotion wie vorher; bei aktiviertem Flag läuft nur die neue Promotion. Klare Reload-Anweisung dokumentiert (Server-Restart oder Konfigurations-Reload — was im Repository üblich ist).
5. Pipeline-Log zeigt für jeden Promotions-Vorgang einen kompletten Span mit allen Entscheidungs-Schritten und berechneten Werten.
6. Bestehende `langzeitgedaechtnis`-Einträge sind unverändert — die alte Tabelle wird in dieser Phase weder geschrieben noch gelesen.

### 13.7 P5 — Enricher liest aus `lzg_knoten` und `lzg_kanten`

**Ziel.** Der Enricher schaltet von der alten `langzeitgedaechtnis`-Tabelle auf die neuen Tabellen um. Initial-Retrieval (pgvector-Cosine auf `lzg_knoten`), Spreading-Activation entlang `lzg_kanten`, Sortierung nach Sortier-Gewicht. Cold-Start: das neue Netz ist zu diesem Zeitpunkt nur mit den seit P4 neu promotierten Knoten gefüllt — Bestandsdaten kommen erst in P8.

**Abgrenzung.** Reducer-Anbindung wird in dieser Phase angepasst, soweit nötig: Der Enricher legt `state["lzg_resonanz"]` als Rohdaten-Liste ab (Konzept 8.4.2), der Reducer integriert sie mit anderen Memory-Quellen. Reducer-eigene Logik nur insoweit erweitert, wie die neue State-Struktur es erzwingt. Decay-Lauf wird in dieser Phase noch nicht aktiv — `gewicht_decay` wird zwar gelesen, aber noch nicht von einem Pixie-Job aktualisiert. Wahrnehmungs-Gravitation bleibt unberührt — das ist P10.

**Voraussetzungen.** P1, P2, P3, P4 abgeschlossen. Konzept-Punkt 8 ist die vollständige Spezifikation des Lesepfads (Initial-Retrieval, Spreading-Activation, Sortierung, Output-Format).

**Datei-Scopes.**

*Anpassen:*

- `server/graph/nodes/enricher.py` — Initial-Retrieval auf `lzg_knoten`, Spreading-Activation entlang `lzg_kanten`, Sortier-Gewicht-Berechnung, State-Struktur `lzg_resonanz` gemäß Konzept 8.4.2. Cluster-abhängige Sprung-Tiefe gemäß Konzept 8.2.1 (neue Konstante `CLUSTER_ENRICHER_SPRUENGE` aus `config.py`).
- Reducer (Brudi verifiziert den genauen Pfad — vermutlich ein eigener Node zwischen GV und Responder) — Konsumption der neuen Rohdaten-Struktur, Dedup gegen andere Memory-Quellen, Aufbau des `[GEDAECHTNIS]`-Prompt-Blocks gemäß Konzept 8.4.4. Behält bisherige Logik bei, soweit sie weiterhin gilt; ersetzt sie, wo die neue State-Struktur abweicht.
- `server/config.py` — Konstante `CLUSTER_ENRICHER_SPRUENGE` als Dict pro Cluster gemäß Konzept 8.2.1, mit ausführlichem deutschem Doc-Kommentar.

*Ergänzen:* Pipeline-Log-Einträge im Enricher an Initial-Retrieval, Spreading-Activation und Sortier-Schritt.

*Stilllegen, nicht löschen:* Der alte Lesepfad auf `langzeitgedaechtnis` bleibt im Code-Repository erhalten, wird aber nicht mehr ausgeführt. Feature-Flag `SYNAPSEN_LESEPFAD_AKTIV` in `config.py`. Vollständige Löschung kommt in P9.

*Tabu:* Promotion-Logik (steht aus P4). Decay-Lauf (kommt in P6). Charakter-Hash. Migration. Wahrnehmungs-Gravitation.

**Abnahme-Tests.**

1. Bei aktiviertem Feature-Flag liest der Enricher exklusiv aus `lzg_knoten` und `lzg_kanten`. Bei deaktiviertem Flag bleibt der alte Pfad aktiv.
2. Ein Konversations-Turn, dessen Embedding einen pgvector-Cosine-Treffer in `lzg_knoten` hat, liefert Initial-Anker und Spreading-Activation-Pool. Sprung-Tiefe entspricht dem aktuellen Cluster gemäß `CLUSTER_ENRICHER_SPRUENGE`.
3. Sortier-Gewicht-Berechnung (Konzept 8.3.1) wird korrekt angewendet: `knoten.gewicht_decay × schalen_faktor × sektor_faktor`. Dedup mit Schalen-Präferenz funktioniert.
4. Vorgänger-Sperre (Konzept 8.2.3) verhindert sofortiges Zurückspringen zum direkten Vorgänger; Zyklen werden am Ende durch Dedup aufgelöst.
5. Bei leerem Netz (keine `lzg_knoten` vorhanden) liefert der Enricher eine leere `lzg_resonanz`-Liste ohne Fehler. Cold-Start-Verhalten ist sauber.
6. Reducer integriert die neue State-Struktur korrekt in den `[GEDAECHTNIS]`-Block; Beispiel-Prompt-Block aus Konzept 8.4.4 ist als Vergleichs-Anker nutzbar.
7. Pipeline-Log zeigt den vollständigen Lesepfad als Span mit allen Zwischenergebnissen.

### 13.8 P6 — Decay-Lauf für `lzg_knoten`

**Ziel.** Täglicher Pixie-Job berechnet das `gewicht_decay`-Feld aller aktiven Knoten neu gemäß Konzept-Punkt 9 (Drei Stärke-Felder, Berechnungsschema, Halbreaktivierung). Knoten, die unter `LZG_KNOTEN_MIN_GEWICHT` fallen, werden auf `aktiv = FALSE` gesetzt. TTL-Cleanup des Pipeline-Logs läuft als kleiner Anhang im selben Job.

**Abgrenzung.** Kanten haben keinen eigenen Decay (Konzept 9.5); ihre effektive Stärke ergibt sich indirekt aus dem Decay der beteiligten Knoten. Kein Re-Cache der Kanten in dieser Phase — Cache-Aktualisierung folgt den drei Triggern aus Konzept 7.9, nicht dem Decay-Lauf. Halbreaktivierung greift nur im Schreibpfad (Konzept 9.3), nicht im Decay-Lauf selbst — wird in dieser Phase als Code-Pfad implementiert, aber nicht durch den Pixie-Lauf ausgelöst. Charakter-Hash bleibt unberührt (kommt in P7).

**Voraussetzungen.** P1, P2, P3, P4, P5 abgeschlossen. Konzept-Punkt 9 ist die vollständige Spezifikation der Decay-Logik.

**Datei-Scopes.**

*Neu anlegen:* Pixie-Agent für den Synapsen-Decay (Brudi verifiziert die Pixie-Agent-Konvention; vermutlich `server/pixie/agents/synapsen_decay.py`). Täglicher Lauf gemäß bestehendem Pixie-Heartbeat-Mechanismus. Berechnet `gewicht_decay` für alle aktiven Knoten gemäß Konzept 9.2 (exponentieller Decay basierend auf `verstaerkt_am` und der Decay-Rate aus `config.py`). Setzt `aktiv = FALSE` für Knoten unter `LZG_KNOTEN_MIN_GEWICHT`. Schreibt `decay_am` als Zeitstempel des Laufs. TTL-Cleanup für `pipeline_log` als kleiner zusätzlicher Schritt im selben Job (löscht Einträge älter als `LZG_PIPELINE_LOG_VORHALTUNG_TAGE`).

*Ergänzen:* Halbreaktivierungs-Code in `server/memory/lzg_knoten.py` — beim Schreibpfad-Aufruf für einen Knoten mit `aktiv = FALSE` wird `gewicht_decay = (gewicht_absolut + LZG_KNOTEN_MIN_GEWICHT) / 2` gesetzt, `aktiv` auf `TRUE` zurück. Pipeline-Log-Eintrag (`art='berechnung'`) mit den Werten vorher/nachher.

*Tabu:* Lesepfad (steht). Promotion-Logik (steht). Kanten-Tabelle wird in diesem Sprint nicht angefasst. Charakter-Hash. Migration.

**Abnahme-Tests.**

1. Pixie-Job läuft einmal pro Tag (Cron-Mechanismus gemäß bestehendem Pixie-Heartbeat). Beim Lauf werden alle aktiven Knoten mit aktualisiertem `gewicht_decay` und gesetztem `decay_am` versehen.
2. Ein Knoten mit `gewicht_absolut = 5.0`, `verstaerkt_am` vor 30 Tagen, bei Decay-Rate 0.02 pro Tag, ergibt `gewicht_decay ≈ 5.0 × exp(-0.02 × 30) ≈ 2.74`. Reproduzierbar im Unit-Test.
3. Ein Knoten, dessen `gewicht_decay` unter `LZG_KNOTEN_MIN_GEWICHT` fällt, wird auf `aktiv = FALSE` gesetzt. Lesepfad ignoriert ihn ab diesem Moment.
4. Halbreaktivierungs-Test: Ein deaktivierter Knoten mit `gewicht_absolut = 4.0` und `LZG_KNOTEN_MIN_GEWICHT = 0.5` wird im Schreibpfad reaktiviert; `gewicht_decay` springt auf `(4.0 + 0.5) / 2 = 2.25`, `aktiv` auf `TRUE`. Nicht auf den alten `gewicht_absolut`-Wert.
5. TTL-Cleanup löscht Pipeline-Log-Einträge, die älter sind als `LZG_PIPELINE_LOG_VORHALTUNG_TAGE`. Jüngere Einträge bleiben unangetastet.
6. Pipeline-Log zeigt den Decay-Lauf als Span mit Anzahl bearbeiteter Knoten, Anzahl deaktivierter Knoten und Anzahl gelöschter Log-Einträge.

### 13.9 P7 — Charakter-Hash auf neuer Topologie

**Ziel.** Die Charakter-Hash-Destillation, die heute aus dem alten `langzeitgedaechtnis` schöpft, wird auf die neuen `lzg_knoten` umgestellt. Pixie-Agent liest Knoten gemäß Filter-Regeln (`beobachter = user`, `aktiv = TRUE`, Sortierung nach `gewicht_absolut`) und destilliert in die Charakter-Hash-Strukturen. Gehört per Konvention nicht zum LZG-Kern (Konzept 8.6 verweist auf `novaberg-pixie-character-hash.md`), wird hier als Mit-Umzug behandelt, weil ohne ihn der Charakter-Pfad ins Leere liest.

**Abgrenzung.** Keine Erweiterung der Charakter-Hash-Logik selbst. Keine Änderung an der Charakter-Identitäts-Pipeline (`nova_kern`, `nova_adaptiv`, etc.). Nur die Datenquelle wird umgestellt. `CHAR-HASH-FILTER`-Bug (assistant-Einträge filtern) wird in dieser Phase strukturell gelöst, weil die Filter-Regel in der neuen Implementierung sauber gesetzt wird — als beobachteter Seiteneffekt, nicht als eigenes Sprint-Ziel.

**Voraussetzungen.** P1, P2, P3, P4, P5, P6 abgeschlossen. `novaberg-pixie-character-hash.md` ist die Spezifikation der Hash-Destillation. Bei Konflikten zwischen Pixie-Char-Hash-Doku und der Neufassung gilt das LZG-Konzept als verbindlich für die Datenquellen-Seite.

**Datei-Scopes.**

*Anpassen:* Der Charakter-Hash-Pixie-Agent (Brudi verifiziert den Pfad — vermutlich `server/pixie/agents/character_hash.py`). Lese-Quelle wechselt von `langzeitgedaechtnis` auf `lzg_knoten`. Filter auf `beobachter = user` und `aktiv = TRUE` explizit setzen. Sortier-Kriterium: `gewicht_absolut DESC`.

*Ergänzen:* Pipeline-Log-Einträge bei Lauf-Start, bei Anzahl gelesener Knoten und bei Schreib-Operationen in die Charakter-Hash-Strukturen.

*Tabu:* Alle anderen Pixie-Agenten. Charakter-Identitäts-Pipeline im HumanGraph (`nova_kern`, etc.). Lesepfad. Promotion.

**Abnahme-Tests.**

1. Charakter-Hash-Pixie-Agent läuft, liest aus `lzg_knoten`, filtert korrekt auf `beobachter = user` und `aktiv = TRUE`. Liest nicht aus `langzeitgedaechtnis`.
2. Destillation-Output ist plausibel vergleichbar mit dem Output vor dem Umzug — keine drastischen Verschiebungen in der Charakter-Hash-Struktur, sofern das neue Netz schon vergleichbare Inhalte trägt.
3. Bei leerem Netz läuft der Agent ohne Fehler und liefert eine leere oder Default-Charakter-Hash-Struktur, je nach bestehender Konvention.
4. Pipeline-Log zeigt den Lauf als Span mit Anzahl gelesener Knoten und Anzahl geschriebener Hash-Einträge.

### 13.10 P8 — Selektive Migration der Bestandsdaten

**Ziel.** Die rund 150 Bestandseinträge aus `langzeitgedaechtnis` werden chronologisch nach `erstellt_am` migriert. Meister wählt manuell circa 120 übernehmenswerte aus, das Migrations-Skript verarbeitet diese Auswahl. Jeder Eintrag wird gegebenenfalls um fehlende Magnet-Felder ergänzt, dann als `lzg_knoten` angelegt; Kanten gegen alle bereits migrierten Knoten werden via Schreibpfad gezogen.

**Abgrenzung.** Keine automatische LLM-Vorauswahl — Meister kuratiert vorab eine Liste der zu migrierenden IDs (oder eine Ausschluss-Liste, je nachdem was praktischer ist). Keine Änderung an aktiver Promotion-Logik — die läuft parallel weiter und schreibt neu entstehende Erinnerungen direkt in `lzg_knoten`. Keine Migration von Cluster-Zugehörigkeit oder alten Häufigkeits-Zählern (Konzept 11.4). Die `langzeitgedaechtnis`-Tabelle wird gelesen, aber nicht gelöscht — das kommt in P9.

**Voraussetzungen.** P1 bis P7 abgeschlossen. Meister hat eine kuratierte Liste der zu migrierenden Einträge bereitgestellt (oder Brudi liefert vorab eine `langzeitgedaechtnis`-Übersicht, aus der Meister selektiert). EntityResolver und TimeParser sind für die Nachrüstung der Magnet-Felder verfügbar.

**Datei-Scopes.**

*Neu anlegen:* Einmal-Skript für die Migration (Brudi verifiziert die im Repository übliche Konvention für Migrations-Skripte — eigener Ordner oder integriert in einen bestehenden). Das Skript nimmt eine Liste von `langzeitgedaechtnis`-IDs entgegen, lädt jeden Eintrag, rüstet fehlende Magnet-Felder via EntityResolver und TimeParser nach, legt einen `lzg_knoten` an, führt den Schreibpfad zur Kanten-Berechnung gegen bereits migrierte Knoten aus. Chronologische Reihenfolge nach ursprünglichem `erstellt_am`. Idempotent: ein Eintrag, der bereits migriert wurde (gemerkte ID-Mapping-Tabelle oder Embedding-Vergleich), wird übersprungen.

*Ergänzen:* Pipeline-Log-Einträge pro migriertem Eintrag mit der alten und neuen ID, Anzahl gezogener Kanten, etwaige Nachrüstung von Magnet-Feldern.

*Tabu:* Alle Live-Code-Pfade (Promotion, Lesepfad, Decay). Bestehende `langzeitgedaechtnis`-Tabelle wird gelesen, nicht geschrieben.

**Abnahme-Tests.**

1. Skript läuft auf der kuratierten Liste durch. Pro Eintrag entsteht ein neuer `lzg_knoten` mit allen Pflichtfeldern. Reihenfolge chronologisch.
2. Magnet-Felder fehlende Einträge werden nachgerüstet: `entitaet_ids` via EntityResolver, `timeline_id` via TimeParser. Bei nicht-resolvbaren Bestandsdaten wird ein leerer Wert gesetzt, kein Fehler.
3. Kanten zwischen migrierten Knoten entstehen entsprechend dem Schreibpfad — bei inhaltlich verwandten Einträgen ist eine Kante mit plausibler Stärke vorhanden.
4. Wiederholter Skript-Lauf auf dieselbe Liste erzeugt keine Duplikate, keine zusätzlichen Kanten — Idempotenz ist gegeben.
5. Pipeline-Log zeigt den Migrations-Lauf als langen Span mit einem Eintrag pro migriertem Knoten.
6. `langzeitgedaechtnis`-Tabelle ist unverändert. `lzg_knoten` enthält jetzt sowohl neu promotierte Einträge (seit P4) als auch die migrierten Bestandsdaten.

### 13.11 P9 — Altes LZG löschen, alte Promotion entfernen

**Ziel.** Codeschloss. Die bisherige `langzeitgedaechtnis`-Tabelle wird gelöscht. Der alte Cluster-Promotion-Code und der alte Lesepfad werden aus dem Repository entfernt. Feature-Flags `SYNAPSEN_PROMOTION_AKTIV` und `SYNAPSEN_LESEPFAD_AKTIV` werden entfernt, weil es nur noch einen Pfad gibt.

**Abgrenzung.** Wird erst gestartet, wenn P5 bis P8 nachweislich stabil im Live-Betrieb laufen. Mindest-Beobachtungszeit: eine Woche aktive Nutzung ohne kritische Befunde im Pipeline-Log. Bei kritischen Bugs zwischen P8 und P9 wird die Frist neu gestartet. Keine Migration mehr — falls Bestandsdaten in dieser Phase noch fehlen, ist das ein Hinweis, P8 zu wiederholen, bevor P9 startet. Konzept-Dokumente (`novaberg-mem-lzg.md` etc.) werden in einem separaten Doku-Sprint überarbeitet, nicht im Code-Sprint P9.

**Voraussetzungen.** P1 bis P8 abgeschlossen und stabil. Pipeline-Log der letzten sieben Tage zeigt keine systematischen Fehler in Promotion, Lesepfad, Decay oder Charakter-Hash. Bestandsdaten sind nach Meisters Bewertung vollständig migriert.

**Datei-Scopes.**

*Löschen:*

- Datenbank-Migration mit `DROP TABLE langzeitgedaechtnis`.
- Die alte LZG-Datei (vermutlich `server/memory/lzg.py` — Brudi verifiziert) — vollständig aus dem Repository entfernen.
- Die alte Cluster-Promotion (Pixie-Agent, vermutlich `server/pixie/agents/promotion.py` — Brudi verifiziert) — vollständig entfernen.
- Alter Lesepfad-Code im Enricher und Reducer — vollständig entfernen.

*Ergänzen:* `server/config.py` — Feature-Flags `SYNAPSEN_PROMOTION_AKTIV` und `SYNAPSEN_LESEPFAD_AKTIV` entfernen.

*Tabu:* Konzept-Dokumente. Doku-Sprint folgt separat nach P9.

**Abnahme-Tests.**

1. Migration läuft sauber durch. `\d langzeitgedaechtnis` in psql liefert „Did not find any relation".
2. Server startet sauber. Keine Import-Fehler, keine fehlenden Referenzen.
3. Konversations-Turn läuft komplett durch — Promotion, Lesepfad, Decay funktionieren weiterhin.
4. Repository enthält keine Referenzen mehr auf `langzeitgedaechtnis`, `SYNAPSEN_PROMOTION_AKTIV`, `SYNAPSEN_LESEPFAD_AKTIV`. Brudi verifiziert per `grep`.
5. Pipeline-Log zeigt keine Fehler in den 24 Stunden nach Deployment.

### 13.12 P10 — Wahrnehmungs-Gravitation

> **Gebaut am 02.08.2026 (Chat 126).** Vier Abweichungen von dieser Beschreibung sind beim Bauen aufgefallen und stehen an Ort und Stelle: der Ablageort der Konstante (§8.5.5), die Knotenreihenfolge (§8.5.2), der Dateizeiger des Markers (§8.5.3) und Abnahme-Test 3 unten. Was gemessen wurde, steht in §8.5.6.

**Ziel.** Embedding-Verschiebung im Enricher vor der pgvector-Suche, abhängig von aktivierten Drive-Zielen, GV-Cluster-Faktor, HumanGraph-Fallback und Imperativ-Override. Vollständige Implementierung der in Konzept 8.5 spezifizierten Mechanik, basierend auf den bereits live vorhandenen Bausteinen (Drive-Ziele mit `embedding`-Spalte, `state["prompt_embedding"]`, Salienz-Marker `"anweisung"`).

**Abgrenzung.** Vollständig unabhängiger Sprint, mechanisch orthogonal zum Synapsen-Umbau. Berührt nur den Enricher (Embedding-Berechnung vor `lzg_knoten`-Suche) und nicht die LZG-Tabellen oder Promotion. `CLUSTER_GRAVITATION_FAKTOR`-Tabelle wird neu in `config.py` angelegt. Vorgeschlagene Umbenennung des Feldes `gravitation` zu `aktivierungs_staerke` an der einen Konsumenten-Stelle in `dispatcher.py` wird mit erledigt.

**Voraussetzungen.** P1 bis P9 abgeschlossen. Konzept-Punkt 8.5 ist die vollständige Spezifikation (Berechnung der Verschiebung, HumanGraph-Sonderfall, Imperativ-Override, architektonische Verortung). Konzept-Punkt 8.5.5 listet die vorhandenen Bausteine und die offenen Stücke.

**Datei-Scopes.**

*Anpassen:*

- `server/graph/nodes/enricher.py` — Embedding-Verschiebungs-Funktion gemäß Konzept 8.5.1: `e_nova = e_anfrage × (1 − faktor) + sum(e_ziel × aktivierungs_staerke) × faktor`. Cluster-Faktor aus neuer Konstante. HumanGraph-Sonderfall: Fallback auf den zuletzt gespeicherten Cluster aus `gv:detail:{user_id}:{character_id}`. Imperativ-Override: bei Salienz-Marker `"anweisung"` wird die Verschiebung übersprungen, rohes Anfrage-Embedding wird verwendet.
- `server/graph/nodes/dispatcher.py` — Umbenennung des Feldes `gravitation` zu `aktivierungs_staerke` an der einen bekannten Konsumenten-Stelle.
- `server/config.py` — neue Konstante `CLUSTER_GRAVITATION_FAKTOR` als Dict pro Cluster gemäß Konzept 8.5.1, mit ausführlichem deutschem Doc-Kommentar.

*Ergänzen:* Pipeline-Log-Einträge an allen Entscheidungs-Stellen: Anzahl aktivierter Ziele, Cluster-Faktor, ob HumanGraph-Fallback gegriffen hat, ob Imperativ-Override gegriffen hat, finales Embedding (gekürzt als Hash oder Dimension-Summary).

*Tabu:* Alles außerhalb der drei genannten Dateien. Insbesondere keine Berührung der LZG-Tabellen, der Promotion oder des Decay-Pfads.

**Abnahme-Tests.**

1. Bei aktiven Drive-Zielen mit hoher Aktivierungs-Stärke wird das Anfrage-Embedding messbar in Richtung der Ziel-Embeddings verschoben. Verschiebung ist im Pipeline-Log dokumentiert.
2. Bei Salienz-Marker `"anweisung"` im aktuellen Turn greift der Imperativ-Override; das Anfrage-Embedding wird nicht verschoben. Pipeline-Log-Eintrag bestätigt das.
3. ~~Im HumanGraph (Pfad 1 unter `ASSISTANT_USER_ID`) greift der Fallback auf den zuletzt gespeicherten Cluster aus Redis; Verschiebung erfolgt mit dem Fallback-Cluster-Faktor.~~ **Nicht erfüllbar, festgestellt am 02.08.2026:** `_enrich_human` führt keine Vektorsuche, es gibt dort keinen Suchschlüssel. Der Redis-Rückfall ist stattdessen im **CharacterGraph** geprüft — dort ist er nach §8.5.2 der einzige Pfad.
4. Cluster-abhängige Stärke der Verschiebung ist gemäß `CLUSTER_GRAVITATION_FAKTOR` aus `config.py` nachvollziehbar — Werkstatt-Cluster verschiebt anders als Glut.
5. Umbenennung `gravitation` → `aktivierungs_staerke` ist in `dispatcher.py` durchgeführt, keine Konsumenten-Stelle ist gebrochen. `grep "gravitation"` im Code zeigt nur noch Verwendungen, die wirklich den Cluster-Faktor meinen.
6. Pipeline-Log zeigt für jeden Enricher-Lauf einen Span mit allen Verschiebungs-Parametern.

