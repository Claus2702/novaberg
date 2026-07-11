# Novaberg — Lesson: Ein Analyse-Upgrade ersetzt keine Messung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Ein stärkeres Modell liest denselben Code und kommt zum selben Schluss
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** novaberg/docs/novaberg-lesson_l_analyse-ersetzt-keine-messung.md
**Auslöser:** THINKER-SELFTRIGGER-KANALLOS — der Vorschlag, den Beweis durch ein besseres Modell zu ersetzen
**Verwandt:** `novaberg-lesson_l_stichprobe-trifft-den-pfad.md`, `novaberg-lesson_l_quelle-vor-destillat.md`, `novaberg-lesson_l_default-wie-fehlschlag.md` §5 („Eine Zahl schlägt drei Hypothesen")

---

## 1. Der Fall

Als der Self-Trigger-Kanalbeweis anstand, war Brudis Herleitung lückenlos: undeklarierter Channel, StateGraph rekonstruiert pro Node aus den Channels, der Wert MUSS an der Node-Grenze verworfen werden — die Mechanik stand sogar als Warnung im selben Block des TypedDict (`lzg_resonanz`-Kommentar in `state.py`). Meister schlug vor, den Fehler „am Code zu ermitteln" — mit einem stärkeren Modell (Fable 5 für Brudi).

**Claude bestand auf der Messung.** Begründung: Wir haben eine *Herleitung*, keine *Messung*. Und dreimal diese Woche gab eine korrekte Code-Analyse die falsche Antwort:

- **Chat 89:** Der Reihenfolge-Tausch (ei_calc vor Enricher) war korrekt analysiert und bewusst entschieden — dass er `raw_turns` für den EI-Calc leerte, sah die Analyse nicht. 16 Chats Blindflug.
- **Chat 101:** Fünf saubere Live-Turns, korrekt beobachtet → „Loop existiert nicht." Die Stichprobe traf den Pfad daneben.
- **Chat 105:** Drei plausible Hypothesen zum Plateau-Vektor, alle korrekt auditiert, mit Belegen — alle drei irrelevant. Eine Diagnose-Log-Zeile (`nova_turns=0`) erledigte sie in einem Log-Auszug.

Der Doppel-Fehlschlag hängt an flakigem Modellverhalten und ist nicht bestellbar. Also wurde der Zweig **deterministisch erzwungen** (`_FORCE_DOPPELFEHLSCHLAG`, temporär, vor dem Commit entfernt). Der Beweis kam in zwei Log-Zeilen (11.7. 18:35:22): Thinker `vorhanden=True`, Tribunal eine Kante später `vorhanden=False`.

---

## 2. Die Regel

> **Ein stärkeres Modell liest denselben Code und kommt zum selben Schluss. Wenn das Problem das Fehlen einer Messung ist, ändert die Analysequalität nichts — nur die Messung.**

Die Unterscheidung, wann welches Werkzeug zahlt:

| Situation | Richtiges Werkzeug |
|---|---|
| Muster über viele Dateien finden (Audits, Abgleiche, Sweeps) | **Besseres Modell** — dort zahlt sich Analyse-Kapazität aus |
| Eine konkrete Verhaltens-Hypothese bestätigen/widerlegen | **Messung** — eine Diagnose-Zeile, ein erzwungener Pfad, ein Log-Auszug |

Der Zwei-Zeilen-Beweis kostete zwei temporäre Log-Zeilen und ein temporäres Force-Flag. Jede weitere Analyse-Runde — egal wie stark das Modell — hätte dieselbe Herleitung eleganter formuliert und denselben Restzweifel behalten. Die Herleitung war ja richtig; das wusste man aber erst NACH der Messung.

---

## 3. Warum die Versuchung wiederkehrt

Ein Analyse-Upgrade fühlt sich wie Fortschritt an und ist sofort verfügbar; eine Messung verlangt, den Pfad zu betreten (Provokation, Force-Flag, Diagnose-Zeile) — das wirkt wie Umweg. Aber die Woche zeigte das Muster dreifach: Die korrekte Analyse ohne Messung produziert selbstbewusste falsche Antworten, und die kosten Chats, nicht Minuten. *Erst die Zeile, dann der Fix* — und wenn der Pfad nicht von allein kommt, wird er erzwungen.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_stichprobe-trifft-den-pfad.md`, `novaberg-lesson_l_log-behauptet-was-es-weiss.md`
→ Bug-Eintrag: THINKER-SELFTRIGGER-KANALLOS (✅ Chat 106, novaberg-bugs.md)
