# Novaberg — Meinungsbildung (Opinion Formation) — Ausarbeitung

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-opinion_k.md`](novaberg-thinking-opinion_k.md) · Bauplan und Umstellung: keiner · Diskussion und Ergänzungen: [`novaberg-thinking-opinion_e.md`](novaberg-thinking-opinion_e.md) · Messungen: [`novaberg-thinking-opinion_m.md`](novaberg-thinking-opinion_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Der bisherige Kopf steht in `_m`.

---

## 5a. Was davon gebaut ist (30.08.2026)

*Hinweis zur Aufteilung in fünf Teile (19.09.2026):* Der Abschnitt ist dem Titel nach ein Baubericht; er beschreibt aber das Datenmodell der Meinungsschicht — Tabelle, Felder und die drei Entscheidungen, die im Code stehen — und bleibt deshalb in der Ausarbeitung. Einen eigenen Bauplan (`_b`) hat das Konzept nicht.

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
