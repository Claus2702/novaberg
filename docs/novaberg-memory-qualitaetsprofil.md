# Novaberg — Die abstrakte Schicht: Qualitätsprofile

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `memory/quality_profile.py` (Prompt, Annahme der Modellantwort, gedeckelter Lauf), `memory/repositories/quality_profile_repository.py` (Speicher), `ei/fascination.py` (Merkmalszug); der Aufrufer ist der achte Schritt des Tageslaufs in `agents/synapsen_decay/agent.py`
**Stand:** 3. September 2026, 21:38 UTC (`date -u`; **Scheibe 1 gebaut und gegen den Bestand gemessen** — **28 Träger, 168 Kanten**, 6,5–8,1 s je Träger. **Die Dominanz kollabiert auf `komplexitaet`: 23 von 25**, was der Handmessung des Konzepts §6.2 widerspricht; die Gegenprobe schließt die Textlänge als Ursache aus. Ein Defekt dabei gefunden und behoben)
**Pfad:** novaberg/docs/novaberg-memory-qualitaetsprofil.md
**Konzept:** `novaberg-thinking-faszination_k.md` §4 (der Träger), §5 (das gesetzte Vokabular), §6 (die sechs Dimensionen), §10.1 (der Merkmalszug)
**Zustand:** 🟠 gebaut, läuft, **und sein Ergebnis steht unter einem Vorbehalt** — Speicher, Erzeuger und Leser stehen, aber vier der sechs Dimensionen sind an keinem einzigen Träger die stärkste

---

## 1. Aufgabe

Ein Träger, der oft genug wiedergekehrt ist, bekommt eine Bewertung auf sechs
Qualitätsdimensionen. Aus diesen sechs Zahlen rechnet der **Merkmalszug** einen Wert — den
zweiten von neun Faktoren der Faszination (Konzept §10.6).

**Der Träger ist nicht die Entität.** Wer sich für ein Werkzeug fasziniert und ein
baugleiches daneben aufnimmt, fasziniert sich für dasselbe; die Zuwendung erbt der Zwilling
nicht. Deshalb hängt die Faszination an einem Merkmalsprofil und nicht an einem Gegenstand.

**Heute ist der Träger ein LZG-Knoten.** Entitäten und Themen sind vorgesehen und nicht
gebaut — die erste Scheibe nimmt den Knoten, weil §6.2 den Dimensionssatz genau daran
geprüft hat.

## 2. Position

Der Erzeuger sitzt **nicht** im Turn, sondern als achter Schritt im Tageslauf des
`SynapsenDecayAgent`:

```
Knoten-Decay → pipeline_log-TTL → Queue-Verfall → Prägungs-Faltung
  → Strang-Nachzug → Strang-Richtungen → Einfärbung → **Qualitätsprofile**
```

**Der Grund ist die Sorte der Größe.** Ein Profil beschreibt den Gegenstand und ändert sich
zwischen zwei Tagen nicht; es entscheidet nichts, was der Turn braucht. Der Turn-Pfad liest
es später — er erzeugt es nicht.

**Gedeckelt auf 20 Träger je Lauf.** Am 03.09.2026 standen 368 Kandidaten im Bestand, und
ebenso viele Modellaufrufe passen nicht in einen Heartbeat-Platz. Bei diesem Deckel füllt
sich der Bestand in rund drei Wochen, und ein Ausfall kostet einen Tag statt eines Laufs.

## 3. Das Schema — zwei Tabellen, und warum sie eigene sind

```
abstrakt_knoten     art ('qualitaet' | 'wert'), name, beschreibung, herkunft
traeger_qualitaet   knoten_id → lzg_knoten, qualitaet_id → abstrakt_knoten,
                    auspraegung [0..1], quelle, haeufigkeit
```

**`art` ist der Typ-Diskriminator, und er ist kein Ordnungsmerkmal.** Ohne ihn sickert die
Valenz von der Werte- auf die Qualitätsseite (Konzept §4.4), und Kriegsgeschichte trüge
weniger Faszination als Gartenkräuter — der Fehler wäre fest im Schema verbaut.

| | Werte-Kante (`lzg_knoten_haltung.ladung`) | Qualitäts-Kante (`traeger_qualitaet.auspraegung`) |
|---|---|---|
| Vorzeichen | **ja**, −1,0 bis +1,0 | **nein**, 0,0 bis 1,0 |
| Aussage | normativ: was gelten soll | deskriptiv: wie viel wovon |
| Revidierbar | ja, mit Wegfall der Prämisse | nein — sie beschreibt den Gegenstand |

### 3a. Die Abweichung vom Konzept, und ihr Messwert

Konzept §4.4 legt Qualitäts- und Werte-Knoten in dieselbe Schicht wie `opinion_k`, und
`lzg_knoten_haltung.praemisse_knoten_id` zeigt auf `lzg_knoten`. **Die abstrakten Knoten
liegen trotzdem in einer eigenen Tabelle.**

`[gemessen]` 03.09.2026: **24 Stellen in 13 Modulen** lesen aus `lzg_knoten`, **22 davon
nach Kriterien statt nach `id`** — Enricher, emotionale Gravitation, Spreading,
Charakter-Agent, Wissenslücken, Gravitation, Re-Embedding. Sechs abstrakte Knoten dort wären
aus jeder einzelnen auszuschließen, und ein vergessener Ausschluss ist ein stiller Fehler:
eine Qualität, die im Spreading als Erinnerung auftaucht.

**Der Preis des Umzugs ist null:** `lzg_knoten_haltung` trägt 0 Zeilen, `praemisse_knoten_id`
ist nie benutzt worden. §6.1 stützt es zusätzlich — `neuheit` wurde ausdrücklich
ausgesondert, weil es *„die Lage im Graphen"* ist. Die sechs Dimensionen sind es gerade
nicht.

**Zwei Zustände genügen, nicht drei.** §4.5 verlangt für die **Wert**-Kante
anwesend/abwesend/ungeprüft. Hier trägt die Zeilenanwesenheit dieselbe Unterscheidung: Ein
Profillauf schreibt alle sechs Dimensionen auf einmal, also heißt keine Zeile *ungeprüft*
und `auspraegung = 0.0` *gemessen abwesend*.

**Nebenbefund:** `lzg_knoten.dimension` trägt bereits eine Inhaltskategorie (kognition,
kontext, emotion, …) und darunter ausgerechnet den Wert `werte` — **161 Zeilen** am
03.09.2026. Wer sie als Knotentyp liest, bekommt 161 Episoden als Werte-Knoten.

## 4. Die Kandidaten

`candidates_load`: `aktiv` **und** `haeufigkeit >= 2` **und** `length(inhalt) >= 400` **und**
noch keine Kante. Die häufigsten zuerst.

**Profiliert wird erst, was wiedergekehrt ist** (Konzept §6.3) — man fragt sich nicht beim
ersten Mal, was einen an einer Sache fasziniert. Der Längenfilter trifft fast dieselbe Menge
wie eine Formklassifikation: Die Sachtexte sind mehrere hundert Wörter, die
Sprechakt-Vermerke ein bis zwei Sätze.

`[gemessen]` 03.09.2026 über 3318 Knoten: Wiederkehr ≥ 2 allein trifft **1538**, Länge ≥ 400
allein **1283**, beide zusammen **368**.

## 5. Der Merkmalszug — ein weiches ODER

```
merkmalszug = m_max + 0,35 × Mittel(übrige fünf)        # 0,0 … 1,35
```

**Die stärkste Dimension trägt allein und vollständig; Kombination ist ein Zuschlag, keine
Bedingung.** Beide naheliegenden Formen sind falsch, aus verschiedenen Gründen:

- **Ein Mittelwert** gäbe bei einer Dimension auf 1,0 und fünf auf 0 den Wert **0,17** — der
  Zauberer bekäme keine Faszination, obwohl gerade seine Ungewissheit sie trägt.
- **Ein Produkt** verstieße gegen Regel (a) aus §10.0: Keine Null aus einer Multiplikation.

Die Obergrenze 1,35 ist durch Konstruktion erreichbar (alle sechs auf 1,0) und wird deshalb
nicht gekappt — was darüber läge, wäre ein Rechenfehler.

## 6. Was gemessen ist

### 6a. Der Erstlauf, 03.09.2026, 21:20–21:30 UTC

Die Vorhersage wurde vor dem ersten Kandidaten aufgeschrieben, die Rohdaten liegen bei den
Messreihen dieses Projekts.

| | |
|---|---:|
| Träger versucht (drei Läufe) | 29 |
| profiliert | **25** |
| Bestand danach | **25 Träger, 150 Kanten** |
| Dauer je Träger | 6,5 bis 8,1 s |
| Merkmalszug | **1,0350 bis 1,2100** |

**Sechs Vorhersagen, drei getroffen.** Ohne Ausschlag 0 (vorhergesagt 0–2) ✅ ·
`bedrohungsrelevanz` 0 (≤ 2) ✅ · kein Merkmalszug 0,0 ✅ · `schemasprengung`+`konflikt` **0**
statt ≥ 8 ❌ · 4 Fehlschläge statt ≤ 3 ❌ · **und der Kollaps** ❌.

### 6b. Der Vorbehalt: die Dominanz kollabiert auf `komplexitaet`

**23 von 25 Trägern sind dominant `komplexitaet`, die übrigen zwei `weite`.** Vier der sechs
Dimensionen sind an keinem einzigen Träger die stärkste.

Das widerspricht der Handmessung in Konzept §6.2 unmittelbar. Dort stand nach 50 von Hand
bewerteten Knoten: *„Der Satz trägt. **Kein Kollaps auf `komplexitaet`.**"* — und
`komplexitaet` war mit **2 von 26** die zweitschwächste Dimension.

**Die naheliegende Erklärung ist widerlegt.** Der Verdacht war, `komplexitaet` messe die
Textlänge; vier kurze Texte bekannter Komplexität, alle unter der Filterschwelle:

| Probe | Zeichen | kompl | weite |
|---|---:|---:|---:|
| *„Der Mülleimer steht neben der Tür."* | 34 | **0,0** | 0,0 |
| ein Zahnarzttermin | 125 | **0,0** | 0,0 |
| Page-Kurve, Informationsparadoxon | 203 | **1,0** | 1,0 |
| Leerräume zwischen Galaxienhaufen | 139 | **0,5** | **1,0** |

Ein 203-Zeichen-Text bekommt 1,0, ein 125-Zeichen-Text 0,0; und `weit-kurz` trennt `weite`
von `komplexitaet` bei fast gleicher Länge wie der triviale. **Die Dimensionen trennen
innerhalb eines kurzen Textes, und die Skala kann Null sagen.**

**Zwei Erklärungen stehen noch, und diese Messung trennt sie nicht:**

1. **Der Korpus ist homogen.** Der Filter wählt die oft reaktivierten langen Sachtexte, und
   die sind bei diesem Paar durchweg Astrophysik und Systemtheorie. Sie *sind* alle komplex.
2. **Modell und Mensch bewerten verschieden.** §6.2 ist eine Handbewertung durch eine
   Person, dieser Lauf eine Modellbewertung.

> **Die Messung, die sie trennt, ist nicht gemacht:** dieselben Knoten maschinell **und** von
> Hand, Zeile für Zeile. Die Handmessung liegt nur als Verteilung vor, nicht als Liste.

**Was nicht behauptet wird:** dass der Satz falsch ist. Vier Dimensionen ohne dominanten
Träger sind ein Warnzeichen und kein Urteil — bei 25 Trägern aus einer gefilterten Ecke eines
einzigen Paares.

### 6c. Der Defekt, den die Messung fand und der behoben ist

Alle vier Fehlschläge des zweiten Laufs trugen **dieselbe Ursache**: Das Modell schrieb
`"un gewissheit"` statt `"ungewissheit"` — ein Leerzeichen in einem Bezeichner, den es
wörtlich vorgegeben bekam. Die Kanon-Prüfung machte es in einem Zug sichtbar.

Behoben durch eine Normalisierung, die **nur Leerraum** abräumt, ihre Zeile ins Log schreibt
und die Kanon-Prüfung darunter scharf lässt. **Im Bestand belegt:** die drei erneut gezogenen
Träger sind profiliert, 6 von 6, 0 gescheitert.

> **Ohne die Behebung wäre der Träger dauerhaft verloren:** Der nächste Lauf sieht ihn ohne
> Kanten, ruft dasselbe Modell und bekommt dasselbe Leerzeichen.

### 6d. Die zweite Kontrolle — der Betrieb statt der Zeugen

**Der gewählte Zugriff war einer, den der Bau nicht benutzt hat.** Der Erstlauf rief
`traeger_profilieren` je Kandidat direkt; **`profil_lauf` selbst** — die Funktion, die der
Tageslauf ruft — war bis dahin **nur gegen Mocks bezeugt**.

`[gemessen]` 03.09.2026, 21:38 UTC, gegen den echten Bestand mit Deckel 3:

```
{'versucht': 3, 'profiliert': 3, 'gescheitert': 0,
 'traeger_gesamt': 28, 'kanten_gesamt': 168, 'error': None}
```

Die Buchführung geht auf, der Deckel greift, `qualities_load` und `candidates_load` liefern
gegen das echte Schema. **Die Dominanz bleibt: 26 von 28 `komplexitaet`.**

> **Und die Kontrolle hat eine Lücke gefunden, die sie nicht schließen konnte: Der
> Betriebsbeleg über den Tageslauf steht aus.** `hintergrund_log` zeigt den letzten
> `synapsen_decay`-Lauf am **03.09.2026 um 19:58 UTC** — anderthalb Stunden **vor** diesem Bau.
> Der Lauf ist täglich; der erste, der den achten Schritt enthält, ist der vom **04.09.2026**.
>
> Damit ist die Verdrahtung **bezeugt** (`test_invoke_ruft_den_profillauf`) und **nicht im
> Betrieb belegt** — genau die Trennung, die an dieser Schicht schon dreimal der Befund war.

## 7. Die Annahme der Modellantwort

Die Antwort eines Sprachmodells ist die unzuverlässigste Quelle im System. Fünf Prüfungen,
jede mit eigener Meldung:

| Prüfung | Verworfen wird |
|---|---|
| leer | eine leere Antwort — sie ist **kein** Profil aus lauter Nullen |
| JSON | kein Objekt, oder gar kein JSON (Codezaun wird abgeräumt) |
| Leerraum in Schlüsseln | **nicht** verworfen, sondern laut zusammengezogen (§6c) |
| Schlüsselsatz | gegen den **Kanon**, nicht gegen eine Teilmenge |
| Werte | außerhalb 0,0/0,5/1,0 — **verworfen, nicht gerundet** |

**Gegen den Kanon und nicht gegen eine Teilmenge:** Ein erfundener Dimensionsname und ein
gültiges *„trifft nicht zu"* wären sonst dasselbe Ergebnis. **Nicht gerundet:** Eine stille
Rundung machte eine erfundene Skala von der vorgegebenen ununterscheidbar — und daran hängt
die Aussage, dass das Modell drei Stufen benutzt und nicht heimlich eine eigene.

## 8. Die Zeugen

`tests/test_quality_profile_schema.py` (6) · `tests/test_quality_profile.py` (32).

Der Schematest ist **der Zünder** und importiert nichts aus dem Bauteil — die rote
Phase war 6 von 6, `relation "abstrakt_knoten" does not exist`.

**Gegenprobe: 3 vorhergesagt, 3 gezählt** (`MERKMALSZUG_BONUS` auf 0.0). Sie fand dabei einen
Zeugendefekt: Die erste Fassung bezog ihre Erwartung aus der Konstante, die sie prüfen sollte,
und ließ **alle 37 grün**. Die Literale stehen jetzt ausgeschrieben.

## 9. Was fehlt

- **Ein Leser des Merkmalszugs.** Er rechnet und niemand liest ihn — dieselbe Lage wie beim
  Prägungszug und der Einfärbung. Der Verbraucher ist §10.6, und der braucht `bindung_roh`
  und die sechs Turn-Modulatoren.
- **`bindung_roh`** (§10.2): drei Zähler am Träger — Wiederkehr, Verweildauer, Eigenimpuls.
- **Die sechs Turn-Modulatoren** (§10.5). Reine Funktionen, ohne Träger baubar.
- **Der Verfall der Qualitäten** (§10.4). Je Dimension verschieden: `ungewissheit` verfällt
  mit der **Zahl der Berührungen**, alle übrigen mit der **Zeit**. Nicht gebaut, und er gehört
  an den Leser, nicht an den Speicher.
- **Die Werte-Seite der abstrakten Schicht.** `abstrakt_knoten` trägt `art = 'wert'` im
  Schema und keine Zeile; sie ist das, worauf `praemisse_knoten_id` wartet.
- **Entitäten und Themen als Träger.** Heute nur LZG-Knoten.
- **Die Stabilität eines Profils.** Zwei Läufe über denselben Träger sind nicht verglichen;
  bei Temperatur 0,0 wäre Gleichheit zu erwarten, gemessen ist sie nicht.
