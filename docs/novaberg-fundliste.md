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

- 2026-07-26 — Zwei Redis-Keys `hash_dirty:meister` und `hash_dirty:nova:meister` liegen ohne Leser und ohne Löscher; der `CharakterAgent` prüft ausschließlich `hash_dirty:meister:nova`.
- 2026-07-26 — `agents/kzg/queues.py:111` setzt `hash_dirty` ohne `PIXIE_AKTIV`-Gate und ohne Log-Zeile, anders als die vier übrigen Setzer.
- 2026-07-26 — `agents/charakter/destillation.py:127-129` trägt die Abschnittsüberschrift „Prompts — Nova (eigene Perspektive)" ohne Inhalt darunter.
- 2026-07-26 — Nach dem Verdichtungs-Fix verstärkt der user-Pfad neuerdings 1–2 Nachbarn je Turn; die Treffer sind die vor dem Fix erzeugten Duplikate. Klingt mit deren TTL ab, ist aber bis dahin ein verfälschtes Gewicht.
- 2026-07-26 — Zwei Salienz-Segmente derselben Nova-Antwort können denselben Kernsatz erzeugen; es entstehen dann zwei KZG-Einträge mit identischem `inhalt` und verschiedenen Themen.
- 2026-07-26 — Ein assistant-Destillat hält eine Handlung fest, die nicht stattgefunden hat (behauptetes Notiz-Update); `notizen` und `fakten` zeigen im selben Zeitraum null Schreibvorgänge. Die assistant-Partition übernimmt damit behauptete Handlungen als Verhaltensbeleg.
- 2026-07-26 — Ein Pixie-Impuls erzeugt zwei bis drei identische Kernsätze: Der Segmentierer zerlegt den Fachtext, aber jedes Segment liefert dasselbe Destillat und damit einen eigenen KZG-Eintrag.
- 2026-07-26 — Der Impuls-Turn erzeugt zwei KZG-Einträge mit `beobachter='assistant'` (AgentGraph: entstehender Gedanke, CharacterGraph: gesprochener). Ein Nutzer-Turn erzeugt dagegen je einen mit `user` und `assistant`. Ob der Impuls beide tragen soll, ist nicht entschieden.
- 2026-07-26 — Der Salienz-Node schreibt in keinem Graphen ins `pipeline_log`. Die Bewertung, das Nadelöhr für alles, was ins Gedächtnis kommt, ist forensisch unsichtbar.
- 2026-07-26 — Ein Pixie-Impuls kann Recherche über die Beziehung zwischen Nutzer und Assistentin selbst in den Gedächtnispfad tragen. Ob solche Themen in den Shadow-Stack gehören, ist nicht entschieden.
- 2026-07-26 — Der Client wurde nur gelesen und kompiliert, nicht ausgeführt: Im `server`-Image gibt es kein GTK, der Impuls-Zweig in `stream_handler.py` hat keinen Testlauf.
- 2026-07-26 — Der Telegram-Bot behandelt einen Nachrichtentyp `shadow_delivery`, den der Server nirgends erzeugt; der Zweig ist tot. Ebenso nennt `client/ui/stream_handler.py` ihn im Auffangzweig-Kommentar.
