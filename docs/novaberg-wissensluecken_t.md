# Novaberg — Wissenslücken: der Zug zu einem Thema (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-wissensluecken_k.md`](novaberg-wissensluecken_k.md) · Bauplan und Umstellung: [`novaberg-wissensluecken_b.md`](novaberg-wissensluecken_b.md) · Diskussion und Ergänzungen: [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

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

**Das Paar ist Pflicht.** ~~`ziele` trägt heute nur `user_id`,~~ `charakter_anweisungen` ebenso — bei mehreren Nutzern und Charakteren bricht beides. Diese Tabelle macht es von Anfang an richtig; die anderen zwei bleiben Vorbestand und gehören in die Fundliste.

> **Zur Hälfte erledigt am 02.08.2026 (Chat 125):** `ziele` trägt jetzt `character_id`. Der Anlass war der hier vorhergesagte: das zweite Paar. `charakter_anweisungen` steht unverändert.

Der `UNIQUE`-Schlüssel macht den Lauf idempotent: Dasselbe Thema erzeugt keine zweite Zeile, sondern frischt die Bewertung auf.

## 5. Wann er läuft

**Der Anstoß kommt über den Stack, nicht aus dem Agenten.** Das ist die Trennung, die alles Weitere ermöglicht:

| Anlass | Wer stößt an |
|---|---|
| Charakter neu destilliert | `CharakterAgent` am Ende seines Laufs |
| Recherche abgeschlossen | später der Recherche-Pfad — neues Wissen, neue Lücken |
| periodisch | eigener Takt des Agenten |

Weil der Anstoß nicht am Charakter hängt, kann **jeder** Wissenszuwachs eine Neuberechnung auslösen. ~~Eine Lücke schließt sich dann nicht, weil jemand sie für geschlossen erklärt, sondern weil sie beim nächsten Lauf den Filter nicht mehr passiert.~~

> **Am 12.09.2026 gemessen und widerlegt — in zwei Schritten.**
>
> **Erstens findet der „nächste Lauf" für eine alte Zeile nicht statt.** Der Agent bewertet die zwanzig neuen Kandidaten eines Laufs; eine bestehende Zeile nur, wenn ein Kandidat ihr zufällig gleicht. `[gemessen]` **114 von 1888** Zeilen (6,0 %) sind je ein zweites Mal angefasst worden, die älteste stammt vom 27.07.2026, geschlossen war keine.
>
> **Zweitens trägt der Filter die Unterscheidung nicht.** `[gemessen, je 120 Stichproben]` Ein Thema, das Nova **nachweislich kennt**, erreicht als höchste Ähnlichkeit zum Bestand im Median **0,490**, ein offenes Lückenthema **0,441**; Thema gegen Thema 0,500 gegen 0,473. **Die Verteilungen überlappen fast vollständig** — und das ist kein Messfehler, sondern die Bauart: Die Lücken sind *Nachbarthemen* bekannter Themen, sie **sollen** ähnlich sein. Eine Schwelle darauf schlösse alles oder nichts.
>
> **Was seither schließt, ist der Nachweis statt des Maßes.** Steht das Thema wörtlich unter den Themen ihrer aktiven Langzeit-Knoten, kennt sie es — ohne Schwelle, ohne Embedding, ohne Modellaufruf (`_bekannte_schliessen`). Erster Lauf am 12.09.2026: **125 von 1908** geschlossen, zweiter Lauf 0.
>
> **Die Reichweite ist damit klein, und der Rest ist eine Absichtsfrage:** Wonach eine Lücke zu schließen wäre, die Nova kennt, ohne dass ihr Thema wörtlich in einem Knoten steht, ist offen. Ähnlichkeit ist es nicht.

**Eigener Agent, nicht Anhang am CharakterAgent.** Getrennte Zuständigkeit, eigener Registry-Eintrag.

Seine Priorität ist **bewusst zu setzen, nicht per Default**. Gemessen am 27.07.2026: `CharakterAgent` mit 0.3 kam erst dran, als das Gespräch verstummte, und eine achtminütige Recherche blockierte den Pixie-Takt vollständig. Ein Agent, der nie läuft, ist so gut wie keiner.

## Audit (seit 18.09.2026)

**Der Dienst belegt jeden Lauf selbst** im `hintergrund_log`, unter der Aufgabe `wissensluecken` (`BaseAgent._audit`, `80d4b37`): `gestartet` mit dem Paar, dann `erledigt` mit angelegten, aufgefrischten und verworfenen Lücken oder `fehler` mit dem Abbruchgrund. Eine Ausnahme aus dem Lauf wird dort als `fehler` belegt, nicht weitergeworfen. Der Pixie-Dispatch schreibt nur noch, wenn der Dienst schweigt — eine entkommene Ausnahme oder ein fehlender Agent (`novaberg-convention-nmcp.md` §8.4, Entscheidung vom 18.09.2026).
