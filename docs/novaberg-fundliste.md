# Novaberg — Fundliste

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Rohe, noch unklassifizierte Funde aus laufender Arbeit
**Stand:** 27. Juli 2026
**Pfad:** novaberg/docs/novaberg-fundliste.md

Was beim Bauen an anderer Stelle auffällt, landet hier — **eine Zeile mit Datum**. Kein Bug-Name, keine Priorität, keine Klassifizierung, keine Diskussion. Der Zweck ist, einen Fund festzuhalten, ohne die laufende Arbeit dafür zu unterbrechen.

Diese Liste ist bewusst roh. Von hier wandern Einträge nach `novaberg-bugs.md` oder `novaberg-backlog.md` und bekommen dort eine stabile ID; die Zeile hier wird beim Umzug entfernt.

---

## Stichtage

Analog zum Kraft-1-Stichtag: ab wann eine Partition brauchbar ist. Kein Backfill; was davor liegt, bleibt falsch und wird nicht gelesen.

- ~~**assistant-Partition (`beobachter='assistant'`) — brauchbar ab 2026-07-26 13:03:30 UTC.** Davor verdichtete Pfad 2 den User-Prompt statt Novas Antwort und legte denselben Satz wie Pfad 1 ab. Der letzte fehlerhafte Eintrag stammt aus Turn `6bc55996748f48dc9a2cfeaf26dc44e2` um 12:59:20 UTC; der erste korrekte ist `kzg:meister:nova:1785071056367`.~~ → **Gegenstandslos seit dem Reset am 27.07.2026, 09:13 UTC.** Die Partition ist leer; es gibt keinen Bestand mehr, gegen den ein Stichtag abgrenzen könnte. Die *Aussage* bleibt richtig — der Verdichtungsfehler war real und ist behoben (`DESTILLAT-SUBJEKT-SCHABLONE`) —, nur die Abgrenzung hat keinen Gegenstand mehr.

- **Neuer Nullpunkt — 2026-07-27 09:13 UTC.** Alle Partitionen beginnen hier. Der erste Eintrag nach diesem Zeitpunkt ist der erste überhaupt.

---

## Offen

- **2026-07-27** — Ein Queue-Eintrag für einen **noch nicht gebauten** Agenten verdrängt laufende Arbeit. Der Pixie-Heartbeat wählt alle 120 s einen Gewinner nach Priorität; `nachfragen` (Prio 0.97) gewann dreimal gegen `charakter_hash` (Prio 0.3) und scheiterte jedes Mal an `Agent 'nachfragen' nicht in Registry`. Nach drei Fehlversuchen verworfen — sechs Minuten ohne anderen Job. Der fehlende Agent ist **kein Bug, sondern Roadmap** (`PIX-MIG-7`); der Befund ist die Verdrängung: Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen. Beleg: Server-Log 13:19–13:23 UTC.
- **2026-07-27** — `CharakterAgent` (Prio 0.3) wird ausgehungert, solange die Queue läuft: `lzg_promotion` steht bei 0.97, jeder Turn erzeugt welche. Vier Heartbeats in Folge ging der Charakter leer aus, obwohl `hash_dirty` gesetzt war. Vermutlich gewollt (Profil-Destillation ist nicht dringend) — als Verhalten aber nirgends festgehalten.
- **2026-07-27** — `uvicorn --reload` überwacht **nur Python-Dateien**. Ein Edit an `db/init.sql` löst keinen Reload aus; der Container sieht die Änderung sofort, `schema_migrieren()` läuft aber erst beim nächsten `.py`-Edit oder Neustart. Schärft die Reload-Falle: SQL schreiben ist harmlos, der nächste Python-Edit zündet es.
- **2026-07-27** — Der `pending_write` des Salienz-Nodes trägt das Segment **nicht** weiter (`daten` enthält nur `salienz_obj`). `agents/kzg/verdichtung.py:93-94` liest `user_prompt`/`response`, also den ganzen Turn. Drei Segmente ⇒ drei LLM-Aufrufe mit bitgleicher Eingabe ⇒ drei Paraphrasen desselben Absatzes; die übrigen Segmente landen nie im Gedächtnis. Präzisiert `KZG-SEGMENT-DUPLIKAT`: Datenpfad, nicht Prompt.
- **2026-07-27** — Themen eines Segments werden aus dem `[LAGEBILD]` übernommen, das der Prompt als „Hintergrund — nicht bewerten" deklariert. Belegt an Turn `975ec093…`: Segmente 0 und 2 tragen `40 Hz Frequenz im Gehirn` wörtlich aus dem 56-Zeichen-Nutzerprompt, obwohl die Wendung in keinem der beiden Segmente vorkommt. Segment 1, das das Thema enthält, trägt vier eigene Themen. Wirkung: falsche thematische Verstärkung.
- **2026-07-27** — Verdacht, nicht belegt: Auch die Salienz-Bewertung könnte den Gesamtzusammenhang statt des Segments bewerten. Alle drei Segmente von Turn `975ec093…` erhielten 0.3, obwohl Segment 0 das Wort „liebe" enthält und die Regeln dafür 0.7–0.8 vorsehen. Zur Klärung Turns mit unterschiedlich gefühlsgeladenen Segmenten vergleichen.
- **2026-07-27** — `novaberg-architecture.md` §7 Dokumentenverzeichnis nennt „**72 Dateien**", tatsächlich liegen 123 `.md` in `docs/`. Kein einziges `novaberg-convention-*.md` steht im Index.
- **2026-07-27** — `novaberg-bugs.md` führt `SHADOW-DELIVERY-DATENVERLUST` mit einem Beleg auf `services/shadow_delivery.py:514-522`, der dort nicht mehr steht; der Chat-110-Umbau hat den Pfad ersetzt. Restrisiko besteht weiter, aber an anderer Stelle und an `BROADCAST-VERSCHLUCKT-FEHLER` hängend.
- **2026-07-27** — Drei Dokumente nennen eine „Promotions-Schwelle 0.8" (`novaberg-charakter-resonanz_k.md:442`, `novaberg-backlog.md:2940` und `:3544`). Im Code gibt es keine 0.8; das Tor ist `KZG_SALIENZ_HIGH = 0.7` in `agents/kzg/queues.py:72`.

---

## Umgezogen — Chat 110 (26.07.2026)

Elf Zeilen sind in `novaberg-bugs.md` zu Einträgen mit Reproduktionsweg geworden. Beim Umzug haben zwei von ihnen sich als ungenauer erwiesen als gedacht — die Messung gehört zum Umzug, nicht zur Notiz:

| Fundlisten-Zeile | Wurde zu | Korrektur beim Umzug |
|---|---|---|
| Zwei bis drei identische Kernsätze je Impuls | `KZG-SEGMENT-DUPLIKAT` | Betrifft **jeden** Turn, nicht nur Impulse: Nutzer-Turn 2 identische, Impuls 3 je Graph |
| Impuls erzeugt zwei assistant-Einträge | `IMPULS-DOPPELTE-SPUR` | Es sind **sechs** (2 Graphen × 3 Segmente); ein Nutzer-Turn hat 1 `user` + 2 `assistant`, nicht je einen |
| Salienz-Node ohne `pipeline_log` | `SALIENZ-OHNE-PIPELINE-LOG` | — |
| Kontaminationsfilter ohne Setzer | `KONTAMINATIONSFILTER-TOT` | Zeile 424 → **448** (nach den Chat-110-Änderungen) |
| Destillat behauptet Handlung | `DESTILLAT-BEHAUPTETE-HANDLUNG` | — |
| `[EIGENER GEDANKE]` nur teilweise | `IMPULS-ICH-PERSPEKTIVE-TEILWEISE` | — |
| Beziehungsrecherche im Gedächtnispfad | `IMPULS-BEZIEHUNGSRECHERCHE` | — |
| Zwei herrenlose `hash_dirty`-Keys | `HASH-DIRTY-WAISENKEYS` | — |
| `queues.py:111` ohne Gate | `HASH-DIRTY-SETZER-DRIFT` | Nicht „ohne Log": das Kürzel `dirty_flag` steht in einer Sammelzeile. Fünf Setzer, **drei** Bauarten |
| Telegram `shadow_delivery` | `TELEGRAM-SHADOW-TYP-TOT` | Zweig war **nie** erreichbar — der Broadcast hieß immer `shadow_impuls` |
| Leere Abschnittsüberschrift | `DESTILLATION-LEERE-UEBERSCHRIFT` | — |
| Duplikat-Verstärkung auf dem user-Pfad | Nachtrag in `KZG-SEGMENT-DUPLIKAT` | Zeitlich begrenzt, klingt mit der TTL ab |
| Client-Impuls-Zweig ohne Testlauf | — | **Erledigt am selben Tag**, am laufenden Client sichtbar geprüft |
