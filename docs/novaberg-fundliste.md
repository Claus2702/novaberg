# Novaberg — Fundliste

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Rohe, noch unklassifizierte Funde aus laufender Arbeit
**Stand:** 28. Juli 2026, Chat 115 (drei Funde aus der Session-Verlaufs-Prüfung ergänzt)
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

- **2026-07-27** — `memory/kzg.py` reicht beim `shadow_queue_push` **kein `prioritaet`** und nimmt damit den Default 0.0 — und zwar direkt unter dem Tor `if salienz >= KZG_SALIENZ_HIGH`. Die Zwillingsstelle in `agents/kzg/queues.py` übergibt `prioritaet=neue_salienz` korrekt. Gemessen in `shadow_queue:<user>`: acht `vertiefen`-Aufträge, alle mit `prioritaet: 0.0`, obwohl jeder nur entstand, weil seine Salienz ≥ 0.7 war; die zwei `nachfragen`-Aufträge (aus der anderen Stelle) tragen 0.7. Die beiden Schreiber sind am `kontext`-Feld unterscheidbar — `queues.py` legt den `kern` ab, `kzg.py` die `zusammenfassung`. Wirkung: Ein Auftrag aus hoher Salienz tritt mit 0.0 an und verliert gegen jede periodische Aufgabe.
- **2026-07-27** — `services/pixie/dispatch.py` liest beim Bau des `AgentState` `eintrag.get("salienz", 0.0)`. Die Shadow-Queue schreibt das Feld aber als `prioritaet`; `salienz` schreibt nur die Promotion-Queue. `kontext["salienz"]` ist damit für **jeden** Shadow-Auftrag 0.0, auch bei echten 0.7. Eine Datei weiter macht `services/pixie/kandidaten.py` es richtig und liest beide Namen. Zusatzbefund: `kontext["salienz"]` wird nirgends gelesen (Grep leer, Positivkontrolle auf dasselbe Muster mit `user_id` = 34 Treffer).
- **2026-07-27** — Ein Queue-Auftrag für einen **nicht registrierten** Agenten gewinnt den Heartbeat und verdrängt laufende Arbeit. `services/pixie/router.py` bildet `vertiefen` → `vertiefung` und `nachfragen` → `nachfragen` ab; **beide Agenten existieren nicht**. Gemessen an der über `discover_agents()` befüllten Registry: 15 Agenten, `recherche` und `wiedervorlage` darunter, die zwei nicht. Beobachtet am selben Tag: `nachfragen` (Prio 0.97) gewann dreimal gegen `charakter_hash` (Prio 0.3) und scheiterte jedes Mal an `Agent 'nachfragen' nicht in Registry` — nach drei Fehlversuchen verworfen, sechs Minuten ohne anderen Job (Server-Log 13:19–13:23 UTC). Die fehlenden Agenten sind **kein Bug, sondern Roadmap** (`PIX-MIG-7`, dort aber nur einer von zweien); der Befund ist die Verdrängung: Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen. **Kopplung beachten:** Wird nur die `prioritaet` oben repariert, gewinnen acht liegengebliebene `vertiefen`-Aufträge sofort den Heartbeat und laufen ins Leere — der Nullwert hält sie heute ruhig.
- **2026-07-27** — `CharakterAgent` (Prio 0.3) wird ausgehungert, solange die Queue läuft: `lzg_promotion` steht bei 0.97, jeder Turn erzeugt welche. Vier Heartbeats in Folge ging der Charakter leer aus, obwohl `hash_dirty` gesetzt war. Vermutlich gewollt (Profil-Destillation ist nicht dringend) — als Verhalten aber nirgends festgehalten.
- **2026-07-28** — Doku-Hygiene, **gemessen**: Drei Dokumente vergeben Überschriften mehrfach und erzeugen damit mehrdeutige Anker — `novaberg-backlog.md` (3× „Phasen-Übersicht", 3× „Hintergrund", 2× „Auswirkung auf Akten-Vision"), `novaberg-roadmap.md` (je 2× „Dokumentation", „Backlog", „Bugfixes") und `novaberg-thinking-skills_k.md` (2× „Wetter-Anfragen"). Ein Zähler über alle `#`-Zeilen meldet zusätzlich `novaberg-memory-synapsen_k.md` mit 12 Treffern — das sind **Python-Kommentare in einem Code-Block**, kein Befund. Wer das nachmisst, muss Code-Fences überspringen.
- **2026-07-28** — `server/agents/kzg/AGENT.md` ist nie gegen den Code geprüft worden. Der KZG-Agent hat seit der Erstfassung Nodes gewonnen und verloren (`magnete_aufloesen` kam, `aehnlichkeit_pruefen` ist gelöscht) — ob die AGENT.md das trägt, ist offen. Gilt sinngemäß für die übrigen AGENT.md-Dateien, die ebenfalls nie systematisch abgeglichen wurden.
- **2026-07-28** — Der LZG-Zweig der emotionalen Gravitation rechnet den Verfall **dreifach**. `ei/gravitation.py` liest die Spalte `gewicht_decay` — den vom Decay-Lauf bereits materialisierten Wert —, schickt sie durch `effektives_gewicht_berechnen()` (Ebbinghaus, live) und multipliziert zusätzlich `_zeit_decay_faktor()` (eigener Verfall, Halbwert 180 Tage). Der Docstring der zweiten Funktion sagt wörtlich „Der Decay wird live berechnet, nie gespeichert" — für `lzg_knoten` gilt das seit der Materialisierung nicht mehr. Die Funktion stammt aus dem alten `langzeitgedaechtnis`-Modell (Tabelle steht heute auf 0 Zeilen); die Query mischt zwei Gedächtnismodelle mit gegensätzlicher Decay-Philosophie. Wirkung heute klein, weil kein Knoten älter als einen Tag ist. Berührt `novaberg-convention-abgeleitete-werte.md` §3(5): Die Kurve wird genau einmal angewandt.

- **2026-07-28** — `memory/session.py:313` `session_context_build()` hat **keinen Aufrufer**. Sie setzt Zusammenfassung und Turns zu einem `[Aktuelle Unterhaltung]`-Block zusammen — genau die Aufgabe, die der Responder seit dem Verlaufs-Umbau selbst und in anderer Form erledigt (`graph/nodes/responder.py`, Turn-Paare unter `----- Turn n von m -----`). Gemessen repoweit über alle Dateitypen: **zwei** Treffer, beide Definition bzw. Re-Export (`memory/__init__.py:39`). Positivkontrolle auf dasselbe Muster mit `session_turns_retrieve`: 52 Treffer in 27 Dateien. Der Befund ist nicht der tote Code, sondern die Falle: Wer den Gesprächskontext nachvollziehen will, findet zuerst diese Funktion und liest eine Formatierung, die kein LLM mehr sieht. **Anhängend:** `SESSION_MAX_TURNS` (=20) wird ebenso exportiert, steht im Code aber an genau einer Stelle — dem `except`-Zweig von `session_summarize_if_needed` (`session.py:202`), also im Notpfad bei gescheitertem LLM-Call. Der reguläre Deckel heißt `SESSION_SUMMARIZE_AT` (=25). Der Name der exportierten Konstante behauptet, sie sei die Regel.

- **2026-07-28** — Novas Eigen-Impulse zählen in die Zusammenfassungs-Schwelle, **erscheinen aber nie im Gesprächsverlauf**. Ein Impuls läuft durch den CharacterGraph; der Dispatcher schreibt dafür einen `assistant`-Session-Turn ohne `user`-Gegenstück. Beide Verlaufs-Bildner überspringen alleinstehende `assistant`-Turns: der Paar-Bildner im Responder (`graph/nodes/responder.py:672-674`) und `format_session_turns_numbered` (`memory/session.py:283-286`), das GV-Node, Router, Perzeption und vier Agenten-Klassifikationen lesen. *(Zeilennummern gemessen 28.07.2026.)* Gemessen am 28.07.2026, 20:15 UTC: `session:<user>:<character>:turns` = 20 Einträge, davon **12 `assistant` gegen 8 `user`**; der Responder-Prompt desselben Fensters trug 7 Turn-Paare. Vier Einträge zählen damit gegen `SESSION_SUMMARIZE_AT`, ohne je im Prompt gestanden zu haben — bei Erreichen der Schwelle schneiden sie echte Wortwechsel weg. Ob ein Impuls in den Verlauf gehört, ist eine offene Frage; dass er ihn verkürzt, ohne darin vorzukommen, ist keine.

- **2026-07-28** — `novaberg-roadmap.md` trägt in der Kopfzeile „**Stand:** Chat 109, 26. Juli 2026", während der Inhalt bis Chat 114 reicht und die Fußzeile „Aktualisiert in Chat 114 (28.07.2026)" nennt. Es ist dieselbe Drift, die der Klammerkommentar zwei Zeilen darunter für die Zeit davor festhält (der Kopf stand bis Chat 109 auf „Chat 93") — beim Schließen der Vier-Chat-Lücke ist sie nicht mitgezogen worden. Wer nur den Kopf liest, hält fünf Sitzungen für undokumentiert und sucht die Arbeit woanders.

- **2026-07-28** — Der Router-Miss-Pfad in `services/pixie/scheduler.py` kehrt zurück, **ohne `abschluss()` zu rufen**. Ein periodischer Kandidat, für den kein Agent gefunden wird, behält damit sein `next_run` und wird beim nächsten Heartbeat erneut Kandidat. Ohne Aging war das harmlos — er verlor gegen die Queue. Mit dem Aging (Chat 113) wächst sein Zuschlag bis zum Deckel, und er gewinnt dann **jeden** Zyklus, ohne je zu laufen. Heute nicht akut: Alle sieben vorhandenen `pixie:schedule:*`-Einträge sind routebar, sechs über die Tabelle, `ziel_decay` über die Namensgleichheit. Der Fund ist die Falle für den nächsten Agenten ohne Routing-Eintrag.

---

## Ohne Gegenstand — der Hinweis überlebte, die Frage nicht

Diese Einträge halten **einen Verlust** fest, keine Aufgabe. Ihr Gegenstand steht in keinem Repo-Dokument mehr; sie sind ohne Rückgriff auf Quellen außerhalb des Repos nicht bearbeitbar. Sie stehen hier getrennt, damit „Offen" bedeutet, was es sagt — vier von fünfzehn Zeilen sahen sonst nach Arbeit aus, die niemand aufnehmen kann.

**Wer eine davon anfasst, erhebt sie neu.** Die alte Zeile ist kein Ausgangspunkt, sondern nur der Hinweis, dass hier einmal etwas war.

- **2026-07-28** — `novaberg-kzg-liberalisierung_k.md` §3.6 und §5 sind als überholungsbedürftig notiert. **Der Grund ist nirgends festgehalten** — das Dokument trägt an beiden Stellen keine Markierung, und was genau dort nicht mehr stimmt, steht in keinem Repo-Dokument. Vor der Bearbeitung neu ermitteln.

- **2026-07-28** — Eine Manager-Signatur-Drift „über 19 Dateien" wird geführt, **ohne dass das Kriterium irgendwo steht**. Ein Nachmessen am 28.07. fand mit selbst gewählten Mustern 4 Dokumente. Ob 19 überholt ist oder das Muster zu eng, ist **nicht entscheidbar** — die Zahl steht ohne die Abfrage, die sie erzeugt hat. Vor der Bearbeitung ist der Fund neu zu erheben; die alte Zahl ist kein Ausgangspunkt, sondern nur ein Hinweis, dass hier etwas war.

- **2026-07-28** — Vier in Chat 107 identifizierte Lessons sind nie als Datei angelegt worden. **Welche vier, steht in keinem Repo-Dokument** — der Inhalt liegt nur im Protokoll außerhalb. Auf der Platte liegen 44 `_l`-Dateien. Diese Zeile hält den Verlust fest, nicht die Aufgabe: Ohne Rückgriff aufs Protokoll ist sie nicht bearbeitbar.

- **2026-07-28** — `broadcast()` steht seit Chat 107 als ungeprüfter Punkt, **ohne dass die Frage dazu festgehalten wäre**. Wie bei der Signatur-Drift: Der Hinweis überlebte, die Fragestellung nicht.

---

## Umgezogen — Chat 114 (28.07.2026)

- **2026-07-27, nachgemessen 27.07. abends** — `novaberg-architecture.md` §7 nennt „**72 Dateien**" in `docs/`; tatsächlich sind es **130** (`ls docs/*.md`). Die Zahl im ursprünglichen Fund lautete 123 und war beim Nachmessen desselben Tages schon überholt — eine Zählung ohne Messdatum ist hier wertlos. **Teilkorrektur:** Die Behauptung „kein einziges `novaberg-convention-*.md` steht im Index" trifft nicht zu. Von sechs Konventionsdateien wird **eine** genannt (`novaberg-convention-event-model.md`, als Querverweis im Fließtext, nicht als Index-Eintrag). Die anderen fünf fehlen.
  → **Erledigt Chat 114.**

- **2026-07-27** — `novaberg-bugs.md` führt `SHADOW-DELIVERY-DATENVERLUST` mit einem Beleg auf `services/shadow_delivery.py:514-522`, der dort nicht mehr steht; der Chat-110-Umbau hat den Pfad ersetzt. Restrisiko besteht weiter, aber an anderer Stelle und an `BROADCAST-VERSCHLUCKT-FEHLER` hängend.
  → **Erledigt Chat 114.**

- **2026-07-27, nachgemessen 27.07. abends** — Mehrere Dokumente nennen eine „Promotions-Schwelle 0.8". Im Code gibt es keine 0.8; das Tor ist `KZG_SALIENZ_HIGH = 0.7` in `agents/kzg/queues.py`, `_aufgabe_aus_intention`-Nachbarschaft. **Die ursprüngliche Aufzählung war unvollständig und in einem Punkt irreführend:**
    - Nicht genannt war `novaberg-mem-lzg.md` („Salienz ≥ 0.8 → Promotion-Queue" im ASCII-Diagramm).
    - Die Zeilennummern für `novaberg-backlog.md` (2940, 3544) stimmen nicht mehr; die Stellen liegen heute bei 2947 und 3556. Das Kriterium trägt weiter, die Nummern nicht.
    - **`novaberg-memory-synapsen-p4-entscheidungen_k.md` darf nicht mitkorrigiert werden.** Dort steht die 0.8 in einem historisch richtigen Satz: dass `queues.py` *von* `PROMOTION_THRESHOLD` (0.8) *auf* `KZG_SALIENZ_HIGH` (0.7) umgehängt wurde. Wer über alle `0.8`-Vorkommen greppt und ersetzt, tilgt eine zutreffende Aussage.

  **Kriterium statt Aufzählung:** zu korrigieren ist jede Stelle, die 0.8 als *geltende* Schwelle beschreibt — nicht jede, die die Zahl nennt.
  → **Erledigt Chat 114.**

---
## Umgezogen — Chat 112 (27.07.2026)

Die Messung gehörte auch hier zum Umzug — bei jeder der vier Zeilen hat sie etwas an der Notiz korrigiert.

| Fundlisten-Zeile | Wurde zu | Korrektur beim Umzug |
|---|---|---|
| Themen aus dem `[LAGEBILD]` übernommen | `SALIENZ-PROMPT-NUTZER-SCHABLONE` | Kein eigener Defekt, sondern dieselbe Ursache: Die Regel wies an, den Hintergrund zu bewerten. Mit dem Rollen-Switch behoben und am Turn vom 21:41 UTC gegengemessen |
| Verdacht: Salienz bewertet den Gesamtzusammenhang | `SALIENZ-PROMPT-NUTZER-SCHABLONE` | Der Verdacht traf zu, aber **die Begründung war die falsche**: Nicht der Gesamtzusammenhang wurde bewertet, sondern das Lagebild — die Anweisung war invertiert, nicht unscharf |
| `pending_write` trägt das Segment nicht weiter | — **erledigt** | Der Fund war zu dem Zeitpunkt richtig und ist seit Bauteil 1a behoben. Belegt: `graph/nodes/salience.py` legt `segment` in `daten` ab, `agents/kzg/verdichtung.py` liest es aus `state["parameter"]`. Die Zeile stand noch offen, weil sie beim Bauen nicht mitgezogen wurde |
| `uvicorn --reload` überwacht nur `.py` | — **gehört nicht ins Repo** | Der Befund stimmt und ist nachgezogen, aber am richtigen Ort: Er beschreibt die **Entwicklungsumgebung**, nicht das Projekt. Nach `CLAUDE.md` bleibt solches Wissen außerhalb — ersatzlos gestrichen, nicht verloren |

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
