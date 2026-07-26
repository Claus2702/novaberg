# Novaberg — Fundliste

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Rohe, noch unklassifizierte Funde aus laufender Arbeit
**Stand:** 26. Juli 2026, Chat 110
**Pfad:** novaberg/docs/novaberg-fundliste.md

Was beim Bauen an anderer Stelle auffällt, landet hier — **eine Zeile mit Datum**. Kein Bug-Name, keine Priorität, keine Klassifizierung, keine Diskussion. Der Zweck ist, einen Fund festzuhalten, ohne die laufende Arbeit dafür zu unterbrechen.

Diese Liste ist bewusst roh. Von hier wandern Einträge nach `novaberg-bugs.md` oder `novaberg-backlog.md` und bekommen dort eine stabile ID; die Zeile hier wird beim Umzug entfernt.

---

## Offen

- 2026-07-26 — Zwei Redis-Keys `hash_dirty:meister` und `hash_dirty:nova:meister` liegen ohne Leser und ohne Löscher; der `CharakterAgent` prüft ausschließlich `hash_dirty:meister:nova`.
- 2026-07-26 — `agents/kzg/queues.py:111` setzt `hash_dirty` ohne `PIXIE_AKTIV`-Gate und ohne Log-Zeile, anders als die vier übrigen Setzer.
- 2026-07-26 — `agents/kzg/verdichtung.py:30-37` legt `user_prompt` fest als Bewertungsobjekt unter dem Label „Eingabe des Nutzers" ab; `graph/nodes/salience.py:120-124` dreht dieselbe Belegung für `ei_calc_rolle == "character"` um.
- 2026-07-26 — `agents/charakter/destillation.py:127-129` trägt die Abschnittsüberschrift „Prompts — Nova (eigene Perspektive)" ohne Inhalt darunter.
