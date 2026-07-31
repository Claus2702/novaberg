# Novaberg — Lesson: Eine Meldung, die im geduldeten Bestand liegt, ist keine

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Das Werkzeug hatte den Absturz gemeldet, bevor er zuschlug
**Stand:** 31. Juli 2026, Chat 120
**Pfad:** novaberg/docs/novaberg-lesson_l_meldung-im-bestand-ertrinkt.md
**Auslöser:** `CHAT-NAME-OHNE-ERZEUGER` — acht Linter-Treffer, zwei echte Abstürze, niemand sah sie
**Verwandt:** `novaberg-lesson_l_default-wie-fehlschlag.md`, `novaberg-lesson_l_log-behauptet-was-es-weiss.md`

---

## 1. Der Fall

Ein `NameError` tötete das abschließende Ereignis jedes Chat-Turns. Gefunden wurde er durch ein Bildschirmfoto aus dem laufenden Betrieb — ein roter Kasten im Client.

**Das Werkzeug hatte ihn einen Tag vorher gemeldet.** Die Regelfamilie für undefinierte Namen trug neun Treffer, acht davon genau diese Stelle, in beiden Pfaden des Endpunkts.

Die Meldung war da. Gelesen hat sie niemand.

## 2. Warum niemand sie las

Die Prüfstrecke misst eine Gesamtzahl und vergleicht sie gegen eine Nulllinie — an jenem Tag 2253 geduldete Treffer. Der Ablauf lautet: Zahl ermitteln, gegen die Nulllinie halten, bei Gleichstand weitermachen.

Acht neue Treffer hätten die Zahl auf 2261 gehoben. Das wäre aufgefallen. **Sie kamen aber mit einem Commit, der andere Treffer entfernte** — die Zahl blieb in der Nähe, und niemand sieht sich 2253 Zeilen an, um zu prüfen, welche davon neu sind.

Das ist keine Nachlässigkeit, sondern die Bauart: Eine Zahl kann nicht sagen, welche ihrer Bestandteile sich getauscht haben.

## 3. Der Unterschied, der übersehen wurde

Nicht alle Regeln sind gleich. Die Nulllinie mischt zwei Sorten:

| Sorte | Beispiel | Was ein Treffer bedeutet |
|---|---|---|
| **Form** | fehlender Docstring, zu lange Zeile, unsortierte Importe | Der Code ist unschön. Er läuft. |
| **Absturz** | undefinierter Name | Der Code **stürzt beim Betreten ab**. |

2253 Treffer der ersten Sorte zu dulden ist eine vertretbare Entscheidung. Acht Treffer der zweiten Sorte zu dulden bedeutet, Code auszuliefern, der nicht läuft.

**Beide standen in derselben Zahl.**

## 4. Die Folge

Die Regel ist hart geschaltet worden — sie steht jetzt in einem zweiten Lauf, der sauber sein **muss**, und duldet keinen Bestand.

Dazu die Bedingung, die bei der ersten harten Familie beinahe gefehlt hätte: **Kann das Werkzeug seinen Gegenstand überhaupt sehen?** Die Regel ist blind für Namen, die zur Laufzeit entstehen — Stern-Importe, `exec`, Zuweisungen in `globals()`. Beide Wege wurden gezählt, beide stehen auf null. Erst damit heißt die Null „kein undefinierter Name vorhanden" statt „das Werkzeug sieht nicht hin".

## 5. Generalisierbare Erkenntnis

> **Eine Regel, deren Verletzung ein Absturz ist, gehört nicht in eine geduldete Trefferzahl.** Sie gehört in eine Wand, die bei Null steht.

Und allgemeiner:

> **Ein Bestand ist eine Aussage über Aufwand, nicht über Schwere.** Wer eine Nulllinie einführt, muss die Regeln vorher danach trennen, was ein Treffer bedeutet — sonst versteckt die Zahl genau das, wogegen das Werkzeug eingeführt wurde.

Der Prüfsatz für jede Regelfamilie, bevor sie in den geduldeten Bestand wandert: **Was passiert, wenn genau dieser Treffer ausgeliefert wird?** Läuft der Code weiter, darf sie warten. Stürzt er ab, muss sie sofort auf null.

---

→ Die harte Teilmenge steht in `ruff-hart.toml`; ihre Aufnahmekriterien stehen dort im Kopf.
→ Der Defekt: `novaberg-bugs.md` → `CHAT-NAME-OHNE-ERZEUGER`
