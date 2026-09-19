# Novaberg — Der Verfall der Shadow-Queue (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-queue-verfall_k.md`](novaberg-queue-verfall_k.md) · Ausarbeitung: [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md) · Diskussion und Ergänzungen: [`novaberg-queue-verfall_e.md`](novaberg-queue-verfall_e.md) · Messungen: [`novaberg-queue-verfall_m.md`](novaberg-queue-verfall_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 10. Die Migration des Bestands

1036 Aufträge liegen als JSON in einer Redis-Liste. Sie tragen keine der neuen Größen.

| Feld | Wert bei der Übernahme | Grund |
|---|---|---|
| `salienz_absolut` | der heutige `prioritaet`-Wert | er *ist* die Auslöse-Salienz |
| `salienz_decay` | **gerechnet**, nicht kopiert | siehe unten |
| `salienz_roh` | rückgerechnet aus `absolut` | `CAP × (asin((absolut/CAP)^(1/exp)) × 2/π)` |
| `haeufigkeit` | 1 | Wiederkehr wurde nie gezählt |
| `verstaerkt_am` | `erstellt` | es gab keine Verstärkung |
| `character_id` | `'nova'` | einziger Charakter im Bestand |
| `beobachter` | `'user'` | der Auslöser war eine Nutzeräußerung |
| `versuche` | `_retries` oder 0 | |

**`salienz_decay` wird beim Übernehmen gerechnet, nicht kopiert.** Der Bestand ist bis zu 18 Tage alt; wer den Anker als Präsenz einträgt, setzt alle Aufträge auf „gerade eben verstärkt" und verschiebt den ersten Verfall um bis zu 18 Tage. Die Formel aus §5 mit `verstaerkt_am = erstellt` bildet das Alter korrekt ab.

**Die 233 Aufträge auf 0,0 fallen beim ersten Lauf sämtlich heraus.** Das ist **gewollt und wird vorher aufgeschrieben**, damit es niemand später für einen Unfall hält. Sie tragen keine gemessene Salienz, sondern eine, die nie geschrieben wurde.

**Die Ursache ist am 15.08.2026 gefunden und gehört hierher, weil sie den Umzug zur Bedingung hat.** `shadow_queue_push` wird von **zwei** Stellen gerufen, und nur eine übergibt den Wert:

```
agents/kzg/queues.py   shadow_queue_push(… prioritaet=neue_salienz …)   ✅
memory/kzg.py          shadow_queue_push(… kein prioritaet-Argument …)  ❌
```

Die Signatur trägt `prioritaet: float = 0.0`. **Der Vorgabewert macht aus einem fehlenden Argument eine Zahl, die wie eine gemessene aussieht** — der Aufruf ist vollständig, es fehlt nichts sichtbar. Geführt als `KANDIDATEN-PRIORITAET-STILLE-NULL`.

**Eine Rekonstruktion der Werte ist trotzdem nicht möglich**: Der auslösende Turn ist nicht mehr zuzuordnen.

> **Der Defekt ist vor dem Umzug zu beheben, nicht danach.** Das neue Schema erzwingt `salienz_absolut NOT NULL` **ohne Vorgabewert** — genau das, was hier fehlt. Wird der Aufrufer vorher berichtigt, ist der Umzug still; wird er es nicht, scheitert nach dem Umzug jeder zweite Schreibpfad an der Datenbank. **Das ist der gewünschte Ausgang und trotzdem der falsche Zeitpunkt**, ihn zu entdecken.

> **Sie fallen heraus, sie verschwinden nicht.** Genau dafür ist das Soft-Delete da. Zeigt sich später, dass die Null ein Schreibfehler war und nicht ein schwacher Anlass, stehen 233 Aufträge zur Reaktivierung bereit — bei hartem Löschen wären sie weg.

---

## 13. Die drei Zeilen

| | |
|---|---|
| **ZIEL** | Ein Auftrag, den 30 Tage lang kein Anlass mehr berührt hat, wird für die Auswahl unsichtbar, bleibt aber gespeichert und kommt bei einem neuen Anlass zum selben Gegenstand mit halber Dringlichkeit zurück. Ein **abgearbeiteter** Auftrag verschwindet dagegen ganz. |
| **TEST** | Wird rot, wenn ein Auftrag mit `salienz_decay` unter 0,3 nach einem Verfallslauf noch `aktiv = TRUE` trägt; wenn ein Auftrag durch den **Verfallslauf** aus der Tabelle verschwindet; wenn ein **erledigter** Auftrag in der Tabelle stehen bleibt; wenn die Auswahl einen inaktiven Auftrag liefert; und wenn die Reaktivierung einen Wert setzt, der nicht `(salienz_absolut + 0,3) / 2` ist. Dazu zwei Gegenproben: Ein Auftrag mit `verstaerkt_am` von vor 29 Tagen bleibt aktiv, einer von vor 31 Tagen nicht — und **die Auswahl liefert bei zwei Aufträgen gleicher Herkunft den jüngeren** (§12.3), was heute umgekehrt wäre. |
| **MESSUNG** | Ein echter Lauf gegen den migrierten Bestand. **Vorhergesagt, bevor er läuft:** 233 Deaktivierungen (die stillen Nullen), 0 weitere — kein Auftrag im Bestand ist älter als 18 Tage. Ein zweiter Lauf 30 Tage später trifft die dann fälligen. |

> **Die Messung hat eine Hürde, die vor dem Bau zu nennen ist.** Die eigentliche Wirkung — ein Auftrag fällt durch Alter heraus — ist am Bestand vom 15.08.2026 **nicht** zu beobachten, weil er zu jung ist. Sie ist nur über gesetzte Zeitstempel prüfbar, und das ist ein Zeuge, keine Messung. Die echte Messung braucht 30 Tage Betrieb. Das ist kein Grund, sie zu ersetzen, sondern einer, sie einzuplanen.

---

## 16. Gebaut und gemessen — 15.08.2026

*Die Messungen aus §16 — „Die Migration“, „Der Verfallslauf am echten Bestand“, „Die Kette, am laufenden Server belegt“ und „Was ungemessen bleibt, ausdrücklich“ — stehen in [`novaberg-queue-verfall_m.md`](novaberg-queue-verfall_m.md).*

`shadow_auftrag` in `db/init.sql`, `memory/repositories/shadow_auftrag_repository.py`,
fünf Konstanten in `config.py`, Umbau von `services/shadow_agent/utils.py`,
`services/pixie/kandidaten.py` und `services/pixie/dispatch.py`, dritter Schritt
in `agents/synapsen_decay/`. **1399 Tests grün, 0 übersprungen** (1373 vorher,
26 neu). Beide Wände sauber, alle berührten Dateien auf ihrer Nulllinie.

### Die Reihenfolge, in der gebaut wurde

**Die stille Null zuerst** — sie war Vorbedingung, weil das Schema erzwingt,
was in der Signatur fehlte. `memory/kzg.py` übergibt seither die Salienz, und
der Vorgabewert `0.0` ist aus `shadow_queue_push` verschwunden.

**Dann die Tabelle**, in der von `16_PERSISTENZ.md` §2 geforderten Folge:
Zeuge zuerst — er brannte gegen das unveränderte Schema und war rot —, dann
der Schema-Edit, dann ein Anfasser. Der Beleg steht im Behälter-Log:
**132 Statements** statt 129, also genau eine Tabelle und zwei Indizes.

### Was der Bau am Konzept berichtigt hat

**Die Migration übernimmt 1:1, ohne Verdichtung.** Das Konzept ließ offen, ob
gleiche Gegenstände beim Übernehmen verschmelzen sollen. Sie tun es nicht: Eine
Verdichtung setzte `haeufigkeit` auf eine Zahl, die nie gemessen wurde. Echte
Dubletten verschmelzen beim nächsten Anlass von selbst.

**Ein zirkulärer Import war zu brechen.** `services/shadow_agent/utils.py`
holt das Repository, `memory/__init__` lädt `memory.kzg`, und die holt sich
`shadow_queue_push` aus genau diesem Modul. Der Import steht deshalb lokal in
der Funktion.

**Der Dispatcher las zwei Feldnamen, die es nie gab.** Der AgentState bekam
`themen` und `salienz` aus dem Auftrag — beides Schlüssel, die ein
Shadow-Auftrag nicht trägt; er erhielt dauerhaft `""` und `0.0`. Derselbe
Namensirrtum stand im Moduldokument und im Rückfall der Kandidatenwahl.
Berichtigt im Zug des Umbaus, weil die alten Namen nach dem Umzug ohnehin
nicht mehr existieren.

### Fünf Bestandszeugen mussten nachgezogen werden

Sie prüften richtige Zusicherungen über den Redis-Umweg. Vier davon gelten
unverändert und belegen sich jetzt an der Tabelle. **Einer beschrieb eine
Zusicherung, die dieser Bau aufhebt:** *„Queue-Einträge altern nicht"* — sie
altern jetzt nach unten. Sein Kern bleibt und ist schärfer geworden: Ein
Auftrag ohne Agenten wandert nicht nach oben, **und er bleibt auch nicht
liegen.**

> **Nebenbei behoben: `SUITE-HAENGT-AM-AKTIVEN-PAAR`.** Zwei Fälle in
> `test_pixie_aging.py` wurden rot, sobald das aktive Paar auf eine Testpersona
> stand. Sie stellen die Queue jetzt über einen Patch, statt sie zu lesen —
> sie prüfen die Wahl des Schedulers, nicht den Speicher.

### Was der Audit der Nähte fand — drei Leser, die niemand mitgeändert hat

**Nach dem Bau wurden die Schnittstellen einzeln durchgegangen.** Fünf Nähte,
drei davon gebrochen — und keine hatte die Suite bemerkt, weil alle drei
*hinter* den geprüften Stellen lagen.

| Naht | Befund |
|---|---|
| Redis-Schlüssel `shadow_queue:*` | sauber, kein Leser mehr im Produktivcode |
| `queue_key` / `queue_raw` / `auftrag_id` | sauber, nach Speicher getrennt |
| **`quelle`-Wert** | **gebrochen** — `services/pixie/router.py` |
| **Auftragsfelder in den Agenten** | **gebrochen** — `recherche`, `nachfragen` |
| Promotions-Queue | sauber, liest ihre eigenen Felder |

**Der Router kannte den neuen Wert nicht.** Er verzweigte weiter auf
`quelle == "queue"`. Die Wirkung war vollständig und still: Der Heartbeat
wählte im Dreißig-Sekunden-Takt einen Auftrag, der Router fand keinen Agenten,
der Auftrag blieb liegen. **Kein einziger Shadow-Auftrag lief mehr** — und die
Warnung je Zyklus sah aus wie der lange bekannte Fall *„Auftrag für einen
Agenten, den es nicht gibt"*. Kein Datenverlust, weil `abschluss` erst nach
einer Ausführung greift.

**`_salienz_aus_auftrag` las zwei Felder, die es nicht mehr gibt.** Der
Recherche-Agent griff nach `salienz` oder `prioritaet`; ein migrierter Auftrag
trägt keines von beiden, sondern drei Salienz-Stände. **Jeder Recherche-Auftrag
hätte `ValueError` geworfen, wäre als Fehlversuch gezählt und nach drei
Versuchen verworfen worden** — bei 608 Aufträgen. Er liest jetzt
`salienz_absolut` zuerst: den **Anker**, nicht die Präsenz. Der Anker ist, was
der Auftrag beim Anlass wert war; die Präsenz schriebe sein Alter in die
Bibliothek.

Dazu eine Logzeile im Nachfragen-Agenten, die den Auftrag über `erstellt`
datierte — jetzt `erstellt_am`.

> **Wer einen Wert einführt, muss seine Leser suchen — nicht nur seine
> Schreiber.** Die Zeugen des Umbaus prüfen den Erzeuger, die Auswahl und den
> Abschluss. **Zwischen Auswahl und Abschluss steht der Router, und ihn hat
> niemand gefragt.** `tests/test_pixie_verdrahtung.py` prüft seither die
> **Kette** statt ihrer Glieder: Es liest die möglichen `quelle`-Werte aus dem
> Quelltext des Erzeugers, statt sie aufzuzählen — eine Aufzählung wäre beim
> nächsten neuen Wert wieder still veraltet.

**Nebenbei bezeugt statt vermutet:** Der Router löst `vertiefen` auf
`vertiefung` auf, und kein Agent dieses Namens ist registriert
(`PIXIE-ROUTING-DOPPELREGISTRY`). Das ist der Grund, warum 383 Aufträge liegen.
Der Fall steht jetzt als Zeuge und ist zu **streichen**, nicht anzupassen,
sobald der Agent existiert.
