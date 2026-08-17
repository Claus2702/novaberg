# Novaberg — Der Dateien-Dienst: ein Verzeichnis, das gelesen werden darf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Indizierung und Durchsuchung eines vorgegebenen Verzeichnisses als NMCP-Dienst
**Stand:** 17. August 2026 (v0.1)
**Pfad:** novaberg/docs/novaberg-agent-dateien_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ **Konzept, kein Code.** Kein Bezeichner dieses Dokuments existiert.
**Voraussetzung:** `novaberg-tool-dateien_k.md` (die Operationen — teils gebaut) · `novaberg-convention-nmcp.md` (die Anmeldung) · `novaberg-convention-verfall.md` (warum hier kein Verfall)
**Abgrenzung:** `novaberg-autonomous-wissen_k.md` — die Bibliothek ist Novas **eigenes** Wissen und ein anderer Korpus, siehe §2

> **Zustandsteil, ausdrücklich getrennt.** Von diesem Konzept ist nichts gebaut. Was existiert: die Werkzeugschicht `tools/dateien/` mit `schreiben.py` (nur schreibend), die Bibliothek `autonomous_wissen` mit 463 Zeilen für Novas eigenes Wissen, und `such_vektor` im Zustandstyp. Der Wächter, die Indextabelle und der Dienst sind Entwurf.

---

## 1. Was gebaut werden soll, in einem Satz

> **Nova soll in einem vorgegebenen Verzeichnis Dateien finden und lesen können — nach Name, nach Thema und nach Inhalt — und dort nichts verändern dürfen.**

Der Zweck ist benannt und er ist der Grund für den Zuschnitt: Wer ihr die Projektdokumentation zugänglich macht, gibt ihr die Möglichkeit, **über sich selbst zu lernen**. Ein Dienst, der dabei schreiben könnte, wäre ein Dienst, der seine eigene Beschreibung ändern kann.

---

## 2. Zwei Korpora, und sie dürfen nicht in eine Tabelle

Es gibt schon eine Tabelle mit `dateipfad`, `thema`, `zusammenfassung` und `themen_embedding`: `autonomous_wissen`, 463 Zeilen. Sie sieht aus wie das Gesuchte und ist es nicht.

| | **Bibliothek** (`autonomous_wissen`) | **Index** (neu) |
|---|---|---|
| Inhalt | was Nova selbst erarbeitet hat | was jemand ins Verzeichnis gelegt hat |
| Wer schreibt die Datei | Nova | der Mensch |
| Wer schreibt die Zeile | Nova, beim Ablegen | der Wächter, beim Erkennen |
| Zugriff des Dienstes | lesend **und** schreibend | **nur lesend** |
| Verfall | ja — vier Spalten, mit Halbwertszeit | **nein** |
| Paar-Schema | ja (`user_id` × `character_id` × `beobachter`) | **nein**, siehe §2.2 |
| Verzeichnis | `knowledge/` | ein vorgegebenes, konfiguriertes |

### 2.1 Der Verzicht auf Verfall folgt aus der bestehenden Regel — er ist keine Ausnahme

Die Verfalls-Konvention trennt in einem Satz:

> **Was als Gedächtnis dient, verfällt. Was als Faktum protokolliert, bleibt.**

**Eine indizierte Datei ist das Zweite.** Der Indexeintrag behauptet nicht *„daran erinnert sich jemand"*, sondern *„diese Datei liegt dort und handelt davon"*. Das ist eine Tatsachenbehauptung über das Dateisystem. Sie wird nicht schwächer, wenn niemand sie liest; sie wird **falsch**, wenn die Datei sich ändert oder verschwindet — und dagegen wirkt kein Verfall, sondern der Wächter.

> **Deshalb wäre ein Gewicht auf dem Index nicht bloß überflüssig, sondern irreführend.** Eine Datei mit sinkendem Gewicht sähe aus wie eine, die an Bedeutung verliert, während sie unverändert dort liegt. Das ist derselbe Fehler wie ein Default im plausiblen Wertebereich: eine Zahl, die etwas behauptet, was niemand gemessen hat.

### 2.2 Kein Paar-Schema, und warum das keine Verletzung ist

Das Paar-Schema (`user_id` × `character_id` × `beobachter`) ist für die **Gedächtnisschichten** verbindlich — Kurzzeit, Langzeit, Charakter-Hash. Es trägt dort die Frage *„wessen Sicht ist das"*.

**Ein Index über ein Verzeichnis hat diese Frage nicht.** Eine Datei ist nicht die Erinnerung eines Menschen an etwas, sondern eine Datei. Sie hat keinen Beobachter.

**Was der Index stattdessen braucht, ist die Wurzel.** Jede Zeile trägt, aus welchem konfigurierten Verzeichnis sie stammt. Damit ist ein zweites Verzeichnis später ohne Migration hinzufügbar, und die Zugriffsfrage bleibt beantwortbar: nicht *„wem gehört die Erinnerung"*, sondern *„welche Wurzel darf dieser Dienst lesen"*.

---

## 3. Zwei Dienste, nicht einer

Der Wächter und das Lesen sind zwei Aufgaben mit verschiedenen Zustellarten. Ein Dienst, der beides tut, hätte eine Zustellart, die für die halbe Arbeit falsch ist.

| Dienst | Zustellart | Aufgabe | Lastart |
|---|---|---|---|
| **`dateien`** | Empfang | eine Frage beantworten: finden, lesen, Fundstellen liefern | LLM-Spur (Klassifikation der Anfrage) |
| **`dateien_index`** | Zeitplan | den Bestand gegen das Verzeichnis halten und Änderungen indizieren | Rechenspur — **außer** bei der Zusammenfassung, siehe §5.3 |

Das ist dieselbe Aufteilung wie bei `synapsen_promotion` und `synapsen_decay`: ein Dienst, der auf Anfrage arbeitet, und einer, der den Bestand pflegt.

> **Ein Befund über die Anmeldung selbst, aufgefallen beim Entwurf:** Die Zustellart ist heute einwertig und aus `graph_eignung` und `periodic_task()` abgeleitet. Ein Dienst, der **beides** legitim ist — auf Anfrage erreichbar und zusätzlich periodisch —, lässt sich damit nicht beschreiben. Die Aufteilung in zwei Dienste umgeht das hier; sie löst es nicht. Gehört in die Fundliste.

---

## 4. Die Indextabelle

**Ein Eintrag je Datei, nicht je Block.** Der Index ist die Karte, nicht der Inhalt — der Inhalt bleibt in der Datei und wird bei Bedarf gelesen (§6).

| Spalte | Zweck | Anmerkung |
|---|---|---|
| `id` | Schlüssel | |
| `wurzel` | aus welchem konfigurierten Verzeichnis | §2.2 |
| `pfad` | Pfad **relativ zur Wurzel** | absolut wäre ein Umgebungsdetail und nicht verschiebbar |
| `name` | Dateiname | für die Namenssuche, ohne Pfadzerlegung zur Abfragezeit |
| `thema` | ein Satz: worum es geht | vom Modell, beim Indizieren |
| `zusammenfassung` | wenige Sätze | vom Modell |
| `stichwoerter` | `text[]` | für die exakte Suche neben der semantischen |
| `themen_embedding` | `vector(768)` | über Thema + Stichwörter, **nicht** über den Volltext — §5.4 |
| `struktur` | `jsonb` — die Blockkarte | Ergebnis von `struktur_analysieren`, damit der Zoom ohne Dateizugriff beginnt |
| `groesse` | Bytes | |
| `zeilen` | Zeilenzahl | die Einheit, in der `datei_grep` antwortet |
| `inhalt_hash` | Prüfsumme des Inhalts | die Änderungserkennung, §5.2 |
| `geaendert_am` | mtime der Datei | |
| `indiziert_am` | wann diese Zeile entstand | |
| `aktiv` | ob die Datei noch existiert | Soft-Delete, §5.5 |
| `verschwunden_am` | wann sie zuletzt fehlte | |

**Keine Gewichts-, Häufigkeits- oder Verfallsspalte.** Das ist die Aussage aus §2.1 in Schemaform.

---

## 5. Der Wächter

### 5.1 Was er tut

Er läuft nach Zeitplan über die konfigurierten Wurzeln und bringt den Index auf den Stand des Verzeichnisses. Drei Fälle, drei Wege:

| Fall | Erkennung | Folge |
|---|---|---|
| **neu** | Pfad nicht im Index | vollständig indizieren |
| **geändert** | `inhalt_hash` weicht ab | neu indizieren, Zeile aktualisieren |
| **verschwunden** | Pfad im Index, Datei fehlt | `aktiv = false`, `verschwunden_am` setzen |

### 5.2 Die Änderungserkennung prüft den Inhalt, nicht die Zeit

**`mtime` allein reicht nicht, und `mtime` allein ist auch zu viel.** Zu wenig, weil ein Werkzeug eine Datei mit gleicher Zeit neu schreiben kann; zu viel, weil ein Kopiervorgang die Zeit ändert, ohne den Inhalt anzufassen — und eine Neu-Indizierung kostet einen Modellaufruf je Datei.

**Also: `mtime` als Vorfilter, `inhalt_hash` als Entscheidung.** Nur wenn der Hash abweicht, wird neu indiziert. Bei 667 Dateien im vorhandenen Verzeichnis ist der Unterschied zwischen „alle" und „die geänderten" die Frage, ob der Wächter Minuten oder Stunden läuft.

### 5.3 Die Lastart ist gemischt, und das muss die Anmeldung sagen

Das Durchlaufen des Verzeichnisses, das Hashen und `struktur_analysieren` sind Rechenarbeit. **Thema, Zusammenfassung und Stichwörter kommen von einem Modell.** Damit ist der Dienst in der LLM-Spur anzumelden — die Vorgabe ist ohnehin die langsame Spur, und sie ist hier die richtige.

> **Der Grund steht in der Anmelderegel:** Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums, nicht der Klasse. Ein Wächter, der sich für rechenfrei erklärt und ein Modell ruft, verstopft die schnelle Spur.

### 5.4 Das Embedding geht über die Metadaten, nicht über den Volltext

Eingebettet werden Thema und Stichwörter, nicht der Dateiinhalt. Drei Gründe, und der dritte ist der, an dem dieses Projekt bezahlt hat:

- Ein Volltext-Embedding über eine lange Datei mittelt alles zu einem Mittelwert und findet dann nichts genau.
- Der Inhalt ist über `datei_grep` erreichbar; dafür braucht er kein Embedding.
- **Das eingesetzte Einbettungsmodell muss vorher gegen den Korpus geprüft werden.** Ein Embedding, das den Bedeutungsträger nicht sieht, liefert eine Ähnlichkeit, die keine ist — und der Fehler zeigt sich nicht als Ausfall, sondern als schlechtes Ergebnis, das wie ein schlechter Korpus aussieht. Die Prüfung ist eine Zeile: zwei fachlich verschiedene Themen einbetten und den Kosinus ansehen.

### 5.5 Verschwundene Dateien werden markiert, nicht gelöscht

Die Zeile bleibt mit `aktiv = false`. Zwei Gründe: Eine Datei, die wieder auftaucht, ist als dieselbe erkennbar; und die Frage *„wo war das noch"* ist auch für eine entfernte Datei eine sinnvolle Frage, solange die Antwort sagt, dass sie weg ist.

---

## 6. Drei Stufen der Auffindbarkeit

Die Stufen sind die des vorhandenen Werkzeug-Konzepts, hier auf den Index gelegt. Jede Stufe kostet mehr als die vorige, und jede beantwortet eine andere Frage.

| Stufe | Frage | Weg | Kosten |
|---|---|---|---|
| **1 — Name** | *„gibt es eine Datei über X"* | `LIKE` auf `name`, plus `stichwoerter` | eine Abfrage |
| **2 — Thema** | *„was habe ich über X"* | Kosinus gegen `themen_embedding` | eine Abfrage |
| **3 — Inhalt** | *„wo steht dieser Satz"* | `datei_grep` über die Treffer aus 1 oder 2 | Dateizugriff je Treffer |

**Stufe 3 setzt Stufe 1 oder 2 voraus.** Ein `grep` über die ganze Wurzel ist kein Suchweg, sondern ein Vollscan; er wird erst brauchbar, wenn die Kandidatenmenge klein ist. Das ist derselbe Zoom wie im Werkzeug-Konzept — nur beginnt er hier im Index statt im Verzeichnis, und das erspart den ersten Dateizugriff.

**Die Blockkarte macht Stufe 3 gezielt.** `struktur` liegt im Index; der Dienst weiß also, welche Abschnitte eine Datei hat, bevor er sie öffnet, und kann `block_lesen` statt `datei_lesen` rufen.

---

## 7. Die Grenze wird erzwungen, nicht deklariert

Der heikelste Teil des Entwurfs, und er ist keine Frage der Anmeldung.

> **Der Dienst hat zwei Zonen mit verschiedenen Rechten, und die Trennung liegt im Code, nicht in einer Zusage.**

| Zone | Recht | Wer schreibt |
|---|---|---|
| die konfigurierten **Indexwurzeln** | **nur lesen** | niemand über diesen Dienst |
| `knowledge/` — **Novas eigenes** | lesen und schreiben | sie selbst, über die Bibliothek |

**Drei Regeln, alle prüfbar:**

1. **Jeder Pfad wird gegen seine Wurzel aufgelöst und geprüft**, nachdem Symlinks und `..` aufgelöst sind. Ein Pfad, der nach der Auflösung außerhalb liegt, wird abgewiesen und gemeldet — nicht zurechtgebogen.
2. **Der lesende Dienst hat keine Schreibfunktion.** Nicht „er benutzt sie nicht", sondern er importiert sie nicht. Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden.
3. **Die Wurzeln stehen in der Konfiguration, nicht im Auftrag.** Ein Verzeichnis, das aus einer Äußerung kommt, ist eine Äußerung — und die kommt von außen.

> **Warum das nicht in die Anmeldung gehört:** Die Anmeldung sagt, was ein Dienst zu tun *verspricht*. Bei einem Dienst mit Dateizugriff ist das zu wenig — was er verspricht und was er kann, müssen zwei verschiedene Prüfungen sein. Die Anmeldung nennt die Grenze, damit der Aufrufer sie kennt; der Code hält sie, damit sie gilt.

---

## 8. Die Anmeldung — der erste Dienst, der von Anfang an unter NMCP entsteht

Alle bisherigen Dienste wurden nachträglich angemeldet. Dieser ist der erste, dessen Anmeldung vor dem Code steht — und damit die erste Probe darauf, ob die Konvention beim Entwerfen trägt.

### 8.1 `dateien` — der lesende Dienst am Empfang

| Angabe | Wert |
|---|---|
| **Aushang** | Die Äußerung fragt nach etwas, das in **Unterlagen** stehen könnte: nach einem Dokument, einer Datei, einer Stelle darin, oder nach einem Thema mit dem Zusatz *„steht das irgendwo"*, *„such mal in"*, *„was haben wir zu"*. Entscheidend ist nicht die Satzform, sondern der Bezug auf einen **abgelegten Text** statt auf eine Erinnerung. |
| **Negativfälle** | eine Frage nach Weltwissen ohne Bezug auf Unterlagen (*„wie funktioniert Photosynthese"*) — das ist Wissen, keine Fundstelle · eine Frage nach etwas Erlebtem (*„was habe ich dir letzte Woche erzählt"*) — das ist Gedächtnis, keine Datei · die Bitte, etwas **abzulegen** — dieser Dienst schreibt nicht |
| **Grenze** | schreibt nichts, in keiner Zone · liefert keine Zusammenfassung ganzer Verzeichnisse · sucht nicht im Inhalt ohne vorherige Einschränkung (§6) · kennt nur die konfigurierten Wurzeln |
| **Kosten** | LLM-Spur — die Anfrage wird klassifiziert |
| **Kadenz** | keine, er wartet |
| **Geltungsbereich** | `user` und `pixie` — auch ein eigener Gedanke darf in Unterlagen nachsehen |
| **Datenhoheit** | liest Dateien, **kein** Gedächtnis. Rührt weder KZG noch LZG an |
| **Bedarf** | `such_vektor` — der Vektor, mit dem in diesem Turn auch die Gedächtnisschichten gesucht haben. **Ein eigenes Embedding zu rechnen hieße, denselben Text ein zweites Mal einzubetten** und dabei die Wahrnehmungs-Gravitation zu verlieren; der Wert ist im Zustandstyp vorhanden und muss dafür in den Zusagenkatalog aufgenommen werden |
| **Quote** | **0 %** — eine Ausnahme. Begründung: Bis der Mensch Verzeichnisse einlegt, kommt der Fall selten vor. Die Angabe ist eine Schätzung und soll widerlegt werden; genau dafür steht sie da |
| **Wiederholverhalten** | idempotent — eine Suche ändert nichts |
| **Ausgänge** | alle vier |

### 8.2 Der vierte Ausgang ist hier besonders brauchbar

Eine Suche, die nichts findet, hat fast immer einen benachbarten Treffer. Die Ablehnung trägt ihn:

| Befund | Beleg | Vorschlag |
|---|---|---|
| *„Unter diesem Namen liegt nichts."* | *„12 Dateien in der Wurzel, keine mit `X` im Namen."* | *„Unter dem Thema gibt es drei — soll ich die durchsehen?"* |
| *„Der Satz steht in keiner der drei Dateien."* | *„3 Kandidaten, 0 Treffer für `X`."* | *„Ohne Anführungszeichen gesucht ergibt es 7 Treffer."* |

**Das ist der Unterschied zwischen einer Suche und einer Auskunft.** Ein blankes *„nichts gefunden"* ist genau die Sackgasse, die die Konvention benennt — und bei einer Dateisuche ist sie besonders teuer, weil der Mensch nicht weiß, ob die Datei fehlt oder die Frage.

### 8.3 `dateien_index` — der Wächter am Zeitplan

| Angabe | Wert |
|---|---|
| **Zustellart** | Zeitplan, kein Aushang |
| **Grenze** | indiziert nur die konfigurierten Wurzeln · löscht keine Datei · ändert keine Datei |
| **Kosten** | LLM-Spur (§5.3) |
| **Kadenz** | periodisch; der Takt folgt der Änderungsrate des Verzeichnisses und nicht dem Gefühl |
| **Datenhoheit** | schreibt ausschließlich in die Indextabelle |
| **Wiederholverhalten** | idempotent über `inhalt_hash` — ein zweiter Lauf über unveränderte Dateien erzeugt keinen zweiten Effekt und keinen Modellaufruf |
| **Ausgänge** | alle vier; die Ablehnung trägt den Fall *„Wurzel nicht lesbar"* mit dem Pfad als Beleg |

---

## 9. Was zu entscheiden ist, bevor gebaut wird

Vier Fragen, die der Entwurf offenlässt, weil sie Absichten sind und keine Umsetzungsdetails:

1. **Welche Wurzel zuerst?** Die Projektdokumentation ist der genannte Zweck. Sie ist zugleich der Korpus, in dem Nova über sich selbst liest — was eine eigene Frage aufwirft (§10).
2. **Sieht jedes Paar denselben Index?** Der Entwurf sagt: ja, ein Index je Wurzel, kein Paar-Bezug. Bei mehreren Menschen am selben System ist das eine Zugriffsentscheidung und keine Schemafrage.
3. **Wie tief darf `datei_grep` gehen?** Eine Obergrenze für Treffer und Dateien ist nötig; ohne sie ist eine unglückliche Anfrage ein Vollscan.
4. **Was passiert bei einer Datei, die kein Text ist?** PDF, Bild, Tabelle. Der Entwurf behandelt Text; alles andere wird erkannt und mit Grund übergangen, nicht stillschweigend.

---

## 10. Der Sonderfall, der beim Zweck mitkommt

Der genannte Zweck ist, Nova die Dokumentation zugänglich zu machen, damit sie **über sich selbst lernen** kann. Das ist mehr als ein weiterer Korpus, und es gehört benannt:

> **Ein System, das seine eigene Beschreibung liest, kann ihr widersprechen.** Die Dokumentation enthält Sätze über Novas Aufbau, ihre Konzepte und ihre offenen Defekte. Liest sie das, kann sie über sich Aussagen machen, die aus dem Dokument stammen und nicht aus ihrem Zustand — und die beiden sind in einer Antwort nicht mehr auseinanderzuhalten.

Zwei Folgen, beide klein und beide nötig:

- **Eine Fundstelle wird als Fundstelle ausgewiesen.** Was aus einer Datei kommt, trägt Datei und Zeile — nicht, damit es zitierfähig ist, sondern damit *„das steht so im Konzept"* von *„so bin ich"* unterscheidbar bleibt.
- **Ein Konzept ist kein Beleg dafür, dass etwas existiert.** Der Satz gilt für jeden Leser der Dokumentation, und er gilt für sie genauso. Ein Dienst, der Konzepte liest, muss damit rechnen, Beschreibungen von Dingen zu finden, die nicht gebaut sind.

---

## Versionshistorie

- **v0.1 — 17.08.2026:** Erstfassung. **Zwei Korpora statt einem:** `autonomous_wissen` trägt Novas eigenes Wissen samt Verfall und Paar-Schema und ist für einen Verzeichnis-Index die falsche Tabelle. **Der Verzicht auf Verfall ist keine Ausnahme, sondern die Anwendung der bestehenden Regel** — ein Indexeintrag ist eine Tatsachenbehauptung über das Dateisystem und kein Gedächtnis; ein Gewicht darauf wäre irreführend statt überflüssig. **Kein Paar-Schema, dafür eine Wurzel** — eine Datei hat keinen Beobachter. **Zwei Dienste**, weil Wächter und Lesen verschiedene Zustellarten haben; dabei fiel ein Befund über die Anmeldung selbst an: Die Zustellart ist einwertig und kann einen Dienst nicht beschreiben, der auf Anfrage **und** periodisch arbeitet (§3). **Die Grenze zwischen lesender und schreibender Zone liegt im Code, nicht in der Anmeldung** — was ein Dienst verspricht und was er kann, sind zwei Prüfungen (§7). Der erste Dienst, dessen Anmeldung vor dem Code steht.
