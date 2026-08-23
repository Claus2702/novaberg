# Novaberg — Paar-Schema: Subjekt × Gegenüber × Beobachter

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Verbindliche Konvention für (user_id, character_id, beobachter)
**Stand:** 23. August 2026 — **§3.2 nachgezogen: der Lesepfad der Bibliothek filtert dreispaltig.** Davor: 16. August 2026 — **§2.1, §2.2 und zwei Designprinzipien richtiggestellt**: `user_id` trägt den Menschen, `character_id` die Figur, die Perspektive allein der `beobachter`. Davor: 29. April 2026, Chat 71
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
| **KZG (Redis)** | `kzg:{user_id}:{character_id}:{id}` (zwei Felder im Key, `beobachter` als Hash-Field) | ~~`kzg:nova:nova:1777481545954` für Nova-Erkenntnisse~~ — der Befund von damals, heute beseitigt |
| **LZG (Postgres)** | drei Spalten: `user_id`, `character_id`, `beobachter` | `(meister, nova, assistant)` für Nova-Sicht auf User |
| **Hash (Postgres)** | zwei Spalten: `(user_id, character_id)` — kein `beobachter` | `(nova, meister)` für Novas Selbstbild |

Drei Konventionen leben in Kopfmodellen, aber keine ist syntaktisch
durchgesetzt. Das Resultat sind verlorene Trigger, falsche Partitionen und
eingefrorene Profile. Diese Konzept-Doku fixiert die verbindliche Konvention
und benennt die Inkonsistenzen, die schrittweise beseitigt werden.

---

## 2. Die verbindliche Konvention

```
user_id      = der Mensch   — welcher Mensch?
character_id = die Figur    — welche Figur?
beobachter   = der Schreiber — wer hat den Eintrag erzeugt? (user | assistant)
```

**Das Paar steht immer in dieser Richtung.** `user_id` trägt den Menschen, `character_id` die Figur — nie umgekehrt. Die **Perspektive** trägt allein der `beobachter`.

> ⚠ **Am 16.08.2026 richtiggestellt, und die alte Fassung war teuer.** Bis dahin las dieser Abschnitt `user_id` als „Subjekt — über wen geht der Eintrag?" und erlaubte damit ausdrücklich, die Figur in die `user_id`-Spalte zu setzen. Daraus entstanden Einträge unter `nova:{mensch}`; ihre Beseitigung im Kurzzeit- und Langzeitgedächtnis hat Arbeit gekostet, und beide Speicher sind seither sauber.
>
> **Was von `user_id` – `character_id` – `beobachter` abweicht, ist falsch.** Das gilt auch für Sätze in diesem Dokument: Die betroffenen stehen unten durchgestrichen, nicht gelöscht.

### 2.1 Beispiele

| Was passiert | Subjekt | Gegenüber | Beobachter |
|---|---|---|---|
| Meister äußert sich → KZG-Eintrag | meister | nova | user |
| Nova antwortet → KZG-Eintrag durch Salienz/Pixie | meister | nova | assistant |
| Nova reflektiert über sich nach Recherche | meister | nova | assistant |
| Hypothetisch: ein zweiter User schreibt über meister | meister | nova | otheruser |

~~Wichtige Konsequenz: **Nova-Erkenntnisse über sich selbst** sind
`(subjekt=nova, gegenueber=meister, beobachter=assistant)`. Sie landen unter
`kzg:nova:meister:*` und im LZG unter `(nova, meister, assistant)` — nicht
unter `(nova, nova, assistant)` und nicht unter `(meister, nova, assistant)`.~~

→ **Falsch, und am 16.08.2026 gestrichen.** `kzg:nova:{mensch}` darf nicht entstehen. **Nova-Erkenntnisse über sich selbst sind `(user_id=meister, character_id=nova, beobachter=assistant)`** — dasselbe Paar wie alle anderen Einträge dieser Beziehung, unterschieden allein durch den Beobachter. Im Kurzzeit- und Langzeitgedächtnis ist das heute so; gemessen am 16.08.2026: **0 Schlüssel `kzg:nova:*`, 0 Zeilen in `lzg_knoten` mit `user_id='nova'`.**

### 2.2 Was die Konvention NICHT bedeutet

- Sie sagt nicht, dass Mensch und Figur je untereinander vertauscht werden
  dürfen, weil "es ja egal ist". ~~Sie sind es nicht — siehe Hash-Loop:
  `(meister, nova)` und `(nova, meister)` sind zwei separate Profile.~~ →
  **Die Begründung war falsch und ist am 16.08.2026 gestrichen.** Dass zwei
  Richtungen zwei Profile ergeben, war kein Argument für die Unterscheidung,
  sondern die Beschreibung des Fehlers: `(nova, meister)` darf es nicht geben.
  Der Satz selbst bleibt richtig — vertauscht wird nicht, weil die Richtung
  **fest** ist.
- ~~Sie sagt nicht, dass `user_id` immer der "anschreibende" User ist. Im
  Schreibkontext ist das oft so, aber als Datenfeld bezeichnet `user_id` das
  Subjekt — auch wenn das Nova selbst ist.~~ → **Falsch, am 16.08.2026
  gestrichen.** `user_id` trägt **immer** den Menschen. Dieser Satz war die
  ausdrückliche Erlaubnis für den Fehler, den §2 jetzt benennt.

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
- ~~Alle KZG-Einträge zu Nova mit Meister-Kontext: `kzg:nova:meister:*`~~ → **Falsch, am 16.08.2026 gestrichen.** Diesen Schlüssel gibt es nicht und darf es nicht geben. Was Nova über sich selbst weiß, liegt unter `kzg:meister:nova:*` mit `beobachter = assistant`.

### 3.2 LZG (Postgres)

- Drei Spalten `user_id`, `character_id`, `beobachter` — heute in `lzg_knoten` (die Tabelle hieß bis zur Aufteilung in Knoten und Kanten `langzeitgedaechtnis`). **Alle drei sind belegt**, gemessen am 16.08.2026.
- Querys filtern auf das vollständige 3-Tupel, sobald der Beobachter
  semantisch wichtig ist (z. B. Charakter-Destillation: nur
  Beobachter `assistant` für Nova-Selbstbild). Heute filtern die meisten
  Lesepfade nur auf `user_id` und ignorieren `character_id` + `beobachter` —
  das wird im Backlog adressiert.

  > **Am 23.08.2026 für die Bibliothek (`autonomous_wissen`) erledigt.** Alle
  > **vier** paargefilterten Abfragen filtern dreispaltig: `suchen` und
  > `zaehlen` im Repository, der Vorcheck im Enricher, die Kandidatenauswahl
  > des Rückwegs. Der Befund hatte zwei genannt — die anderen beiden fand ein
  > Kriterium (*wer fragt `autonomous_wissen` mit `user_id = %s`?*), und genau
  > die wären bei einer Prüfung entlang der Aufzählung nie aufgefallen.
  >
  > **Der Beobachter ist dort Pflichtfeld ohne Default**, geprüft gegen den
  > neuen `BEOBACHTER_KANON` (`config.py`) — nicht gegen den einen erwarteten
  > Wert: Eine Prüfung auf `assistant` allein könnte einen unbekannten Wert
  > nicht von einem gültigen zweiten unterscheiden. Die gelesene Perspektive
  > steht als `BIBLIOTHEK_BEOBACHTER` an einer Stelle statt als Literal an
  > vier.
  >
  > **Folgenlos im heutigen Bestand und trotzdem nötig:** 831 aktive Zeilen,
  > alle `beobachter='assistant'`, der Filterwechsel entfernt null. Der
  > Ausfall wäre still gewesen — fremde Zeilen erschienen als eigene
  > Ausarbeitung, und eine Trefferliste, die zu viel enthält, sieht aus wie
  > eine Bibliothek mit Bestand.
  >
  > **Offen bleiben die anderen Speicher.** `lzg_knoten` wird im Enricher
  > unmittelbar daneben weiterhin zweispaltig gefragt, und der Wert steht an
  > acht Stellen des Baums als Literal. Beides in der Fundliste.

### 3.3 Charakter-Hash (Postgres)

- **Soll-Zustand:** drei Spalten `(user_id, character_id, beobachter)` als
  Primärschlüssel. Damit gibt es zwei `(meister, nova, *)`-Hashes — einen für
  `beobachter=user` (wie der Mensch Nova erlebt) und einen für
  `beobachter=assistant` (wie Nova sich selbst sieht). Der Enricher
  entscheidet kontextabhängig, welcher gelesen wird.

  **Dieser Abschnitt war von Anfang an richtig und ist nie gebaut worden.** Er
  weicht nicht von `user_id` – `character_id` – `beobachter` ab, er ist diese
  Definition.

- ~~**Heutiger Stand:** zwei Spalten `(user_id, character_id)` als
  Primärschlüssel. Das mischt zwei semantische Sichten in einem Eintrag:
  Nova-aus-User-Sicht und Nova-aus-Selbstsicht haben heute denselben Hash.~~ →
  **Am 16.08.2026 nachgemessen: Sie teilen sich keinen Eintrag — sie stehen in
  zwei Zeilen, und die zweite ist falsch geschlüsselt.**

> ⚠ **Die Tabelle trägt noch die Struktur des alten, falschen Modells.**
> `charakter_hash` hat zwei Schlüsselspalten und damit **keinen Platz für die
> Perspektive**. Weil der `beobachter` fehlt, bleibt der schreibenden Stelle
> nur die Paar-Richtung als Träger: Der `CharakterAgent` legt das Nova-Profil
> unter dem **vertauschten** Paar ab. Die gespiegelten Zeilen sind nicht die
> Ursache, sondern das Symptom — die fehlende dritte Spalte ist es.
>
> `[gemessen]` — 16.08.2026: **34 Zeilen, exakt gespiegelt.** Zu jedem der
> siebzehn Menschen gibt es die richtige Zeile `({mensch}, nova)` **und** eine
> zweite `(nova, {mensch})`, in der die Figur in der `user_id`-Spalte steht.
> `(nova, meister)` trägt ein Änderungsdatum von diesem Tag — **der Fehler ist
> kein Bestandsrest, er entsteht weiter.**
>
> Beteiligt sind drei Stellen, und alle berufen sich auf den gestrichenen §2.1:
> `agents/charakter/agent.py` (schreibt), `memory/charakter.py` →
> `nova_charakter_hash_retrieve_dict` (liest, zitiert ihn im Docstring),
> `graph/nodes/db_zugriff.py` (verbraucht ihn für `state["internal"]`).
>
> **Kein Weg zur Behebung in diesem Dokument.** Er berührt das Schema, und das
> ist eine eigene Entscheidung. Geführt als **`CHAR-HASH-PAAR-VERTAUSCHT`**
> in `novaberg-bugs.md`.

---

## 4. Stand der Implementierung (29. April 2026)

### 4.1 Konform

- LZG schreibt seit Chat 66 mit allen drei Feldern.
- KZG-Manager (`plugins/kzg_manager`): User-Schreibpfad nutzt `(meister, nova)`
  korrekt.
- ~~CharakterAgent iteriert beide Hash-Paare `(meister, nova)` und
  `(nova, meister)` und destilliert für beide.~~ → **Am 16.08.2026 aus
  „Konform" gestrichen: Das ist der Fehler, nicht seine Abwesenheit.** Er
  destilliert zwei Perspektiven — richtig — und legt die zweite unter dem
  **vertauschten Paar** ab, weil die Tabelle keine Spalte für den Beobachter
  hat (§3.3).

### 4.2 Bekannte Abweichungen (Stand Chat 71)

| Pfad | Verstoß | Wirkung |
|---|---|---|
| `nova_gedaechtnis.py` (vor Chat 71) | rief `kzg_store(user_id=user_id, character_id=ASSISTANT_USER_ID)` — Nova-Erkenntnisse landeten unter `kzg:meister:nova:*` (oder `kzg:nova:nova:*` wenn Caller-User=nova). Subjekt und Gegenüber waren falsch herum. | `hash_dirty:nova:meister` wurde nie zuverlässig gesetzt → Nova-Hash blieb veraltet. |
| ~~**Chat 71 Fix:**~~ **Am 16.08.2026 gestrichen — dieser Fix schrieb auf den verbotenen Schlüssel `kzg:nova:meister:*`.** Die Datei `nova_gedaechtnis.py` existiert nicht mehr, und nichts hat ihre Aufgabe übernommen; gemessen sind **0 Schlüssel `kzg:nova:*`**. Das ist der richtige Zustand, nicht eine Lücke. | — | — |
| `agents/promotion/agent.py:575-577` | Cluster-Promotion-Guard `if user_id == ASSISTANT_USER_ID: return 0` — überspringt Nova-Partition. | Nova-KZG wird nie systematisch in LZG promotet. Kern-Hash für Nova bleibt dünn. |
| Charakter-Hash-Schema | Zwei statt drei Spalten — kein `beobachter`. | Nova-aus-User-Sicht und Nova-aus-Selbstsicht teilen sich einen Eintrag. Konfundierung. |
| Altdaten in Redis | 19× `kzg:nova:nova:*` aus Pre-Fix-Zeit. | Werden vom CharakterAgent zufällig mitgelesen (Wildcard `kzg:nova:*`). Solange unschädlich, sollten aber migriert werden. |

### 4.3 Roadmap

- **Sofort (Chat 71):** Schritt 1 (`nova_gedaechtnis.py` Subjekt/Gegenüber-Fix) ✅, Schritt 2 (diese Doku) ✅.
- **Mittelfristig:** Hash-Schema um `beobachter` erweitern, Cluster-Promotion-Guard für Nova entschärfen — siehe `novaberg-backlog.md`.
- ~~**Datenseitig:** Migrations-Skript `kzg:nova:nova:*` → `kzg:nova:meister:*` mit `beobachter=assistant`.~~ → **Am 16.08.2026 gestrichen: Das Ziel war der verbotene Schlüssel.** Das Skript liegt als `server/tools/migrate_kzg_nova_nova.py` im Baum und **darf nicht laufen** — es würde Einträge unter `kzg:nova:{mensch}` anlegen und `hash_dirty:nova:{mensch}` setzen. Der Bestand ist ohne es sauber: 0 Schlüssel `kzg:nova:*`.

---

## 5. Designprinzipien für künftige Pfade

1. **Nie ohne alle drei Felder schreiben.** Wer einen KZG-Eintrag erzeugt,
   muss `(subjekt, gegenueber, beobachter)` explizit setzen. Defaults sind
   ein Code-Smell.
2. ~~**Subjekt und Beobachter dürfen identisch sein** (Nova reflektiert über
   Nova → `subjekt=nova, beobachter=assistant`), aber nur, wenn das
   semantisch wirklich gemeint ist.~~ → **Am 16.08.2026 gestrichen.** `user_id`
   trägt den Menschen; die Figur steht dort nie. Dass Nova über sich selbst
   nachdenkt, zeigt allein `beobachter = assistant`.
3. ~~**`character_id == user_id`** ist erlaubt, aber sollte als bewusste
   Selbst-Reflexion dokumentiert sein, nicht als Default-Fallback.~~ → **Am
   16.08.2026 gestrichen: Es ist nicht erlaubt.** Mensch und Figur sind
   verschiedene Dinge und stehen in verschiedenen Spalten. Die 19 Altdaten
   unter `kzg:nova:nova:*` waren ein Bug-Artefakt, kein Design-Statement — sie
   sind beseitigt, und der Bestand ist seither sauber.
4. **Trigger folgt Daten.** Wer schreibt, setzt das `hash_dirty`-Flag mit
   demselben `(subjekt, gegenueber)`-Paar. Das CharakterAgent-Loop und der
   Pixie-Runner verlassen sich darauf.

---

## 6. Verweise

- Code-Fix Schritt 1: `server/services/shadow_agent/tasks/nova_gedaechtnis.py` (Chat 71)
- Bug-Bericht: `novaberg-bugs.md` → CHAR-BEZ-STALE (Chat 71)
- Backlog: `novaberg-backlog.md` → "Hash-Schema um beobachter erweitern", "Migrations-Skript kzg:nova:nova:*"
- Vorgängermigration: `novaberg-bugs.md` Chat 66 (Paar-Schema-Einführung)

---

## Versionshistorie

- **v0.2 — 16.08.2026:** **Die Konvention hat sich selbst widersprochen, und der falsche Teil war der bekanntere.** §2 las `user_id` als „Subjekt — über wen geht der Eintrag?" und erlaubte damit ausdrücklich, die Figur in die `user_id`-Spalte zu setzen; §2.1 schrieb `kzg:nova:meister:*` vor, §2.2 verteidigte es, und zwei Designprinzipien in §5 bauten darauf auf. **Alles davon ist gestrichen.** Die Richtung des Paares ist fest: Mensch, Figur, Beobachter — und die Perspektive trägt allein der Beobachter. §3.3 blieb unverändert gültig: Es fordert genau diese drei Spalten und ist nie gebaut worden. **Was die Richtigstellung sichtbar gemacht hat:** `charakter_hash` trägt noch die Struktur des alten Modells — zwei Schlüsselspalten ohne Platz für die Perspektive —, und deshalb legt der `CharakterAgent` das Nova-Profil unter dem vertauschten Paar ab. 34 Zeilen, exakt gespiegelt, mit einem Änderungsdatum von heute. Im Kurzzeit- und Langzeitgedächtnis ist derselbe Fehler längst beseitigt (0 Schlüssel, 0 Zeilen); hier ist er nie beseitigt worden.
- **v0.1 — 29.04.2026, Chat 71:** Erstfassung nach einem eingefrorenen Beziehungsprofil — drei konkurrierende Konventionen für dasselbe Paar, verteilt über drei Speicher.
