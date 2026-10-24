# Novaberg — Pixie-Agent: SynapsenPromotionAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Moduldokument — `agents/synapsen_promotion/agent.py`: der Weg vom Kurzzeit- ins Langzeitgedächtnis
**Stand:** 23. Oktober 2026, 22:31 UTC (`date -u`; Schritt 4 und die Dublette committet als `d11de95` und `782274c` und im Betrieb gemessen, beide Kennungen im Archiv). Davor 23. Oktober 2026, 21:18 UTC (`date -u`; **§3b neu — der Weg eines Eintrags mit Schritt 4:** Nach einer gelungenen Neuanlage wird der KZG-Hash gelöscht, nach einem Treffer bleibt er bis zur TTL; ein Treffer auf einen aktiven Knoten ist eine Dublette ohne Verstärkung — gebaut, getestet und gegengeprüft in den Code-Trees `2d18b83` und `5342a6a`, im Betrieb nicht gemessen; §3a, §5 (`tests/test_promotion_umzug.py`, 11 Zeugen) und §6 nachgezogen). Davor 23. Oktober 2026, 20:11 UTC (`date -u`; §6: die Verstärkung beim Treffer ist nach der Entscheidung vom 23.10.2026 ein Defekt, `LZG-PROMOTION-TREFFER-VERSTAERKT`). Davor 19. September 2026, 20:53 UTC (`date -u`; ein unlesbarer Anlagezeitpunkt wird verworfen statt erfunden, §3a). Davor 18. September 2026 (Audit: der Dienst belegt seinen Lauf selbst). Davor 4. September 2026 (**zwei Defekte gegen das Konzept**: Der KZG-Hash wird entgegen §7.7 nach der Promotion **nicht geloescht** — der Eintrag geht erneut durch und matcht den Knoten, der aus ihm selbst entstand: **95,2 % aller 14.947 Verstaerkungen tragen `cosine = 1.0000`**, bis zu 91 je Turn ueber acht Tage. Und die Verstaerkung sitzt hier statt im Dispatcher, wo sie nach dem neuen §7.1a hingehoert. Beleg und Kennungen: `novaberg-memory-synapsen_k.md` §7.1a, `KZG-EINTRAG-BLEIBT-NACH-PROMOTION`, `KZG-THEMA-VERSTAERKT-NACHBARN`, `VERSTAERKUNG-OHNE-VERWENDUNG`.). Davor 1. September 2026 (angelegt — der Agent hatte kein Moduldokument, und der Defekt `PROMOTION-NUR-EIN-PAAR` wurde deshalb zunächst im Dokument seines abgelösten Vorgängers vermerkt)
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

## 3a. Was verworfen wird

**Verworfen wird, was nie grün werden kann**, und zwar vor dem Embedding: ein Auftrag ohne Schlüssel, ein Kurzzeit-Hash, der nicht mehr steht — TTL abgelaufen oder, seit dem 23.10.2026, nach einer Neuanlage schon promotet und gelöscht (etwa ein zweiter Auftrag für denselben Schlüssel) —, ein leerer Inhalt und seit dem 19.09.2026 ein fehlender oder unlesbarer Anlagezeitpunkt (`erstellt_am`; auch `nan`, unendlich und Werte ≤ 0, `_kzg_erstellt_am_lesen`). Ein verworfener Eintrag schreibt `fehler` in `hintergrund_log` und `pipeline_log`, beim Anlagezeitpunkt mit Rohwert und Schlüssel. Er verlässt die Arbeitsliste, denn erneutes Zustellen macht ihn nicht lesbar.

**Bis zum 19.09.2026 stand für einen unlesbaren Anlagezeitpunkt still *jetzt*.** Der Knoten trug dann ein erfundenes `kzg_erstellt_am` (die Spalte ist `NOT NULL`) und sah aus wie jeder andere. Im Bestand hat das keine Spur hinterlassen: 4.552 von 4.555 Knoten tragen den Zeitpunkt ihres Schlüssels auf die Millisekunde, 3 weichen um 1 ms ab (Rundung) `[gemessen 19.09.2026]`.

## 3b. Der Weg eines Eintrags — und Schritt 4 (seit dem 23.10.2026)

`_eintrag_verarbeiten` prüft die vier Vorbedingungen (§3a), liest die Felder aus dem Hash, bettet den Inhalt allein ein und lädt die Knoten des Paares samt Kosinus, auch deaktivierte (`kandidaten_mit_cosine_laden(…, include_inactive=True)`). Der beste wird gegen `LZG_KNOTEN_MATCH_SCHWELLE` (0,82) geprüft (`match_pruefen`). Dann einer von drei Pfaden:

| Pfad | Wann | Was geschieht | `aktion` | KZG-Hash danach |
|---|---|---|---|---|
| **Halbreaktivierung** | Treffer auf einen deaktivierten Knoten | `reactivate_node` weckt ihn (halber `gewicht_decay`, `aktiv = TRUE`), keine Kanten neu (`novaberg-memory-synapsen_t.md` §9.3) | `halbreaktivierung` | bleibt bis zur TTL |
| **Dublette** | Treffer auf einen aktiven Knoten | nichts am Knoten: kein `knoten_verstaerken`, keine Neuberechnung der Kanten (§7.1a) — bis zum 23.10.2026 an dieser Stelle die Verstärkung samt Trigger 2, Aktion `reinforcement` (Festlegung K10) | `dublette` | bleibt bis zur TTL |
| **Neuanlage** | kein Treffer | `knoten_anlegen`, dann Kanten zu allen Kandidaten (Trigger 1) | `neuanlage` | **gelöscht** (Schritt 4) |

Hinter allen drei bekommt die Brücke `verbindung` die `lzg_id` des Knotens, `hash_dirty` wird gesetzt, und der Rückweg wird eingereiht — er liest `turn_id` aus dem Hash. **Dann folgt Schritt 4, nur nach einer Neuanlage: Der KZG-Hash wird gelöscht** (`_kzg_eintrag_loeschen`; `novaberg-memory-synapsen_t.md` §7.2, §7.7; `novaberg-kzg-salienz_t.md` §8). Gelöscht wird genau der Schlüssel des Auftrags und nur mit dem Präfix `kzg:`; danach prüft `exists`, dass er fort ist. **Nach einem Treffer bleibt der Hash bis zu seiner TTL stehen:** Aus dem Eintrag entsteht dort kein Knoten, seine eigenen Felder kämen nirgends an, und ein Löschen wäre ein Datenverlust. Das ist der Regelfall und kein Fehler; die Schlusszeile trägt `kzg_geloescht=nein`. **Nach einem Fehlschlag bleibt er ebenso:** `knoten_anlegen` liefert `None` (`_fehler`, der Lauf endet vor Schritt 4), oder eine Ausnahme bricht den Lauf ab (der Auftrag bleibt in `:arbeit`, §3). **Ein Fehler beim `DEL` wirft nicht:** Knoten und Rückweg stehen schon, und ein Wurf ließe den Auftrag in der Arbeitsliste — der nächste Lauf reihte den Rückweg ein zweites Mal ein. Der Fehler steht laut im Log und als Fehlerzeile im `pipeline_log` (`schritt=kzg_loeschen`), der Hash fällt auf seine TTL zurück. Die Schlusszeile in `hintergrund_log` und `pipeline_log` trägt `kzg_geloescht`; ein Löschen ohne Fehler schreibt dazu eine eigene Zeile `aktion=kzg_geloescht`.

**Warum diese Reihenfolge:** Bis zum Rückweg liest der Lauf den Hash; die Brücke liest ihn nicht, sie trägt nur den Schlüssel. Ein Löschen davor ließe den Rückweg ohne `turn_id`.

**Bis zum 23.10.2026 blieb der Hash auch nach einer Neuanlage stehen** und verfiel über seine TTL. Er ging erneut in die Promotion und traf den Knoten, der aus ihm entstand — `[gemessen 04.09.2026]` 95,2 % von 14.947 Verstärkungen mit `cosine = 1.0000` (`KZG-EINTRAG-BLEIBT-NACH-PROMOTION`). Gebaut in den Code-Trees `2d18b83` (Schritt 4) und `5342a6a` (Dublette), ~~**im Betrieb nicht gemessen**; beide Kennungen bleiben offen bis zur Messung~~ → committet als `d11de95` und `782274c`, im Betrieb gemessen am 23.10.2026; beide Kennungen im Archiv. Einträge, die vor dem Bau promotet wurden, verfallen weiter über ihre TTL.

**Was der Bau offen lässt** (Fundliste, 23.10.2026): Ein Hash, der nach einem Treffer stehen bleibt, kann erneut eingereiht werden und geht dann mit Brücke, `hash_dirty` und Rückweg noch einmal durch; der Rückweg wird auch für eine Dublette eingereiht; der Kommentar über der Brücke spricht für alle drei Pfade von einem Umzug; eine gescheiterte Halbreaktivierung meldet nur eine Warnung (Bestand); nach einem als neuer Knoten promoteten Turn fehlt der Hash dem Kalibrier-Korpus (`agents/kalibrierung/korpus.py`); zwischen `hget` und `hset` der thematischen Verstärkung kann das Löschen einen Rumpf-Hash ohne `inhalt` entstehen lassen.

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
`tests/test_promotion_erstellt_am.py` (4) — ein fehlender, unlesbarer oder nicht endlicher Anlagezeitpunkt ergibt keinen Knoten, sondern eine Fehlerzeile mit Rohwert; ein gültiger kommt unverändert am Knoten an. Er läuft durch den echten `invoke` bis `knoten_anlegen`. Sein Redis-Doppel kennt seit dem 23.10.2026 `delete`, und der Hash folgt dem Löschen; die Zusicherungen sind unverändert.
`tests/test_promotion_umzug.py` (11, seit dem 23.10.2026) — der echte `_eintrag_verarbeiten` gegen ein Redis-Doppel mit echter Hash-Semantik, das jedes `delete` zählt. Nach der Neuanlage ist der Schlüssel fort, und zwar erst nachdem der Rückweg `turn_id` gelesen hat; nach Treffer und Wecken (`HitKeepsTest`), nach gescheiterter Anlage, gescheitertem Wecken und einer Ausnahme steht er noch, ohne `delete`; ein `DEL` mit `ConnectionError` wirft nicht und schreibt genau eine Fehlerzeile; ein Schlüssel ohne `kzg:` wird nicht gelöscht und schreibt eine Fehlerzeile. `DuplicateHitTest`: Ein Treffer auf einen aktiven Knoten ruft weder `knoten_verstaerken` noch `kanten_neuberechnen_fuer_knoten`, `knoten_anlegen`, `reactivate_node` oder `delete`; der Zwilling weckt einen deaktivierten. Gegenprobe über beide Bauten **7 von 8, kein blinder Zeuge** (`labor/2026-10-23_promotion_gegenprobe.txt`): Die eine Abweichung ist eine Vorhersage, die für einen Stand ohne Dublette geschrieben war — auf diesem wurde ein Zeuge mehr rot als vorhergesagt; auch der Präfix-Riegel ist bezeugt.

Redis ist in allen ~~vieren~~ → fünfen ein Fake statt eines MagicMock, mit echter Listen- und in `test_promotion_umzug.py` echter Hash-Semantik: Geprüft wird vor allem, was am Ende in den Listen und Hashes steht, nicht welche Methoden gerufen wurden.

---

## 6. Offene Punkte

**Der Treffer verstärkt, und das ist seit dem 23.10.2026 ein Defekt** (`LZG-PROMOTION-TREFFER-VERSTAERKT`). Gleicht ein Eintrag einem Knoten des Paares mit Kosinus ≥ 0,82, verstärkt der Agent einen aktiven Knoten (`knoten_verstaerken`, danach Trigger 2), wie es die Festlegung K10 vorsah. Entschieden ist seither das Gegenteil: Es gilt die Regel *„Verstärkt wird ausschließlich, was Nova in ihrer Antwort tatsächlich hergenommen hat“* — ein Treffer verhindert nur die Dublette ([`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md) A, E7; [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) §7.1a). Der Dispatcher verstärkt über die Verwendung seit dem 04.09.2026; ~~dieser Agent tut es daneben weiter~~. → **Behoben im Code-Tree `5342a6a`** (23.10.2026; ~~im Betrieb nicht gemessen, die Kennung bleibt offen bis dahin~~ → committet als `782274c`, im Betrieb gemessen am 23.10.2026, die Kennung im Archiv): Der Treffer auf einen aktiven Knoten ist eine Dublette (§3b); dieser Agent verstärkt nicht mehr.

~~**Der Agent hat nur einen schmalen Zeugen für den Promotionsvorgang selbst.**~~ Drei Testdateien decken die Warteschlange; `tests/test_promotion_erstellt_am.py` führt seit dem 19.09.2026 durch den echten `_eintrag_verarbeiten`, aber nur bis zur Anlage eines Knotens, mit ersetztem Embedding, Kandidaten und Kanten. ~~Reinforcement, Halbreaktivierung und die Kantenbildung bleiben unbezeugt.~~ → Seit dem 23.10.2026 bezeugt `tests/test_promotion_umzug.py` die drei Pfade bis Schritt 4, Dublette und Halbreaktivierung je mit Zwilling (§5); die Kantenbildung bleibt unbezeugt, sie ist dort ersetzt. `_eintrag_verarbeiten` ist mit ~~85 Anweisungen und 13 Verzweigungen~~ → 88 Anweisungen und 14 Verzweigungen (`ruff`, PLR0915 und PLR0912, am Code-Tree `5342a6a`) die komplexeste Funktion des Moduls.

**Der Lauf ist nach Paaren sequenziell.** Bei vielen Paaren mit großem Rückstand kann ein Heartbeat lange dauern; er läuft auf der CPU-Spur und blockiert dort die übrigen Agenten. Bisher nicht gemessen, weil der Rückstand vor dem 01.09.2026 nie abfloss.

## Audit (seit 18.09.2026)

**Der Dienst belegt jeden Lauf selbst** im `hintergrund_log`, unter der Aufgabe `synapsen_promotion` (`BaseAgent._audit`, `80d4b37`): `gestartet`, dann `erledigt` mit den Zählern über alle Paare (`promotet`, `fehler`, `zurueckgelegt`, `endgueltig`) oder `fehler`. Die Zeilen je KZG-Schlüssel (`synapsen_promotion:<key>`) bleiben daneben. Im Betrieb am 18.09.2026, 23:24 UTC: `promotet=12, fehler=0`. Eine Ausnahme aus dem Lauf wird dort als `fehler` belegt, nicht weitergeworfen. Der Pixie-Dispatch schreibt nur noch, wenn der Dienst schweigt — eine entkommene Ausnahme oder ein fehlender Agent (`novaberg-convention-nmcp.md` §8.4, Entscheidung vom 18.09.2026).
