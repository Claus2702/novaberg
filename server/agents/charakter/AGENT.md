# CharakterAgent

Destilliert 5 Charakter-Profile aus LZG (PostgreSQL) und KZG (Redis).

## Trigger
- Periodisch (alle 10 min), aber nur aktiv wenn `hash_dirty:{user_id}` gesetzt
- Flag wird vom PromotionAgent nach erfolgreicher LZG-Promotion gesetzt

## Profile
| Profil | Quelle | Beschreibt |
|--------|--------|-----------|
| kern_hash | LZG | Grundpersönlichkeit |
| adaptive_hash | KZG | Aktuelle Phase |
| intentions_profil | LZG | Kommunikationsstil |
| emotions_profil | LZG | Emotionale Grundtendenz |
| beziehungsprofil | KZG | Beziehungsdynamik |

## Besonderheiten
- Iteriert über alle User (meister + nova)
- 1 LLM-Call pro Profil pro User (max 10 Calls bei beiden dirty)
- CPU-Modell (kein GPU-Contention)
- Kein eigener Subgraph — reines invoke()
