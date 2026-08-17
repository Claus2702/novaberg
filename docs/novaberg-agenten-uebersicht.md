# Novaberg — Übersicht: der Stand aller Dienste

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Überblick — welche Dienste es gibt, wie sie erreicht werden, und wie weit sie der NMCP-Konvention entsprechen
**Stand:** 17. August 2026
**Pfad:** novaberg/docs/novaberg-agenten-uebersicht.md
**Typ:** Überblick (Zustandsdokument)
**Regelwerk:** `novaberg-convention-nmcp.md` · `novaberg-convention-planner-needs.md`

> **Dieses Dokument ist ein Zustandsbericht, kein Regelwerk.** Jede Zahl darin ist am 17.08.2026 am laufenden Bestand erhoben und am Tag danach möglicherweise falsch. Die Regeln stehen in der NMCP-Konvention; hier steht, wie weit der Bestand ihnen entspricht.
>
> **Erhebbar statt erinnerbar:** Die Tabelle in §3 entsteht aus einem Lauf über die Registry. Wer sie nachrechnen will, liest Aushang, Negativfälle, Grenze, Quote, Bedarf und Ausgänge je Dienst aus der Registry und meldet jeden über `anmelden()` an.

---

## 1. Drei Ebenen, und sie werden leicht verwechselt

Die Namen, die im Gespräch fallen — *Fakten*, *Notizen*, *Gedächtnis*, *Dateien* — liegen **nicht** auf derselben Ebene. Das ist der häufigste Irrtum bei der Einschätzung des Systems, weil alle vier wie Bausteine derselben Art klingen.

| Ebene | Was sie ist | Wird sie gewählt? | Hat sie vier Ausgänge? |
|---|---|---|---|
| **Dienst** (Agent) | ein Subgraph mit eigener Pipeline und eigenem Zustand | ja, über seinen Aushang — **oder** über Zeitplan/Queue | kann sie haben |
| **Anbieter** (Manager) | ein Aushang plus ein Schreib- oder Lesepfad, ohne Subgraph | ja, über seinen Aushang | **nein**, konstruktiv nicht |
| **Werkzeug** | eine Funktion, die ein Dienst aufruft | nein, nie | nein |

**Ein Anbieter ohne Dienst kann nicht begründet ablehnen.** Er hat keine Pipeline, in der ein Urteil entstehen könnte. Deshalb bekommt er die Zweifelsregel ausdrücklich zurückgenommen (`novaberg-convention-nmcp.md` §5.8): Ihm wird nur zugestellt, wenn der Aushang klar passt.

### 1.1 Die vier Namen, eingeordnet

| Name | Ebene | Stand am 17.08.2026 |
|---|---|---|
| **Fakten** | Anbieter, **kein Dienst** | Aushang 346 Zeichen, über den Empfang erreichbar. Keine vier Ausgänge, keine Semantik-Prüfung, keine Rücknahme — er führt aus, was ihn erreicht |
| **Notizen** | Dienst **und** Anbieter | vollständig umgestellt: Aushang, 3 Negativfälle, 3 Grenzen, Quote 25 %, vierter Ausgang |
| **Gedächtnis** | **kein einzelner Baustein** — vier Schichten auf drei Ebenen, siehe §4 | teils Dienst, teils Anbieter, teils reiner Lesepfad |
| **Dateien** | **Werkzeug** (`tools/dateien/`) | kein Dienst, kein Anbieter, über den Empfang **nicht erreichbar**. Nur `schreiben.py` gebaut; der Lesepfad fehlt |

> **Dass *Dateien* kein Dienst ist, erklärt eine Beobachtung im Betrieb:** Eine Bitte, etwas in eine Datei zu schreiben, erreicht keinen Dienst und erzeugt keinen Fehler. Es gibt niemanden, der sie ablehnen könnte — es gibt niemanden.

---

## 2. Was „umgestellt" heißt

Ein Dienst entspricht der NMCP-Konvention, wenn er sechs Angaben trägt und vier Ausgänge bedient:

| Angabe | Frage des Aufrufers | Pflicht für wen |
|---|---|---|
| **Aushang** | Woran erkenne ich, dass ich dich brauche? | nur Dienste am Empfang |
| **Negativfälle** | Wen schicke ich dir ausdrücklich nicht? | nur Dienste am Empfang |
| **Grenze** | Was tust du ausdrücklich nicht? | alle |
| **Quote** | In welchem Anteil der Äußerungen kommst du vor? | nur Dienste am Empfang |
| **Bedarf** | Welchen Zustand brauchst du? | alle, leer ist zulässig |
| **Ausgänge** | Bedienst du auch die begründete Ablehnung? | alle |

**Ein Dienst, der nicht über den Empfang läuft, braucht Aushang, Negativfälle und Quote nicht.** Er wird nicht gewählt — von ihm eine Erkennungsregel zu verlangen wäre eine Forderung ohne Gegenstand.

---

## 3. Der Stand der vierzehn Dienste

**Erhoben am 17.08.2026 am laufenden Bestand.** `Aus` = Aushang vorhanden, `Neg`/`Grz`/`Bed` = Anzahl der Einträge, `4.Ausg` = bedient die begründete Ablehnung.

| Dienst | Zustellart | Aus | Neg | Grz | Quote | Bed | 4.Ausg | Grad |
|---|---|---|---|---|---|---|---|---|
| **charakter_identitaet** | Empfang | ✅ | 3 | 3 | 0 % | 0 | ✅ | **vollständig** |
| **direktiven** | Empfang | ✅ | 3 | 3 | 0 % | 0 | ✅ | **vollständig** |
| **notizen** | Empfang | ✅ | 3 | 3 | 25 % | 0 | ✅ | **vollständig** |
| **timeline** | Empfang | ✅ | 3 | 3 | 25 % | 0 | ✅ | **vollständig** |
| kzg | Queue | — | 0 | 0 | — | **1** | ❌ | eingeschränkt |
| delegation | Queue | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| nachfragen | Queue | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| recherche | Queue | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| charakter | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| synapsen_decay | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| synapsen_promotion | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| wiedervorlage | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| wissensluecken | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |
| ziel_decay | Zeitplan | — | 0 | 0 | — | 0 | ❌ | eingeschränkt |

**Vier von vierzehn sind vollständig, und es sind genau die vier am Empfang.** Kein Dienst ist verweigert; alle vierzehn sind eingebunden.

### 3.1 Was „eingeschränkt" bei den zehn wirklich bedeutet — und wo die Angabe irreführt

Bei allen zehn steht genau **ein** Mangel: der fehlende vierte Ausgang. Aushang, Negativfälle und Quote werden von ihnen nicht verlangt (§2).

> **Die praktische Folge der Einschränkung ist bei ihnen leer.** „Eingeschränkt" heißt nach der Konvention: *bekommt keine Zweifelsfälle*. Ein Dienst, der über Zeitplan oder Queue läuft, bekommt aber überhaupt keine Zustellentscheidung — es gibt keinen Zweifelsfall, der ihm entgehen könnte.

**Damit ist der Grad für Hintergrunddienste eine Aussage ohne Wirkung, und das ist ein Mangel der Prüfung, nicht der Dienste.** Er steht hier statt in der Konvention, weil er erst beim Erheben dieser Tabelle sichtbar wurde. Was der vierte Ausgang ihnen trotzdem brächte: Ein Hintergrunddienst, der einen unsinnigen Auftrag bekommt, meldet heute `fehler` — eine Störung, um die sich der Betreiber kümmern soll. Ein Urteil wäre die richtigere Auskunft, und der Auftraggeber ist in diesem Fall der Zeitgeber oder die Queue.

### 3.2 Der einzige angemeldete Bedarf

`kzg` meldet `timeline_id` an — die ID eines im **selben** Durchlauf angelegten Timeline-Eintrags. Ohne diesen Wert legt der KZG-Schreibpfad einen zweiten Erinnerungs-Anker für denselben Tag an. Der Wert ist optional; sein Fehlen kostet eine Dublette und keinen Fehler.

**Seit dem 17.08.2026 wird der Zustand auf den angemeldeten Bedarf zugeschnitten.** Ein Clipboard-Wert, den ein Dienst nicht angemeldet hat, erreicht ihn nicht mehr und wird einzeln protokolliert.

---

## 4. Die vier Gedächtnisschichten und ihre Erreichbarkeit

*Gedächtnis* ist kein Baustein, sondern eine Menge von Schichten mit verschiedenen Zugängen. Das ist der Grund, warum eine Frage nach Erinnertem manchmal einen Dienst erreicht und manchmal nicht.

| Schicht | Wo | Wie sie erreicht wird | Über den Empfang wählbar |
|---|---|---|---|
| **Session** | Redis, `session:*:turns` | wird in jeden Prompt gelesen | nein — sie ist immer da |
| **Kurzzeit (KZG)** | Redis | Schreibpfad hängt am Dispatcher-Knoten, läuft in **jedem** Turn | nein — er wird nicht gewählt |
| **Langzeit (Synapsen)** | PostgreSQL, `lzg_knoten`/`lzg_kanten` | Lesepfad über den Enricher; Schreibpfad über `synapsen_promotion` (Zeitplan) | nein |
| **Bibliothek (`wissen`)** | PostgreSQL plus Dateien | **sechste Kontextquelle des Enrichers**, kein Dispatch-Ziel | nein — und das ist richtig |

> **`wissen` hat keinen Aushang, und das ist kein Defekt.** Der Manager ist ein Lesepfad des Enrichers, kein Ziel einer Zustellung. Die NMCP-Konvention nimmt den Lesepfad ausdrücklich aus (§11): Mehrere Lesequellen laufen parallel ohne Datenfluss untereinander; sie brauchen keine Vorbedingung, nur eine Quelle.

**Was daraus für die Einschätzung folgt:** Eine Frage nach Erinnertem wird **nicht** an einen Gedächtnis-Dienst zugestellt. Sie wird beantwortet aus dem, was der Enricher in den Prompt gelegt hat. Findet der Enricher nichts, sagt die Antwort *„ich weiß nichts davon"* — und das ist von einer richtigen Auskunft nicht zu unterscheiden. Nur die drei Fachgedächtnisse mit eigenem Dienst (`timeline`, `notizen`, `direktiven`) und der Anbieter `fakten` werden wirklich **gefragt**.

---

## 5. Die zwei Anbieter ohne Dienst

| Anbieter | Aushang | Lage |
|---|---|---|
| **fakten** | 346 Zeichen | über den Empfang erreichbar, **ohne** vier Ausgänge. Bekommt keine Zweifelsfälle; die Zweifelsregel ist an seinem Zettel zurückgenommen |
| **wissen** | keiner | kein Dispatch-Ziel, sondern Kontextquelle des Enrichers (§4) |

**`fakten` ist der Kandidat, an dem die nächste Umstellung am meisten brächte.** Er trägt das Faktengedächtnis, wird über den Empfang gewählt, und kann einen unsinnigen Auftrag weder prüfen noch begründet ablehnen — er führt ihn aus.

---

## 6. Wie das System einzuschätzen ist

Vier Sätze, jeder mit seiner Zahl:

**Die Anmeldung steht.** Vierzehn Dienste geprüft, vierzehn eingebunden, null verweigert. Der Handshake läuft bei jedem Start; eine fehlerhafte Anmeldung würde den Dienst ausschließen und nicht das System.

**Die Auswahl liest die Zettel der Dienste.** Fünf Aushänge stehen am Brett — vier von Diensten, einer vom Anbieter `fakten` —, dazu vier Negativblöcke und eine Rücknahme der Zweifelsregel.

**Die Ablehnung ist gebaut und wirkt.** Vier Dienste bedienen den vierten Ausgang; am 17.08.2026 hat er zweimal live gefeuert, und der Vorschlag erreichte den Antwortpfad.

**Und die Zustellentscheidung ist nicht stabil.** Dieselbe Klasse Frage wurde einmal zugestellt und einmal nicht. Solange das gilt, ist eine ausgebliebene Zustellung von einer richtigen Auskunft nicht zu unterscheiden — das ist die offene Schwäche des Systems, nicht die Anmeldung.

---

## 7. Was als Nächstes den größten Unterschied macht

Nach Wirkung geordnet, jede Zeile mit ihrer Begründung:

1. **Die Zustellquote messen, bis sie urteilt.** Der Abgleich braucht 30 Äußerungen für ein Fehlerurteil und 100 für eine Warnung; die Zähler werden bei jedem Neustart genullt. Solange sie das tun, bleibt die Instabilität aus §6 unbeziffert.
2. **`fakten` einen Dienst geben** oder ihn ausdrücklich als urteilslos führen. Heute führt er aus, was ihn erreicht.
3. **Den vierten Ausgang auf die Hintergrunddienste ausdehnen** — damit ein unsinniger Auftrag als Urteil statt als Störung erscheint.
4. **Die Unabhängigkeit der Zettel-Beurteilung prüfen** (`novaberg-convention-nmcp.md` §3.6a). Sie ist heute eine Anweisung im Prompt und keine Eigenschaft des Aufbaus.

---

## Versionshistorie

- **v0.1 — 17.08.2026:** Erstfassung, erhoben am laufenden Bestand nach der NMCP-Umstellung. Vier von vierzehn Diensten vollständig, alle vierzehn eingebunden, keiner verweigert. Neu benannt: die **drei Ebenen** Dienst/Anbieter/Werkzeug und die Einordnung von *Fakten*, *Notizen*, *Gedächtnis* und *Dateien*, die im Gespräch wie Bausteine derselben Art klingen und keine sind. Zwei Befunde sind beim Erheben entstanden: **der Grad „eingeschränkt" ist für Hintergrunddienste eine Aussage ohne Wirkung** (§3.1), und **eine Frage nach Erinnertem erreicht keinen Gedächtnis-Dienst** (§4) — sie wird aus dem beantwortet, was der Enricher gelegt hat, und ein leerer Fund ist von einer richtigen Auskunft nicht zu unterscheiden.
