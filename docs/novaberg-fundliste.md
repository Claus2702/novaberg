# Novaberg — Fundliste

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Rohe, noch unklassifizierte Funde aus laufender Arbeit
**Stand:** 26. Juli 2026
**Pfad:** novaberg/docs/novaberg-fundliste.md

Was beim Bauen an anderer Stelle auffällt, landet hier — **eine Zeile mit Datum**. Kein Bug-Name, keine Priorität, keine Klassifizierung, keine Diskussion. Der Zweck ist, einen Fund festzuhalten, ohne die laufende Arbeit dafür zu unterbrechen.

Diese Liste ist bewusst roh. Von hier wandern Einträge nach `novaberg-bugs.md` oder `novaberg-backlog.md` und bekommen dort eine stabile ID; die Zeile hier wird beim Umzug entfernt.

---

## Stichtage

Analog zum Kraft-1-Stichtag: ab wann eine Partition brauchbar ist. Kein Backfill; was davor liegt, bleibt falsch und wird nicht gelesen.

- **assistant-Partition (`beobachter='assistant'`) — brauchbar ab 2026-07-26 13:03:30 UTC.** Davor verdichtete Pfad 2 den User-Prompt statt Novas Antwort und legte denselben Satz wie Pfad 1 ab. Der letzte fehlerhafte Eintrag stammt aus Turn `6bc55996748f48dc9a2cfeaf26dc44e2` um 12:59:20 UTC; der erste korrekte ist `kzg:meister:nova:1785071056367`.

---

## Offen

*(leer — alle Einträge vom 26.07.2026 sind nach `novaberg-bugs.md`, Sektion Chat 110, umgezogen und tragen dort stabile IDs)*

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
