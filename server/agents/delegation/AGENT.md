# DelegationsAgent — Halluzinations-Ventil (VENT1)

Novas Ventil fuer RLHF-Handlungsdrang. Schreibt PostgreSQL-Akten
und gibt dem Responder ein Beruhigungs-Signal.

## Faehigkeiten
- Duplikat-Erkennung (Embedding + Cosine Similarity)
- Akte erstellen (Header + erste Seite)
- Akte anreichern (neue Seite, Prioritaet erhoehen)
- Beruhigungs-Signal an Responder

## Trigger
Dispatcher-ODER: Effektivwert / Emotions-Vektor / Salienz.
Kein User-Facing-Agent — Back-end-Dispatch.

## Kein LLM-Call
Alle Daten liegen im State vor. Rein deterministisch.

## Tabellen
- delegations_akten (Header: Themen, Trigger, Prioritaet)
- delegations_seiten (Detail: EI-Snapshot, Session-Auszug)

## Typ
Workflow (Typ 1). Kein LLM-Call. Nur im User-Graph.
