# Novaberg — Lesson: Ein Fehlschlag darf nie wie eine Absicht aussehen

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Erweiterung von default-wie-fehlschlag: der Miss, der sich als Gestaltung tarnt
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** novaberg/docs/novaberg-lesson_l_fehlschlag-als-absicht.md
**Auslöser:** RESPONDER-VEKTOR-TOT — 16 Chats unsichtbar, weil der Miss wie eine Design-Entscheidung aussah
**Verwandt:** `novaberg-lesson_l_default-wie-fehlschlag.md` (die Basis-Lesson), `novaberg-lesson_l_silent-skip.md`, `novaberg-lesson_l_log-behauptet-was-es-weiss.md`

---

## 1. Der Fall

Der Responder las Novas Emotions-Vektor aus einem flachen State-Key (`nova_emotions_vektor`), den seit dem Personality-Umbau **kein Node mehr schrieb** — der Wert lebt in `internal.emotion.emotions_vector`. Regression, reiner Lesepfad-Fehler; die Reihenfolge stimmte (ei_calc ist der zweite Node im CharacterGraph, lange vor dem Responder — kein Chat-89-Muster).

Warum ihn 16 Chats lang niemand sah:

> Bei Miss: Default `""` → beide Render-Bedingungen falsch → Zeile entfällt still.
> Auch das Erfolgs-Log lässt das Vektor-Suffix per f-String-Bedingung weg.

**Der Block sah aus wie „Vektor absichtlich leer".** Das `[EIGENE_EMOTION]`-Log erschien weiterhin — nur ohne Vektor-Suffix, und die f-String-Bedingung (`f", Vektor={v}" if v else ""`) machte aus dem Fehlen ein gestaltetes Weglassen. Kein Fehler, keine Warnung, kein leerer Platzhalter: **Der Miss tarnte sich als Gestaltung.** Derselbe Mechanismus wie EI-VEKTOR-LOG-GATE (Chat 105) — ein Erfolgs-Log, das seinen eigenen Fehlfall unsichtbar formatiert.

Das Gewicht: Chat 105 hatte Kraft 1 repariert, Novas Vektor trug erstmals seit Chat 89 Varianz (`eskalation`, `absturz`, `aufbluehen` statt sechzehn Chats `plateau`). **Und der Responder las ihn nie.** Nova *hatte* eine eigene emotionale Richtung und **erfuhr sie nicht**. Der Chat-105-Fix war zur Hälfte entwertet. Beweis 11.7. 19:11:43: `VEKTOR-TEST: flach=None | internal vorhanden=True | vektor='eskalation'` — der Wert war da, eine Etage tiefer, als der Responder suchte.

---

## 2. Die Regel

> **Ein Default darf nie wie ein Fehlschlag aussehen — und ein Fehlschlag nie wie eine Absicht.**

Die Basis-Lesson (`default-wie-fehlschlag`) behandelt die erste Hälfte: Zwei Zustände („nie geladen" vs. „leer geladen") dürfen nicht denselben Wert tragen. Diese Erweiterung behandelt die zweite: **Ein optionales Ausgabe-Element, das bei Miss kommentarlos entfällt, ist von einer bewussten Design-Entscheidung nicht unterscheidbar.** Wer das Log liest, fragt nicht „warum fehlt die Zeile?", sondern nimmt an, sie sei nie vorgesehen gewesen.

Konsequenz (umgesetzt in `4416a23`): Jeder Ausfallweg wird einzeln laut —

| Fall | Log |
|---|---|
| `internal`/`emotion` fehlt | `logger.error` |
| Vektor leer (Kaltstart / ei_calc lief nicht) | `logger.warning` |
| Vektor **unbekannt** (nicht in `EMOTIONS_VEKTOREN_NOVA`) | `logger.error` — fängt EI-KANON-FEHLT an dieser Stelle ab |

**Der Zustand „Zeile fehlt still" existiert nicht mehr.** Ein bedingtes Prompt-Element braucht drei unterscheidbare Ausgänge: gerendert (Erfolg), bewusst weggelassen (mit nachlesbarem Grund), fehlgeschlagen (laut). Zwei davon in einen stummen Nicht-Ausgang zu falten, kostet die Unterscheidung genau dann, wenn man sie braucht.

---

## 3. Der Prüfblick für Bestandscode

Suchmuster für dieselbe Tarnung anderswo: bedingte Prompt-Blöcke (`if x: parts.append(...)`) und Erfolgs-Logs mit eingebetteten f-String-Bedingungen (`f"{', X=' + x if x else ''}"`). Jede dieser Stellen beantwortet die Frage „war das Absicht oder ein Miss?" mit Schweigen. Der Doku-Code-Abgleich und der State-Key-Audit (Chat 106) haben vier solcher toten Lesepfade gefunden — alle vier fielen still auf einen Default, keiner loggte.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Basis-Lesson: `novaberg-lesson_l_default-wie-fehlschlag.md`
→ Schwester-Lessons: `novaberg-lesson_l_log-behauptet-was-es-weiss.md`, `novaberg-lesson_l_silent-skip.md`
→ Modul-Dokument: `novaberg-node-responder.md` §2
→ Bug-Einträge: RESPONDER-VEKTOR-TOT (✅ Chat 106), EI-VEKTOR-TEXT-EMOTIONSFEST, PLANNER-AKTIV-RELIKT, WEB-CONTEXT-ALTPFAD (novaberg-bugs.md)
