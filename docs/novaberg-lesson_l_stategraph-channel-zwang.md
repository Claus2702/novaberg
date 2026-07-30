# Novaberg — Lesson: StateGraph-Channel-Zwang

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Bei `StateGraph(TypedDict)` ist das TypedDict die Verkabelung, nicht ein Typhinweis
**Stand:** 24. Juni 2026, Chat 100
**Pfad:** novaberg/docs/novaberg-lesson_l_stategraph-channel-zwang.md
**Kategorie:** Allgemein, nicht modul-bezogen — Grundlagen-Lesson für LangGraph-Datentransport
**Schwester-Lesson:** `novaberg-lesson_l_silent-skip.md` (stilles Verwerfen ohne Fehler)
**Bezug:** `novaberg-graph.md` (ConversationState als geteilte Datei / Clipboard-Prinzip)

---

## 1. Der Vorfall

Der Synapsen-Lesepfad P5 war fertig gebaut. Der Enricher holte über `spreading_lesen` die assoziativen Erinnerungen aus dem `lzg_knoten`-Netz, gewichtete sie, deduplizierte sie und schrieb das Ergebnis in den State: `state["lzg_resonanz"] = {...}`. Der Reducer sollte diesen Block an den Formatter reichen, der ihn als `[GEDAECHTNIS]`-Resonanz mit Spreading-Pfaden in den Responder-Prompt rendert.

Live tat sich nichts. Der `[GEDAECHTNIS]`-Block enthielt keine Resonanz. Nova „erinnerte sich" nicht an das, was das Spreading gefunden hatte — obwohl das Spreading nachweislich Treffer hatte. Das Log des Enrichers zeigte sauber `lzg_resonanz_count: 3`: drei Erinnerungen befüllt, Schalen traversiert, Pfade gebaut. Der Wert war da, einen Node früher. Beim Responder kam er als nichts an.

Das Tückische: Aus jeder Einzelperspektive funktionierte alles. Der Enricher schrieb korrekt. Der Reducer las korrekt. Der Formatter rendert korrekt, *wenn* er Daten bekommt. Es gab keine Exception, keinen Stacktrace, keine Warnung. Ein Wert, der in einem Node existierte, war im nächsten verschwunden — lautlos.

## 2. Die Ursache

Der Hauptgraph wird als `StateGraph(ConversationState)` instanziiert, wobei `ConversationState` ein TypedDict ist. Genau hier liegt der Denkfehler, der den Bug trägt: Ein TypedDict wirkt wie ein gewöhnlicher Typhinweis — eine Annotation, die zur Laufzeit folgenlos ist, weil Python TypedDicts nicht erzwingt. Bei LangGraph ist das TypedDict aber **keine Annotation, sondern die Definition der Channels**. Jeder Schlüssel im TypedDict ist ein Kanal, durch den Daten von Node zu Node fließen dürfen. Was nicht als Schlüssel deklariert ist, ist kein Kanal.

LangGraph reicht den State nicht als ein gemeinsames, mutierbares Objekt durch die Kette. Es **rekonstruiert** den State vor jedem Node aus den deklarierten Channels. Ein Node bekommt einen frisch zusammengesetzten State, der ausschließlich die Channel-Schlüssel enthält; sein Rückgabewert wird kanalweise zurückgeschrieben — wieder nur für deklarierte Channels.

`lzg_resonanz` war nie im `ConversationState`-TypedDict deklariert. Der Enricher konnte den Schlüssel per In-place-Mutation auf sein lokales State-Objekt setzen und dieses zurückgeben — der Code lief fehlerfrei. Aber beim Übergang Enricher→Reducer baute LangGraph den State neu aus den Channels zusammen, und `lzg_resonanz` war keiner. Der Schlüssel fiel an der Naht heraus. Der Reducer rief `state.get("lzg_resonanz")` und bekam `None` — nicht weil der Enricher nichts geschrieben hätte, sondern weil das Geschriebene den Node-Übergang nicht überlebte.

```python
# Enricher: schreibt, gibt State zurück — sieht nach Durchreichung aus
state["lzg_resonanz"] = {"erinnerungen": [...], "count": 3}
return state

# Reducer, ein Node später: liest None
resonanz = state.get("lzg_resonanz")   # -> None, der Channel existierte nie
```

In-place-Mutation plus `return state` **täuscht eine Durchreichung vor, die nicht stattfindet.** Der Schreibvorgang ist echt, das lokale Objekt trägt den Wert — aber das lokale Objekt ist nicht der Transport. Der Transport sind die Channels, und durch einen nicht deklarierten Channel fließt nichts.

## 3. Die Diagnose

Der Bug wurde nicht durch Code-Lesung gefunden. Er konnte es nicht werden.

Drei isolierte Code-Audits liefen über den Pfad — Producer, Consumer, Kette. Jedes bestätigte sein Stück: Der Enricher schreibt korrekt (Audit 1). Der Reducer liest und reicht korrekt durch (Audit 2). Die Kette Enricher→Reducer→Formatter ist topologisch intakt (Audit 3). Alle drei hatten recht. Keines fand den Fehler, weil der Fehler in keinem der drei Stücke saß — er saß in der **Naht** zwischen ihnen, an der Stelle, die kein Audit ansah, weil sie nicht im Code steht, sondern im Framework-Verhalten.

Gefunden wurde es erst durch eine **Messung an der Naht**: eine einzige Debug-Log-Zeile im Reducer, direkt nach dem `state.get("lzg_resonanz")`, die den Typ des gelesenen Werts ausgab. Das Log sagte `typ=NoneType`. Der Enricher loggte einen Zeile vorher `lzg_resonanz_count: 3`. Zwischen diesen beiden Log-Zeilen lag der Node-Übergang, und genau dort verschwand der Wert. Die Differenz war nicht im Code sichtbar, nur in der Live-Messung an der Übergangsstelle.

Das ist die eigentliche Diagnose-Lehre: Die isolierte Betrachtung der Enden war erschöpfend und ergebnislos. Erst die Beobachtung am Übergang — nicht am Producer, nicht am Consumer, sondern an der Stelle dazwischen — machte den Defekt sichtbar.

## 4. Die Behebung

Der Fix war eine Zeile: `lzg_resonanz` als Channel im `ConversationState`-TypedDict deklarieren.

```python
class ConversationState(TypedDict):
    ...
    lzg_resonanz: dict | None
```

Damit wurde aus dem nicht existierenden Channel ein echter. LangGraph trägt den Wert seither über den Node-Übergang, genau wie das benachbarte `memory_entries`. Live verifiziert: `erinnerungen=3` am Reducer, Resonanz-Block mit Spreading-Pfaden im Responder-Prompt (Commit `f14c8b4`, Bug `LZG-RESONANZ-STATE-DEKL`).

Kein Producer- und kein Consumer-Code wurde angefasst — sie waren immer korrekt. Der Fehler war nie in den Enden; er war im fehlenden Kanal.

## 5. Die falsche Vorannahme

In Chat 99 war dieser fehlende Channel bereits notiert worden — als Backlog-Punkt `LZG-RESONANZ-STATE-DEKL` mit der Einschätzung: *„Prio niedrig, `lzg_resonanz` ist nicht im TypedDict deklariert; läuft zur Laufzeit (TypedDict nicht runtime-enforced)."*

Diese Einschätzung war die eigentliche Falle. Sie stimmt für ein gewöhnliches Funktions-Dict: Da ist ein TypedDict tatsächlich nur ein Typhinweis, und ein nicht deklarierter Schlüssel funktioniert zur Laufzeit klaglos. Sie stimmt **nicht** für ein TypedDict, das als `StateGraph`-Schema dient. Dort ist die Deklaration keine Typ-Dokumentation, sondern die Verkabelung. „Läuft trotzdem zur Laufzeit" war exakt verkehrt — es lief eben nicht, der Wert wurde still verworfen.

Die Lehre: Der Satz „TypedDict ist nicht runtime-enforced" ist wahr und führt in die Irre, sobald das TypedDict ein Graph-Schema ist. Der Kontext ändert die Bedeutung derselben Konstruktion vollständig.

## 6. Die Prinzipien

### Prinzip 1 — Jeder Cross-Node-Key MUSS ein Channel sein

Jeder Wert, den eine Node an eine andere weitergeben muss, wird als Schlüssel im State-TypedDict deklariert. Bei `StateGraph(TypedDict)` ist das TypedDict die Channel-Definition. Was nicht deklariert ist, ist kein Transportweg — egal wie korrekt Producer und Consumer aussehen.

### Prinzip 2 — In-place-Mutation täuscht Durchreichung vor

`state["key"] = wert; return state` sieht aus wie Durchreichung, ist es aber nicht. LangGraph rekonstruiert den State pro Node aus den Channels; das lokale State-Objekt eines Nodes ist nicht der Transport. Der Schreibvorgang kann echt sein und der Wert trotzdem am Node-Übergang verschwinden. Man darf der Mutation nicht ansehen, ob sie ankommt — nur der Channel-Deklaration.

### Prinzip 3 — An der Naht messen, nicht die Enden erneut lesen

Wenn ein Wert zwischen zwei Nodes „verschwindet", obwohl Producer und Consumer beide korrekt aussehen: zuerst die Channel-Deklaration prüfen, dann an der Übergangsstelle messen. Eine Log-Zeile direkt nach dem `state.get` im Consumer, die Typ und Wert ausgibt, schlägt jede weitere isolierte Code-Lesung der Enden. Drei Audits der Enden fanden den Bug nicht; eine Messung an der Naht fand ihn sofort. Bugs, die in der Naht zwischen korrekten Stücken sitzen, sind nur durch Beobachtung am Übergang auffindbar.

### Prinzip 4 — Derselbe Konstrukt-Typ bedeutet je nach Kontext etwas anderes

Ein TypedDict als Funktions-Argument ist ein folgenloser Typhinweis. Dasselbe TypedDict als `StateGraph`-Schema ist die Laufzeit-Verkabelung. Eine Einschätzung, die für den einen Kontext stimmt („nicht runtime-enforced, läuft trotzdem"), kann für den anderen das Gegenteil bedeuten. Vor der Prio-Einstufung gilt: in welchem Kontext lebt diese Konstruktion?

## 7. Die Konsequenz

`LZG-RESONANZ-STATE-DEKL` wurde von „Prio niedrig" auf erledigt umgewertet — und der ursprüngliche Eintrag im Backlog ausdrücklich als widerlegt markiert, damit die falsche Einschätzung nicht ein zweites Mal als Beruhigung dient. Der Bug steht jetzt in `novaberg-bugs.md` als Wurzel des P5-Render-Ausfalls.

Für künftige State-Felder gilt die Reihenfolge: erst den Channel im `ConversationState`-TypedDict deklarieren, dann Producer und Consumer verdrahten. Ein neuer Cross-Node-Wert ohne Channel-Deklaration ist kein „läuft schon, Deklaration nachziehen"-Fall, sondern ein nicht verdrahteter Pfad, der stillschweigend nichts transportiert.

Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum in Novaberg jedes neue State-Feld zuerst als Channel deklariert wird, bevor irgendein Node es schreibt, liest hier nach.

## 8. Der Preis

Vergleichsweise milde: Der Defekt lebte nur die Spanne zwischen P5-Fertigstellung (Chat 99) und Live-Abnahme (Chat 100). P5 wurde in Chat 99 als „Lesepfad live" notiert, war es aber nicht — die Resonanz erreichte nie den Prompt, weil die Verkabelung an der letzten Naht fehlte. Die Abnahme in Chat 99 stützte sich auf Import-Smokes und Mock-Funktionstests, die die Naht nicht durchliefen; sie hätten den Bug strukturell nicht sehen können.

Der eigentliche Preis war Diagnose-Zeit: drei vollständige Code-Audits, die korrekt arbeiteten und trotzdem ins Leere liefen, weil sie das Falsche prüften — die Enden statt die Naht. Diese Stunden sind die Mahnung der Lesson: Bei einem Wert, der zwischen korrekten Nodes verschwindet, ist die erste Frage nicht „ist der Producer richtig?", sondern „ist der Channel deklariert?" — und die erste Handlung ist eine Messung am Übergang, nicht eine weitere Lesung der Enden.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lesson: `novaberg-lesson_l_silent-skip.md` (stilles Verwerfen ohne Fehler)
→ Bezug: `novaberg-graph.md` (ConversationState als geteilte Datei / Clipboard-Prinzip)
→ Bug: `novaberg-bugs.md` — `LZG-RESONANZ-STATE-DEKL`
