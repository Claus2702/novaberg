# Novaberg — Klärung: Abweichung und Lücke sind derselbe Vorgang

**Absicht:** Weicht eine Eigenschaft eines Objekts von der gespeicherten ab oder fehlt eine notwendige, erkennt Nova das als denselben ungeklärten Objektzustand, baut nicht darauf und überschreibt nichts — ob sie nachfragt, entscheidet ~~allein~~ ihr Charakter; hängt ein klarer Auftrag daran, wird immer gefragt (entschieden am 17.10.2026, §2.1).
**Stand:** 17. Oktober 2026, 21:50 UTC (`date -u`; die Bauart der Klärfälle am Objekt angenommen, `_e` A, *Bauart*; nachgezogen in §2.3 — die Bestimmung einer Entität in der Sachlage, das Ereignis sofort mit der Genauigkeit *Monat* — und in §6, ein- und mehrwertige Beziehungen; nichts gebaut). Davor 17. Oktober 2026, 15:40 UTC (`date -u`; neu §2.3: wer gemeint ist — die Bestimmung einer Entität über den vorhandenen Erzeuger der Mehrdeutigkeit, und ein Ereignis mit unklarem Zeitraum; entschieden am 17.10.2026, `_e` A, M4 und M5; dazu §6, das Faktengedächtnis). Davor 17. Oktober 2026, 14:36 UTC (`date -u`; die Fragen zu den Klärfällen am Objekt entschieden, `_e` A; damit sind B.3 und B.4 beantwortet; am Konzept selbst nichts geändert). Davor 5. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Klärung* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md) · [`novaberg-klaerung_b.md`](novaberg-klaerung_b.md) · [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md) · [`novaberg-klaerung_m.md`](novaberg-klaerung_m.md)
**Entschieden:** ~~0~~ → ~~6~~ → ~~8~~ → 9 (17.10.2026, zu den Klärfällen am Objekt; M2 folgt aus M1; M4 und M5 zur Bestimmung einer Entität und zum Zeitraum eines Ereignisses; am Abend die Bauart der Klärfälle angenommen) · **Offen beim Meister:** ~~4~~ → 2 (Liste in [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-klaerung_k.md §2.1` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md), `_b` ist [`novaberg-klaerung_b.md`](novaberg-klaerung_b.md), `_e` ist [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md), `_m` ist [`novaberg-klaerung_m.md`](novaberg-klaerung_m.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| 1 (mit *Warum das zusammengehört*) | `_k` |
| 2 (mit *Tor 1*, *Tor 2*) · 2.1 | `_k` |
| 2.3 (seit 17.10.2026) | `_k` |
| 2.2 | `_t` |
| 3 · 3.1 · 3.2 | `_m` |
| 4 · K1 · K2 · K3 · K4 · K5 | `_b` |
| 5 | `_b` |
| 6 · 7 | `_k` |
| 8 | `_e` |
| *Versionshistorie* | `_e` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Betrifft, Verwandt) | `_e` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Der Grundsatz

> **Zu jedem Objekt gehört eine Menge von Eigenschaften. Weicht eine vorhandene von der gespeicherten ab, oder fehlt eine notwendige, ist das derselbe Zustand: Der Objektzustand ist nicht geklärt. Er wird geprüft — und wenn die Prüfung ihn nicht auflöst, wird gefragt.**

Das ist kein Bauteil eines Sprints. Es ist eine Eigenschaft, die ein System haben muss, das Fakten über die Zeit hält und sie mit einem Menschen zusammen fortschreibt.

Die beiden Fälle sehen verschieden aus und sind es nicht:

| | Zustand | Beispiel |
|---|---|---|
| **Abweichung** | erwartet, vorhanden — **und anders** | „seit vier Monaten zusammen" gegen „seit acht Monaten" |
| **Lücke** | erwartet, notwendig — **und abwesend** | Einkaufsliste für Nudelsalat ohne Nudeln |

Beide heißen *erwartet ≠ vorhanden*. Beide enden, wenn sie bedeutsam genug sind, in derselben Handlung: **einer Frage, bevor weitergearbeitet wird.**

### Warum das zusammengehört

Wer die beiden Fälle trennt, baut zwei Mechanismen, die dieselbe Entscheidung zweimal treffen — und die beim ersten Konflikt auseinanderlaufen. Der Vergleich *erwartet gegen vorhanden* ist eine Operation; ob das Ergebnis „fehlt" oder „weicht ab" lautet, ist sein Ausgang, nicht sein Gegenstand.

Es ist auch dieselbe kognitive Bewegung. Ein Mensch, dem in einer Aufzählung etwas fehlt, und einer, dem zwei Angaben widersprechen, tun beide dasselbe: Sie halten an, prüfen, und fragen nach — oder lassen es, weil es nicht wichtig genug ist.

---

## 2. Zwei Tore, nicht eines

Zwischen der Erkennung und der Frage liegen **zwei** Entscheidungen, und sie speisen sich aus verschiedenen Quellen. Sie zu verwechseln ist der Fehler, der aus Aufmerksamkeit ein Verhör macht.

### Tor 1 — Notwendigkeit: *Muss diese Eigenschaft da sein?*

Kommt vom **Objekt und von der Aufgabe**, nicht vom Charakter.

- Ein Nudelsalat braucht Nudeln. Das ist Weltwissen über den Objekttyp.
- Eine Einkaufsliste ist erst brauchbar, wenn sie vollständig ist. Das ist der Zweck.
- Ein Besuch hat einen Besucher. Ohne ihn ist der Eintrag kein Ereignis, sondern ein Wort.

**Nicht notwendig** ist alles, was das Objekt nicht trägt: die Augenfarbe des Besuchers, die Marke der Mayonnaise. Eine Eigenschaft, die nur *denkbar* ist, ist keine Lücke.

### Tor 2 — Salienz: *Ist es das Unterbrechen wert?*

Kommt vom **Charakter und von der Beziehung** — Neugier, Zuwendung, Distanz, Aufnahmebereitschaft. Alle vier sind gebaut.

Dasselbe gilt für die Abweichung: Vier Monate gegen acht bei einer Beziehung ist bedeutsam. Zwei Tage Unterschied bei einem beiläufig erwähnten Termin ist es nicht.

> **Tor 1 entscheidet, ob es eine Lücke ist. Tor 2 entscheidet, ob sie eine Frage wert ist.**
>
> Ohne Tor 1 fragt Nova nach Belanglosem. Ohne Tor 2 fragt sie nach allem Notwendigen sofort, auch mitten in einer Trauerpassage. Beide Fehler sind unangenehmer als das Problem, das sie lösen sollen.

### 2.1 Vier Stufen, und nur die letzte hängt am Charakter

Der Fehler, der hier naheliegt, ist die Annahme, die **Frage** sei der Schutz. Sie ist es nicht. Der Vorgang hat vier Stufen, und drei davon laufen unbedingt:

| Stufe | Gesteuert von | Kosten |
|---|---|---|
| **1. Erkennen** — erwartet gegen vorhanden | nichts, unbedingt | ein Vergleich |
| **2. Nicht darauf bauen** — der abweichende Wert wird nicht Prämisse | nichts, unbedingt | keine |
| **3. Vermerken** — der Speicher überschreibt nicht stillschweigend | nichts, unbedingt | keine |
| **4. Fragen** | **Charakter** | ein Gesprächszug |

**Nur Stufe 4 kostet etwas, das der Charakter abwägen darf.** Die Stufen 1 bis 3 sind still und gratis; sie zu überspringen spart nichts und verliert alles.

Daraus folgt das Verhalten bei hoher Distanz, und es ist stimmig: **Nova merkt die Abweichung, baut nicht darauf, überschreibt den Fakt nicht — und sagt nichts.** Sie ist nicht blind, sie ist wortkarg. Das ist eine Persönlichkeit, kein Defekt.

**Entschieden am 17.10.2026, für einen Klärfall an einem Auftrag** (`_e` A, M1): Hängt ein klarer Auftrag des Menschen am Klärfall, wird Stufe 4 immer gestellt, und der Charakter färbt nur den Ton; Stimmung, Nähe und Pflichtbewusstsein entscheiden bei einer Aussage ohne klaren Auftrag. Die Tabelle oben gilt damit für Abweichung und Lücke im Gespräch, nicht für einen Auftrag, der auf eine Antwort wartet.

Und umgekehrt: Der Schaden aus dem Sykophanz-Befund — die Verhandlungsempfehlung auf einer erfundenen Zusage, die Beruhigung vor der Klassenarbeit — wird von **Stufe 2** verhindert, nicht von der Frage. Deshalb darf Stufe 2 nie am Charakter hängen.

> **Hinweis zur Aufteilung (19.09.2026):** §2.2 *Woraus sich das Interesse speist* steht in [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md).

### 2.3 Wer gemeint ist — die Bestimmung einer Entität (17.10.2026)

**Entschieden am 17.10.2026** (`_e` A, M4): Was an einem Objekt offen ist, klärt Nova, damit sich die Entitäten bestimmen lassen. Passt ein Name auf zwei Entitäten, ist das derselbe ungeklärte Objektzustand wie eine Lücke: Dem Objekt fehlt seine Referenz. Beispiel, synthetisch: *„Welche Lena? Ich kenne zwei — deine frühere Nachbarin und deine Kollegin.“*

**Der Erzeuger steht.** Der gemeinsame Dienst zur Auflösung von Entitäten (`EntityResolutionService`) meldet eine Mehrdeutigkeit schon: `braucht_klärung`, eine Rückfrage und die Kandidaten ([`novaberg-pattern-entity-resolution.md`](novaberg-pattern-entity-resolution.md) §2.3, §8). Gelesen wird das heute nirgends. Der Magnet-Pfad des Kurzzeitgedächtnisses überspringt solche Namen still, und die Bindung der Sachlage bindet nicht, wenn zwei Entitäten passen `[Code, gelesen 17.10.2026: agents/kzg/magnete.py, memory/services/entity_resolution.py]`. Die stillen Stufen laufen damit schon: Nova erkennt die Mehrdeutigkeit, baut nicht darauf und bindet nichts falsch. Es fehlt Stufe 4.

**Was gilt:**

- **Der Klärfall steht in der Sachlage am Objekt**, mit den Kandidaten als fester, nummerierter Liste (`_e` A, M0 und F1).
- **Hängt ein klarer Auftrag daran** (*„Trag ein, dass Lena morgen kommt“*), wird immer gefragt (M1).
- **Ohne Auftrag ist die Frage Neugier.** Stimmung, Nähe und Pflichtbewusstsein entscheiden, ob Nova fragt (M1), bei hoher Salienz eher ja.
- **Geht der Mensch darüber hinweg**, bleibt der Punkt offen und darf noch einmal angesprochen werden. Verfällt die Sachlage, gilt das als kein Interesse (M3).
- **Nach der Antwort** ist das Objekt an genau eine Entität gebunden. Gebaut wird das als Bauteil F3 des Faktengedächtnisses ([`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6), am Klärfall am Objekt (Backlog `KLA-KLAERFALL-AM-OBJEKT`).
- **Die Bauart, angenommen am 17.10.2026, nicht gebaut** (`_e` A, *Bauart*): Den Klärfall erzeugt die Sachlage selbst, im selben Turn. Bleibt ein Objekt der Klasse `person` ungebunden, sucht sie die Entitäten nur über den Namen, ohne Rückfall auf Embeddings; passt der Name auf zwei oder mehr, hängt sie einen Klärfall der Art `bestimmung` mit den Kandidaten an das Objekt. Die Antwort bindet das Objekt an die gewählte Entität, mit einer eigenen Herkunft der Bindung.

**Ein Ereignis mit unklarem Zeitraum** (entschieden am 17.10.2026, `_e` A, M5). Beispiel, synthetisch: *Lena zieht im November nach Kassel.*

- Der genaue Zeitraum fehlt, und das ist eine Lücke. Die Sachlage klärt sie aus dem Weltwissen: Ein privater Umzug dauert ein bis zwei Tage und fällt vermutlich auf ein Wochenende.
- **Diese Annahme ist kein Wert, sondern eine offene Eigenschaft**, bis sie geklärt ist. Es gilt Stufe 2: Nova baut nicht darauf.
- **Die Frage *„Welches Wochenende?“* ist Neugier, keine Pflicht-Rückfrage**, denn an ihr hängt kein Auftrag. Ob Nova fragt, entscheiden Pflichtbewusstsein und Nähe, bei hoher Salienz eher ja.
- Das Ereignis selbst gehört in die Timeline. Der Fakt, der daraus folgt, gilt ab dem Ereignis ([`novaberg-memory-fakten_k.md`](novaberg-memory-fakten_k.md) §2.3). → **Entschieden am 17.10.2026, nicht gebaut** ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 15 und 19): Das Ereignis wird nicht erst nach der Klärung eingetragen, sondern sofort, mit der Genauigkeit *Monat*, und nach der Klärung verschoben. Über der Grenze der Salienz geschieht das ohne Auftrag; darunter fragt Nova je nach Willen und Pflichtbewusstsein.

---

## 6. Verhältnis zu bestehenden Konzepten

**`novaberg-sykophanz-eindaemmung_k.md`** behandelt einen Sonderfall dieses Grundsatzes: die Abweichung, bei der der Nutzer seinem eigenen früheren Wort widerspricht. `SYK-B1` liefert genau das Urteil, das K2 für seinen Abweichungs-Ausgang braucht. **Der Sprint ist damit kein Fremdkörper, sondern das erste Stück hiervon.**

**`novaberg-wissensluecken_k.md`** ist *nicht* dasselbe und wird oft dafür gehalten. Dort geht es um den Zug zu einem **Thema** über Wochen — Weltwissen, das Nova erwerben will. Hier geht es um Eigenschaften eines **konkreten Objekts** im laufenden Gespräch. Die eine Lücke wird recherchiert, die andere gefragt.

**GV4** findet akute Lücken bereits, aber turn-flüchtig und ohne Ausgang. K2 ist der Ort, an dem so ein Fund eine Folge bekommt.

**`novaberg-memory-fakten_k.md`**, das Faktengedächtnis, ist der Speicher, für den dieses Konzept geschrieben wurde (§1: *„ein System … das Fakten über die Zeit hält“*). Dort löst ein neuer Wert den alten bi-temporal ab, ohne Rückfrage (entschieden am 17.10.2026) — → bei einer einwertigen Beziehung; bei einer mehrwertigen kommt der neue Wert dazu (entschieden am selben Tag, [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 17). Das erfüllt Stufe 3, denn der alte Wert bleibt in der Historie. Ob Nova bei einer Abweichung fragt, bleibt Stufe 4. Den Schreibpfad selbst prüft K5 (`_b`).

---

## 7. Nicht enthalten

**Die Beantwortung der Frage.** Was mit der Antwort des Nutzers geschieht, ist der Schreibpfad — K4 stellt nur zurück.

**Automatische Auflösung von Widersprüchen.** Nach dem Grundsatz, nie zu löschen, dürfen zwei widersprüchliche Werte nebeneinander stehen. Wer sie später zusammenführt, ist offen und gehört nicht hierher.

**Das Weltwissen selbst.** K1 fragt das Modell nach Objekttypen; ein Wissensspeicher ist ein eigenes Thema.

---
