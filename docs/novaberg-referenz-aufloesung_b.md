# Novaberg — Referenz-Auflösung (REF-KASKADE) (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-referenz-aufloesung_k.md`](novaberg-referenz-aufloesung_k.md) · Ausarbeitung: [`novaberg-referenz-aufloesung_t.md`](novaberg-referenz-aufloesung_t.md) · Diskussion und Ergänzungen: [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen.

---

## 8. Der Weg dorthin — Messung vor Bau

Vier Schichten sind vier Wartungspfade und vier Drift-Quellen. Bevor wir sie bauen, wollen wir
wissen, **welche Schicht wie viel trägt.** Sonst bauen wir L1–L3 und stellen fest, dass in
90 % der Fälle doch L4 ran muss — dann wäre die Kaskade reiner Ballast.

### 8.1 Schritt 1 — Embedding-Diagnose (5 Minuten, kein Code, kein Risiko)

```python
# Cosinus-Ähnlichkeit mit dem LIVE-Modell
paare = [
    ("Liste",         "Notiz"),         # muss HOCH sein  — sonst ist L3 tot
    ("Einkaufsliste", "Notiz"),
    ("Matcha-Pulver", "Pulver"),        # muss HOCH sein
    ("Matcha-Pulver", "Kakaopulver"),   # muss NIEDRIGER sein als die Zeile darüber
    ("Liste",         "Fahrrad"),       # Kontrolle: muss NIEDRIG sein
]
```

**Abbruchkriterium:** Liegt `("Liste","Notiz")` nahe bei `("Liste","Fahrrad")`, ist das
Embedding für deutsche Semantik unbrauchbar. Dann ist L3 nicht der Sprint — dann ist der
Modellwechsel der Sprint.

**Ausweg, falls nötig:** BGE-M3 (MIT, 100+ Sprachen, dense **und** sparse in einem Modell —
bedient damit exakt unseren Notizen-Suchpfad) oder multilingual-e5-large (MIT). Beide auf
Ollama. **Aber:** Modellwechsel = **alles neu embedden** (KZG-Blobs in Redis, `lzg_knoten`,
`charakter_hash`). Eigener Migrations-Sprint. Nicht nebenbei.

### 8.2 Schritt 2 — Discovery-Audit

Läuft (Chat 106). Beantwortet: Wo wird das Embedding berechnet? Existiert der Entity-Layer
pro Turn (→ L2a)? Wo sind alle State-Init-Punkte?

### 8.3 Schritt 3 — SCHATTEN-Sprint (das Herzstück)

**Baue L0 + L1. Lass sie NICHTS verändern.** Sie schreiben nur ins Log:

```
REF/L0: Marker erkannt — text='die Liste' art=definite_nominal head='Liste'
REF/L1: 8 Turns durchsucht, Kandidaten: ['Einkaufsliste' (d=3, s=0.74)]
REF/L1: Status=GEFUNDEN — Kopf-Match, Marge 0.74 (kein Zweiter)
REF/SCHATTEN: würde ersetzen 'die Liste' -> 'Einkaufsliste'   [NICHT ANGEWENDET]
```

**Null Risiko.** Kein Verhaltenswechsel, kein Retrieval berührt, kein Prompt verändert.
Ein `SCHATTEN`-Flag in `config.py`, Default `true`.

Nach ein paar Tagen Alltagsbetrieb weißt du:

| Frage | Antwort aus dem Log |
|---|---|
| Wie oft feuert L0 überhaupt? | Die Kosten-Basis. Literatur sagt >60 % — stimmt das für **uns**? |
| Wie oft löst L1 allein? | Trägt die Python-Schicht — oder ist sie Deko? |
| Wo hätte L1 **falsch** gebunden? | Der Nachweis, dass die Marge nötig ist. |
| Welche Scores treten real auf? | **Die Schwellenwerte für L3 — gemessen statt geraten.** |

Das ist dieselbe Methode, die in Chat 105 den Kraft-1-Bug fand: **Erst die Zeile, dann der Fix.**
Fünf Minuten Diagnose-Log deckten sechzehn Chats blinde EI-Berechnung auf. Hier stehen ein paar
Tage Log gegen einen Sprint, der sonst auf Vermutungen gebaut wäre.

### 8.4 Schritt 4 — Scharfschalten, schichtweise

L1 scharf → messen → L2 → messen → L3 → messen → L4. **Eine Schicht pro Commit.**
Jede Schicht hat ein eigenes Flag. Jede kann einzeln abgeschaltet werden.

---
