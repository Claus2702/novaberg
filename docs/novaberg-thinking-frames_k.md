# Novaberg — Frames (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Frames — Strukturelle Wissens-Erhebung für Vorhaben und Ereignisse (Konzept)
**Stand:** 08. Mai 2026, Chat 80
**Pfad:** novaberg/docs/novaberg-thinking-frames_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 80 (gesamte Konzeption — entstanden aus NotizenAgent-Audit zur Bezugsauflösung, weitergedacht zum Slot-Filling-Pattern)

---

## 1. Vision

Wenn der Nutzer sagt *"Am Freitag habe ich einen Zahnarzttermin"*, soll Nova nicht nur einen Eintrag mit `title="Zahnarzttermin"` und `event_time=Freitag` anlegen. Sie soll erkennen, dass ein Termin **strukturell vier Aspekte** hat — wer, wo, wann, was — und mit den Lücken bewusst umgehen: rekonstruieren, nachfragen oder akzeptieren.

Statt einer flachen Erinnerung entsteht ein vollständiges Wissensobjekt:

> *"Meister hat am Freitag einen Termin beim Zahnarzt in Treuchtlingen, voraussichtlich zur Zahnreinigung."*

Diese Vollständigkeit hat zwei Konsequenzen:

1. **Der Termin wird anschlussfähig.** Wenn Nova später nach *"Zahnarzt"* oder *"Treuchtlingen"* gefragt wird, findet sie den Eintrag über mehrere Magnet-Achsen, nicht nur über den rohen Titel-Text.
2. **Der Termin wird zu strukturiertem Wissen.** Die Slots speisen das Faktengedächtnis, das wiederum bei zukünftigen Termin-Anlagen als Vor-Erfahrung dient. *"Du gehst beim Zahnarzt seit drei Jahren nach Treuchtlingen"* — Nova kann das Vor-Wissen aktivieren, weil es als Tripel im Knowledge Graph liegt.

> **Leitmetapher:** Ein guter Butler hört nicht nur, was sein Herr sagt, sondern weiß, was zu einem Anliegen dazugehört. *"Sir wünscht morgen ein Treffen — selbstverständlich. Mit wem darf ich rechnen, im Kaminzimmer wie üblich?"* — Der Butler füllt die offenen Punkte mit Vor-Wissen und fragt nur, was wirklich offen ist.

**Designziel:** Nova soll nicht nur Termine *speichern*, sondern Vorhaben *verstehen* — als strukturierte Frames, die mit dem Weltwissen verzahnt sind.

---

## 2. Kognitionswissenschaftliche Grundlage

### 2.1 Frame Semantics (Fillmore, 1976)

Charles Fillmore beschrieb in den 1970ern, dass Bedeutung nicht aus isolierten Wörtern entsteht, sondern aus **Frames** — schematischen Wissensstrukturen, die zu einem Begriff dazugehören. Wer das Wort *"Termin"* hört, aktiviert automatisch ein Frame mit Slots wie Teilnehmer, Ort, Zeit, Anlass — auch wenn nicht alle erwähnt werden. Das Verstehen passiert im Kopf des Hörers, nicht im Text.

**Implikation für Nova:** Wenn das LLM den Begriff *"Termin"* erkennt, hat es das Frame implizit verfügbar. Wir müssen es nicht definieren, sondern nur abfragen.

### 2.2 Slot Filling und Frame-Based Dialogue Management

Die Dialog-Systeme der späten 1990er und frühen 2000er (DARPA Communicator, TRIPS, RavenClaw) basierten auf **Slot-Filling**: Der Nutzer hat ein Vorhaben (Flug buchen, Termin planen), das System kennt die Slots, die das Vorhaben braucht, und fragt sie strukturiert ab. Damals starr und mit Decision-Trees gebaut, weil die Sprachverarbeitung roh war.

Mit modernen LLMs lebt das Pattern wieder auf — flexibler, weil das Verständnis kein Decision-Tree mehr ist. Was bleibt: die Disziplin der Slot-Klärung als Grundlage für sinnvolle Aktion.

**Implikation für Nova:** Slot-Filling ist eine bewährte Disziplin, kein neues Experiment. Was neu ist: Die Schemas leben im LLM-Wissen, nicht im Code.

### 2.3 Schema-Gedächtnis (Bartlett, 1932)

Frederic Bartlett zeigte, dass Erinnerungen nicht als Pixel-genaue Reproduktionen gespeichert werden, sondern als **Schemata** — Gerüste, die beim Abrufen mit Details rekonstruiert werden. Wer eine Geschichte nacherzählt, füllt schematische Lücken mit Plausiblem aus dem eigenen Wissen.

**Implikation für Nova:** Der Frame-Auflöser, der fehlende Slots aus Vor-Wissen rekonstruiert, ist kein Hack — er bildet eine kognitive Grundoperation nach. *"Wo war der Zahnarzt? Wahrscheinlich Treuchtlingen, da warst du immer."*

### 2.4 Interface vs. Referenz — die strukturelle Türschwelle

Diese Unterscheidung ist Novabergs eigene und entstand parallel zum Substanz-Filter aus der Magneten-Convention §7. Ein Wort kann **interface-haft** verwendet sein (beiläufig, ohne Vorhaben-Charakter) oder **referenziell** (mit konkretem Bezug auf eine Sache, die strukturierbar ist):

| Aussage | Klasse |
|---|---|
| *"Ich kaufe morgen Fleisch"* | Interface — beiläufige Erwähnung |
| *"Ich gehe morgen Einkaufen und besorge Fleisch"* | Referenz — Vorhaben mit Vorbereitungs-Verben |
| *"Anna ist nett heute"* | Interface — Eindruck |
| *"Anna wohnt in München"* | Referenz — Aussage über Welt |

Nur Referenzen erzeugen Frames. Interfaces bleiben im KZG mit Themen-Magneten, ohne Frame-Aufbau.

---

## 3. Kernidee — Frames als Weltwissen, zentrales Lager als Konsens

### 3.1 Doppelte Bewegung

Frames werden in Novaberg **nicht als Schema-Definitionen im Code** gehalten. Sie sind Weltwissen, das das LLM bereits hat. *"Termin hat wer/wo/wann/was"* steht in jedem hinreichend trainierten Modell, weil Menschen so denken.

Dafür gibt es ein **zentrales Lager**, das die LLM-erhobenen Frames sammelt und einen **gelernten Konsens** aufbaut. Das Lager ist nicht autoritativ — es zwingt keine Schemas auf — sondern dient als **Konsistenz-Hilfe** und **Vor-Erfahrungs-Speicher**.

### 3.2 Warum das eleganter ist als hardcoded Schemas

| Vergleich | Hardcoded Schema | LLM-Wissen + zentrales Lager |
|---|---|---|
| Neue Frame-Art (z.B. "Werkstatt-Termin") | Code-Änderung nötig | Funktioniert sofort |
| Frame-Variante (z.B. "Online-Termin ohne Ort") | Schema-Erweiterung | Frame hat Slot `wo=null`, ist OK |
| Domänen-spezifisches Wissen ("Zahnarzt-Termine in Treuchtlingen") | Schwer abzubilden | Aus dem Lager: "Du warst da bisher in Treuchtlingen" |
| Falsche Slot-Bewertung | Hartnäckig | Selbst-korrigierend, wenn 100 Termine nie `wo` haben |

**Bonus:** Das Lager **lernt mit**. Nach 50 Terminen weiß es: typische Termin-Slots sind wer/wo/wann/was. Nach 30 Reisen: wer/wo/wann/was/wie-lang. Es ist ein **emergentes Schema-Gedächtnis**, kein deklariertes.

### 3.3 Verwandtschaft zum Knowledge Graph

Das Frame-Lager ist konzeptuell ein **leichtgewichtiger Knowledge Graph für Frame-Schemas selbst**. Schemas sind Wissen, lebendig, verändern sich. Sie liegen in derselben Architektur-Familie wie Entitäten und Fakten — nur eine Ebene meta.

Konkret: Ein Frame-Eintrag ist eine `(art, slot-belegungen, häufigkeit, zuletzt_gesehen)`-Tupel. Das ähnelt der bi-temporalen Fakten-Struktur, ist aber in Schwere und Strenge reduziert.

---

## 4. Interface vs. Referenz — Der Türsteher

### 4.1 Linguistische Marker

Die Klassifikation ist eine LLM-Aufgabe, aber sie hat klare Indikatoren, die der Classify-Prompt explizit benennen sollte:

**Referenz-Marker:**
- **Substantive für Vorhaben:** "Termin", "Einkauf", "Reise", "Treffen", "Besorgung", "Vortrag"
- **Verben mit Vorbereitungs-Charakter:** "gehen + besorgen", "fahren + holen", "treffen mit X"
- **Konkrete Anlass-Marker:** "wegen", "zum", "für"
- **Zeitliche Konkretisierung:** "morgen um 10", "am Freitag", "nächste Woche"

**Interface-Marker:**
- **Beiläufige Verben:** "kaufen", "essen", "haben", "machen"
- **Generische Objekte:** "Fleisch" statt "Steak vom Metzger"
- **Vergangenheit / hypothetisch / wertend:** "war", "wäre", "fühlt sich"
- **Beobachtungen ohne Akteur-Absicht:** "Wetter ist schön"

### 4.2 Beispiele in voller Breite

| Aussage | Klasse | Frame? | Was passiert |
|---|---|:---:|---|
| *"Ich kaufe morgen Fleisch"* | Interface | nein | KZG-Eintrag mit Themen `["einkaufen","fleisch"]` |
| *"Ich gehe morgen Einkaufen und besorge Fleisch"* | Referenz | ja | Frame `einkauf` mit `wann=morgen, was=Fleisch, wo=?` |
| *"Am Freitag habe ich einen Zahnarzttermin"* | Referenz | ja | Frame `termin` mit `wann=Freitag, was=Zahnarzt, wo=?, wer=Meister` |
| *"Ich war heute beim Bäcker"* | Interface | nein | KZG mit Entität "Bäcker" |
| *"Anna ist nett heute"* | Interface | nein | KZG mit Entität "Anna" |
| *"Anna wohnt in München"* | Referenz | (Fakt direkt) | Tripel `(Anna, WOHNT_IN, München)` ohne Frame-Pfad |
| *"Ich möchte morgen Schuhe kaufen"* | Referenz schwach | ja | Frame `einkauf` mit `wann=morgen, was=Schuhe, wo=?, wer=Meister` |

Aussagen wie *"Anna wohnt in München"* sind Welt-Aussagen ohne Vorhaben-Charakter — sie gehen direkt ins Faktengedächtnis, ohne durch das Frame-System zu laufen. Das Frame-System ist für **Vorhaben und Ereignisse mit Slot-Struktur**, nicht für jede strukturierte Aussage.

### 4.3 Bedeutung für die Pipeline

Der Classify-Node entscheidet pro Prompt: *"Ist das eine Referenz mit Frame-Charakter?"* Falls nein, läuft die Pipeline wie heute (KZG-Schreiben, ggf. Notiz/Timeline-CRUD ohne Frame-Aufbau). Falls ja, wird das Frame-System aktiviert.

Diese Türschwelle verhindert Übergeneralisierung. Nicht jede Aussage soll zum Vorhaben aufgewertet werden — *"Ich kaufe morgen Fleisch"* will keine Rückfrage produzieren.

---

## 5. Pipeline — Wo das Frame-System eingreift

### 5.1 Aktuelle Pipeline (vereinfacht)

```
User-Prompt
    ↓
Salienz (extrahiert Roh-Fakten parallel)
    ↓
Validate → Classify → [Search] → CRUD → Confirm
                  ↑
              Aktion festgelegt
```

Heute geht zwischen Classify und Search/CRUD nichts, was das Datenpaket aktion-spezifisch anpasst.

### 5.2 Erweiterte Pipeline mit Frames

```
User-Prompt
    ↓
Salienz (Pfad 1: extrahiert Roh-Fakten parallel — bleibt bestehen)
    ↓
Validate
    ↓
Classify+Frame (LLM-Call 1: action, target, normalisiert, frame)
    ├─ ist_referenz=false → kein Frame-Pfad
    │    → Search → CRUD → Confirm (heutige Pipeline)
    │
    ├─ ist_referenz=true, Frame vollständig
    │    → Search/Gather (KG + Vorerfahrungen über Slots)
    │    → CRUD (schreibt Timeline mit Magneten)
    │    → Confirm
    │    → FaktenAgent-Push (Pfad 2: schreibt Frame-Tripel)
    │
    └─ ist_referenz=true, Frame mit Lücken
         → Frame-Auflöser (LLM-Call 2)
              ├─ Lücken aus Wissen rekonstruierbar? → füllen, Slot markieren
              ├─ kritische Lücke nicht rekonstruierbar? → Rückfrage formulieren
              └─ unkritische Lücke? → akzeptieren mit slot=null
         → Resume nach User-Antwort
         → Frame jetzt vollständig → weiter wie oben
```

### 5.3 Welche Nodes neu, welche erweitert

| Node | Status | Aufgabe |
|---|---|---|
| `Classify` | erweitert | Zusätzliches Output-Feld `frame` mit Slots und Referenz-Markierung |
| `Frame-Auflöser` | **neu** | Optional, nur bei Frame mit Lücken. Lücken-Analyse, ggf. Rückfrage |
| `Search/Gather` | erweitert | Sammelt Wissen aus KG+Timeline+Notizen über die Frame-Slots |
| `CRUD` | erweitert | Schreibt Magneten (`themen`, Verhaltens-Flags) und ruft FaktenAgent-Push |
| `FaktenAgent-Push` | **neu** als Trigger-Pfad | Schreibt strukturierte Tripel aus Frame-Resultat |

### 5.4 Trade-Off zur Latenz

Bei **vollständigen Frames** (kein Frame-Auflöser nötig) entsteht **kein zusätzlicher LLM-Call** — das Frame ist Teil des bestehenden Classify-Calls. Latenz unverändert.

Bei **Frames mit Lücken** entsteht ein zweiter LLM-Call (Frame-Auflöser, ca. 1-2 Sekunden). Das ist akzeptabel, weil der Auflöser nur dann läuft, wenn ohnehin eine Rückfrage entsteht. Der Butler-Vergleich passt: *"Hmmmm... Sir, ich habe da noch eine Frage: wird es wieder der Zahnarzt in Treuchtlingen sein?"* — die zwei Sekunden Nachdenken sind Teil der Geste, kein Bug.

---

## 6. Frame-Erhebung im Classify-Node

### 6.1 Output-Schema

Der Classify-Node gibt heute schon ein JSON mit `action`, `target`, `target_typ`, `konfidenz`, `normalisiert` zurück. Neu kommt das Feld `frame` hinzu:

```json
{
    "action": "create",
    "target": "Zahnarzttermin",
    "target_typ": "interface",
    "konfidenz": "hoch",
    "normalisiert": "create: Termin am Freitag, Anlass Zahnarzt",
    "frame": {
        "art": "termin",
        "ist_referenz": true,
        "slots": {
            "wer":  "Meister",
            "wann": "Freitag",
            "was":  "Zahnarzt",
            "wo":   null
        },
        "fehlend": ["wo"],
        "fehlend_kritisch": []
    }
}
```

Bei `ist_referenz=false` enthält `frame` nur das Feld `ist_referenz`, die anderen Felder bleiben leer. Der Pfad-Switch passiert an dieser Markierung.

### 6.2 Was das Classify-LLM hinzulernen muss

Drei Erweiterungen am bestehenden Classify-Prompt:

1. **Referenz-Erkennung:** Linguistische Marker für Vorhaben-Charakter (Abschnitt 4.1). Konkrete Beispiele in beide Richtungen.
2. **Frame-Art bestimmen:** Aus dem Anliegen die Frame-Art ableiten (`termin`, `einkauf`, `reise`, `treffen`, `notiz_liste`...). Offene Liste, das LLM darf neue Arten erfinden.
3. **Slot-Erhebung:** Pro Frame-Art die naheliegenden Slots benennen und aus dem Prompt belegen.

Die Frame-Art-Liste muss nicht im Prompt vorgegeben werden — das LLM kennt typische Vorhaben-Klassen aus seinem Weltwissen. Optional kann das **zentrale Lager** dem Classifier eine Liste der bisher gesehenen Arten als Konsistenz-Hinweis mitgeben (Abschnitt 11.3).

### 6.3 Domain-Language-Erweiterung

Die `[FACHSPRACHE]`-Konvention der Agenten wird um Frame-Beispiele ergänzt. Beispiel-Format für TimelineAgent:

| User sagt | Frame-Output |
|---|---|
| *"Am Freitag Zahnarzt"* | `art=termin, slots={wann:Freitag, was:Zahnarzt}` |
| *"Treffen mit Anna nächste Woche im Café"* | `art=treffen, slots={wer:[Meister,Anna], wann:nächste Woche, wo:Café, was:?}` |
| *"Ich gehe morgen Einkaufen"* | `art=einkauf, slots={wer:Meister, wann:morgen, was:?, wo:?}` |

---

## 7. Frame-Auflöser-Node — Lücken-Analyse und Rückfrage

### 7.1 Wann der Auflöser läuft

Nur dann, wenn Classify ein Frame mit Lücken liefert. Bei vollständigen Frames oder Nicht-Referenzen wird der Auflöser übersprungen. Das ist die einzige Stelle, an der ein zweiter LLM-Call entsteht.

### 7.2 Was der Auflöser tut

Drei Aufgaben in einem LLM-Call:

**Aufgabe 1 — Rekonstruktion aus Vor-Wissen.**
Für jeden fehlenden Slot prüft das LLM, ob es aus Wissen ableitbar ist:

- Slot `wo` für Frame-Art `termin` mit `was=Zahnarzt`: Schaue im Knowledge Graph nach `(Meister, GEHT_ZUM_ZAHNARZT_IN, ?)` oder im Frame-Lager nach früheren Zahnarzt-Frames mit belegtem `wo`-Slot.
- Slot `wer` für Frame-Art `termin` mit Default-Annahme: meist der User selbst.
- Slot `wo` für Frame-Art `einkauf` mit `was=Fleisch`: Schaue nach besuchten Geschäften.

Wenn rekonstruierbar: Slot füllen, im Output markieren als `quelle=rekonstruiert` und ggf. **bei der Bestätigung dem User mitteilen** (*"Wahrscheinlich Treuchtlingen, da warst du immer — passt das?"*).

**Aufgabe 2 — Kritikalität bewerten.**
Für jede verbleibende Lücke entscheiden: kritisch oder unkritisch?

- **Kritisch:** Ohne diesen Slot ist die Aktion nicht sinnvoll durchführbar. Beispiel: `wann` für einen Termin.
- **Unkritisch:** Aktion ist auch ohne den Slot nützlich. Beispiel: `was` für einen Termin (man weiß: Termin ist morgen, Anlass offen — kann man später noch ergänzen).

**Aufgabe 3 — Rückfrage formulieren oder akzeptieren.**
Wenn kritische Lücke: Eine einzelne Rückfrage formulieren, die alle kritischen Lücken bündelt (Abschnitt 12 zur Rückfragen-Disziplin). Wenn nur unkritische Lücken: Frame mit `slot=null` akzeptieren, weiter zur Aktion.

### 7.3 Output-Schema des Auflösers

```json
{
    "frame_aufgeloest": {
        "art": "termin",
        "slots": {
            "wer":  {"wert": "Meister",    "quelle": "default"},
            "wann": {"wert": "Freitag",    "quelle": "prompt"},
            "was":  {"wert": "Zahnarzt",   "quelle": "prompt"},
            "wo":   {"wert": "Treuchtlingen", "quelle": "rekonstruiert"}
        },
        "vollstaendig": true,
        "rueckfrage_noetig": false,
        "rueckfrage_text": null
    }
}
```

Wenn `rueckfrage_noetig=true`, läuft der Standard-Resume-Mechanismus an (Pending-Agent in Redis, TTL 300s, Resume nach User-Antwort). Beim Resume wird der Auflöser nicht erneut aufgerufen — die User-Antwort füllt den Slot direkt, das Frame ist vollständig, Pipeline läuft weiter.

### 7.4 Quellen-Markierung als Vertrauens-Information

Die `quelle`-Markierung pro Slot ist nicht nur dokumentarisch. Sie hat zwei Konsequenzen:

1. **Im Confirm-Schritt:** Rekonstruierte Slots werden im Bestätigungs-Text erwähnt (*"...beim Zahnarzt in Treuchtlingen, wie immer"*), damit der User korrigieren kann.
2. **Beim FaktenAgent-Push:** Rekonstruierte Slots werden mit niedrigerer Konfidenz in den Knowledge Graph geschrieben (oder gar nicht — siehe Abschnitt 10.4).

---

## 8. Search als Gatherer — Wissens-Aktivierung über Slots

### 8.1 Konzeptuelle Vertiefung

Heute ist Search ein punktueller "finde Ziel-Eintrag in DB"-Schritt — pg_trgm-Suche, gewichtete Felder, Score-Gap. Im Frame-Konzept wird Search zum **Gatherer**: einem Sammelpunkt für alles Wissen, das zum Frame gehört.

Beispiel: Frame `einkauf` mit `wo=Aldi`. Search holt:
- Bestehende Notizen mit `entitaet_ids @> [aldi_id]` — also Listen, die Aldi betreffen
- Bestehende Timeline-Einträge mit Aldi-Bezug — vergangene Aldi-Besuche, Häufigkeit
- Bestehende Tripel im Knowledge Graph mit Aldi als Subjekt oder Objekt
- Bestehende Frames im Lager mit Frame-Art `einkauf` und `wo=Aldi`

### 8.2 Was der Gatherer dem CRUD übergibt

```python
state["frame_kontext"] = {
    "frame": {...},                    # vom Auflöser
    "verwandte_notizen": [...],        # für Aldi: bestehende Aldi-Liste
    "verwandte_timeline": [...],       # vergangene Aldi-Besuche
    "verwandte_tripel": [...],         # Knowledge-Graph-Wissen
    "vergangene_frames": [...],        # ähnliche Frames aus Lager
}
```

CRUD nutzt das, um:
- Bei einem neuen Aldi-Einkauf-Frame die existierende Aldi-Notiz als Verknüpfung anzubieten
- Im Confirm-Text auf Vor-Wissen zu verweisen (*"Auf deiner Aldi-Liste steht auch Joghurt — soll ich das hinzufügen?"*)
- Magneten konsequent zu setzen (Frame liefert `entitaet_ids` aus den Slots)

### 8.3 Magnet-Aktivierung über Frame-Slots

Das ist die Stelle, an der Frames die Magneten-Convention §1 in Wirkung bringen. Heute sind Magneten geleerte Schienen — Spalten in der DB, die nicht befüllt werden (außer für Timeline seit M2.5a). Frames sind die strukturelle Quelle für Magnet-Befüllung:

| Frame-Slot | Magnet-Eintrag |
|---|---|
| `wer` | `entitaet_ids` (User + ggf. weitere Personen) |
| `wo` | `entitaet_ids` (Ort als Entität) |
| `wann` | `timeline_id` (Verweis auf Timeline-Eintrag) |
| `was` | `themen` (Anlass als Theme) |

Diese Mapping ist domänen-übergreifend stabil — `wer` ist immer `entitaet_ids`, `wann` ist immer `timeline_id`, unabhängig ob `termin` oder `einkauf`.

---

## 9. CRUD und Magneten-Befüllung

### 9.1 CRUD bei Frame-Aktionen

Bei einem Frame-getriebenen CRUD-Aufruf bekommt der CRUD-Code:

- Den Frame mit aufgelösten Slots
- Den Gatherer-Output (verwandte Wissens-Schichten)
- Optional die User-Antwort aus einer Resume-Phase

Der CRUD führt aus:

1. **Hauptobjekt anlegen** (Timeline-Eintrag, Notiz, Termin) mit Magneten aus den Frame-Slots
2. **Verknüpfungen setzen** zu existierenden Wissens-Schichten (Notiz an bestehende Aldi-Liste anhängen, statt neue zu erstellen)
3. **FaktenAgent triggern** mit Frame als Input (Abschnitt 10)
4. **Bestätigung formulieren**, die Vor-Wissen erwähnt

### 9.2 Magneten-Befüllung in einem Schritt

Das M2.5a-Pattern (themen + Verhaltens-Flags aus `event_type`) bleibt bestehen, wird aber durch Frame-Daten ergänzt:

| Magnet | Quelle vor Frames | Quelle mit Frames |
|---|---|---|
| `themen` | abgeleitet aus `event_type` | aus `was`-Slot + `event_type` |
| `binding`, `remind`, `conflict_check` | abgeleitet aus `event_type` | unverändert |
| `entitaet_ids` | leer (M5-Scope) | aus `wer`+`wo`-Slots, vor M5 |
| `timeline_id` | (selbst, bei Timeline) | (selbst, bei Timeline) |

Damit bringt das Frame-Konzept einen Teil der M5-Magnet-Befüllung **vor** ihren ursprünglichen Sprint — natürlich, weil die Frame-Slots ohnehin Entitäten und Themen liefern.

### 9.3 Verknüpfung statt Neuanlage

Wenn der Gatherer eine bestehende Wissens-Schicht findet, die zum Frame passt, soll CRUD nicht blind neu anlegen. Beispiel:

- User: *"Ich gehe morgen zu Aldi und brauche Joghurt"*
- Gatherer findet: Notiz "Aldi-Liste" existiert bereits mit Inhalt "Brot, Milch"
- CRUD-Entscheidung: Joghurt wird per `add_content` an bestehende Notiz angehängt, nicht als neue Notiz angelegt

Diese Logik ist bereits embryonal in den CRUD-Codes (Container-vs-Inhalt-Regel beim NotizenAgent), wird aber durch Frame-Daten deterministischer.

---

## 10. FaktenAgent als Pipeline-Schluss — Komplementär zur Salienz

### 10.1 Heutige Fakten-Pipeline

Der FaktenManager (`plugins/fakten_manager/manager.py`) wird heute über zwei Pfade aufgerufen, beschrieben in `novaberg-mem-knowledge-graph.md` §5:

**Pfad 1 — Salienz-getriggert (Hauptpfad):**
Die Salienz extrahiert Roh-Fakten als `{subjekt, schluessel, wert, typ}` aus dem User-Prompt. Der FaktenManager transformiert sie über Konstanten-Tabellen (`_ENTITAETS_SCHLUESSEL`, `_ATTRIBUT_MAP`, `_WERT_TYP_MAP`) und schreibt Tripel.

**Pfad 2 — Planner-getriggert (explizit):**
Bei Management-Befehlen wie *"Was weißt du über Anna?"* routet der Planner direkt zum FaktenManager.

### 10.2 Was fehlt heute

Die Salienz sieht den **rohen User-Prompt**, nicht das **strukturierte Frame** nach Auflösung. Wenn ein Frame `wo` durch Rekonstruktion aus Vor-Wissen füllt (z.B. *"Treuchtlingen"* aus Vor-Erfahrung), hat die Salienz das nicht gesehen. Die strukturierte Information geht im aktuellen Pfad nicht ins Faktengedächtnis.

### 10.3 Der neue Trigger — Agent-Push

Das Frame-Konzept ergänzt einen **dritten Pfad**:

**Pfad 3 — Agent-Push (neu):**
Nach erfolgreichem CRUD ruft der ausführende Agent (TimelineAgent, NotizenAgent...) den FaktenAgent mit dem **vollständigen Frame als Input**. Der FaktenAgent extrahiert daraus Tripel und schreibt sie.

Beispiel:
- Frame nach Auflösung: `art=termin, slots={wer:Meister, wann:Freitag, was:Zahnarzt, wo:Treuchtlingen}`
- FaktenAgent-Push erzeugt:
  - `(Meister, HAT_TERMIN_AM, Freitag)` mit Verweis auf Timeline-Eintrag
  - `(Termin-X, ANLASS, Zahnarzt)`
  - `(Termin-X, ORT, Treuchtlingen)`
  - Optional: `(Meister, GEHT_ZUM_ZAHNARZT_IN, Treuchtlingen)` als verallgemeinerter Fakt

### 10.4 Komplementarität, nicht Ablösung

Die drei Pfade koexistieren:

| Pfad | Quelle | Was extrahiert wird |
|---|---|---|
| Pfad 1 (Salienz) | roher User-Prompt | Lose Aussagen, Erwähnungen, Entitäten im Text |
| Pfad 2 (Planner) | explizite Management-Anfrage | Strukturierte Anfrage, vom User intendiert |
| Pfad 3 (Agent-Push) | strukturierter Frame nach Auflösung | Vollständige Tripel aus Frame-Slots inkl. rekonstruiertem Wissen |

Konflikte zwischen den Pfaden löst die **Edge Invalidation** der Fakten-Tabelle (KG-Doku §5 Schritt 3): Wenn zwei Pfade denselben Fakt schreiben wollen, wird der ältere invalidiert, der neuere ist aktiv. Bi-temporales Modell, kein Daten-Verlust.

### 10.5 Trigger-Logik

Wann triggert ein Agent den FaktenAgent-Push?

- **Bei vollständigem Referenz-Frame:** Immer pushen. Strukturelles Wissen ist faktwürdig.
- **Bei Frame mit unkritischen Lücken:** Pushen, was vorhanden ist. Lücken bleiben Lücken.
- **Bei Interface-Klassifikation:** Kein Push. Salienz allein entscheidet.
- **Bei rekonstruierten Slots:** Push, aber mit Vermerk `quelle=rekonstruiert` — der FaktenAgent kann selbst entscheiden, ob er solche Tripel mit niedrigerer Konfidenz schreibt oder verwirft.

Der Salienz-Schwellen-Mechanismus aus dem heutigen Pfad 1 bleibt für unstrukturierte Aussagen sinnvoll. Bei Frame-Pushes ist die Salienz strukturell garantiert hoch — Frames entstehen nur aus Referenz-Aussagen, die per Definition substanzhaft sind. Daher kein zusätzlicher Salienz-Check beim Push.

### 10.6 Position in der Pipeline

```
... CRUD (schreibt Hauptobjekt) → Confirm → FaktenAgent-Push → END
```

Position am Schluss, weil:
- CRUD könnte beim Schreiben Fakten brauchen, die der Push erst erzeugt — Reihenfolge umgekehrt wäre Henne-Ei
- Confirm soll vor dem Push laufen, damit der User die Bestätigung schnell sieht (Push kann asynchron sein)

Asynchrone Ausführung des Pushes ist möglich, falls Latenz ein Thema wird. Konzeptuell ist die Reihenfolge wichtiger als die Synchronität.

### 10.7 Verbindung zu M2.5b

Im Backlog steht **M2.5b — FaktenAgent neu anlegen** (heutiger FaktenManager → echter Agent). Das Frame-Konzept hat zwei Konsequenzen für M2.5b:

1. **M2.5b muss vor dem Frame-Pilot liegen.** Den Push-Trigger braucht einen Agent, der angesprochen werden kann.
2. **M2.5b sollte den Push-Trigger gleich mit vorsehen.** Der neue FaktenAgent bekommt von Anfang an drei Trigger-Pfade in seiner Architektur.

---

## 11. Frame-Lager — Lernende Konsens-Speicherung

### 11.1 Zweck

Das Frame-Lager ist kein Schema-Definitions-Ort und kein autoritativer Speicher. Es ist ein **Konsens-Gedächtnis** für Frame-Wissen über die Zeit:

- Welche Frame-Arten haben wir bisher gesehen?
- Welche Slots werden bei Frame-Art X typischerweise belegt?
- Welche Werte tauchen häufig auf? (z.B. *"Treuchtlingen"* bei `wo` für Zahnarzt-Frames)

Das Lager wächst mit jeder Frame-Erhebung. Der Classify-Node und der Frame-Auflöser können es als Konsistenz-Hilfe konsultieren.

### 11.2 Schema (vorläufig)

```sql
CREATE TABLE frames (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    character_id    TEXT NOT NULL,
    frame_art       TEXT NOT NULL,        -- 'termin', 'einkauf', 'reise', ...
    slots           JSONB NOT NULL,       -- aufgelöste Slot-Belegungen
    quellen         JSONB,                -- pro Slot: prompt|rekonstruiert|default
    haeufigkeit     INTEGER DEFAULT 1,
    erstellt_am     TIMESTAMPTZ DEFAULT NOW(),
    zuletzt_gesehen TIMESTAMPTZ DEFAULT NOW(),
    timeline_id     INTEGER REFERENCES timeline(id) ON DELETE SET NULL,
    notiz_id        INTEGER REFERENCES notizen(id) ON DELETE SET NULL,
    aktiv           BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_frames_art         ON frames (user_id, character_id, frame_art);
CREATE INDEX idx_frames_zuletzt     ON frames (zuletzt_gesehen DESC);
CREATE INDEX idx_frames_slots_gin   ON frames USING GIN (slots);
```

Paar-skopiert über `(user_id, character_id)` analog zu LZG/Notizen/Timeline (Magneten-Convention §6). Querverweise zu Timeline/Notizen für Re-Identifikation.

### 11.3 Operationen

```python
def frame_registrieren(art, slots, quellen, ...) -> int:
    """Legt Frame-Eintrag an. Erhöht Häufigkeit, falls identisches Frame existiert."""

def frame_konsens_holen(art) -> dict | None:
    """Aggregiert Konsens für Frame-Art:
       - typische Slots (welche werden in >X% der Fälle belegt?)
       - typische Werte (Modus, häufigste Belegung)
       - durchschnittliche Vollständigkeit"""

def frame_aehnliche_finden(art, slots) -> list[dict]:
    """Findet Frames mit gleicher Art und teil-überlappenden Slots.
       Für Rekonstruktion: 'In früheren Zahnarzt-Frames war wo=Treuchtlingen'."""

def frame_dekay() -> int:
    """Decay analog zu LZG: alte, selten gesehene Frames verlieren Gewicht.
       Salienz-Inspirierte Dekay-Funktion (siehe Memory-Decay-Konzept)."""
```

### 11.4 Lernende Eigenschaften

Das Lager ist nicht statisch. Drei Lern-Mechanismen:

1. **Häufigkeits-Aggregation:** Je öfter ein Slot belegt wird, desto mehr "gehört" er zum Frame. Ein Termin-Frame mit `wo=null` in 90% der Fälle wäre ein Hinweis, dass `wo` für Termine **nicht kritisch** ist.
2. **Wert-Cluster:** Häufige Werte für einen Slot (wie *"Treuchtlingen"* bei Zahnarzt-Termin-`wo`) werden zur impliziten Default-Annahme für die Rekonstruktion.
3. **Decay:** Alte, selten reproduzierte Frame-Arten verschwinden langsam. Das Schema lebt mit dem Nutzer.

### 11.5 Verhältnis zum Knowledge Graph

Das Frame-Lager und der Knowledge Graph sind verschiedene Schichten:

| | Frame-Lager | Knowledge Graph |
|---|---|---|
| Granularität | Vorhaben-Schemas mit Slot-Belegungen | Atomare Tripel `(S, P, O)` |
| Lebensdauer | Wachsend, dekaybar | Bi-temporal (valid_from, valid_to) |
| Zweck | Schema-Konsens, Vor-Erfahrung | Welt-Wissen für Anfragen |
| Schreibtrigger | Classify+Frame, Auflöser | Salienz, Planner, Agent-Push |

Zusammenspiel: Ein neuer Termin-Frame schreibt sowohl ins Frame-Lager (als Schema-Beleg) als auch über den FaktenAgent-Push in den Knowledge Graph (als atomare Tripel).

---

## 12. Rückfragen-Disziplin

### 12.1 Maximal eine Rückfrage pro Frame-Erhebung

Mehrere Rückfragen in Folge sind nervig. Wenn nach der ersten Rückfrage immer noch kritische Slots offen sind: lieber den Frame mit den vorhandenen Daten anlegen und später einen Hinweis geben (*"Der Termin ist eingetragen, bei Gelegenheit fehlt mir noch der Anlass"*).

### 12.2 Bündelung mehrerer Slots in einer Frage

Wenn mehrere kritische Slots fehlen, formuliert der Auflöser **eine** Frage, die mehrere Slots adressiert:

- Schlecht: *"Wann?"* → User antwortet → *"Wo?"* → User antwortet → *"Was?"*
- Gut: *"Wann und wo wäre das Treffen, und worum geht es?"*

Das LLM kann das, wenn der Prompt es so formuliert.

### 12.3 Vehicle-Stil aus Beziehungs-Schicht

Der Frame-Auflöser formuliert die Rückfrage **strukturell** (die Information). Wie sie ausgesprochen wird (Ton, Vehicle, Empathie) entscheidet die Beziehungs-Schicht (Responder, Gesprächsraum). Der Auflöser liefert *"Ort fehlt für Termin"*, der Responder formt daraus *"Der Zahnarzt in Treuchtlingen wie üblich, oder diesmal woanders?"*.

### 12.4 Akzeptierte Lücken

Unkritische Lücken bleiben Lücken. Der Frame wird mit `slot=null` angelegt, der Konsens-Speicher lernt, dass dieser Slot häufig leer ist, und mit der Zeit wird er als optional markiert.

---

## 13. Vehicle als separate Beziehungs-Schicht

### 13.1 Was Vehicle ist

Vehicle ist die Art, wie Nova ihre Informationsabfrage oder -mitteilung **einkleidet**. Statt *"Welcher Anlass?"* zu sagen, fragt sie *"Hoffentlich nur zur Zahnreinigung?"* — die Frage ist die gleiche, der Vehicle ist Beziehungspflege.

### 13.2 Wo Vehicle wohnt — nicht im Frame-System

Frame-System liefert Struktur (Slots, Lücken, Rückfrage-Inhalt). Die Beziehungs-Schicht (Responder, Gesprächsraum) entscheidet:
- Soll überhaupt etwas zum Frame gesagt werden, oder nur eine Bestätigung?
- Wenn ja, in welchem Vehicle?
- Soll ein Vehicle eine empathische Bemerkung sein statt einer Frage?

Diese Entscheidung gehört zum Charakter und zur Stimmung — nicht zum Frame-System.

### 13.3 Beispiel-Sequenz

- Frame-System liefert: *"Frame `termin` vollständig: wer=Meister, wann=Freitag, was=Zahnarzt, wo=Treuchtlingen"*
- Beziehungs-Schicht entscheidet: Bestätigung + empathisches Vehicle
- Nova sagt: *"Ist eingetragen, Freitag in Treuchtlingen. Hoffe, nur zur Routine?"*

Dasselbe Frame, andere Stimmung — andere Beziehungs-Antwort:

- Frame-System liefert: *"Frame `termin` vollständig: ..."*
- Beziehungs-Schicht entscheidet: knappe Bestätigung
- Nova sagt: *"Eingetragen."*

Der Frame ist konstant, das Vehicle variiert mit Charakter und Kontext. Diese Trennung ist explizit gewollt.

---

## 14. Verbindungen zu existierenden Konzepten

### 14.1 Magneten-Convention

Frame-Slots speisen Magneten-Spalten direkt. `wer`/`wo` liefern `entitaet_ids`, `was` liefert `themen`. Das Frame-System ist die **strukturelle Quelle** für die Magnet-Befüllung, die heute noch leer ist (außer Timeline seit M2.5a).

### 14.2 Domain Language (Pattern)

Domain Language definiert die Verben pro Agent (`create`, `update`, `add_content`...). Frame-System ergänzt: pro Aktion, welche Slots sind relevant. Domain Language sagt das *Was*, Frame-System sagt das *Womit*.

### 14.3 Substanz-Filter (Magneten-Convention §7)

Substanz-Filter und Interface/Referenz-Türsteher sind eng verwandt. Der Substanz-Filter entscheidet *"ist das Tripel-würdig?"*, der Frame-Türsteher entscheidet *"ist das Frame-würdig?"*. Beide haben dieselbe linguistische Grundlage — das *Namensschild-Prinzip*. Beide schützen das jeweilige strukturierte Gedächtnis vor Übergeneralisierung.

### 14.4 Entity Resolution (Pattern)

Frame-Slots `wer` und `wo` sind Entitäten. Sie laufen durch die bestehende Entity Resolution (`memory/services/entity_resolution.py`) — der ICH/Name/Embedding-Algorithmus aus KG-Doku §6. Das Frame-System ruft Entity Resolution für seine Entitäts-Slots auf, anders nichts.

### 14.5 Action-Context-Pattern (im Backlog erwähnt)

Im Chat 80 wurde diskutiert, ob ein "Compose-Context"-Node nach Classify das aktion-spezifische Datenpaket schnürt. Mit Frame-System ist das **teilweise schon erledigt** — Classify liefert das Frame, der Auflöser ergänzt Wissen, Search wird zum Gatherer. Die `action_context`-Idee ist eine Generalisierung dieser Mechanik. Sie kann später formalisiert werden, ist aber für Frame-Zwecke nicht zwingend nötig.

### 14.6 Neugier (`thinking-curiosity_k`)

Frames sind ein neuer Trigger für Neugier. Wenn ein häufiger Frame plötzlich einen ungewöhnlichen Slot-Wert bekommt (*"Termin beim Zahnarzt — diesmal in Nürnberg statt Treuchtlingen"*), kann das Neugier auslösen: *"Warum diesmal woanders?"* — das ist Berlynes Sweet Spot in strukturierter Form.

### 14.7 Drive (`thinking-drive_k`)

Frames können Drive-Ziele konkretisieren. Ein abstraktes Drive-Ziel *"Botanik vertiefen"* wird greifbar, wenn ein Frame `besuch_botanischer_garten` mit Slots `wann/wo/wer` entsteht. Frames sind die Mikro-Strukturen, in denen Drive-Ziele Form annehmen.

### 14.8 Metakognition (`metakognition_k`)

Das Frame-Lager als emergentes Schema-Gedächtnis ist eine Form von metakognitivem Wissen — Wissen über die Struktur des eigenen Wissens. Es passt zur Vision, dass Nova ihre eigenen Verhaltensmuster beobachten und reflektieren kann.

---

## 15. Designprinzipien

1. **Frames sind Weltwissen, nicht Code.** Das LLM kennt sie. Wir definieren keine Schemas hard.
2. **Das Lager lernt, das Lager zwingt nicht.** Konsens entsteht aus Häufigkeit, nicht aus Vorgabe.
3. **Türsteher vor Aufbau.** Erst Interface vs. Referenz klären, dann Frame erheben.
4. **Lücken sind erlaubt, kritische Lücken werden eingefordert.** Maximal eine Rückfrage.
5. **Rekonstruktion vor Rückfrage.** Was aus Vor-Wissen ableitbar ist, wird abgeleitet, nicht erfragt.
6. **Quelle pro Slot festhalten.** prompt / rekonstruiert / default — Vertrauen ist nicht uniform.
7. **Komplementäre Trigger ins Faktengedächtnis.** Salienz, Planner, Agent-Push — drei Pfade, ein Speicher.
8. **Struktur und Beziehung trennen.** Frame liefert Inhalt, Vehicle liefert Form.
9. **Speichern ist billig, Vergessen ist intelligent.** Auch für Frames — Decay über Häufigkeit + Zeit.
10. **Magneten als Frame-Konsequenz.** Frame-Slots befüllen Magnet-Spalten direkt.

---

## 16. Offene Punkte und nächste Schritte

### 16.1 Offene konzeptionelle Fragen

- **Frame-Decay:** Welche Funktion? Salienz-Inspiration aus LZG-Decay (logarithmisch + Häufigkeit) als Startpunkt, aber für Frames vermutlich weniger aggressiv (Schema-Wissen ist langfristiger als Erlebnis).
- **Multi-Frame-Erhebung pro Turn:** Wenn der User in einem Prompt mehrere Vorhaben erwähnt (*"Morgen Zahnarzt, übermorgen Aldi"*), sollte Classify mehrere Frames produzieren? Pro Vorhaben einer? Im ersten Wurf: ja, das LLM kann das, Output-Schema müsste `frame` als Liste statt als Dict erlauben.
- **Frame-Hierarchie:** Sind manche Frames Spezialisierungen anderer? `arzttermin` als Spezialfall von `termin`? Vorerst flach lassen, beobachten ob Hierarchie nötig wird.
- **Konflikt mit existierenden Aussagen:** Was, wenn ein Frame `wo=Nürnberg` rekonstruiert, der KG aber sagt `(Meister, ZAHNARZT_IN, Treuchtlingen)`? Auflöser muss vor Push prüfen und ggf. nachfragen statt anlegen.

### 16.2 Implementierungs-Reihenfolge

**Phase 0 — Vorbereitung (vor allem anderen):**
- M2.5b — FaktenAgent als echter Agent (statt Plugin) anlegen
- TIMELINE-PAIR-MIGRATION + NOTIZEN-PAIR-MISSING + FAKTEN-PAIR-IGNORED — `character_id`-Lücken schließen, sonst leakt Frame-Wissen zwischen Charakteren

**Phase 1 — Pilot-Frame:**
- Genau ein Frame, genau ein Agent: `termin` im TimelineAgent
- Classify-Erweiterung um `frame`-Output
- Frame-Auflöser-Node (LLM-Call 2)
- Frame-Lager als Tabelle (kein Decay, kein Konsens-Aggregator)
- FaktenAgent-Push für Termin-Frames
- Schmaler Scope: keine Vehicle-Schicht, keine Multi-Frame-Erhebung

**Phase 1b — Übertragung NotizenAgent:**

- Frame-Arten `notiz_create`, `notiz_update`, `notiz_rename` im NotizenAgent
- Frame-Auflöser-Node aus Phase 1 wiederverwendet (Slot-für-Slot-Rekonstruktion über Vor-Turns, Distanz >1)
- Slot `neuer_typ` im `notiz_update`-Frame definiert Container-Wechsel (Notiz↔Liste) als legitime Aktion
- Frame-Definitionen in der Domain-Language repräsentieren legitime Skills — Voraussetzung für Skill-Selbstkenntnis
- Adressiert die Bugs aus Chat 80 (siehe Backlog):
  - **NOTIZEN-KONTEXT-REKONSTRUKTION** — Mehrschritt-Rekonstruktion (Frame-Auflöser iteriert über Vor-Turns)
  - **NOTIZEN-CONTAINER-WECHSEL** — `notiz_update`-Frame mit Slot `neuer_typ`
  - **NOTIZEN-SKILL-MANIFEST** — implizit durch Frame-Definitionen als Skill-Quelle (Frame-Lager §11)
  - **NOTIZEN-UPDATE-TARGET-LEER** — Bezugs-Auflösung in UPDATE-Pfad analog zur Inhalts-Auflösung im CREATE-Pfad

**Phase 2 — Generalisierung:**
- Frame-Konzept auf NotizenAgent (Frame-Art `notiz_liste`, `merkzettel`)
- Frame-Lager bekommt Konsens-Aggregator (`frame_konsens_holen`)
- Decay-Mechanismus für Frame-Lager
- Verhältnis zu existierenden Patterns (Action-Context, Domain Language) formalisieren

**Phase 3 — Beziehungs-Schicht:**
- Vehicle-Mechanismus für Frame-Bestätigungen
- Frame-Auflöser-Output an Beziehungs-Schicht weiterreichen
- Charakter-spezifische Vehicle-Wahl

**Phase 4 — Integration in Drive und Neugier:**
- Drive-Ziele werden über Frames konkretisiert
- Ungewöhnliche Slot-Werte triggern Neugier-Resonanz
- Frame-Häufigkeit als Magnet-Aktivierung

### 16.3 Risiken

- **Übergeneralisierung:** LLM erkennt zu viele Aussagen als Referenz, Frame-Lager wird zur Müllhalde. Gegenmaßnahme: Türsteher streng prompten, Substanz-Filter-Verwandtschaft nutzen.
- **Rekonstruktions-Halluzination:** Frame-Auflöser füllt Slots aus dünner Vor-Erfahrung, schreibt falsche Tripel ins KG. Gegenmaßnahme: `quelle=rekonstruiert` mitführen, FaktenAgent kann strenger filtern, ggf. Bestätigungs-Pflicht.
- **Latenz:** Zwei LLM-Calls statt einer bei jeder Frame-Erhebung mit Lücken. Akzeptabel im Butler-Stil, aber nicht überall. Gegenmaßnahme: Auflöser nur bei kritischen Lücken, sonst direkt durchwinken.
- **Konversations-Reibung:** Zu viele Rückfragen werden nervig. Gegenmaßnahme: Maximal eine Rückfrage, kritische Lücken streng definieren, im Zweifel akzeptieren.

---

## 17. Verweise

### Verbindliche Dokumente

- Convention: `novaberg-convention-magneten.md` — Drei-Achsen-Modell, Substanz-Filter, Welt vs. Erlebnis
- Convention: `novaberg-convention-paar-schema.md` — `(user_id, character_id)`-Skopierung
- Convention: `novaberg-convention-event-model.md` — User und Charakter als Akteure
- Pattern: `novaberg-pattern-domain-language.md` — Aktion-Verben pro Agent
- Pattern: `novaberg-pattern-entity-resolution.md` — Auflösung von Eigennamen

### Zugrundeliegende Konzepte

- `novaberg-mem-knowledge-graph.md` — Entitäten, Fakten, FaktenManager-Pipeline
- `novaberg-mem-lzg.md` — Langzeitgedächtnis, Decay, Salienz
- `novaberg-thinking-curiosity_k.md` — Neugier (Berlynes Sweet Spot)
- `novaberg-thinking-drive_k.md` — Drive-Ziele
- `novaberg-metakognition_k.md` — Selbstbeobachtung und Reflexion

### Agent-Dokumente

- `novaberg-agent-notes.md` — NotizenAgent, Classify-Node, Domain Language
- `novaberg-agent-timeline.md` — TimelineAgent, Magnet-Befüllung seit M2.5a

### Verwandte Backlog-Einträge

- M2.5b — FaktenAgent als Agent (Vorbedingung für Phase 1)
- TIMELINE-PAIR-MISSING / NOTIZEN-PAIR-MISSING / FAKTEN-PAIR-IGNORED — Paar-Skopierung (Vorbedingung)
- NOTIZEN-VOR-TURN-BEZUG (Chat 80) — Inhalts-Auflösung im Classify (verwandt, kleiner Scope)
- MEMORY-SALIENZ-VERERBUNG — Salienz auf semantischen Trägern (Frame-Slots als Träger)

### Quellen

- Chat 80 — Gesamte Konzeption: NotizenAgent-Audit → Bezugsauflösung → aktion-spezifisches Datenpaket → Slot-Filling → Frame-System → FaktenAgent-Push → Frame-Lager
