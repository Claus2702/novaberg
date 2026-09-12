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
from ei.gap_topics import embed_topics, load_user_topics, split_topics, touched_by_user
from ei.neugier import register_kompatibilitaet
from ei.source_weights import SOURCES, load_weight_distributions, weight_rank
from ei.utils import cosine_similarity
from graph.reiz import reiz_text
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
) -> list[dict]:
    """Sucht die LZG-Knoten **aus Novas Sicht**, die dem Turn am naechsten liegen.

    **Seit dem 12.09.2026 liefert die Suche Knoten, nicht Kandidaten** (`F-GV-2`).
    Kandidat ist ein Thema eines dieser Knoten; die Zerlegung, die Naehe zum Turn
    und die Resonanz zum Kern entstehen danach, auf dem Thema. Bis dahin rechnete
    diese Abfrage die Kern-Naehe des **Satzes** mit — und der Satz trug den
    Sprecher (+0,302 zwischen Nova- und Nutzer-Saetzen).

    **Nur `beobachter = 'assistant'`**: Die Luecke beim Nutzer ist ein Thema, das
    Nova kennt. Themen aus Nutzer-Knoten waeren nach Definition beruehrt.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht, gap_arousal, themen, quelle.
    """
    kandidaten: list[dict] = []

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        embedding_str: str = "[" + ",".join(str(v) for v in turn_embedding) + "]"

        cursor.execute(
            """
            SELECT inhalt,
                   1 - (embedding <=> %s::vector) AS similarity,
                   gewicht_decay,
                   COALESCE(arousal, 0.3) AS gap_arousal,
                   themen
            FROM lzg_knoten
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
              AND beobachter = 'assistant'
            ORDER BY embedding <=> %s::vector
            LIMIT 10
            """,
            (embedding_str, user_id, character_id, embedding_str),
        )

        for row in cursor.fetchall():
            inhalt, similarity, gewicht, gap_arousal, themen = row
            # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.1 —
            # liess im alten Raum 93 % durch, filterte nichts. 0.20 liegt
            # knapp ueber dem neuen Grundrauschen (0.16).
            if similarity and similarity > 0.20:
                kandidaten.append({
                    "konzept":    inhalt,
                    "similarity": float(similarity),
                    "gewicht":    float(gewicht) if gewicht else 0.5,
                    "gap_arousal": float(gap_arousal),
                    "themen":     list(themen or []),
                    "quelle":     "lzg",
                })

        conn.close()
        logger.info(f"GV4-LZG: {len(kandidaten)} Knoten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-LZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def kzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
) -> list[dict]:
    """Sucht die KZG-Eintraege **aus Novas Sicht**, die dem Turn am naechsten liegen.

    **Seit dem 12.09.2026 liefert die Suche Eintraege, nicht Kandidaten** — wie
    `lzg_kandidaten_suchen`, und aus demselben Grund. Das `embedding` kommt nicht
    mehr mit: Die Resonanz entsteht auf dem Thema, nicht auf dem Satz.

    **Nutzt weiter `redis_client_bytes` und dekodiert selbst.** Ohne Blob in der
    Rueckgabe waere auch der dekodierende Client moeglich; der Weg bleibt, damit
    ein spaeter wieder mitgeholtes Byte-Feld die Suche nicht lautlos leert
    (12.09.2026: 0 Kandidaten bei 3544 Schluesseln, weil ein Blob durch UTF-8 lief).

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht (=salienz), gap_arousal, themen, quelle.
    """
    kandidaten: list[dict] = []

    try:
        query_blob: bytes = np.array(turn_embedding, dtype=np.float32).tobytes()

        ergebnis = redis_client_bytes.execute_command(
            "FT.SEARCH", "idx:kzg",
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}} @beobachter:{{assistant}})"
            f"=>[KNN 10 @embedding $vec AS score]",
            "PARAMS", "2", "vec", query_blob,
            "SORTBY", "score",
            "LIMIT", "0", "10",
            "RETURN", "5", "inhalt", "salienz", "arousal", "score", "themen",
            "DIALECT", "2",
        )

        if ergebnis and isinstance(ergebnis, list) and len(ergebnis) > 1:
            idx: int = 1
            while idx < len(ergebnis) - 1:
                felder = ergebnis[idx + 1]
                idx += 2

                feld_dict: dict = {}
                for i in range(0, len(felder), 2):
                    k = felder[i].decode("utf-8") if isinstance(felder[i], bytes) else felder[i]
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
                    kandidaten.append({
                        "konzept":     inhalt,
                        "similarity":  similarity,
                        "gewicht":     salienz,
                        "gap_arousal": arousal,
                        "themen":      feld_dict.get("themen", ""),
                        "quelle":      "kzg",
                    })

        logger.info(f"GV4-KZG: {len(kandidaten)} Eintraege gefunden")

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


def _rank_weights(
    candidates: list[dict], user_id: str, character_id: str,
) -> list[dict]:
    """Setzt an jeden Kandidaten `gewicht_rang` — den Rang seines Gewichts in der eigenen Quelle.

    Vorbedingung: `user_id` und `character_id` sind gesetzt; jeder Kandidat traegt
        `quelle` (`lzg` oder `kzg`) und `gewicht`.
    Nachbedingung: Jeder zurueckgegebene Kandidat traegt `gewicht_rang` in [0, 1].
        Ein Kandidat, fuer dessen Quelle auch nach einem Neuladen keine
        Verteilung vorliegt, faellt heraus — **laut**, als Fehler.
    Fehlerfaelle: Ist die Verteilung nicht ladbar, kommt eine leere Liste zurueck
        und ein Fehler steht im Log: Ohne gemeinsame Skala gibt es in diesem Turn
        keine Luecken, und das darf nicht aussehen wie ein Turn ohne Kandidaten.

    Args:
        candidates: die Kandidaten nach den Filtern, beide Quellen gemischt.
        user_id: der Mensch des Paares.
        character_id: die Figur des Paares.

    Returns:
        Die Kandidaten mit gesetztem `gewicht_rang`.
    """
    # ── Eingabe-Validierung ─────────────────────
    unbekannt: list[str] = sorted({str(k.get("quelle")) for k in candidates} - set(SOURCES))
    if unbekannt:
        logger.error(
            "GV4: Kandidaten mit unbekannter Quelle %s — erwartet %s; verworfen",
            unbekannt, SOURCES,
        )
        candidates = [k for k in candidates if k.get("quelle") in SOURCES]

    # ── Verarbeitung ────────────────────────────
    try:
        verteilungen: dict[str, list[float]] = load_weight_distributions(user_id, character_id)
        if any(not verteilungen[k["quelle"]] for k in candidates):
            # Ein Kandidat aus einer Quelle ohne Verteilung: Der Zwischenspeicher
            # ist aelter als der erste Eintrag dieser Quelle. Einmal neu laden.
            verteilungen = load_weight_distributions(user_id, character_id, refresh=True)
    except Exception as fehler:
        logger.error(
            "GV4: Gewichtsverteilung fuer %s/%s nicht ladbar (%s: %s) — ohne "
            "gemeinsame Skala keine Luecken in diesem Turn",
            user_id, character_id, type(fehler).__name__, fehler, exc_info=True,
        )
        return []

    ergebnis: list[dict] = []
    for k in candidates:
        verteilung: list[float] = verteilungen[k["quelle"]]
        if not verteilung:
            logger.error(
                "GV4: Kandidat aus %s, aber keine Gewichtsverteilung dieser Quelle "
                "fuer %s/%s — verworfen: '%s'",
                k["quelle"], user_id, character_id, str(k.get("konzept", ""))[:60],
            )
            continue
        try:
            k["gewicht_rang"] = weight_rank(k["gewicht"], verteilung)
        except ValueError:
            logger.exception("GV4: Gewicht nicht einordbar — Kandidat verworfen")
            continue
        ergebnis.append(k)

    # ── Ausgabe-Verifikation ────────────────────
    if len(ergebnis) != len(candidates):
        logger.error(
            "GV4: %d von %d Kandidaten ohne Rang verworfen (Gruende oben)",
            len(candidates) - len(ergebnis), len(candidates),
        )
    return ergebnis


def _topic_candidates(nodes: list[dict], state: ConversationState) -> list[dict]:
    """Macht aus Knoten Themen-Kandidaten und behaelt nur, was der Nutzer nicht beruehrt hat.

    **Die Luecke beim Nutzer** (`F-GV-2`): ein Thema aus Novas Bestand nahe am
    Turn, das (a) in keinem Nutzer-Eintrag des Paares als Thema steht und (b) im
    laufenden Gespraech nicht gefallen ist. Beides ist eine Annaeherung — das
    Fehlen eines Belegs, kein Nachweis.

    Vorbedingung: jeder Knoten traegt `themen`, `quelle`, `gewicht`,
        `gewicht_rang`, `similarity` und `gap_arousal`; `state` traegt Paar und
        Sitzungsturns.
    Nachbedingung: je Thema (ohne Gross-/Kleinschreibung) hoechstens ein
        Kandidat — der aus dem Knoten mit dem hoechsten `similarity × gewicht_rang`.
        Jeder Kandidat traegt `konzept` (das Thema), `knoten` (Anfang des Satzes),
        `knoten_similarity` und die Felder des Knotens. Die Zaehlung steht je
        Turn im Pipeline-Log, auch wenn nichts bleibt.
    Fehlerfaelle: Ist der Themenbestand des Nutzers nicht ladbar, kommt eine
        leere Liste zurueck und ein Fehler steht im Log — ohne ihn laesst sich
        nicht sagen, was eine Luecke **beim Nutzer** ist.

    Args:
        nodes: Knoten beider Quellen mit gesetztem Rang.
        state: der Zustand des Turns.

    Returns:
        Die Themen-Kandidaten.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id: str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    try:
        nutzer = load_user_topics(user_id, character_id)
    except Exception as fehler:
        logger.error(
            "GV4: Themenbestand des Nutzers %s/%s nicht ladbar (%s: %s) — ohne ihn "
            "keine Luecke beim Nutzer in diesem Turn",
            user_id, character_id, type(fehler).__name__, fehler, exc_info=True,
        )
        return []

    # ── Verarbeitung ────────────────────────────
    # **Der laufende Reiz gehoert zum Gespraech.** `session_turns` traegt nur die
    # vorigen Turns; ohne den Reiz selbst kam das Echo der eigenen Frage als
    # Luecke zurueck — `[gemessen 12.09.2026]` *„Staerke des Magnetfelds im
    # Vergleich zur Erde"* (Naehe 0,798) auf genau diese Frage.
    session_turns: list[dict] = [
        *(state.get("session_turns", []) or []),
        {"inhalt": reiz_text(state)},
    ]
    besten: dict[str, dict] = {}
    zaehlung: dict[str, int] = {"knoten": len(nodes), "ohne_themen": 0, "themen": 0,
                                "beruehrt": 0, "erwaehnt": 0}
    for knoten in nodes:
        themen: list[str] = split_topics(knoten.get("themen"))
        if not themen:
            zaehlung["ohne_themen"] += 1
            continue
        for thema in themen:
            zaehlung["themen"] += 1
            if touched_by_user(thema, nutzer):
                zaehlung["beruehrt"] += 1
                continue
            if ist_bereits_erwaehnt(thema, session_turns):
                zaehlung["erwaehnt"] += 1
                continue
            gewicht: float = knoten["similarity"] * knoten["gewicht_rang"]
            alt = besten.get(thema.lower())
            if alt is None or gewicht > alt["knoten_similarity"] * alt["gewicht_rang"]:
                besten[thema.lower()] = {
                    "konzept":           thema,
                    "knoten":            str(knoten.get("konzept", ""))[:80],
                    "knoten_similarity": knoten["similarity"],
                    "quelle":            knoten["quelle"],
                    "gewicht":           knoten["gewicht"],
                    "gewicht_rang":      knoten["gewicht_rang"],
                    "gap_arousal":       knoten["gap_arousal"],
                }
    kandidaten: list[dict] = list(besten.values())

    # ── Ausgabe-Verifikation ────────────────────
    if len({k["konzept"].lower() for k in kandidaten}) != len(kandidaten):
        raise RuntimeError("GV4: doppeltes Thema unter den Kandidaten")
    zaehlung["kandidaten"] = len(kandidaten)
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "wissensluecken",
        quelle  = pipeline_quelle(state),
        inhalt  = {"schritt": "gv4_themen", **zaehlung},
        user_id      = user_id,
        character_id = character_id,
    )
    logger.info(
        "GV4: %d Knoten → %d Themen, %d vom Nutzer beruehrt, "
        "%d im Gespraech erwaehnt → %d Kandidaten",
        zaehlung["knoten"], zaehlung["themen"], zaehlung["beruehrt"],
        zaehlung["erwaehnt"], len(kandidaten),
    )
    return kandidaten


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

    # ── 1b. Kern-Embedding ──
    # Gebraucht in Schritt 3c, wo jedes Thema gegen den Kern gemessen wird. Bis
    # zum 12.09.2026 (abends) brauchten ihn die beiden Suchen, um die Naehe des
    # **Satzes** zum Kern mitzurechnen; seit die Kandidaten Themen sind, messen
    # sie ihn nicht mehr.
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

    # ── 2. Knoten aus Novas Bestand, nahe am Turn ──
    alle_knoten: list[dict] = (
        lzg_kandidaten_suchen(turn_embedding, user_id, character_id)
        + kzg_kandidaten_suchen(turn_embedding, user_id, character_id)
    )
    if not alle_knoten:
        logger.info("GV4: Keine Knoten gefunden")
        return []

    # ── 3. Das Gewicht auf die gemeinsame Skala ──
    # **Die Naht zwischen LZG und KZG.** Roh traegt das LZG `gewicht_decay`
    # (3–10), das KZG `salienz` (0–1); im Produkt gewann das LZG allein durch
    # seine Skala — 77 von 83 Luecken im Prompt, 12.09.2026. Das Gewicht geht
    # deshalb als **Rang in der eigenen Quelle** ein. Das rohe Gewicht bleibt am
    # Kandidaten stehen, damit die Rechnung nachvollziehbar bleibt.
    alle_knoten = _rank_weights(alle_knoten, user_id, character_id)
    if not alle_knoten:
        return []

    # ── 3b. Themen statt Saetze — und nur, was der Nutzer nicht beruehrt hat ──
    gefiltert: list[dict] = _topic_candidates(alle_knoten, state)
    if not gefiltert:
        logger.info("GV4: Keine Themen-Kandidaten nach den Filtern")
        return []

    # ── 3c. Naehe zum Turn und Resonanz zum Kern — auf dem Thema ──
    # Ein Stapelaufruf fuer alle neuen Themen; bekannte kommen aus dem
    # Zwischenspeicher. Faellt die Einbettung aus, gibt es in diesem Turn keine
    # Luecken — laut, nicht als leerer Bestand.
    try:
        vektoren: dict[str, list[float]] = embed_topics([k["konzept"] for k in gefiltert])
    except Exception as fehler:
        logger.error(
            "GV4: Themen nicht einbettbar (%s: %s) — keine Luecken in diesem Turn",
            type(fehler).__name__, fehler, exc_info=True,
        )
        return []
    for k in gefiltert:
        vektor: list[float] = vektoren[k["konzept"]]
        k["similarity"] = cosine_similarity(vektor, turn_embedding)
        if kern_embedding:
            k["charakter_resonanz"] = cosine_similarity(vektor, kern_embedding)

    gefiltert = [
        k for k in gefiltert
        if k["similarity"] <= GV_LUECKEN_SIM_OBERGRENZE
    ]
    if not gefiltert:
        logger.info("GV4: Alle Themen zu nah am Turn — bereits gesagt")
        return []

    # ── 4. Relevanz berechnen ──
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    for k in gefiltert:
        basis: float = k["similarity"] * k["gewicht_rang"] * GV_QUELLEN_FAKTOR

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
    # Feststellung.** Die Naehe zum Kern ist in Schritt 3c je Thema entstanden;
    # hier wird nur noch gezaehlt, ob sie vorliegt. Der frueher hier gerechnete
    # Wert war fuer alle Kandidaten derselbe — die Naehe des **Turns** — und
    # machte aus dem Filter einen globalen Schalter; der danach auf dem Satz
    # gerechnete trennte nach Sprecher.
    resonanz_pruefbar: bool = _resonanz_pruefbar(gefiltert, kern_embedding)
    if kern_embedding and not resonanz_pruefbar:
        # Ein Kern lag vor, und trotzdem fehlt der Wert bei mindestens einem
        # Kandidaten: Das ist ein Defekt der Themen-Messung in 3c und **kein**
        # Cold-Start. Er darf nicht als derselbe Fall durchlaufen.
        ohne: int = sum(1 for k in gefiltert if "charakter_resonanz" not in k)
        logger.error(
            "GV4: Kern vorhanden, aber %d von %d Kandidaten ohne "
            "`charakter_resonanz` — die Themen-Messung hat den Wert nicht "
            "gesetzt. Die Resonanz-Pruefung entfaellt fuer diesen Turn.",
            ohne, len(gefiltert),
        )

    # **Die Verteilung wird protokolliert, nicht nur die Entscheidung.**
    # Seit dem 12.09.2026 ist es die Verteilung ueber **Themen** gegen den Kern
    # — eine andere Paarung als zuvor, mit eigenem Grenzwert. Ohne
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

    # **Die Quellenmischung wird je Turn festgehalten, auch wenn sie leer ist.**
    # Sie ist die Zahl, an der die Naht zwischen LZG und KZG gemessen wird; ohne
    # diese Zeile stuende sie nur im Server-Log, das rotiert.
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "wissensluecken",
        quelle  = pipeline_quelle(state),
        inhalt  = {
            "schritt":    "gv4_quellen_naht",
            "kandidaten": {q: sum(1 for k in gefiltert if k["quelle"] == q) for q in SOURCES},
            "ergebnis":   {q: sum(1 for k in ergebnis if k["quelle"] == q) for q in SOURCES},
            "rang":       [round(k["gewicht_rang"], 4) for k in ergebnis],
        },
        user_id      = user_id,
        character_id = character_id,
    )

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
