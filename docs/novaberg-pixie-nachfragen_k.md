# Novaberg — NachfragenAgent: die einfühlsame Rückfrage

**Absicht:** Erkennt die EI einen Druck auf dem Nutzer, legt ein Hintergrund-Agent einen Reiz zur Zuwendung auf den Stapel — keinen vorformulierten Satz, sondern die Lage, die der CharacterGraph in Novas Stimme ausformt; bei negativer Stimmung ist diese Zuwendung das Einzige, was ungefragt zugestellt wird, bei Stress schweigt auch sie.
**Stand:** 15. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *NachfragenAgent* 🔴 · *Stapel + Zustellung (Shadow Delivery)* 🔴 · `PIX-STAPEL-RADFAKTOR` ohne eigene Zeile — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md) · [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md) · [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md) · [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md)
**Entschieden:** 8 · **Offen beim Meister:** 0 (Liste in [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-pixie-nachfragen_k.md §8` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md), `_b` ist [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md), `_e` ist [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md), `_m` ist [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md).

| § | Datei |
|---|---|
| Hinweis unter dem Kopf (*Dieses Dokument beschreibt ausschließlich die Zuwendungs-Rolle*) | `_k` |
| 1 · 2 | `_k` |
| 3 (*Auslöser*, *Routing*, *Sonderstellung in der Zustellung*, *Konfiguration*) | `_t` |
| 4 | `_e` (Abschnitt D) |
| 5 | `_m` |
| 6 (mit *Was die Trennung am Bestand sichtbar macht*) | `_k` (mit Hinweis) |
| 7 (mit *Was daran noch zu messen ist*) | `_t` |
| 8 · 8.1 · 8.2 · 8.3 · 8.4 · 8.5 · 8.8 | `_t` |
| 8.6 · 8.7 | `_b` |
| 9: Einleitung, *Zwei Gegenproben*, *Der Auslöser ist mitgeändert* | `_b` |
| 9: *Was der Reiz geworden ist*, *Die Messung, in zwei Hälften* | `_m` |
| Versionshistorie | `_e` (Abschnitt F) |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Verwandt) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

> **Dieses Dokument beschreibt ausschließlich die Zuwendungs-Rolle.** Am 05.08.2026 ist entschieden, dass `nachfragen` und die Klärungsfrage aus `novaberg-autonomous-wissen_k.md` §11.3 **zwei Agenten** sind, nicht einer. Die Begründung und die Abgrenzung stehen in §6.

---

## 1. Warum dieses Dokument

Der NachfragenAgent existiert nicht. Sein Auftrag wird aber bereits erzeugt, geroutet und in der Zustellung sonderbehandelt — an vier unabhängigen Stellen im Code, die sich über seine Rolle einig sind, ohne dass sie irgendwo beschrieben wäre.

Das ist die gefährliche Lage: Ein Verhalten ist verdrahtet, aber nicht dokumentiert. Wer eine der vier Stellen ändert, kann die anderen drei nicht kennen. Dieses Dokument hält fest, was **gebaut ist**, und trennt es von dem, was **noch nicht entschieden ist**.

Vorfall, der es ausgelöst hat: Am 27.07.2026 gewann ein `nachfragen`-Auftrag dreimal den Pixie-Heartbeat und scheiterte jedes Mal an der Registry — sechs Minuten, in denen kein anderer Hintergrund-Job drankam.

## 2. Die Rolle

**Nova geht von sich aus auf den Nutzer zu, wenn es ihm schlecht geht.**

Das unterscheidet den Agenten von seinen Geschwistern. Recherche und Vertiefung bringen Inhalt; das Nachfragen bringt Zuwendung. Der Router benennt es in seinem Kommentar als *„einfühlsame Begleitung"*.

**Geschärft am 05.08.2026 — das Kriterium ist der Druck:**

> Nachfragen bedeutet, dass die **EI-Erkennung einen Druck auf dem Nutzer gefunden** hat. Nova möchte da sein, präsent sein, unterstützen. Dafür fragt sie. Es ist eine Zuwendung bei einem Absturz.

Das ist keine Umformulierung, sondern ein prüfbares Kriterium, und es entscheidet §3 und §4. „Es geht ihm schlecht" ließ offen, woran man das erkennt; „die EI hat einen Druck gefunden" benennt den Erkenner und damit die Größe, an der der Auslöser hängt.

---

## 6. Die Trennung in zwei Agenten

> **Hinweis zur Aufteilung (19.09.2026):** Dieser Abschnitt mischt Absicht und Befund. Der Unterabschnitt *Was die Trennung am Bestand sichtbar macht* trägt einen Befund am Bestand der Queue vom 05.08.2026 und die Folge für den Bau. Er bleibt hier, weil er die Entscheidung über den Auslöser begründet. Die übrigen Messungen stehen in [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md).

**Entschieden am 05.08.2026.** `nachfragen` war zweimal konzipiert, in zwei unvereinbaren Rollen — und keins der beiden Dokumente wusste vom anderen. `novaberg-autonomous-wissen_k.md` §11.3 (04.08.2026) schreibt ausdrücklich, `nachfragen` *„kommt in **keinem** Konzept vor"*; dieses Dokument beschreibt es seit dem 27.07.2026. Das neuere Konzept ist ohne Kenntnis des älteren entstanden, es ist deshalb **keine Ablösung**.

Die beiden Rollen sind wirklich zwei Dinge und bekommen zwei Aufgabennamen:

| | `nachfragen` (dieses Dokument) | `klaerfrage` (`novaberg-autonomous-wissen_k.md` §11.3) |
|---|---|---|
| **Was Nova bringt** | **Zuwendung** | **Wissen** |
| **Warum sie eröffnet** | weil es dem Gegenüber schlecht geht | weil nur das Gegenüber die Antwort hat |
| **Auslöser** | Intentionen `emotionaler_ausdruck`, `hilferuf`; Emotionsvektor `absturz`/`spirale`/`einbruch` | Lücke oder Abweichung aus der Klärung, Tor 1 und Tor 2 (`novaberg-klaerung_k.md` §2) |
| **Steuerung** | keine — der Zustellungsfilter entscheidet | Interesse-Speichen: `lenkungsdrang`, `eigensinn`, `widerspruchsfreude` gegen `folgsamkeit`, `zurueckhaltung`, `gespraechsdistanz` |
| **Ergebnis** | ein Gesprächszug, kein Speicherinhalt | Wissen in der Bibliothek: was gefragt wurde, was zurückkam, was folgt |
| **Stand** | verdrahtet an vier Stellen (§3), Agent fehlt | weder verdrahtet noch gebaut |

**Warum ein neuer Name und nicht der bestehende.** Genau die Doppelbelegung eines Namens hat diesen Widerspruch erzeugt und ein Konzept entstehen lassen, das die vorhandene Beschreibung nicht fand. `klaerfrage` bricht bewusst mit der Verbform von `vertiefen` und `nachfragen` — die Ähnlichkeit von `nachfragen` und `erfragen` wäre dieselbe Falle noch einmal. Der Name bindet stattdessen an sein Konzept, `novaberg-klaerung_k.md`.

**Der zweite Agent ist heute nicht baubar.** Sein Eingang ist eine erkannte Lücke, und die erzeugt das Klärungstor `KLA-K2` — das auf `KLA-K1` wartet. Beide sind ungebaut, und im Code gibt es zu keinem von beiden eine Zeile (geprüft am 05.08.2026). Bis dahin bleibt er Konzept.

### Was die Trennung am Bestand sichtbar macht

**Die 62 `nachfragen`-Aufträge in der Queue passen zu keiner der beiden Rollen.** Die Form, **synthetisch nachgebaut** — die Feldbelegung ist die gemessene, das Thema konstruiert:

```json
{"aufgabe": "nachfragen", "thema": "Ringsystem des Saturn",
 "intentionen": ["emotionaler_ausdruck"], "emotion": "freude", "modus": "emotional"}
```

- **Sie tragen `freude` und `begeisterung`**, nicht Not. Der Intentions-Auslöser `emotionaler_ausdruck` (§3) feuert bei **jeder** Gefühlsäußerung, auch bei einer positiven. Nur der Emotionsvektor-Pfad des Routers trifft die Lage, die §2 beschreibt. **Damit widerspricht der gebaute Auslöser dem §2 dieses Dokuments** — „wenn es ihm schlecht geht" gilt für einen der beiden Auslöser, nicht für beide.
- **Sie tragen keine Wissenslücke.** Das Feld existiert im Auftragsformat nicht. Ein Agent nach §11.3 bekäme 62 Aufträge, die seinen Eingang nicht tragen.

**Folge für den Bau, entschieden am 05.08.2026:** Mit dem Kriterium aus §2 — die EI hat einen **Druck** gefunden — ist das ableitbar, was vorher offen war. `emotionaler_ausdruck` ist **kein** Druck; die Intention deckt jede Gefühlsäußerung ab, auch Freude und Begeisterung. Die Zuordnung ist ein **Defekt**, kein zweiter gewollter Fall.

| Auslöser | Trägt Druck? | |
|---|---|---|
| `emotions_vektor` ∈ `absturz`, `spirale`, `einbruch` | ja — es sind Bewegungen ins Negative | ✅ bleibt |
| Intention `hilferuf` | ja | ✅ bleibt |
| Intention `emotionaler_ausdruck` | **nein** | ❌ **entfällt** |

Der Ersatzwert ist `""` — kein Auftrag. Jede andere Zuordnung erfände eine Absicht, die niemand genannt hat; eine rein gefühlsmäßige Äußerung ohne Druck ist kein Hintergrundauftrag, genau wie `smalltalk` und `feedback_geben` schon heute keinen erzeugen.

**Die Zuordnungstabelle steht doppelt** — `memory/kzg.py` und `agents/kzg/queues.py` führen `_INTENTION_AUFGABE_MAP` je einmal, und sie sind bereits auseinandergelaufen (`bestätigung` gegen `bestaetigung`). Beide sind zu ändern; dass es zwei sind, steht in der Fundliste.
