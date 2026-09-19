# Novaberg — Meinungsbildung (Opinion Formation) — Umsetzung und Ausarbeitung

**Teil 2 von 3 — Umsetzung und Ausarbeitung.** Absicht und Planung: [`novaberg-thinking-opinion_k.md`](novaberg-thinking-opinion_k.md) · Entscheidungen und offene Fragen: [`novaberg-thinking-opinion_e.md`](novaberg-thinking-opinion_e.md)

---

## Bisheriger Kopf

*Der Stands-Kopf des Konzepts bis zur Aufteilung am 19.09.2026, ungekürzt.*

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Wie Nova zu einer eigenen Haltung kommt
**Stand:** 5. September 2026, 15:05 UTC (**§2a neu — woher (A) kommt**: Setzung des Eigentümers, dass Prägung und Faszination die Meinungsbildung tragen. Die Grenze zwischen (A) und (B) läuft entlang der **Quelle** — Fäden und Stränge gegen Recherche —, und die Meinung liegt **eine Stufe unterhalb** der valenzblinden Faszination: Die Valenz sitzt im Strang und ist dort **gebaut und im Bestand**, neun Stränge. Vorbehalt: alle neun tragen eine **positive** Valenz). Davor 3. September 2026, 21:30 UTC (**der Ort fuer die Praemisse-Kante existiert** — `abstrakt_knoten` traegt seit heute einen Typ-Diskriminator `art`; die Qualitaetsseite ist gefuellt, die Werteseite traegt keine Zeile, und `praemisse_knoten_id` zeigt weiterhin auf `lzg_knoten`, wo die abstrakten Knoten **nicht** liegen. §5a). Davor 30. August 2026 (die Fundamente gegen den Bestand gehalten: Pixie läuft, das Substrat heißt `lzg_*` und trägt 3.260 Knoten; dazu die Naming-Wache — `valenz` ist an die GV-Achse vergeben). Davor: Erstfassung
**Pfad:** novaberg/docs/novaberg-thinking-opinion_k.md
**Status:** Konzept. Skelett steht, Kalibrierung offen. Bewusst offene Punkte sind durchgehend mit ⬜ markiert und in §10 gesammelt.
**Verwandt:** novaberg-thinking-drive_k.md · novaberg-thinking-frames_k.md · novaberg-memory-synapsen_k.md · novaberg-node-gv_k.md · novaberg-node-tribunal.md · novaberg-pixie.md · novaberg-ei.md

---

## 5a. Was davon gebaut ist (30.08.2026)

**Der Speicher steht: `lzg_knoten_haltung`.** Eine additive Annotation auf `lzg_knoten`, kein zweiter Store — und eine eigene Tabelle statt Spalten, weil ein Knoten **mehrere** Ladungen trägt (je Eigenschaft eine). Genau dieser Widerspruch unterscheidet die Haltung vom Schalter, und Spalten könnten ihn nicht tragen.

| Feld | Was es trägt |
|---|---|
| `knoten_id`, `eigenschaft` | der Gegenstand; leere Eigenschaft = die Sache als ganze (die grobe Stufe aus §9) |
| `ladung` | Vorzeichen **und** Stärke, −1.0 bis +1.0, als `CHECK` im Schema |
| `emotion`, `quelle` | die Emotion dahinter; die Herkunft ist **Pflicht** — ohne sie ist eine Haltung nicht nachrechenbar |
| `praemisse_knoten_id` | die Prämisse als **Kante**, wie §5 sie verlangt. Bis es Werte-Knoten gibt, bleibt sie leer — **und seit dem 03.09.2026 gibt es den Ort dafür**: `abstrakt_knoten` trägt einen Typ-Diskriminator `art` mit den Werten `qualitaet` und `wert`. Die Qualitätsseite ist gefüllt (sechs gesetzte Dimensionen, 25 profilierte Träger), **die Werteseite trägt keine Zeile.** Achtung beim Anschluss: Der Fremdschlüssel zeigt heute noch auf `lzg_knoten`, die abstrakten Knoten liegen aber **nicht** dort — Grund und Messwert in `novaberg-memory-qualitaetsprofil.md` §3a |
| `staerke_roh` / `_decay`, `haeufigkeit`, `aktiv` | die Dynamik des Knotens (`F-VERFALL-1`): eine Haltung ist Gedächtnis, kein Faktum |

**Drei Entscheidungen, die im Code stehen:**

**Eine zweite Beobachtung ist kein zweiter Eintrag.** `UNIQUE (knoten_id, eigenschaft)`; die neue Ladung wandert mit halbem Gewicht in die vorhandene, `haeufigkeit` steigt, die Stärke wird auf 1.0 zurückgesetzt. Ein Ausreißer kippt damit keine gewachsene Haltung, eine wiederholte Erfahrung setzt sich trotzdem durch. Gemessen an einem echten Knoten: 0,8 dann 0,6 ergibt **+0,70 (×2)**.

**Die Netto-Haltung ist gewichtet, nicht gemittelt** (`net_stance`). Eine oft bestätigte Ladung wiegt schwerer als eine einmalige, eine verfallene weniger als eine frische — der Widerspruch bleibt im Ergebnis sichtbar, statt sich wegzukürzen. Beispiel aus dem Betrieb: *faszinierend +0,70 (×2)* gegen *schwer zu fassen −0,40* ergibt **+0,333**. **Die Charaktergewichtung aus §6 fehlt weiterhin** — bis dahin zählt allein die Erfahrung.

**Zwei Aktivitäten, und beide müssen gelten.** Der Graph löscht nicht, er lässt ruhen. Ein Knoten unter der Schwelle steht auf `aktiv = FALSE` und bleibt stehen — seine Ladung ebenso, und sie darf trotzdem nicht mehr sprechen. Der Leseweg verbindet deshalb mit dem Knoten und prüft **dessen** Aktivität mit. Ohne den Verbund hätte eine Haltung ihren Gegenstand überlebt, ohne dass irgendwo etwas falsch aussieht.

**Was fehlt, ausdrücklich:** ein **Erzeuger** (niemand schreibt Ladungen — die Bildung aus §4 ist nicht gebaut) und ein **Leser** im Turn (der Spreading-Pass fragt sie nicht ab). Die Schicht ist damit vollständig gebaut und vollständig ungenutzt; 19 Zeugen decken sie ab, Gegenprobe 2/1/3/1/1.

---
