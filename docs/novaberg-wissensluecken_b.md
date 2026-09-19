# Novaberg — Wissenslücken: der Zug zu einem Thema (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-wissensluecken_k.md`](novaberg-wissensluecken_k.md) · Ausarbeitung: [`novaberg-wissensluecken_t.md`](novaberg-wissensluecken_t.md) · Diskussion und Ergänzungen: [`novaberg-wissensluecken_e.md`](novaberg-wissensluecken_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 6. ZIEL / TEST / MESSUNG

| | |
|---|---|
| **ZIEL** | Nach einem Lauf stehen in `wissensluecken` Themen, die Nova angehen und die sie noch nicht kennt — je mit Resonanz, Neuheit und dem daraus gerechneten Vektor. Ein Thema, über das sie danach spricht, verschwindet beim nächsten Lauf aus der Liste. |
| **TEST** | `neugier_vektor` als reine Funktion, ohne LLM prüfbar: Zentrum (Resonanz 0.9, Neuheit 0.1) liegt unter Rand (0.7 / 0.7); Außen (0.1 / 0.9) ebenfalls. Idempotenz: zweimal rechnen liefert bitgleich. Zweiter Lauf mit demselben Thema erzeugt keine zweite Zeile. Fehlerpfade: kein Charakterkern → laut abbrechen statt gegen einen Nullvektor rechnen; leere Kandidatenliste → null Zeilen und eine Log-Zeile, die das benennt. Positiver Zwilling: ein Lauf mit Kandidaten legt Zeilen an. |
| **Gegenprobe** | Den Neuheits-Faktor testweise auf 1.0 festnageln — der Zentrum-vor-Rand-Test muss rot werden. Ohne Neuheit ist der Vektor reine Resonanz und zieht zu dem, was sie längst weiß. |
| **MESSUNG** | Agent auf einem echten Bestand laufen lassen. `SELECT thema, resonanz, neuheit, neugier_vektor FROM wissensluecken ORDER BY neugier_vektor DESC LIMIT 10` — die obersten Themen müssen *plausibel am Rand* liegen: erkennbar ihres, aber nicht bereits besprochen. Dann ein Gespräch über eines davon, erneuter Lauf, und die Zeile muss inaktiv werden oder fallen. |
