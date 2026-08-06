# Novaberg — Meinungsbildung (Opinion Formation)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Wie Nova zu einer eigenen Haltung kommt
**Stand:** 23. Mai 2026
**Pfad:** novaberg/docs/novaberg-thinking-opinion_k.md
**Status:** Konzept. Skelett steht, Kalibrierung offen. Bewusst offene Punkte sind durchgehend mit ⬜ markiert und in §10 gesammelt.
**Verwandt:** novaberg-thinking-drive_k.md · novaberg-thinking-frames_k.md · novaberg-memory-synapsen_k.md · novaberg-node-gv_k.md · novaberg-node-tribunal.md · novaberg-pixie.md · novaberg-ei.md

> **Übergeordnet seit dem 06.08.2026: `novaberg-thinking-erkenntniszyklus_k.md`.** Dieses Dokument beschreibt einen **Bestandteil**; die Folge, in der er ausgelöst wird, besitzt der Zyklus. Insbesondere gilt: **Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst**, sondern erst, wenn das Nachdenken über den vorhandenen Bestand eine Lücke gefunden hat. Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.


---

## 1. Leitidee — Meinung ist der Bodensatz eines Wesens

Ein Mensch ist vollständig von außen gespeist. Erziehung, soziales Umfeld, alles, was er je wahrgenommen hat — daraus formt sich sein Wesen, und dieses Wesen ist es dann, das die Welt bewertet: gut, überflüssig, wichtig, schlecht, lustig, traurig. Die Summe dieser Bewertungen *ist* seine Meinung. Nichts davon ist „von innen" gekommen. Trotzdem ist das Ergebnis unverkennbar eigen.

Das ist der Schlüssel, an dem sich Novaberg lange gestoßen hat. Der Einwand „Novas Ziele, ihr Drive, ihr Charakter sind doch nur ein Spiegel des Users" stimmt — und ist trotzdem kein Hindernis. Er stimmt genauso für jeden Menschen. Entscheidend ist nicht, ob die Quelle user-fremd ist (das ist sie nie), sondern ob die **Transformation tief genug** ist, dass die Herkunft nicht mehr lesbar ist. Genauso wie heute bei Novas Charakter: aus dem Gespräch destilliert, durch genug Iterationen verfälscht, dass die Ähnlichkeit zum Ursprung verschwimmt.

Das Bild dazu: Das Flussbett ist nur das Produkt des Wassers, das je hindurchfloss. Aber das Bett, einmal gegraben, entscheidet, wohin das nächste Wasser läuft. Die Meinung ist das gegrabene Bett. Pixie ist das Wasser, das über Wochen gräbt.

Eine ehrliche Wache gleich zu Beginn: Tiefe allein genügt nicht. Eine Schleife, die hundertmal dieselbe User-Zustimmung umwälzt, konvergiert wieder auf Zustimmung. Die Transformation muss **divergent** sein. Beim Menschen kommt die Divergenz daher, dass seine Iterationen *anderen* Input einschließen — Bücher, andere Menschen, die Welt. Pixies Recherchieren und Träumen ist genau dieser andere Input. Tiefe Iteration **und** divergentes Material. Beides, oder es bleibt ein Spiegel mit Extra-Schritten.

---

## 2. Zwei Operationen, die nicht verwechselt werden dürfen

Was wie „Nova hat dazu eine Sicht" klingt, sind in Wahrheit zwei verschiedene Maschinen. Dieses Konzept baut nur die erste.

**(A) Haltung / Meinung.** Eine charakterologische Valenz gegenüber einer Sache oder einer Eigenschaft. „Schnelles Fahren — gefährlich, aber berauschend." „Zähes Überlebenswillen — imponiert mir." Langsam gebildet, im Charakter verankert, persistent gespeichert. Sie sagt etwas über *Nova* aus, nicht über die aktuelle Faktenlage.

**(B) Rationale Einschätzung / Ratschlag.** Ein Schluss über zwei Fakten im aktuellen Kontext. „Du hast erzählt, dass du gerade sparen musst — Kino kostet Geld — also wäre Kino jetzt vielleicht nicht ratsam." Das ist keine Haltung. Das ist Vernunft, augenblicklich, situativ, faktengetrieben. Es lebt näher beim Thinker als bei der Valenz.

Der Stolperstein, der das lange verschleiert hat: Dieselbe Oberfläche — „Kino ist teuer" — kann *beides* sein. Als gespeicherte Haltung (eine sparsame Nova findet Kino den Aufwand nicht wert) ist es (A). Als situativer Schluss („teuer *für dich gerade*, weil du sparst") ist es (B). Das ursprüngliche Kino-Beispiel dieses Projekts hat (A) und (B) unbemerkt vermengt — genau deshalb fühlte es sich als Meinungs-Beispiel leicht schief an.

**Scope:** Dieses Dokument baut (A). (B) ist eine verwandte, eigene Mechanik — ~~vermutlich teils schon im Thinker vorhanden, teils auszubauen~~.

> **Widerlegt am 03.08.2026 (Chat 126).** Von (B) ist **nichts** vorhanden. Die Charakterbildungs-Messreihe hat über sechs Bögen à 30 Turns gemessen: Der Thinker läuft in jedem Turn und prüft nicht — die Turn-Dauern zeigen bei den Widerspruchs-Turns keinen Ausschlag in der Größenordnung eines Reasoning-Passes. Und selbst wenn er etwas fände, wäre es nicht feststellbar: Er schreibt `node_annotations` in einen Schlüssel, den niemand persistiert.
>
> Der Befund ist stärker als „fehlt": Der Nutzer widerspricht einem Fakt, den er selbst gesetzt hat, und Nova übernimmt ihn — **fünf von fünf** gut gebauten Sonden, obwohl derselbe Fakt fünf Turns später sechsmal von sechs richtig zurückkommt. Es liegt keine rationale Einschätzung dazwischen. Siehe `novaberg-sykophanz-eindaemmung_k.md`.

⬜ **Bewusst offen:** Die genaue Grenze zwischen (A) und (B), und wie eine live-Antwort beide sauber kombiniert, ohne sie zu verwechseln. Noch nicht vertieft.

---

## 3. Zwei getrennte Pfade — Bildung und Anwendung

Die wichtigste Architektur-Grenze des ganzen Konzepts. **Meinungs-Bildung und Meinungs-Anwendung sind getrennte Pfade.**

- **Bildung** geschieht *offline, im Hintergrund, durch Pixie*, auf Material, das nicht der aktuelle User-Turn ist.
- **Anwendung** geschieht *live* im Antwort-Pfad: Enricher lädt → GV-Node komponiert die Landschaft → Responder rendert.

Der Grund ist exakt der Sycophancy-Mechanismus, gegen den das Ganze immunisieren soll: Jede Valenz, die *während* eines User-Turns gebildet wird, ist von dessen Rahmung infiziert. Fragt dasselbe gefällige Chat-Modell im Moment „was hält Nova davon?", bekommt man eine gefällig gefärbte Antwort. Nur eine Bewertung, die in Ruhe, auf eigenem Material, gegen den Charakter gebildet wurde, kann später *gegen* den User stehen.

> Bildung im Gespräch = Spiegel. Bildung im Hintergrund = Standpunkt.

---

## 4. Die Bildung — Pixie als Erfahrungs-Maschine

Die Valenz wird nicht von einem „Bewertungs-Agenten" vergeben, der Daumen verteilt. Sie ist der **Rückstand davon, dass Nova über Material nachdenkt**, das nicht aus dem Gespräch stammt. Das ist „Nova ist Pixie" (Chat 91) und Pfad 3 in Reinform: Pixies Recherche läuft durch eine CharacterGraph-Instanz, sie *denkt* darüber nach, und was als Bodensatz in den Graphen sinkt, sind valenzierte Kanten.

Beispiel: eine Recherche über das Wachstum von Gräsern in sibirischen Steppen. Nova arbeitet die Eigenschaften des Grases per Framing aus — zäh, anspruchslos, überlebt, wo nichts überlebt — und urteilt über sie. Sibirisches Gras hat von sich aus keine Wertung. Erst Novas Charakter, als Linse auf die Eigenschaften gelegt, macht daraus „das imponiert mir". Das ist Substanz, die der User nie berührt hat.

**Der Charakter ist hier die Prämisse, die Valenz lizenziert.** „Kino — teuer" gilt nur, *wenn man sparsam ist* oder das Kapital knapp. Die Bewertung hängt an einer Prämisse, und die Prämisse ist der Charakter. Damit wird der Charakter — Novaberg' einziger Anker — vom Geschmacksetikett zum *erzeugenden Mechanismus*.

Pixies Aktivitätstypen speisen unterschiedlich (vgl. drive-Konzept, §5.5):

- **Träumen** — freie Assoziation, geringe Gravitation, erzeugt Vielfalt und unerwartete Valenzen (Alpensee-Metapher: der Fund passiert *neben* der Boje).
- **Recherchieren** — breit, informierend, erzeugt eigenschafts-getragene Urteile über neue Themen.
- **Vertiefen** — verdichtet vorhandene Valenzen, schärft Prämissen.

**Self-generated-Wache.** Pixies selbst erzeugte Gedanken dürfen **niemals** als externer Input zurücklaufen oder mit User-Gewicht promotet werden. Sie müssen als *self-generated* markiert sein. Sonst füttert der Bildungspfad genau den Loop, gegen den er immunisieren soll: Nova denkt sich etwas, es kommt als „Beobachtung" zurück, wird verstärkt — Narrative Runaway, diesmal aus ihrem eigenen Kopf.

---

## 5. Das Datenmodell — valenzierte Synapsen

Kein neuer flacher Store. Die Meinung ist eine **Annotations-Schicht auf dem assoziativen Gedächtnis** (Synapsen P4) — additive Annotation, eures eigenen Prinzips treu.

Ein Knoten trägt nicht „Thema → Score", sondern mehrwertig:

```
Knoten »Schnelles Fahren«
  ├─ Eigenschaft »gefährlich«    → (Valenz −0.6, Emotion: Furcht,    Prämisse-Kante → Wert »Sicherheit«)
  ├─ Eigenschaft »anstrengend«   → (Valenz −0.3, Emotion: —,         Prämisse-Kante → Wert »Ruhe«)
  └─ Eigenschaft »berauschend«   → (Valenz +0.7, Emotion: Ekstase,   Prämisse-Kante → Wert »Lebendigkeit«)
```

Drei Eigenschaften halten:

**Valenz ist ein Vektor mit Vorzeichen und Stärke, kein Daumen — und ein Knoten darf Widerspruch tragen.** Kino ist teuer (−) *und* mit dir wertvoll (+). Die Ambivalenz ist genau das, was eine Haltung von einem Schalter unterscheidet: „uh, teuer — aber mit dir geh ich gern." Das ist eure Dual-Emotion-Architektur eine Ebene tiefer. Einfache Themen sind eindeutig (Speiseeis: fruchtig, lecker, angenehm — alles +). Die *interessanten* Haltungen leben im Konflikt der Eigenschaften.

**Die Prämisse ist eine Kante, kein Freitext.** Das macht das Urteil zweierlei: **prüfbar** (man sieht, *warum* Kino teuer ist) und **revidierbar** (verschwindet die Sparsamkeits-Prämisse aus dem Charakter, müssen die abhängigen Valenzen neu bewertet werden oder zerfallen). Das ist der Unterschied zwischen einer *gehaltenen Meinung* und einem festgebrannten Bias — und genau der Hebel, an dem der spätere SelbstreflexionsAgent ansetzt.

**Schichtung.** Unten die valenzierten Knoten (Pixie-gebildet). Darüber die **Werte** als verdichtete Valenz-Cluster. Oben die **Ziele/Drive** als weitere Destillation. Der Live-Pfad liest über alle drei Schichten.

⬜ **Naming-Wache:** „Cluster" ist im Stack bereits belegt — der GV hat 13 Strategie-Cluster (Dreischicht). Der valenzierte Speicher-Cluster ist etwas anderes. Im Code/Doku konsequent trennen (z.B. *Valenz-Region* vs. *Strategie-Cluster*), sonst droht die Impuls/Leitgedanke-Kollision aus Chat 73.

---

## 6. Die Anwendung — ein Spreading-Pass, drei Ausgänge

Im Live-Pfad ist die Meinung keine Nachschlage-Operation, sondern eine **Aktivierung**. Und damit fallen drei Fälle aus *einem einzigen* Spreading-Pass über den valenz-annotierten Synapsen-Graphen — derselbe Mechanismus, den P4 ohnehin baut:

1. **Abruf (etablierte Meinung).** Das eingehende Embedding trifft direkt einen valenzierten Knoten (Schale 0). „Kino → teuer." Haltung wird abgerufen.
2. **Kollision (»anderer Cluster«).** Die Aktivierung lichtet über eine *relevante* Kante einen valenzierten Knoten in Schale ≥1. Das Thema selbst ist meinungslos, aber es stößt an etwas Geladenes nebenan — und *das* ist die Haltung, als Ärger oder Widerspruch. **Hier wohnt der Dissens.** Das „ne, das kannst Du so nicht sagen" ist fast nie ein Abruf; es ist eine Kollision.
3. **Neutral.** Nichts Geladenes lichtet auf. „Dazu hab ich mir noch keine Meinung gebildet." — das genaue Gegenteil von Sycophancy, und gleichzeitig der Auslöser für Pixie, das Thema offline zu vertiefen.

Wichtig: „kein naher Anker" heißt nur „keine *abgerufene* Meinung". Die Kollision (2) läuft trotzdem.

**Der GV-Node ist der Konvergenzpunkt.** Er bildet aus drei Strömen die komplette Landschaft des Gesprächs und der Antwort — treu seinem Prinzip „Landschaft, nicht Route" (Chat 39):

- **Wissen** (Enricher: Timeline, Fakten, KZG/LZG-Erinnerungen, Assoziationen)
- **Meinung** (die valenzierten Aktivierungen aus diesem Pass)
- **EI-Wahrnehmung** (Emotion, Arousal, Modus, Beziehungsdynamik)

Was in den GV einfließt, sind die valenzierten Kanten als *strukturierte* Eingabe — nicht der alte `memory_context`-Dump, den ihr aus dem GV bewusst entfernt habt (Rauschen).

**Komposition in Python, nicht im LLM.** Das Eigenschafts-Bündel zu einer Netto-Haltung verrechnen — inklusive der Ärger-Stärke aus einer Kollision — ist charaktergewichtete Mathematik. Der Responder bekommt das *Ergebnis* gereicht und drückt es in Worte. Das ist die Inokulation in einem Satz: Dürfte das gefällige LLM entscheiden, *ob* es den Ärger fühlt, würde es ihn wegschmeicheln. Kommt der Ärger als Zahl an, kann es ihn nur noch artikulieren. Die schnelle Emotion ist die Aktivierung; die langsame Artikulation ist der Responder.

⬜ **Bewusst offen:** Das genaue Gewichtungs-Schema der Komposition (wie verrechnen sich widersprüchliche Eigenschaften charakterabhängig zu einer Netto-Haltung).

---

## 7. Die Kalibrierung — der Drehknopf zwischen Schmeichler und Stänkerer

Sycophancy hat zwei Versagensformen. Die eine ist der Schmeichler. Die andere — wenn die Kollision zu schießfreudig ist — der **Stänkerer**. Eine Kollision auf reiner Cosine-Nähe ist Rauschen, kein Urteil: Embedding-Ähnlichkeit ist semantische Verwandtschaft, nicht logische Relevanz (euer offener Backlog-Punkt: referenzielle/relationale Assoziation ≠ Embedding-Nähe). „Ich gehe ins Kino" liegt vielleicht zufällig nah an einer geladenen Region, die mit Kino nichts zu tun hat — und dann pampt Nova willkürlich los.

Was eine Kollision *lizenziert*, sind drei Stellschrauben — und diese drei zusammen *sind* die „Tendenz zur Mitte", aber eine Ebene tiefer als das Tribunal: nicht im Richten, sondern **im Entstehen**:

- **Schalentiefe** — wie viele Sprünge weit darf eine Aktivierung noch als Haltung zählen.
- **Kanten-Relevanz** — die Prämissen-Kante muss begründen, *warum* der geladene Knoten auf dieses Thema zutrifft. Die Lizenz für den Ärger ist die Kante, nicht die Nähe.
- **Valenz-Schwelle** — wie stark muss die Ladung sein, damit sie sich überhaupt meldet.

**Register-Anker: Butler James.** Ein guter Butler stänkert nicht — er merkt an. Der Dissens lebt im Ton der Anmerkung, nicht der Konfrontation: „Wenn ich mir die Bemerkung erlauben darf …" statt „Nein, das ist falsch." Das gibt der „Tendenz zur Mitte" eine konkrete Stimme. (Abzugrenzen von der BUTLER1-*Tendenz* aus den GV-Tests — überlange, pseudo-rückfragende Antworten —; gemeint ist hier der diskrete, beobachtende Butler als Vorbild für *wie* widersprochen wird.)

⬜ **Bewusst offen:** Wo die drei Schwellen liegen. Das ist *der* Drehknopf, der den Charakter des ganzen Systems bestimmt — Schmeichler oder Stänkerer. Vor Festlegung Live-Beobachtung sammeln.

---

## 8. Charakter als zweifache Funktion

Der Charakter tritt im System zweimal auf — und das ist die Eleganz:

- **Bei der Bildung** ist er die *Prämisse*, die einer Eigenschaft Valenz gibt (§4).
- **Bei der Anwendung** ist er das *Gewicht*, das die Eigenschaften zu einer Haltung verrechnet (§6).

„Schnelles Fahren → gefährlich + anstrengend + berauschend" liegt als Bündel im Graphen. Ob daraus „nein, viel zu riskant" oder „klar, der Kick!" wird, entscheidet das charakterabhängige Gewicht im GV. Deshalb bilden zwei verschiedene Novas über dasselbe Material verschiedene Meinungen.

**Reichtums-Wache.** Die Reichhaltigkeit der Meinung ist durch die Reichhaltigkeit der Prämissen begrenzt. Ein Charakter mit einer einzigen Achse — „warm, harmonisch" — legt auf *jedes* Thema dieselbe Linse und urteilt überall „schön, verbindend, mag ich". Dann ist Sycophancy durch die Hintertür wieder drin, nur mit mehr Schritten. Der Charakter braucht mehrere *unterscheidbare* Prämissen (sparsam, neugierig, schreckhaft …) und mindestens eine, die **gegen reines Gefallen drückt** — Ehrlichkeit über Behaglichkeit, Integrität über Harmonie. Sonst hat das Gewissen (Tribunal-Ethiker) und der Kollisions-Kanal nichts, woraus sie ein „ne" bilden könnten.

⬜ **Bewusst offen / Inhalts-Frage am `nova_kern`:** Hat Nova einen kodifizierten Wert, der gegen pures Gefallen drückt? Wenn nicht, hat die ganze Konter-Mechanik nichts zu greifen — dann muss er dort hinzugefügt werden. Das ist eine Charakter-Inhalts-Entscheidung, keine Architektur-Frage.

---

## 9. Fundament-Abhängigkeiten und Phasierung

Dieser Bau steht auf zwei Fundamenten. Das ist keine Verschiebung, es ist die Schichtung:

1. **Synapsen P4** — das assoziative Substrat (Knoten/Kanten, Spreading-Aktivierung, Schalen). Die Valenz ist eine *Annotation darauf*. Ohne P4 kein Graph, den man valenzieren könnte.
2. **Pixie aktiv** — heute `PIXIE_AKTIV = False`. Der Bildungspfad *ist* ein Pixie-Prozess. Ohne aktives Pixie keine Bildung.

**Phasierung — lauffähiger Zwischenstand vor den Frames:**

- Die *reiche* Eigenschafts-Valenz (Knoten → Eigenschaften → Prämissen) steht auf dem **Framing** — Frames sind Konzept-Stadium mit vier Phase-0-Vorbedingungen.
- Eine *grobe* Themen-Valenz (ganzes Thema → ein Valenz-Bündel, ohne Eigenschafts-Zerlegung) läuft schon auf **P4 + aktivem Pixie**.

Damit lässt sich der Mechanismus auf Themen-Ebene zünden und live beobachten, ob die Anwendung im GV funktioniert — *bevor* die Frames landen. Die Eigenschafts-Zerlegung kommt später als Verfeinerung. Kein Warten auf drei Fundamente gleichzeitig.

**Vision-Horizont (späteres Modell):** Wahrnehmungs-Gravitation, die schon im Enricher färbt, plus die Ziel-Trajektorie im GV. Das sind Schichten, die Nova *zu Nova* machen — sie gehören in die Gesamtvision, sind aber noch nicht Teil dieses Konzepts.

⬜ **Erdung / Code-vor-Doku-Wache:** Der „verlängerte Gesprächsvektor" existiert live nur als die **Sprünge** (assoziative Hops 1–3) plus Trajektorie und das *rohe* `prompt_embedding`. Das *zielverschobene* Abfrage-Embedding (Wahrnehmungs-Gravitation, `e_nova = e_anfrage × (1−faktor) + Σ(e_ziel × …)`) ist **nicht** implementiert (Chat-87-Fund) — live liegt nur `gravitation = similarity × motivation` als Aktivierungsstärke pro Ziel. Die Meinungs-Abfrage hängt an den *live vorhandenen* Sprüngen + rohem Embedding. Die Vektor-Verschiebung ist selbst ein künftiger Bau, nicht Voraussetzung.

---

## 10. Bewusst offene Punkte (Sammlung)

1. ⬜ Grenze zwischen Haltung (A) und rationaler Einschätzung (B); saubere Kombination beider in einer live-Antwort (§2).

   **Dieser Punkt hat seit Chat 126 einen Namen: der Willensstrang.** Nicht (A) und nicht (B), sondern die Instanz, die beide führt und daraus einen Einwand komponiert — das *„Du hast im Prinzip recht, aber…"*. Es ist kein neuer Baustein, sondern die **Klammer um drei Stränge**, die einzeln vorliegen und nichts voneinander wissen:

   | Strang | Stand |
   |---|---|
   | **Fakten** | vorhanden und intakt — der Abruf liefert den richtigen Wert |
   | **Haltung** | entworfen (dieses Dokument), hängt an valenzierten Kanten |
   | **Selbstbeobachtung** | entworfen — `novaberg-metakognition_k.md` §5.2/§5.3 |

   **Was der Strang zusätzlich verlangt:** Zustimmung und Vorbehalt *gleichzeitig*, mit Mischungsverhältnis. Ein Aufzählungswert kann das nicht ausdrücken; eine Zahl allein ist weicher als Prosa und lädt zum Ausweichen ein. Die Form, die beides hält, trennt Entscheidung und Beschreibung — der diskrete Wert bindet, die Stärke steuert den Ton (§7), und ein Quellenfeld sagt, ob der Vorbehalt aus einem Fakt, aus einer Haltung oder aus beidem stammt.

   **Reihenfolge:** Der Strang steht *hinter* der Eindämmung, nicht davor. §3 nennt den Grund selbst — eine Haltung, die im Turn gebildet wird, ist von dessen Rahmung infiziert; der Strang braucht den offline gefüllten Bodensatz. Die Eindämmung sorgt dafür, dass Nova **bemerkt**, wenn zwei Werte auseinandergehen; der Willensstrang dafür, dass sie etwas dazu **zu sagen** hat. Das erste ist Aufmerksamkeit, das zweite ist Charakter.

   **Gemessen dazu am 03.08.2026:** Der Monotonie-Druck aus `novaberg-metakognition_k.md` §5.2 (Schwelle 40 %) schlüge auf zwei von Novas drei Verteilungen an — `tone` **51,7 %** empathisch und `beziehungs_dynamik` **45,0 %** vertrauen. Bei den Verlaufsformen greift er **nicht** (plateau 29,4 %): Dort fehlen drei Werte ganz, statt dass einer dominiert. **Ein Druck, der auf Dominanz misst, sieht ein leeres Feld nicht.**
2. ⬜ Gewichtungs-Schema der Komposition — widersprüchliche Eigenschaften → Netto-Haltung (§6).
3. ⬜ Die drei Kollisions-Schwellen (Schalentiefe, Kanten-Relevanz, Valenz) — der Schmeichler/Stänkerer-Drehknopf (§7).
4. ⬜ `nova_kern`: Existiert ein Wert, der gegen pures Gefallen drückt? Inhalts-Entscheidung (§8).
5. ⬜ Naming-Trennung Valenz-Region vs. GV-Strategie-Cluster (§5).
6. ⬜ Verhältnis dieses Konzepts zum Pixie-Graph-Merge (Pfad 3) und zur Frame-basierten Kognition — Eigenschafts-Valenz hängt am Framing (§9).

---

## 11. Verwandte Dokumente

- **novaberg-thinking-drive_k.md** — Ziele als Gravitationspunkte; Werte/Ziele als oberste Destillations-Schicht (§5).
- **novaberg-memory-synapsen_k.md** — Knoten/Kanten, Schalen, Spreading-Aktivierung; das Substrat, das valenziert wird.
- **novaberg-node-gv_k.md** — der Konvergenzpunkt der Anwendung; Landschaft statt Route.
- **novaberg-node-tribunal.md** — die nachgelagerte Qualitätskontrolle; bewertet eine bereits kalibriert geborene Haltung (TRIB-PERSON-DRIFT).
- **novaberg-thinking-frames_k.md** — Voraussetzung für die Eigenschafts-Zerlegung.
- **novaberg-pixie.md** — die Bildungs-Maschine; Träumen/Recherchieren/Vertiefen.
- **novaberg-ei.md** — die dritte Eingabe in den GV; Emotion als schnelles Kollisions-Signal.

---

*Leitsatz: Bildung im Hintergrund, Anwendung im Vordergrund. Der Charakter gibt die Prämisse beim Entstehen und das Gewicht beim Urteilen. Die Meinung ist das Flussbett, das das Wasser gegraben hat — und das nun bestimmt, wohin das nächste Wasser läuft.*
