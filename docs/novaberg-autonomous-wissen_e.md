# Novaberg — Autonomes Wissen (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-autonomous-wissen_k.md`](novaberg-autonomous-wissen_k.md) · Ausarbeitung: [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md) · Bauplan und Umstellung: [`novaberg-autonomous-wissen_b.md`](novaberg-autonomous-wissen_b.md) · Messungen: [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §11.3, Kasten *„Entschieden am 04.08.2026: Keine der Sperren wird gebrochen — von keinem Modus.“* | Weder `klaerfrage` noch `traum` bricht eine Sperre der Zustellung. **Seit dem 15.08.2026 gegenstandslos**, weil es den Cooldown nicht mehr gibt (Abschnitt D, §11.8; Abschnitt F, v0.6) — die Entscheidung bleibt stehen | 04.08.2026 |
| **E2** | `_t` §11.3, Kasten *„Umbenannt am 05.08.2026“*: *„Entschieden ist, dass es **zwei Agenten** sind“* | `nachfragen` behält die Rolle aus `novaberg-pixie-nachfragen_k.md`, die Wissensrolle heißt `klaerfrage` | 05.08.2026 |

Der Wortlaut der Entscheidungen steht in keinem der beiden Abschnitte; E1 gibt den Beschluss als Satz mit Begründung wieder, E2 als Ergebnis.

**Im Text als entschieden oder gewählt geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §11.1: der Weg über den Benutzernamensraum *„wurde verworfen“*; die Rechte werden im Schreibpfad gesetzt.
- `_t` §11.7: *„Der Verfall wird ein dritter Schritt des vorhandenen Tageslaufs“* — *„die gewählte Variante“*.
- `_t` §11.5: *„Die Schwelle bleibt bei 0.60 — belegt, nicht übernommen.“*
- `_t` §11.6: die Startwerte des Stapels — ausdrücklich *„Kalibrierung, keine Festlegung“*.
- `_b`, *Audit*: verweist auf eine Entscheidung vom 18.09.2026, die in `novaberg-convention-nmcp.md` §8.4 steht, nicht hier.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage an den Meister.

**Offen ohne Frage an den Meister** — was das Konzept selbst als offen führt:

- Abschnitt D (§11.8): Priorität und Salienz als eine oder zwei Größen; woran eine Verstärkung erkannt wird (*„Das ist eine Entscheidung, keine Ableitung“* — ohne Adressat); ob der Verfall eine eigene Frequenz braucht; ob der Stapel eine harte Obergrenze braucht.
- `_k`, Vorrang-Hinweis zum Erkenntniszyklus: *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.“*
- `_t` §11.3: die Schwelle, ab der ein Vertiefungsergebnis *„dieselbe Datei“* trifft — *„Offen, und vor `vertiefung` zu messen.“*
- `_t` §7.3a: die dritte Rolle *Werkzeug* (`SILO-OHNE-WERKZEUG`) und die Schwelle der Bibliothek (`WIS-SCHWELLE-MESSEN`); `_t` §7.3a, *Die Tiefe bleibt Stufe 1*: Stufe 2 ist nicht gebaut.
- `_t` §11.6: die Startwerte des Stapels nach einigen Wochen Betrieb gegen die tatsächliche Verteilung prüfen.
- `_m`, *Befunde aus dem Betrieb*: *„geprueft ist keiner von ihnen gegen den heutigen Code“*.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k`, Vorrang-Hinweise — §1 bis §10 sind der Entwurf vom April, §11 hat Vorrang; Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst, sondern erst nach einer gefundenen Lücke.
- `_t` §2.2 — die flache Ablage je Charakter; durchgestrichen, am 22.08.2026 um die Nutzerebene erweitert.
- `_t` §7.2 — der Tabellenentwurf mit `context_user`/`charakter`, `salienz FLOAT DEFAULT 0.0` und `ivfflat`-Index; gebaut in der Fassung von §11, der Index nicht angelegt.
- `_t` §11.1 — der Weg über den Benutzernamensraum; verworfen.
- `_t` §11.3 — der Satz, `nachfragen` komme in keinem Konzept vor (durchgestrichen, widerlegt am 05.08.2026); die Annahme, `klaerfrage` könne die vorhandenen Aufträge übernehmen; der Cooldown als Schutz (bis zum 15.08.2026).
- `_t` §11.5 — das Löschen ähnlicher Stapel-Einträge als *„Duplikat“*; der frühere Vorschlag 0.50 für die Schwelle, widerlegt.
- `_t` §11.6 — die Knoten-Rate für den Stapel; Redis als Ort der Bibliothek.
- `_t` §11.7 — ein eigener Agent `gedanken_decay` (bleibt die Wahl, falls eine andere Frequenz nötig wird); der Verdacht, Tagesläufe verhungerten hinter der Recherche, widerlegt.

---

## D. Aus §11 — Was offen bleibt

Die übrigen Unterabschnitte von §11 stehen in [`novaberg-autonomous-wissen_t.md`](novaberg-autonomous-wissen_t.md).

### 11.8 Was offen bleibt

**Sind Priorität und Salienz zwei Größen oder eine?** Die Shadow-Queue schreibt `prioritaet`, der Dispatcher liest `salienz` — zwei Funde vom 27.07.2026 beschreiben das als Defekt. Bevor eine zweistufige Sortierung „erst Priorität, dann Bedeutung" in eine Tabellendefinition eingeht, muss feststehen, ob sich die beiden überhaupt unterscheiden. Sollen sie es: **Priorität = wie dringend, Salienz = wie bedeutsam.**

**Woran wird eine Verstärkung erkannt?** Vorschlag: an derselben Embedding-Nähe von 0.60, die heute löscht. Das ist eine Entscheidung, keine Ableitung.

~~**Darf ein bedeutsames Anliegen den Zustellungs-Cooldown brechen?**~~ **Entschieden am 04.08.2026: nein, von keinem Modus.** Begründung in §11.3. → **Seit dem 15.08.2026 gegenstandslos:** Es gibt keinen Cooldown mehr, den ein Modus brechen könnte. Die Entscheidung bleibt richtig und hat keinen Gegenstand.

**Braucht der Verfall später eine eigene Frequenz?** Dann wird aus dem dritten Schritt ein eigener Agent (§11.7).

**Braucht der Stapel zusätzlich eine harte Obergrenze?** Mit dem Verfall greift sie im Normalbetrieb nie. Als Netz gegen einen Fehler im Produzenten wäre sie trotzdem sinnvoll — die Größenordnung folgt aus §11.6, nicht aus einer runden Zahl.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B6 stammen aus der Sichtung, B7 bis B11 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf*, Feld **Status** | *„⬜ **nicht gebaut.**“*; `_t` §7.2 (*Gebaut am 04.08.2026*), `_b` *Aus §11.6* (Tabelle, Schreibpfad `WIS-3`), `_t` §7.3a (*Gebaut, nicht geplant*), `_t` §2.2 (Umzug vom 22.08.2026) und `_b` *Audit* belegen Gebautes — tatsächlich teilweise | `[gelesen 19.09.2026]` |
| **B2** | `_t` §2.1 gegen `_t` §11.1 | Speicherort `obsidian-vault/autonomous/` gegen `knowledge/` außerhalb des Repositoriums | `[gelesen 19.09.2026]` |
| **B3** | `_t` §7.2 (Nachtrag 18.08.2026) gegen `_t` §2.2 (22.08.2026) | *„die Bibliothek trägt 234 Dateien“* gegen *„1097 Dateien über 17 Kennungen“* — verschiedene Zeitpunkte, ohne Bezug aufeinander | `[gelesen 19.09.2026]` |
| **B4** | `_b` §9 | Der Phasenplan vom April ist nicht nachgezogen; `WIS-2`, `WIS-3`, der zweite Eingang und der Umzug kommen darin nicht vor | `[gelesen 19.09.2026]` |
| **B5** | `_k`, Vorrang-Hinweis zum Erkenntniszyklus | *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus“* — unerledigt seit dem 06.08.2026 | `[gelesen 19.09.2026]` |
| **B6** | `_m`, *Befunde aus dem Betrieb* | Rohe Betriebsbefunde, ausdrücklich ungeprüft gegen den Code angehängt | `[gelesen 19.09.2026]` |
| **B7** | `_t` §7.3 (Stufe 1) · `_t` §7.3a · `_m`, *Befunde aus dem Betrieb* | Die Abrufschwelle steht in drei Fassungen: `themen_embedding <=> %s < 0.4` als Distanz (§7.3), *„Der Befund vom 17.08.2026 … fand 0,40 zu lasch“* (§7.3a), *„Die Abrufschwelle steht auf **0,50**“* (20.08.2026) — ein Wechsel ist nicht vermerkt | `[gelesen 19.09.2026]` |
| **B8** | `_t` §11.6, Absatz *Warum die Bibliothek nach PostgreSQL gehört* | `pgvector` *„durchsucht ihn über `ivfflat`“*; `_t` §7.2 sagt, der `ivfflat`-Index ist nicht angelegt | `[gelesen 19.09.2026]` |
| **B9** | `_b`, *Aus §11.6*, *Was damit noch nicht gebaut ist* | Die Gewichtsspalten *„bekommen ihre Werte erst mit `WIS-3` (Schreibpfad) und `WIS-5` (Verfall)“*; zwei Absätze davor steht *„`WIS-3` gebaut am 04.08.2026“* — ob `WIS-3` die Spalten schreibt, sagt der Text nicht | `[gelesen 19.09.2026]` |
| **B10** | `_t` §6.2, Schritt 5 | *„DESTILLATION [Gemma4, Sprache]“*; nach `novaberg-microservice-modell-queue_t.md` §5 läuft der Hintergrund über `qwen36-cpu` für Sprache und Analyse | `[gelesen 19.09.2026]` |
| **B11** | Abschnitt D (§11.8), erste Frage | *„Sind Priorität und Salienz zwei Größen oder eine?“* steht offen; `novaberg-queue-verfall_k.md` §3 (heute `_t`) hat `prioritaet` als Salienz des auslösenden Turns benannt und in drei Salienz-Felder zerlegt, und dessen §16 (heute `_b`) berichtigt den Dispatcher, der `salienz` las — die Frage trägt keine Marke | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Versionshistorie

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Autonomes Wissensverzeichnis — Recherche, Vertiefung, Klaerfrage, Traeumen
**Stand:** 18. September 2026 (Audit: der Dienst belegt seinen Lauf selbst). Davor 22. August 2026 (v0.7 — **`autonomous/{charakter}/{context_user}/`**: der Speicher bekommt eine Ebene und wird als Wurzel adressierbar, §2.2 und §2.3). Davor: 15. August 2026 (v0.6); davor 4. August 2026 (Erstfassung 29. April 2026, Chat 70)
**Pfad:** novaberg/docs/novaberg-autonomous-wissen_k.md
**Status:** ⬜ **nicht gebaut.** Die Erstfassung ist drei Monate alt und wurde nie umgesetzt; §11 traegt die Ueberarbeitung auf den heutigen Stand.
**Quellen:** Chat 70 (autoresearch, Claude Code autoDream, SWE-agent, Letta, Sleep-time Compute Paper)
**Verwandt:** `novaberg-klaerung_k.md` (woher der Auftrag kommt) · `novaberg-gedankenkette_k.md` (wie er ueber mehrere Zuege traegt) · `novaberg-wissensluecken_k.md` (Themen-Neugier, ein anderer Gegenstand)

## Versionshistorie

- **v0.6 — 15.08.2026:** Zwei Stellen nachgezogen, weil **der Zustellungs-Cooldown nicht mehr existiert** (`novaberg-eigenzeit_k.md` §2.5). §11 nennt als Schutz jetzt Burst-Grenze und Verträglichkeitsprüfung ohne ihn, und die Entscheidung vom 04.08.2026 — kein Modus bricht den Cooldown — ist als **gegenstandslos** markiert statt gelöscht: Sie war richtig und hat ihren Gegenstand verloren.

- **v0.5 — 05.08.2026:** §11.3 heißt **Die Klärfrage ist die dritte Quelle** — der Modus hieß hier `nachfragen`, und der Name war bereits vergeben. `novaberg-pixie-nachfragen_k.md` (27.07.2026) beschreibt unter demselben Namen eine andere Rolle, Zuwendung statt Wissen, verdrahtet an vier Stellen im Code. **Widerlegt** ist damit der Satz dieses Abschnitts, `nachfragen` komme „in keinem Konzept vor" — es kam in einem vor, acht Tage älteren, das bei der Abfassung nicht gefunden wurde. Entschieden ist die Trennung in **zwei Agenten**; die Abgrenzung steht in jenem Dokument §6, hier bleibt alles inhaltlich gültig unter dem Namen `klaerfrage`. Zusätzlich am Bestand belegt: Die 62 vorhandenen `nachfragen`-Aufträge tragen `freude`/`begeisterung` und keine Wissenslücke — dieser Modus kann sie nicht übernehmen und braucht einen eigenen Erzeuger, der auf `KLA-K1`/`KLA-K2` wartet.
- **v0.4 — 04.08.2026:** `WIS-3` gebaut, am `recherche`-Agenten. §11.3 um die **Reichweite** erweitert: Quelle ist nicht der einzige Unterschied zwischen `recherche` und `vertiefung` — Recherche steckt einen flachen, breiten Umkreis ab, Vertiefung gräbt an einer Stelle und liegt ihrem Ausgangsthema im Vektorraum **näher**. Daraus folgt, dass die Schwelle, ab der ein Ergebnis „dieselbe Datei" trifft, für die beiden Modi nicht dieselbe Frage ist; die 0.60 aus §11.5 ist an Gedächtnisknoten gemessen, nicht an Vertiefungsergebnissen. §11.6 hält fest, was der Bau ergänzt hat: Ein **gescheiterter Durchlauf hinterlässt einen Bericht**, und das Gate wird dabei übergangen.
- **v0.3 — 04.08.2026:** `WIS-2` gebaut. §7.2 trägt eine Marke: Die Tabelle steht in der Fassung von §11, und der dort genannte `ivfflat`-Index ist **nicht** angelegt — bei kleinen Zeilenzahlen bricht sein Recall auf nahezu null ein, belegt in Chat 107 an `lzg_knoten`. §11.6 hält fest, was gebaut ist und was nicht: Die Spalten stehen, die Kurve rechnet niemand, bis `WIS-3` und `WIS-5` da sind. Drei Zusicherungen liegen im Schema statt im Code — Paar-Tripel und `salienz_anfang` ohne Vorgabewert, `dateipfad UNIQUE` —, alle drei live geprüft.
- **v0.2 — 04.08.2026:** §11 ergänzt — die Überarbeitung auf den heutigen Stand, nachdem die Erstfassung drei Monate ungebaut lag. Sechs Punkte: der Speicherort liegt **außerhalb des Git-Roots** (die Erstfassung nannte die Repo-Grenze nicht, obwohl die Dateien aus Gesprächen abgeleitete Inhalte tragen); das **Paar-Schema** ersetzt `context_user`/`charakter`; **`nachfragen` ist die dritte Quelle** und bekommt hier zum ersten Mal überhaupt eine Aufgabenbeschreibung — es existierte seit Monaten als Routing-Ziel ohne Konzept, weshalb der Agent nie gebaut wurde; die auslösende **Salienz ohne Vorgabewert**; das **Aufräumen wird Fortsetzen**, weil Embedding-Nähe „vom selben Thema" heißt und nicht „schon gesagt" — mit der Schwelle 0.60 an **778.128 Paaren** aus 1248 LZG-Knoten belegt (Trefferverhältnis 10 : 1) und einem Zwischenvorschlag von 0.50 widerlegt, der aus einer zu kleinen Stichprobe stammte; und **Gewichtung, Sättigung und Verfall nach dem Knoten-Schema** mit hergeleiteten Startwerten (Dämpfungs-Exponent 1.0, λ = 0.0768 für 60 Tage); ; die Bibliothek erbt den Verfall des LZG **samt Konstante**, nur der Stapel bekommt eine eigene Rate; und **wer den Verfall rechnet** — ein dritter Schritt im vorhandenen Tageslauf `synapsen_decay` statt eines neuen Agenten, weil jeder periodische Auftrag um denselben einen seriellen Platz konkurriert. Dabei widerlegt: die Vermutung, niedrig priorisierte Tagesläufe verhungerten hinter der blockierenden Recherche — 14 und 16 Läufe im Audit-Protokoll belegen das Gegenteil. Die §§1–10 bleiben stehen und tragen ihre Begründungen; §11 hat Vorrang, wo sie widersprechen.
- **v0.1 — 29.04.2026:** Erstfassung. Verzeichnisstruktur, Wissen- und Bericht-Datei, Keep/Discard-Gate, agentische Iteration, Metadaten-Tabelle und Zwei-Stufen-Retrieval, Prune-Zyklus, Implementierungsreihenfolge.
