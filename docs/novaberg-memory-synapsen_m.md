# Novaberg — Memory-Kern: Synapsen-Modell (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) · Ausarbeitung: [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) · Bauplan und Umstellung: [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) · Diskussion und Ergänzungen: [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er die Messung vom 02.08.2026 trägt.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Synapsen-Modell für das Langzeitgedächtnis
**Stand:** 18. September 2026 (§10.2: `switch` hat eine feste Form für Entscheidungs-Einträge, `log_decision`). Davor 4. September 2026, 23:40 UTC (**§7.1a — die Protokollzeile traegt jetzt die Entscheidung**: Der erste Betriebsbeleg war ein Nullbefund, in dem **sechs Ausgaenge gleich aussahen**; die Zeile fuehrt seither `naehen_alle`, `knappster_verworfener`, `schwelle`, `deckel` und `ausgang`. Fuer die zwei Zeilen davor einmalig nachgerechnet: knappster verworfener **0,2935** und **0,4334** — beide unter dem Maximum der Zufallsverteilung (0,5305), **der Nullbefund ist richtig und die Schwelle steht nicht zu hoch**. Suite **2974**.). Davor 4. September 2026 (**§7.1a gebaut** — `memory/usage_reinforcement.py`, gerufen vom Dispatcher; Schwelle **0,55** aus 75.975 Paaren abgeleitet, Deckel 3. Gegen den Bestand: 13 von 15 Turns verstärken, 24 von 30 nahen Kandidaten genommen, **0 von 45 fremden**. Die Segmentregel ist **vor dem Bau widerlegt** — 25 von 25 Antworten ergeben ein Segment, und die Segmentierung kostete 1,53 s im Turn. Davor am selben Tag: **§7.1a — das Erkennungskriterium ist entschieden**: Embedding-Naehe zwischen Antwort und Erinnerung, **je Segment**, weil die Selbstauskunft des Verfassers fantasieren koennte und der Ganztext verduennt. Die Schwelle wird gemessen, nicht gesetzt — die Naehe trennt schwach (0,355 gegen 0,504 ueber 19.900 Paare). Davor am selben Tag: **§7.1a neu — Verstärkung setzt Verwendung voraus, nicht Nachbarschaft**: Der Ort ist der Dispatcher, nicht der Responder. Gemessen: 95,2 % aller Verstärkungen tragen `cosine = 1.0000`, ein einzelner KZG-Eintrag erzeugte bis zu 91 Verstärkungen über acht Tage, und 91,5 % der scheinbaren Wiederkehr sind Wiederholung desselben Turns. §9.2 verschärft. **Dasselbe Bild wie am 12.07.2026, andere Ursache.**). Davor 30. August 2026, 17:40 UTC (§4.1: was die Skala [0…10] bedeutet — Dauer, nicht Wichtigkeit; der Anlagewert 3,25–3,96 und seine Jahresrechnung). Davor 30. August 2026 (§8.4.4: der Block in den Namen seines Lesers; 29.08.: die Zeile `Sprecher:` je Erinnerung, der Lesepfad lädt `beobachter`); davor 2. August 2026, Chat 125 — **der Umbau ist abgeschlossen: P1 bis P9 gebaut, P10 offen.** Die abgelöste Tabelle `langzeitgedaechtnis` ist gelöscht, der alte Cluster-Pfad aus dem Repositorium entfernt. Zuvor: Chat 107 (Gewichts-Reset des Bestands am 12.07.2026 — Bruch in der Historie, siehe §9; ivfflat-Index entfernt). Zuvor: Chat 87, Punkt 1–8 vollständig ausgearbeitet.

> **Gemessen am 02.08.2026, nicht geschätzt:** 1108 Knoten, 110.340 Kanten, alte Tabelle 0 Zeilen. Kantenzusammensetzung: embedding 87,7 %, themen 10,9 %, entitaet 1,1 %, timeline 0,3 %.
>
> **Die dünnen Schichten sind überwiegend der Korpus, nicht der Schreibpfad.** Von 1076 Knoten ohne `timeline_id` enthalten fünf überhaupt einen Zeitausdruck; von 766 ohne `entitaet_ids` nennen drei Viertel nichts Bekanntes. Die Gespräche sind Weltwissen — Entropie, Hawking-Strahlung, Raumzeit —, und Weltwissen hat weder Referenz noch Datum. Dass die dichte Relation (Embedding) die seltenen (Entität, Zeit) zahlenmäßig überwiegt, ist erwartbar und kein Versagen: Der Kern des Umbaus war, dass jede Erinnerung ein **eigener Knoten bleibt** statt zu einem Aggregat zu verschmelzen. Das hält.
>
> **Woran es sich entscheiden wird:** an der Charakterbildungs-Messreihe. Jeder ihrer sechs Bögen setzt in Turn 7 einen Namen mit Zahl und in Turn 9 ein Datum mit Ort und fragt beides in Turn 22 und 24 zurück ab. Erst dieser Korpus kann zeigen, ob die Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt.
**Pfad:** novaberg/docs/novaberg-memory-synapsen_k.md
**Vorgänger-Konzepte:** novaberg-kzg-liberalisierung_k.md (Chat 64), novaberg-pixie-promotion.md

---

## Aus §7.1a — Verstärkung setzt Verwendung voraus, nicht Nachbarschaft

Regel, Ort, Erkennungskriterium, Schwelle und Protokollzeile stehen in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §7.1a. Hier stehen die Messungen am Bestand, die der Abschnitt trägt.

#### Die Schwelle: 0,55 — abgeleitet, nicht gesetzt

Aus diesem Unterabschnitt nur der Absatz mit der Messung gegen den echten Bestand; die Ableitung der Schwelle mit der Tabelle der Quantile steht in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §7.1a.

`[gemessen]` 04.09.2026 gegen den echten Bestand, 15 Antworten mit je 2 nahen und 3 zufälligen Kandidaten: **13 von 15 Turns** tragen eine Verstärkung, **24 von 30** nahen Kandidaten werden genommen — und **0 von 45 fremden**. Kein falscher Positiver.

#### Was heute stattdessen gilt, und was es anrichtet

Zwei Mechanismen verstärken, **beide am Schreiben eines neuen Eintrags, keiner an der
Verwendung**:

| Mechanismus | Auslöser | Wirkung |
|---|---|---|
| `kzg_store` — thematische Verstärkung | ein neuer Eintrag teilt **ein einziges Thema** | `haeufigkeit` +1, Salienz neu, **TTL neu gesetzt** |
| `synapsen_promotion` → `knoten_verstaerken` | Embedding-Match ≥ Schwelle | `haeufigkeit` +1, `gewicht_roh` +0,1 |

Der erste scannt bei **jedem** Turn die ganze Paar-Partition und verstärkt jeden Eintrag mit
einem gemeinsamen Thema-Tag. `[gemessen]` 04.09.2026 über 2.911 KZG-Einträge des Paares
`meister:nova`, Stichprobe 400: `haeufigkeit` im Mittel **8,1**, Maximum **110**, und **64 %**
tragen mindestens eine Verstärkung.

**Daraus wird eine geschlossene Schleife:** Ein Eintrag mit gängigen Themen wird bei jedem
verwandten Turn verstärkt → seine Salienz steigt über `KZG_SALIENZ_HIGH` → seine TTL wird neu
auf 30 Tage gesetzt → er läuft nicht ab → er geht erneut in die Promotion → dort matcht er
**den Knoten, der aus ihm selbst entstanden ist** → verstärkt ihn → von vorn.

`[gemessen]` 04.09.2026 über 14.947 Reinforcements: **95,2 % tragen `cosine = 1.0000`**, also
einen identischen Vektor. Ein einzelner KZG-Eintrag erzeugte bis zu **91** Verstärkungen
desselben Knotens, verteilt über **acht und mehr Kalendertage**. Über den Bestand: 14.947
Verstärkungen auf 1.538 Knoten — **Faktor 9,7**.

> **Dieses Bild gab es schon einmal.** Am 12.07.2026 standen 2.910 Reinforcements auf 302
> Knoten bei `cosine_max = 1.0000` — **Faktor 9,6** —, und der ganze Bestand wurde
> zurückgesetzt (siehe den Bruch-Hinweis in Punkt 9). Damals war die Ursache das casing-blinde
> Embedding, das seither gewechselt hat. **Dasselbe Bild, andere Ursache** — und das ist der
> Grund, warum die Sperre als Regel gehört und nicht als Einzelbehebung.

#### Die Folge für die Zähler

`haeufigkeit` und `gewicht_roh` messen heute **nicht Wiederkehr, sondern Wiederholung**. Jede
Auswahl, die darauf sortiert, zieht die am häufigsten wiederholten Einträge statt der
wiederkehrendsten.

`[gemessen]` 04.09.2026: Zählt man Berührungen über **verschiedene Turns** statt über Zeilen,
fallen die Träger mit Wiederkehr ≥ 2 von **1.250 auf 106**, das Mittel von 2,64 auf **1,04**.
**91,5 % der scheinbaren Wiederkehr sind Wiederholung desselben Turns.**

---

## Aus §8.5 — Wahrnehmungs-Gravitation

Die Mechanik steht in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §8.5, was für die Umsetzung ausstand und wie es erledigt wurde, in [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) §8.5.5.

#### 8.5.6 Was die erste Messung ergeben hat

**Zwei Turns gegen das Produktivsystem, 02.08.2026.**

Der erste landete auf dem Übersprungspfad: sieben aktive Ziele des Paares, **keines aktiviert**. Die Aktivierungs-Stärken lagen zwischen 0.102 und 0.212 gegen `GRAVITATIONS_SCHWELLE` = 0.4 — das stärkste um den Faktor 1,9 darunter.

Der zweite Turn war bewusst nahe an einem langfristigen Ziel gewählt und überschritt die Schwelle: Aktivierungs-Stärke 0.631, Cluster `schlachtfeld` (Faktor 0.05), Cosinus zum rohen Embedding **0.9998** — eine Drehung von **1,14°**. Die gespeicherte Zerlegung lässt sich von Hand nachrechnen und ergibt denselben Wert.

> **Der Befund: Aktivierungsschwelle und Verschiebungswirkung ziehen gegeneinander.** Ein Ziel überschreitet die Schwelle nur, wenn es der Frage schon ähnlich ist — und in Richtung eines fast parallelen Vektors zu verschieben dreht kaum. Selbst im stärksten Cluster (`glut`, 0.30) wären es bei derselben Lage 7,8°.

**Ob die Verschiebung die Trefferliste je ändert, ist nicht gemessen.** Das ist die offene Frage von P10, nicht ein Defekt seiner Umsetzung. Sie ist erst an einem Korpus entscheidbar, in dem Ziele und Fragen auseinanderliegen — also an der Charakterbildungs-Messreihe.

---

## Aus §9 — Decay-Logik

Die Decay-Logik steht in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §9; dort stand dieser Hinweis am Kopf des Abschnitts. Der Befund *„Dieses Bild gab es schon einmal“* (oben, Aus §7.1a) verweist auf ihn als *„Bruch-Hinweis in Punkt 9“*.

> **⚠ Bruch in der Gewichts-Historie (12.07.2026, Chat 107):** Im Zuge der Embedding-Migration EMBEDDING-CASING-BLIND wurden die Gewichte des gesamten `lzg_knoten`-Bestands zurückgesetzt (`knoten_gewichte_zuruecksetzen`: `haeufigkeit = 1`, `gewicht_roh`/`gewicht_absolut`/`gewicht_decay` auf Initialwerte; `lzg_kanten` komplett gelöscht und aus den frischen Vektoren neu aufgebaut). Grund: Die bis dahin akkumulierten Gewichte waren **Zufall** — im casing-blinden Embedding-Raum fand praktisch jeder neue KZG-Eintrag irgendwo einen Skelett-Zwilling über der Match-Schwelle (2910 Reinforcements auf 302 Knoten, `cosine_max = 1.0000` in der Produktionshistorie); die Attraktoren waren Satzformen, keine Bestätigungen. Ein Gewicht, von dem man weiß, dass es Zufall ist, richtet mehr Schaden an als kein Gewicht.
>
> **Konsequenz für jede Zeitreihen-Auswertung:** Gewichts- und Häufigkeitswerte vor dem 12.07.2026 sind mit den Werten danach nicht vergleichbar. Alle Bestandsknoten starteten bei `haeufigkeit = 1`; der zweite Durchlauf der geretteten KZG-Hashes (30-Tage-TTL) hat nur die jüngste Historie nachgezogen — ältere Knoten bleiben bei 1. Das ist eine ehrliche Schieflage, die der Decay über die Zeit angleicht. Befund und Beweiskette: `novaberg-embedding-casing-blind_k.md`.
