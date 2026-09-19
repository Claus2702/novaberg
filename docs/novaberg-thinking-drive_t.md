# Novaberg — Antrieb (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md) · Bauplan und Umstellung: [`novaberg-thinking-drive_b.md`](novaberg-thinking-drive_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-drive_e.md`](novaberg-thinking-drive_e.md) · Messungen: [`novaberg-thinking-drive_m.md`](novaberg-thinking-drive_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

Der bisherige Kopf des ungeteilten Konzepts steht in [`novaberg-thinking-drive_m.md`](novaberg-thinking-drive_m.md).

---

## Aus §5 — Gravitation

Die übrigen Unterabschnitte von §5 stehen in [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md).

### 5.2 Berechnung in Python

> **Hinweis zur Aufteilung (19.09.2026):** Der erste Satz ist Absicht (Rechnung in Python, nicht im Modell) und gilt für `_k` §5 mit; der Abschnitt steht wegen Rechenweg und Optimierungen hier.

**Berechnung in Python, nicht im LLM.** Die semantische Nähe zwischen aktuellem Thema und Zielsätzen lässt sich über Embeddings berechnen. Cosine-Similarity zwischen dem Themen-Embedding des aktuellen Turns und den Embeddings der Zielsätze. Das ist eine reine Python-Operation — kein LLM-Call nötig.

```
Für jeden aktiven Zielsatz:
  motivation  = aus Anker und Alter gerechnet (ziele_live_bewerten, seit 28.08.2026) —
                nicht das Feld vom letzten Tageslauf; unter ZIEL_DEAKTIVIERUNGS_SCHWELLE
                kommt das Ziel gar nicht erst hierher
  similarity = cosine_similarity(turn_embedding, ziel_embedding)
  gravitation = similarity × motivation

  Wenn gravitation > GRAVITATIONS_SCHWELLE
     oder ziel_typ == 'kurzfristig' (seit 28.08.2026, §3.3 — sein Tor ist der Verfall):
    → Zielsatz wird als "aktiviert" markiert (kurzfristige zuerst, dann nach Stärke)
    → Wird dem GV-Node und der Salienz als Kontext mitgegeben
```

**Performance-Optimierung:** Bei maximal 7 aktiven Zielsätzen (2 langfristig + 5 mittelfristig) fallen 7 Cosine-Similarity-Berechnungen pro Turn an. Das ist unkritisch (Vektoroperationen auf 768-dimensionalen Embeddings sind µs-schnell), aber zwei Optimierungen vermeiden unnötige Arbeit:

1. **Turn-Embedding cachen:** Das Themen-Embedding des aktuellen Turns wird im Session-State gespeichert. Solange das Thema nicht wechselt, wird es nicht neu berechnet.
2. **Gravitation nur bei Themenwechsel:** Wenn die Salienz-Themen des aktuellen Turns identisch zu den vorherigen sind (kein Themenwechsel), werden die Gravitationsergebnisse aus dem Session-State wiederverwendet. Erst bei Themenwechsel wird neu berechnet.
3. **Ziel-Embeddings vorberechnet:** Die Embeddings der Zielsätze werden beim Schreiben in die Tabelle berechnet und gespeichert — nicht bei jedem Turn.

### 5.3 Gravitationseinfluss auf die Salienz

> **Hinweis zur Aufteilung (19.09.2026):** Die Absicht — ein zielrelevanter Turn wird bevorzugt gespeichert — steht im letzten Absatz und in `_k` §5.1; der Abschnitt steht wegen Rechnung und Berichtigung hier. §8.2 in [`novaberg-thinking-drive_b.md`](novaberg-thinking-drive_b.md) nennt noch die ersetzte Addition (Befund B1 in `_e`).

Die Salienz-Berechnung läuft heute rein auf dem aktuellen Turn: Thema, Emotion, Wiederholung, Gedächtnistyp. Der Gravitationsterm erweitert die Berechnung:

> ~~**Die Addition unten ist am 09.09.2026 ausgebaut.**~~ Sie unterstellt einen Term, der
> klein gegen 1 bleibt — das Beispiel rechnet mit **einem** Ziel. Der Term ist aber die
> **Summe über alle** aktivierten Ziele und erreichte gemessen **5,9955**; von 498 Boosts
> trugen **277 (55,6 %)** einen Term ≥ 1,0, und dort stand die Salienz danach **immer** auf
> 1,0 — unabhängig davon, was das Modell bewertet hatte (Basis im Mittel 0,327).
>
> **Seither: der Term ist normiert** (`sin^0.5`, Cap aus der gemessenen Spanne abgeleitet),
> und die Addition ist durch die **Auffüllregel** ersetzt:
> `neu = basis + term × (1 − basis)`. Sie hebt immer, senkt nie und geht nie über 1 —
> ohne Kappung (`F-NAHT-1`). Geführt als `GRAVITATIONSTERM-OHNE-OBERGRENZE`.
>
> Das Beispiel darunter bleibt stehen, weil es die **Absicht** richtig beschreibt: Ein
> zielrelevanter Turn wird bevorzugt gespeichert. Nur seine Rechnung gilt nicht mehr.

```
salienz_final = salienz_basis + gravitationsterm      ← ersetzt am 09.09.2026

Beispiel Basilikumpflanze:
  salienz_basis = 0.4 (einmalige, sachliche Erwähnung)
  Ziel "Botanik und Kräuter" → Motivation 0.8, Similarity 0.85
  gravitationsterm = 0.8 × 0.85 × GRAVITATIONS_SALIENZ_FAKTOR
  salienz_final = 0.4 + 0.34 = 0.74 → hohe Salienz, KZG mit langer TTL

Beispiel "Ich war heute einkaufen":
  salienz_basis = 0.3
  Kein Ziel mit hoher Similarity
  gravitationsterm = 0.0
  salienz_final = 0.3 → niedrige Salienz, kein KZG-Eintrag
```

Damit werden zielrelevante Informationen bevorzugt gespeichert — genau wie beim Menschen, der sich an den Kräutertopf erinnert, aber das Einkaufen vergisst. Klingers Current Concerns als algorithmischer Salienz-Boost.

---

## Aus §6 — Dual-Emotion-Architektur

Die übrigen Unterabschnitte von §6 stehen in [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md).

### 6.6 Speicherung der Dual-Emotion

Pro Turn werden im Session-Gedächtnis beide Emotionszustände gespeichert:

| Feld | Beschreibung |
|------|-------------|
| `nutzer_emotion` | Emotion des Nutzers (aus Perzeption) — existiert |
| `nutzer_arousal` | Arousal des Nutzers — existiert |
| `nova_emotion` | Novas Position im 8-dim Plutchik-Raum (8 Floats) — **neu** |
| `nova_arousal` | Novas Arousal-Level (abgeleitet aus Vektorbetrag) — **neu** |
| `emotion_konflikt` | Boolean — Ziel- und Nutzer-Vektor divergieren — **neu** |

Im KZG wird der Eintrag mit beiden Emotionen annotiert. Novas Emotionsvektor wird zwischen Turns im Session-State mitgeführt als persistenter Wert mit eigenem Decay pro Dimension.

---

## 7. Speicherung: Zieltabelle

> **Hinweis zur Aufteilung (19.09.2026):** Der Kasten *„Widerlegt am 02.08.2026“* trägt eine Absicht — ein Ziel gehört einer Beziehung — und ist in `_e` als E2 geführt; der Abschnitt ist Datenmodell und steht deshalb hier.

Ziele sind keine Fakten und kein normales KZG. Sie brauchen eine eigene Tabelle, weil sie semantisch etwas anderes sind — ein Fakt informiert, ein Ziel zieht. Und weil der GV-Node und der Pixie-Router sie gezielt laden müssen, getrennt vom Wissensbestand. Alle Einträge sind `user_id="nova"` — es sind Novas Gedanken, nicht die des Nutzers.

> **Widerlegt am 02.08.2026 (Chat 125): Ein Ziel gehört einer Beziehung, nicht Nova allein.** Der Satz oben bleibt in seinem ersten Teil richtig — das Subjekt ist immer Nova. Was fehlte, ist das Gegenüber. Die Destillation liest das Kurzzeitgedächtnis **genau eines Paares** und leitet daraus ab, was Nova langfristig will; das Ergebnis ist damit eine Aussage über Nova *in dieser Beziehung*.
>
> Sichtbar wurde es erst mit dem zweiten Paar: Vor dem Schreiben deaktiviert die Destillation **alle** aktiven langfristigen Ziele. Bei einem Paar ist das die vorgesehene Fortschreibung, bei zweien ein Wettlauf, den der zuletzt destillierte gewinnt — und der Enricher legte das Ergebnis anschließend jedem Turn in den Prompt, gleich aus welcher Beziehung es stammte.
>
> Die Tabelle trägt seither `character_id` (Gegenüber) nach `novaberg-convention-paar-schema.md` §2. Der Bestand von 91 Zeilen wurde auf `(nova, meister)` migriert.

### 7.1 Tabelle `ziele`

Eine Tabelle für beide Zeithorizonte. Der `ziel_typ` bestimmt das Decay-Verhalten: Langfristige Ziele haben keinen Decay (werden nur bei Charakter-Destillation aktualisiert), mittelfristige Ziele verblassen über Zeit.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `id` | SERIAL | Primärschlüssel |
| `user_id` | TEXT | Subjekt — immer "nova" |
| `character_id` | TEXT | Gegenüber — der Mensch der Beziehung (Chat 125). **Kein Default:** Ein Schreiber ohne Gegenüber scheitert an `NOT NULL`, statt eine leere Zeichenkette abzulegen |
| `ziel_typ` | TEXT | `langfristig` oder `mittelfristig` |
| `zielsatz` | TEXT | Formulierte Absicht (1–2 Sätze) |
| `thema` | TEXT | Themen-Stichwörter |
| `motivation` | FLOAT | 0.0–1.0 (dynamisch bei mittelfristig, stabil bei langfristig) |
| `valenz` | TEXT | positiv / negativ / neutral |
| `emotion` | TEXT | Spezifische Emotion (neugierig, besorgt, begeistert, ...) |
| `embedding` | VECTOR | Embedding des Zielsatzes (nomic-embed-text, vorberechnet) |
| `erstellt_am` | TIMESTAMP | Zeitpunkt der Erstellung |
| `aktualisiert_am` | TIMESTAMP | Letzte Aktualisierung ~~(Decay-Referenz für mittelfristig)~~ — **kein Decay-Bezug mehr, siehe unten** |
| `motivation_basis` | FLOAT | Anker des Verfalls: der zuletzt *gesetzte* Motivationswert (Chat 113) |
| `motivation_basis_am` | TIMESTAMP | Zeitpunkt dieser Setzung. Wird nur gemeinsam mit dem Anker geschrieben |
| `quelle` | TEXT | Herkunft (charakter_destillation / recherche / vertiefen / traeumen) |
| `herkunftsthema` | TEXT | Ursprüngliches Queue-Thema (nur mittelfristig) |
| `datei_pfad` | TEXT | Pfad zur Wissens-Datei (nur mittelfristig) |
| `aktiv` | BOOLEAN | Für Decay-Management |

**Decay-Berechnung (korrigiert Chat 113):** ~~Mittelfristige Ziele verwenden `aktualisiert_am` als Referenz.~~ Das war zum Zeitpunkt der Niederschrift gedacht, aber untauglich: `aktualisiert_am` wird von **jedem** Schreiber gesetzt, auch vom Decay-Lauf selbst, der damit seine eigene Zeitbasis zurücksetzte. Ein Anker braucht seinen eigenen Zeitstempel, der nur mit ihm zusammen geschrieben wird.

```
motivation = motivation_basis × exp(−ln2 / ZIEL_MITTELFRISTIG_DECAY_TAGE × tage_seit_motivation_basis_am)
```

~~`motivation` bleibt das **materialisierte** Feld, das jede Abfrage liest — einmal rechnen, hundertmal lesen, dieselbe Rollenteilung wie `gewicht_decay` im LZG.~~ → **Widerlegt am 28.08.2026, an der Zeitskala:** Der Tageslauf (`PIXIE_DECAY_INTERVALL_SEKUNDEN` = 86400, gemessen im `hintergrund_log`: 25.–27.08. je ~19:58 UTC) hinkt bei 14 Tagen Halbwertszeit höchstens 5 % hinterher — bei 3 Stunden bis zu acht Halbwertszeiten. Ein Wert ist so frisch wie sein Takt, und für das kurzfristige Ziel entscheidet er allein (§5.2). **Seither rechnet `ziele_aktive_laden` die Motivation beim Lesen** aus `motivation_basis` und `motivation_basis_am` (`ziele_live_bewerten`, dieselbe Formel `motivation_berechnen`, für jeden Typ mit Halbwertszeit — `halbwertszeit_tage_fuer_typ`) und liefert nichts unter `ZIEL_DEAKTIVIERUNGS_SCHWELLE` (0,15, seit dem Abend in `config.py`). Das Feld bleibt materialisiert und der Tageslauf bleibt: Er schreibt es für Leser, die nicht rechnen, und legt `aktiv` um. Der Lauf schreibt es neu und ist trotzdem kein Akkumulator, weil er aus Anker und Zeit rechnet und nie aus dem vorherigen Wert. Zehn Läufe hintereinander liefern denselben Stand wie einer; gar nicht zu laufen macht den Wert veraltet, nicht falsch — und genau deshalb liest die Gravitation ihn nicht mehr. `[gemessen]` 28.08.2026, 19:52 UTC: sieben aktive Zeilen des Paares, der Lader lieferte fünf; zwei mittelfristige lagen live bei 0,148 und 0,146 unter der Schwelle, im Feld bei 0,153 und 0,155 vom Vortag.

**Wer die Motivation setzt, setzt den Anker** — nicht den Momentwert. Damit beginnt die Vergessenskurve von vorn, genau wie `knoten_verstaerken` im LZG `verstaerkt_am` zurücksetzt: Ein Ziel wieder aufzugreifen *ist* seine Verstärkung.

**Nur `mittelfristig` ~~verfällt~~ und — seit dem 28.08.2026 — `kurzfristig` verfallen**, je als Allowlist geprüft und mit eigener Halbwertszeit (14 Tage / 3 Stunden), ein Lauf je Typ. Die frühere Fassung übersprang lediglich `langfristig` und hätte damit jeden anderen Typ mit der mittelfristigen Halbwertszeit behandelt — auch `kurzfristig`, das es ~~heute nicht gibt und morgen geben kann~~ seit dem 28.08.2026 gibt (§3.3).

**Abfrage-Pattern:** `SELECT * FROM ziele WHERE aktiv = TRUE AND user_id = 'nova'` lädt alle aktiven Ziele beider Typen in einem Query. Der Enricher filtert dann in Python nach Similarity.

### 7.2 Pixie-Output: Wissens-Datei + Metadaten

Jede Pixie-Aktivität produziert ein Tripel:

1. **Wissens-Datei:** Der Fließtext — Rechercheergebnisse, Destillat, Vertiefung. Gespeichert als Datei (wie bisher).
2. **Zielsatz:** Formulierte Absicht mit angepasster Motivation und Emotion. Gespeichert in `ziele` mit `ziel_typ = 'mittelfristig'`.
3. **KZG-Eintrag:** Wissens-Kern mit Salienz, wie bisher. Aber die Salienz ist jetzt bereits durch den Gravitationsterm beeinflusst.

---

## 11. Konfigurationsparameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `GRAVITATIONS_SCHWELLE` | float | 0.40 | Minimum-Gravitation, ab der ein Ziel aktiviert wird. Historie: 0.3 (Konzept) → 0.75 (Chat 69) → 0.60 → **0.40** (Chat 107, Rekalibrierung auf `nomic-embed-text-v2-moe` — im alten casing-blinden Raum lag 0.60 unter dem Grundrauschen 0.74 und feuerte immer). **Gilt nicht für `kurzfristig`** (28.08.2026, gemessen): Dessen Zielsatz liegt zur Nutzeräußerung bei Kosinus 0,13–0,41, Stärke 0,09–0,29 — die Schwelle hätte es nie passiert. Es ist per Bauart aktiviert, solange es lebt; die Zahlen bleiben echt |
| `GRAVITATIONS_SALIENZ_FAKTOR` | float | 0.5 | Skalierungsfaktor für den Salienz-Boost |
| `NOVA_EMOTION_DECAY` | float | 0.85 | Decay-Rate für Novas Emotion pro Turn (→ Neutralität, pro Dimension) |
| `NOVA_EMPATHIE_BENACHBART` | float | 0.15 | α bei Sektor-Distanz 0–1 (gleichgerichtete Emotionen bestätigen leicht) |
| `NOVA_EMPATHIE_GEGENUEBER` | float | 0.8 | α bei Sektor-Distanz 3–4 (gegenüberliegende Emotionen überschreiben stark) |
| `NOVA_EMOTION_KONFLIKT_SCHWELLE` | float | -0.3 | Cosine-Similarity zwischen Ziel- und Nutzer-Vektor, ab der ein Konflikt-Flag gesetzt wird |
| `ZIEL_MITTELFRISTIG_DECAY_TAGE` | int | 14 | Halbwertszeit mittelfristiger Ziele in Tagen |
| `ZIEL_MAX_MITTELFRISTIG` | int | 5 | Maximale Anzahl aktiver mittelfristiger Ziele |
| `ZIEL_MAX_LANGFRISTIG` | int | 2 | Maximale Anzahl langfristiger Ziele |
| `EMOTIONALE_GRAVITATIONS_SCHWELLE` | float | 0.40 | Minimum-Gravitation, ab der eine emotionale Erinnerung aktiviert wird. Historie: 0.5 → **0.40** (Chat 107, Rekalibrierung auf `nomic-embed-text-v2-moe`) |
| `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT` | int | 180 | Halbwertszeit emotionaler Gravitation in Tagen |
| `EMOTIONALE_GRAVITATION_MAX_PRO_TURN` | int | 2 | Maximale Anzahl aktivierter emotionaler Erinnerungen pro Turn |
| `EMOTIONALE_GRAVITATION_FAKTOR_SESSION` | float | 1.0 | Quellen-Faktor für Session-Einträge (frisch, voll wirkend) |
| `EMOTIONALE_GRAVITATION_FAKTOR_KZG` | float | 0.8 | Quellen-Faktor für KZG-Einträge (leicht gedämpft) |
| `EMOTIONALE_GRAVITATION_FAKTOR_LZG` | float | 0.5 | Quellen-Faktor für LZG-Einträge (stärker gedämpft) |

**Alle Schwellwerte sind Startwerte und müssen empirisch kalibriert werden.** Insbesondere `GRAVITATIONS_SCHWELLE` (0.3 bei Cosine-Similarity könnte zu viel Rauschen erzeugen) und die Empathie-Faktoren (bestimmen, wie asymmetrisch Novas Emotion dem Nutzer folgt) sollten über mehrere Hundert Turns beobachtet und angepasst werden. Zielmetrik für Gravitation: Pro Turn werden durchschnittlich 0.5–2.0 Zielsätze aktiviert. Wenn regelmäßig >3 aktiviert werden, ist die Schwelle zu niedrig. Die Empathie-Werte zwischen `NOVA_EMPATHIE_BENACHBART` und `NOVA_EMPATHIE_GEGENUEBER` werden über die Sektor-Distanz interpoliert — die bestehende Distanzfunktion aus `novaberg-ei-plutchik.md` liefert den Faktor.

---

→ Absicht: [`novaberg-thinking-drive_k.md`](novaberg-thinking-drive_k.md)
→ Bauplan und Umstellung: [`novaberg-thinking-drive_b.md`](novaberg-thinking-drive_b.md)
→ Diskussion und Ergänzungen, Befunde: [`novaberg-thinking-drive_e.md`](novaberg-thinking-drive_e.md)
→ Messungen: [`novaberg-thinking-drive_m.md`](novaberg-thinking-drive_m.md)
