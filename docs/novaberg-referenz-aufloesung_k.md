# Novaberg — Referenz-Auflösung (REF-KASKADE)

**Absicht:** Rückbezüge wie „das Pulver“ werden vor dem Retrieval aufgelöst — billige Schichten erzeugen Kandidaten, teure wählen unter ihnen aus, jede Schicht meldet einen Zustand statt eines Werts, das LLM schlägt nur vor und Python entscheidet, im Zweifel fragt Nova gezielt zurück, und der Responder sieht den umgeschriebenen Prompt nie.
**Stand:** 11. Juli 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Referenz-Auflösung (anaphorische Verweise)* ⚫; verwandt *Query Rewriting* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-referenz-aufloesung_t.md`](novaberg-referenz-aufloesung_t.md) · [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md) · [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md) · `novaberg-referenz-aufloesung_m.md` — keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-referenz-aufloesung_k.md §3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-referenz-aufloesung_t.md`](novaberg-referenz-aufloesung_t.md), `_b` ist [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md), `_e` ist [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md).

| § | Datei |
|---|---|
| 1 · 1.1 | `_k` |
| 2 · 3 · 4 | `_k` |
| 5 | `_t` |
| 6 (Schichten L0–L5) | `_t` |
| 7 · 7.1 · 7.2 · 7.3 | `_t` |
| 8 · 8.1 · 8.2 · 8.3 · 8.4 | `_b` |
| 9 | `_t` |
| 10 | `_e` |
| 11 · 12 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Status) | `_e` |
| Entschieden, Offen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Das Problem

Nova löst Rückbezüge aus dem Gesprächsverlauf nicht auf.

| Beleg | Prompt | Novas Verhalten |
|---|---|---|
| Matcha | 8 Turns über Matcha-Pulver, dann *„schauen wir nochmal nach dem Pulver"* | Fragt zurück: Kakao oder anderes? |
| Grillkäse | *„Die andere ist die mit dem Grillkäse"* | Klassifikator: `rejected` |
| Liste | *„Was steht auf der Liste?"* (Notiz heißt `Einkauf`) | Findet nichts |

Ein Mensch löst das ohne Nachdenken. Der rationale, semantische, thematische Bezug ist
vollständig vorhanden — er steht nur nicht **im Satz**, sondern **im Verlauf**.

### 1.1 Es sind zwei Wurzeln, nicht eine

Die drei Belege sehen gleich aus. Sie sind es nicht:

| Klasse | Beispiel | Wurzel |
|---|---|---|
| **Referenz** | „das Pulver" → „Matcha-Pulver" | Der Referent steht im Verlauf, nicht im Satz. |
| **Vokabular-Mismatch** | „Liste" → Notiz `Einkauf` | Der Referent steht in der **DB** unter anderem Namen. |

Beide zusammen ergeben den Liste-Fall: *welche* Liste (Referenz) **und** wie heißt sie
wirklich (Mismatch).

**Wichtig — der Mismatch löst sich womöglich von selbst:** Wenn die Kaskade *„die Liste"*
zu *„Einkaufsliste"* auflöst, findet die **bestehende** bidirektionale LIKE-Suche des
Notizen-Agenten (AGT-FIX4, Chat 22: *„Einkaufsliste" findet „Einkauf"*) die Notiz bereits.
Der Mismatch verschwindet, weil der aufgelöste Referent das Kompositum trägt.

Das gilt nur, wenn im Verlauf je „Einkaufsliste" fiel. Fiel dort nur „Notiz Einkauf" und
der User sagt „Liste", bleibt echter Vokabular-Mismatch → das ist L3 (Embedding) oder L5
(Rückfrage). Kein separater Sprint nötig, aber ein bewusst offener Fall.

---

## 2. Einordnung: das Feld heißt Conversational Query Rewriting

Das Problem ist seit ~2019 systematisch bearbeitet. **CQR** erzeugt aus dem Roh-Input eine
de-kontextualisierte Anfrage, indem es den Verlauf einbezieht und Koreferenzen, Ellipsen und
Themenwechsel auflöst. Datensätze/Benchmarks: **CANARD**, **QReCC**, **TopiOCQA**, **TREC CAsT**.

Drei Befunde aus der Literatur, die unser Design tragen:

1. **Der Schritt gehört VOR das Retrieval.** Ohne Rewriting bekommt die Vektordatenbank eine
   kontextfreie Anfrage und liefert irrelevante Dokumente. Über 60 % der konversationellen
   Folgefragen tragen unaufgelöste Koreferenzen.
2. **CANARDs Methode ist unsere L1:** Schlüsselwörter aus dem Kontext extrahieren, den
   referierenden Ausdruck ersetzen.
3. **Latenz zählt.** Der Schritt sitzt auf dem kritischen Pfad jeder Antwort. Ein kleines,
   schnelles Modell reicht — kein Frontier-Modell.

**Nicht übernommen:** `maverick-coref-de` (Uni Hamburg, KONVENS 2025). Technisch das beste
deutsche Koreferenz-System — aber **CC BY-NC-SA 4.0** (NonCommercial + ShareAlike).
Unvereinbar mit Apache 2.0. Weder Code lesen noch einbinden. Das Paper darf gelesen werden,
Ideen sind nicht schutzfähig. **Clean Room.**

Und selbst mit Lizenz löste es nur eine unserer vier Schichten: Dokument-Koreferenz kennt
unsere Datenbank nicht, kann kein Entitäts-Grounding, ist auf Fließtext trainiert statt auf
Dialog-Turns. Der Vokabular-Mismatch bliebe ungelöst.

---

## 3. Die Leitidee: Generatoren und Selektoren

Der naive Kaskaden-Entwurf lässt jede Schicht **unabhängig** versuchen und bei Misserfolg an
die nächste weiterreichen. Das ist falsch — es verschenkt die Arbeit der billigen Schichten.

**Richtig:** Billige Schichten sind **Kandidaten-Generatoren** (hohe Trefferquote, geringe
Präzision). Teure Schichten sind **Selektoren** (hohe Präzision auf einer *bereits
eingegrenzten* Menge).

```
L0 Detektor    → gibt es überhaupt eine Referenz?         (Kostenbremse)
L1 Kompositum  → Kandidaten aus dem Verlauf               (Generator, µs)
L2 Entität     → Kandidaten aus Verlaufs-Entitäten + DB   (Generator, ms)
L3 Embedding   → rankt die Kandidaten aus L1+L2           (Selektor, ~10 ms)
L4 LLM         → entscheidet den Rest, Python verifiziert (Selektor, ~300 ms)
L5 Rückfrage   → Nova fragt SPEZIFISCH                    (ehrlicher Ausgang)
```

L3 sucht nicht selbst nach Referenten. L3 bekommt eine Liste und sortiert sie. Das macht die
teuren Schichten schnell *und* sicher: Sie können nichts erfinden, was L1/L2 nicht gesehen
haben.

**Ausnahme:** Findet L1+L2 **null** Kandidaten, darf L4 (LLM) einen aus dem Verlauf
vorschlagen — aber **nur** mit Turn-Beleg, den Python nachprüft (§7).

---

## 4. Der zentrale Defekt, den dieses Konzept vermeiden muss

> **Eine falsche Bindung ist schlimmer als gar keine.**

Bindet L1 *„die Liste"* an *„Preisliste"* aus Turn 3, geht ein **falsch aufgelöster, aber
syntaktisch perfekter** Prompt ins Retrieval. Nova antwortet dann selbstbewusst über die
falsche Sache — und **niemand merkt es**, weil kein Fehler geloggt wurde.

Das ist Halluzination *durch* Auflösung. Es ist der einzige Weg, wie dieser Sprint das System
schlechter machen kann als vorher.

Deshalb gilt, direkt aus `lesson_l_default-wie-fehlschlag`:

> **Ein Default darf nie wie ein Fehlschlag aussehen — und ein Fehlschlag nie wie ein Treffer.**

**Konsequenz:** Keine Schicht liefert einen Wert. Jede Schicht liefert einen **Zustand**:

| Zustand | Bedeutung | Folge |
|---|---|---|
| `GEFUNDEN` | Ein Kandidat über Schwelle **und** mit Abstand zum zweiten | Substitution, fertig |
| `UNSICHER` | Kandidaten da, aber keiner klar genug | **Eskalation** mit Kandidatenliste |
| `NICHTS` | Kein Kandidat über Schwelle | **Eskalation** ohne Kandidaten |

**Zwei fast gleich gute Kandidaten *sind* Unsicherheit.** Ein Schwellwert allein genügt
nicht — es braucht die **Marge** zum Zweitplatzierten. Ohne sie ist „UNSICHER" Geschmackssache.

---

> **§5 bis §10 stehen nicht in dieser Datei.** Datenstrukturen, die Schichten L0–L5, der Einbau in den Graph und die Paket-Abhängigkeiten (§5–§7, §9) stehen in [`novaberg-referenz-aufloesung_t.md`](novaberg-referenz-aufloesung_t.md); der Weg dorthin — Messung vor Bau (§8) in [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md); die offenen Entscheidungen (§10) und der bisherige Kopf in [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

---

## 11. Abgrenzung — was dieses Konzept NICHT löst

- **`PENDING-RELEVANZ`** — ob ein Prompt die Antwort auf eine **Rückfrage** ist, ist verwandt,
  aber nicht dasselbe. Eigener Eintrag, eigener Sprint.
- **`NOTIZ-BEFEHL-ALS-TITEL`** — der Klassifikator, der „Neue Notiz anlegen" als *Namen*
  speichert. Verwandte Wurzel (Meta-Befehl vs. Sach-Inhalt), aber ein anderer Node.
  ⚠ Er ist der **Auslöser** der Duplikate, die L5 überhaupt erst nötig machen.
- **Embedding-Migration** — falls Messung 8.1 negativ ausfällt: eigener Sprint, nicht hier.

---

## 12. Warum das ein eigener Beitrag ist

Die CQR-Literatur schreibt einen Prompt um. Sie hat keine Datenbank dahinter.

**Unsere L2 gleicht gegen tatsächlich existierende Objekte ab** — Notiz-Titel, Termine,
Direktiven. Ein Referent, der kein reales Objekt bezeichnet, wird verworfen statt geraten.
Das ist kein Nachbau von Maverick. Das ist **„Entität schlägt Embedding"**, angewandt auf die
Referenz-Auflösung — und es ist die These, die ein Paper trägt.

Dazu die Kaskade selbst: Generatoren billig, Selektoren teuer, jede Schicht mit drei
Zuständen, und ein LLM, das nur vorschlagen darf, während Python entscheidet.

**Nova soll nicht raten, was gemeint war. Sie soll es wissen — oder ehrlich fragen.**
