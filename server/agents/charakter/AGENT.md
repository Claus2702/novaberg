# CharakterAgent

Destilliert 5 Charakter-Profile aus LZG (PostgreSQL) und KZG (Redis).

## Trigger
- Periodisch (alle 10 min), aber nur aktiv wenn `hash_dirty:{user_id}` gesetzt
- Flag wird vom PromotionAgent nach erfolgreicher LZG-Promotion gesetzt

## Profile
| Profil | Quelle | Beschreibt |
|--------|--------|-----------|
| kern_hash | ~~LZG~~ → **Turn-Wortlaut** (`pipeline_log`, 40 Turns) | Grundpersönlichkeit |
| adaptive_hash | KZG | Aktuelle Phase |
| intentions_profil | LZG | Kommunikationsstil |
| emotions_profil | LZG | Emotionale Grundtendenz |
| beziehungsprofil | KZG-Schlüssel → Turn-Wortlaut | Beziehungsdynamik |

## Auswahl der KZG-Einträge (seit 16.08.2026)

`_kzg_laden` liefert die `PIXIE_CHARAKTER_KZG_LIMIT` Einträge mit der höchsten
**effektiven Salienz** = `salienz × zeitgewicht(alter)`, nicht die ersten, die
`SCAN` ausgibt. Das Zeitgewicht ist `exp(-ln2/T · t)` mit
`PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE` (1,7 Tage).

- **Warum eine Ordnung nötig ist:** `SCAN` sagt keine zu. Gemessen am
  produktiven Paar lagen die vorher genommenen 20 auf den Zeiträngen 245 bis
  2162 von 2202, im Mittel 18 Tage alt — für ein Profil mit der Frage
  *„Was beschäftigt ihn gerade?"*. Nach dem Umbau: 2,1 Tage.
- **Warum es trotzdem billig bleibt:** Die Schlüssel tragen ihre Zeitmarke, die
  Sortierung kostet keinen Redis-Zugriff. Sinkt das Zeitgewicht unter die
  schwächste bereits gewählte effektive Salienz, kann kein älterer Eintrag mehr
  aufholen (`salienz ≤ 1`) — ab da wird nicht weitergelesen. Gemessen: 28
  gelesene statt 2202 durchsuchter Schlüssel.
- **Ohne Themenfeld kein Platz:** Solche Einträge verwirft die Destillation
  ohnehin. Unter den jüngsten `assistant`-Einträgen tragen nur 70 % eines.
- Verworfenes wird **gezählt** und steht in der Logzeile — beide Pfade waren
  vorher stille `continue`.

## Besonderheiten
- Iteriert über alle User (meister + nova)
- 1 LLM-Call pro Profil pro User (max 10 Calls bei beiden dirty)
- CPU-Modell (kein GPU-Contention)
- Kein eigener Subgraph — reines invoke()
