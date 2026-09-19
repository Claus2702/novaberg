# Novaberg — Die Initiative-Achse: wer das Gespräch führt (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-gv-initiative_k.md`](novaberg-gv-initiative_k.md) · Ausarbeitung: [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md) · Diskussion und Ergänzungen: [`novaberg-gv-initiative_e.md`](novaberg-gv-initiative_e.md) · Messungen: [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §7 — Der Kalibrier-Agent

Zweck und Aufwand des Agenten (Einleitung von §7) stehen in [`novaberg-gv-initiative_t.md`](novaberg-gv-initiative_t.md), die Läufe und Audits (§7.2 bis §7.4) in [`novaberg-gv-initiative_m.md`](novaberg-gv-initiative_m.md).

### 7.1 Was gebaut ist, was nicht (Chat 117)

| Teil | Stand |
|---|---|
| Cohens κ, Schwellensuche mit Erreichbarkeits-Nebenbedingung | **gebaut**, `ei/kalibrierung.py` |
| Der Zeuge: zwei Texte, Sprecher A und B | **gebaut**, `agents/kalibrierung/zeuge.py` |
| Korpus aus Rohturns, `verbindung`, KZG; Rohwerte über `fuehrung_messen` | **gebaut**, `korpus.py` |
| Zwischenstand und Wiederanlauf | **gebaut**, `zwischenstand.py` |
| Trennung von Erheben und Anwenden (`KALIBRIERUNG_ANWENDEN`) | **gebaut**, Default `false` |
| Pixie-Agent mit Takt und Gate | **nicht gebaut** |
| Ablage der erhobenen Schwelle je Paar | **nicht gebaut** — die Konstante gilt |
| Entscheidung, ob die gemessene Schwelle die Konstante ersetzt | **offen** |

**Der Takt ist entschieden, nicht gebaut:** eigener periodischer Vorgang, täglich, mit einem Gate auf die Zahl neuer Turns seit der letzten Erhebung. Nicht an die Charakter-Destillation gehängt — die läuft alle zehn Minuten bei `hash_dirty`, und achtzig Urteile darin hielten den Hintergrundtakt jedes Mal für Minuten auf. Untergrenze der Fallzahl: **60** (`KALIBRIERUNG_MIN_TURNS`), gesetzt und nicht gemessen.

---

## 11. Baustand des Rads (Chat 116)

| | |
|---|---|
| Speichen und Züge | `INITIATIVE_ZUG_HOCH` / `_RUNTER` in `agents/charakter/destillation.py` |
| Prompt | `INITIATIVE_RAD_PROMPT`, direkt neben dem bestehenden `CHARAKTER_RAD_PROMPT` |
| Rechnung | `initiative_versatz_berechnen` — reine Funktion, lehnt unvollständige Räder ab |
| Erhebung | `initiative_rad_destillieren`, gerufen vom `CharakterAgent` nach den fünf Profilen |
| Speicher | `charakter_hash.initiative_versatz{,_quelle,_rad,_am}` — vier Spalten nach dem Muster von `nutzer_gewichtung` |
| Verbraucher | `memory/charakter.py`, `initiative_versatz_laden`; der GV-Node reicht den Wert an `fuehrung_messen` |
| Tests | `tests/test_initiative_rad.py` (13) |

**Volle Auslenkung trifft ±0.25 exakt** — live nachgerechnet: alle fünf oben ausgeprägt ergeben +0.2500, alle fünf unten −0.2500, das leere Rad 0.0000. Die Kappung ist damit Sicherung, kein Formteil.

**Die Zug-Summen sind getestet, nicht nur gesetzt.** Weicht eine Summe von 0.25 ab, trifft die volle Auslenkung die Grenze nicht mehr, und die Kappung würde vom Sicherungsnetz zum Formteil — das fällt sonst niemandem auf, weil beide Fälle denselben Wert liefern.

**Zwei Fälle, die derselbe Zahlenwert sind und nicht dasselbe bedeuten**, unterscheidbar allein am Herkunftsfeld und am gespeicherten Rad:

- Versatz 0.0000, `quelle='destilliert'`, Rad mit belegten Speichen → die Speichen heben sich auf. Eine Messung.
- Versatz 0.0000, `quelle='destilliert'`, Rad überall 0.0 → das Profil sagt über Gesprächsführung nichts. Auch eine Messung, aber eine andere.
- Versatz 0.0000, `quelle='default'` → nie erhoben. Kein Messergebnis.

**Wenn das Laden ausfällt, rechnet die Achse ohne Versatz** statt mit einem erfundenen — der Rohwert bleibt dann die reine Messung, und die Logzeile sagt es. Dasselbe gilt für einen Versatz aus dem Default: Der GV-Node meldet, dass der Charakter die Achse noch nicht verschiebt.

**Offen bleibt die Spannweite.** ±0.25 ist gesetzt, nicht gemessen. Prüfbar, sobald genug Turns vorliegen: wie viele Turns die volle Auslenkung tatsächlich umklappt.
