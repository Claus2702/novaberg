# Novaberg — Paar-Schema: Subjekt × Gegenüber × Beobachter

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Verbindliche Konvention für (user_id, character_id, beobachter)
**Stand:** 29. April 2026, Chat 71
**Pfad:** novaberg/docs/novaberg-convention-paar-schema.md
**Typ:** Convention
**Voraussetzung:** Paar-Schema-Migration, Chat 66 ✅
**Folgendes:** CHAR-BEZ-STALE (novaberg-bugs.md), Backlog "Hash-Schema um beobachter erweitern", Backlog "Migrations-Skript Altdaten kzg:nova:nova:*"

---

## 1. Motivation

Chat 71 hat einen Bug aufgedeckt, der seit der Paar-Schema-Migration latent
schwelt: Das Beziehungsprofil im Charakter-Hash für `(nova, meister)` zeigt
Nova als "rein sachliche und effizienzorientierte Instanz" — obwohl die
tatsächliche Beziehung "vertraut und emotional" ist.

Die Forensik zeigt drei konkurrierende Konventionen für dasselbe konzeptuelle
Paar (Subjekt + Gegenüber + Beobachter), verteilt über die drei Speicher KZG,
LZG und Charakter-Hash:

| Speicher | Heutiges Schema | Beispiel-Eintrag |
|---|---|---|
| **KZG (Redis)** | `kzg:{user_id}:{character_id}:{id}` (zwei Felder im Key, `beobachter` als Hash-Field) | `kzg:nova:nova:1777481545954` für Nova-Erkenntnisse |
| **LZG (Postgres)** | drei Spalten: `user_id`, `character_id`, `beobachter` | `(meister, nova, assistant)` für Nova-Sicht auf User |
| **Hash (Postgres)** | zwei Spalten: `(user_id, character_id)` — kein `beobachter` | `(nova, meister)` für Novas Selbstbild |

Drei Konventionen leben in Kopfmodellen, aber keine ist syntaktisch
durchgesetzt. Das Resultat sind verlorene Trigger, falsche Partitionen und
eingefrorene Profile. Diese Konzept-Doku fixiert die verbindliche Konvention
und benennt die Inkonsistenzen, die schrittweise beseitigt werden.

---

## 2. Die verbindliche Konvention

```
user_id      = Subjekt    — über wen geht der Eintrag?
character_id = Gegenüber  — im Kontext welcher anderen Entität?
beobachter   = Schreiber  — wer hat den Eintrag erzeugt? (user | assistant)
```

Die Achsen sind orthogonal. Subjekt ist nicht Beobachter, Gegenüber ist nicht
Beobachter, und alle drei können in beliebiger Kombination vorkommen.

### 2.1 Beispiele

| Was passiert | Subjekt | Gegenüber | Beobachter |
|---|---|---|---|
| Meister äußert sich → KZG-Eintrag | meister | nova | user |
| Nova antwortet → KZG-Eintrag durch Salienz/Pixie | meister | nova | assistant |
| Nova reflektiert über sich nach Recherche | nova | meister | assistant |
| Hypothetisch: ein zweiter User schreibt über meister | meister | nova | otheruser |

Wichtige Konsequenz: **Nova-Erkenntnisse über sich selbst** sind
`(subjekt=nova, gegenueber=meister, beobachter=assistant)`. Sie landen unter
`kzg:nova:meister:*` und im LZG unter `(nova, meister, assistant)` — nicht
unter `(nova, nova, assistant)` und nicht unter `(meister, nova, assistant)`.

### 2.2 Was die Konvention NICHT bedeutet

- Sie sagt nicht, dass Subjekt und Gegenüber je untereinander vertauscht
  werden dürfen, weil "es ja egal ist". Sie sind es nicht — siehe Hash-Loop:
  `(meister, nova)` und `(nova, meister)` sind zwei separate Profile.
- Sie sagt nicht, dass `user_id` immer der "anschreibende" User ist. Im
  Schreibkontext ist das oft so, aber als Datenfeld bezeichnet `user_id` das
  Subjekt — auch wenn das Nova selbst ist.

---

## 3. Die drei Speicher unter dieser Konvention

### 3.1 KZG (Redis)

- Key: `kzg:{subjekt}:{gegenueber}:{id}`
- Felder im Hash: `beobachter`, `inhalt`, `themen`, …
- Trigger: `hash_dirty:{subjekt}:{gegenueber}` wird gesetzt, sobald der
  Eintrag landet.

Konsequenz für Lese-Pfade:
- Alle KZG-Einträge zu Meister mit Nova-Kontext (egal ob User- oder
  Assistant-Beobachter): `kzg:meister:nova:*`
- Alle KZG-Einträge zu Nova mit Meister-Kontext: `kzg:nova:meister:*`

### 3.2 LZG (Postgres)

- Drei Spalten `user_id`, `character_id`, `beobachter` in
  `langzeitgedaechtnis` (existiert bereits).
- Querys filtern auf das vollständige 3-Tupel, sobald der Beobachter
  semantisch wichtig ist (z. B. Charakter-Destillation: nur
  Beobachter `assistant` für Nova-Selbstbild). Heute filtern die meisten
  Lesepfade nur auf `user_id` und ignorieren `character_id` + `beobachter` —
  das wird im Backlog adressiert.

### 3.3 Charakter-Hash (Postgres)

- **Heutiger Stand:** zwei Spalten `(user_id, character_id)` als Primärschlüssel.
  Das mischt zwei semantische Sichten in einem Eintrag:
  Nova-aus-User-Sicht und Nova-aus-Selbstsicht haben heute denselben Hash.
- **Soll-Zustand (Backlog):** drei Spalten `(user_id, character_id, beobachter)`
  als Primärschlüssel. Damit gibt es zwei `(nova, meister, *)`-Hashes —
  einen für `beobachter=user` (wie Meister Nova erlebt) und einen für
  `beobachter=assistant` (wie Nova sich selbst sieht). Der Enricher
  entscheidet kontextabhängig, welcher gelesen wird.

---

## 4. Stand der Implementierung (29. April 2026)

### 4.1 Konform

- LZG schreibt seit Chat 66 mit allen drei Feldern.
- KZG-Manager (`plugins/kzg_manager`): User-Schreibpfad nutzt `(meister, nova)`
  korrekt.
- CharakterAgent iteriert beide Hash-Paare `(meister, nova)` und
  `(nova, meister)` und destilliert für beide.

### 4.2 Bekannte Abweichungen (Stand Chat 71)

| Pfad | Verstoß | Wirkung |
|---|---|---|
| `nova_gedaechtnis.py` (vor Chat 71) | rief `kzg_store(user_id=user_id, character_id=ASSISTANT_USER_ID)` — Nova-Erkenntnisse landeten unter `kzg:meister:nova:*` (oder `kzg:nova:nova:*` wenn Caller-User=nova). Subjekt und Gegenüber waren falsch herum. | `hash_dirty:nova:meister` wurde nie zuverlässig gesetzt → Nova-Hash blieb veraltet. |
| **Chat 71 Fix:** `nova_gedaechtnis.py` ruft jetzt `kzg_store(user_id=ASSISTANT_USER_ID, character_id=gegenueber_id)` mit `gegenueber_id = user_id if user_id != ASSISTANT_USER_ID else DEFAULT_USER_ID`. | Eintrag landet unter `kzg:nova:meister:*`, Trigger `hash_dirty:nova:meister` greift. | Nova-Hash wird beim nächsten Pixie-Lauf wieder destilliert. |
| `agents/promotion/agent.py:575-577` | Cluster-Promotion-Guard `if user_id == ASSISTANT_USER_ID: return 0` — überspringt Nova-Partition. | Nova-KZG wird nie systematisch in LZG promotet. Kern-Hash für Nova bleibt dünn. |
| Charakter-Hash-Schema | Zwei statt drei Spalten — kein `beobachter`. | Nova-aus-User-Sicht und Nova-aus-Selbstsicht teilen sich einen Eintrag. Konfundierung. |
| Altdaten in Redis | 19× `kzg:nova:nova:*` aus Pre-Fix-Zeit. | Werden vom CharakterAgent zufällig mitgelesen (Wildcard `kzg:nova:*`). Solange unschädlich, sollten aber migriert werden. |

### 4.3 Roadmap

- **Sofort (Chat 71):** Schritt 1 (`nova_gedaechtnis.py` Subjekt/Gegenüber-Fix) ✅, Schritt 2 (diese Doku) ✅.
- **Mittelfristig:** Hash-Schema um `beobachter` erweitern, Cluster-Promotion-Guard für Nova entschärfen — siehe `novaberg-backlog.md`.
- **Datenseitig:** Migrations-Skript `kzg:nova:nova:*` → `kzg:nova:meister:*` mit `beobachter=assistant` — siehe `novaberg-backlog.md`.

---

## 5. Designprinzipien für künftige Pfade

1. **Nie ohne alle drei Felder schreiben.** Wer einen KZG-Eintrag erzeugt,
   muss `(subjekt, gegenueber, beobachter)` explizit setzen. Defaults sind
   ein Code-Smell.
2. **Subjekt und Beobachter dürfen identisch sein** (Nova reflektiert über
   Nova → `subjekt=nova, beobachter=assistant`), aber nur, wenn das
   semantisch wirklich gemeint ist.
3. **`character_id == user_id`** ist erlaubt, aber sollte als bewusste
   Selbst-Reflexion dokumentiert sein, nicht als Default-Fallback. Die 19
   Altdaten unter `kzg:nova:nova:*` waren ein Bug-Artefakt, kein
   Design-Statement.
4. **Trigger folgt Daten.** Wer schreibt, setzt das `hash_dirty`-Flag mit
   demselben `(subjekt, gegenueber)`-Paar. Das CharakterAgent-Loop und der
   Pixie-Runner verlassen sich darauf.

---

## 6. Verweise

- Code-Fix Schritt 1: `server/services/shadow_agent/tasks/nova_gedaechtnis.py` (Chat 71)
- Bug-Bericht: `novaberg-bugs.md` → CHAR-BEZ-STALE (Chat 71)
- Backlog: `novaberg-backlog.md` → "Hash-Schema um beobachter erweitern", "Migrations-Skript kzg:nova:nova:*"
- Vorgängermigration: `novaberg-bugs.md` Chat 66 (Paar-Schema-Einführung)
