# NotizenAgent

Verwaltet Freiform-Inhalte: Einkaufslisten, ToDos, Merkzettel, Entwuerfe, Ideensammlungen.

## Faehigkeiten
- notiz_erstellen: Neue Notiz anlegen (Name, Typ, Text, Themen)
- notiz_lesen: Notiz per Stichwort, Volltext oder Thema finden
- notiz_aktualisieren: Bestehende Notiz aendern (LLM generiert neue Version)
- notiz_loeschen: Notiz archivieren (Soft-Delete)
- notiz_anhaengen: Text an bestehende Notiz anhaengen

## Trigger
- "schreib auf", "merk dir", "Einkaufsliste", "ToDo", "fueg hinzu"
- "streich von der Liste", "was steht auf meiner Liste"
- "zeig mir meine Notizen", "loesch die Notiz"
- intent: notizen_management

## Typ
Workflow (Typ 1) — deterministische Schrittfolge, LLM nur fuer Textgenerierung.
