# Novaberg — Die Charakter-Räder als Messreihe (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-charakter-rad-messreihe_k.md`](novaberg-charakter-rad-messreihe_k.md) · Ausarbeitung: [`novaberg-charakter-rad-messreihe_t.md`](novaberg-charakter-rad-messreihe_t.md) · Bauplan und Umstellung: [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md) · Diskussion und Ergänzungen: [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil sein Feld **Stand** die Messwerte vom 26. und 27.08.2026 trägt.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — ein akuter Zustand, der durch die Messungen der letzten Tage stabilisiert wird
**Stand:** 27. August 2026 (**die Verfahrensstreuung von 0.08 ist ueberholt** — der Knoten steht seit dem 26.08.2026 auf `temperature = 0.0`, drei Rad-Laeufe sind zeichengleich, Spanne 0,0000; das Kriterium der MESSUNG-Zeile ist damit nicht mehr anwendbar. § 1 und § MESSUNG markiert. Davor: 26. August 2026 (**die offene Ursache der Streuungsangabe ist beantwortet** — der Profiltext muss sich nicht aendern: Bei festgehaltenem Material bewegt allein die Neuziehung des Kerns den Faktor um **0,2908**, das **5,3-fache** der Streuung, die die Dreifacherhebung einfaengt; siehe den Abschnitt am Ende. Davor: 1. August 2026
**Pfad:** novaberg/docs/novaberg-charakter-rad-messreihe_k.md
**Typ:** Konzept (`_k`)
**Status:** ✅ gebaut für **beide Räder**, im Betrieb seit 01.08.2026.
**Voraussetzung:** `novaberg-convention-abgeleitete-werte.md` · `novaberg-salienz-berechnung_k.md` §5 (die zwölf Speichen)
**Betrifft:** `novaberg-charakter-resonanz_k.md` · `novaberg-haltungsraum_k.md` · `novaberg-kzg-salienz_k.md` (Verbraucher des Faktors)

---

## Was die Streuungsangabe misst — und was nicht

**`gemessen` 30.07.2026.** **Die Streuung der Charakter-Räder misst die Einigkeit dreier Läufe über denselben Text, nicht die Haltbarkeit des Werts** — und sie sieht aus wie eine Verlässlichkeitsangabe. Gemessen an je zwei Destillationen beider Richtungen eines Paares, 20:07 und 22:00 UTC: Auf **einer der beiden Zeilen wechselte der Initiative-Versatz zwischen den Erhebungen das Vorzeichen** — von „behält die Initiative" zu „überlässt die Führung" — bei einem Betrag der Änderung von **0.16 auf einer Spanne von ±0.25**, während die abgelegte Streuung der drei Läufe dieser Erhebung **0.005** beträgt. Auf der anderen Zeile betrug die Änderung 0.055 bei einer Streuung von 0.06. Die Drift zwischen zwei Erhebungen erreicht damit im einen Fall das Dreißigfache der Streuung innerhalb einer. **Nicht gemessen ist die Ursache:** Ob sich der zugrundeliegende Profiltext zwischen den beiden Läufen geändert hat, ist offen — beide Erklärungen ändern nichts daran, dass die einzige gespeicherte Unsicherheitsangabe eine andere Frage beantwortet, als ihr Name nahelegt. Betrifft jede Verwendung des Versatzes als kalibrierte Eingangsgröße.

> **Die offene Ursache ist am 26.08.2026 beantwortet, und zwar gegen die naheliegende Vermutung: Der Profiltext muss sich nicht ändern.**
>
> Gemessen mit **festgehaltenem** Turn-Material und **festgehaltenem** Beziehungsprofil — variiert wurde allein der Kern-Hash, viermal frisch destilliert, auf jedem ein Zuwendungs-Rad mit den vorgeschriebenen drei Läufen und Median:
>
> | | Spanne des Faktors |
> |---|---|
> | Innerhalb eines Kerns, drei Läufe | **0,0550** im Mittel (größte 0,1041) |
> | Über vier Kerne, je Median aus drei | **0,2908** |
>
> Die vier Mediane: 1,2088 · 1,1426 · 1,0695 · 0,9180. Bei einer Faktorspanne von 0,5 bis 1,5 sind das **29 % des gesamten Bereichs** — allein daraus, welche Ziehung des Kerns das Rad gerade gelesen hat. **Die Streuung über Kerne ist das 5,3-fache der Streuung innerhalb eines Kerns.**
>
> **Damit ist die Unsicherheitsangabe nicht nur anders benannt als gemeint, sondern um den Faktor fünf zu klein.** Sie misst die Einigkeit dreier Läufe über *denselben* Text; die größere Bewegung entsteht eine Stufe davor, beim Entstehen dieses Textes. Ein Zusammenhang mit der Kernlänge besteht nicht — der längste Kern (4850 Zeichen) liefert 1,0695, der kürzeste (3987) 0,9180.
>
> Aufgenommen als `RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`. Werkzeug: `labor/2026-08-26_rad_kernstreuung.py`.
