"""
GV4: Wissensluecken — semantisch nahe, aber unbesprochene Konzepte.

Durchsucht LZG (PostgreSQL/pgvector) und KZG (Redis/RediSearch).
Berechnet Relevanz aus 6 Systemen: Gedaechtnis, Aktualitaet, Drive,
Neugier, Register, Charakter.
Konzept: Chat 71 — validiert über 58-Testfälle-Matrix.
"""

import logging

import numpy as np
import psycopg2

from config import (
    GV_CHARAKTER_RESONANZ_SCHWELLE,
    GV_LUECKEN_MAX,
    GV_LUECKEN_MIN_RELEVANZ,
    GV_LUECKEN_SIM_OBERGRENZE,
    GV_NEUGIER_BOOST_SCHWELLE,
    GV_QUELLEN_FAKTOR,
    POSTGRES_URL,
    redis_client,
    redis_client_bytes,
)
from ei.neugier import register_kompatibilitaet
from ei.utils import cosine_similarity
from graph.state import ConversationState, pipeline_quelle
from memory.pipeline_log import log_berechnung
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.ei.wissensluecken")


def ist_bereits_erwaehnt(inhalt: str, session_turns: list[dict]) -> bool:
    """Prueft ob der Inhalt einer Luecke bereits in der Session erwaehnt wurde.

    Einfacher Token-Overlap: Wenn mehr als 40% der Woerter des Inhalts
    in den letzten 8 Session-Turns vorkommen, gilt es als bereits besprochen.
    """
    if not session_turns:
        return False

    inhalt_woerter: set[str] = {
        w.lower() for w in inhalt.split() if len(w) > 3
    }
    if not inhalt_woerter:
        return False

    session_text: str = " ".join(
        turn.get("inhalt", "") for turn in session_turns[-8:]
    ).lower()

    treffer: int = sum(1 for w in inhalt_woerter if w in session_text)
    overlap: float = treffer / len(inhalt_woerter)
    return overlap > 0.4


def lzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
    kern_embedding: list[float] | None = None,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im LZG via pgvector.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht, gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        embedding_str: str = "[" + ",".join(str(v) for v in turn_embedding) + "]"

        # **Die Kern-Naehe kommt aus derselben Abfrage** (12.09.2026). Der
        # Charakter-Filter verglich bis heute den **Turn** mit dem Kern und
        # setzte denselben Wert fuer alle zwanzig Kandidaten — ein globaler
        # Schalter unter dem Namen eines Kandidatenfilters. Je Kandidat ein
        # eigener Wert kostet hier **keinen** weiteren Aufruf: Der Vektor liegt
        # in der Zeile, und ein zweiter Abstandsausdruck rechnet ihn mit.
        #
        # Ohne Kern-Embedding (Cold-Start) bleibt die Spalte NULL, und der
        # Aufrufer sieht es am fehlenden Feld — kein Vorgabewert, derselbe Grund
        # wie bei `resonanz_pruefbar` (Chat 107, GV-RESONANZ-FALLBACK-LUEGT).
        kern_str: str | None = (
            "[" + ",".join(str(v) for v in kern_embedding) + "]"
            if kern_embedding else None
        )

        cursor.execute(
            """
            SELECT inhalt,
                   1 - (embedding <=> %s::vector) AS similarity,
                   gewicht_decay,
                   COALESCE(arousal, 0.3) AS gap_arousal,
                   CASE WHEN %s::vector IS NULL THEN NULL
                        ELSE 1 - (embedding <=> %s::vector) END AS kern_naehe
            FROM lzg_knoten
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
            ORDER BY embedding <=> %s::vector
            LIMIT 10
            """,
            (embedding_str, kern_str, kern_str,
             user_id, character_id, embedding_str),
        )

        for row in cursor.fetchall():
            inhalt, similarity, gewicht, gap_arousal, kern_naehe = row
            # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.1 —
            # liess im alten Raum 93 % durch, filterte nichts. 0.20 liegt
            # knapp ueber dem neuen Grundrauschen (0.16).
            if similarity and similarity > 0.20:
                eintrag: dict = {
                    "konzept":    inhalt,
                    "similarity": float(similarity),
                    "gewicht":    float(gewicht) if gewicht else 0.5,
                    "gap_arousal": float(gap_arousal),
                    "quelle":     "lzg",
                }
                if kern_naehe is not None:
                    eintrag["charakter_resonanz"] = float(kern_naehe)
                kandidaten.append(eintrag)

        conn.close()
        logger.info(f"GV4-LZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-LZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def kzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
    kern_embedding: list[float] | None = None,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im KZG via RediSearch KNN.

    **Nutzt `redis_client_bytes`, nicht `redis_client`** — seit dem 12.09.2026
    holt die Abfrage das `embedding` mit, und ein float32-Blob ueberlebt
    `decode_responses=True` nicht: redis-py liest die ganze Antwort als UTF-8,
    und die Suche bricht mit `'utf-8' codec can't decode byte 0xd0` ab. Der
    Abbruch wird gefangen und als Warnung protokolliert — also **null
    Kandidaten, die aussehen wie ein leerer Speicher**. Deshalb dekodiert dieser
    Pfad selbst, Feld fuer Feld, und laesst `embedding` als Bytes stehen.

    Der frueher hier stehende Satz — *„da wir nur Text-/Numeric-Felder
    zurueckliefern (kein Embedding-Blob), spielt decode_responses=True hier
    keine Rolle"* — nannte die Bedingung, unter der er galt. Sie gilt nicht mehr.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht (=salienz), gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        query_blob: bytes = np.array(turn_embedding, dtype=np.float32).tobytes()

        ergebnis = redis_client_bytes.execute_command(
            "FT.SEARCH", "idx:kzg",
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN 10 @embedding $vec AS score]",
            "PARAMS", "2", "vec", query_blob,
            "SORTBY", "score",
            "LIMIT", "0", "10",
            # `embedding` kommt mit, damit die Kern-Naehe je Kandidat
            # gerechnet werden kann — der Vektor liegt gespeichert, ein
            # zweiter Modellaufruf waere Verschwendung.
            "RETURN", "5", "inhalt", "salienz", "arousal", "score", "embedding",
            "DIALECT", "2",
        )

        if ergebnis and isinstance(ergebnis, list) and len(ergebnis) > 1:
            idx: int = 1
            while idx < len(ergebnis) - 1:
                _key = ergebnis[idx]
                felder = ergebnis[idx + 1]
                idx += 2

                feld_dict: dict = {}
                for i in range(0, len(felder), 2):
                    k = felder[i].decode("utf-8") if isinstance(felder[i], bytes) else felder[i]
                    # **`embedding` bleibt rohes Byte-Feld.** Es ist ein
                    # float32-Blob und kein Text; ein `decode("utf-8")` darauf
                    # wirft oder liefert Muell.
                    if k == "embedding":
                        feld_dict[k] = felder[i + 1]
                        continue
                    v = (
                        felder[i + 1].decode("utf-8")
                        if isinstance(felder[i + 1], bytes)
                        else felder[i + 1]
                    )
                    feld_dict[k] = v

                inhalt:  str   = feld_dict.get("inhalt", "")
                salienz: float = float(feld_dict.get("salienz", "0.5"))
                arousal: float = float(feld_dict.get("arousal", "0.3"))
                score:   float = float(feld_dict.get("score", "1.0"))
                similarity: float = 1.0 - score

                # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher
                # 0.1 — filterte nichts. 0.20 knapp ueber Grundrauschen 0.16.
                if inhalt and similarity > 0.20:
                    eintrag: dict = {
                        "konzept":     inhalt,
                        "similarity":  similarity,
                        "gewicht":     salienz,
                        "gap_arousal": arousal,
                        "quelle":      "kzg",
                    }
                    roh = feld_dict.get("embedding")
                    if kern_embedding and isinstance(roh, bytes):
                        eintrag["charakter_resonanz"] = cosine_similarity(
                            np.frombuffer(roh, dtype=np.float32).tolist(),
                            kern_embedding,
                        )
                    kandidaten.append(eintrag)

        logger.info(f"GV4-KZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-KZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def _resonanz_pruefbar(kandidaten: list[dict], kern_embedding: list[float] | None) -> bool:
    """Sagt, ob die Resonanz-Schwelle fuer DIESEN Stapel angewandt werden darf.

    Zwei Bedingungen, und die zweite ist neu am 12.09.2026: Es braucht einen
    Charakterkern **und** den Wert an **jedem** Kandidaten. Fehlt er bei einem,
    faellt die Schwelle fuer den ganzen Turn aus — nicht fuer diesen einen.

    **Der Grund ist die Unterscheidbarkeit.** Ein Kandidat ohne Wert waere sonst
    entweder stillschweigend durchgelassen (dann entscheidet die Schwelle je
    Kandidat etwas anderes) oder verworfen (dann kostet ein Defekt der Suche
    eine Luecke, die es gab). Beides ist schlimmer als der Ausfall, und keins
    von beiden waere im Log zu sehen.

    **Eigene Funktion, weil eine Regel inline nur behauptet ist**
    (`20_TESTS/entscheidung-inline-ist-nicht-bezeugbar.md`): Sie stand zuerst
    als `bool(...) and all(...)` im Ablauf und war von aussen nur ueber
    Datenbank und Redis erreichbar.

    Vorbedingung: keine; `kandidaten` darf leer sein.
    Nachbedingung: True genau dann, wenn ein Kern vorliegt und jeder Kandidat
        `charakter_resonanz` traegt. Der Leerfall ist True — es gibt nichts,
        was ungeprueft durchkaeme.
    Fehlerfaelle: keine.
    """
    if not kern_embedding:
        return False
    return all("charakter_resonanz" in k for k in kandidaten)


def _qualifizieren(kandidaten: list[dict], resonanz_pruefbar: bool) -> list[dict]:
    """Behaelt, was beide Schwellen nimmt — und sagt, woran der Rest fiel.

    **Die Zeile ist der Grund, warum diese Funktion eine ist.** Bis zum
    12.09.2026 stand die Auswahl als Listen-Komprehension ohne Ausgabe: Zwanzig
    Kandidaten gingen hinein, null kamen heraus, und aus dem Log war nicht zu
    sehen, an welcher der beiden Bedingungen — nur aus einer Nachrechnung
    gegen den Bestand (`22_STILLE_FEHLER`). Die naechste Kalibrierung haette
    dasselbe Problem gehabt.

    **Beide Schwellen sind seit dem 12.09.2026 kandidateneigen.** Bis dahin
    setzte der Aufrufer fuer jeden Kandidaten denselben Wert —
    `cosine(turn, kern)`, die Naehe des **Turns** zum Charakterkern —, und die
    Schwelle wirkte als globaler Schalter: alle oder keiner. Gemessen ueber
    sieben Paare liess sie bei **zwei** von ihnen keinen einzigen Turn durch,
    also nicht selten, sondern nie.

    **Jetzt vergleicht sie den Kandidaten mit dem Kern**, und das kostet keinen
    weiteren Modellaufruf: Der Vektor jedes Kandidaten liegt gespeichert — im
    LZG als Spalte, im KZG als Feld —, und beide Suchen rechnen die Naehe mit.
    `[vorher gerechnet ueber 4232 aktive Knoten]` Auf dieser Groesse trennt die
    Schwelle bei **jedem** Paar: Mediane 0,405 bis 0,548 gegen 0,097 bis 0,282
    beim Turn, und bei 0,30 passieren 70 bis 92 % statt 0 bis 27 %.

    **Der Grenzwert ist deshalb vorerst unveraendert, und das ist Absicht.**
    0,30 laesst auf dieser Groesse viel durch; der Arbeitspunkt liegt nach der
    Vorausrechnung im Band 0,45 bis 0,50. Die Vorausrechnung lief aber ueber
    **alle** aktiven Knoten und nicht ueber die zwanzig, die ein Turn wirklich
    hochholt — die sind nach Turn-Naehe vorausgewaehlt. Eine Schwelle an einem
    Stellvertreter zu setzen ist genau der Fehler, den
    `21_MESSUNG/stellvertreter-eicht-nicht.md` beschreibt. Die Spur unten
    erhebt die echte Verteilung; danach wird gesetzt.

    Vorbedingung: jeder Kandidat traegt `relevanz`; bei `resonanz_pruefbar`
        zusaetzlich `charakter_resonanz`.
    Nachbedingung: die qualifizierten Kandidaten, Reihenfolge unveraendert.
        Die Log-Zeile nennt beide Ausfallgruende mit Zahl — auch bei null.
    Fehlerfaelle: keine.
    """
    # ── Verarbeitung ────────────────────────────
    zu_schwach: int = 0
    zu_fern:    int = 0
    behalten:   list[dict] = []

    for k in kandidaten:
        if k["relevanz"] < GV_LUECKEN_MIN_RELEVANZ:
            zu_schwach += 1
            continue
        if resonanz_pruefbar and k["charakter_resonanz"] < GV_CHARAKTER_RESONANZ_SCHWELLE:
            zu_fern += 1
            continue
        behalten.append(k)

    # ── Ausgabe-Verifikation ────────────────────
    # **Auch null wird gemeldet.** Ein Durchgang ohne Treffer und einer, der
    # nicht lief, sehen sonst gleich aus — und genau so blieb der Ausfall
    # dieses Filters wochenlang unsichtbar.
    logger.info(
        "GV4: %d von %d qualifiziert (Relevanz unter %.2f: %d · "
        "Kern-Resonanz unter %.2f: %d%s)",
        len(behalten), len(kandidaten), GV_LUECKEN_MIN_RELEVANZ, zu_schwach,
        GV_CHARAKTER_RESONANZ_SCHWELLE, zu_fern,
        "" if resonanz_pruefbar else ", Resonanz nicht pruefbar",
    )
    return behalten


def wissensluecken_finden(
    state:             ConversationState,
    aufnahmebereitschaft: float,
) -> list[dict]:
    """Findet semantisch nahe, aber unbesprochene Konzepte.

    Durchsucht LZG (pgvector) und KZG (RediSearch), filtert bereits
    Erwaentes und zu Aehnliches heraus, berechnet Relevanz aus
    6 Systemen und gibt die Top-N Luecken zurueck.

    Systeme:
      1. Gedaechtnis     — similarity × gewicht (aus DB)
      2. Aktualitaet     — nur Session-Turns (hier: alle DB = 1.0)
      3. Drive           — Ziel-Gravitation (neugier_boost)
      4. Neugier         — aufnahmebereitschaft (6 Saeulen, sin^0.5)
      5. Register        — register_kompatibilitaet (sachlich/offen)
      6. Charakter       — kern_hash Cosine >= Schwelle

    Returns:
        Top GV_LUECKEN_MAX Luecken sortiert nach Relevanz,
        oder leere Liste wenn nichts gefunden.
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "nova")
    user_prompt:  str = state.get("user_prompt", "")
    internal = state.get("internal")
    modus:        str = internal.emotion.mode                 if internal else "alltag"
    dynamik:      str = internal.emotion.relationship_dynamic if internal else "neutral"

    if not user_prompt or not user_id:
        # **Der stumme Rueckkehrpfad war der Ausfall selbst** (12.09.2026).
        # Bis heute kehrte GV4 hier ohne ein Wort zurueck; im Log war das von
        # *„lief und fand nichts"* nicht zu unterscheiden, und die Tor-Zeile
        # meldete beide Faelle als `wissensluecken: 0`. `[gemessen]` 40 Turns
        # mit offenem Tor, 0 Luecken, und **keine einzige** GV4-Zeile im Log
        # (`22_STILLE_FEHLER` §5).
        logger.info(
            "GV4: uebersprungen — user_prompt %s, user_id %s",
            "leer" if not user_prompt else f"{len(user_prompt)} Zeichen",
            "leer" if not user_id else f"'{user_id}'",
        )
        return []

    # ── 1. Turn-Embedding ──
    # Bevorzugt das vom Enricher bereits berechnete Embedding (spart ~1.6s).
    turn_embedding: list[float] = state.get("prompt_embedding") or []
    if not turn_embedding:
        try:
            request = EmbedRequest(text=user_prompt)
            embed_response = model_service.embed.submit_sync(request)
            turn_embedding = embed_response.embedding
            logger.debug(
                "Wissensluecken: GV4-Fallback Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(turn_embedding),
                embed_response.duration_seconds,
            )
        except Exception as fehler:
            logger.warning(f"GV4: Embedding fehlgeschlagen: {fehler}")
            return []

    # ── 1b. Kern-Embedding, VOR den Suchen ──
    # **Die Reihenfolge ist der Bauteil.** Bis zum 12.09.2026 entstand der Kern
    # erst in Schritt 5, nach der Suche — und konnte deshalb nur mit dem Turn
    # verglichen werden, nicht mit den Kandidaten. Er gehoert vor die Suche,
    # weil beide ihn brauchen; ein Aufruf bleibt ein Aufruf.
    kern_embedding: list[float] | None = None
    nova_kern: str = internal.character.core if internal else ""
    if nova_kern:
        try:
            kern_embedding = model_service.embed.submit_sync(
                EmbedRequest(text=nova_kern)
            ).embedding
        except Exception as fehler:
            # Zweig 2 — Infrastrukturdefekt (Kern vorhanden, Embedding
            # scheitert): laut krachen statt still einen Wert erfinden.
            logger.error(
                "GV4: Kern-Embedding fehlgeschlagen (user=%s) — Resonanz-Pruefung "
                "entfaellt: %s", user_id, fehler, exc_info=True,
            )
    else:
        # Zweig 1 — legitimer Cold-Start: frisches Paar, noch keine
        # Charakter-Destillation. Einmal pro Aufruf, nicht pro Kandidat.
        logger.warning(
            "GV4: kein Charakter-Kern (Cold-Start) fuer user=%s — "
            "Resonanz-Pruefung entfaellt", user_id,
        )

    # ── 2. Kandidaten aus LZG + KZG ──
    lzg_kandidaten: list[dict] = lzg_kandidaten_suchen(
        turn_embedding, user_id, character_id, kern_embedding=kern_embedding
    )
    kzg_kandidaten: list[dict] = kzg_kandidaten_suchen(
        turn_embedding, user_id, character_id, kern_embedding=kern_embedding
    )
    alle_kandidaten: list[dict] = lzg_kandidaten + kzg_kandidaten

    if not alle_kandidaten:
        logger.info("GV4: Keine Kandidaten gefunden")
        return []

    # ── 3. Filter: bereits erwaehnt ──
    session_turns: list[dict] = state.get("session_turns", [])
    gefiltert: list[dict] = [
        k for k in alle_kandidaten
        if not ist_bereits_erwaehnt(k["konzept"], session_turns)
    ]

    gefiltert = [
        k for k in gefiltert
        if k["similarity"] <= GV_LUECKEN_SIM_OBERGRENZE
    ]

    if not gefiltert:
        logger.info("GV4: Alle Kandidaten bereits erwaehnt oder zu aehnlich")
        return []

    # ── 4. Relevanz berechnen ──
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    for k in gefiltert:
        basis: float = k["similarity"] * k["gewicht"] * GV_QUELLEN_FAKTOR

        # Neugier-Boost aus Ziel-Gravitation (Turn-Embedding als Proxy)
        neugier_boost: float = 0.0
        if aktivierte_ziele:
            max_grav: float = 0.0
            for ziel in aktivierte_ziele:
                ziel_embedding = ziel.get("embedding")
                if not ziel_embedding:
                    continue
                ziel_sim: float = cosine_similarity(
                    turn_embedding, ziel_embedding
                )
                grav: float = ziel_sim * ziel.get("motivation", 0.5)
                max_grav = max(max_grav, grav)
            if max_grav >= GV_NEUGIER_BOOST_SCHWELLE:
                neugier_boost = max_grav

        register: float = register_kompatibilitaet(
            k["gap_arousal"], modus, dynamik
        )

        relevanz: float = (
            basis
            * (1.0 + neugier_boost)
            * aufnahmebereitschaft
            * register
        )

        k["relevanz"]      = relevanz
        k["neugier_boost"] = neugier_boost
        k["register"]      = register

    # ── 5. Charakter-Filter ──
    # resonanz_pruefbar statt Zahlen-Fallback (Chat 107,
    # GV-RESONANZ-FALLBACK-LUEGT): Der fruehere Fallback 0.5 hat nie etwas
    # entschieden — er lag ueber der Schwelle (0.40), also passierte ohnehin
    # jeder Kandidat. Er hat ein "nicht anwendbar" als "passt hervorragend"
    # verkleidet. Das Flag trifft dieselbe Entscheidung und sagt die Wahrheit
    # darueber. Fallback 0.0 wurde bewusst VERWORFEN: Er haette die Neugier
    # beim frischen Paar abgewuergt, ausgerechnet dort, wo ungefilterte
    # Neugier plausibel ist.
    #
    # **Seit dem 12.09.2026 steht hier keine Rechnung mehr, sondern eine
    # Feststellung.** Die Naehe zum Kern ist in Schritt 2 je Kandidat mit der
    # Suche entstanden; hier wird nur noch gezaehlt, ob sie vorliegt. Der
    # frueher hier gerechnete Wert war fuer alle Kandidaten derselbe — die
    # Naehe des **Turns** — und machte aus dem Filter einen globalen Schalter.
    resonanz_pruefbar: bool = _resonanz_pruefbar(gefiltert, kern_embedding)
    if kern_embedding and not resonanz_pruefbar:
        # Ein Kern lag vor, und trotzdem fehlt der Wert bei mindestens einem
        # Kandidaten: Das ist ein Defekt einer der beiden Suchen und **kein**
        # Cold-Start. Er darf nicht als derselbe Fall durchlaufen.
        ohne: int = sum(1 for k in gefiltert if "charakter_resonanz" not in k)
        logger.error(
            "GV4: Kern vorhanden, aber %d von %d Kandidaten ohne "
            "`charakter_resonanz` — eine der beiden Suchen hat den Vektor "
            "nicht geliefert. Die Resonanz-Pruefung entfaellt fuer diesen Turn.",
            ohne, len(gefiltert),
        )

    # **Die Verteilung wird protokolliert, nicht nur die Entscheidung.**
    # Der Grenzwert steht noch auf dem Wert, der fuer die Turn-Naehe gesetzt
    # war; was er auf der Kandidaten-Naehe tut, sagt erst der Betrieb. Ohne
    # diese Zeile waere die naechste Kalibrierung wieder auf einen
    # Stellvertreter angewiesen (`21_MESSUNG/stellvertreter-eicht-nicht.md`).
    if resonanz_pruefbar and gefiltert:
        werte: list[float] = sorted(k["charakter_resonanz"] for k in gefiltert)
        log_berechnung(
            turn_id = state.get("turn_id", "unbekannt"),
            node    = "wissensluecken",
            quelle  = pipeline_quelle(state),
            inhalt  = {
                "schritt":   "gv4_kern_resonanz",
                "n":         len(werte),
                "min":       round(werte[0], 4),
                "median":    round(werte[len(werte) // 2], 4),
                "max":       round(werte[-1], 4),
                "schwelle":  GV_CHARAKTER_RESONANZ_SCHWELLE,
                "darueber":  sum(1 for w in werte if w >= GV_CHARAKTER_RESONANZ_SCHWELLE),
                "quellen":   {"lzg": sum(1 for k in gefiltert if k["quelle"] == "lzg"),
                              "kzg": sum(1 for k in gefiltert if k["quelle"] == "kzg")},
            },
            user_id      = user_id,
            character_id = character_id,
        )

    qualifiziert: list[dict] = _qualifizieren(gefiltert, resonanz_pruefbar)

    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)

    # Deduplizierung: Wenn zwei Luecken untereinander zu aehnlich sind,
    # nur die mit der hoeheren Relevanz behalten.
    dedupliziert: list[dict] = []
    for kandidat in qualifiziert:
        ist_duplikat: bool = False
        for behalten in dedupliziert:
            # Einfacher Token-Overlap als Proxy (kein Embedding noetig)
            woerter_a: set[str] = {w.lower() for w in kandidat["konzept"].split() if len(w) > 3}
            woerter_b: set[str] = {w.lower() for w in behalten["konzept"].split() if len(w) > 3}
            if woerter_a and woerter_b:
                overlap: float = len(woerter_a & woerter_b) / min(len(woerter_a), len(woerter_b))
                if overlap > 0.6:
                    ist_duplikat = True
                    logger.debug(
                        f"GV4-Dedup: '{kandidat['konzept'][:50]}' "
                        f"ist Duplikat von '{behalten['konzept'][:50]}' "
                        f"(Overlap {overlap:.0%})"
                    )
                    break
        if not ist_duplikat:
            dedupliziert.append(kandidat)
    qualifiziert = dedupliziert

    # ── 6. Top N ──
    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)
    ergebnis: list[dict] = qualifiziert[:GV_LUECKEN_MAX]

    if ergebnis:
        logger.info(
            f"GV4: {len(ergebnis)} Wissensluecken qualifiziert — "
            + ", ".join(
                f"'{luecke['konzept'][:40]}' ({luecke['quelle']}, rel={luecke['relevanz']:.3f})"
                for luecke in ergebnis
            )
        )
    else:
        logger.info(
            f"GV4: {len(gefiltert)} Kandidaten geprueft, "
            f"keine ueber Relevanz-Schwelle {GV_LUECKEN_MIN_RELEVANZ}"
        )

    return ergebnis
