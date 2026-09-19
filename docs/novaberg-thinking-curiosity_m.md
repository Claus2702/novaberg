# Novaberg — Neugier (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-thinking-curiosity_k.md`](novaberg-thinking-curiosity_k.md) · Ausarbeitung: [`novaberg-thinking-curiosity_t.md`](novaberg-thinking-curiosity_t.md) · Bauplan und Umstellung: [`novaberg-thinking-curiosity_b.md`](novaberg-thinking-curiosity_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-curiosity_e.md`](novaberg-thinking-curiosity_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Vermerk — Namen, Zustand und Berichtigung

Der Namens- und Zustandsvermerk und seine Berichtigung vom 08.09.2026, ungekürzt. Sie standen im ungeteilten Konzept zwischen Kopf und §1. Beide stehen zusammen hier: Die Berichtigung widerlegt den Vermerk an Ort und Stelle und trägt die Messung vom 08.09.2026.

> ## ⚠ Namens- und Zustandsvermerk (Chat 111, 27.07.2026)
>
> **Was dieses Dokument `effektive_neugier` nennt, ist nicht der Wert, der heute im Code so hieß.** Es gibt drei Größen, die bis Chat 111 alle „Neugier" hießen:
>
> | Größe | Was sie ist | Stand |
> |---|---|---|
> | **`aufnahmebereitschaft`** | Maß ihrer Fähigkeit, *jetzt* neugierig zu sein — sechs Säulen aus Zustand und Situation, `sin^0.5`-normiert. Skaliert jede gefundene Lücke und kann sie bei Krise auf 0 löschen. | gebaut (`ei/neugier.py`, Chat 71/72), hieß bis Chat 111 `effektive_neugier` |
> | **`wissensluecken`** | Die akute Lücke aus dem laufenden Turn — *„Kuchen? Was für ein Kuchen?"*. Passiv, extern ausgelöst, einen Turn lang. | gebaut (`ei/wissensluecken.py`, GV4) |
> | **`neugier_vektor`** | Der Zug zu einem Thema über den Turn hinaus — *„Wie entstehen Wurmlöcher?"*. Aktiv, treibt Pixie und Agenten. **Das ist, was dieses Dokument beschreibt.** | ~~nicht gebaut~~ **gebaut** — `agents/wissensluecken/berechnung.py`, seit dem 27.07.2026; **ohne Leser** |
>
> Der Satz, der sie trennt: **Der Vektor sagt, wohin sie will. Die Bereitschaft sagt, ob jetzt der Moment dafür ist.**
>
> ~~**Die Formel dieses Dokuments — `NOVA_NEUGIER × Resonanz × Neuheit` (§3.3) — wurde nie gebaut.** Der Code rechnet seit Chat 71 sechs Zustands- und Situationsfaktoren.~~ Die Kopfzeile „Code-Alignment — Konzept unverändert" bezieht sich auf einen Abgleich, bei dem die Abweichung gesehen und bewusst stehengelassen wurde; sie ist **kein** Beleg, dass das Konzept dem Code entspricht.
>
> ~~Insbesondere fehlt der **Neuheits-Faktor** vollständig.~~ Er ist es, der die tiefe von der flachen Neugier unterscheidet — ein halb bekanntes Thema ist der Sweet Spot; für die heutige Lückensuche ist es entweder zu ähnlich oder unauffällig.
>
> ---
>
> ### Berichtigung des Vermerks — 08.09.2026, gegen den Code gemessen
>
> **Zwei Sätze des Vermerks oben waren schon am Tag ihrer Niederschrift falsch, und sie standen 42 Tage.**
>
> | Aussage vom 27.07.2026 | Befund am 08.09.2026 |
> |---|---|
> | *„Die Formel … wurde nie gebaut“* | `berechnung.py::neugier_vektor_berechnen` gibt `NOVA_NEUGIER * resonanz * neuheit` zurück — **wörtlich die Formel aus §3.3**, gebaut mit `f62302a` am **27.07.2026**, demselben Tag |
> | *„Insbesondere fehlt der Neuheits-Faktor vollständig“* | `neuheit_berechnen` steht in derselben Datei, zwanzig Zeilen darüber, und geht als zweiter Faktor ein |
>
> **Der Vermerk widerlegt sich in seinem eigenen Text.** Seine Tabelle trennt drei Größen sauber — `aufnahmebereitschaft`, `wissensluecken`, `neugier_vektor`. Der Satz darunter wirft zwei davon wieder zusammen: Die *„sechs Zustands- und Situationsfaktoren seit Chat 71“* sind die **Aufnahmebereitschaft**, und die war nie strittig. Über den `neugier_vektor` sagen sie nichts.
>
> **Was heute stimmt, gemessen und nicht erinnert:**
>
> | Größe | Zustand `[gemessen 08.09.2026]` |
> |---|---|
> | `aufnahmebereitschaft` | gebaut **und gelesen** — vier Dateien; sie steuert `wissensluecken_finden` im Gesprächsvektor |
> | `wissensluecken` | gebaut |
> | `neugier_vektor` | gebaut, gerechnet, gespeichert — **und außerhalb seines eigenen Agenten von niemandem gelesen** |
>
> **`TRAUM_NEUGIER_SCHWELLE` aus §3.4 existiert nicht.** Weder in `config.py` noch sonst im Code, und `neugier_vektor` wird an keiner Stelle gegen eine Schwelle geprüft. Der einzige gebaute Regler ist `NOVA_NEUGIER = 0.5` (`config.py:2989`).
>
> **Und das ist ein Glück, kein Mangel — hier steht die Zahl, die es zeigt:** Über **1762** Zeilen reicht `neugier_vektor` von **0,0102 bis 0,1148**, Mittel **0,0640**. Die im Konzept genannte Schwelle von **0,25** wäre **kein einziges Mal** überschritten worden — der höchste je erreichte Wert liegt unter der Hälfte davon. Wäre §3.4 gebaut worden, stünde der Mechanismus still.
>
> > **Ein Produkt zweier Werte unter Eins ist strukturell klein.** §3.3 rechnet mit Beispielwerten wie *Resonanz 0,8 × Neuheit 0,9* und kommt auf 0,58. Im Betrieb liegen echte Cosine-Ähnlichkeiten weit darunter, und das Produkt nutzt **23 %** seiner Spanne [0 … 0,5]. Die Schwelle ist gegen die Beispieltabelle geeicht, nicht gegen Messwerte.
>
> **Was daraus für einen Bau an der Neugier folgt** — nicht *„die Formel muss noch gebaut werden“*, sondern: **Die gebaute Formel braucht einen Leser, und ihre Skala braucht eine Eichung an Messwerten statt an einer Beispieltabelle.** Solange sie niemand liest, ist die Skala ohnehin folgenlos.
>
> **Die zwanzig Formelstellen bleiben unverändert**, aus dem Grund, den der Vermerk selbst nennt: Eine durchgängige Umbenennung gehört in den Bau, nicht in eine Berichtigung.
>
> **Wer hier `effektive_neugier` liest, meint `neugier_vektor` und findet ihn im Code nicht.** Beim Bau wird dieses Dokument durchgängig umbenannt; bis dahin bleibt es unverändert, damit die zwanzig Formelstellen nicht stillschweigend auf den falschen Begriff gedreht werden.
