# KZG-Agent — Kurzzeitgedaechtnis

Verdichtet Gespraechs-Turns zu Kern-Saetzen und speichert sie im Kurzzeitgedaechtnis (Redis).

## Faehigkeiten
- Turn-Verdichtung (LLM-Call)
- Aehnlichkeitssuche (Embedding + Cosine)
- KZG-Store / Verstaerkung
- Session-Turn-Annotation
- Promotion-Queue + Shadow-Queue

## Trigger
Wird vom Dispatcher nach der Salienz aufgerufen. Kein User-Facing-Agent.

## Typ
Workflow (Typ 1). Deterministisch mit einem LLM-Call (Verdichtung).

## Graph-Eignung
Nur im User-Graph (nach Salienz). Nicht im Pixie-Graph.
