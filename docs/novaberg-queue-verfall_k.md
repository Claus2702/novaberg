# Novaberg — Der Verfall der Shadow-Queue

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Warum ein Auftrag verfällt, wie er verfällt, und wohin die Queue dafür umzieht
**Stand:** 15. August 2026, Chat 141 — v0.5, gebaut, gemessen und die Nähte auditiert (§16)
**Pfad:** novaberg/docs/novaberg-queue-verfall_k.md
**Typ:** Konzept
**Status:** ✅ **Gebaut und gemessen am 15.08.2026.** Tabelle, Repository, Migration (1036 Aufträge), Schreib- und Auswahlpfad, Verfallslauf. §16 trägt die Messwerte. Offen: die Messung über 30 Tage Betrieb
**Verwandt:** `novaberg-autonomous-wissen_k.md` §11.6/§11.7 (**das Schwesterdokument — dort steht der Stapel, hier die Queue**) · `novaberg-memory-synapsen_k.md` §9 (das Vorbild) · `novaberg-kzg-salienz_k.md` §3 (die Aufbaukurve) · `novaberg-pixie.md` (das Modul)

---

## 1. Warum dieses Dokument — und warum es kein zweites ist

**Die Shadow-Queue wächst und schrumpft nie.** Am 15.08.2026 liegen 1036 Aufträge darin, der älteste 18 Tage alt. Es gibt keinen Weg hinaus außer der Ausführung und dem Verwerfen nach drei Fehlversuchen. Ein Auftrag, den niemand je ausführt, bleibt für immer.

> **Es gibt auch keine Obergrenze — entgegen dem, was das Moduldokument sagte.** `novaberg-pixie.md` §3 führte *„Max 20 Eintraege pro User"* als Eigenschaft der Shadow-Queue. Geprüft am 15.08.2026: Im Schreibpfad (`shadow_queue_push`) steht kein `LTRIM`, keine Längenprüfung, keine Konstante dieser Art; im ganzen Modul gibt es keinen Begrenzer. Der Bestand von 1036 ist der Beleg. **Die Zahl war eine Absicht, die als Zustand geschrieben stand** — und solange jemand sie glaubte, gab es keinen Anlass, nach einem Verfall zu fragen.

> **Ein Auftrag ist ein Vorsatz, kein Sachverhalt.** Ein Sachverhalt bleibt wahr, wenn man ihn liegen lässt. Ein Vorsatz verliert seinen Anlass — die Lage, aus der er entstand, ist nach zwei Wochen eine andere. Was der Verfall entfernt, ist deshalb nicht Speicherplatz, sondern **die Behauptung, dieser Vorsatz gelte noch**.

### Was es zu diesem Gegenstand schon gibt

**`novaberg-autonomous-wissen_k.md` §11.6 beschreibt dieselbe Bauart für zwei andere Speicher** — den Stapel und die Bibliothek. Dort steht die dreistufige Kurve, das Soft-Delete über `aktiv`, die Spaltenliste und die Entscheidung, wer den Verfall rechnet (§11.7).

**Dieses Dokument ist deshalb keine Neuerfindung, sondern die Übertragung auf einen dritten Speicher.** Wo §11.6 trägt, wird verwiesen statt wiederholt. Was hier neu ist, ist dreierlei: die Queue kam in §11.6 nicht vor, sie liegt auf einer anderen Skala, und sie muss dafür umziehen.

**Die Abgrenzung, damit die beiden nicht auseinanderlaufen:**

| Speicher | Dokument | Inhalt | Verfall |
|---|---|---|---|
| `shadow_queue` | **hier** | Aufträge — was getan werden soll | eigene Rate, 30 Tage |
| `shadow_stack` | `autonomous-wissen_k.md` §11.6 | ungesagte Gedanken | eigene Rate, 60 Tage |
| `autonomous_wissen` | `autonomous-wissen_k.md` §11.6 | erarbeitetes Wissen | die des LZG |
| `lzg_knoten` | `memory-synapsen_k.md` §9 | Erinnerung | 0,0015/Tag |

**Drei Speicher, eine Bauart, drei Raten.** Die Bauart wird geteilt, weil sie sich bewährt hat. Die Raten nicht, weil ein unerledigter Auftrag schneller gegenstandslos wird als ein Gedanke, und ein Gedanke schneller als eine Erinnerung.

---

## 2. Der Befund am Bestand

**Gemessen am 15.08.2026 um 13:52 UTC** über `shadow_queue:meister`. **Zählvorschrift:** alle Einträge aus `LRANGE 0 -1`, je Eintrag der JSON-Satz; Werkzeug `labor/werkzeug/queue_bestand_messung.py`.

```
Bestand            1036 Aufträge
Aufgabenarten      recherche 608 · vertiefen 383 · nachfragen 45
prioritaet         233 auf exakt 0,0        — davon vertiefen 233
                    18 im Band 0,67378–0,94393
                   785 im Band 0,94393–1,0
                   Median 0,9764 · Minimum 0,0 · Maximum 1,0
thema leer         145                      — vertiefen 141, nachfragen 4
Alter              0 bis 18 Tage, Median 9 — keiner über 30
_retries           43 Aufträge tragen das Feld
Gegenstände        878 verschiedene (aufgabe, thema)-Paare
```

> **Der Bestand wächst, während man ihn misst.** Eine Zählung wenige Stunden zuvor am selben Tag ergab 1032, die hier zitierte 1036. Das ist keine Messungenauigkeit, sondern der Gegenstand des Dokuments: **Es gibt einen Zufluss und keinen Abfluss außer der Ausführung.** Wer eine Zahl von hier zitiert, zitiert einen Zeitpunkt.

Drei Dinge stehen darin, die das Konzept tragen müssen.

**Erstens: Die Verteilung ist zweigipflig, nicht breit.** 785 von 1036 liegen im obersten Band, 233 auf null, dazwischen 18. Es gibt kaum mittlere Werte. **Eine Schwelle trennt hier nicht die schwachen von den starken Aufträgen — sie trennt die belegten von den unbelegten.** Wer erwartet, dass eine Schwelle von 0,3 beim ersten Lauf ein Drittel abräumt, misst die 233 Nullen und hält sie für Rauschen im Sinne von „schwach". Sie sind etwas anderes: Aufträge, deren Salienz nie geschrieben wurde.

**Zweitens: Der Bestand ist jünger als die Frist.** Kein Auftrag ist älter als 18 Tage, die Frist soll 30 sein. **Der erste Verfallslauf wird deshalb außer den 233 Nullen nichts finden** — und das ist kein Fehlschlag, sondern die richtige Vorhersage. Wer sie nicht vorher aufschreibt, hält den Lauf hinterher für wirkungslos.

**Drittens: 383 Aufträge warten auf einen Agenten, den es nicht gibt.** Im Verzeichnis `server/agents/` liegt kein `vertiefen`. Das sind 37 % des Bestands.

### 2.1 Die beiden Befunde sind einer

**Die stillen Nullen und die verwaisten Aufträge sind dieselbe Menge.** Aufgeschlüsselt am 15.08.2026:

```
prioritaet 0,0    233  —  davon vertiefen 233, recherche 0, nachfragen 0
thema leer        145  —  davon vertiefen 141, nachfragen 4
```

**Alle Nullen sind `vertiefen`-Aufträge, ausnahmslos.** Das war aus der Gesamtzahl nicht zu sehen und ändert die Deutung: Die stille Null ist kein Streufehler über alle Aufgabenarten, sondern eine Eigenschaft **eines** Pfades — desselben, der auf einen fehlenden Agenten zeigt und dessen Aufträge in 141 Fällen auch noch ohne Thema ankommen.

> **Drei Befunde, ein Pfad:** `information_teilen` → `vertiefen` erzeugt Aufträge ohne Salienz, oft ohne Thema, für einen Agenten, den es nicht gibt. Wer einen davon einzeln behebt, hat den Pfad nicht behoben. **Der Verfall räumt alle drei zusammen ab — und keiner davon ist damit behoben** (§15).

---

## 3. Was der Wert bedeuten soll

### 3.1 Der Name ist falsch, die Größe ist richtig

Das Feld heißt `prioritaet`. Es trägt aber keine Priorität im Sinne einer Rangvorgabe, sondern die **Salienz des auslösenden Turns** — `agents/kzg/queues.py` setzt es aus `neue_salienz`. Der Kommentar an der Auswahlstelle sagt es ausdrücklich: *„Queue-Eintraege altern nicht: basis == effektiv."*

**Der Name bleibt vorerst, die Bedeutung wird benannt.** Eine Umbenennung im Zug dieses Konzepts wäre eine zweite Änderung an denselben Stellen; sie gehört in den Umzug (§7), wo die Spalten ohnehin neu entstehen.

### 3.2 Die dritte Rolle — und warum sie keine dritte ist

Der Wert trägt heute zwei Rollen: **Auslöse-Salienz** (woher er kommt) und **Scheduler-Rang** (wonach ausgewählt wird). Mit dem Verfall käme scheinbar eine dritte dazu: **Verfallsgegenstand**.

**Sie kommt nicht dazu, sie ersetzt die zweite.** Nach dem Vorbild von `lzg_knoten` zerfällt der eine Wert in drei Felder mit getrennten Zuständigkeiten:

| Feld | Rolle | Wer ändert es |
|---|---|---|
| `salienz_roh` | Akkumulator — was sich angesammelt hat | Anlage, Verstärkung |
| `salienz_absolut` | **Anker** — was der Auftrag beim letzten Anlass wert war | Anlage, Verstärkung |
| `salienz_decay` | **Präsenz** — was er *jetzt* im Rang einbringt | Anlage, Verstärkung, Verfallslauf |

**Der Scheduler wählt danach nach `salienz_decay`, nicht mehr nach `prioritaet`.** Damit ist die Zwei-Rollen-Vermengung aufgelöst, statt um eine dritte erweitert: Die Herkunft steht im Anker, der Rang in der Präsenz. Das ist derselbe Schnitt, den `lzg_knoten` zwischen `gewicht_absolut` und `gewicht_decay` zieht, und aus demselben Grund.

---

## 4. Die Bauart — drei Stufen, wie beim Knoten

```
salienz_roh       Anfangs-Salienz + Boost je Verstärkung        wächst linear
     ↓  cap · sin(min(roh/cap, 1) · π/2) ^ exp
salienz_absolut   gedämpft, gesättigt bei cap                   Sättigung
     ↓  · e^(−λ · Tage seit verstaerkt_am)
salienz_decay     der effektive Rang                            Zeit
     ↓  < schwelle
aktiv = FALSE     ruhend, nicht gelöscht                        reaktivierbar
```

**Zwei verschiedene Kurven, und sie werden regelmäßig verwechselt.** Der **Aufbau** ist eine Sinus-Sättigung und stammt aus `novaberg-kzg-salienz_k.md` §3. Der **Verfall** ist exponentiell und stammt aus `novaberg-memory-synapsen_k.md` §9.2. Der Sinus verfällt nicht, und das Exponential sättigt nicht; wer „die Sinus-Formel" für den Verfall sagt, meint die Aufbauhälfte.

**Die Sättigung ist der Grund, warum ein Dauerthema den Verfall nicht aushebelt.** Der erste Auftrag zu einem Thema zählt viel, der fünfzigste kaum noch. Ohne sie könnte ein oft wiederkehrender Anlass beliebig hoch klettern und läge dauerhaft über jeder Schwelle.

---

## 5. Die Formel

**Bei Anlage und bei Verstärkung** (ein neuer Anlass betrifft denselben Auftrag):

```
salienz_roh      = salienz_roh + QUEUE_VERSTAERKUNG_BOOST
salienz_absolut  = CAP × sin(min(salienz_roh / CAP, 1) × π/2) ^ DAEMPFUNG_EXP
salienz_decay    = salienz_absolut
verstaerkt_am    = NOW()
decay_am         = NOW()
aktiv            = TRUE
haeufigkeit      = haeufigkeit + 1
```

**Beim Verfallslauf** (einmal täglich, alle aktiven Aufträge):

```
salienz_decay = salienz_absolut × exp(−QUEUE_DECAY_RATE × Tage seit verstaerkt_am)
decay_am      = NOW()
if salienz_decay < QUEUE_SCHWELLE:
    aktiv = FALSE
```

`salienz_absolut` bleibt **unangetastet**. Sie ist die Erinnerung daran, wie dringlich der Auftrag einmal war — und die Bezugsgröße der Reaktivierung.

> **Die Wirkung der Verstärkung sitzt in `verstaerkt_am`, nicht im Boost — nachgerechnet in §12.2.** Zehn Verstärkungen heben `salienz_absolut` um 0,024 und kaufen damit **0,6 Tage**; das Zurücksetzen der Uhr in derselben Zeile schenkt **30**. **Das ist der Zweck der Sinus-Kurve, nicht ihr Versagen:** Wer oben ist, gewinnt durch eine weitere Verstärkung fast nichts, und ein Dauerthema hebelt den Verfall damit nicht aus. Derselbe Bau steht im KZG, wo eine Verstärkung die **TTL** verlängert statt den Wert zu heben.

---

## 6. Die Reaktivierung — 50 % des Wegs zurück

**Ein deaktivierter Auftrag springt bei einem neuen Anlass nicht auf seine alte Dringlichkeit.** Er bekommt die Halbreaktivierung aus `novaberg-memory-synapsen_k.md` §9.3:

```
salienz_decay = (salienz_absolut + QUEUE_SCHWELLE) / 2
verstaerkt_am = NOW()
decay_am      = NOW()
aktiv         = TRUE
```

**Diese Formel ist exakt „50 %", aber nicht 50 % wovon man zuerst denkt.** Sie setzt den Wert auf die Mitte zwischen Deaktivierungsschwelle und Anker — also auf **50 % des Bandes über der Schwelle**. In Absolutwerten sind das bei Schwelle 0,3 je nach Anker 65 bis 80 %:

| Anker | springt auf | vom Anker | vom Band über der Schwelle |
|---|---|---|---|
| 1,0000 | 0,6500 | 65,0 % | **50 %** |
| 0,9764 | 0,6382 | 65,4 % | **50 %** |
| 0,8409 | 0,5704 | 67,8 % | **50 %** |
| 0,6738 | 0,4869 | 72,3 % | **50 %** |
| 0,5000 | 0,4000 | 80,0 % | **50 %** |

**Der Prozentsatz vom Anker ist keine Konstante, der vom Band ist eine.** Das ist der Grund, die Formel zu übernehmen statt „×0,5" zu schreiben: Ein halbierter Anker läge bei einem schwachen Auftrag unter der Schwelle und deaktivierte ihn im selben Zug, in dem er geweckt wird.

**`salienz_roh` und `salienz_absolut` bleiben unverändert.** Der Auftrag wird geweckt, nicht verstärkt — der Boost greift erst bei der nächsten echten Verstärkung.

### 6.1 Was einen ruhenden Auftrag weckt

**Ein neuer Auftrag zum selben Gegenstand.** Das ist die Entsprechung zum Anker-Treffer im LZG, und sie fällt mit einer Lücke zusammen, die heute schon besteht: `shadow_queue_push` prüft **nicht**, ob derselbe Auftrag bereits liegt. Die Schwester-Funktion `promotion_queue_push` tut es seit Chat 111.

> **Damit ist die Reaktivierung keine neue Mechanik, sondern die fehlende Dublettenprüfung — von der anderen Seite gesehen.** Heute erzeugt derselbe Anlass einen zweiten Auftrag; künftig verstärkt er den vorhandenen. Liegt der ruhend, weckt er ihn. **Das ist der einzige Weg, auf dem Wiederkehr sichtbar wird**: Ohne ihn hätte `haeufigkeit` keinen Schreiber und bliebe für immer auf 1, und die Sättigungskurve aus §4 hätte nichts zu sättigen.

**Was „derselbe Gegenstand" heißt, ist eine Setzung und wird gemessen, nicht erfunden.** Gleiches `aufgabe` **und** gleiches `thema` bei demselben Paar. Eine Ähnlichkeitsprüfung über Embeddings wäre der zweite Schritt und braucht eine Schwelle, die es hier noch nicht gibt — und `novaberg-pixie-nachfragen_k.md` §3 hält fest, was eine Schwelle ohne ihre gemessene Paarung wert ist.

### 6.2 Ein leeres Thema ist kein Gegenstand

**Die Regel aus §6.1 fällt ohne diesen Zusatz in sich zusammen, und die Messung zeigt es.** Am 15.08.2026 tragen **145 von 1036** Aufträgen ein leeres `thema` — 141 `vertiefen`, 4 `nachfragen`. Über `aufgabe` + `thema` bilden sie **eine einzige** Gruppe.

```
Verschiedene (aufgabe, thema)-Paare   878 bei 1036 Einträgen
Größte Gruppe                         141 × aufgabe='vertiefen', thema=''
Zweitgrößte                             4 × aufgabe='nachfragen', thema=''
Alle übrigen Gruppen                  höchstens 2 Einträge
```

**Ohne die Leergruppe sind echte Dubletten selten** — keine Gruppe über zwei. Mit ihr würde die Reaktivierung 141 unverwandte Aufträge zu einem einzigen verschmelzen und seine `haeufigkeit` auf 141 treiben. Die Sättigungskurve machte daraus einen Auftrag, der dauerhaft an der Spitze steht und nie verfällt — **aus einem fehlenden Wert würde der wichtigste Eintrag der Queue.**

**Deshalb:** Ein Auftrag mit leerem `thema` ist von der Dublettenerkennung **ausgenommen**. Er verstärkt nichts und wird von nichts verstärkt; er verfällt allein über die Zeit.

> **Das ist eine Notmaßnahme, kein Entwurf.** Ein Auftrag ohne Thema ist bereits defekt — bei `vertiefen` steht der Gegenstand statt dessen als Fließtext in `kontext`, was das Feld nicht meint. Die Ausnahme verhindert, dass der Defekt über die Reaktivierung Wirkung entfaltet; sie behebt ihn nicht. **Das Schema erzwingt `thema NOT NULL`, aber nicht `<> ''`** — eine Prüfung auf Nichtleere gehört in den Schreibpfad, und der gehört nicht zu diesem Bauteil.

---

## 7. Der Umzug nach PostgreSQL

### 7.1 Warum eine Redis-Liste das nicht trägt

**Soft-Delete in einer Liste markiert das Rauschen, statt es abzuräumen.** Die Auswahl liest heute bei jedem Heartbeat die ganze Liste (`LRANGE 0 -1`) und rechnet über jeden Eintrag. Ein deaktivierter Eintrag bliebe darin liegen und würde weiter mitgelesen — der Vollscan wird nie kleiner. Genau das, was der Verfall leisten soll, bliebe aus.

Dazu kommt: Eine Redis-Liste kennt **kein Feld-Update**. `salienz_decay` täglich neu zu schreiben hieße, die ganze Liste zu lesen, jeden Eintrag neu zu serialisieren und die Liste komplett neu zu schreiben. In Postgres ist derselbe Vorgang ein `UPDATE` über eine indizierte Spalte — dieselbe Form wie `run_node_decay`.

### 7.2 Warum die Queue umzieht und der Stapel nicht

**Gemessen am 15.08.2026:**

| | gelesen von | Takt |
|---|---|---|
| `shadow_queue` | Pixie-Heartbeat | alle **30 s** (CPU-Spur) bis **120 s** (LLM-Spur) |
| `shadow_stack` | Zustellungs-Loop | alle **5 s**, je verbundenem Client |

**Der Stapel wird sechs- bis vierundzwanzigmal häufiger gelesen als die Queue** — und sein billigster Riegel ist heute ein `LLEN`, ein O(1)-Aufruf gegen den Arbeitsspeicher. Er bleibt, wo er ist. Für ihn gilt `novaberg-autonomous-wissen_k.md` §11.6 unverändert.

> **Der Preis des Umzugs ist benannt, nicht weggeredet.** Die Postgres-Zugriffe dieses Projekts öffnen je Aufruf eine eigene Verbindung (`psycopg2.connect` in jeder Funktion von `memory/lzg_knoten.py`); einen Verbindungspool gibt es nicht. Im 30-Sekunden-Takt der Queue ist das folgenlos — 2880 Verbindungen am Tag, gegen die der Heartbeat ohnehin Modellaufrufe von 35 bis 38 Sekunden stellt. Im 5-Sekunden-Takt des Stapels wäre es keins von beidem. **Das ist der Grund für die Grenze, nicht die Größe der Daten.**

### 7.3 Was der Umzug nebenbei mitbringt

- **Die Auswahl wird ein Index-Zugriff.** Heute ein O(n)-Vollscan über 1036 Einträge, künftig `ORDER BY salienz_decay DESC LIMIT 1` über einen Index.
- **Der Retry wird ein `UPDATE`.** Heute wird der Eintrag entfernt und neu ans Ende geschrieben — was seine Position ändert und bei einem Absturz zwischen beiden Schritten den Auftrag verliert.
- **Entnehmen und Retry treffen den richtigen Eintrag.** Beide adressieren ihn heute über seinen **exakten JSON-Wortlaut** (`LREM key 1 <rohsatz>`); ein Primärschlüssel ist eindeutig, und ein Fehlgriff wird sichtbar statt wirkungslos (§12.1).
- **Das Paar-Tripel wird vollständig.** Die Queue trägt heute nur `user_id`. Nach dem Paar-Schema gehören `character_id` und `beobachter` dazu.
- **Die Zusicherungen wandern ins Schema.** `NOT NULL` auf `salienz_absolut` macht die 233 stillen Nullen künftig unmöglich.

---

## 8. Das Schema — lückenlos

Jedes Feld des heutigen JSON-Satzes hat eine Spalte, und jede Spalte hat eine Herkunft.

```sql
CREATE TABLE IF NOT EXISTS shadow_auftrag (
    -- Identität
    id                SERIAL           PRIMARY KEY,

    -- Paar-Partition (Paar-Schema: Subjekt × Gegenüber × Beobachter)
    user_id           TEXT             NOT NULL,
    character_id      VARCHAR(50)      NOT NULL,
    beobachter        VARCHAR(20)      NOT NULL,

    -- Auftrag: was getan werden soll
    aufgabe           TEXT             NOT NULL,
    thema             TEXT             NOT NULL,
    kontext           TEXT             NOT NULL DEFAULT '',

    -- Anlass: die Lage, aus der er entstand
    intentionen       TEXT[]           NOT NULL DEFAULT '{}',
    emotion           TEXT             NOT NULL DEFAULT '',
    modus             TEXT             NOT NULL DEFAULT '',

    -- Salienz-Dynamik (Vorbild: lzg_knoten)
    salienz_roh       DOUBLE PRECISION NOT NULL,
    salienz_absolut   DOUBLE PRECISION NOT NULL,
    salienz_decay     DOUBLE PRECISION NOT NULL,
    haeufigkeit       INTEGER          NOT NULL DEFAULT 1,
    aktiv             BOOLEAN          NOT NULL DEFAULT TRUE,

    -- Zeit
    erstellt_am       TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    verstaerkt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    decay_am          TIMESTAMPTZ      NOT NULL DEFAULT NOW(),

    -- Ausführung
    versuche          INTEGER          NOT NULL DEFAULT 0
);

-- Der Auswahlpfad: aktive Aufträge eines Paares, nach Präsenz sortiert.
CREATE INDEX IF NOT EXISTS idx_shadow_auftrag_wahl
    ON shadow_auftrag (user_id, character_id, aktiv, salienz_decay DESC);

-- Der Reaktivierungspfad: derselbe Gegenstand bei demselben Paar (§6.1).
CREATE INDEX IF NOT EXISTS idx_shadow_auftrag_gegenstand
    ON shadow_auftrag (user_id, character_id, aufgabe, thema);
```

**Die Abbildung, Feld für Feld:**

| heute im JSON | Spalte | Anmerkung |
|---|---|---|
| `aufgabe` | `aufgabe` | unverändert |
| `user_id` | `user_id` | unverändert |
| `thema` | `thema` | unverändert |
| `kontext` | `kontext` | unverändert |
| `prioritaet` | `salienz_roh` / `salienz_absolut` / `salienz_decay` | **zerfällt in drei** (§3.2) |
| `intentionen` | `intentionen` | JSON-Liste → `TEXT[]` |
| `emotion` | `emotion` | unverändert |
| `modus` | `modus` | unverändert |
| `erstellt` | `erstellt_am` | ISO-Zeichenkette → `TIMESTAMPTZ` |
| `_retries` | `versuche` | **war undokumentiert** — 43 von 1036 tragen es; die Unterstrich-Konvention verrät ein Feld, das nachträglich hinzukam |
| — | `character_id`, `beobachter` | **neu**, aus dem Paar-Schema |
| — | `haeufigkeit`, `aktiv`, `verstaerkt_am`, `decay_am` | **neu**, aus der Verfallsmechanik |
| — | `arousal` | **nachgetragen am 15.08.2026** — die dritte Größe derselben Lage, die `emotion` und `modus` beschreiben. Sie fehlte, und damit konnte die Recherche keinen Level auf den Stapel legen: Bauteil B war gebaut und ohne Eingabe. **NULL-fähig und ohne Vorgabewert**, anders als ihre beiden Nachbarn — die Quelle liefert sie stellenweise selbst leer, und eine 0,5 wäre ein Messwert, den nie jemand gemessen hat. Bestandszeilen bleiben NULL |

**Drei Zusicherungen stehen im Schema statt im Code**, nach dem Vorbild von `autonomous_wissen`:

1. **Das Paar-Tripel trägt keinen Vorgabewert.** Eine neue Tabelle kann sich den strengeren Weg leisten; ein Vorgabewert `'nova'` würde eine fehlende Zuordnung als gültige ausgeben.
2. **Die drei Salienz-Spalten sind `NOT NULL` ohne Default.** Genau das hätte die 233 stillen Nullen verhindert: Wer ohne Salienz einreiht, scheitert an der Datenbank, statt eine 0,0 zu erzeugen, die wie ein gemessener Wert aussieht.
3. **`versuche` beginnt bei 0, nicht bei `NULL`.** Ein fehlender Zähler und ein Zähler bei null sind verschiedene Aussagen; hier ist nur die zweite gemeint.

---

## 9. Die Konstanten

| Konstante | Wert | Herleitung |
|---|---|---|
| `QUEUE_SALIENZ_CAP` | **1,0** | Die Größe ist Salienz. `KZG_SALIENZ_CAP` ist 1,0, und die Queue führt sie heute so — 785 von 1036 im Band 0,94393–1,0 |
| `QUEUE_SCHWELLE` | **0,3** | entschieden |
| `QUEUE_DECAY_RATE` λ | **0,0393 / Tag** | `ln(0,9764 / 0,3) / 30` — der gemessene Median fällt nach **30 Tagen** unter die Schwelle |
| `QUEUE_DAEMPFUNG_EXP` | **0,5** | wie `lzg_knoten` und wie der KZG-Aufbau |
| `QUEUE_VERSTAERKUNG_BOOST` | **0,03** | wie `KZG_SALIENZ_BOOST` — die Queue trägt KZG-Salienz, der Zuwachs soll derselbe sein |

> **„0,3" ist zweideutig, und beide Lesarten haben im System einen Namen.** Die Salienz existiert als **Rohwert** und als **gedämpfter Wert**, und `config.py` führt die Umrechnung als Konstante mit: `KZG_SALIENZ_MINIMUM = 0.67378`, im Kommentar als *„roh 0.3"* bezeichnet. Ein Rohwert von 0,3 **ist** also der gedämpfte Wert 0,674 — nachgerechnet über die Umkehrung aus §10, die alle drei KZG-Marken exakt reproduziert.
>
> **Hier gilt die Schwelle auf dem gedämpften Wert**, also auf `salienz_decay` selbst. Das ist die Größe, die im Rang steht und die der Verfallslauf schreibt; eine Schwelle auf dem Rohwert müsste bei jedem Vergleich erst zurückgerechnet werden.
>
> **Die Wahl ändert die Frist, nicht nur die Zahl.** Läge die Schwelle bei 0,674, erreichte der Median sie mit derselben Rate schon nach **9,4 Tagen** statt nach 30. Wer beide Angaben — „Schwelle 0,3" und „30 Tage" — für unabhängig hält, bekommt eine dritte Kurve, die keine von beiden ist.

> **Die Skala ist 1,0 und nicht 10,0, und das ist die folgenreichste Setzung dieses Dokuments.** `novaberg-autonomous-wissen_k.md` §11.6 rechnet für den Stapel auf Cap 10,0, weil es dort die Knoten-Skala übernimmt. Auf dieser Skala wäre eine Schwelle von 0,3 gleich **3 %** — sie würde praktisch nie erreicht, und der Verfall liefe ins Leere, ohne dass eine Fehlermeldung entstünde. Die Queue führt Salienz im Bereich 0…1; die Schwelle 0,3 ist auf dieser Skala gemeint.

**Was die Rate bedeutet, gegengerechnet:**

| Startwert | fällt unter 0,3 nach |
|---|---|
| 1,0000 | 30,6 Tagen |
| 0,9764 (Median) | 30,0 Tagen |
| 0,9439 | 29,1 Tagen |
| 0,8409 | 26,2 Tagen |
| 0,6738 | 20,6 Tagen |

**Zum Vergleich: Mit der LZG-Rate 0,0015 fiele derselbe Median erst nach 787 Tagen** — gut zwei Jahre. Die Queue-Rate ist 26-mal höher, und das ist der Punkt: Ein unerledigter Auftrag ist schneller gegenstandslos als eine Erinnerung.

> **Damit lösen sich „30 Tage TTL" und „nichts wird hart gelöscht" auf, die zunächst widersprüchlich aussehen.** Die 30 Tage sind **keine Löschfrist**. Sie sind die Zeit, in der ein unberührter Auftrag von voller Salienz auf die Deaktivierungsschwelle fällt. Danach ruht er und ist reaktivierbar — er verschwindet nicht.

**Diese Zahlen sind hergeleitet und teilweise gemessen, aber nicht erprobt.** Der Median stammt aus dem Bestand vom 15.08.2026; die Rate folgt daraus rechnerisch. Ob 30 Tage die richtige Frist sind, ist eine Setzung. Wer sie später vorfindet, darf sie nicht für ein Messergebnis halten.

---

## 10. Die Migration des Bestands

1036 Aufträge liegen als JSON in einer Redis-Liste. Sie tragen keine der neuen Größen.

| Feld | Wert bei der Übernahme | Grund |
|---|---|---|
| `salienz_absolut` | der heutige `prioritaet`-Wert | er *ist* die Auslöse-Salienz |
| `salienz_decay` | **gerechnet**, nicht kopiert | siehe unten |
| `salienz_roh` | rückgerechnet aus `absolut` | `CAP × (asin((absolut/CAP)^(1/exp)) × 2/π)` |
| `haeufigkeit` | 1 | Wiederkehr wurde nie gezählt |
| `verstaerkt_am` | `erstellt` | es gab keine Verstärkung |
| `character_id` | `'nova'` | einziger Charakter im Bestand |
| `beobachter` | `'user'` | der Auslöser war eine Nutzeräußerung |
| `versuche` | `_retries` oder 0 | |

**`salienz_decay` wird beim Übernehmen gerechnet, nicht kopiert.** Der Bestand ist bis zu 18 Tage alt; wer den Anker als Präsenz einträgt, setzt alle Aufträge auf „gerade eben verstärkt" und verschiebt den ersten Verfall um bis zu 18 Tage. Die Formel aus §5 mit `verstaerkt_am = erstellt` bildet das Alter korrekt ab.

**Die 233 Aufträge auf 0,0 fallen beim ersten Lauf sämtlich heraus.** Das ist **gewollt und wird vorher aufgeschrieben**, damit es niemand später für einen Unfall hält. Sie tragen keine gemessene Salienz, sondern eine, die nie geschrieben wurde.

**Die Ursache ist am 15.08.2026 gefunden und gehört hierher, weil sie den Umzug zur Bedingung hat.** `shadow_queue_push` wird von **zwei** Stellen gerufen, und nur eine übergibt den Wert:

```
agents/kzg/queues.py   shadow_queue_push(… prioritaet=neue_salienz …)   ✅
memory/kzg.py          shadow_queue_push(… kein prioritaet-Argument …)  ❌
```

Die Signatur trägt `prioritaet: float = 0.0`. **Der Vorgabewert macht aus einem fehlenden Argument eine Zahl, die wie eine gemessene aussieht** — der Aufruf ist vollständig, es fehlt nichts sichtbar. Geführt als `KANDIDATEN-PRIORITAET-STILLE-NULL`.

**Eine Rekonstruktion der Werte ist trotzdem nicht möglich**: Der auslösende Turn ist nicht mehr zuzuordnen.

> **Der Defekt ist vor dem Umzug zu beheben, nicht danach.** Das neue Schema erzwingt `salienz_absolut NOT NULL` **ohne Vorgabewert** — genau das, was hier fehlt. Wird der Aufrufer vorher berichtigt, ist der Umzug still; wird er es nicht, scheitert nach dem Umzug jeder zweite Schreibpfad an der Datenbank. **Das ist der gewünschte Ausgang und trotzdem der falsche Zeitpunkt**, ihn zu entdecken.

> **Sie fallen heraus, sie verschwinden nicht.** Genau dafür ist das Soft-Delete da. Zeigt sich später, dass die Null ein Schreibfehler war und nicht ein schwacher Anlass, stehen 233 Aufträge zur Reaktivierung bereit — bei hartem Löschen wären sie weg.

---

## 11. Wer den Verfall rechnet

**Der Weg existiert und ist erprobt; es wird kein neuer Mechanismus gebaut.** `novaberg-autonomous-wissen_k.md` §11.7 hat das für den Stapel entschieden, und die Begründung trägt hier unverändert: Der Tageslauf `synapsen_decay` tut heute schon Knoten-Decay und `pipeline_log`-Aufräumen. Ein weiterer Schritt darin kostet **keinen zusätzlichen Platz im Heartbeat** — bei einem einzigen seriellen Platz ist das ausschlaggebend.

**Der Preis ist derselbe und wird genauso bezahlt:** Ein Lauf, der mehreres tut, färbt bei einem Fehlschlag im letzten Schritt den ganzen Auftrag rot. Dagegen hilft, was die Norm ohnehin verlangt — **je Schritt ein eigener `hintergrund_log`-Eintrag** mit `gestartet` / `erledigt` / `fehler`. Erst dann ist unterscheidbar, ob der Verfall lief und nichts fand, oder ob er gar nicht lief.

---

## 12. Der Lebenszyklus — geprüft, gerechnet, entschieden

Der Entwurf ist am 15.08.2026 gegen den gemessenen Bestand durchgerechnet worden: Anlegen, Bestand, Priorisierung, Verfall, Löschen, Reaktivierung. **Vier Stellen sahen dabei aus wie Mängel und sind es nicht** — sie sind die Bauart, und dieser Abschnitt hält fest, warum. Eine fünfte ist offen geblieben und ist es weiterhin.

### 12.1 Drei Wege aus der Queue, und nur einer ist ein Löschen

| Weg | Was geschieht | Rückweg |
|---|---|---|
| **Erledigt** — der Agent hat den Auftrag ausgeführt | **Die Zeile wird entfernt.** Ein erledigter Vorsatz ist kein Vorsatz mehr | keiner, und keiner nötig |

| **Verfallen** — 30 Tage ohne Anlass | `aktiv = FALSE`, die Zeile bleibt | Reaktivierung (§6) |
| **Gescheitert** — drei Fehlversuche | **Die Zeile wird entfernt** (`_RETRY_GRENZE`) | keiner |

> **Das Entnehmen nach der Ausführung ist ein Löschen, und es ist das einzige, das keiner Begründung bedarf.** Was abgearbeitet wurde, ist erledigt; es aufzubewahren hieße, eine Aufgabenliste mit einem Tagebuch zu verwechseln. **Alles andere wird gelagert, bis es drankommt** — und wenn es nicht drankommt, ist es später deaktiviert, nicht verschwunden.

**Der Weg „erledigt" ist heute schon gebaut und ändert sich nur in der Technik.** `abschluss(kandidat, erfolg=True)` ruft `_eintrag_entfernen`, und das ist ein `LREM key 1 <rohsatz>`. **Nach dem Umzug wird daraus ein `DELETE … WHERE id = …`** — und das ist der stillste Gewinn des Umzugs: `LREM` sucht den Eintrag über seinen **exakten JSON-Wortlaut**. Weicht ein einziges Zeichen ab, entfernt es nichts und meldet nichts, denn die Funktion hält im Docstring ausdrücklich fest, `lrem` auf einem nicht vorhandenen Satz sei wirkungslos. Ein Primärschlüssel kann das nicht.

**Damit steht die Queue zwischen den beiden Gedächtnissen, und der Vergleich ist die Begründung ihrer Bauart:**

| Speicher | Was am Ende geschieht | Rückweg |
|---|---|---|
| **KZG** (Redis) | **hart gelöscht** über die TTL — 7 / 14 / 30 Tage, gestaffelt nach Salienz (`KZG_TTL_LOW/MID/HIGH`) | keiner |
| **LZG** (`lzg_knoten`) | **nie gelöscht** — `aktiv = FALSE`, die Zeile bleibt | Halbreaktivierung |
| **Queue** (künftig) | erledigt → **entfernt** · nicht erledigt → **`aktiv = FALSE`** | Reaktivierung |

**Die Queue nimmt vom KZG die Frist und vom LZG den Rückweg.** Das ist kein Kompromiss, sondern folgt aus dem Gegenstand: Ein Auftrag hat wie ein KZG-Eintrag ein Verfallsdatum, weil sein Anlass altert — aber er soll wie ein LZG-Knoten weckbar bleiben, weil derselbe Anlass wiederkommen kann.

> **Ein Detail des KZG stützt §12.2:** Bei einer Verstärkung wird dort die **TTL verlängert** (`expire(key, max(verbleibend, neuer_ttl))`), nicht der Wert erhöht. Auch im Kurzzeitgedächtnis wirkt Wiederholung über die Uhr.

### 12.2 Die Sättigung ist die Absicht — die Uhr ist die Wirkung

**Gerechnet, mit dem gemessenen Median als Einstieg:**

| Verstärkungen | `salienz_absolut` | Zugewinn | gewonnene Zeit |
|---|---|---|---|
| 0 | 0,976400 | — | 30,00 Tage |
| 1 | 0,983116 | +0,0067 | 30,17 Tage |
| 5 | 0,998739 | +0,0223 | 30,58 Tage |
| **10** | 1,000000 | +0,0236 | **30,61 Tage** |

**Wer oben ist, gewinnt durch eine weitere Verstärkung fast nichts — und genau dafür ist die Sinus-Kurve da.** Ein Auftrag steigt bei `salienz_roh ≈ 0,80` von Cap 1,0 ein und liegt damit bereits im flachen Teil. Das ist kein Fehlschlag der Kurve, sondern ihr Zweck: Ein Dauerthema soll nicht unbegrenzt wachsen und den Verfall aushebeln.

**Die Wirkung der Verstärkung sitzt deshalb in `verstaerkt_am`:** Die Uhr wird zurückgesetzt, der Auftrag bekommt **volle 30 Tage neu**. Das ist die Größenordnung, um die es geht — 30 Tage gegen 0,61.

> **Was daraus für die Kalibrierung folgt:** `QUEUE_VERSTAERKUNG_BOOST` ist **keine Stellschraube der Frist**. Wer die Haltedauer eines wiederkehrenden Themas ändern will, ändert `QUEUE_DECAY_RATE` oder nichts. Ein Boost, der von 0,03 auf 0,10 gedreht wird, bewegt am oberen Ende der Kurve weiterhin fast nichts — und der, der ihn dreht, sucht den Fehler dann anderswo.

### 12.3 Die Rangfolge ist Dringlichkeit — und Dringlichkeit ist Frische

**Entschieden am 15.08.2026: Jeder Punkt kommt nach Dringlichkeit dran.** `salienz_decay` **ist** die Dringlichkeit, und weil der Verfall sie über die Zeit senkt, ist der jüngste Auftrag zugleich der dringlichste.

> **Der letzte Gedanke ist der präsenteste.** Er ist frisch, er glüht, er will präsent sein — nicht der von vor dreißig Tagen, der nach Wartezeit als nächster an der Reihe wäre. Ein Vorsatz wird nicht dadurch dringlicher, dass er lange liegt; er wird es weniger.

**Was das gegenüber heute ändert, und es ist eine Umkehr:**

```
heute        _queue_peek nimmt den ersten mit echt groesserer Prioritaet.
             Das Maximum 1,0 tragen 59 Eintraege; der erste steht an
             Listenposition 894 von 1036. rpush haengt hinten an
             → es gewinnt der aelteste Eintrag des Hoechstwerts.  FIFO

kuenftig     ORDER BY salienz_decay DESC
             → es gewinnt der juengste Eintrag ueberhaupt.        LIFO
```

**Die Umkehr ist gewollt und hier festgehalten, damit sie nicht später als Defekt gemeldet wird.** Sie ist keine Nebenwirkung des Umzugs, sondern die Absicht: Was heute FIFO ist, war nie entschieden, sondern folgte aus `prio > beste_prio` und der Einfügereihenfolge einer Liste.

**Die Wechselwirkung mit dem Aging der periodischen Aufgaben ist zu kennen.** Im selben Scheduler laufen jetzt zwei gegenläufige Zeitregeln:

| | Maßstab | Richtung |
|---|---|---|
| Periodische Aufgaben (`_aging_zuschlag`) | absolute Wartezeit | Priorität **steigt** mit dem Warten |
| Queue-Aufträge (dieses Konzept) | Dringlichkeit | Priorität **fällt** mit dem Warten |

**Das ist kein Widerspruch, sondern zwei verschiedene Gegenstände.** Eine Wartungsaufgabe wird dringlicher, je länger sie aussteht — ein unerledigter Einfall wird es nicht. **Die Folge ist trotzdem zu benennen:** Über die Zeit verschiebt sich das Kräfteverhältnis im Heartbeat zugunsten der periodischen Aufgaben. Heute gewinnen Queue-Aufträge fast immer, weil sie bei 0,94 bis 1,0 liegen; ein zwanzig Tage alter Auftrag liegt bei 0,44 und verliert gegen jede vier Stunden überfällige Wartungsaufgabe am Aging-Deckel.

### 12.4 Die Reaktivierung hält am Leben — das ist ihr Zweck, nicht ihre Grenze

Ein reaktivierter Auftrag springt auf `(salienz_absolut + 0,3) / 2` — bei einem Anker von 0,976 also auf **0,638**, den Stand eines rund elf Tage alten Auftrags. Gegen frische Zugänge bei 0,976 gewinnt er damit nicht.

**Das ist richtig so.** Die Reaktivierung soll einen Vorsatz **am Leben halten**, nicht ihn vordrängeln. Ein Anlass, der wiederkehrt, hebt den alten Auftrag aus der Ruhe zurück in den Bestand — ob er dann drankommt, entscheidet dieselbe Dringlichkeitsordnung wie für alle anderen (§12.3). Wollte man ihn nach vorn holen, müsste man ihn über die frischen Zugänge setzen, und damit wäre die Wiederholung wichtiger als die Gegenwart.

**Wiederholt sich der Anlass mehrfach, holt er den Auftrag von selbst nach oben** — jede Verstärkung setzt die Uhr zurück (§12.2), und ein Auftrag mit frischer Uhr steht wieder ganz oben.

### 12.5 Die Menge ist keine Grenze — die Rate ist die Stellschraube

**Es wird nichts gelöscht außer dem Erledigten und dem Gescheiterten.** Die Tabelle wächst deshalb: bei rund 1000 neuen Aufträgen im Monat und kleinem Abfluss etwa 12.000 Zeilen im Jahr, überwiegend inaktiv.

**Für PostgreSQL ist das folgenlos** — der Auswahl-Index trägt `aktiv` an führender Stelle; inaktive Zeilen kosten die Auswahl nichts.

> **Entschieden am 15.08.2026: keine Mengengrenze, keine zweite Frist.** Sammeln sich einmal Zehntausende aktiver Einträge, die nie abfließen, dann ist **der Verfall zu schwach eingestellt und wird verstärkt** — `QUEUE_DECAY_RATE` ist die Stellschraube. Eine Obergrenze wäre der falsche Hebel: Sie würde Einträge nach ihrer Zahl verwerfen statt nach ihrer Dringlichkeit, und damit genau die Ordnung durchbrechen, die dieses Konzept herstellt.

**Ein Jahresablauf für nie reaktivierte Aufträge ist erwogen und nicht eingeführt.** Das Argument dagegen ist dasselbe wie im LZG: Was einmal ein Vorsatz war, kostet als ruhende Zeile fast nichts und ist der einzige Beleg dafür, dass er je bestand. **Die Bedingung, unter der er doch käme, steht damit fest** — wenn die Tabelle die Auswahl messbar verlangsamt, und nicht, wenn sie nur groß aussieht.

### 12.6 Was die Prüfung gestützt hat

**Der Abfluss ist der eigentliche Befund.** Die Altersverteilung des Bestands dünnt zu den alten Tagen hin nicht aus:

```
18 Tage: 57   17 Tage: 54   16 Tage: 26   15 Tage: 74
14 Tage: 113  13 Tage: 151  …   2 Tage: 124   1 Tag: 104   0 Tage: 120
```

**Würde die Queue nennenswert abgearbeitet, müsste diese Verteilung zu den alten Tagen hin ausdünnen. Sie tut es nicht** — 57 Aufträge vom ältesten Tag liegen unberührt. Zusammen mit dem Zuwachs während der Messung heißt das: Der Zufluss übersteigt den Abfluss deutlich, und **der Verfall ist damit der einzige realistische Weg hinaus** für alles, was nicht drankommt.

**Was ungeprüft bleibt:** Die tatsächliche Abflussrate ist aus der Altersverteilung erschlossen, nicht aus dem `hintergrund_log` gezählt. Das trägt die Aussage „klein", nicht eine Zahl.

## 13. Die drei Zeilen

| | |
|---|---|
| **ZIEL** | Ein Auftrag, den 30 Tage lang kein Anlass mehr berührt hat, wird für die Auswahl unsichtbar, bleibt aber gespeichert und kommt bei einem neuen Anlass zum selben Gegenstand mit halber Dringlichkeit zurück. Ein **abgearbeiteter** Auftrag verschwindet dagegen ganz. |
| **TEST** | Wird rot, wenn ein Auftrag mit `salienz_decay` unter 0,3 nach einem Verfallslauf noch `aktiv = TRUE` trägt; wenn ein Auftrag durch den **Verfallslauf** aus der Tabelle verschwindet; wenn ein **erledigter** Auftrag in der Tabelle stehen bleibt; wenn die Auswahl einen inaktiven Auftrag liefert; und wenn die Reaktivierung einen Wert setzt, der nicht `(salienz_absolut + 0,3) / 2` ist. Dazu zwei Gegenproben: Ein Auftrag mit `verstaerkt_am` von vor 29 Tagen bleibt aktiv, einer von vor 31 Tagen nicht — und **die Auswahl liefert bei zwei Aufträgen gleicher Herkunft den jüngeren** (§12.3), was heute umgekehrt wäre. |
| **MESSUNG** | Ein echter Lauf gegen den migrierten Bestand. **Vorhergesagt, bevor er läuft:** 233 Deaktivierungen (die stillen Nullen), 0 weitere — kein Auftrag im Bestand ist älter als 18 Tage. Ein zweiter Lauf 30 Tage später trifft die dann fälligen. |

> **Die Messung hat eine Hürde, die vor dem Bau zu nennen ist.** Die eigentliche Wirkung — ein Auftrag fällt durch Alter heraus — ist am Bestand vom 15.08.2026 **nicht** zu beobachten, weil er zu jung ist. Sie ist nur über gesetzte Zeitstempel prüfbar, und das ist ein Zeuge, keine Messung. Die echte Messung braucht 30 Tage Betrieb. Das ist kein Grund, sie zu ersetzen, sondern einer, sie einzuplanen.

---

## 14. Was nicht enthalten ist

- **Der Stapel zieht nicht um.** Er bleibt in Redis, mit den Konstanten aus `novaberg-autonomous-wissen_k.md` §11.6. Der Grund steht in §7.2 und ist gemessen, nicht vermutet.
- **Wiederkehrende Aufgaben bleiben, wie sie sind.** Sie dürfen über 1,0 steigen und immer gewinnen; das ist gewollt. Ihr Aging (`_aging_zuschlag`) ist ein anderer Mechanismus mit einem anderen Zweck — Verhungerungsschutz statt Verfall — und wird von hier nicht berührt.
- **Der Retry-Pfad bleibt, wie er ist.** Nach `_RETRY_GRENZE` = 3 Fehlversuchen wird ein Auftrag **hart** verworfen. Das ist kein Verfall, sondern ein Ausführungsfehler; die drei Wege hinaus stehen in §12.1.
- **Kein Verhungerungsschutz für Queue-Aufträge.** Was die periodischen Aufgaben über `_aging_zuschlag` bekommen, bekommt die Queue ausdrücklich **nicht**: Ein Vorsatz wird nicht dringlicher, weil er lange liegt (§12.3). Ein Aging-Zuschlag auf `salienz_decay` würde den Verfall teilweise aufheben und ist deshalb nicht nur unnötig, sondern gegenläufig.
- **Keine Mengengrenze und kein Jahresablauf** (§12.5). Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt.
- **Die Umbenennung von `prioritaet`** geschieht im Umzug, weil die Spalten dort ohnehin neu entstehen — nicht als eigener Zug (§3.1).
- **Keine Ähnlichkeitsprüfung bei der Dublettenerkennung.** Gleiches `aufgabe` und `thema`, mehr nicht (§6.1).

---

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

## 16. Gebaut und gemessen — 15.08.2026

`shadow_auftrag` in `db/init.sql`, `memory/repositories/shadow_auftrag_repository.py`,
fünf Konstanten in `config.py`, Umbau von `services/shadow_agent/utils.py`,
`services/pixie/kandidaten.py` und `services/pixie/dispatch.py`, dritter Schritt
in `agents/synapsen_decay/`. **1399 Tests grün, 0 übersprungen** (1373 vorher,
26 neu). Beide Wände sauber, alle berührten Dateien auf ihrer Nulllinie.

### Die Reihenfolge, in der gebaut wurde

**Die stille Null zuerst** — sie war Vorbedingung, weil das Schema erzwingt,
was in der Signatur fehlte. `memory/kzg.py` übergibt seither die Salienz, und
der Vorgabewert `0.0` ist aus `shadow_queue_push` verschwunden.

**Dann die Tabelle**, in der von `16_PERSISTENZ.md` §2 geforderten Folge:
Zeuge zuerst — er brannte gegen das unveränderte Schema und war rot —, dann
der Schema-Edit, dann ein Anfasser. Der Beleg steht im Behälter-Log:
**132 Statements** statt 129, also genau eine Tabelle und zwei Indizes.

### Die Migration

| | |
|---|---|
| gelesen / geschrieben | **1036 / 1036**, 0 unlesbar |
| danach aktiv | **803** |
| danach ruhend | **233** — ausnahmslos `vertiefen` |
| je Aufgabenart | recherche 608 (608 aktiv) · vertiefen 383 (150 aktiv) · nachfragen 45 (45 aktiv) |
| `erstellt_am` | 27.07. bis 15.08.2026 |

**Die Vorhersage aus §13 ist exakt eingetroffen:** 233 Deaktivierungen, keine
weiteren. Gegengeprüft wurde außerdem, dass keine Zeile `salienz_decay >
salienz_absolut` trägt, keine aktive Zeile unter der Schwelle liegt und keine
ein fremdes Paar-Tripel hat — je 0 Treffer.

### Der Verfallslauf am echten Bestand

```
vorher    aktiv 803, ruhend 233
Lauf      805 verarbeitet, 0 deaktiviert, kein Fehler
nachher   aktiv 803, ruhend 233
Summe     1036 -> 1036   — nichts gelöscht
```

**0 Deaktivierungen sind das richtige Ergebnis**, nicht ein wirkungsloser
Lauf: Die 233 ruhen bereits, und kein übriger Auftrag ist 30 Tage alt. Die 805
gegenüber 803 sind zwei Zeilen eines Testpaares, die der Lauf global miterfasst
hat — der Verfall filtert nicht auf ein Paar, wie `run_node_decay` auch nicht.

Der Gewinner der Auswahl war der **jüngste** Auftrag (erstellt am selben Tag,
`salienz_decay` 0,9974) — die Rangfolge aus §12.3 im Betrieb.

### Was der Bau am Konzept berichtigt hat

**Die Migration übernimmt 1:1, ohne Verdichtung.** Das Konzept ließ offen, ob
gleiche Gegenstände beim Übernehmen verschmelzen sollen. Sie tun es nicht: Eine
Verdichtung setzte `haeufigkeit` auf eine Zahl, die nie gemessen wurde. Echte
Dubletten verschmelzen beim nächsten Anlass von selbst.

**Ein zirkulärer Import war zu brechen.** `services/shadow_agent/utils.py`
holt das Repository, `memory/__init__` lädt `memory.kzg`, und die holt sich
`shadow_queue_push` aus genau diesem Modul. Der Import steht deshalb lokal in
der Funktion.

**Der Dispatcher las zwei Feldnamen, die es nie gab.** Der AgentState bekam
`themen` und `salienz` aus dem Auftrag — beides Schlüssel, die ein
Shadow-Auftrag nicht trägt; er erhielt dauerhaft `""` und `0.0`. Derselbe
Namensirrtum stand im Moduldokument und im Rückfall der Kandidatenwahl.
Berichtigt im Zug des Umbaus, weil die alten Namen nach dem Umzug ohnehin
nicht mehr existieren.

### Fünf Bestandszeugen mussten nachgezogen werden

Sie prüften richtige Zusicherungen über den Redis-Umweg. Vier davon gelten
unverändert und belegen sich jetzt an der Tabelle. **Einer beschrieb eine
Zusicherung, die dieser Bau aufhebt:** *„Queue-Einträge altern nicht"* — sie
altern jetzt nach unten. Sein Kern bleibt und ist schärfer geworden: Ein
Auftrag ohne Agenten wandert nicht nach oben, **und er bleibt auch nicht
liegen.**

> **Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.** Zwei Fälle in
> `test_pixie_aging.py` wurden rot, sobald das aktive Paar auf eine Testpersona
> stand. Sie stellen die Queue jetzt über einen Patch, statt sie zu lesen —
> sie prüfen die Wahl des Schedulers, nicht den Speicher.

### Was der Audit der Nähte fand — drei Leser, die niemand mitgeändert hat

**Nach dem Bau wurden die Schnittstellen einzeln durchgegangen.** Fünf Nähte,
drei davon gebrochen — und keine hatte die Suite bemerkt, weil alle drei
*hinter* den geprüften Stellen lagen.

| Naht | Befund |
|---|---|
| Redis-Schlüssel `shadow_queue:*` | sauber, kein Leser mehr im Produktivcode |
| `queue_key` / `queue_raw` / `auftrag_id` | sauber, nach Speicher getrennt |
| **`quelle`-Wert** | **gebrochen** — `services/pixie/router.py` |
| **Auftragsfelder in den Agenten** | **gebrochen** — `recherche`, `nachfragen` |
| Promotions-Queue | sauber, liest ihre eigenen Felder |

**Der Router kannte den neuen Wert nicht.** Er verzweigte weiter auf
`quelle == "queue"`. Die Wirkung war vollständig und still: Der Heartbeat
wählte im Dreißig-Sekunden-Takt einen Auftrag, der Router fand keinen Agenten,
der Auftrag blieb liegen. **Kein einziger Shadow-Auftrag lief mehr** — und die
Warnung je Zyklus sah aus wie der lange bekannte Fall *„Auftrag für einen
Agenten, den es nicht gibt"*. Kein Datenverlust, weil `abschluss` erst nach
einer Ausführung greift.

**`_salienz_aus_auftrag` las zwei Felder, die es nicht mehr gibt.** Der
Recherche-Agent griff nach `salienz` oder `prioritaet`; ein migrierter Auftrag
trägt keines von beiden, sondern drei Salienz-Stände. **Jeder Recherche-Auftrag
hätte `ValueError` geworfen, wäre als Fehlversuch gezählt und nach drei
Versuchen verworfen worden** — bei 608 Aufträgen. Er liest jetzt
`salienz_absolut` zuerst: den **Anker**, nicht die Präsenz. Der Anker ist, was
der Auftrag beim Anlass wert war; die Präsenz schriebe sein Alter in die
Bibliothek.

Dazu eine Logzeile im Nachfragen-Agenten, die den Auftrag über `erstellt`
datierte — jetzt `erstellt_am`.

> **Wer einen Wert einführt, muss seine Leser suchen — nicht nur seine
> Schreiber.** Die Zeugen des Umbaus prüfen den Erzeuger, die Auswahl und den
> Abschluss. **Zwischen Auswahl und Abschluss steht der Router, und ihn hat
> niemand gefragt.** `tests/test_pixie_verdrahtung.py` prüft seither die
> **Kette** statt ihrer Glieder: Es liest die möglichen `quelle`-Werte aus dem
> Quelltext des Erzeugers, statt sie aufzuzählen — eine Aufzählung wäre beim
> nächsten neuen Wert wieder still veraltet.

**Nebenbei bezeugt statt vermutet:** Der Router löst `vertiefen` auf
`vertiefung` auf, und kein Agent dieses Namens ist registriert
(`PIXIE-ROUTING-DOPPELREGISTRY`). Das ist der Grund, warum 383 Aufträge liegen.
Der Fall steht jetzt als Zeuge und ist zu **streichen**, nicht anzupassen,
sobald der Agent existiert.

### Die Kette, am laufenden Server belegt

```
15:46:23  Pixie[llm]: Gewinner — recherche (Prio 1.00, Quelle: shadow_auftrag)
15:46:23  RechercheAgent: Start — Thema aus Queue: 'kosmische Präzision, …'
```

Auswahl aus der Tabelle, Router, Registry, Agent — mit dem richtigen Thema.
Vor der Berichtigung endete es nach der ersten Zeile. Ein Auftrag mit Salienz
0,0 scheitert weiterhin laut, wie gefordert.

**Suite 1399 → 1404 grün** (fünf Zeugen der Verdrahtung).


### Was ungemessen bleibt, ausdrücklich

**Die eigentliche Wirkung — ein Auftrag fällt durch Alter heraus — ist am
Bestand nicht zu beobachten**, weil keiner alt genug ist. Sie ist über gesetzte
Zeitstempel geprüft (29 Tage aktiv, 31 Tage nicht), und das ist ein Zeuge,
keine Messung. Die echte Messung braucht 30 Tage Betrieb.

Ebenso ungemessen: die **Reaktivierung im Betrieb**. Dass sie rechnet, ist
belegt; dass ein wiederkehrender echter Anlass denselben Gegenstand trifft,
nicht.

---

## Versionshistorie

- **v0.6 — 15.08.2026:** Die Spaltentabelle in §8 trägt **`arousal`** — die dritte Größe derselben Lage, die `emotion` und `modus` beschreiben. Sie fehlte seit dem Umzug, und die Folge war keine Fehlfunktion, sondern eine **Leere**: Die Recherche konnte keinen Level auf den Stapel legen, weil sie keinen bekam, und Bauteil B der Eigenzeit war gebaut und ohne Eingabe. **NULL-fähig und ohne Vorgabewert**, anders als ihre beiden Nachbarn — die Quelle liefert sie stellenweise selbst leer, und eine 0,5 wäre ein Messwert, den nie jemand gemessen hat. 1050 Bestandszeilen bleiben NULL. DDL angekündigt, Beleg im Log: 133 Statements statt 132.

- **v0.5 — 15.08.26:** §16 um den **Audit der Nähte** erweitert. Fünf Schnittstellen einzeln durchgegangen, **drei gebrochen** — und keine hatte die Suite bemerkt, weil alle drei hinter den geprüften Stellen lagen. Der **Router** kannte `quelle = "shadow_auftrag"` nicht und verzweigte weiter auf `"queue"`: Der Heartbeat wählte im Dreißig-Sekunden-Takt einen Auftrag, fand keinen Agenten und ließ ihn liegen — **kein einziger Shadow-Auftrag lief mehr**, und die Warnung sah aus wie der bekannte Fall des fehlenden Agenten. **`_salienz_aus_auftrag`** las `salienz`/`prioritaet`, die ein migrierter Auftrag nicht trägt; jeder der 608 Recherche-Aufträge wäre mit `ValueError` gescheitert und nach drei Versuchen verworfen worden. Dazu eine Logzeile auf `erstellt` statt `erstellt_am`. **Die Lesson:** Wer einen Wert einführt, muss seine **Leser** suchen, nicht nur seine Schreiber — die Zeugen prüften Erzeuger, Auswahl und Abschluss, und zwischen Auswahl und Abschluss stand der Router. Der neue Zeuge liest die möglichen Werte aus dem Quelltext des Erzeugers statt sie aufzuzählen. Nebenbei bezeugt: `vertiefen` löst auf einen nicht registrierten Agenten auf (`PIXIE-ROUTING-DOPPELREGISTRY`) — der Grund für die 383 liegenden Aufträge.
- **v0.4 — 15.08.26:** **Gebaut und gemessen**, §16 neu. Die Migration übernahm **1036 von 1036** Aufträgen; danach 803 aktiv, 233 ruhend — und die 233 sind ausnahmslos `vertiefen`, die Vorhersage aus §13 traf exakt. Der Verfallslauf am echten Bestand: 805 verarbeitet, 0 deaktiviert, Summe unverändert — **nichts gelöscht**, und 0 Deaktivierungen sind hier das richtige Ergebnis. Drei Dinge hat der Bau am Konzept berichtigt: Die Migration übernimmt **1:1 ohne Verdichtung**, weil eine Verdichtung `haeufigkeit` eine nie gemessene Zahl gäbe; ein **zirkulärer Import** zwischen `shadow_agent.utils` und `memory.kzg` war lokal zu brechen; und der Dispatcher las mit `themen` und `salienz` **zwei Feldnamen, die es nie gab** — der AgentState bekam dauerhaft `""` und `0.0`. Fünf Bestandszeugen sind nachgezogen, vier davon unverändert gültig; der fünfte trug den Satz „Queue-Einträge altern nicht", den dieser Bau aufhebt. Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.
- **v0.3 — 15.08.26:** **§12 auf die Entscheidungen umgeschrieben — was in v0.2 wie vier Mängel aussah, ist die Bauart.** §12.1 neu: **drei Wege aus der Queue, und nur einer ist ein Löschen** — was abgearbeitet wurde, wird entnommen (heute schon: `abschluss(erfolg=True)` → `LREM`), was scheitert, wird nach drei Versuchen verworfen, was nur wartet, wird deaktiviert und bleibt. Dazu der Vergleich, der die Bauart begründet: **Der KZG löscht hart** über Redis-TTL (7 / 14 / 30 Tage nach Salienz), **das LZG nie** — die Queue nimmt vom KZG die Frist und vom LZG den Rückweg. Ein Detail des KZG stützt §12.2: Eine Verstärkung verlängert dort die **TTL**, sie hebt nicht den Wert; auch im Kurzzeitgedächtnis wirkt Wiederholung über die Uhr. **Die Sättigung ist der Zweck der Sinus-Kurve, nicht ihr Versagen** — wer oben ist, gewinnt durch eine weitere Verstärkung fast nichts, und ein Dauerthema hebelt den Verfall damit nicht aus; der Boost ist dafür ausdrücklich **keine Stellschraube der Frist**. **Die Rangfolge ist Dringlichkeit, und Dringlichkeit ist Frische:** Der letzte Gedanke ist der präsenteste, nicht der von vor dreißig Tagen — die Umkehr von FIFO auf LIFO ist damit die Absicht und nicht eine Nebenwirkung. Benannt bleibt die Wechselwirkung mit dem Aging der periodischen Aufgaben: zwei gegenläufige Zeitregeln im selben Scheduler, beide für ihren Gegenstand richtig, mit einer langsamen Verschiebung zugunsten der Wartungsaufgaben. **Die Reaktivierung hält am Leben und drängelt nicht vor** — wiederholt sich der Anlass mehrfach, holt die zurückgesetzte Uhr den Auftrag von selbst nach oben. **Keine Mengengrenze und kein Jahresablauf:** Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt — eine Obergrenze würde nach Zahl statt nach Dringlichkeit verwerfen. Als Gewinn des Umzugs neu benannt: `LREM` adressiert den Eintrag über seinen exakten JSON-Wortlaut und ist bei jeder Abweichung **wirkungslos und stumm**; ein Primärschlüssel kann das nicht.
- **v0.2 — 15.08.26:** **§12 neu — der Lebenszyklus ist gegen den Bestand durchgerechnet**, und vier Stellen trugen nicht, wie sie in v0.1 standen. **Die Verstärkung wirkt nicht über die Höhe:** Zehn Verstärkungen heben `salienz_absolut` um 0,024 und kaufen 0,61 Tage, weil ein Auftrag bei `salienz_roh ≈ 0,80` von Cap 1,0 einsteigt und die Sinus-Kurve dort waagerecht ist — die Sättigung ist erreicht, bevor der erste Auftrag entsteht. Die Wirkung sitzt in `verstaerkt_am`, das 30 Tage neu schenkt; der Boost bleibt im Schema, aber **niemand darf von ihm eine Rangwirkung erwarten**. **Die Rangfolge kehrt sich um:** Heute gewinnt der älteste Eintrag des Höchstwerts (das Maximum 1,0 tragen 59 Einträge, der erste steht an Listenposition 894 von 1036) — nach dem Umzug gewinnt über `ORDER BY salienz_decay DESC` der jüngste überhaupt, weil der Verfall `salienz_decay` zur Umkehrfunktion des Alters macht. Aus FIFO wird LIFO, ohne dass eine Zeile es ankündigt, und für die periodischen Aufgaben ist dieselbe Frage ausdrücklich anders entschieden. **Die Reaktivierung stellt die Existenz wieder her, nicht die Chance:** 0,638 gegen 0,976 der Neuzugänge. **Der Lebenszyklus hat kein Ende** — es wird nichts mehr gelöscht, die Tabelle wächst monoton. **Was die Prüfung stützt:** Die Altersverteilung dünnt zu den alten Tagen hin nicht aus (57 Aufträge vom ältesten Tag liegen unberührt), der Abfluss ist also so klein, dass die Reihenfolge heute kaum zählt — die Umkehrung wird erst wichtig, wenn der Engpass am einen seriellen Platz fällt, und dann ist sie eingebaut und unbenannt.
- **v0.1 — 15.08.26:** Erstfassung. Entstanden aus dem Backlog-Eintrag `QUEUE-VERFALL-KONZEPT`, der ein eigenes Dokument verlangte — **die Suche nach dem Gegenstand fand `novaberg-autonomous-wissen_k.md` §11.6/§11.7**, wo dieselbe Bauart für Stapel und Bibliothek bereits steht. Dieses Dokument ist deshalb die Übertragung auf einen dritten Speicher und verweist, wo das Schwesterdokument trägt. Entschieden: **Soft-Delete statt hartem Löschen**, Reaktivierung auf 50 % des Bandes über der Schwelle nach `novaberg-memory-synapsen_k.md` §9.3, Frist **30 Tage**, Schwelle **0,3**. Daraus die Rate **λ = 0,0393/Tag**, gerechnet aus dem gemessenen Median 0,9764 — 26-mal die LZG-Rate. **Die Skala ist 1,0 und nicht die 10,0 des Schwesterdokuments**, weil die Queue Salienz führt; auf Cap 10 wäre die Schwelle 3 % und der Verfall liefe still ins Leere. **Die Queue zieht nach PostgreSQL um, der Stapel nicht** — gemessen: Die Queue wird alle 30 bis 120 s gelesen, der Stapel alle 5 s je Client, und die Postgres-Zugriffe dieses Projekts öffnen je Aufruf eine eigene Verbindung. Das Schema bildet jedes heutige JSON-Feld auf eine Spalte ab, einschließlich des bis dahin undokumentierten `_retries`; neu sind das Paar-Tripel und die Verfallsfelder. Die 233 Aufträge auf Salienz 0,0 fallen beim ersten Lauf heraus — vorher aufgeschrieben, damit es niemand für einen Unfall hält, und dank Soft-Delete rückholbar. Offen und als Absichtsfrage benannt: die 383 verwaisten `vertiefen`-Aufträge, für die der Verfall ein Ventil ist und kein Fix.
