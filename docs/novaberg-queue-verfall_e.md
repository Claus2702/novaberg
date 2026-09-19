# Novaberg — Der Verfall der Shadow-Queue (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-queue-verfall_k.md`](novaberg-queue-verfall_k.md) · Ausarbeitung: [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md) · Bauplan und Umstellung: [`novaberg-queue-verfall_b.md`](novaberg-queue-verfall_b.md) · Messungen: [`novaberg-queue-verfall_m.md`](novaberg-queue-verfall_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidungen stehen in den Abschnitten, die sie tragen, und bleiben dort. Hier steht der Verweis. Alle zehn fielen am 15.08.2026, beim Durchrechnen des Lebenszyklus gegen den gemessenen Bestand; die Tabelle *„Was aus der Prüfung des Lebenszyklus **nicht** offen blieb“* in Abschnitt D fasst vier davon zusammen.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §12.1; Abschnitt F, v0.1 (*„Entschieden: **Soft-Delete statt hartem Löschen**“*) | Ein nicht erledigter Auftrag wird deaktiviert, nicht gelöscht | 15.08.2026 |
| **E2** | `_t` §6; Abschnitt F, v0.1 | Die Reaktivierung setzt auf 50 % des Bandes über der Schwelle (Halbreaktivierung nach dem Vorbild der Knoten) | 15.08.2026 |
| **E3** | `_t` §9 (Kasten *„30 Tage TTL“*); Abschnitt F, v0.1 | Frist 30 Tage — keine Löschfrist, sondern die Zeit bis zur Schwelle | 15.08.2026 |
| **E4** | `_t` §7.2; `_k` §14, erster Punkt | Die Queue zieht nach PostgreSQL um, der Stapel bleibt in Redis | 15.08.2026 |
| **E5** | `_t` §12.1 | Entnehmen nach der Ausführung ist das einzige Löschen; alles andere wird gelagert | 15.08.2026 |
| **E6** | `_t` §12.3: *„Entschieden am 15.08.2026: Jeder Punkt kommt nach Dringlichkeit dran.“* | Rangfolge nach Dringlichkeit, damit LIFO statt FIFO | 15.08.2026 |
| **E7** | `_t` §12.5: *„Entschieden am 15.08.2026: keine Mengengrenze, keine zweite Frist.“* | Wächst der Bestand, wird `QUEUE_DECAY_RATE` verstärkt | 15.08.2026 |
| **E8** | `_t` §12.5, letzter Absatz | Ein Jahresablauf für nie reaktivierte Aufträge ist erwogen und nicht eingeführt, mit benannter Bedingung | 15.08.2026 |
| **E9** | `_t` §12.2; Abschnitt D, Tabelle | Die Sättigung der Verstärkung ist gewollt, die Wirkung sitzt in `verstaerkt_am` | 15.08.2026 |
| **E10** | `_t` §12.4; Abschnitt D, Tabelle | Die Reaktivierung hält am Leben und drängelt nicht vor | 15.08.2026 |

Der Wortlaut der Entscheidungen steht in keinem der Abschnitte; E6 und E7 geben den Beschluss als Satz wieder, die übrigen als Ergebnis.

**Im Text als entschieden oder gesetzt geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §9: `QUEUE_SCHWELLE` **0,3**, Herleitung *„entschieden“* (Abschnitt F, v0.1, nennt die Schwelle unter *Entschieden* mit).
- `_k` §14, dritter Punkt: der Fehlversuchspfad legt seit dem 23.08.2026 still statt hart zu verwerfen — *„Sie hat die Entscheidung getragen, und die Entscheidung steht“*.
- `_t` §6.1: *„Was ‚derselbe Gegenstand‘ heißt, ist eine Setzung“* — gleiches `aufgabe` und gleiches `thema` bei demselben Paar.
- `_b` §16, *Was der Bau am Konzept berichtigt hat*: Die Migration übernimmt 1:1, ohne Verdichtung (beim Bau).

---

## B. Offen beim Meister

| | Stelle | Frage |
|---|---|---|
| **O1** | Abschnitt D (§15) | Die 383 verwaisten `vertiefen`-Aufträge: den Agenten bauen oder `information_teilen` nicht mehr einreihen — *„Zwei Wege, und die Wahl ist eine Absicht, keine Implementierungsfrage“* |
| **O2** | `_k` §14, dritter Punkt, *Was bleibt* | *„Die **Auswahl** zieht weiter den Salienzstärksten zuerst, und der scheitert deshalb zuerst. Das ist eine eigene Absicht und nicht der Rest dieses Zuges.“* |

**Offen ohne Frage an den Meister** — Beobachtungen und Messungen, die das Konzept selbst als offen führt:

- `_m`, *Bisheriger Kopf* und §16 *Was ungemessen bleibt*: die Messung über 30 Tage Betrieb; die Reaktivierung im Betrieb.
- `_m` §12.6: Die Abflussrate ist aus der Altersverteilung erschlossen, nicht aus dem `hintergrund_log` gezählt.
- Abschnitt D (§15, Schluss) und `_t` §12.3: die Verschiebung zugunsten der Wartungsaufgaben — *„zu **beobachten**, nicht vorab zu regeln“*.
- `_t` §6.1: eine Ähnlichkeitsprüfung über Embeddings als zweiter Schritt, mit einer Schwelle, die es noch nicht gibt.
- `_t` §6.2: eine Prüfung auf nicht leeres `thema` im Schreibpfad.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k` §1 — *„Max 20 Eintraege pro User“* aus dem Moduldokument; geprüft am 15.08.2026, es gibt keinen Begrenzer: *„Die Zahl war eine Absicht, die als Zustand geschrieben stand“*.
- `_t` §3.1 — die Umbenennung von `prioritaet` als eigener Zug; verschoben in den Umzug (auch `_k` §14).
- `_t` §6 — *„×0,5“* statt der Halbreaktivierungsformel; ein halbierter Anker läge bei einem schwachen Auftrag unter der Schwelle.
- `_t` §7.1 und §7.2 — Soft-Delete in der Redis-Liste; und der Umzug des Stapels, verworfen wegen der Lesefrequenz.
- `_t` §9 — die Schwelle auf dem Rohwert; und die Skala 10,0 des Schwesterdokuments, auf der die Schwelle 3 % wäre.
- `_t` §12.2 — der Boost als Stellschraube der Frist.
- `_t` §12.5 — Mengengrenze und Jahresablauf (E7, E8).
- `_k` §14 — Verhungerungsschutz für Queue-Aufträge, Ähnlichkeitsprüfung bei der Dublettenerkennung, und das harte Verwerfen nach drei Fehlversuchen (durchgestrichen, geändert am 23.08.2026).
- `_b` §16, *Was der Bau am Konzept berichtigt hat* — die Verdichtung gleicher Gegenstände bei der Migration.
- Abschnitt D (§15) — der Weg, die Intention stillzulegen, als *„der billigere und der schlechtere“*; beides zu lassen und den Verfall arbeiten zu lassen, als *„Was nicht geht“*.

---

## D. Offene Frage des Konzepts

§15 des ungeteilten Konzepts, ungekürzt.

## 15. Was offen bleibt

**Die 383 verwaisten `vertiefen`-Aufträge — der Verfall ist ein Ventil, kein Fix.**

Er räumt sie nach 30 Tagen ab. Sie entstehen aber weiter, solange kein `vertiefen`-Agent existiert: `_INTENTION_AUFGABE_MAP` bildet `information_teilen` auf `vertiefen` ab, in beiden Kopien. **Der Verfall macht das Problem unsichtbar, ohne es zu lösen** — und er macht es dabei schwerer auffindbar, weil der Rückstand nicht mehr wächst.

Zwei Wege, und die Wahl ist eine Absicht, keine Implementierungsfrage:

1. **Den Agenten bauen.** Dann sind die Aufträge richtig und werden abgearbeitet. **Das Konzept dafür existiert** — `novaberg-pixie-deepdive_k.md`, geführt als *„VertiefungsAgent (Konzept, nicht implementiert)"*. Es fehlt der Bau, nicht der Entwurf.
2. **Die Intention nicht mehr einreihen** — `information_teilen` auf `""`, wie es am 05.08.2026 mit `emotionaler_ausdruck` geschah. Dann entstehen sie gar nicht erst.

**Der zweite Weg ist der billigere und der schlechtere.** `information_teilen` ist die häufigste Intention des Bestands; sie stillzulegen hieße, den Anlass wegzuwerfen statt ihn zu bedienen. Der erste Weg ist teurer und löst dabei auch die stille Null und das leere Thema — **denn beide entstehen auf demselben Pfad** (§2.1), und ein Pfad, an dessen Ende ein Agent steht, wird beim Bauen einmal ganz durchgesehen.

**Was nicht geht, ist beides zu lassen und den Verfall dafür arbeiten zu lassen.** Ein Auftrag, der entsteht, um zu verfallen, ist ein Rechenweg ohne Adressaten — er kostet bei jeder Auswahl einen Vergleich und bei jedem Verfallslauf eine Zeile.

Bis zur Entscheidung ist das Verhalten benannt und nicht stillschweigend: **Der Verfall räumt sie ab, und sie kommen wieder.**

### Was aus der Prüfung des Lebenszyklus **nicht** offen blieb

Vier Fragen sahen nach offenen Punkten aus und sind am 15.08.2026 entschieden; sie stehen hier, damit niemand sie als Lücke wieder aufnimmt:

| Frage | Entscheidung |
|---|---|
| Reihenfolge der Abarbeitung | **Dringlichkeit**, und damit LIFO — der frische Gedanke ist der präsente (§12.3) |
| Wirkungslose Verstärkung? | **Nein, gewollt** — die Sättigung ist der Zweck der Kurve, die Wirkung sitzt in der Uhr (§12.2) |
| Reaktivierung ohne Rangwirkung? | **Richtig so** — sie hält am Leben, sie drängelt nicht vor (§12.4) |
| Mengengrenze oder zweite Frist | **Keine von beiden** — wächst der Bestand über das Erträgliche, wird der Verfall verstärkt (§12.5) |

**Die einzige verbliebene Spannung ist benannt und nicht entschieden, weil sie keinen Entschluss braucht:** Im Heartbeat laufen zwei gegenläufige Zeitregeln — das Aging der periodischen Aufgaben hebt mit der Wartezeit, der Verfall der Queue senkt mit ihr (§12.3). Beide sind für ihren Gegenstand richtig. Die Folge ist eine langsame Verschiebung zugunsten der Wartungsaufgaben, und die ist zu **beobachten**, nicht vorab zu regeln.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung, B5 bis B7 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_t` §12.1, Tabelle *Drei Wege aus der Queue* | Die Tabelle ist durch eine Leerzeile nach der ersten Datenzeile zerrissen; die Zeilen *Verfallen* und *Gescheitert* stehen außerhalb der Tabelle | `[gelesen 19.09.2026]` |
| **B2** | `_m`, *Bisheriger Kopf*, Feld **Stand**, gegen Abschnitt F (Versionshistorie) | Der Kopf nennt v0.6 für den 23.08.2026, die Historie führt v0.6 am 15.08.2026 (`arousal`); Einträge für den 23.08.2026 (Fehlversuchspfad) und den 28.08.2026 (`ausloeser_turn_id`) fehlen | `[gelesen 19.09.2026]` |
| **B3** | `_t` §6.1 | *„`shadow_queue_push` prüft **nicht**, ob derselbe Auftrag bereits liegt“* steht ohne Marke; nach `novaberg-pixie-graph-merge_k.md` ist das seit dem 15.08.2026 erledigt | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt D (§15) | Die Absichtsfrage (`vertiefen`-Agent bauen oder die Intention stilllegen) stand bisher nur im Rumpf; sie ist jetzt O1 in Abschnitt B | `[gelesen 19.09.2026]` |
| **B5** | `_t` §12.5, erster Satz | *„Es wird nichts gelöscht außer dem Erledigten und dem Gescheiterten“*; seit dem 23.08.2026 wird das Gescheiterte stillgelegt, nicht gelöscht (`_t` §12.1, Zeile *Gescheitert*; `_k` §14) — der Satz trägt keine Marke | `[gelesen 19.09.2026]` |
| **B6** | `_b` §10, Kasten *„Der Defekt ist vor dem Umzug zu beheben“* | Die stille Null (`KANDIDATEN-PRIORITAET-STILLE-NULL`) steht als offen; `_b` §16, *Die Reihenfolge, in der gebaut wurde*, sagt, `memory/kzg.py` übergibt seither die Salienz und der Vorgabewert `0.0` ist verschwunden — §10 trägt keine Marke | `[gelesen 19.09.2026]` |
| **B7** | `_t` §7.1, §7.3, §12.1 (Absatz *Der Weg „erledigt“*), §12.3 (Block *heute / kuenftig*) | Die Redis-Liste wird im Präsens als *„heute“* beschrieben und die Tabelle als *„künftig“*; der Umzug ist seit dem 15.08.2026 gebaut (`_b` §16) | `[gelesen 19.09.2026]` |

---

## F. Versionshistorie

Die Versionshistorie des ungeteilten Konzepts, ungekürzt.

## Versionshistorie

- **v0.6 — 15.08.2026:** Die Spaltentabelle in §8 trägt **`arousal`** — die dritte Größe derselben Lage, die `emotion` und `modus` beschreiben. Sie fehlte seit dem Umzug, und die Folge war keine Fehlfunktion, sondern eine **Leere**: Die Recherche konnte keinen Level auf den Stapel legen, weil sie keinen bekam, und Bauteil B der Eigenzeit war gebaut und ohne Eingabe. **NULL-fähig und ohne Vorgabewert**, anders als ihre beiden Nachbarn — die Quelle liefert sie stellenweise selbst leer, und eine 0,5 wäre ein Messwert, den nie jemand gemessen hat. 1050 Bestandszeilen bleiben NULL. DDL angekündigt, Beleg im Log: 133 Statements statt 132.

- **v0.5 — 15.08.26:** §16 um den **Audit der Nähte** erweitert. Fünf Schnittstellen einzeln durchgegangen, **drei gebrochen** — und keine hatte die Suite bemerkt, weil alle drei hinter den geprüften Stellen lagen. Der **Router** kannte `quelle = "shadow_auftrag"` nicht und verzweigte weiter auf `"queue"`: Der Heartbeat wählte im Dreißig-Sekunden-Takt einen Auftrag, fand keinen Agenten und ließ ihn liegen — **kein einziger Shadow-Auftrag lief mehr**, und die Warnung sah aus wie der bekannte Fall des fehlenden Agenten. **`_salienz_aus_auftrag`** las `salienz`/`prioritaet`, die ein migrierter Auftrag nicht trägt; jeder der 608 Recherche-Aufträge wäre mit `ValueError` gescheitert und nach drei Versuchen verworfen worden. Dazu eine Logzeile auf `erstellt` statt `erstellt_am`. **Die Lesson:** Wer einen Wert einführt, muss seine **Leser** suchen, nicht nur seine Schreiber — die Zeugen prüften Erzeuger, Auswahl und Abschluss, und zwischen Auswahl und Abschluss stand der Router. Der neue Zeuge liest die möglichen Werte aus dem Quelltext des Erzeugers statt sie aufzuzählen. Nebenbei bezeugt: `vertiefen` löst auf einen nicht registrierten Agenten auf (`PIXIE-ROUTING-DOPPELREGISTRY`) — der Grund für die 383 liegenden Aufträge.
- **v0.4 — 15.08.26:** **Gebaut und gemessen**, §16 neu. Die Migration übernahm **1036 von 1036** Aufträgen; danach 803 aktiv, 233 ruhend — und die 233 sind ausnahmslos `vertiefen`, die Vorhersage aus §13 traf exakt. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unverändert — **nichts gelöscht**, und 0 Deaktivierungen sind hier das richtige Ergebnis. Drei Dinge hat der Bau am Konzept berichtigt: Die Migration übernimmt **1:1 ohne Verdichtung**, weil eine Verdichtung `haeufigkeit` eine nie gemessene Zahl gäbe; ein **zirkulärer Import** zwischen `shadow_agent.utils` und `memory.kzg` war lokal zu brechen; und der Dispatcher las mit `themen` und `salienz` **zwei Feldnamen, die es nie gab** — der AgentState bekam dauerhaft `""` und `0.0`. Fünf Bestandszeugen sind nachgezogen, vier davon unverändert gültig; der fünfte trug den Satz „Queue-Einträge altern nicht", den dieser Bau aufhebt. Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.
- **v0.3 — 15.08.26:** **§12 auf die Entscheidungen umgeschrieben — was in v0.2 wie vier Mängel aussah, ist die Bauart.** §12.1 neu: **drei Wege aus der Queue, und nur einer ist ein Löschen** — was abgearbeitet wurde, wird entnommen (heute schon: `abschluss(erfolg=True)` → `LREM`), was scheitert, wird nach drei Versuchen verworfen, was nur wartet, wird deaktiviert und bleibt. Dazu der Vergleich, der die Bauart begründet: **Der KZG löscht hart** über Redis-TTL (7 / 14 / 30 Tage nach Salienz), **das LZG nie** — die Queue nimmt vom KZG die Frist und vom LZG den Rückweg. Ein Detail des KZG stützt §12.2: Eine Verstärkung verlängert dort die **TTL**, sie hebt nicht den Wert; auch im Kurzzeitgedächtnis wirkt Wiederholung über die Uhr. **Die Sättigung ist der Zweck der Sinus-Kurve, nicht ihr Versagen** — wer oben ist, gewinnt durch eine weitere Verstärkung fast nichts, und ein Dauerthema hebelt den Verfall damit nicht aus; der Boost ist dafür ausdrücklich **keine Stellschraube der Frist**. **Die Rangfolge ist Dringlichkeit, und Dringlichkeit ist Frische:** Der letzte Gedanke ist der präsenteste, nicht der von vor dreißig Tagen — die Umkehr von FIFO auf LIFO ist damit die Absicht und nicht eine Nebenwirkung. Benannt bleibt die Wechselwirkung mit dem Aging der periodischen Aufgaben: zwei gegenläufige Zeitregeln im selben Scheduler, beide für ihren Gegenstand richtig, mit einer langsamen Verschiebung zugunsten der Wartungsaufgaben. **Die Reaktivierung hält am Leben und drängelt nicht vor** — wiederholt sich der Anlass mehrfach, holt die zurückgesetzte Uhr den Auftrag von selbst nach oben. **Keine Mengengrenze und kein Jahresablauf:** Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt — eine Obergrenze würde nach Zahl statt nach Dringlichkeit verwerfen. Als Gewinn des Umzugs neu benannt: `LREM` adressiert den Eintrag über seinen exakten JSON-Wortlaut und ist bei jeder Abweichung **wirkungslos und stumm**; ein Primärschlüssel kann das nicht.
- **v0.2 — 15.08.26:** **§12 neu — der Lebenszyklus ist gegen den Bestand durchgerechnet**, und vier Stellen trugen nicht, wie sie in v0.1 standen. **Die Verstärkung wirkt nicht über die Höhe:** Zehn Verstärkungen heben `salienz_absolut` um 0,024 und kaufen 0,61 Tage, weil ein Auftrag bei `salienz_roh ≈ 0,80` von Cap 1,0 einsteigt und die Sinus-Kurve dort waagerecht ist — die Sättigung ist erreicht, bevor der erste Auftrag entsteht. Die Wirkung sitzt in `verstaerkt_am`, das 30 Tage neu schenkt; der Boost bleibt im Schema, aber **niemand darf von ihm eine Rangwirkung erwarten**. **Die Rangfolge kehrt sich um:** Heute gewinnt der älteste Eintrag des Höchstwerts (das Maximum 1,0 tragen 59 Einträge, der erste steht an Listenposition 894 von 1036) — nach dem Umzug gewinnt über `ORDER BY salienz_decay DESC` der jüngste überhaupt, weil der Verfall `salienz_decay` zur Umkehrfunktion des Alters macht. Aus FIFO wird LIFO, ohne dass eine Zeile es ankündigt, und für die periodischen Aufgaben ist dieselbe Frage ausdrücklich anders entschieden. **Die Reaktivierung stellt die Existenz wieder her, nicht die Chance:** 0,638 gegen 0,976 der Neuzugänge. **Der Lebenszyklus hat kein Ende** — es wird nichts mehr gelöscht, die Tabelle wächst monoton. **Was die Prüfung stützt:** Die Altersverteilung dünnt zu den alten Tagen hin nicht aus (57 Aufträge vom ältesten Tag liegen unberührt), der Abfluss ist also so klein, dass die Reihenfolge heute kaum zählt — die Umkehrung wird erst wichtig, wenn der Engpass am einen seriellen Platz fällt, und dann ist sie eingebaut und unbenannt.
- **v0.1 — 15.08.26:** Erstfassung. Entstanden aus dem Backlog-Eintrag `QUEUE-VERFALL-KONZEPT`, der ein eigenes Dokument verlangte — **die Suche nach dem Gegenstand fand `novaberg-autonomous-wissen_k.md` §11.6/§11.7**, wo dieselbe Bauart für Stapel und Bibliothek bereits steht. Dieses Dokument ist deshalb die Übertragung auf einen dritten Speicher und verweist, wo das Schwesterdokument trägt. Entschieden: **Soft-Delete statt hartem Löschen**, Reaktivierung auf 50 % des Bandes über der Schwelle nach `novaberg-memory-synapsen_k.md` §9.3, Frist **30 Tage**, Schwelle **0,3**. Daraus die Rate **λ = 0,0393/Tag**, gerechnet aus dem gemessenen Median 0,9764 — 26-mal die LZG-Rate. **Die Skala ist 1,0 und nicht die 10,0 des Schwesterdokuments**, weil die Queue Salienz führt; auf Cap 10 wäre die Schwelle 3 % und der Verfall liefe still ins Leere. **Die Queue zieht nach PostgreSQL um, der Stapel nicht** — gemessen: Die Queue wird alle 30 bis 120 s gelesen, der Stapel alle 5 s je Client, und die Postgres-Zugriffe dieses Projekts öffnen je Aufruf eine eigene Verbindung. Das Schema bildet jedes heutige JSON-Feld auf eine Spalte ab, einschließlich des bis dahin undokumentierten `_retries`; neu sind das Paar-Tripel und die Verfallsfelder. Die 233 Aufträge auf Salienz 0,0 fallen beim ersten Lauf heraus — vorher aufgeschrieben, damit es niemand für einen Unfall hält, und dank Soft-Delete rückholbar. Offen und als Absichtsfrage benannt: die 383 verwaisten `vertiefen`-Aufträge, für die der Verfall ein Ventil ist und kein Fix.
