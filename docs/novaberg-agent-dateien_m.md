# Novaberg — Der Dateien-Dienst: ein Verzeichnis, das gelesen werden darf (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-agent-dateien_k.md`](novaberg-agent-dateien_k.md) · Ausarbeitung: [`novaberg-agent-dateien_t.md`](novaberg-agent-dateien_t.md) · Bauplan und Umstellung: [`novaberg-agent-dateien_b.md`](novaberg-agent-dateien_b.md) · Diskussion und Ergänzungen: [`novaberg-agent-dateien_e.md`](novaberg-agent-dateien_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts samt Zustandsteil, ungekürzt. Er steht hier, weil er Messwerte trägt (Zeugen, Erstlauf, Kosinus im Betrieb).

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Indizierung und Durchsuchung eines vorgegebenen Verzeichnisses als NMCP-Dienst
**Stand:** 25. August 2026 (v0.20 — §4b.3: die Zahl loest die Frage aus, das Modell beantwortet sie; ein Nebensatz verschiebt die Aehnlichkeit weiter, als eine Schwelle reicht. Davor v0.19: der Vergleich ist justierbar, Schwelle an den echten Faellen abgelesen und an `pg_trgm` geeicht. Davor v0.18: *„ohne Dopplung" war eine Absicht, kein Riegel*; der Rueckweg setzte eine Kopie neben ihr Original, und `paarung_pruefen` hielt dabei). Davor: 23. August 2026 (v0.17 — die Prompt-Dateien beider Bloecke und der Kanon der Eigentumswerte sind benannt. Davor: 22. August 2026, v0.16 — **jede Wurzel traegt, wessen Material sie enthaelt**, und der Block haengt daran: neuer §1a.5. Davor: 18. August 2026, v0.15)
**Pfad:** novaberg/docs/novaberg-agent-dateien_k.md
**Typ:** Konzept (`_k`)
**Status:** 🟠 **Stufe 1 bis 3 gebaut und gemessen, Stufe 4 zur Hälfte** (18.08.2026) — Freigabe, Wächter und die Enricher-Quelle laufen, letztere seit heute **zweikanalig**; Suche und Zoom des Auftrags-Wegs stehen. **Was fehlt, ist der Aufrufer:** Aushang, Klassifikation und Dispatch des Dienstes `dateien` (§8.1). Offen bleibt der Rückweg (§4b).
**Voraussetzung:** `novaberg-tool-dateien_k.md` (die Operationen — teils gebaut) · `novaberg-convention-nmcp.md` (die Anmeldung) · `novaberg-convention-verfall.md` (warum hier kein Verfall)
**Abgrenzung:** `novaberg-autonomous-wissen_k.md` — die Bibliothek ist Novas **eigenes** Wissen und ein anderer Korpus, siehe §2

> **Zustandsteil, ausdrücklich getrennt.** **Die Werkzeugschicht ist seit dem 18.08.2026 gebaut; am selben Tag kam der erste Dienst dazu.**
>
> | | Stand |
> |---|---|
> | `tools/dateien/operationen.py` — Karte, Block, Fenster, Fundstelle | **gebaut**, 26 Zeugen |
> | `tools/dateien/redaktion.py` — chirurgische Schnitte | **gebaut**, 20 Zeugen |
> | `tools/dateien/versionierung.py` — `[cN>]`/`[dN>]`/`[iN>]`, Paarungsprüfung | **gebaut**, 20 Zeugen |
> | `tools/dateien/hand.py` — Auftragsform `DATEI: {json}` | **gebaut**, 22 Zeugen |
> | Schreibvorlage erzeugt `## AKTUELL` + Version | **gebaut und produktiv** — 10 Dateien belegt |
> | ~~**Kein Aufrufer** — kein Knoten ruft die Werkzeuge, keine Anleitung in einem Prompt~~ | ⬜ **gilt weiter für `tools/dateien/`** — der Wurzeln-Dienst ruft sie nicht, er verwaltet Freigaben |
> | `agents/dateien_wurzeln/` — Freigeben, Lesen, Umbenennen, Zurücknehmen, Wiederaufnehmen | **gebaut**, 48 Zeugen, im Betrieb gemessen |
> | `agents/dateien_wurzeln/aussenrand.py` — die Schranke aus §7 | **gebaut**, Gegenprobe 5/5 |
> | Tabelle `dateien_wurzeln` | **steht** — DDL am 18.08.2026 angekündigt und freigegeben |
> | `dateien_index` — Indextabelle und Wächter | **gebaut**, 18 Zeugen · Erstlauf 3 Dateien in 16 s, zweiter Lauf 0 Modellaufrufe |
> | Der **Takt** des Wächters | ⬜ — `periodic_task()` ist None, bis die Änderungsrate gemessen ist; Anstoß über `/admin/dateien/index` |
> | `zuletzt_gelernt_hash` | ⬜ Spalte steht, **kein Schreiber** — sie gehört zum frühen Tor (§3.0d) |
> | `dateien` — der lesende Dienst am Empfang | 🟠 **halb** — Suche und Zoom stehen, der Empfang fehlt |
> | Die Enricher-Quelle und der Block `[AUFZEICHNUNGEN]` (§1a.2) | **gebaut**, 27 Zeugen · seit dem 18.08.2026 **zweikanalig** (§6.3a) · im Betrieb: scharfer Kanal 0,4879, Fremdthema 0 Treffer, und zwei Treffer unter dem Boden, die nur der scharfe Kanal fand |
> | `agents/dateien/suche.py` — drei Kanäle, scharf vor unscharf | **gebaut**, gegen den echten Bestand gemessen · **kein Aufrufer** |
> | `agents/dateien/zoom.py` — Karte, Block, Nadel | **gebaut** · die Karte kostet keinen Dateizugriff · **kein Aufrufer** |
> | `dateien` — Aushang, Klassifikation, Dispatch | ⬜ **fehlt** — damit hat der Zoom kein Gespräch, das ihn ruft |
>
> **Die Werkzeuge funktionieren, das System benutzt sie nicht.** Das ist der Unterschied zwischen einem geprüften Bauteil und einer Verdrahtung.
>
> **Für den Wurzeln-Dienst gilt das seit dem 18.08.2026 nicht mehr**, und der Beleg ist ein Betriebslog und keine Testbilanz: `Router: mgmt=agent/dateien_wurzeln` → `Planner: Match via target` → `Agent-Dispatch` → Tor → `verifiziert=True`. **Eine Freigabe ohne Leser bleibt es trotzdem** — es gibt noch nichts, das die freigegebenen Verzeichnisse liest.

---

## Aus §1a.5

### 1a.5 Nicht jede Wurzel trägt fremdes Material (22.08.2026)

Der übrige Abschnitt steht in [`novaberg-agent-dateien_t.md`](novaberg-agent-dateien_t.md).

> **Gemessen im Betrieb, 22.08.2026.** Auf *„Du hast fleißig recherchiert"* antwortet sie zunächst richtig — *„meine kleinen Studien"* —, dreht aber im selben Absatz auf *„dient **dir** das eigentlich"*. Auf die ausdrückliche Korrektur *„Du recherchierst ja, nicht ich"* antwortet sie: *„die ganze Recherche war **dein** Werk, nicht meins. Ich habe nur beobachtet."*
>
> **Der Fehler pflanzt sich über §1a.4 fort:** Ein Langzeit-Knoten desselben Tages trägt bereits *„Nova fragt den Nutzer, ob **seine** Recherche…"*.

---

## Aus §1a.4

### 1a.4 Die Beschriftung trägt die Herkunft über den Gedächtnis-Übergang

Der Abschnitt steht in [`novaberg-agent-dateien_k.md`](novaberg-agent-dateien_k.md); der Kasten folgt dort auf *„Das ist prüfbar und gehört in die Messung …“*.

> **`[gemessen]` — 18.08.2026, und der Weg ist am Tag seines Baus gelaufen.** Der Messturn erzeugte genau einen KZG-Eintrag mit Dateibezug (`beobachter=assistant`, 13:53:31). Nachgeholt über den Suchvektor desselben Themas, liefert der Abruf ihn zurück, und der Formatter rendert ihn als `[KZG]`-Zeile — **also unter `[GEDAECHTNIS]`**. Von 2908 KZG-Einträgen trägt einer einen Dateipfad; `/files` steht dort sogar in der Themenspalte.
>
> **Die Zusicherung dieses Abschnitts hat gehalten, und zwar als einzige:** Der gespeicherte Wortlaut trägt die Herkunft dreimal mit — *„… laut `/files/novaberg-papers-stoffsammlung_k.md`"*. Ohne die Beschriftung stünde dort ab Turn N+1 eine herkunftslose Aussage, die sie als eigene vertritt, **und kein Tor liegt auf diesem Weg**.
>
> **Was die Messung offenlässt, ist keine Umsetzungsfrage:** Ob die Aneignung *„sie hat es gelesen, also erinnert sie sich, es gelesen zu haben"* gewollt ist, sagt weder dieses Konzept noch der Code. Beide Lesarten sind vertretbar, und die Wahl ändert das Verhalten — sie gehört entschieden, nicht abgeleitet. Bis dahin gilt die gebaute: Die Erinnerung an das **Nachsehen** entsteht, der Dateiinhalt bleibt in der Datei. Der Blocktext sagt seit dem 18.08.2026 genau das, nachdem seine erste Fassung (*„Woran du dich erinnerst, steht in [GEDAECHTNIS]"*) ab Turn N+1 unwahr geworden wäre.
>
> **Was den Weg sichtbar gemacht hat, war der Blick über die Turn-Grenze** — alle Belege des Umbaus (19 Zeugen, zwei Gegenproben, zwei Messturns) liegen **innerhalb** eines Turns, und diese Zusicherung gilt über ihn hinaus. Wer den gebauten Weg abgeht, findet sie nicht; sie liegt quer dazu.

---

## §3.0a

Der Unterabschnitt *Was daraus für den Index folgt* steht in [`novaberg-agent-dateien_t.md`](novaberg-agent-dateien_t.md).

### 3.0a Die Schwelle wird gemessen, nicht gesetzt — und 0,40 war keine Messung

Ein Block, der in jedem Turn erscheint, ist Rauschen; einer, der nie erscheint, ist tot. Dazwischen liegt eine Schwelle auf dem Kosinus, und **sie darf nicht geschätzt werden.**

Der Grund steht im Bestand: Am selben Embedding gemessen liegt **Beziehungsprosa sechs einander fremder Menschen bei 0,774** — eine Zahl, die nach hoher Ähnlichkeit aussieht und keine ist. Wer eine Schwelle nach Gefühl auf 0,7 setzt, bekommt bei jedem Turn Treffer.

**Also: erst den Korpus vermessen, dann die Schwelle setzen.** Die Nebenbedingung ist dieselbe wie bei den Gesprächslandschaften — die Schwelle trennt nur dann etwas, wenn beide Seiten vorkommen.

#### Der Präzedenzwert hat der Prüfung nicht standgehalten

Bis v0.6 stand hier, die Bibliothek liefere mit **0,40** einen gemessenen Anhalt, und der Index solle dort starten. **Das ist widerlegt — und der Bestand hatte es die ganze Zeit dazugesagt.**

Der Wert hat eine Herkunftskette, und jede Stufe außer der letzten trägt ihren Vorbehalt mit:

| Stufe | Was dort steht |
|---|---|
| **Ankerabruf** des Langzeitgedächtnisses | 0,40 ist **kalibriert** — 100 echte Prompts gegen 302 Knoten: 0,50 → 53 % Abdeckung, **0,40 → 82 % bei 4,1 Ankern**, 0,35 → 89 % und Rauschen. Dazu die Marke *„begründeter Startwert, kein Verteilungs-Messergebnis"* |
| **Bibliothek** | *„von `anker_retrieval` übernommen, **NICHT gemessen**"* — mit Grund: *„die Bibliothek hatte bei ihrer Einführung drei Zeilen"*. Ein offener Backlog-Eintrag verlangt die Messung, sobald Bestand da ist |
| **dieses Konzept, v0.5** | *„ein gemessener Wert eines anderen Korpus"* |

> **Der Vorbehalt ist beim Kopieren verdunstet.** Zwei Code-Stellen sagen ausdrücklich, dass die Zahl ein Startwert und kein Ergebnis ist; übernommen wurde die Zahl, nicht der Satz daneben. **Das ist keine Nachlässigkeit einer Person, sondern die Eigenschaft eines Wertes, der ohne seine Messbedingung reist** — und der Grund, warum die Berichtigung hier nicht bloß eine andere Zahl einsetzt, sondern sagt, woran sie hängt.

Am 17.08.2026 gegen den laufenden Bestand gemessen:

| Messung | Ergebnis |
|---|---|
| Aufrufe der Bibliothek im Protokoll | 42 |
| davon mit **genau 3** Treffern | **40** — und `WISSEN_RETRIEVAL_TOP_K` ist 3 |
| Kosinus des **dritten** Treffers | min 0,404 · **Median 0,588** · max 0,691 |

**In 40 von 42 Aufrufen hat nicht die Schwelle ausgewählt, sondern die Kappung.** Das Ergebnis war genau so groß wie die Obergrenze — mehr Einträge lagen über 0,40, als geliefert wurden. Nur in **zwei** Aufrufen hat die Schwelle tatsächlich begrenzt; auf zwei Beobachtungen ist kein Wert kalibrierbar.

Die Gegenprobe über die Geometrie des Korpus selbst sagt dasselbe. Alle 217 aktiven Einträge paarweise gegeneinander, 23.436 Paare:

| Kosinus | Median | 95. Perzentil | Maximum |
|---|---|---|---|
| über alle Paare | **0,369** | 0,503 | 0,830 |

**Damit liegt 0,40 fast genau auf dem Median des Rauschens.** Ausgezählt: **35,6 % aller Paare liegen darüber** — für eine beliebige Anfrage qualifizieren sich rund **77 von 217** Einträgen. Was die Bibliothek vor diesem Ergebnis bewahrt, ist allein die Kappung bei drei.

#### Der Median sagt etwas über den Korpus, nicht über das Embedding

**Bevor man aus 0,369 auf ein schwaches Einbettungsmodell schließt, ist nachzusehen, was dort eigentlich liegt.** Alle 217 Einträge sind vom Modus `recherche`, alle mit eindeutigem Thema, entstanden in dreizehn Tagen — und sie stehen in **einem einzigen Register**:

> *Achtsamkeit, Präsenz im Augenblick* · *Bewusstsein, thermodynamische Entropie, ästhetische Erfahrung* · *Architektur der Beziehung, Gegensätzliche Vektoren* · *Bindung, Energie, Chaos vs. Ordnung* · *biologische Desidentifikation, Selbstschutz, Ich-Auflösung*

**Das ist kein Wissensbestand über die Welt, sondern eine Sammlung von Reflexionen über die Gespräche selbst** — durchweg abstrakt, relational, in derselben Sprachform.

> **Ein homogener Korpus hat eine hohe Grundähnlichkeit, und eine Schwelle darauf misst die Zugehörigkeit zur Textsorte statt das Thema.** Die teilen aber alle Einträge. Deshalb konnte hier keine Schwelle trennen — nicht weil das Maß schlecht ist, sondern weil beide Seiten fehlen, die sie trennen soll.

**Für den Dateien-Index ist das mehr als die Feststellung „anderer Korpus".** Fachtexte, Tabellen, Codeblöcke und Verzeichnisstrukturen sind **heterogen**; dort kann eine Schwelle trennen, wo sie es hier nie konnte. Die Zahl ist damit nicht nur zu übertragen verboten — sie ist auch in ihrer Richtung nicht übertragbar: Der eigene Korpus wird vermutlich eine **niedrigere** Grundähnlichkeit zeigen und damit eine andere Schwelle brauchen als die hier gerechnete.

| Schwelle | Anteil der Paare darüber | Treffer je Abfrage (217 Einträge) |
|---|---|---|
| **0,40** | 35,6 % | **77** |
| 0,45 | 16,6 % | 36 |
| 0,50 | 5,4 % | 12 |
| **0,55** | 1,4 % | **3** |
| 0,60 | 0,4 % | 0,8 |

> **Die wirksame Schwelle der Bibliothek ist 0,55, nicht 0,40** — die Zeile in der Konfiguration und die Zahl, die den Ausschlag gibt, sind zwei verschiedene Dinge. Der gemessene Median des dritten Treffers (0,588) und der gerechnete Wert für drei Treffer (0,55) treffen sich; zwei Zugänge, ein Ergebnis.

**Damit gibt die Messung der Übernahme quantitativ Unrecht.** Im Knotenraum, für den 0,40 kalibriert wurde, qualifiziert der Wert rund **1,4 %** des Bestandes (4,1 von 302). In der Bibliothek qualifiziert derselbe Wert **35,6 %**. Derselbe Embedding-Raum, **Faktor 26 im Trennverhalten** — eine Schwelle ist keine Eigenschaft des Raums, sondern eine Eigenschaft des Raums **und** der Dichte des Korpus darin.

> **Ein Vorbehalt zur Genauigkeit, weil er hierher gehört:** Die 35,6 % sind an Einträgen gegen Einträge gemessen, nicht an echten Anfragevektoren gegen Einträge — die Anfragevektoren werden nicht aufbewahrt. Als Beleg trägt das nur zusammen mit dem Betriebsbefund, und der ist unabhängig davon: **40 von 42 Aufrufen auf der Kappung** heißt, dass die Schwelle mehr durchgelassen hat, als geliefert wurde. Die Richtung ist damit belegt, die zweite Nachkommastelle nicht.

---

## Aus §5.6

### 5.6 Archiviert sieht nicht aus wie geltend

Der Abschnitt steht in [`novaberg-agent-dateien_t.md`](novaberg-agent-dateien_t.md).

**Gemessen am 23.08.2026 gegen den echten Bestand** (`labor/2026-08-23_archivetikett_betrieb.py`), über beide Wege aus `dateien_index` und alle 175 Indexzeilen: **6 etikettiert, 0 fälschlich, 0 Abweichungen** je Weg. 15 Zeugen. Gegenprobe: Etikett stillgelegt → 5 Zeugen rot (6 vorhergesagt; in `ErkennungTest` prüfen zwei Zeugen den archivierten Fall, nicht drei).

---

## §8.1a

### 8.1a Warum dieser Dienst nicht optional ist — gemessen, nicht argumentiert

Am 18.08.2026 wurde eigens eine Datei angelegt, die **Wissen trägt, das kein Sprachmodell haben kann**: die Rechenweise der Salienz im Kurzzeitgedächtnis, mit Schwelle 0,67379, den Bändern 0,84090 und 0,94393 und den Fristen 7 / 14 / 30 Tage. Damit ist *„aus der Datei"* von *„aus sich"* unterscheidbar — bei einer Frage nach Orchideen ist es das nicht.

**Das Ergebnis hat zwei Hälften.**

**Die Zuschreibung hält.** Der Enricher-Weg fand die Datei über den scharfen Kanal (0,4718), und die Antwort nannte die Fundstelle im Wortlaut: *„Wie in den Aufzeichnungen unter `/files/kzg-salienz.md` beschrieben …"*. Die Zusicherung aus §1a.4 ist damit an einem harten Fall belegt.

**Die Auskunft nicht.**

| Was in der Datei steht | Was die Antwort sagte |
|---|---|
| Schwelle bei **0,67379** | *„liegt nicht an einem festen Ort … eine bestimmte kritische Marke"* |
| **7 / 14 / 30 Tage** als Fristen **im** Kurzzeitgedächtnis | *„drei spezifische Fristen"* ohne Zahlen — und die hohe Frist als **Übergang ins Langzeitgedächtnis** gedeutet |

Die zweite Zeile ist eine sachliche Verschiebung, dazu eigene Ausschmückung, die in der Datei nicht vorkommt.

> **Und der Grund ist bauartbedingt, kein Modellfehler:** Der Enricher-Weg liefert **Thema und Zusammenfassung, nicht den Dateiinhalt**. Sie *konnte* die Zahl nicht wissen — sie hatte die Karte und nicht das Gebiet. In diese Lücke setzt ein Sprachmodell plausibel klingende Prosa.

**Damit ist die Arbeitsteilung aus §3.0 gemessen statt behauptet:** Der Enricher-Weg beantwortet *„hier liegt etwas"*. Wer *„und darin steht Folgendes"* beantworten will, muss die Datei lesen — und genau das ist dieser Dienst. Solange er fehlt, ist die Fundstelle richtig und die Auskunft daneben, **und beides steht im selben Satz**.

> **Der Gegenbeweis liegt seit dem 18.08.2026 abends daneben, am selben Bestand.** Der Dienst hat seinen Aufrufer; dieselbe Sache gefragt, antwortete sie:
>
> *„Ich habe die entsprechende Stelle in den Unterlagen unter `/files/kzg-salienz.md` verifiziert. […] liegt bei einem Wert von **0,67379**."*
>
> **Fundstelle und Zahl im selben Satz, und beide stimmen.** Der Weg im Betriebslog: scharfer Kanal 1 Treffer, Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen. Damit ist §8.1a keine Begründung mehr für einen fehlenden Bauteil, sondern die Messung, die seinen Nutzen belegt — **die beiden Läufe unterscheiden sich in genau einem Bauteil.**

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **19.08.2026** — **Der schreibende Speicher ist der leere, der volle ist der lesende.** `notizen` ist das einzige Silo, in das eine Nutzeräußerung Text ablegen kann — der Zettel löst auf *erstellen, bearbeiten, löschen* aus und sogar implizit aus dem Verlauf (*„Wir brauchen auch Erdbeeren"*). Gezählt: **1 Notiz, 1 aktiv, jüngste Änderung 01.08.2026 16:18 UTC** — seit 18 Tagen unberührt. Der Dateien-Verbund führt dagegen 14 Dateien, wird laufend gelesen und hat **keinen** Schreibpfad: Der Manager trägt eine Methode, deren Nachbedingung 0 ist und die einen Schreibversuch als `logger.error` meldet. **Die Fähigkeit liegt vollständig vor** (`tools/dateien/redaktion.py` mit chirurgischen Schnitten, `versionierung.py` mit Paarungsprüfung, je 20 Zeugen) — es fehlt allein ein Eingang von der Nutzerseite. **Das verschiebt die Gewichtung von `SILO-OHNE-WERKZEUG`:** Das Silo, dem etwas fehlt, ist nicht das ungenutzte.
