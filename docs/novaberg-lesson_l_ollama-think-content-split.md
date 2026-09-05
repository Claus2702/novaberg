# Novaberg — Lesson: Der Ollama content/thinking-Split

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Bei think=True trennt Ollama den Output nicht-deterministisch in content und thinking; ein Loop, der nur content liest, läuft blind
**Stand:** 5. September 2026, 17:06 UTC (zwei Stellen als widerlegt markiert — die Auswahl des Normalizers haengt nicht am Connector, und ihr Schluessel war bis heute das konfigurierte statt des antwortenden Modells). Davor 21. Mai 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_ollama-think-content-split.md
**Kategorie:** Architektur — Modell-spezifisches Verhalten kapseln + Diagnose vor Lösung
**Schwester-Lessons:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md` (Microservice-Welle)
**Konzept-Bezug:** `novaberg-microservice-modell-queue_k.md`, `novaberg-node-thinker.md` §3.4/§3.5
**Externe Belege:** Ollama Issue #10976, LiteLLM Issue #18922 (beide offen seit 2025), verwandt mit #15260

---

## 1. Der Vorfall

Block 3 der Microservice-Welle schaltete den Thinker zum ersten Mal auf echtes `think=True`. Vorher lief er — wie jeder andere Node — ohne Reasoning-Modus; der `think=True`-Wert in seiner Config war toter Code, der nie beim Modell ankam. Mit Block 3 Teil 1 floss `think` durch die ganze Kette, und der Thinker begann tatsächlich zu reasonieren: ein einzelner Call dauerte nun rund eine Minute, mit echter Tool-Nutzung und Faktenprüfung. Das war der gewollte Zustand.

Dann fiel auf, dass Nova bei bestimmten Turns nur ankündigte, etwas nachzuschauen — „ich schaue gleich nach" — aber die Antwort nicht lieferte. Im Log zeigte sich das Muster: Der Thinker iterierte fünfmal (bis `max_iterations`) und lieferte am Ende `text_len=0`. Vier leere Antworten in Folge, jede rund 25 Sekunden, der Token-Verbrauch stieg, am Ende stand „Max Iterationen erreicht — Antwort bleibt unverändert". Die ursprüngliche, teils halluzinierte Responder-Antwort blieb stehen.

Der erste Verdacht lag nahe und war falsch: „Bei `think=True` steckt der Output im thinking-Feld, der Thinker liest aber content — also lies das thinking-Feld." Dieser Reflex hätte zu einem Fix geführt, der das eigentliche Problem nicht trifft.

## 2. Die Ursache

Diagnose-Logging in `OllamaProvider.chat` machte beide Felder sichtbar — `content_len` und `thinking_len` für jeden Call. Der Befund war eindeutig und differenzierter als der erste Verdacht:

Bei `think=True` legt Ollama (mit gemma4 ebenso wie mit qwen3) den Modell-Output **nicht-deterministisch** ab. In manchen Iterationen steht der ausführbare Steuer-Token sauber in `content` (`TOOL: web_search(...)`, `ERGEBNIS: OK`), und das thinking-Feld trägt zusätzlich die Reasoning-Prosa. In anderen Iterationen bleibt `content` **komplett leer** (`content_len=0`), und der gesamte Output — inklusive der eigentlichen Schlussfolgerung — landet im thinking-Feld (`thinking_len` von 7000–8000 Zeichen).

Das ist kein Eigenbau-Defekt. Es ist ein dokumentiertes, breit reproduziertes Ollama-Verhalten: Issue #10976 („Thinking + tools + qwen3 = empty output") und LiteLLM #18922 („tool_calls dropped when thinking field is present") beschreiben exakt dasselbe Muster. Beide Issues sind seit 2025 offen. Es ist verwandt mit #15260 (think=True und format=json schließen sich aus). Der gemeinsame Nenner: Ollamas Thinking-Handling bricht die saubere Trennung zwischen Reasoning und ausführbarem Output. Das Problem ist **Ollama-spezifisch, nicht modell-spezifisch** — gemma4 und qwen3 zeigen es beide.

Entscheidend war die zweite Diagnose-Stufe: das **vollständige** thinking-Feld bei leerem content loggen, nicht nur die ersten 200 Zeichen. Damit ließ sich die eigentliche Frage beantworten, die über den richtigen Fix entschied:

- **Fall 1:** Der Steuer-Token (`TOOL:`/`ERGEBNIS:`) steht am Ende des thinking-Texts. Dann genügt es, ihn aus thinking nach content zu ziehen.
- **Fall 2:** Das thinking-Feld enthält **nur** Reasoning-Prosa — keinen Steuer-Token. Das Modell hat gedacht, aber keine ausführbare Entscheidung formuliert.

Das vollständige Log zeigte **Fall 2**: seitenweise sauberes Reasoning (der Thinker erkannte sogar korrekt eine Halluzination und formulierte die Korrektur aus), aber nirgends ein Steuer-Token. Damit war der naheliegende „lies das thinking-Feld"-Fix als unzureichend bewiesen — es gab dort nichts Verwertbares zum Auslesen. Hätte man ohne die zweite Diagnose-Stufe gefixt, hätte man Fall 1 gebaut und Fall 2 nicht gelöst.

## 3. Die strukturelle Lösung

Drei Bausteine, klar getrennt nach Verantwortung.

**Der Datenfluss.** Das thinking-Feld wurde durch die Worker-Kette geführt — `LLMAntwort` → `ChatResponse`, additiv mit Default `""`. Ohne diesen Schritt kann kein Konsument das thinking-Feld sehen; es wurde vorher im Provider weggeworfen. (Symmetrisch auch in `BackgroundResponse`, als Anschluss für einen künftigen PixieGraph-Thinker — kein toter Code, sondern ein bereitstehender Kanal.)

**Der Normalizer — modell-spezifisches Verhalten hinter einer Factory.** Code in `tools/thinking_normalizer.py`: eine Basisklasse `ThinkingNormalizer` (No-Op — content gilt immer als brauchbar) und eine erbende Klasse `ThinkSplitNormalizer`, die den content-leer/thinking-voll-Fall behandelt. Welche Klasse aktiv ist, entscheidet eine Factory (`get_thinking_normalizer()`). ~~Connector-Factory~~ — **die Bezeichnung war schon bei der Niederschrift ungenau und ist seit dem 05.09.2026 falsch:** Verglichen wurde nie der Connector, sondern der Modellname, und zwar der **konfigurierte** (`OLLAMA_MODEL`). Seit dem 05.09.2026 kommt er aus der Backend-Wahl (`config.antwortendes_chat_modell()`) und benennt damit das Modell, das **antwortet**. Der Unterschied war folgenlos, solange jedes Backend ein lokales war; beim ersten fremden Rueckhalt haette der Aufraeumer weiter gegriffen, obwohl das antwortende Modell den Split nicht erzeugt. Der Thinker-Loop ruft `normalizer.pruefen(content, thinking)` und bleibt **modell-agnostisch** — das Wissen über Ollamas Eigenart sitzt gekapselt in der erbenden Klasse, nicht im Loop. Modelle ohne das Problem bekämen die No-Op-Basis und der Loop merkt keinen Unterschied. Wenn Ollama #10976 eines Tages behoben ist, wird eine Klasse gelöscht, nicht ein verstreuter `if content_len==0`-Hack aus dem Loop gefischt.

**Die Nachfass-Iteration — gegen Fall 2.** Erkennt der Normalizer content-leer + thinking-voll, stößt der Thinker eine Nachfass-Iteration an: ein Folge-Call mit `think=False` (damit der Reparatur-Call nicht wieder ins thinking driftet), der das bereits erzeugte Reasoning als Material mitgibt und ausschließlich die Entscheidung im Steuer-Format einfordert. Das Modell muss nicht neu denken — es soll sein fertiges Reasoning nur noch in einen Steuer-Token gießen. Hartes Limit `NACHFASS_MAX = 2`, turn-weit, zählt **nicht** gegen `max_iterations` (Reparatur ist kein Reasoning). Im Live-Betrieb verifiziert: in einem Fall genügte eine Nachfass-Runde, in einem anderen wurden beide gebraucht — „lieber einmal zu viel als zu wenig" bewährte sich.

**Der Notnagel — Fall 2 doppelt fehlgeschlagen.** Wenn auch beide Nachfass-Iterationen keinen verwertbaren Token liefern, greift kein technisches Auslesen mehr, sondern eine Charakter-Entscheidung: Die Original-Antwort bleibt erhalten, eine neutrale Geste wird angehängt („Hmm... ich muss das nochmal durchgehen."), und über den vorhandenen Self-Trigger-Mechanismus der Event-Queue läuft ein zweiter, vollständiger Durchlauf, in dem Nova die Klärung mit eigenen Worten liefert. Kein vorformulierter Ersatztext, kein steriles Modell-Urteil — wenn der Notnagel zieht, bleibt es Nova.

## 4. Das Prinzip

### Modell-spezifisches Verhalten gehört hinter eine Factory, nicht in den Loop

Wenn ein Modell (oder die Inferenz-Schicht darunter) eine Eigenart hat, die der Konsument umgehen muss, ist die falsche Lösung, eine Fallunterscheidung in die Konsumenten-Logik zu schreiben (`if modell == "gemma4": ...`). Die richtige Lösung ist eine Abstraktion, die das Verhalten kapselt: eine Basisklasse mit No-Op-Standardverhalten, erbende Klassen pro betroffenem Verhalten, Auswahl über eine Factory **an derselben Quelle, aus der die Modellwahl selbst kommt**. ~~am Connector~~ — **05.09.2026 verschaerft:** Die Factory ist nur so gut wie ihr Schluessel. Liest sie eine *andere* Konstante als die, die das Backend waehlt, ist die Kapselung an der Naht wieder offen; die Fallunterscheidung ist dann nicht verschwunden, sondern nur umgezogen. Der Konsument bleibt sauber; das Modell-Wissen lebt an einer Stelle, die man bei einem Fix der Modell-Schicht gezielt entfernen kann. Das ist dasselbe Muster, das die Provider- und Worker-Schicht der Microservice-Welle trägt — hier auf die Thinking-Ebene angewandt.

### Erst messen, dann bauen — und die richtige Frage messen

Der erste Verdacht („lies das thinking-Feld") war plausibel und falsch. Was ihn widerlegte, war nicht besseres Nachdenken, sondern besseres Messen: das vollständige thinking-Feld sichtbar machen und Fall 1 (Steuer-Token vorhanden) von Fall 2 (nur Prosa) unterscheiden. Diese Unterscheidung bestimmte die gesamte Lösung — Fall 1 hätte ein simples Auslesen verlangt, Fall 2 verlangte die Nachfass-Iteration. Wer ohne die zweite Diagnose-Stufe gefixt hätte, hätte das falsche Werkzeug gebaut. Die Lehre ist nicht „logge mehr", sondern: identifiziere die *eine* Tatsache, die zwischen zwei möglichen Lösungen entscheidet, und miss genau die, bevor du baust.

### Ein monatelanger Workaround ist kein Provisorium, sondern Standard

Der `think`/`content`-Split wurde anfangs für einen kurzlebigen Bug gehalten. Tatsächlich sind #10976 und #15260 seit Monaten offen und tragen den Normalbetrieb. Code, der monatelang den Regelfall bedient, ist kein „eigentlich temporär", sondern Architektur — und gehört sauber gebaut und dokumentiert, nicht als Fußnote geduldet. Wenn der Bug eines Tages fällt, baut man gegen die *dann* gültige Realität, nicht gegen eine heute ausgemalte. Den hypothetischen Zukunfts-Pfad nicht auf Vorrat konservieren (YAGNI), aber den realen Gegenwarts-Pfad nicht als Provisorium kleinhalten.

## 5. Die Konsequenz

**Erstens:** Jeder künftige Node, der `think=True` nutzt (z. B. ein PixieGraph-Thinker auf dem Background-Pfad), erbt den Normalizer-Mechanismus über die Connector-Factory — ohne dass der Loop angefasst werden muss. Das thinking-Feld läuft bereits symmetrisch durch beide Worker-Responses.

**Zweitens:** Der Normalizer ist die designierte Stelle, an der ein künftiger Ollama-Fix rückgebaut wird. Fällt #10976, wird `ThinkSplitNormalizer` zur No-Op oder gelöscht, und der Thinker-Loop bleibt unverändert. Die Kapselung macht den Rückbau zu einer lokalen Operation.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum es einen `thinker_nachfass`-Caller im Log gibt, warum der Thinker eine Klasse aus `tools/thinking_normalizer.py` zieht, oder warum bei `think=True` zwei Felder durch die Worker-Kette laufen, liest hier nach. Der Mechanismus wirkt überbaut, bis man die fünf leeren Iterationen kennt, die er verhindert.

## 6. Der Preis

Der `text_len=0`-Bug kostete bei jedem Auftreten bis zu fünf vergebliche Iterationen à ~25 Sekunden — über zwei Minuten Reasoning-Zeit für nichts, am Ende eine ungeprüfte (teils halluzinierte) Antwort. Der eigentliche Preis lag aber im verdeckten Charakter des Defekts: Von außen sah es aus, als „denke Nova lange nach" — tatsächlich drehte sie blind im Leerlauf. Ohne das Diagnose-Logging wäre das schwer von echtem, gründlichem Reasoning zu unterscheiden gewesen. Der zweistufige Diagnose-Aufwand (content/thinking-Längen, dann vollständiges thinking) kostete zwei kurze Mess-Runden; er verhinderte, dass das falsche Werkzeug (simples Feld-Auslesen für einen Fall, der gar nicht vorlag) gebaut wurde.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md`
→ Modul-Dokument: `novaberg-node-thinker.md` §3.4 (ThinkingNormalizer + Nachfass) / §3.5 (Self-Trigger-Notnagel)
→ Konzept-Dokument: `novaberg-microservice-modell-queue_k.md`
→ Externe Belege: Ollama #10976, LiteLLM #18922, verwandt mit #15260

---

## ⚠ Nachtrag (Chat 106, 11.7.2026)

Der oben beschriebene Self-Trigger-Notnagel („läuft ein zweiter, vollständiger
Durchlauf") hat zum Zeitpunkt dieser Lesson **nie funktioniert**. `self_trigger` und
`self_trigger_payload` waren nicht als Channel deklariert und wurden an der ersten
Node-Grenze (Thinker → Tribunal) still verworfen. Live belegt Chat 106, 18:35:22.
Fix: `090ac07`.

Diese Lesson wurde in gutem Glauben geschrieben — der Thinker loggte
`"Self-Trigger fuer Klaerung gesetzt"`. Das Log log.

Der Text bleibt unverändert stehen. Er ist das Zeugnis dafür, dass ein lügendes Log
nicht nur das Debugging in die Irre führt, sondern ein Dokument erzeugt, das die Lüge
beglaubigt und archiviert.

→ siehe novaberg-lesson_l_log-behauptet-was-es-weiss.md
