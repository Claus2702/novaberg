# Novaberg — Lesson: Die gelesene Quelle ist nicht die wirksame

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Wo ein Wert zweimal existiert, entscheidet nicht der, den man liest
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-lesson_l_gelesen-ist-nicht-wirksam.md
**Auslöser:** Drei Defekte an einem Tag, alle mit derselben Bauart, keiner von einem Test gefunden
**Verwandt:** `novaberg-lesson_l_log-behauptet-was-es-weiss.md`, `novaberg-lesson_l_silent-skip.md`, `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`

---

## 1. Drei Fälle, eine Bauart

### Fall 1 — Die Quittung aus dem verworfenen Zustand

Ein Upsert lief über `db_manager.select()`, weil die Funktion eine Rückgabe hat und der Aufrufer den `RETURNING`-Wert brauchte. Sie lehnt das Schreib-Statement nicht ab — sie **führt es aus**, liest die Zeilen aus der offenen Transaktion und legt die Verbindung ohne `commit` in den Pool zurück. Dort wird alles verworfen.

Der Lauf meldete zwanzig Neuanlagen. Die Tabelle hatte keine. Die zwanzig Zeilen hatten wirklich existiert — in einem Zustand, den es Sekunden später nicht mehr gab.

### Fall 2 — Die Konfiguration, die nur beim ersten Start gilt

Der Pixie-Zeitplan schrieb seinen Redis-Eintrag unter `if not redis_client.exists(key)`. Beim ersten Start entstand er aus `config.py`; ab dem zweiten war der **gespeicherte** Wert maßgeblich. Jede spätere Änderung an Intervall oder Priorität stand im Code, wirkte aber nie — ohne Fehler, ohne Warnung, ohne etwas, das widersprochen hätte.

Betroffen waren alle sieben periodischen Aufgaben. **Folge für alles Frühere:** Beobachtungen zum Takt- oder Prioritätsverhalten vor Commit `3dc151e` können gegen einen veralteten Redis-Stand gemessen worden sein statt gegen den Code. Ein Backfill ist nicht möglich; die damaligen Werte sind fort.

### Fall 3 — Das Register und seine Abschrift

Ein Agent wird in der `AgentRegistry` registriert. Der periodische Router entscheidet aber nicht anhand des Registers, sondern anhand einer **Tabelle daneben**, die dieselbe Zuordnung ein zweites Mal führt. Der neu registrierte Agent gewann den Heartbeat, fand keine Route und starb mit einer Warnung — und weil der Takt einen Gewinner je Runde kennt, lief in dieser Runde auch sonst nichts.

---

## 2. Was die drei gemeinsam haben

In jedem Fall existiert derselbe Sachverhalt **zweimal**: einmal dort, wo er geschrieben wird, einmal dort, wo er wirkt.

| | geschrieben | wirksam |
|---|---|---|
| Fall 1 | Zeilen der offenen Transaktion | der committete Stand |
| Fall 2 | `config.py` | der Redis-Eintrag |
| Fall 3 | `AgentRegistry` | die Routing-Tabelle |

Und in jedem Fall wird die **geschriebene** Seite gelesen und für die wirksame gehalten.

Das unterscheidet die Klasse von den benachbarten Lessons. Ein Silent Skip **überspringt** die Arbeit. Ein Default **täuscht** einen geladenen Wert vor. Ein Log **behauptet** eine Wirkung, die es nicht beobachten kann. Hier dagegen ist alles ehrlich: Die Zeilen sind echt, der Konfigurationswert ist echt, die Registrierung ist echt. Nur gilt keiner von ihnen.

Deshalb ist die Klasse schwerer zu sehen als die anderen — es gibt **nichts Falsches** zu finden. Es gibt nur etwas Zweites.

---

## 3. Die Regel

> **Wo ein Wert an zwei Stellen lebt, muss eine der beiden die andere erzeugen — oder ihr widersprechen. Schweigen ist die Fehlerbedingung.**

Drei brauchbare Formen, alle drei am selben Tag gebaut:

- **Ableiten statt abschreiben.** Das Routing fällt auf Namensgleichheit zurück; die Tabelle bleibt nur für die Fälle, in denen die Namen wirklich abweichen. Was abgeleitet wird, kann nicht auseinanderlaufen.
- **Bei jedem Start angleichen, nicht nur beim ersten.** Der Zeitplan zieht Intervall, Priorität und Beschreibung aus der Konfiguration nach und **loggt die Abweichung**. Der laufende Zustand bleibt, wo er nur den Takt betrifft (`next_run`), damit ein Reload den Schlag nicht vorzieht.
- **Die Quittung aus dem Zustand nehmen, der gilt.** `execute_returning` committet und gibt die Zeile zurück. Es gab die Funktion längst; gegriffen wurde zur falschen, weil sie zufällig auch etwas zurückgibt.

---

## 4. Warum kein Test das findet

Alle drei Defekte bestanden, während die Suite grün war — 173 Tests, keiner übersprungen.

Ein Unit-Test baut seine Welt selbst auf und wieder ab. In dieser Welt gibt es **nur eine Wahrheit**: keinen zweiten Start, gegen den eine gespeicherte Konfiguration gewinnen könnte; keine Verbindung, die in einen Pool zurückkehrt; kein Register, das über die Laufzeit hinaus bestünde. Die Klasse entsteht erst dort, wo ein zweiter Speicher den Lauf überdauert — und genau den stellt ein Test nicht her.

Gefunden wurden alle drei durch **Nachmessen am laufenden System**: die Tabelle zählen statt dem Zähler glauben, den Redis-Eintrag lesen statt der Konstante, den Heartbeat beobachten statt der Registrierung.

---

## 5. Der Prüfblick für Bestandscode

- Gibt es zu diesem Konfigurationswert einen **persistierten Zwilling**? Wer gewinnt beim zweiten Start?
- Wird eine Quittung in demselben Zustand gelesen, der nachher gilt — oder in einem, der noch verworfen werden kann?
- Spiegelt eine **Aufzählung** ein Register? Was geschieht mit dem Eintrag, den die Aufzählung nicht kennt: Fehler, oder Stille?
- Und zuletzt, für alle drei: **Was widerspricht, wenn die beiden Seiten auseinanderlaufen?** Wenn die Antwort „nichts" lautet, ist das der Defekt — nicht der aktuelle Unterschied, sondern das fehlende Widerwort.
