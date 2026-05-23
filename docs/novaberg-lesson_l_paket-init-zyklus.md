# Novaberg — Lesson: Paket-`__init__`-Zyklus

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Ein Symbol-Import aus einem Submodul lädt das Paket-`__init__`; ein zustandsloser Util gehört nicht hinter ein `__init__`, das schwere Abhängigkeiten initialisiert
**Stand:** 23. Mai 2026, Chat 94
**Pfad:** novaberg/docs/novaberg-lesson_l_paket-init-zyklus.md
**Kategorie:** Architektur — Import-Topologie und Paket-Struktur
**Schwester-Lessons:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md`
**Konzept-Bezug:** `novaberg-microservice-modell-queue_k.md`
**Handbuch-Bezug:** `DEVELOPER_HANDBOOK.md`

---

## 1. Der Vorfall

Der Kahlschlag in Chat 94 (Block 3 Teil 2) war reiner Code-Tod — verhaltensneutral, durch viele kleine pattern-verifizierte Schnitte abgesichert. Greps grün, Schnitte sauber. Weil die Testsuite im Container nicht lief (`pytest` fehlt), wurde als Ersatz-Verifikation ein Import-Smoke-Test über alle berührten Module gefahren: schlicht jedes betroffene Modul importieren und prüfen, ob es lädt.

Er lud nicht:

```
ImportError: cannot import name 'AnthropicProvider' from partially initialized
module 'services.llm_provider' (most likely due to a circular import)
```

Ein zentrales Modul — `llm_provider` — war nicht mehr importierbar. Der Server war nicht lauffähig. Und das, obwohl jeder einzelne Lösch-Schnitt verhaltensneutral war und jeder Grep grün.

Der Bug stammte nicht aus dem Kahlschlag selbst. Er stammte aus einem früheren Edit derselben Welle — der Postprocess-Konsolidierung, bei der `OllamaProvider.chat` und `AnthropicProvider.chat` von ihren privaten JSON-Helfern auf die zentralen Funktionen in `postprocess.py` umgestellt wurden. Dafür war eine neue Import-Zeile nötig:

```python
from services.model_services.postprocess import (
    clean_json_response,
    deduplicate_repetition,
    repair_truncated_json,
)
```

Eine harmlose Zeile. Sie holt drei zustandslose Funktionen aus einem Modul, das selbst nur `json` und `re` importiert. Nichts daran sah gefährlich aus.

## 2. Die Ursache

Der Zyklus war genau eine Kante lang:

```
llm_provider.py:23   from services.model_services.postprocess import ...
   ↓ Python MUSS zuerst das Paket laden → model_services/__init__.py
model_services/__init__.py:19   from services.model_services.registry import model_service
   ↓ Python lädt registry.py
registry.py:37   from services.llm_provider import AnthropicProvider, LLMProvider, OllamaProvider
   ↑ ImportError — llm_provider ist noch in seiner eigenen Init bei Zeile 23,
     die Provider-Klassen (ab Zeile 72) sind noch nicht definiert
```

Der entscheidende, leicht zu übersehende Mechanismus steht in Schritt 1: **Ein `from paket.submodul import x` importiert nicht nur das Submodul — es führt zuerst das `__init__.py` des Pakets aus.** Das ist Python-Standardverhalten, kein Sonderfall. Wer ein Submodul anfasst, zahlt immer den vollen Paket-Init-Preis.

`postprocess.py` selbst war vollkommen sauber — keine Rück-Importe, nur Stdlib. Aber es lag *innerhalb* des Pakets `model_services`, dessen `__init__.py` beim Laden die Registry hochzieht, und die Registry braucht (völlig zu Recht) die Provider-Klassen aus `llm_provider`. Solange `llm_provider` selbst nichts aus `model_services` importierte, lief das in eine Richtung und war zyklusfrei. Die neue Import-Zeile schloss den Ring: Jetzt importierte `llm_provider` aus einem Paket, dessen Init auf `llm_provider` zurückzeigt.

Die `registry`→`llm_provider`-Kante war dabei nicht der Fehler. Sie ist eine legitime, beabsichtigte Abhängigkeit — eine Factory muss die Klassen kennen, die sie baut. Der Fehler war, einen zustandslosen Util-Helfer in ein Paket zu legen, dessen `__init__` Lifecycle-Code initialisiert, und ihn dann von der Schicht zu importieren, die dieser Lifecycle-Code seinerseits braucht.

## 3. Die strukturelle Lösung

Drei Wege standen zur Wahl:

1. **Lazy-Import in `llm_provider.chat`** — die Import-Zeile in die Methoden ziehen, die die Helfer nutzen. Trifft die selbst eingezogene Kante, aber verteilt einen Import auf zwei Hot-Path-Methoden und verschleiert die Abhängigkeit.
2. **Lazy-Import in `registry`** — die Provider-Importe in die Factory-Funktion ziehen. Funktioniert, aber verbiegt eine *gesunde, beabsichtigte* Top-Level-Abhängigkeit, um einen Zyklus zu brechen, der woanders entstand. Wer später `registry` liest, sieht einen grundlosen Lazy-Import.
3. **Die Datei aus dem Paket lösen** — `postprocess.py` per `git mv` von `services/model_services/postprocess.py` nach `services/postprocess.py`, als flacher Top-Level-Util neben `llm_provider.py`.

Option 3 wurde gewählt, weil sie als einzige die *Wurzel* behebt statt sie zu verstecken. Ein zustandsloser Util ohne Lifecycle gehört nicht hinter ein Paket-`__init__`, das die halbe Service-Schicht initialisiert. Gegencheck vor dem Move: `services/__init__.py` war leer (0 Bytes). Damit triggert `from services.postprocess import ...` nur das leere `services/__init__.py` und `postprocess.py` selbst — kein Pfad zurück zu `model_services`, `registry` oder `llm_provider`. Der Zyklus ist nach dem Move strukturell unmöglich, nicht bloß verlagert.

```bash
git mv novaberg/server/services/model_services/postprocess.py \
       novaberg/server/services/postprocess.py
# + vier Import-Pfade umgestellt (llm_provider, chat_worker, background_worker, ein Docstring)
```

Der Import-Smoke-Test, der den Bug fand, war anschließend grün: `alle betroffenen Module importieren sauber`.

## 4. Das Prinzip

### Ein Submodul-Import zahlt den Paket-Init-Preis

`from paket.submodul import x` führt das `paket/__init__.py` aus, bevor `x` verfügbar wird. Was im `__init__` steht, erbt jeder, der irgendein Submodul des Pakets importiert — auch wenn das Submodul selbst harmlos ist.

Daraus folgt eine Platzierungs-Regel: **Zustandslose Utilities gehören nicht in ein Paket, dessen `__init__` schwere Abhängigkeiten oder Lifecycle-Code initialisiert.** Ein reiner Helfer (nur Stdlib, keine Rück-Importe, kein Zustand) sollte so flach liegen, dass sein Import nichts außer ihm selbst lädt. Liegt er hinter einem `__init__`, das Provider, Worker, Registries hochzieht, dann zwingt jeder Importeur des Helfers die gesamte Maschinerie hochzufahren — und riskiert genau dann einen Zyklus, wenn der Importeur selbst Teil dieser Maschinerie ist.

Die zweite, allgemeinere Lehre betrifft die **Verifikations-Ebene**: Greps finden tote Symbole, aber keine Import-Topologie. Ein verhaltensneutraler Code-Tod-Commit kann jeden Grep bestehen und trotzdem den Import-Graphen brechen — durch eine Kante, die ein *früherer* Edit derselben Welle eingezogen hat. Der Import-Smoke-Test (`python -c "import …"` über alle berührten Module plus `main`) ist die Mindest-Verifikation, die diese Klasse von Fehlern fängt. Er ist kein Ersatz für eine Testsuite, aber er ist die untere Schranke: Wenn ein Modul nicht einmal importiert, ist jede weitere Aussage über sein Verhalten gegenstandslos.

## 5. Die Konsequenz

**Erstens:** Neue zustandslose Utilities werden flach unter `services/X.py` angelegt, nicht innerhalb eines Subpakets mit aktivem `__init__`. `services/postprocess.py` ist jetzt das Muster — neben `llm_provider.py`, `event_consumer.py`, `shadow_delivery.py`.

**Zweitens:** Nach jedem Edit, der eine neue Import-Kante zwischen Modulen einzieht — besonders zwischen einer Schicht und einem Paket, das auf diese Schicht zurückzeigt —, läuft ein Import-Smoke-Test über die berührten Module plus `main`. Greps allein genügen nicht; sie sehen die Topologie nicht.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum `postprocess.py` flach unter `services/` liegt und nicht bei den anderen Worker-Modulen in `services/model_services/`, liest hier nach. Die Platzierung wirkt inkonsistent, bis man sich an den Zyklus erinnert, den sie verhindert.

## 6. Der Preis

Ein nicht-lauffähiger Server zwischen dem Postprocess-Edit und seiner Entdeckung. Der Bug wurde nicht im Moment seines Entstehens bemerkt — er lag latent, weil zwischen dem Edit und dem Import-Test mehrere weitere Kahlschlag-Schnitte lagen, alle mit grünen Greps. Hätte es keinen Import-Smoke-Test gegeben (etwa weil man sich auf die grünen Greps verlassen hätte), wäre der Server erst beim nächsten echten Start gecrasht — möglicherweise erst Blöcke später, mit dann größerem Suchraum, weil mehrere Wellen dazwischen lägen.

Der eigentliche Wert lag im billigen Fund: Der Import-Test kostete eine Zeile pro Modul und einen Terminal-Aufruf. Er machte einen latenten, server-tötenden Topologie-Bug sofort sichtbar — an genau der Stelle, an der die Greps blind waren. Die Lehre ist nicht „Zyklen sind schlimm" (das weiß jeder), sondern: Die Verifikations-Ebene muss zur Fehler-Klasse passen. Ein Code-Tod-Commit braucht Greps *und* einen Import-Test, weil Löschen das eine Risiko (übersehenes totes Symbol) und ein begleitender Struktur-Edit das andere (gebrochene Topologie) trägt.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md`
→ Konzept-Dokument: `novaberg-microservice-modell-queue_k.md`
