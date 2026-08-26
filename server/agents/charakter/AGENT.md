# CharakterAgent

Destilliert 5 Charakter-Profile aus LZG (PostgreSQL) und KZG (Redis).

## Trigger
- Periodisch (alle 10 min), aber nur aktiv wenn `hash_dirty:{user_id}` gesetzt
- Flag wird vom PromotionAgent nach erfolgreicher LZG-Promotion gesetzt

## Profile
| Profil | Quelle | Beschreibt |
|--------|--------|-----------|
| kern_hash | ~~LZG~~ → ~~40 Turns~~ → **Wortlaut der Begegnungen** (`pipeline_log`, `herkunft='nutzer_turn'`), **zeitlich geschichtet über die ganze Historie bis `PIXIE_CHARAKTER_KERN_BUDGET_ZEICHEN`** | Grundpersönlichkeit |
| adaptive_hash | KZG | Aktuelle Phase |
| intentions_profil | LZG | Kommunikationsstil |
| emotions_profil | LZG | Emotionale Grundtendenz |
| beziehungsprofil | KZG-Schlüssel → Turn-Wortlaut | Beziehungsdynamik |

## Nur Begegnungen speisen den Kern (seit 16.08.2026)

`_turns_laden` verlangt `herkunft='nutzer_turn'`. **Ein eigener Impuls hat kein
Gegenüber**, und beide Räder messen eine Haltung *gegenüber* jemandem — er
trägt deshalb zu keinem der beiden Profile bei.

Der Anlass war ein Defekt: Ein Impuls schreibt seinen Text in dasselbe Feld
`user_prompt` wie eine Nutzeräußerung. Ungefiltert las der Kern die eigenen
Gedanken der Figur als Äußerungen des Menschen — gemessen **25 von 40 Turns,
95,4 % des Materials**. Was ausgenommen wird, steht mit seiner Zahl im Log.

## Das Material ist geschichtet, nicht das Ende der Historie (seit 26.08.2026)

`_turns_laden` liest nicht mehr die 40 neuesten Begegnungen, sondern zieht
**zeitlich gleichmäßig über die ganze Historie**, bis das Zeichenbudget
`PIXIE_CHARAKTER_KERN_BUDGET_ZEICHEN` erschöpft ist. Gelesen wird in zwei
Schritten: erst Kennung und Zeichenzahl je Begegnung, dann der Wortlaut der
ausgewählten.

Der Anlass ist gemessen: Mit dem gleitenden Fenster beschrieb der Kern das
Themenband dieses Fensters und **keine wiedererkennbare Person** — Novas
sieben Kern-Profile ähnelten einander nicht stärker als die Profile sieben
verschiedener Menschen (`KERNHASH-TRAEGT-KEINE-PERSON`, 25.08.2026).

**Am produktiven Paar nach dem Umbau:** 98 von 223 Begegnungen, 75 783 von
80 000 Zeichen; das Material der Figur wuchs von 15 521 auf 68 652 Zeichen,
das des Menschen von 3 879 auf 9 873. Die Bindung des Kerns an den Wortschatz
der 40 neuesten Begegnungen fiel dabei über zwei Läufe von **28,4 % auf 15,8 %
bzw. 10,8 %** (Figur) und von **11,4 % auf 3,1 % bzw. 3,6 %** (Mensch). Ein
voller Destillationszyklus dauert seither **rund 375 s** statt 261 s, bei einem
Takt von 600 s.

**Was der Umbau nicht behebt:** Die gemeinsamen Inhaltswörter beider Kerne sind
nicht gefallen, sondern von 38 auf 43 bzw. 51 gestiegen. Der geteilte
Gesprächsstoff bleibt; erledigt ist nur die Bindung an dessen jüngsten
Ausschnitt.

## Wo Impulse ausgenommen werden — und wo nicht (17.08.2026)

Nicht überall. Der Trennstrich ist das **Gegenüber**: Eine Aussage über Umgang
setzt eines voraus, ein Impuls hat keines. Was jemanden beschäftigt und was er
fühlt, steht dagegen sehr wohl in seinen eigenen Gedanken.

| Profil | Frage | Impulse |
|---|---|---|
| Kern | wer ist er dauerhaft | **raus** |
| Beziehung | wie steht er zum Gegenüber | **raus** |
| Intentionen | wie geht er mit anderen um | **raus** |
| Adaptiv | was beschäftigt ihn gerade | **bleiben** |
| Emotionen | was fühlt er | **bleiben** |

Deshalb zwei KZG-Auswahlen je Perspektive: `_kzg_laden(...)` für den
Adaptiv-Hash und `_kzg_laden(..., nur_begegnungen=True)` für das
Beziehungsprofil. **Der Filter gehört in die Auswahl, nicht dahinter** —
gemessen am 17.08.2026 hatten *null* von Novas zwanzig stärksten KZG-Einträgen
einen erreichbaren Begegnungs-Wortlaut; nachgelagert gefiltert wäre ihr
Beziehungsprofil dauerhaft leer geblieben. Mit der eigenen Auswahl sind es 20.

`wortlaut_holen` und `_lzg_intentionen_laden` filtern über die Brücke
`verbindung` → `pipeline_log` mit `IS DISTINCT FROM 'eigener_impuls'` — ein
Knoten ohne Brücke bleibt erhalten, er ist nicht nachweislich ein Impuls
(19 % der Knoten der Figur).

## Auswahl der KZG-Einträge (seit 16.08.2026)

`_kzg_laden` liefert die `PIXIE_CHARAKTER_KZG_LIMIT` Einträge mit der höchsten
**effektiven Salienz** = `salienz × zeitgewicht(alter)`, nicht die ersten, die
`SCAN` ausgibt. Das Zeitgewicht ist `exp(-ln2/T · t)` mit
`PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE` (1,7 Tage).

- **Warum eine Ordnung nötig ist:** `SCAN` sagt keine zu. Gemessen am
  produktiven Paar lagen die vorher genommenen 20 auf den Zeiträngen 245 bis
  2162 von 2202, im Mittel 18 Tage alt — für ein Profil mit der Frage
  *„Was beschäftigt ihn gerade?"*. Nach dem Umbau: 2,1 Tage.
- **Warum es trotzdem billig bleibt:** Die Schlüssel tragen ihre Zeitmarke, die
  Sortierung kostet keinen Redis-Zugriff. Sinkt das Zeitgewicht unter die
  schwächste bereits gewählte effektive Salienz, kann kein älterer Eintrag mehr
  aufholen (`salienz ≤ 1`) — ab da wird nicht weitergelesen. Gemessen: 28
  gelesene statt 2202 durchsuchter Schlüssel.
- **Ohne Themenfeld kein Platz:** Solche Einträge verwirft die Destillation
  ohnehin. Unter den jüngsten `assistant`-Einträgen tragen nur 70 % eines.
- Verworfenes wird **gezählt** und steht in der Logzeile — beide Pfade waren
  vorher stille `continue`.

## Besonderheiten
- Iteriert über alle User (meister + nova)
- 1 LLM-Call pro Profil pro User (max 10 Calls bei beiden dirty)
- CPU-Modell (kein GPU-Contention)
- Kein eigener Subgraph — reines invoke()
