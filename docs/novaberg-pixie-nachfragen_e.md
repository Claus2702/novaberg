# Novaberg — NachfragenAgent: die einfühlsame Rückfrage (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-pixie-nachfragen_k.md`](novaberg-pixie-nachfragen_k.md) · Ausarbeitung: [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md) · Bauplan und Umstellung: [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md) · Messungen: [`novaberg-pixie-nachfragen_m.md`](novaberg-pixie-nachfragen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Alle acht Entscheidungen sind im Text datiert; einen Urheber nennt der Text bei keiner. Die Entscheidungen in `_k` und `_t` stehen in dem Abschnitt, den sie tragen, und bleiben dort. E3 bis E6 stehen unten in Abschnitt D. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §2, *„Geschärft am 05.08.2026 — das Kriterium ist der Druck“* | Nachfragen heißt: Die EI-Erkennung hat einen Druck auf dem Nutzer gefunden — ein prüfbares Kriterium statt *„es geht ihm schlecht“* | 05.08.2026 |
| **E2** | `_k` §6 und der Hinweis unter dem Kopf | `nachfragen` (Zuwendung) und `klaerfrage` (Wissen) sind zwei Agenten mit zwei Aufgabennamen | 05.08.2026 |
| **E3** | Abschnitt D, §4, erster Punkt | Der Agent formuliert nicht; er legt einen Reiz auf den Stapel, die Form entsteht im CharacterGraph | 05.08.2026 |
| **E4** | Abschnitt D, §4, zweiter Punkt mit Nachtrag | Der Agent schweigt nicht selbst; der Charakter wägt ab, aber in der Zustellung (Bauart in `_t` §8.8) | 05.08.2026 |
| **E5** | Abschnitt D, §4, dritter Punkt | Die Zuwendung bleibt offen, ohne Anlassbezug | 05.08.2026 |
| **E6** | Abschnitt D, §4, vierter Punkt mit Nachtrag | Kein Modus bricht den Cooldown. Seit dem Wegfall des Zustellungs-Cooldowns am 15.08.2026 hat die Entscheidung laut demselben Punkt ihren Gegenstand verloren | 04.08.2026 |
| **E7** | `_k` §6, *„Folge für den Bau, entschieden am 05.08.2026“* | Die Zuordnung `emotionaler_ausdruck` → `nachfragen` ist ein Defekt und entfällt auf `""`; vollzogen laut `_b` §9 | 05.08.2026 |
| **E8** | `_t` §8.8, *„Entschieden am 05.08.2026: Modulation, kein Veto, keine Untergrenze“* | Das Zuwendungsrad wirkt als Faktor in der Zustellung, nie als Veto | 05.08.2026 |

**Im Text als Entscheidung geführt, nicht gezählt:**

- `_t` §8.1: *„Das ist die tragende Entscheidung dieses Bauteils“* — der Druck wird frisch gelesen, nicht dem Auftrag entnommen. Eine Entscheidung beim Bauen.
- `_t` §3, Nachtrag vom 15.08.2026 zu Riegel 4: *„Wonach ohne Bezug gewählt werden soll, ist entschieden (höchste Salienz), aber nicht gebaut.“* Die Entscheidung gehört zur Kette in `novaberg-eigenzeit_k.md` §2.5.
- `_b` §9, *Der Auslöser ist mitgeändert*: die benannte Abweichung von §8.7 (der Vektor-Kanon als Konstante).

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage, die eine Entscheidung über die Absicht verlangt.

**Offen ohne Frage** — was das Konzept selbst als offen führt:

- `_t` §3, Nachtrag vom 15.08.2026: Riegel 1 (Zuwendung) und Riegel 2 (Führungsmaß) sind Konzept; die Schwelle von Riegel 2 ist *„eine Entscheidung, die noch aussteht“*. Sie gehört zur Kette in `novaberg-eigenzeit_k.md` §2.5 und ist hier nicht gezählt.
- `_t` §3, Riegel 4: Die Wahl ohne Bezugsvektor (höchste Salienz) ist nicht gebaut.
- `_t` §3, Riegel 5: Die Schwelle 0,30 steht auf drei Äußerungen — *„eine begründete Setzung, kein belastbarer Messwert“*.
- `_t` §7, *Was daran noch zu messen ist*: ob das Material den Verlauf mitträgt oder der Vektor genügt.
- `_t` §8.3: eine Stufe 2 mit Modellaufruf, falls der deterministische Reiz zu dünn ist.
- `_t` §8.8: Die Grenzen des Radfaktors sind *„ausdrücklich zu kalibrieren“*; das Bauteil `PIX-STAPEL-RADFAKTOR` ist offen.
- Abschnitt D, §4, vierter Punkt: wie oft ein Auftrag *entsteht* — *„offen für die Erzeugung“*.
- `_m` §5: der latente Defekt, dass ein Auftrag für einen nicht registrierten Agenten den Heartbeat gewinnt.
- `_m`, *Die Messung, in zwei Hälften*: Der Weg vom Turn zum Vektor ist ungemessen.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_t` §3, *Auslöser*: `emotionaler_ausdruck` → `nachfragen`, durchgestrichen; die Intention trägt keinen Druck (E7).
- `_t` §3, *Routing*: das Literal im Router, ersetzt durch `EMOTIONS_VEKTOREN_DRUCK` am 05.08.2026.
- Abschnitt D, §4: die vier ursprünglichen Fassungen der offenen Punkte, durchgestrichen, die Entscheidung daneben; der erste Punkt war *„falsch gestellt“*.
- Abschnitt D, §4, Nachtrag zum zweiten Punkt: Die erste Fassung (*„der Charakter spricht nicht mit“*) ist korrigiert, weil sie `novaberg-klaerung_k.md` §2.1 widersprach.
- `_k` §6: derselbe Name für beide Rollen; verworfen, weil die Doppelbelegung den Widerspruch erzeugt hatte (`klaerfrage`, nicht `erfragen`).
- `_t` §7: die Kompaktzeile der Zustellung und der Weg über `user_prompt` in beide Graphen; überholt am 15.08.2026, ersetzt durch einen Zeiger.
- `_t` §8.3: ein Modellaufruf in Stufe 1; zurückgestellt (das Zielregister liegt schon vor, 35 bis 38 Sekunden je Aufruf, die deterministische Fassung ist die Nulllinie für Stufe 2).
- `_t` §8.4: Schreiben in KZG, Bibliothek oder Ziele; ausgeschlossen, weil kein Wissen entsteht.
- `_t` §8.8: ein Summand statt eines Faktors; verworfen, weil er ein Veto wäre, das wie eine Gewichtung aussieht. Ebenso das Einrechnen beim Ablegen; es entfällt, weil das Rad zur Zustellzeit gelesen wird.

---

## D. Aus §4 — die vier Punkte, die nicht entschieden waren

Der Abschnitt steht ganz hier, weil er aus Entscheidungen besteht (E3 bis E6).

## 4. Was nicht entschieden war — und wie es entschieden wurde

*Die Überschrift hieß bis zum 05.08.2026 „Was nicht entschieden ist". Alle vier Punkte sind an diesem Tag entschieden; sie bleiben mit ihrer ursprünglichen Fassung stehen, weil die Begründung sonst ihren Gegenstand verliert.*

~~**Was der Agent erzeugt.** Ob eine Frage, eine Beobachtung oder ein bloßes Dasein-Signal — nirgends festgelegt.~~ → **Entschieden am 05.08.2026: keines von dreien — die Frage war an der falschen Schicht gestellt.** Ein Pixie-Agent formuliert nicht, was Nova sagt; er legt einen **Reiz** auf den Stapel, und der CharacterGraph macht daraus Emotion, Assoziation und Stimme (§7). Ob die Zuwendung als Frage oder als Beobachtung herauskommt, entscheidet sich zur Laufzeit am Charakter — nicht im Agenten. Die alte Task-Datei `services/shadow_agent/tasks/nachfragen.py` wurde beim Runner-Rückbau gelöscht (Roadmap, Chat 79); ihr Inhalt ist nicht mehr die Vorlage.

~~**Wann er schweigt.** Der Zustellungsfilter regelt, *ob* etwas rausgeht. Ob der Agent selbst zu dem Schluss kommen darf, dass Nachfragen gerade falsch wäre, ist offen.~~ → **Entschieden am 05.08.2026: Er schweigt nicht selbst.** Der Zustellungsfilter regelt das *Ob* und tut es bereits (§3). Ein zweiter Schweige-Entscheid im Agenten wäre dieselbe Logik an zwei Stellen — und die zweite Stelle wäre die, die niemand prüft, weil der Filter sichtbar davorsteht.

> **Nachtrag am selben Tag — die erste Fassung dieses Absatzes war zu weit gefasst und ist korrigiert.** Sie schloss aus dem richtigen Satz „der Agent entscheidet nicht" den falschen „der Charakter spricht nicht mit". Das widerspricht `novaberg-klaerung_k.md` §2.1, wonach **das Fragen** die eine Stufe ist, die der Charakter abwägen darf — und eine Nachfrage ist ein Fragen, das einen Gesprächszug kostet. Richtig ist: Der Charakter wägt ab, aber **in der Zustellung**, nicht im Agenten. Damit bleibt es bei einer Stelle statt zweien. Die Bauart steht in §8.8.

~~**Der Bezug zum Anlass.** Der Auftrag trägt Thema und Kontext des auslösenden KZG-Eintrags. Ob die Rückfrage daran anknüpfen soll („du hattest gestern von … erzählt") oder offen bleibt, ist eine Charakterfrage.~~ → **Entschieden am 05.08.2026: offen, ohne Anlassbezug.** Nova nennt nicht, worauf sie sich bezieht. Der Preis ist benannt: Die Annäherung verliert ihre Verankerung. Der Grund, sie trotzdem so zu bauen, ist, dass ein genannter Anlass sichtbar macht, dass mitgeschrieben und bewertet wurde — in genau der Lage, in der das am wenigsten trägt.

~~**Der Abstand.** Kein Mechanismus begrenzt heute, wie oft nachgefragt wird. Bei anhaltend negativer Stimmung erzeugt jeder hinreichend saliente Turn einen neuen Auftrag.~~ → **Gegenstandslos für die Zustellung, offen für die Erzeugung.** Wie oft etwas *rausgeht*, begrenzten bis zum 15.08.2026 der Zustellungs-Cooldown (`shadow_cooldown:{user_id}`, TTL 3600 s) und die Burst-Grenze gemeinsam. **Der Cooldown ist am 15.08.2026 mit dem Bau von Riegel 2 gefallen** (`novaberg-eigenzeit_k.md` §2.5): Was den Zeitpunkt beurteilt, sind jetzt die Riegel; was die Wiederholung begrenzt, ist allein der Burst-Zähler. Die Entscheidung vom 04.08.2026 — kein Modus bricht ihn — hat damit ihren Gegenstand verloren. Unberührt bleibt, wie oft ein *Auftrag entsteht* — das ist ein Mengenproblem der Queue und trifft alle Aufgabenarten gleich, nicht nur diese.

> **Nachtrag 15.08.2026 — es sind seither drei Bedingungen, nicht zwei.** Zu Cooldown und Burst-Grenze ist **`_rueckfrage_offen`** getreten: Solange eine Rückfrage Novas unbeantwortet ist, geht kein Impuls hinaus. Sie steht **vor** dem Burst-Zähler, und diese Reihenfolge ist die Aussage — ein unterdrückter Impuls soll die nächste Gelegenheit nicht mitverbrauchen. Stünde sie dahinter, zählte das Warten als Verbrauch.
>
> **Der Satz von 04.08.2026 gilt unverändert:** Den Cooldown bricht **kein** Modus. Die neue Bedingung bricht ihn nicht, sie kommt hinzu — sie kann nur zusätzlich verhindern, nie zusätzlich erlauben.

**Damit sind alle vier entschieden.** Der erste stand seit dem 27.07.2026 als „nicht entschieden" — er war aber gar nicht offen, sondern falsch gestellt: Er fragte nach einer Formulierung, und Formulieren ist nicht die Aufgabe eines Agenten. Was tatsächlich zu entscheiden war, ist **woraus das Material besteht**; das steht in §7.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung, B5 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_k` §1 (*„Der NachfragenAgent existiert nicht“*) und `_k` §6, Tabelle, Zeile **Stand** (*„verdrahtet an vier Stellen (§3), Agent fehlt“*) | Der bisherige Kopf (Abschnitt F, Feld **Status**) sagt *„Gebaut und gemessen am 05.08.2026“*; `_b` §9 beschreibt den Bau | `[gelesen 19.09.2026]` |
| **B2** | `_k` §6, Tabelle, Zeile **Auslöser** | Führt die Intention `emotionaler_ausdruck` noch als Auslöser; `_t` §3 und `_b` §9 sagen, sie ist entfallen (E7) | `[gelesen 19.09.2026]` |
| **B3** | `_b` §8.7 | Nennt den Cooldown als Teil der Zustellung, die unberührt bleibt; Abschnitt D (§4, vierter Punkt) sagt, der Zustellungs-Cooldown ist am 15.08.2026 gefallen. Der bisherige Kopf nennt als letzten Nachzug *„§8.8 auf den Wegfall des Zustellungs-Cooldowns“* | `[gelesen 19.09.2026]` |
| **B4** | `_t` §8.8 | `novaberg-eigenzeit_k.md`, Anhang *„Befunde aus dem Betrieb“*, steht in einem ungeprüften Konflikt zu §8.8: Riegel gegen Faktor | `[gelesen 19.09.2026]` |
| **B5** | `_t` §3, Nachtrag vom 15.08.2026, Riegel-Tabelle, Zeile 3 (*„Cooldown, Burst — bestand schon · erweitert“*); Abschnitt D, §4, Nachtrag (*„Zu Cooldown und Burst-Grenze ist `_rueckfrage_offen` getreten“*, *„Den Cooldown bricht kein Modus“*) | Beide führen den Cooldown als bestehend; derselbe §4 sagt im Absatz davor, er ist am 15.08.2026 gefallen | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Versionshistorie

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Rolle, Auslöser und Sonderstellung des NachfragenAgenten
**Stand:** 15. August 2026, Chat 143 — §8.8 auf den Wegfall des Zustellungs-Cooldowns nachgezogen; davor Chat 141 — §3 und §7 auf den Zustellungspfad
**Pfad:** novaberg/docs/novaberg-pixie-nachfragen_k.md
**Typ:** Konzept
**Status:** ✅ **Gebaut und gemessen am 05.08.2026** — `PIX-MIG-7`. Stufe 1 ohne Modellaufruf; §9 trägt die Messwerte. Offen bleibt der Radfaktor (`PIX-STAPEL-RADFAKTOR`, §8.8)
**Verwandt:** `novaberg-pixie.md` §5 · `novaberg-pixie-deepdive_k.md` (Schwester-Agent) · `novaberg-autonomous-wissen_k.md` §11.3 (`klaerfrage` — der abgetrennte zweite Agent, §6)

Die Versionshistorie des ungeteilten Konzepts, ungekürzt:

## Versionshistorie

- **v0.7 — 15.08.26:** **Nachzug auf den Zustellungspfad**, fällig seit dem 14.08.2026 — der Code lief diesem Abschnitt einen Tag voraus, in Teilen zehn. §3: Der überholende Absatz war im **Futur** geschrieben (*„Vor die emotionale Kompatibilität **treten** …"*) und ist zur Hälfte eingetreten; die Riegel tragen jetzt einzeln ihren Stand, in der Nummerierung von `novaberg-eigenzeit_k.md` §2.5. Gebaut sind **4** (Bezug auf die Äußerungen des Menschen, ohne Zeitfenster) und **5** (Themen-Tor, 0,30); **1** und **2** — Zuwendung und Führungsmaß — bleiben Konzept. **Die Paarung gehört zur Zahl:** Der Vorgänger 0,40 galt auf Langtext gegen Langtext und maß damit Textsortengleichheit, 52 von 56 Impulsen kamen durch; die 0,30 gilt auf Stapeltext gegen Nutzeräußerung und steht auf drei Äußerungen — begründete Setzung, kein belastbarer Messwert. Riegel **3** hat eine dritte Bedingung bekommen (`_rueckfrage_offen`, **vor** dem Burst-Zähler, damit ein unterdrückter Impuls die nächste Gelegenheit nicht mitverbraucht); der Satz von 04.08., dass **kein** Modus den Cooldown bricht, bleibt davon unberührt — die Bedingung kann nur zusätzlich verhindern, nie zusätzlich erlauben. **§3 war darüber hinaus an drei Stellen älter als das eigene Dokument** — alle drei sind Fälle von *nicht nur weiter unten korrigieren*: Die Intentions-Tabelle führte `emotionaler_ausdruck` → `nachfragen` weiter, obwohl §6 den Wegfall entscheidet und §9 ihn vollzieht (geprüft: in beiden Kopien steht `""`). Das Codebeispiel des Routers zeigte ein Literal, das seit dem 05.08. durch `EMOTIONS_VEKTOREN_DRUCK` ersetzt ist — der Grep im Router findet es nicht mehr. Und **fünf von fünf Zeilenzitaten des Abschnitts waren überholt**; sie sind durch Ankernamen ersetzt, wie es die Doku-Grundsätze verlangen. §7: Die Kompaktzeile ist durch einen **Zeiger** ersetzt statt durch eine zweite Aufzählung, weil eine Kopie der Riegelliste hier zuerst altern würde. **Der Reiz-Satz ist halb überholt und bleibt stehen:** Er gilt weiter für *wer formuliert*, nicht mehr für *auf welchen Platz das Material geht* — als er geschrieben wurde, war das dieselbe Frage. Der Gedanke reist als `eigener_gedanke` und kommt in beiden erzeugenden Stufen als **Block** an; im Ereignis für den CharacterGraph **fehlt `user_prompt` ganz**, nicht leer, sondern abwesend.
- **v0.6 — 05.08.26:** **Gebaut und gemessen**, §9 neu. Stufe 1 laeuft ohne Modellaufruf und erzeugt den Reiz aus drei Farbton-Saetzen und dem Anlass. Die wertvollere Haelfte der Messung ist die stille: ein sechs Tage alter Auftrag gegen die laufende Session, Vektor `eskalation`, kein Stapel-Eintrag, beide Audit-Zeilen nachgewiesen — §8.1 im Betrieb. Zwei Gegenproben vorher benannt und exakt eingetroffen (7 und 2). Ausdruecklich ungemessen bleibt der Weg vom Turn zum Vektor: Ein Absturz laesst sich nicht bestellen, und ihn in der Produktivsession zu setzen hiesse, falsche Gefuehlshistorie zu schreiben. Der Auslöser `emotionaler_ausdruck` ist in beiden Kopien entfernt, der Vektor-Kanon steht als Konstante — Letzteres eine benannte Abweichung von der Abgrenzung in §8.7.
- **v0.5 — 05.08.26:** §8.8 neu — **das Zuwendungsrad macht die Nachfrage wahrscheinlicher oder unwahrscheinlicher.** Die Größe war bereits gebaut und heißt `fragen` (`SPEICHEN_BEITRAG` in `ei/haltung.py`); `pflicht` trägt dort **−0.20**, weil „Auftraege ernst nehmen" abarbeitet statt fragt. Bis heute wirkt sie erst stromabwärts und formt, *wie* Nova fragt, nicht *ob* die Nachfrage aufgeworfen wird. **Damit ist die Entscheidung aus §4 korrigiert:** Aus „der Agent entscheidet nicht" war fälschlich „der Charakter spricht nicht mit" geworden, was `novaberg-klaerung_k.md` §2.1 widerspricht — das Fragen ist die eine Stufe, die der Charakter abwägen darf. Der Charakter wägt ab, aber in der Zustellung. Der Faktor ist **multiplikativ**, damit „kein Veto" eine Eigenschaft der Bauart ist und nicht der Kalibrierung: Ein Summand könnte den Score auf null drücken, und ein Eintrag mit Score ≤ 0 gewinnt auch als einziger nie. Das Rad wird zur Zustellzeit gelesen — womit das fehlende Gewichtsfeld des Stapels für diesen Zweck **entfällt**. Eigenes Bauteil `PIX-STAPEL-RADFAKTOR`, weil es alle Aufgabenarten betrifft.
- **v0.4 — 05.08.26:** §8 neu — **der Bauplan.** Die tragende Entscheidung ist, dass der Druck **frisch gelesen** und nicht dem Auftrag entnommen wird: Die Aufträge im Bestand sind fünf bis neun Tage alt, und Zuwendung zu einem Druck, der vorbei ist, ist keine. Stufe 1 verdichtet **ohne Modellaufruf** — der Farbton spricht bereits im Zielregister, ein Hintergrundaufruf kostet hier 35 bis 38 Sekunden, und die deterministische Fassung ist der Zeuge, gegen den eine spätere Modellfassung zu messen wäre. Kein KZG-, Bibliotheks- oder Ziel-Schreiben, weil kein Wissen entsteht. Der Ausgang „kein Druck mehr" ist ausdrücklich `erledigt` und nicht `fehler`. ZIEL, TEST und MESSUNG stehen, samt der Hürde, dass ein Absturz sich nicht bestellen lässt — erreichbar über ein wissenschaftliches Thema mit negativer Valenz, weil der Vektor die Bewegung liest und nicht den Gegenstand.
- **v0.3 — 05.08.26:** §2 um das prüfbare Kriterium geschärft — **die EI-Erkennung hat einen Druck gefunden**; Nova will präsent sein und fragt deshalb. Damit sind zwei Punkte ableitbar geworden, die eine Stunde vorher noch als „nicht abzuleiten" markiert waren. §7 neu — **die elementare Aufgabe**: Ein Agent legt einen Reiz ab und formuliert nicht; das Material ist der Druck, und die EI rechnet ihn bereits als Bewegung (`ei/berechnung.py`), als Klartext (`ei/farbton.py`) und als Schwere (`ei/dreischicht.py`). Der erste Punkt aus §4 ist damit nicht beantwortet, sondern als **falsch gestellt** erkannt: Er fragte nach einer Formulierung. In §6 entschieden: `emotionaler_ausdruck` → `nachfragen` ist ein **Defekt** und entfällt, weil die Intention keinen Druck trägt.
- **v0.2 — 05.08.26:** §6 neu — die Trennung in zwei Agenten, entschieden, nachdem der Widerspruch zwischen diesem Dokument und `novaberg-autonomous-wissen_k.md` §11.3 gefunden war. Drei der vier offenen Punkte aus §4 entschieden, der erste (die Form) bleibt und ist als einziger offen gekennzeichnet — belegt durch eine Suche über alle Konzepte, die ihn nicht füllt. §5 um die Messung ergänzt, die den dort beschriebenen Defekt als **latent** ausweist: Die Recherche-Aufträge verdrängen die agentenlosen, und den Heartbeat blockiert stattdessen der besetzte Slot. Neu belegt und in §6 festgehalten: Der Auslöser `emotionaler_ausdruck` feuert auch bei positiver Emotion und widerspricht damit §2.
- **v0.1 — 27.07.26:** Erstfassung. Hält fest, was an vier Stellen verdrahtet ist, und trennt es von dem, was nicht entschieden ist.
