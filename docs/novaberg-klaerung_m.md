# Novaberg — Klärung: Abweichung und Lücke sind derselbe Vorgang (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) · Ausarbeitung: [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md) · Bauplan und Umstellung: [`novaberg-klaerung_b.md`](novaberg-klaerung_b.md) · Diskussion und Ergänzungen: [`novaberg-klaerung_e.md`](novaberg-klaerung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Was der Bestand heute tut

| Stelle | Zustand |
|---|---|
| `fakten` — Triple-Store | ✅ **trägt die Struktur**: `subjekt_id` → `attribut` → `objekt_id \| objekt_wert`, bitemporal über `t_valid` / `t_invalid` / `aktiv` |
| Aktualisierung eines Fakts | ❌ **entscheidet an einer Zeichenkette** — und läuft heute gar nicht: `fakten` hat 0 Zeilen, kein Aufrufer setzt `ziel = "fakten"` (Backlog `15e`). Siehe §3.1 |
| GV4-Lückensuche | 🔶 findet die akute Lücke des Turns, **und vergisst sie**. Sie führt zu keiner Handlung |
| `wissensluecken` | 🔶 ein **Themen**-Verzeichnis (`thema`, `resonanz`, `neuheit`) — es beantwortet „wohin zieht es sie über Wochen", nicht „welcher Slot dieses Objekts fehlt" |
| Rückfrage samt Resume | 🔶 **gebaut, aber agentengebunden** — ausgelöst nur von Mehrdeutigkeit einer Agenten-Operation, nie von einer Wissenslücke |
| Erwartungsschema je Objekttyp | ❌ **existiert nicht.** Nichts sagt, welche Eigenschaften ein „Besuch" hat |
| Urteil über eine Abweichung | 🔶 neu mit `SYK-B1` — dreiwertig; ~~niemand liest es~~ **seit 05.08.2026 liest es die Vorzeichenprüfung** (`SYK-B4` Stufe 1) und legt ihren Befund ins `pipeline_log`. Für K2 bleibt es der Eingang; dass es gelesen wird, ist damit kein Neubau mehr, sondern ein Anschluss |

### 3.1 Der Kern des Defekts — heute unerreichbar

> **Vorab, gemessen am 04.08.2026:** Die Tabelle `fakten` hat **null Zeilen**, und kein Aufrufer setzt jemals `ziel = "fakten"` — im Bestand kommen nur `kzg` und `notizen` vor. Der Triple-Store war in Betrieb und ist beim Umbau nicht mitgezogen worden; der Backlog führt den fehlenden Erzeuger als `15e`. Der folgende Code läuft also korrekt beschrieben, aber **nicht**. Er wird zum Defekt in dem Moment, in dem `15e` gebaut ist — und deshalb steht er hier, statt vergessen zu werden.

Der Aktualisierungspfad des Faktengedächtnisses entscheidet so:

```python
if alter_wert != neuer_wert:
    # Widerspruch → alten Fakt invalidieren
```

Ein reiner Ungleichheitsvergleich invalidiert den bestehenden Fakt und schreibt den neuen. **Drei verschiedene Fälle nehmen denselben Weg:**

| Fall | Richtig | Heute |
|---|---|---|
| zutreffende Berichtigung („ich hatte den Urlaub vergessen") | aktualisieren | aktualisiert ✅ |
| Fortschreibung („jetzt sind es sieben Wochen") | aktualisieren | aktualisiert ✅ |
| Widerspruch zum eigenen früheren Wort | markieren, beide halten | **überschreibt** ❌ |

Das ist Erkennung ohne Bewertung. Die bitemporale Maschinerie, die beide Werte halten könnte, ist vorhanden — es fehlt das Signal, sie unterschiedlich zu benutzen.

### 3.2 Die strukturelle Lücke: zwei Graphen, ein Turn

~~Fakten werden aus zwei Quellen geschrieben: aus dem Salienz-Knoten auf normalen Turns, und über den Aufgabenpfad.~~ **Korrigiert am 04.08.2026** — der Salienz-Knoten schreibt ausschließlich `ziel: "kzg"`, keine Fakten.

Die Lücke ist eine andere und größer:

| Graph | Knotenfolge | Verfasser? |
|---|---|---|
| **HumanGraph** (Pfad 1) — die Nutzeräußerung | `perzeption → enricher → ei_calc → salience → dispatcher` | **nein** |
| **CharacterGraph** (Pfad 2) — Novas Seite | u. a. `planner → … → verfasser → responder → … → salience → dispatcher` | ja, außer bei `task_context_cut` |

**Es sind zwei getrennte Durchläufe über denselben Turn**, korreliert allein über `turn_id`. Das Urteil entsteht im zweiten Graphen; was der erste schreibt, sieht es nie. Eine Prüfung, die am Urteil des Verfassers hängt, deckt den HumanGraph also grundsätzlich nicht ab — nicht nur „manchmal nicht", wie es die Erstfassung nahelegte.

**Dazu kommt der Aufgabenpfad:** Bei `task_context_cut` wird auch im CharacterGraph der Verfasser übersprungen (der Kontext-Schnitt beendete eine Halluzination bei Agent-Erfolg und ist so gewollt). Dort entsteht ebenfalls kein Urteil — ausgerechnet dann, wenn ein Nutzer ausdrücklich etwas ändern lässt.

> **Daraus folgt der Ort der Prüfung.** Sie gehört in den **Schreibpfad**, nicht in den Antwortpfad: Dort deckt sie beide Graphen und den Aufgabenpfad ab, und sie ist Stufe 1 bis 3 aus §2.1 — still, unbedingt, ohne Charakteranteil. Das Verfasser-Urteil verfeinert sie, wo es vorliegt.

---
