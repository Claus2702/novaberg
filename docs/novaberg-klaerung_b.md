# Novaberg — Klärung: Abweichung und Lücke sind derselbe Vorgang (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) · Ausarbeitung: [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md) · Diskussion und Ergänzungen: [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md) · Messungen: [`novaberg-klaerung_m.md`](novaberg-klaerung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 4. Die Bauteile

Keines ist beschlossen. Die Reihenfolge folgt der Abhängigkeit, nicht der erwarteten Wirkung.

### K1 — Das Erwartungsschema je Objekttyp

| | |
|---|---|
| **ZIEL** | Zu einem genannten Objekt ist abrufbar, welche Eigenschaften es trägt und welche davon notwendig sind. |
| **TEST** | Für einen Objekttyp liefert der Abruf eine Menge benannter Eigenschaften mit Notwendigkeitsmarke. |
| **MESSUNG** | Trefferquote gegen eine Handprobe von Objekttypen aus echten Turns. |
| **Gegenprobe** | Ein Typ ohne sinnvolle Pflichteigenschaften liefert eine leere Pflichtmenge, nicht eine erfundene. |

Das Schema ist Weltwissen und kommt vom Modell. **Es wird abgelegt, nicht je Turn erfragt** — sonst zahlt jeder Turn für eine Antwort, die sich nicht ändert.

**Gegenargument:** Ein vom Modell erzeugtes Schema ist selbst eine Behauptung. Es kann Pflichtfelder erfinden. Deshalb die Gegenprobe und deshalb die Notwendigkeitsmarke als eigenes Feld — ein Schema, das alles für notwendig hält, ist unbrauchbar und muss als solches erkennbar sein.

### K2 — Das Klärungstor

| | |
|---|---|
| **ZIEL** | Vor dem Schreiben und vor der Antwort steht fest, ob der Objektzustand geklärt ist. |
| **TEST** | Ein Turn mit einer notwendigen fehlenden Eigenschaft erzeugt einen Klärungsbedarf mit Begründung. |
| **MESSUNG** | Anteil der Turns mit Klärungsbedarf; Verteilung über die beiden Ausgänge Lücke und Abweichung. |
| **Gegenprobe** | Ein vollständiger, widerspruchsfreier Turn erzeugt keinen. |

Vergleicht erwartet gegen vorhanden und liefert **beide** Ausgänge aus einer Operation. Der Abweichungs-Ausgang bekommt sein Urteil aus `SYK-B1`; der Lücken-Ausgang aus K1.

### K3 — Die Salienz der Klärung

| | |
|---|---|
| **ZIEL** | Ob gefragt wird, hängt an Novas Interesse — bei hoher Distanz fragt sie fast nie. |
| **TEST** | Bei `distanz` nahe 1.0 und hoher `zurueckhaltung` unterbleibt die Frage. |
| **MESSUNG** | Fragen je Turn gegen erkannte Bedarfe, aufgetragen über die Radwerte. |
| **Gegenprobe** | Bei unterbliebener Frage sind die Stufen 1 bis 3 trotzdem gelaufen: Der Bedarf ist vermerkt, der abweichende Wert nicht ausgebaut, der Fakt nicht überschrieben. |

**Die Gegenprobe ist der wichtigere Teil — aber nicht so, wie es zuerst aussieht.** Naheliegend wäre, der Bedeutung eine Untergrenze zu geben, die der Charakter nicht unterschreiten darf. Das ist falsch: Es zwänge eine distanzierte Nova zum Nachfragen und machte den Charakter zur Fassade.

Der Schutz sitzt nicht in der Frage, sondern in den Stufen davor (§2.1). Eine wortkarge Nova, die merkt, nicht darauf baut und nichts überschreibt, ist vollständig sicher — sie sagt nur nichts. **Deshalb prüft die Gegenprobe, dass das Schweigen die stillen Stufen nicht mitnimmt**, und nicht, dass irgendwann doch gefragt wird.

### K4 — Der Zwischenschritt im Gesprächspfad

| | |
|---|---|
| **ZIEL** | Eine Klärungsfrage kann gestellt werden, ohne dass der strittige Wert vorher geschrieben wird. |
| **TEST** | Bei Klärungsbedarf über der Schwelle enthält die Antwort die Frage, und der Schreibvorgang ist zurückgestellt. |
| **MESSUNG** | Anteil zurückgestellter Schreibvorgänge, die nach der Antwort des Nutzers aufgelöst werden. |
| **Gegenprobe** | Ohne Klärungsbedarf wird wie bisher geschrieben, ohne Verzögerung. |

Der Rückfrage-Fluss samt Pending und Resume existiert, hängt aber am Agentenpfad. Hier wird er für den Gesprächspfad verfügbar gemacht.

**Preis:** Eine zurückgestellte Schreibung, die nie aufgelöst wird, ist ein Verlust. Es braucht einen Verfall oder eine Auflösung nach n Turns — sonst sammeln sich Schwebezustände.

### K5 — Der Faktenpfad liest das Urteil

| | |
|---|---|
| **ZIEL** | Ein widersprochener Wert überschreibt einen bestehenden Fakt nicht ohne Marke. |
| **TEST** | Ein Turn mit `abweichend` invalidiert den bestehenden Fakt nicht. |
| **MESSUNG** | Anteil der Invalidierungen, die auf `trifft_zu` beruhen, gegen die auf reinem Wertvergleich. |
| **Gegenprobe** | Eine zutreffende Berichtigung invalidiert weiterhin — sonst ist der Speicher nicht mehr fortschreibbar. |

> ### ⚠ K5 hat heute keinen Gegenstand — korrigiert am 04.08.2026
>
> Die Erstfassung dieses Abschnitts stand auf zwei Annahmen, die beide falsch waren. Beide sind nachgemessen.
>
> **Die Tabelle `fakten` ist leer — null Zeilen.** Kein Aufrufer setzt jemals `ziel = "fakten"`; im ganzen Bestand kommen nur `kzg` (Salienz-Knoten) und `notizen` (Notizen-Manager) vor. Der `FaktenManager` ist registriert, seine Entscheidungslogik steht da — und wird nie erreicht. Der Zeichenketten-Vergleich, der diesen Abschnitt ausgelöst hat, ist **nie eingetreten**, weil der Pfad nicht läuft.
>
> **Und Urteil und Schreibvorgang liegen nicht im selben Zustand.** Es sind zwei Graphen: Der HumanGraph (`perzeption → enricher → ei_calc → salience → dispatcher`) verarbeitet die Nutzeräußerung und hat **keinen Verfasser**; der CharacterGraph erzeugt das Urteil. Beide laufen als getrennte Durchläufe über denselben Turn, korreliert allein über `turn_id`. Die Klammer fehlt hier also **genauso wie bei `SYK-B8`** — der Vergleich in der Erstfassung war falsch herum.
>
> **Der Grund ist bekannt und kein Defekt:** Der Triple-Store war in Betrieb und ist beim Umbau nicht mitgezogen worden. Der Backlog führt den fehlenden Erzeuger als **`15e — FaktenAgent (Salienz-Pipeline)`**. Wie weit der Umbau gekommen ist, zeigen die Nachbarn: `entitaeten` 433 Zeilen, `lzg_knoten` 1252, `fakten` **0**. Subjekt und Objekt entstehen, das Tripel dazwischen nicht.
>
> **K5 ist damit nicht das erste Bauteil, sondern eines der letzten.** Es setzt `15e` voraus. Solange nichts geschrieben wird, gibt es nichts zu schützen — und eine Prüfung in einen toten Pfad zu bauen hieße, sie nie zu messen.

**Wenn der Pfad wieder trägt, gehört die Prüfung dorthin und nicht in den Verfasser.** Der Grund ist die Zweiteilung der Graphen: Eine Prüfung im Schreibpfad deckt **beide** ab — Nutzerfakten aus dem HumanGraph und Novas eigene Ableitungen aus dem CharacterGraph — und sie deckt den Aufgabenpfad mit ab, auf dem der Verfasser nicht läuft. Sie ist Stufe 1 bis 3 aus §2.1: still, unbedingt, ohne Charakteranteil.

Das Urteil des Verfassers wird dann **Zusatzinformation statt Voraussetzung**: Liegt eines vor — über `turn_id` auffindbar —, verfeinert es die Entscheidung; liegt keines vor, prüft der Schreibpfad gröber, aber er prüft.

---

## 5. Reihenfolge

```
K1   Erwartungsschema je Objekttyp    ── ohne es gibt es keinen Lücken-Ausgang
 │
K2   Klärungstor                      ── braucht K1 und das Urteil aus SYK-B1
 │
K3   Salienz der Klärung              ── ohne sie ist K2 ein Verhör
 │
K4   Zwischenschritt im Gesprächspfad ── die Frage, die aus alldem folgt

K5   Faktenpfad prüft selbst          ── unabhängig, aber erst nach Backlog 15e
```

**K5 stand in der Erstfassung vorn und ist ans Ende gerückt.** Es setzt nicht `SYK-B1` voraus, sondern **`15e — FaktenAgent (Salienz-Pipeline)`**: Solange die Tabelle `fakten` keinen Erzeuger hat, gibt es nichts zu prüfen. Danach wirkt es unabhängig von K1 bis K4 und deckt beide Graphen ab.

K1 bis K4 bauen aufeinander.

---
