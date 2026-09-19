# Novaberg — Der Dateien-Dienst: ein Verzeichnis, das gelesen werden darf (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-agent-dateien_k.md`](novaberg-agent-dateien_k.md) · Ausarbeitung: [`novaberg-agent-dateien_t.md`](novaberg-agent-dateien_t.md) · Bauplan und Umstellung: [`novaberg-agent-dateien_b.md`](novaberg-agent-dateien_b.md) · Messungen: [`novaberg-agent-dateien_m.md`](novaberg-agent-dateien_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidungen stehen in den Abschnitten, die sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §4b.1, Überschrift *„entschieden am 18.08.2026: es gilt die rohe“*; Abschnitt D, §9 Punkt 8 | Alle Salienzschwellen des Rückwegs stehen auf der rohen Skala. Daraus folgt der Zuschnitt des Rückwegs in `_t` §4b.1a | 18.08.2026 |
| **E2** | Abschnitt D, §9 Punkt 9 | Eingearbeitet wird die rohe Textfassung, nicht die verdichtete — auch beim Recherche-Weg. Der Grund ist der Platz, nicht die Sparsamkeit | 18.08.2026 |
| **E3** | Abschnitt D, §9 Punkt 10; die Frage selbst in `_k` §1a.4 und `_m` *Aus §1a.4* | Dateiinhalt darf über ihre Antwort ins Gedächtnis übergehen; es gilt die Lesart *„sie hat es gelesen, also erinnert sie sich daran, es gelesen zu haben“*, und es wird kein Tor gebaut | 18.08.2026 |

Der Wortlaut der Entscheidungen steht in keinem der Abschnitte; sie geben sie als Ergebnis wieder.

**Im Text als entschieden oder beantwortet geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §4b.1a: *„Entschieden am 18.08.2026.“* — die drei Wege des Rückwegs; der erste, *das Einprägsame*, ist am 19.08.2026 entfallen, begründet mit einer Messung.
- `_t` §4b.1a-bis: *„Das Zugehörige verstärkt, es schneidet nicht — entschieden am 19.08.2026“*.
- `_t` §4, Zeile `entitaet_ids`: *„ohne Schreiber, entschieden am 23.08.2026“*, begründet in `_t` §6.1a (*„seither ist es eine Entscheidung, und sie hat eine Zahl“*).
- Abschnitt D, §9 Punkt 5: Kappung `K = 3` und Boden 0,30, *„Beantwortet und gebaut am 18.08.2026“*.
- Abschnitt D, §9 Punkt 2 (beantwortet durch §2.2) und Punkt 6 (beantwortet in v0.9 durch §3.0d).
- `_t` §1a.5: `gemischt` läuft in den Fremd-Block, der Vorgabewert ist `nutzer`; über den Gesprächsweg wird die Angabe gefragt (seit 22.08.2026).

---

## B. Offen beim Meister

§9 führt seine offenen Punkte ausdrücklich als *„Absichten und keine Umsetzungsdetails“*. Nicht durchgestrichen und damit offen sind sechs:

- **§9 Punkt 1** — Welche Wurzel zuerst? (siehe Befund B11)
- **§9 Punkt 2, Anschlussfall** — was mit den Indexzeilen geschieht, wenn die letzte Freigabe auf ein Verzeichnis zurückgenommen wird.
- **§9 Punkt 3** — wie tief `datei_grep` gehen darf.
- **§9 Punkt 4** — was bei einer Datei geschieht, die kein Text ist (siehe Befund B12).
- **§9 Punkt 7** — wo ein neuer Wissenstext entsteht und wo ein bestehender erweitert wird.
- **§9 Punkt 11** — was mit dem Gelernten geschieht, wenn die Quelldatei sich als falsch erweist: ob ein erneuter Durchlauf den Wissenstext berichtigt oder danebenlegt.

**Offen ohne Frage an den Meister** — was das Konzept selbst als offen, verschoben oder gemeldet führt:

- `_t` §3.0b, *Drei Dinge folgen daraus*: getrennte Zähler je Grund oder ein gemeinsamer mit Vorrang für die Reparatur — *„Die Entscheidung dazu gehört nicht in dieses Dokument“*; dazu die eigene Zulassungsprüfung der Vertiefung.
- Abschnitt D, §9 Punkt 5: die Quantilschwelle `1 − K/N`, Backlog `AUFZEICHNUNGEN-QUANTIL`.
- `_m`, *Bisheriger Kopf*: der Takt des Wächters (bis die Änderungsrate gemessen ist), `zuletzt_gelernt_hash` ohne Schreiber, kein Aufrufer für `tools/dateien/`.
- `_t` §6.1a: eine Entitäten-Erhebung aus dem Dateiinhalt, Backlog `DATEIINDEX-GRAPHKANAL`.
- `_t` §3.0c: das Web ist über den Empfang nicht als Dienst wählbar.
- `_t` §3.1: die Zustellart ist einwertig — *„Gehört in die Fundliste.“*
- `_b`, *Aus §1a.5*: der Außenrand prüft den Pfad, nicht das Paar — *„Steht in der Fundliste.“*; der Indexlauf der dritten Wurzel.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_t` §1a.2 — die Entwurfsfassung des Blocks mit drei `NICHT`-Sätzen, überholt am 18.08.2026 (`F-PROMPT-1`); die Fassung in zweiter Person, ersetzt am 30.08.2026.
- `_t` §1a.5 — der Blockname `[EIGENE AUFZEICHNUNGEN]`, weil er den ersten als Teilzeichenkette enthält.
- `_k` §2, §2.1 — eine gemeinsame Tabelle mit der Bibliothek und ein Gewicht oder Verfall auf dem Index.
- `_k` §2.2 — das Paar an der Datei statt an der Wurzel (Umkehrung in v0.2).
- `_k` §3.0 — ein eigenes Embedding je Turn.
- `_m` §3.0a — der Präzedenzwert 0,40 als *„gemessener Wert“*, widerlegt am 17.08.2026; `_t` §3.0a-bis — die Schwelle als Konstante.
- `_t` §3.0b — die Vertiefung als *„ein zweiter Aufrufer der Selbstauslösung“*; das Ergebnis der Vertiefung als Ganzes in die Antwort.
- `_t` §3.0d — *„kein Wissen zum Thema, also Lücke“* als alleiniges Kriterium.
- `_t` §3.0c — der durchgestrichene Satz über das eigene Wissen ohne Zettel, erledigt am 19.08.2026.
- `_t` §4a, §4a.1 — die Zuordnung über den nächstliegenden Vektor und die Schwelle, die das Konzept bis v0.9 messen wollte.
- `_t` §4b.1a — der Weg *das Einprägsame*, entfallen am 19.08.2026.
- `_t` §4b.1a-bis — der Schnitt für das Zugehörige; ein Zettel mit Bedingungsblock für beide Auftragsarten.
- `_t` §4b.3 — der Vergleich über den ganzen Absatz, der exakte Wortlaut (12 von 18 Doppelgängern), die Berechnung über `pg_trgm` in der Datenbank, die Schwelle allein ohne Modellaufruf in der mittleren Zone.
- `_t` §5.5a — *„diesmal nicht gesehen“* als *„gelöscht“*.
- `_t` §5.6 — `startswith("archive/")`, `"archive" in pfad`, die exakte englische Kleinschreibung.
- `_t` §6.1a — die Auflösung der Stichwörter gegen den Entitätenbestand; die zurückgenommene Begründung *„die Auflösung lege an“*.
- `_t` §6.3a — der Treffer gegen den ganzen `suchtext`.
- Abschnitt D, §9 Punkt 5 — der Boden 0,30 als alleinige Zusicherung, widerlegt am selben Tag; Abhilfe ist der zweite Kanal.

---

## D. §9 — Was zu entscheiden ist, bevor gebaut wird

Der Abschnitt des Konzepts, unverändert. Welche Datei die Abschnitte trägt, auf die er verweist, sagt die Tabelle *„§ → Datei“* in [`novaberg-agent-dateien_k.md`](novaberg-agent-dateien_k.md).

## 9. Was zu entscheiden ist, bevor gebaut wird

Die Fragen, die der Entwurf offenlässt, weil sie Absichten sind und keine Umsetzungsdetails. **Beantwortete bleiben durchgestrichen stehen** — sie erklären, warum der Code so aussieht, wie er aussieht:

1. **Welche Wurzel zuerst?** Die Projektdokumentation ist der genannte Zweck. Sie ist zugleich der Korpus, in dem Nova über sich selbst liest — was eine eigene Frage aufwirft (§10).
2. ~~**Sieht jedes Paar denselben Index?**~~ → **Beantwortet (§2.2):** Das Paar hängt an der Freigabe. Zwei Menschen, die dasselbe Verzeichnis freigeben, teilen sich die Indexzeilen und haben zwei Wurzeln. Offen bleibt der Anschlussfall: **Was geschieht mit den Indexzeilen, wenn die letzte Freigabe auf ein Verzeichnis zurückgenommen wird** — sie sind dann von niemandem mehr erreichbar und stehen weiter da.
3. **Wie tief darf `datei_grep` gehen?** Eine Obergrenze für Treffer und Dateien ist nötig; ohne sie ist eine unglückliche Anfrage ein Vollscan.
4. **Was passiert bei einer Datei, die kein Text ist?** PDF, Bild, Tabelle. Der Entwurf behandelt Text; alles andere wird erkannt und mit Grund übergangen, nicht stillschweigend.
5. ~~**Wie groß ist die Kappung des Enricher-Wegs, und wo liegt der absolute Boden?**~~ → **Beantwortet und gebaut am 18.08.2026.** `K = 3` — dieselbe Zahl wie die Bibliothek; die Fundstelle je Eintrag ist nicht kürzbar, aber sie kostet eine Zeile und keine Verdopplung, und der Auszug ist bei 300 Zeichen gekappt. **Der Boden ist gemessen, nicht gesetzt: 0,30**, aus acht Sonden gegen die drei Indexzeilen, beide Seiten erhoben:

   | Seite | bester Treffer je Sonde |
   |---|---|
   | einschlägig | 0,3800 · 0,4610 · 0,4961 |
   | fremd | 0,2014 · 0,2010 · 0,1896 · 0,1861 · 0,0729 |

   0,30 lag fast mittig in der Lücke — 0,10 über der höchsten fremden, 0,08 unter der niedrigsten einschlägigen Sonde.

   > **Am selben Tag widerlegt, und zwar planmäßig** (18.08.2026, Nachmittag). Sobald der Korpus **heterogen** war — 10 Sachdateien dazu, 13 Zeilen —, ergab dieselbe Messung: einschlägige Sonden ab **0,2899** (Töpferei), fremde bis **0,2515** (Gravitationslinsen). **Die Lücke schrumpfte von 0,18 auf 0,038**, und 0,30 schnitt einen echten Treffer ab. Der Vorbehalt, der an der Zahl stand, hat genau das vorhergesagt.
   >
   > **Die Abhilfe ist nicht die nächste Zahl, sondern der zweite Kanal** (§6.3a). Ein Boden in einer Lücke von 0,038 wäre ein Münzwurf mit Nachkommastellen. **Die Messbedingung reist mit der Zahl** und steht an ihr in `config.py`, weil genau das beim Präzedenzwert 0,40 verdunstet ist: Die Sonden liefen mit dem **rohen** Anfrage-Embedding, der Betrieb sucht mit dem verschobenen `such_vektor`, und der Bestand war **drei Zeilen aus einem Register**. Ein Startwert mit benannter Bedingung, kein Verteilungs-Ergebnis.

   **Offen bleibt die Quantilschwelle** `1 − K/N`. Sie ist nicht vergessen, sondern noch nicht rechenbar: Sie ist das Quantil der **mitlaufenden** Verteilung, und diese Verteilung beginnt erst mit diesem Bauteil zu entstehen. Der K-te Wert wird seit dem 18.08.2026 je Turn protokolliert (`schlechtester`); sobald er trägt, tritt das Quantil neben den Boden — Backlog `AUFZEICHNUNGEN-QUANTIL`.
6. ~~**Was misst die Trefferqualität, die der Block ausweisen soll?**~~ → **Beantwortet in v0.9 (§3.0d):** Es braucht keine Qualitätszahl. Das Kriterium ist die **Lücke**, nicht die Nähe — und sie wird an der Bibliothek geprüft, nicht am Kosinus. Der rohe Kosinus wäre ohnehin untauglich gewesen, weil niemand seine Skala kennt (0,588 klingt mittelmäßig und ist der Normalfall).
7. **Wo entsteht ein neuer Wissenstext, und wo wird ein bestehender erweitert?** Findet sie einen Fund, ist zu entscheiden, ob er in eine vorhandene Datei gehört oder eine neue rechtfertigt (§3a). Das ist dieselbe Bedarfsfrage eine Ebene höher und heute nirgends beantwortet — der Ablage-Weg legt je Durchlauf eine neue Datei an.
8. ~~**Welche Salienz-Lesart gilt für den Rückweg?**~~ → **Beantwortet am 18.08.2026 (§4b.1): die ROHE.** Gemessen an 2394 Einträgen des laufenden Bestandes nimmt eine Schwelle von 0,7 auf der *wirksamen* Skala 95 bis 100 % — sie trennt dort nichts, weil die Kurve oben staucht und `KZG_SALIENZ_MINIMUM` unten abschneidet. Auf der rohen nimmt dieselbe Zahl 59 % (`user`) und 82 % (`assistant`). **Damit steht zugleich der Zuschnitt des Rückwegs** (§4b.1a): eine Schwelle für das Einprägsame, die vorhandene Promotion für das Überlebende, und für das Zugehörige **keine Schwelle**, weil `autonomous_wissen` bei min 0,944 liegt und jede Bedingung „≥ 0,7" dort eine Tautologie wäre.

9. ~~**Welche Textfassung wird eingearbeitet — die verdichtete oder die rohe?**~~ → **Beantwortet am 18.08.2026: die ROHE.** Der Grund ist der Platz, nicht die Sparsamkeit — `pipeline_log` hält 365 Tage gegen 7 bis 30 des Kurzzeitgedächtnisses, und wo Platz ist, wird nicht verdichtet. Damit fällt der Einwand *„Preis je Aufruf"*, und §4b.3 gilt ungeschmälert: kein Destillat auf einem Destillat. **Dieselbe Wahl gilt für den Recherche-Weg** — auch dort geht die Rohfassung in die Datei. **Die eigene Sprache entsteht dabei nicht beim Ablegen, sondern beim Antworten:** Der Speicher hält den Rohtext, die Stimme kommt im Gesprächsgraphen dazu.

10. ~~**Geht Dateiinhalt über ihre Antwort ins Gedächtnis?**~~ → **Beantwortet am 18.08.2026: ja, er darf übergehen.** Gemessen am selben Tag: Ein Messturn erzeugte einen KZG-Eintrag mit drei Dateipfaden im Wortlaut, der Abruf holt ihn zurück, und die Herkunft steht im gespeicherten Text (§1a.4). Von den beiden vertretbaren Lesarten gilt die erste — *sie hat es gelesen, also erinnert sie sich daran, es gelesen zu haben*. **Es wird deshalb kein Tor gebaut**; die Unterscheidung trägt die Beschriftung, nicht eine Sperre.
11. **Was geschieht mit dem Gelernten, wenn die Quelldatei sich als falsch erweist?** Der Wächter meldet die Änderung und öffnet die Lücke wieder (§5.2a) — das deckt den Fall *„es steht jetzt etwas anderes da"*. Nicht gedeckt ist *„das Gelernte war falsch"*: Ihr Wissenstext ist dann bereits geschrieben, und ob ein erneuter Durchlauf ihn berichtigt oder danebenlegt, ist eine Absicht und keine Umsetzungsfrage.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B7 stammen aus der Sichtung, B8 bis B14 sind beim Aufteilen am selben Tag gelesen. Die Zeilenangaben der Sichtung beziehen sich auf das ungeteilte Konzept; hier stehen die neuen Orte.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_m`, *Bisheriger Kopf*, Feld **Stand** | Der Kopf nennt v0.20 (25.08.2026); die Versionshistorie in `_b` endet bei v0.17 | `[gelesen 19.09.2026]` |
| **B2** | `_m`, *Bisheriger Kopf*, Feld **Status** und Zustandsteil (Zeilen `dateien` *„halb — der Empfang fehlt“*, `suche.py` und `zoom.py` *„kein Aufrufer“*, *„Aushang, Klassifikation, Dispatch — fehlt“*) | `_b`, Versionshistorie v0.16: *„Der lesende Dienst hat seinen Aufrufer“*; ebenso `_m` §8.1a, *Der Gegenbeweis* | `[gelesen 19.09.2026]` |
| **B3** | Abschnitt D, §9 Punkt 8 | nennt als Zuschnitt noch *„eine Schwelle für das Einprägsame“*; `_t` §4b.1a führt diesen Weg als entfallen am 19.08.2026 | `[gelesen 19.09.2026]` |
| **B4** | `_t` §4b.1b, Kasten *Beim Bauen fiel auf* | Im selben Absatz: *„nicht um das Zwölffache, sondern unbegrenzt“* und unmittelbar danach *„um mehr als das Zwölffache“* | `[gelesen 19.09.2026]` |
| **B5** | `_b`, Versionshistorie v0.11 | *„Die erste Wurzel ist nicht die Projektdokumentation“*, §10 *„auf einen späteren Zeitpunkt verschoben“*; `_b`, *Aus §7*: `/docs` ist seit dem 20.08.2026 freigegeben | `[gelesen 19.09.2026]` |
| **B6** | `_b` §3a.1 | Die Tabelle führt `struktur_analysieren`, `block_lesen`, `datei_grep`, die chirurgischen Schnitte und `str_replace_in_block` als *„entworfen“*; der Zustandsteil in `_m` führt `operationen.py` und `redaktion.py` als gebaut, `_t` §4b.3 sagt *„Genau dafür sind die Werkzeuge gebaut“* | `[gelesen 19.09.2026]` |
| **B7** | `_k` §1a.3, `_t` §1a.5, `_k` §1a.4 | Die Abschnittsfolge im ungeteilten Konzept war 1a.3, 1a.5, 1a.4 | `[gelesen 19.09.2026]` |
| **B8** | `_b`, *Aus §7*, Kasten, Absatz *Was mit `/docs` neu ist* (20.08.2026) | *„Ein archiviertes Konzept sieht im Index aus wie ein geltendes … ein Etikett am Indexeintrag gibt es nicht“*; `_t` §5.6: seit dem 23.08.2026 trägt die Fundstelle ein Etikett, in allen drei Ausgabewegen | `[gelesen 19.09.2026]` |
| **B9** | `_t` §5.5a | *„Der Satz oben stand hier zwei Monate“*; die Erstfassung des Konzepts ist vom 17.08.2026 (`_b`, Versionshistorie v0.1), der Nachtrag vom 23.08.2026 | `[gelesen 19.09.2026]` |
| **B10** | `_t` §5.2a | *„Damit trägt die Indexzeile eine Angabe mehr, als §4 vorsieht“*; die Tabelle in `_t` §4 führt `zuletzt_gelernt_hash` bereits | `[gelesen 19.09.2026]` |
| **B11** | Abschnitt D, §9 Punkt 1 | steht offen und nicht durchgestrichen; `_b`, Versionshistorie v0.11: *„§9 Punkt 1 ist beantwortet“* | `[gelesen 19.09.2026]` |
| **B12** | Abschnitt D, §9 Punkt 4 | steht offen und nicht durchgestrichen; `_t` §5.1, Kasten vom 20.08.2026: *„das ist die Regel aus §9 Punkt 4 und sie bleibt“* | `[gelesen 19.09.2026]` |
| **B13** | `_t` §5.5b | *„weil keine der drei Spalten bis heute einen Schreiber hat (§6.1)“*; die Schreiber-Frage steht in `_t` §6.1a | `[gelesen 19.09.2026]` |
| **B14** | `_k` §2, `_m` §3.0a, `_t` §5.6 | Bestand von `autonomous_wissen`: *„463 Zeilen“* (§2), *„217 aktiven Einträge“* (§3.0a, 17.08.2026), *„820 Zeilen“* (§5.6, 23.08.2026) — §2 nennt keinen Zeitpunkt | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Keine. Das ungeteilte Konzept trug keine Schlusszeile; die *Befunde aus dem Betrieb — nachgetragen am 20.08.2026* stehen in [`novaberg-agent-dateien_m.md`](novaberg-agent-dateien_m.md).
