"""
Session-Kontext — Gesprächsverlauf in Redis.
Temporär (TTL), mit automatischer Zusammenfassung.
"""

import json
import logging
import time
from dataclasses import dataclass

import redis

from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.memory.session")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
SESSION_MAX_TURNS:    int = 20
SESSION_SUMMARIZE_AT: int = 25      # Ab 25 Turns: älteste 10 zusammenfassen

# Wie lange ein Verlauf ohne Aeusserung ueberdauert. **Sie muss mindestens so
# lang sein wie die Verfallskurve der Eigenzeit** (`EIGENZEIT_NULLPUNKT_SEKUNDEN`,
# 3 h): Sonst entsteht ein Fenster, in dem der Verlauf vor dem Zustand
# verschwindet — Nova waere noch nicht zur Ruhe gekommen und haette schon
# vergessen, worueber gesprochen wurde. Genau die fremde Nova, die
# `novaberg-eigenzeit_k.md` §2.2 vermeiden will, nur von der anderen Seite.
#
# Am 15.08.2026 von 7200 (2 h) auf 14400 erhoeht. Die Frist kostet nichts pro
# Turn: Die Laenge des Verlaufs begrenzen SESSION_SUMMARIZE_AT und
# SESSION_MAX_TURNS, nicht sie.
SESSION_TTL:          int = 14400   # 4 Stunden Inaktivitaet


def _session_key(user_id: str, character_id: str, suffix: str) -> str:
    """Baut den Redis-Key für eine Session-Partition.

    Format: session:{user_id}:{character_id}:{suffix}
    Beispiel: session:meister:nova:turns
    """
    return f"session:{user_id}:{character_id}:{suffix}"


# ─────────────────────────────────────────────
# Turn speichern
# ─────────────────────────────────────────────
def session_turn_store(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    rolle:        str,
    inhalt:       str,
    intentionen:  list = None,
    emotion:      str  = "",
    arousal:      float = 0.5,
    modus:        str  = "",
    kern:         str  = "",
    emotions_vektor:    str = "",
    sprach_stil:        str = "",
    beziehungs_dynamik: str = "",
    tone:               str = "",
    themen:             list[str] | None = None,
    embedding:          list[float] | None = None,
    herkunft:           str = "",
) -> None:
    """Speichert einen Turn in der Session, vollständig mit allen Meta-Daten.

    `herkunft` benennt den Vorgang, der den Turn erzeugt hat — `nutzer_turn`
    oder `eigener_impuls`. Leer bleibt sie nur dort, wo der Aufrufer sie nicht
    bestimmen kann; **leer heisst unbekannt und nicht "vom Nutzer"**.
    """
    key: str = _session_key(user_id, character_id, "turns")

    turn_data: dict = {
        "rolle":        rolle,
        "inhalt":       inhalt,
        "zeit":         time.time(),
        "intentionen":  intentionen or [],
        "emotion":      emotion,
        "arousal":      arousal,
        "modus":        modus,
        "kern":         kern,
        "emotions_vektor":    emotions_vektor,
        "sprach_stil":        sprach_stil,
        "beziehungs_dynamik": beziehungs_dynamik,
        "tone":               tone,
        # Wer diesen Turn erzeugt hat. Zwei Vorgaenge schreiben Eintraege
        # derselben Form in diesen Verlauf — die Antwort auf eine
        # Nutzeraeusserung und Novas eigener Impuls —, und ohne dieses Feld
        # sind sie in den Daten nicht zu unterscheiden. Sie waren es bis zum
        # 30.07.2026 nicht: Die Herkunft stand allein im Laufzeit-Protokoll,
        # und wer den Verlauf aus dem Speicher las, hielt einen Impuls fuer
        # eine Antwort (novaberg-bugs.md -> PFAD1-TIMEOUT-TURNVERLUST).
        #
        # Leer heisst **unbekannt**, nicht "nutzer_turn". Turns von vor dieser
        # Aenderung tragen das Feld nicht, und ein Default haette aus ihnen
        # rueckwirkend eine Aussage gemacht, die niemand erhoben hat.
        "herkunft":           herkunft,
    }

    if themen is not None:
        turn_data["themen"] = themen

    # Embedding als JSON-Array mitspeichern (nur fuer User-Turns relevant — wird
    # vom Gravitationsgraph-Panel gelesen, um Turns auf 2D zu projizieren).
    if embedding:
        turn_data["embedding"] = list(embedding)

    turn: str = json.dumps(turn_data, ensure_ascii=False)

    redis_client.rpush(key, turn)
    redis_client.expire(key, SESSION_TTL)

    laenge: int = redis_client.llen(key)
    logger.info(f"Session: Turn gespeichert ({rolle}, {laenge} Turns)")


# ─────────────────────────────────────────────
# Turn als Agent-Aktion markieren (KONTEXT1)
# ─────────────────────────────────────────────
def session_turn_mark_action(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    erledigt:     bool = True,
    erfolgreich:  bool = False,
) -> None:
    """Markiert den letzten User-Turn mit Agent-Aktionsstatus.

    Zwei Flags:
    - aktion_erledigt:    Agent hat Verarbeitung beendet (abgeschlossen oder fehler)
    - aktion_erfolgreich: Agent hat die Aktion umgesetzt (nur bei abgeschlossen)

    Wird NICHT aufgerufen bei Rueckfragen (status=rueckfrage).
    """
    key: str = _session_key(user_id, character_id, "turns")
    turns: list = redis_client.lrange(key, 0, -1)

    if not turns:
        return

    for idx in range(len(turns) - 1, -1, -1):
        try:
            turn: dict = json.loads(turns[idx])
        except json.JSONDecodeError:
            continue

        if turn.get("rolle") == "user":
            turn["aktion_erledigt"] = erledigt
            turn["aktion_erfolgreich"] = erfolgreich
            redis_client.lset(key, idx, json.dumps(turn, ensure_ascii=False))
            logger.debug(f"Session-Turn {idx} markiert: erledigt={erledigt}, erfolgreich={erfolgreich}")
            return


# ─────────────────────────────────────────────
# Zusammenfassung prüfen und erstellen
# ─────────────────────────────────────────────
def session_summarize_if_needed(
    redis_client:  redis.Redis,
    user_id:       str,
    character_id:  str,
) -> None:
    """Fasst älteste Turns zusammen wenn der Stack zu groß wird."""
    key:         str = _session_key(user_id, character_id, "turns")
    summary_key: str = _session_key(user_id, character_id, "summary")
    laenge:      int = redis_client.llen(key)

    if laenge <= SESSION_SUMMARIZE_AT:
        return

    # Älteste 10 Turns holen
    alte_turns_raw: list      = redis_client.lrange(key, 0, 9)
    alte_turns:     list[str] = []

    for raw in alte_turns_raw:
        try:
            turn: dict = json.loads(raw)
        except json.JSONDecodeError:
            continue
        # Auch hier steht der Sprecher im Feld. Die Zusammenfassung ueberdauert
        # den Verlauf und wird spaeter als Tatsache gelesen — ein Impuls, der
        # hier als blosse Antwort steht, wird zu einer Aeusserung auf Zuruf,
        # und der Anlass ist danach nicht mehr rekonstruierbar.
        beitrag: Verlaufsbeitrag = _beitrag_aus_turn(turn)
        if not beitrag.inhalt:
            continue
        alte_turns.append(
            f"{sprecher_bezeichnen(beitrag, nova_name='Assistent')}: {beitrag.inhalt}"
        )

    if not alte_turns:
        return

    bisherige_summary: str = redis_client.get(summary_key) or ""

    zusammenfassung_prompt: str = (
        "Fasse den folgenden Gesprächsverlauf in 3-5 Sätzen zusammen. "
        "Behalte konkrete Namen, Fakten, Orte und Zahlen bei. "
        "Antworte NUR mit der Zusammenfassung.\n\n"
    )

    if bisherige_summary:
        zusammenfassung_prompt += (
            f"Bisherige Zusammenfassung:\n{bisherige_summary}\n\n"
            f"Neue Turns:\n"
        )

    zusammenfassung_prompt += "\n".join(alte_turns)

    try:
        # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
        # session_summarize_if_needed() wird vom CharacterGraph-dispatcher-Node
        # gerufen ([dispatcher.py:264]) — der CharacterGraph laeuft in
        # event_consumer.py via asyncio.to_thread(_graph_streamen, ...).
        # Kein Event-Loop im aufrufenden Thread → submit_sync. Einzige
        # nicht-Pixie-getriggerte G3-Stelle und damit live-verifizierbar
        # ohne Block 4.
        chat_request = ChatRequest(
            messages    = [{"role": "user", "content": zusammenfassung_prompt}],
            system      = "Du fasst Gespräche zusammen. Kurz, präzise, keine Details verlieren.",
            temperature = 0.2,
            caller      = "session/summary",
        )
        response = model_service.chat.submit_sync(chat_request)

        neue_summary: str = response.text.strip()

        redis_client.set(summary_key, neue_summary)
        redis_client.expire(summary_key, SESSION_TTL)
        redis_client.ltrim(key, 10, -1)

        logger.info(f"Session: 10 Turns zusammengefasst, {redis_client.llen(key)} verbleiben")

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Session-Zusammenfassung fehlgeschlagen")
        redis_client.ltrim(key, laenge - SESSION_MAX_TURNS, -1)


# ─────────────────────────────────────────────
# Turns abrufen
# ─────────────────────────────────────────────
def session_turns_retrieve(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> list[dict]:
    """Holt alle Turns der aktuellen Session."""
    key:        str       = _session_key(user_id, character_id, "turns")
    raw_turns:  list      = redis_client.lrange(key, 0, -1)
    turns:      list[dict] = []

    for raw in raw_turns:
        try:
            turns.append(json.loads(raw))
        except json.JSONDecodeError:
            continue

    return turns


# ─────────────────────────────────────────────
# Verlauf gruppieren — die Zuordnung kommt aus dem Feld
# ─────────────────────────────────────────────
#: Herkunftswert eines Turns, den Nova von sich aus begonnen hat.
HERKUNFT_EIGENER_IMPULS: str = "eigener_impuls"


@dataclass
class Verlaufsbeitrag:
    """Eine Aeusserung im Verlauf, mit ihrem Sprecher.

    **Der Sprecher steht im Feld, nicht in der Position.** Wer ihn aus der
    Reihenfolge erschliesst, ordnet nach einem Ausfall jede folgende
    Aeusserung der falschen Person zu — und jede sieht an ihrer neuen Stelle
    plausibel aus.
    """

    sprecher:           str            #: "user" | "nova"
    inhalt:             str
    aus_eigenem_antrieb: bool = False  #: Nova hat begonnen, niemand hat gefragt
    herkunft_bekannt:   bool  = True   #: False -> Turn von vor dem 30.07.2026
    emotion:            str   = ""
    arousal:            float = 0.0
    aktion_erledigt:    bool  = False
    aktion_erfolgreich: bool  = False


def _beitrag_aus_turn(turn: dict) -> Verlaufsbeitrag:
    """Uebersetzt einen gespeicherten Turn in einen Beitrag mit Sprecher.

    Vorbedingung: `turn` ist ein Dict aus `session_turn_store`; fehlende
        Felder sind zulaessig — Turns von vor dem 30.07.2026 tragen kein
        `herkunft`.
    Nachbedingung: `sprecher` ist "user" oder "nova", nie leer, und
        `herkunft_bekannt` ist genau dann False, wenn der Turn keine
        Herkunftsangabe traegt. **Ein fehlendes Feld wird zu "unbekannt",
        nicht zu "nutzer_turn"** — ein Default haette hier rueckwirkend eine
        Aussage erzeugt, die niemand erhoben hat.
    Fehlerfaelle: keine; jedes fehlende Feld hat einen benannten Ausfallwert.
    """
    ist_nutzer: bool = turn.get("rolle") == "user"
    herkunft:   str  = (turn.get("herkunft") or "").strip()
    return Verlaufsbeitrag(
        sprecher            = "user" if ist_nutzer else "nova",
        inhalt              = turn.get("inhalt", ""),
        aus_eigenem_antrieb = herkunft == HERKUNFT_EIGENER_IMPULS,
        herkunft_bekannt    = bool(herkunft),
        emotion             = turn.get("emotion", ""),
        arousal             = turn.get("arousal", 0.0) or 0.0,
        aktion_erledigt     = bool(turn.get("aktion_erledigt")),
        aktion_erfolgreich  = bool(turn.get("aktion_erfolgreich")),
    )


def verlauf_gruppieren(turns: list[dict]) -> list[list[Verlaufsbeitrag]]:
    """Gruppiert Turns zu nummerierbaren Abschnitten — **ohne einen zu verlieren**.

    Vorbedingung: `turns` ist die Liste aus `session_turns_retrieve`, aeltester
        zuerst. Ein Turn ohne `inhalt` traegt nichts bei und faellt weg; das ist
        der einzige Fall, in dem hier etwas entfaellt.
    Nachbedingung: Jeder Turn mit Inhalt steht in genau einer Gruppe, und jeder
        Beitrag nennt seinen Sprecher aus seinen **eigenen** Feldern.
    Fehlerfaelle: keine — eine unbekannte Rolle wird zu "nova", weil der Verlauf
        nur zwei Sprecher kennt und ein dritter Name den Leser mehr verwirrte
        als die Zuordnung zur nicht-fremden Seite.

    **Die Gruppe ist eine Anzeigeeinheit, keine Zuordnung.** Sie fasst
    zusammen, was zeitlich zusammengehoert; wer gesprochen hat, entscheidet
    ausschliesslich der Beitrag.

    **Ein Impuls oeffnet immer seine eigene Gruppe** — entschieden am Feld
    `herkunft`, nicht an der Position. Bis zum 24.08.2026 fiel er aus dem
    Verlauf: Die Paarbildung kannte nur `user` gefolgt von `assistant` und
    uebersprang alles andere. Von 24 Turns eines laufenden Gespraechs
    erreichten **8** den Verlauf nicht, und Nova schrieb daraufhin einen
    Vorschlag, den sie selbst gemacht hatte, dem Nutzer zu
    (`novaberg-bugs.md` -> `IMPULS-FAELLT-AUS-DEM-VERLAUF`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turns:
        return []

    # ── Verarbeitung ────────────────────────────
    gruppen: list[list[Verlaufsbeitrag]] = []

    for turn in turns:
        beitrag: Verlaufsbeitrag = _beitrag_aus_turn(turn)
        if not beitrag.inhalt:
            continue

        # Wann eine neue Gruppe beginnt: bei jeder Nutzeraeusserung, bei jedem
        # Eigen-Impuls, und immer dann, wenn die offene Gruppe den Sprecher
        # schon enthaelt. Der letzte Fall ist der Riegel gegen Verlust: Er
        # macht es unmoeglich, dass ein Beitrag keinen Platz findet.
        offen: list[Verlaufsbeitrag] | None = gruppen[-1] if gruppen else None
        neue_gruppe: bool = (
            offen is None
            or beitrag.sprecher == "user"
            or beitrag.aus_eigenem_antrieb
            or any(b.sprecher == beitrag.sprecher for b in offen)
        )

        if neue_gruppe:
            gruppen.append([beitrag])
        else:
            offen.append(beitrag)

    # ── Ausgabe-Verifikation ────────────────────
    # Der Zweck dieser Funktion ist, dass nichts verschwindet — die Zaehlung
    # haelt genau das fest.
    #
    # **Sie ist ein Regressionsriegel und keine Datenpruefung, und das ist ein
    # Unterschied.** Solange die Schleife oben jeden Beitrag mit Inhalt in
    # genau eine Gruppe legt, sind `erwartet` und `gezaehlt` dasselbe
    # Praedikat ueber dieselbe Menge: Sie kann heute nicht anschlagen. In
    # 40.439 konstruierten Faellen tat sie es null Mal (zweite Kontrolle,
    # 24.08.2026). Ihr Wert liegt in der Zukunft — sie feuert, sobald jemand
    # ein `continue` in diese Schleife setzt, und genau so ist der Defekt
    # entstanden, den sie bewacht. Wer sie fuer eine Laufzeitpruefung der
    # Daten haelt, ueberschaetzt sie.
    erwartet: int = sum(1 for x in turns if (x.get("inhalt") or ""))
    gezaehlt: int = sum(len(g) for g in gruppen)
    if gezaehlt != erwartet:
        logger.error(
            "verlauf_gruppieren: %d Turns mit Inhalt hinein, %d Beitraege "
            "heraus — der Verlauf verliert eine Aeusserung",
            erwartet, gezaehlt,
        )

    return gruppen


def fenster_waehlen(
    gruppen:   list[list[Verlaufsbeitrag]],
    max_turns: int,
) -> list[list[Verlaufsbeitrag]]:
    """Die letzten `max_turns` **Wortwechsel** — Impulse dazwischen kommen mit.

    Vorbedingung: `gruppen` aus `verlauf_gruppieren`, aelteste zuerst.
    Nachbedingung: Das Ergebnis enthaelt hoechstens `max_turns` Gruppen **mit
        einer Nutzeraeusserung** und dazu jede Eigen-Impuls-Gruppe, die
        zwischen ihnen liegt. Die Reihenfolge bleibt.
    Fehlerfaelle: `max_turns <= 0` liefert eine leere Liste — das ist die
        Bedeutung der Zahl und kein Fehler.

    **Gezaehlt werden Wortwechsel, nicht Gruppen, und der Grund ist eine
    Regression.** Bis zum 24.08.2026 hiess `max_turns` *Turn-Paare*, und ein
    Impuls zaehlte gar nicht — er wurde uebersprungen. Danach zaehlte jede
    Gruppe, also auch ein Impuls. Das kehrt den behobenen Defekt um: Der
    Impuls faellt nicht mehr aus dem Verlauf, aber er **verdraengt** den
    Nutzer aus dem Fenster derer, die nur fuenf Einheiten sehen.

    `[gemessen]` — 24.08.2026, dieselbe Session Zustand fuer Zustand
    nachgefahren: Bei **16 von 24** Zustaenden lagen weniger Nutzer-Turns im
    Fenster als vorher, und bei einem (n=13) **keiner mehr** — Perzeption,
    Router und sechs Klassifikations-Knoten haetten dort einen Verlauf aus
    fuenf aufeinanderfolgenden Eigen-Impulsen und keinem Wort des Nutzers
    bekommen. Acht der neun Aufrufer uebergeben unveraendert `5`; die Zahl
    haette bei allen mitwandern muessen. **Sie wandert stattdessen hier
    zurueck in ihre alte Bedeutung.**
    """
    # ── Eingabe-Validierung ─────────────────────
    if max_turns <= 0 or not gruppen:
        return []

    # ── Verarbeitung ────────────────────────────
    # Von hinten zaehlen, bis `max_turns` Wortwechsel beisammen sind. Alles,
    # was dabei ueberstrichen wird — auch reine Impulsgruppen —, bleibt drin:
    # Ein Impuls **zwischen** zwei Wortwechseln ist der Anlass fuer den
    # zweiten und gehoert genau dorthin.
    wortwechsel: int = 0
    anfang:      int = len(gruppen)

    for i in range(len(gruppen) - 1, -1, -1):
        if any(b.sprecher == "user" for b in gruppen[i]):
            if wortwechsel == max_turns:
                break
            wortwechsel += 1
        anfang = i

    return gruppen[anfang:]


def sprecher_bezeichnen(
    beitrag:   Verlaufsbeitrag,
    nova_name: str = "NOVA",
    zusatz:    str = "",
) -> str:
    """Der Name, unter dem ein Beitrag im Prompt steht.

    `zusatz` nimmt Anmerkungen des Aufrufers (Emotion, Aktionsmarke) auf, damit
    sie **in derselben Klammer** stehen wie der Anlass. Zwei Klammern
    hintereinander lesen sich wie zwei verschiedene Angaben ueber verschiedene
    Dinge; hier sind es Angaben ueber dieselbe Aeusserung.

    Nachbedingung: nicht-leer, und fuer eine Aeusserung ohne belegte Herkunft
        ausdruecklich als unbelegt gekennzeichnet — **leer heisst unbekannt und
        nicht "auf Zuruf"** (`session_turn_store`).
    """
    name: str = "USER" if beitrag.sprecher == "user" else nova_name

    teile: list[str] = []
    if beitrag.sprecher != "user":
        if beitrag.aus_eigenem_antrieb:
            teile.append("von sich aus")
        elif not beitrag.herkunft_bekannt:
            teile.append("Anlass unbekannt")
    if zusatz.strip():
        teile.append(zusatz.strip())

    return f"{name} ({', '.join(teile)})" if teile else name


# ─────────────────────────────────────────────
# Nummerierte Turn-Formatierung (Chat 24)
# ─────────────────────────────────────────────
def format_session_turns_numbered(
    turns: list[dict],
    max_turns: int = 5,
    max_chars: int = 100,
) -> str:
    """Formatiert Session-Turns mit Naehenummerierung.

    Hoehere Nummer = naeher am aktuellen Prompt.

    Vorbedingung: `turns` aus `session_turns_retrieve`, aeltester zuerst.
    Nachbedingung: Jede Zeile nennt ihren Sprecher. Ein Eigen-Impuls steht als
        eigene Gruppe mit `(von sich aus)` — **er faellt nicht aus und er steht
        nicht auf dem Platz der fremden Rede.**
    Fehlerfaelle: keine; eine leere Eingabe liefert einen leeren Text.

    Args:
        turns: Liste von Turn-Dicts aus Redis
        max_turns: Maximale Anzahl **Gruppen** (bis 24.08.2026: Turn-Paare —
            ein Impuls zaehlte gar nicht, weil er uebersprungen wurde)
        max_chars: Maximale Zeichen pro Beitrag

    Returns:
        Formatierter String mit nummerierten Gruppen, leer wenn keine Turns
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turns:
        return ""

    # ── Verarbeitung ────────────────────────────
    gruppen: list[list[Verlaufsbeitrag]] = fenster_waehlen(
        verlauf_gruppieren(turns), max_turns,
    )

    zeilen: list[str] = []
    for nr, gruppe in enumerate(gruppen, start=1):
        for beitrag in gruppe:
            text: str = beitrag.inhalt
            if len(text) > max_chars:
                text = text[:max_chars] + "..."

            anmerkung: str = beitrag.emotion
            if beitrag.aktion_erledigt:
                marke: str = "ERLEDIGT" if beitrag.aktion_erfolgreich else "FEHLGESCHLAGEN"
                anmerkung = f"{anmerkung}, {marke}" if anmerkung else marke

            wer: str = sprecher_bezeichnen(beitrag, zusatz=anmerkung)
            zeilen.append(f"[{nr}] {wer}: {text}")

    return "\n".join(zeilen)


# ─────────────────────────────────────────────
# Kontext bauen (Summary + Turns)
# ─────────────────────────────────────────────
def session_context_build(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> str:
    """Baut den vollständigen Session-Kontext: Zusammenfassung + aktuelle Turns."""
    parts: list[str] = []

    summary_key: str = _session_key(user_id, character_id, "summary")
    summary:     str = redis_client.get(summary_key) or ""

    if summary:
        parts.append(f"[Bisheriger Gesprächsverlauf, zusammengefasst]\n{summary}")

    turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)

    if turns:
        turn_lines: list[str] = []
        for turn in turns:
            beitrag: Verlaufsbeitrag = _beitrag_aus_turn(turn)
            if not beitrag.inhalt:
                continue
            turn_lines.append(
                f"{sprecher_bezeichnen(beitrag, nova_name='Assistent')}: {beitrag.inhalt}"
            )

        parts.append("[Aktuelle Unterhaltung]\n" + "\n".join(turn_lines))

    return "\n\n".join(parts) if parts else ""


# ─────────────────────────────────────────────
# Session zurücksetzen
# ─────────────────────────────────────────────
def session_reset(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> None:
    """Löscht die aktuelle Session komplett."""
    redis_client.delete(_session_key(user_id, character_id, "turns"))
    redis_client.delete(_session_key(user_id, character_id, "summary"))
    redis_client.delete(_session_key(user_id, character_id, "stack"))
    redis_client.delete(_session_key(user_id, character_id, "pending"))

    logger.info(f"Session: Zurückgesetzt für user '{user_id}', charakter '{character_id}'")
