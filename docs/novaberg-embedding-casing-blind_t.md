# EMBEDDING-CASING-BLIND (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md) · Bauplan und Umstellung: [`novaberg-embedding-casing-blind_b.md`](novaberg-embedding-casing-blind_b.md) · Diskussion und Ergänzungen: [`novaberg-embedding-casing-blind_e.md`](novaberg-embedding-casing-blind_e.md) · Messungen: [`novaberg-embedding-casing-blind_m.md`](novaberg-embedding-casing-blind_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Tragweite

Betroffen sind **sechs pgvector-Spalten** und **zwei Redis-Formate** (Quelle: Brudi-Audit):

| Speicher | Spalte / Key |
|---|---|
| Postgres | `lzg_knoten.embedding` (302 Zeilen), `langzeitgedaechtnis.embedding` (Legacy), `entitaeten.embedding`, `fakten.embedding`, `ziele.embedding`, `delegations_akten.themen_embedding` |
| Redis | KZG-Hashes `kzg:{user_id}:{character_id}:{id}` — Feld `embedding`, float32-Bytes |
| Redis | Shadow-Stack `shadow_stack:{user_id}` — JSON-Float-Liste |
| Prozess | `_strategie_embeddings_cache` in `ei/dreischicht.py` (Modul-Cache) |
| Abgeleitet | `lzg_kanten.embedding_cosine_initial` — **eingefrorene Alt-Cosines** |

Alles darauf Gebaute lief blind: **Anker-Retrieval, Spreading Activation
(Schale 0!), Magnete/Entitätsauflösung, KZG-Deduplizierung, emotionale Gravitation,
Ziel-Gravitation, Wissenslücken, Delegations-Dedup, Shadow-Delivery.**

### 2.1 `REF-KASKADE` ist keine eigene Baustelle mehr

*„Wir reden 8 Turns über Matcha-Pulver, dann sage ich ‚schauen wir nochmal nach dem
Pulver' — und Nova fragt, ob ich Kakao meine."*

Gemessen unter v1: `sim(Matcha-Pulver, Kakaopulver) = 0.9846`.
`sim(Matcha-Pulver, Paraphrase)` = 0.8172.

> **Die Verwechslung lag näher am Anker als die richtige Antwort.** Das war kein
> Referenzproblem. Das war das Embedding.

Nach dem Wechsel muss REF-KASKADE **neu bewertet** werden. Der Rewriting-Schritt
bleibt sinnvoll (Koreferenz *„das Pulver"* → *„Matcha-Pulver"* ist keine
Embedding-Aufgabe), aber die Dringlichkeit ändert sich.

### 2.2 `KZG-DEDUP` löst sich mit

Die Kalibrierung förderte Dubletten im LZG zutage:

```
0.9254  [150] Der Nutzer lobt die Tiefe, die Worte, die Farben ...
        [151] Der Nutzer mag die Tiefe, die Worte, die Farben ...

0.9135  [102] Lumi stirbt vermutlich bald.
        [103] Lumi wird vermutlich nicht mehr lange leben.
```

`[Herkunft geprüft 19.09.2026: Lumi ist eine Pflanze]`

Paraphrasen desselben Fakts als **getrennte Knoten**. Genau das sollte
`LZG_KNOTEN_MATCH_SCHWELLE = 0.85` verhindern. Passierquote im alten Raum: **0.06 %**.

> **Die Dubletten sind kein eigener Bug — sie sind der Abdruck des blinden Embeddings.**

---

## 3. Der Nachfolger: `nomic-embed-text-v2-moe`

Gemessen auf sechs deutschen Triplets, alle Kandidaten im Vergleich:

| Modell | Casing | Diskriminierung ↑ | Grundrauschen ↓ | **Signal/Rausch** | Dim |
|---|---|---|---|---|---|
| `nomic-embed-text` (IST) | **durchgefallen** | 0.037 | 0.738 | **0.05** | 768 |
| `nomic-embed-text` + `.lower()` | — | 0.121 | 0.612 | 0.20 | 768 |
| **`nomic-embed-text-v2-moe`** | bestanden | 0.391 | **0.155** | **2.52** | **768** |
| `embeddinggemma` | bestanden | **0.450** | 0.236 | 1.91 | 768 |
| `bge-m3` | bestanden | 0.339 | 0.437 | 0.78 | 1024 |

**Entscheidung: `nomic-embed-text-v2-moe`, ohne Task-Präfix.**

- Bestes Signal/Rausch-Verhältnis — **50× über dem IST-Zustand**
- **768 Dimensionen** → kein `ALTER TABLE`, kein Index-Neubau
- 512-Token-Limit: `lzg_knoten` max. 618 Zeichen (p95 = 330) → **Faktor 2,4 Luft**
  > **Nachtrag 19.09.2026 — die Grenze ist belegt, und woher sie kommt.** `[gemessen]` Das betriebene Modell trägt in seinen Metadaten `context_length = 512` (Ollama `/api/show`). Ollamas `/api/embed` kürzt eine längere Eingabe **still am Ende**, solange `truncate` nicht ausdrücklich `false` ist — die Voreinstellung ist `true`, und der Server setzt den Parameter nicht. **Die Modellbeschreibung sagt etwas anderes und gilt hier nicht:** Nussbaum & Duderstadt (2025, arXiv:2502.07972) trainieren mit Segmenten von 2048 Tokens und kürzen nur in einer Auswertung auf 512 — die betriebene Fassung ist auf 512 begrenzt. Wer eine Grenze aus dem Papier des Modells liest statt aus dem Dienst, liest die falsche. Was über ~1500 Zeichen liegt, bettet der Dienst nur mit seinem Anfang ein (Phase 1 unten; ein zweiter Fall steht in der Fundliste vom 19.09.2026).
- VRAM: 955 MB gegen 604 MB von v1 → **netto +351 MB**. Live verifiziert:
  gemma4-gpu (21 GB) + v2-moe passen gemeinsam zu 100 % auf die GPU
- **Präfixe schaden bei allen Modellen** (v1, v2-moe, embeddinggemma — konsistent
  gemessen). Datenblatt empfiehlt sie; die Messung widerspricht. Wir folgen der Messung.
  > **Nachtrag 19.09.2026 — die Messung ist klein, die Gegenseite ist die Bauart des Modells.** Die Entscheidung beruht auf **sechs** Triplets. Das Modell ist für die Präfixe trainiert, und seine Beschreibung benutzt sie in der eigenen Auswertung (dort „search query" und „search document"); die Unterscheidung von Anfrage und Dokument ist genau das, wofür sie gebaut sind. Seitdem sind Schwellenmessungen an fünf Suchräumen entstanden, deren Befunde zur Lücke zwischen Frage und gespeichertem Vektor teilweise auf den fehlenden Präfixen beruhen könnten. **Die Entscheidung bleibt bis zur Nachmessung stehen** — `EMBED-PRAEFIX-NACHMESSEN` in `novaberg-backlog-gedaechtnis.md`.

**Rückfall:** `embeddinggemma` (gezogen, nicht löschen bis zur Abnahme).
**Verworfen:** `bge-m3` (gelöscht — schlechter *und* Schema-Migration).
**`.lower()` ist kein Fix**, nur ein Notnagel: hebt v1 auf 0.20, bleibt 10× unter v2-moe.

> **Hinweis zur Aufteilung (19.09.2026):** §3.1 *Neue Konvention: Casing-Eingangsprüfung* steht in [`novaberg-embedding-casing-blind_k.md`](novaberg-embedding-casing-blind_k.md).

---

## 4. Die Schwellwert-Landschaft

Der Audit fand **19 Ähnlichkeits-Schwellwerte an 14 Orten**, davon **4 hartkodiert**
außerhalb der Config. Die Kalibrierung auf allen 302 echten `lzg_knoten`:

```
ALT: eine einzige Glocke, 0.39–0.89, Gipfel bei 0.72. KEIN TAL.
NEU: Rauschberg 0.10–0.40, dünner Schwanz nach rechts, Median 0.26, p99 0.57
```

| Schwelle | ALT passiert | NEU passiert |
|---|---|---|
| 0.80 | **1.78 %** | 0.02 % |
| 0.65 | **88.60 %** | 0.26 % |

> **Zwischen „feuert nie" und „filtert nichts" lagen im alten Raum 15 Hundertstel.
> Es gab keine Stelle, an der eine Schwelle hätte sitzen können. Alle 19 waren
> funktionslos — nicht schlecht gewählt, sondern strukturell unmöglich.**

`GRAVITATIONS_SCHWELLE = 0.60` lag **unter** dem Grundrauschen (0.74) → hat *immer*
gefeuert. Der Config-Kommentar begründet sie mit „nomic-Baseline ~0.55–0.60" — die
echte Baseline war 0.74. Auch das war schon falsch.

`LZG_KNOTEN_MATCH_SCHWELLE = 0.85` lag **über** dem Signal (Paraphrasen bei 0.78),
aber **unter** der Verwechslung (Matcha/Kakao bei 0.98).
→ **Der Match hat systematisch die *falschen* Knoten verstärkt.**

### 4.1 Abgeleitete Werte (Knoten ↔ Knoten — gemessen) ✅ Gesetzt Chat 107 (Commit `3adc682`)

| Schwellwert | Ort | alt | **neu** | Begründung |
|---|---|---|---|---|
| `LZG_KNOTEN_MATCH_SCHWELLE` | `config.py` | 0.85 | **0.82** | über dem Termin-Fehlpaar (0.788), unter dem echten Duplikat (0.830) |
| `LZG_EMBEDDING_SCHWELLWERT` | `config.py` | 0.85 | **0.55** | p99 = 0.568 |
| `CLUSTER_THEMEN_SIMILARITY` | `config.py` | 0.85 | **0.82** | Alt-Pfad, aber mitziehen |
| `CLUSTER_LZG_SIMILARITY` | `config.py` | 0.80 | **0.75** | Alt-Pfad, aber mitziehen |
| `DELEGATION_SIMILARITY_SCHWELLE` | `config.py` | 0.82 | **0.75** | Akten-Dedup |
| `entitaeten.find_similar` (Default) | `entitaeten_repository.py` | 0.80 | **0.70** | kurze Texte → engerer Raum, konservativ |
| `fakten.find_similar` (Default) | `fakten_repository.py` | 0.80 | **0.70** | tot, aber mitziehen |
| `_stack_aehnliche_entfernen` | `shadow_delivery.py` | 0.65 | **0.60** | hartkodiert in der Signatur |
| `kzg_similar_find` `SIMILARITY_THRESHOLD` | `memory/kzg.py` | 0.85 | **0.75** | tot, aber mitziehen |
| `wissensluecken` Kandidaten-Untergrenze | `ei/wissensluecken.py` | 0.10 (×2) | **0.20** | 0.10 lässt 93 % durch — filtert nichts |
| `_FORCE_ATTRACT_THRESHOLD` | `api/drive.py` | 0.10 | **0.25** | nur Visualisierung |
| `migrate_lzg_synapsen.py --schwelle` | Tool | 0.90 | **0.85** | |

### 4.2 Prompt ↔ Knoten — Startwerte gesetzt, Wachposten aktiv ✅ Chat 107 (Commit `3adc682`)

Diese Werte vergleichen **Prompt ↔ Knoten**, nicht Knoten ↔ Knoten. Die
Abdeckungsmessung (100 echte User-Prompts gegen 302 Knoten) hat den Blocker
aufgelöst — für `anker_retrieval` liegt eine echte Messung vor, die übrigen
sind **begründete Startwerte, keine Messergebnisse** und tragen im Code
Wachposten-Kommentare.

| Schwellwert | Ort | alt | **gesetzt** |
|---|---|---|---|
| `anker_retrieval` `min_similarity` | `memory/lzg_knoten.py` | 0.50 | **0.40** (gemessen: 82 % Turns mit Anker, Ø 4.1 — bei 0.50 nur 53 %/Ø 0.9; bei 0.35 beginnt Rauschen). **Am 21.08.2026 gegengeprüft und bestätigt:** Vier Fragen zu nie besprochenen Gegenständen und eine anaphorische Rückfrage liefern **0 Anker**, eine einschlägige Frage **3** — dieselbe Zahl, die im Kurzzeitgedächtnis wirkungslos war, trennt hier sauber. **Der Unterschied ist der Einbettungstext**, nicht die Zahl: hier die Identität des Inhalts, dort eine Schablone in jedem Eintrag |
| `kzg_entries_retrieve` | `memory/kzg.py` | 0.50 (hartkodiert) | ~~**0.40**~~ → **0.72** am 21.08.2026, als `KZG_RETRIEVAL_SCHWELLE` in `config.py`. **Der Wachposten hat sich bestätigt, und zwar schärfer als vermutet:** Die 0.40 war nicht zu niedrig, sondern **wirkungslos** — der schlechteste Eintrag des gesamten Bestandes erreicht gegen eine beliebige Frage 0.48 bis 0.54, die Schwelle lag unter dem Boden des Raums. Gemessen an 40 Fragen mit bekannter richtiger Erinnerung; die Reihe steht an der Konstante. **Am 21.08.2026 zusätzlich im echten Turn belegt**, mit Gegenprobe gegen die alte Zahl: 0 / 0 / 10 gegen 10 / 10 / 10 |
| `GRAVITATIONS_SCHWELLE` | `config.py` | 0.60 | **0.40** |
| `EMOTIONALE_GRAVITATIONS_SCHWELLE` | `config.py` | 0.50 | **0.40** |
| `GV_CHARAKTER_RESONANZ_SCHWELLE` | `config.py` | 0.40 (Fallback 0.5) | ~~**0.40** (geprüft, bewusst unverändert)~~ → **0.30 seit dem 12.09.2026** → **0.15 am selben Abend, weil die Paarung wechselte** (Thema gegen Kern statt Satz gegen Kern). Die Prüfung von damals hielt den Wert gegen die Embedding-Kalibrierung, nicht gegen die **Verteilung, die er filtert**: `cosine(turn, kern)` liegt über 150 echte Turns bei median 0,228 und max 0,421. **Und die Verteilung ist je Paar eine andere** (12.09.2026, 378 Turns über sieben Paare): Mediane 0,097 bis 0,282, bei zwei Paaren lässt 0,30 nichts durch. Der Vergleich stellt einen Turn von rund hundert Zeichen gegen einen Kern von Tausenden — gegen Konvention 4 und §5 von `novaberg-convention-embedding.md` |
| `GV_NEUGIER_BOOST_SCHWELLE` | `config.py` | 0.30 | **0.30** (geprüft, bewusst unverändert) |
| ~~`shadow_delivery` `SIMILARITY_THRESHOLD`~~ | `shadow_delivery.py` | 0.40 | ~~**0.40** (geprüft, bewusst unverändert)~~ → **überholt am 14.08.2026**, siehe unten |

> **`anker_retrieval` ist der wichtigste Einzelwert im System — an ihm hängt Schale 0
> der gesamten Spreading Activation.** 100 % Abdeckung ist NICHT das Ziel: „Hast Du
> mich denn vermisst?" braucht keinen Anker — Cold Start ist dort die richtige
> Antwort, kein Ausfall. (Alter Raum bei 0.50: 100 % Abdeckung, Ø 299,6 von 302 —
> jeder Turn bekam praktisch den gesamten Korpus.)

> **Überholt am 14.08.2026 — die Zeile zu `shadow_delivery` war richtig und ist es nicht mehr.** Die Konstante heißt heute `THEMEN_SCHWELLE` und steht bei **0,30**. Die Absenkung ist keine Nachjustierung derselben Größe: **Der Wert wird auf einer anderen Paarung gemessen.** Die 0,40 galt für Langtext gegen Langtext und hat damit vor allem Textsortengleichheit erfasst — Median 0,557 im Bestand, 52 von 56 Impulsen kamen durch. Die 0,30 gilt für **Stapeltext gegen Nutzeräußerung**, einen langen Fachtext gegen einen kurzen Zuruf; dort liegt der beste je erreichte echte Treffer bei 0,438, und über 0,45 kommt nichts mehr durch, auch das Passende nicht.
>
> **Das ist der Fall, vor dem der Wachposten unten warnt, in einer zweiten Gestalt.** Dort steht die Sorge, ein Fallback-Wert könne eine Schwelle immer passieren; hier hat eine Schwelle über Monate fast alles passieren lassen, weil sie gegen die falsche Paarung gehalten wurde. **Eine Zahl ohne ihre Paarung ist keine Schwelle** — und ein „geprüft, bewusst unverändert" prüft die Zahl, nicht die Paarung.
>
> Die 0,30 steht auf **drei** Äußerungen: eine begründete Setzung, kein belastbarer Messwert. Herleitung in `novaberg-pixie-nachfragen_k.md` §3.

**Wachposten:** Ziele und `nova_kern` wurden nicht gemessen; nach Live-Betrieb
prüfen. Der `charakter_resonanz`-Fallback 0.5 (bei fehlendem Kern-Embedding) passiert
die 0.40-Schwelle weiterhin immer — im neuen Raum ist 0.5 ein semantisch hoher Wert
(Default-wie-Erfolg-Muster, bei der Nachmessung mitprüfen).

---
