# Novaberg — Wissenslücken: der Zug zu einem Thema

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — persistente Wissenslücken, `neugier_vektor`, eigener Agent
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-wissensluecken_k.md
**Typ:** Konzept
**Herkunft:** `novaberg-thinking-curiosity_k.md` (Vision, TR1/TR2) — dieses Dokument ist die konkrete Bauform
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md`
**Abnehmer:** `novaberg-salienz-berechnung_k.md` §4 — dritter Antrieb im Eigen-Pfad

---

## 1. Welche Neugier hier gemeint ist

Drei Größen hießen bis Chat 111 alle „Neugier". Dieses Dokument baut die dritte:

| | Was sie ist | Stand |
|---|---|---|
| `aufnahmebereitschaft` | ob jetzt der Moment dafür ist — Zustand und Situation | gebaut |
| GV4-Lückensuche | die akute Lücke aus **diesem** Turn, flüchtig | gebaut |
| **`neugier_vektor`** | der Zug zu einem Thema **über den Turn hinaus** | **dieses Dokument** |

**Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.**

Die GV4-Suche ist turn-gebunden: Sie findet, was gerade nebenan liegt, und vergisst es. Was hier entsteht, überdauert — es liegt in einer Tabelle, wird angereichert, und schließt sich erst, wenn Nova das Thema wirklich kennt.

## 2. Was der Agent tut

```
   bekannte Themen                 Gesprächs-Themen
          │                               │
          └───────────┬───────────────────┘
                      ▼
              1. ERWEITERN   (LLM)  →  Nachbarthemen
                      ▼
              2. FILTERN  (Embedding) →  was sie schon weiß, fällt raus
                      ▼
              3. BEWERTEN            →  Resonanz · Neuheit · neugier_vektor
                      ▼
              4. ABLEGEN             →  Tabelle wissensluecken
```

### Erweitern braucht einen Erzeuger

Das ist der Kern, und er ist neu. **Eine Vektorsuche über den eigenen Bestand kann nichts entdecken** — sie liefert nur, was schon drinsteht. Aus „Himmel und Wolken" wird niemals „Garten", weil „Garten" ja gerade fehlt.

Ein LLM schlägt darum zu einem bekannten Thema **Rand- und Unterthemen** vor und liefert sie als Stichpunktliste: *Kosmologie* → „Dunkle Materie", „Rotverschiebung", „Inflation". *Himmel und Wolken* → „Regen", „Gartenbewässerung". Das Modell steuert das Weltwissen bei, das im eigenen Bestand definitionsgemäß fehlt.

**Entschieden Chat 111:** ein LLM als Erzeuger, **zwanzig Stichpunkte je Lauf**. Alternativen — Web-Suche, Ontologie — sind teurer und liefern nicht zwangsläufig Themen, die zu ihr passen. Die Zwanzig sind ein Startwert und nach der ersten Messung nachzujustieren.

### Vier Quellen für Stichpunkte

Der Erzeuger ist nur eine davon. Themen, die sie bewegen, hinterlassen ohnehin Spuren:

| Quelle | Wo sie liegt | `herkunft` |
|---|---|---|
| LLM-Erweiterung bekannter Themen | — | `nachbar` |
| Gesprächs-Turns | `pipeline_log`, LZG-Knoten | `gespraech` |
| Abgeschlossene Recherchen | `pipeline_log` | `recherche` |
| Vertiefungen | `pipeline_log` | `vertiefung` |

Die letzten drei kosten keinen Erzeuger — dort stehen die Stichpunkte schon, sie müssen nur extrahiert werden. Und sie tragen eine andere Qualität: Was aus einer Recherche fällt, hat sie tatsächlich beschäftigt, nicht bloß ein Modell für plausibel gehalten.

### Filtern ist der billige Teil

Jeder Kandidat wird embedded und gegen ihren Bestand (LZG-Knoten, KZG) geprüft. Was zu nah an Bekanntem liegt, ist keine Lücke.

### Nicht zwanzigmal dasselbe finden

**Der Fehler, der diesen Agenten nutzlos machen würde:** Läuft er über dieselben bekannten Themen, schlägt das LLM dieselben Nachbarn vor, und jeder Lauf verbrennt einen Aufruf für ein Ergebnis, das schon in der Tabelle steht.

Zwei Maßnahmen zusammen:

**Die Tabelle ist ihre eigene Ausschlussliste — über Embeddings, nicht über Text.** Jeder Kandidat wird ohnehin embedded. Ihn zusätzlich gegen die bestehenden Lücken zu prüfen kostet nichts:

```
kandidat  vs.  Bestand         → hohe Aehnlichkeit = sie weiss es      (neuheit)
kandidat  vs.  wissensluecken  → >= 0.95            = schon erfasst    (Dublette)
```

Der Vergleich läuft über **alle** Zeilen, unabhängig vom Status: Was offen, geschlossen oder ausgeschlossen ist, blockiert gleichermaßen einen neuen Vorschlag.

Ein Textvergleich täte das nicht — *„Dunkle Materie"* gegen *„dunkle Materie im Kosmos"* ist textlich verschieden, inhaltlich dasselbe. Und eine Textliste müsste in den Prompt, würde wachsen und den Kontext verstopfen.

**Zwei Schichten, verschiedene Aufgaben:**

- **Prompt-Hinweis**, kurz: die zuletzt erfassten Themen als Wink, damit das Modell seine zwanzig Plätze nicht für Dubletten verbraucht. Darf ungenau sein.
- **Embedding-Prüfung**, vollständig: die Garantie, unabhängig von Formulierung und Listenlänge. Muss es nicht.

**Wechselnde Saat.** Nicht jeder Lauf startet von denselben bekannten Themen. Der Agent zieht eine Stichprobe aus ihrem Bestand, damit über mehrere Läufe die Breite abgedeckt wird statt immer derselbe Ausschnitt. Ohne sie ließe die Ausschlussprüfung das Modell zu demselben Saatgut immer entferntere Vorschläge machen, bis sie beliebig werden.

**Zur Schwelle 0.95.** Das Projekt kennt bereits `LZG_KNOTEN_MATCH_SCHWELLE = 0.82` für Erinnerungs-Dubletten. Die beiden machen Verschiedenes: 0.82 fragt *„dieselbe Erinnerung?"* und **verschmilzt**; hier fragen wir *„dasselbe Thema?"* und **verwerfen**. Bei 0.95 kommen *„Dunkle Materie"* und *„Dunkle Materie im frühen Universum"* als zwei Lücken durch — verschiedene Tiefen desselben Feldes, und das ist gewollt. Ob Umformulierungen durchrutschen, zeigt die erste Messung an der Tabelle.

**Bei einer Dublette wird aufgefrischt, nicht verworfen.** Die bestehende Zeile bekommt neu gerechnete `neuheit` und `neugier_vektor`. Ihre Neuheit kann seit dem letzten Lauf gesunken sein, weil Nova inzwischen darüber gesprochen hat — und genau daran schließt sich eine Lücke. Ein stumpfes Verwerfen ließe sie mit veralteten Werten stehen.

### Drei Zustände, eine Sperrwirkung

| `status` | Bedeutung | sperrt neue Vorschläge |
|---|---|---|
| `offen` | noch zu erschließen | ja |
| `geschlossen` | sie kennt es inzwischen | ja |
| `ausgeschlossen` | **Antithema** — soll nicht verfolgt werden | ja |

Eine Zeile wird **nie gelöscht**, nur umgestellt. Geschlossene Lücken belegen, dass der Kreislauf funktioniert, und zeigen später, welche Themen sie sich erschlossen hat — eine Wissensbiografie, die aus dem Bestand allein nicht ablesbar ist. Dort steht nur, was sie weiß, nicht was sie sich erarbeitet hat.

`ausgeschlossen` ist der einzige Weg, ein Thema dauerhaft loszuwerden, das immer wieder auftaucht und niemanden interessiert. Ohne diesen Zustand käme es bei jedem Lauf zurück.

## 3. Die Formel

```
resonanz       = cosine(thema, charakterfeld)
neuheit        = 1 − max(cosine(thema, bestand))
neugier_vektor = NOVA_NEUGIER × resonanz × neuheit
```

**Warum das Produkt eine umgekehrte U-Kurve ergibt.** Hohe Resonanz verlangt Nähe zu ihr, hohe Neuheit verlangt Ferne zum Bekannten. Beides zugleich geht nur **am Rand** ihres Feldes — dort, wo ein Thema sie angeht, sie es aber noch nicht kennt.

- **Zentrum:** hohe Resonanz, niedrige Neuheit → *„Ja, kenn ich."*
- **Rand:** mittlere bis hohe Resonanz, hohe Neuheit → **der Zug**
- **Außen:** niedrige Resonanz → *„Nicht meins."*

Das ist Berlynes umgekehrte U-Kurve, ohne dass sie eigens modelliert werden müsste — sie fällt aus dem Produkt heraus. Eine Summe hätte diese Eigenschaft nicht: Sie würde ein völlig fremdes Thema mit maximaler Neuheit belohnen.

**Alle drei Größen werden gespeichert, nicht nur das Produkt.** Der Vektor muss aus ihnen nachrechenbar sein (Konvention, Regel 3), und man sieht dann, **warum** eine Lücke zieht: hohe Resonanz bei mittlerer Neuheit ist etwas anderes als umgekehrt.

### Das Charakterfeld

Die Resonanz misst gegen ihren Charakter — `kern_hash` des Paares plus die aktive Charakter-Anweisung, gemeinsam embedded.

**Es wird nicht persistiert.** Der Agent bildet es zu Beginn seines Laufs, benutzt es für alle Kandidaten und verwirft es. Was bleibt, sind die Lücken. Ein Zwischenergebnis zu speichern hieße, es gegen seinen Quelltext synchron halten zu müssen — Aufwand ohne Gegenwert.

**Achtung beim Zusammenbauen:** Kern und Anweisung liegen unter **verschiedenen Schlüsseln.** Der Kern steht in `charakter_hash(nova, meister)`, die Anweisung in `charakter_anweisungen` unter `user_id='meister'` — dort fehlt bis heute jedes `character_id`. Wer das später abgreift, muss es wissen.

## 4. Die Tabelle

```sql
CREATE TABLE IF NOT EXISTS wissensluecken (
    id              SERIAL           PRIMARY KEY,
    user_id         TEXT             NOT NULL,
    character_id    TEXT             NOT NULL,
    thema           TEXT             NOT NULL,
    embedding       VECTOR(768),
    resonanz        DOUBLE PRECISION NOT NULL,
    neuheit         DOUBLE PRECISION NOT NULL,
    neugier_vektor  DOUBLE PRECISION NOT NULL,
    herkunft        TEXT             NOT NULL DEFAULT 'nachbar',
    status          TEXT             NOT NULL DEFAULT 'offen',
    erstellt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    geschlossen_am  TIMESTAMPTZ,
    UNIQUE (user_id, character_id, thema)
);
```

`status` trägt `'offen'`, `'geschlossen'` oder `'ausgeschlossen'` — kein `aktiv`-Flag. Ein Boolean sagt nur, dass eine Zeile nicht mehr zählt; er sagt nicht, **warum**. Bei einer Lücke ist der Grund die ganze Aussage: Sie ist zu, weil Nova das Thema inzwischen kennt.

`herkunft` trägt `'nachbar'`, `'gespraech'`, `'recherche'` oder `'vertiefung'` — welche der vier Quellen den Stichpunkt geliefert hat. Ohne das Feld ließe sich später nicht sagen, welcher Weg tatsächlich trägt.

**Das Paar ist Pflicht.** `ziele` trägt heute nur `user_id`, `charakter_anweisungen` ebenso — bei mehreren Nutzern und Charakteren bricht beides. Diese Tabelle macht es von Anfang an richtig; die anderen zwei bleiben Vorbestand und gehören in die Fundliste.

Der `UNIQUE`-Schlüssel macht den Lauf idempotent: Dasselbe Thema erzeugt keine zweite Zeile, sondern frischt die Bewertung auf.

## 5. Wann er läuft

**Der Anstoß kommt über den Stack, nicht aus dem Agenten.** Das ist die Trennung, die alles Weitere ermöglicht:

| Anlass | Wer stößt an |
|---|---|
| Charakter neu destilliert | `CharakterAgent` am Ende seines Laufs |
| Recherche abgeschlossen | später der Recherche-Pfad — neues Wissen, neue Lücken |
| periodisch | eigener Takt des Agenten |

Weil der Anstoß nicht am Charakter hängt, kann **jeder** Wissenszuwachs eine Neuberechnung auslösen. Eine Lücke schließt sich dann nicht, weil jemand sie für geschlossen erklärt, sondern weil sie beim nächsten Lauf den Filter nicht mehr passiert.

**Eigener Agent, nicht Anhang am CharakterAgent.** Getrennte Zuständigkeit, eigener Registry-Eintrag.

Seine Priorität ist **bewusst zu setzen, nicht per Default**. Gemessen am 27.07.2026: `CharakterAgent` mit 0.3 kam erst dran, als das Gespräch verstummte, und eine achtminütige Recherche blockierte den Pixie-Takt vollständig. Ein Agent, der nie läuft, ist so gut wie keiner.

## 6. ZIEL / TEST / MESSUNG

| | |
|---|---|
| **ZIEL** | Nach einem Lauf stehen in `wissensluecken` Themen, die Nova angehen und die sie noch nicht kennt — je mit Resonanz, Neuheit und dem daraus gerechneten Vektor. Ein Thema, über das sie danach spricht, verschwindet beim nächsten Lauf aus der Liste. |
| **TEST** | `neugier_vektor` als reine Funktion, ohne LLM prüfbar: Zentrum (Resonanz 0.9, Neuheit 0.1) liegt unter Rand (0.7 / 0.7); Außen (0.1 / 0.9) ebenfalls. Idempotenz: zweimal rechnen liefert bitgleich. Zweiter Lauf mit demselben Thema erzeugt keine zweite Zeile. Fehlerpfade: kein Charakterkern → laut abbrechen statt gegen einen Nullvektor rechnen; leere Kandidatenliste → null Zeilen und eine Log-Zeile, die das benennt. Positiver Zwilling: ein Lauf mit Kandidaten legt Zeilen an. |
| **Gegenprobe** | Den Neuheits-Faktor testweise auf 1.0 festnageln — der Zentrum-vor-Rand-Test muss rot werden. Ohne Neuheit ist der Vektor reine Resonanz und zieht zu dem, was sie längst weiß. |
| **MESSUNG** | Agent auf einem echten Bestand laufen lassen. `SELECT thema, resonanz, neuheit, neugier_vektor FROM wissensluecken ORDER BY neugier_vektor DESC LIMIT 10` — die obersten Themen müssen *plausibel am Rand* liegen: erkennbar ihres, aber nicht bereits besprochen. Dann ein Gespräch über eines davon, erneuter Lauf, und die Zeile muss inaktiv werden oder fallen. |

## 7. Nicht enthalten

**Der Wissensspeicher.** Rechercheergebnisse in Dateien, später über MCP erreichbar, Dokumente und Obsidian-Vault — das ist ein eigenes Subsystem mit eigenem Konzept. Es berührt die Repo-Grenze neu: Der Server erreicht heute ausschließlich `novaberg/`, und Rechercheinhalte sind vom Gespräch abgeleitet. Ein Wissensverzeichnis **muss außerhalb des Git-Roots liegen**, sonst veröffentlicht jeder Commit die gesammelten Inhalte.

**Die Verdrahtung in die Salienz.** `salienz_charakter = max(ziel_grav, emo_grav, neugier_vektor)` folgt, wenn die Lücken stehen.

**Der Traum-Zyklus** aus `thinking-curiosity_k.md` §4 — TR3 bis TR9 bleiben Vision.

## 8. Offen

**Wie viele Saat-Themen je Lauf?** Die Stichprobe aus ihrem Bestand bestimmt, wie breit ein Lauf streut. Noch nicht entschieden.

**Verfall.** Eine Lücke, die über Wochen niemanden interessiert, sollte verblassen — sonst zieht die Tabelle ewig zu Themen, die einmal am Rand lagen. Ob über `aktualisiert_am` und einen Decay wie beim LZG-Gewicht, ist offen.

**Feld-Divergenz.** Wächst ihr Feld über Monate, interessiert sie sich am Ende für alles. `thinking-curiosity_k.md` §11 nennt das und schlägt ein Budget vor — hier nicht entschieden.

**Zusammenhang:** `novaberg-thinking-curiosity_k.md` (Vision) · `novaberg-salienz-berechnung_k.md` §4 (Abnehmer) · `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-gv-strategie_k.md` (GV4, die turn-gebundene Schwester)
