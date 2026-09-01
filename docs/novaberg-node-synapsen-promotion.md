# Novaberg — Pixie-Agent: SynapsenPromotionAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `agents/synapsen_promotion/agent.py`: der Weg vom Kurzzeit- ins Langzeitgedächtnis
**Stand:** 1. September 2026 (angelegt — der Agent hatte kein Moduldokument, und der Defekt `PROMOTION-NUR-EIN-PAAR` wurde deshalb zunächst im Dokument seines abgelösten Vorgängers vermerkt)
**Pfad:** novaberg/docs/novaberg-node-synapsen-promotion.md
**Konzept:** `novaberg-memory-synapsen_k.md` (P4 — Knoten, Kanten, Spreading)
**Vorgänger:** `novaberg-pixie-promotion.md` — der `PromotionAgent`, den es nicht mehr gibt; die Zwei-Call-Bauart und die EVA-Härtung sind dort beschrieben und hier eingegangen

---

## 1. Aufgabe

Der Agent nimmt Kurzzeit-Einträge, die eine Salienzschwelle gerissen haben, und macht daraus Knoten und Kanten im Langzeitgedächtnis. **Er ist der einzige Weg dorthin** — was er nicht abarbeitet, verfällt mit der TTL des Kurzzeit-Hashes nach sieben bis dreißig Tagen.

Er läuft ausschließlich über den Pixie-Heartbeat (`graph_eignung: ["pixie"]`), auf der **CPU-Spur** (`lastart: "cpu"`): Embed-Worker und Datenbank, kein Sprachmodell.

---

## 2. Wer einreiht, und wer liest

**Eingereiht** wird in `agents/kzg/queues.py`, sobald ein Eintrag `KZG_SALIENZ_HIGH` erreicht — beim Anlegen und bei thematischer Verstärkung eines Nachbarn. `promotion_queue_push` prüft auf einen bestehenden Auftrag für denselben Schlüssel; eine Dublette kann nichts beitragen, weil der Agent die Salienz **frisch aus dem Hash** liest statt aus dem Auftrag.

**Gelesen** wird `queue:{user_id}` — eine Liste je Paar. Seit dem 15.08.2026 liegt die Shadow-Queue in PostgreSQL; diese Liste trägt damit **nur** Promotionsaufträge.

### 2a. Welche Warteschlange gelesen wird

Ein **gezielter** Aufruf nennt sein Paar im Kontext; der **periodische** Pixie-Lauf nennt keines.

> **`PROMOTION-NUR-EIN-PAAR`** — behoben am 01.09.2026, gefunden am selben Tag.
>
> Der Agent las `state["kontext"].get("user_id", "") or DEFAULT_USER_ID`. Ohne Kontext nahm er den Rückfall `meister`, sah in dessen Queue nach und meldete alle fünf Minuten *„Queue leer — nichts zu tun"*. **Die Meldung stimmte für das Paar, in das er schaute** — und genau deshalb fiel nichts auf.
>
> `[gemessen]` 01.09.2026: **13 Aufträge über fünf Paare** lagen unbearbeitet — `nmcp_probe` 5, `b1_live` 2, `nmcp_live` 2, `sektorprobe` 2, `scheibe2probe` 2. **Alle fünf hatten null LZG-Knoten.** Für jedes Paar außer dem Standard entstand nie ein Langzeitgedächtnis, und alles, was darauf aufbaut, lief ins Leere: Die emotionale Gravitation findet nichts zu reaktivieren, und die Prägungsschicht bekommt keine Berührungen.
>
> **Gefunden wurde er nicht durch eine Prüfung**, sondern weil der Betriebsbeleg für die Prägungs-Verstärkung nicht zustande kam und jemand nach dem Grund suchte.
>
> **Nach dem Bau gemessen:** Queue 2 → 0 und LZG 0 → 2 innerhalb von 90 Sekunden; über alle fünf Paare flossen alle 13 Aufträge ab, das Langzeitgedächtnis trägt 13 Knoten, wo vorher keiner stand.

Der Rumpf heißt seit dem 01.09.2026 `_paar_abarbeiten(user_id)`; `invoke` iteriert. Ein gezielter Aufruf bleibt bei seinem Paar, ein periodischer nimmt alle mit Aufträgen (`_paare_mit_auftraegen`). **Nebenlisten sind keine Paare:** `:arbeit`, `:gescheitert` und `:versuche` werden ausgesiebt, sonst zählte ein liegengebliebener Rest als Arbeit eines neuen Paars. Ein Fehler in einem Paar stoppt die übrigen nicht.

**Die Klasse:** Ein Vorgabewert an der Stelle, an der die Eingabe fehlt, macht aus *„nichts angegeben"* ein *„dieses eine"*.

---

## 3. Die Arbeitsliste — warum zwei Listen

**Der Auftrag wird nicht entnommen, sondern verschoben.** `lpop` nahm ihn aus der Liste, bevor die Arbeit begann; scheiterte sie, war die Zeile weg, und nichts reihte sie je wieder ein — der Erzeuger schreibt nur bei einem neuen Turn. Der Kurzzeit-Hash überlebte seine TTL und wurde nie promotet. **Jeder vorübergehende Fehler kostete dauerhaft einen Gedächtniskandidaten**, und die Zählung sagte es nicht.

```
queue:{paar}            wartend
queue:{paar}:arbeit     in Arbeit — genau ein Eintrag, solange es läuft
```

Grün heißt `LREM` aus der Arbeitsliste. Rot heißt: Der Eintrag **bleibt dort liegen** und ist sichtbar statt verschwunden; beim nächsten Lauf wird er zurückgelegt.

**Ein gefülltes `:arbeit` beim Start ist eindeutig**, weil der Pixie-Heartbeat ein Job mit `max_instances=1` ist und dieser Agent nur über ihn erreichbar. Wer hier läuft, läuft allein — ein Rest ist immer der eines abgebrochenen Laufs, nie die Arbeit eines Zweiten. Das ersetzt jede Zeitheuristik.

> Diese Eindeutigkeit hängt daran, dass **niemand den Agenten von außerhalb des Serverprozesses aufruft.** Ein Standalone-Skript liefe neben dem Heartbeat und machte `:arbeit` mehrdeutig — und es scheitert ohnehin, weil die ModelWorker nur im Server-Loop laufen.

Der Versuchszähler steht als eigener Hash, nicht in der Nutzlast: Ihn dort hochzuzählen hieße entnehmen, ändern, neu schreiben — und ein Absturz zwischen den Schritten verlöre genau den Eintrag, den die Mechanik retten soll.

---

## 4. Was gemessen ist

| Was | Gemessen | Wann | Beleg |
|---|---|---|---|
| **Der periodische Lauf erreicht alle Paare** | 13 Aufträge über 5 Paare, alle abgeflossen | 01.09.2026 | Queue-Längen vor und nach dem Neustart |
| **Die Wirkung ist schnell** | Queue 2 → 0, LZG 0 → 2 in **90 Sekunden** | 01.09.2026 | Wächter über `lzg_knoten` je Paar |
| **Der Rückstand war kein Einzelfall** | 11 der 13 Aufträge standen länger als der Befund | 01.09.2026 | `queue:*` beim Befund |
| **Ein Fehler isoliert nicht mehr die übrigen** | Zeuge: ein kaputtes Paar, ein heiles — 1 promotet, 1 in `:arbeit` | 01.09.2026 | `tests/test_promotion_alle_paare.py` |

**Gegenprobe:** Der Umbau zurück auf ein Paar — **3 vorhergesagt, 3 gezählt**, und es waren die vorhergesagten.

**Eine Zusicherung wurde dabei gestrichen**, statt sie grün zu färben: Sie prüfte, dass fremde Aufgabenarten in derselben Queue liegen bleiben. Die Shadow-Queue liegt seit dem 15.08.2026 in PostgreSQL; `queue:{paar}` trägt nur Promotionen. **Ein Zeuge auf einen Fall, den der Bestand nicht hervorbringt, prüft nichts.**

---

## 5. Zeugen

`tests/test_promotion_alle_paare.py` (5) — der periodische Lauf über alle Paare, der gezielte über eines, Nebenlisten, die Summierung, ein Fehler je Paar.
`tests/test_promotion_arbeitsliste.py` (7) — was grün durchläuft, ist fort; was rot läuft, liegt sichtbar.
`tests/test_promotion_queue_dubletten.py` (8) — derselbe Schlüssel steht höchstens einmal.

Redis ist in allen dreien ein Fake mit echter Listen-Semantik statt eines MagicMock: Geprüft wird, was am Ende in den Listen steht, nicht welche Methoden gerufen wurden.

---

## 6. Offene Punkte

**Der Agent hat keinen eigenen Zeugen für den Promotionsvorgang selbst** — die drei Testdateien decken die Warteschlange, nicht die Umwandlung eines Kurzzeit-Eintrags in Knoten und Kanten. `_eintrag_verarbeiten` ist mit 86 Anweisungen und 13 Verzweigungen die komplexeste Funktion des Moduls und in den Zeugen durchgehend ersetzt.

**Der Lauf ist nach Paaren sequenziell.** Bei vielen Paaren mit großem Rückstand kann ein Heartbeat lange dauern; er läuft auf der CPU-Spur und blockiert dort die übrigen Agenten. Bisher nicht gemessen, weil der Rückstand vor dem 01.09.2026 nie abfloss.
