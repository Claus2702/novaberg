# Novaberg — Konzept: Hermes als Ausführungs-Substrat (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-hermes-substrat_k.md`](novaberg-hermes-substrat_k.md) · Ausarbeitung: [`novaberg-hermes-substrat_t.md`](novaberg-hermes-substrat_t.md) · Diskussion und Ergänzungen: [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen.

---

## 11. Messfragen — Phase 0

Diese Fragen sind am laufenden Testcontainer zu beantworten, bevor das
Anbindungs-Konzept geschrieben wird. Sie sind **Messungen**, keine Analysen.

| Nr. | Frage | Blockiert |
|-----|-------|-----------|
| **M0** | Startet der Gateway ohne konfigurierte Plattform, und tickt der Dispatcher? | Naht B insgesamt (5.1) |
| **M1** | Wieviel Struktur nimmt ein Kanban-Worker aus den Feldern auf, wieviel muss Prosa im `--body` sein? | Auftragsbildungs-Node (7.2) |
| **M2** | Ist `complete --result` strukturierbar? Kann ein Ausgabeschema vorgegeben werden? | Verifikations-Node (7.2) |
| **M3** | Welche Felder liefert `hermes skills list` maschinenlesbar? Reicht das für einen Körperschema-Knoten? | Körperschema (8.3) |
| **M4** | Wie erfährt ein Aufrufer von `block`? Nur durch Polling, oder gibt es einen Rückkanal? | Rückfragen (7.6) |
| **M5** | Läuft lokale Ollama über den Custom-Endpoint-Pfad? Welches Tool-Calling-Verhalten zeigt `qwen36-cpu`? | Modellwahl (5.5) |
| **M6** | Queue-Tiefe und Wartezeiten an Port 11435 vor und nach Anschluss des dritten Verbrauchers. | Dauerbetrieb (5.6) |

**Reihenfolge:** M0 und M5 zuerst — beide ohne LLM-Entscheidung prüfbar
beziehungsweise Voraussetzung für alles Weitere. M1–M4 danach. M6 erst im
Dauerbetrieb.

**Wichtig:** Ein schwaches Modell lässt Hermes kaputt aussehen. Tool-Calling ist
die Disziplin, an der billige Modelle zuerst brechen — oft still, mit halb
gefüllten Argumenten statt einer Fehlermeldung. Wird M5 vor M1–M4 nicht sauber
beantwortet, misst man das Modell und nicht Hermes, und kann die beiden
hinterher nicht auseinanderhalten.

---

> **Hinweis zur Aufteilung (19.09.2026):** §12 *Offene Entscheidungen* — die Entscheidungen H1–H8, die von diesen Messfragen abhängen — steht in [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md), Abschnitt C.
