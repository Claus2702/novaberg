"""Charakter-Hash — Kern + Adaptiv aus PostgreSQL."""

import json
import logging

import psycopg2

from config import ASSISTANT_USER_ID, INITIATIVE_RAD_SPANNE, RAD_MAX, RAD_MIN

logger = logging.getLogger("ki_server.memory.charakter")


def charakter_hash_retrieve(postgres_url: str, user_id: str, character_id: str = "") -> str:
    """Holt den aktuellen Charakter-Hash fuer ein Gespraechspaar."""
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            kern, adaptiv = row
            parts: list[str] = []
            if kern:
                parts.append(f"Kern-Persönlichkeit: {kern}")
            if adaptiv:
                parts.append(f"Aktuelle Phase: {adaptiv}")
            logger.info(f"Charakter-Hash gefunden fuer Paar '{user_id}/{character_id}'")
            return "\n".join(parts)

        return ""

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Charakter-Hash Abruf fehlgeschlagen")
        return ""


def charakter_hash_retrieve_dict(postgres_url: str, user_id: str, character_id: str = "") -> dict:
    """Holt den Charakter-Hash als Dict fuer ein Gespraechspaar."""
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil "
            "FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "kern":              row[0] or "",
                "adaptiv":           row[1] or "",
                "beziehungsprofil":  row[2] or "",
                "intentions_profil": row[3] or "",
                "emotions_profil":   row[4] or "",
            }

        return {}

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Charakter-Hash-Dict Abruf fehlgeschlagen")
        return {}


def nova_charakter_hash_retrieve_dict(postgres_url: str, user_id: str) -> dict:
    """Laedt Novas Charakter-Hash fuer das Gespraech mit einem bestimmten User.

    Im Paar-Schema lebt Novas Charakter unter (ASSISTANT_USER_ID, user_id):
    ASSISTANT_USER_ID ist der Schreiber (Subjekt), user_id der Gegenueber.
    Diese Funktion macht die Argument-Reihenfolge logisch — ohne sie waere
    der Aufrufer auf den Vertausch von user_id und character_id angewiesen.

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: Liefert dict mit den fuenf Hash-Schichten oder {} bei
    fehlendem Datensatz.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nova_charakter_hash_retrieve_dict: user_id leer — verworfen")
        return {}

    # ── Verarbeitung ────────────────────────────
    return charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)


def nutzer_gewichtung_laden(postgres_url: str, user_id: str) -> tuple[float | None, str]:
    """Laedt Novas Gewichtung des Nutzers — den Faktor des Charakter-Rads.

    Gelesen wird die Zeile (ASSISTANT_USER_ID, user_id), also **Novas Zuwendung
    zum Nutzer**. Die Gegenzeile (user_id, ASSISTANT_USER_ID) traegt dieselben
    Spaltennamen und ist seine Zuwendung zu ihr — sie hat bewusst keinen
    Verbraucher. Wer sie laese, bekaeme die Gewichtung auf dem Kopf: Ein
    aufmerksamer Nutzer machte dann IHR Gedaechtnis empfaenglicher, obwohl
    ueber ihre Bereitschaft nichts gesagt waere
    (novaberg-salienz-berechnung_k.md §8, "Welche Zeile die Formel liest").

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: (faktor, quelle) mit faktor in [RAD_MIN, RAD_MAX] und quelle
        aus {'default', 'destilliert'}.
    Fehlerfaelle: leere user_id, fehlender Datensatz oder DB-Fehler — dann
        (None, 'fehlt'). Ausdruecklich NICHT (0.9, 'default'): Der Aufrufer
        muss "nie destilliert" von "nicht gelesen" unterscheiden koennen, sonst
        sieht ein Lesefehler aus wie ein Charakter ohne Auspraegung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nutzer_gewichtung_laden: user_id leer — verworfen")
        return None, "fehlt"

    # ── Verarbeitung ────────────────────────────
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nutzer_gewichtung, nutzer_gewichtung_quelle FROM charakter_hash "
            "WHERE user_id = %s AND character_id = %s",
            (ASSISTANT_USER_ID, user_id),
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: nutzer_gewichtung_laden: Abruf fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' fehlgeschlagen"
        )
        return None, "fehlt"

    if not row:
        logger.error(
            f"nutzer_gewichtung_laden: keine charakter_hash-Zeile fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' — Faktor nicht ermittelbar"
        )
        return None, "fehlt"

    faktor: float = float(row[0])
    quelle: str   = row[1] or "default"

    # ── Ausgabe-Verifikation ────────────────────
    # Die Destillation kappt bereits beim Schreiben. Greift die Pruefung hier
    # trotzdem, steht ein Wert in der Tabelle, den kein Rad erzeugt haben kann
    # — das gehoert benannt, nicht stillschweigend mitgerechnet.
    if not RAD_MIN <= faktor <= RAD_MAX:
        logger.warning(
            f"nutzer_gewichtung_laden: Faktor {faktor:.4f} ausserhalb "
            f"[{RAD_MIN}, {RAD_MAX}] fuer Paar '{ASSISTANT_USER_ID}/{user_id}' "
            f"— gekappt, Herkunft '{quelle}'"
        )
        faktor = max(RAD_MIN, min(RAD_MAX, faktor))

    logger.debug(
        f"nutzer_gewichtung_laden: {faktor:.4f} (Herkunft '{quelle}') "
        f"fuer Paar '{ASSISTANT_USER_ID}/{user_id}'"
    )
    return faktor, quelle


def _rad_flach_machen(roh: str, paar: str) -> tuple[dict[str, float] | None, str]:
    """Liest das Rad-JSON und legt beide Seiten zu einem flachen Rad zusammen.

    Steht als eigene Funktion, weil eine Waechterkette sonst die Zweigzahl
    ihres Aufrufers bestimmt: Der Lader soll laden, nicht auswerten. Die Zahl
    der Rueckgaben ist die Zahl der Vorbedingungen und folgt dem Datenmodell.

    Args:
        roh:  der Spalteninhalt, nicht leer. Pruefung erfolgt beim Aufrufer.
        paar: nur fuer die Meldungen, damit sie den Fall benennen.

    Returns:
        (rad, "") im Gutfall, sonst (None, grund) — der Grund im Klartext, mit
        dem Wert und nicht nur dem Feldnamen.
    """
    try:
        verschachtelt: dict = json.loads(roh)
    except (ValueError, TypeError) as fehler:
        return None, (
            f"JSON nicht lesbar fuer Paar '{paar}' ({type(fehler).__name__}) "
            f"— Rohwert: {roh[:120]!r}"
        )

    if not isinstance(verschachtelt, dict):
        return None, (
            f"Rad fuer Paar '{paar}' ist {type(verschachtelt).__name__}, "
            "erwartet wird ein Objekt mit den Seiten 'hoch' und 'runter'"
        )

    rad: dict[str, float] = {}
    for seite in ("hoch", "runter"):
        speichen = verschachtelt.get(seite)
        if not isinstance(speichen, dict):
            return None, (
                f"Seite {seite!r} fehlt oder ist {type(speichen).__name__} "
                f"im Rad zu Paar '{paar}' — verworfen"
            )
        for name, wert in speichen.items():
            # Ein Wahrheitswert ist in Python eine Zahl und rechnete stumm mit.
            if isinstance(wert, bool) or not isinstance(wert, (int, float)):
                return None, (
                    f"Speiche {name!r} traegt {wert!r} "
                    f"({type(wert).__name__}) im Paar '{paar}', erwartet wird "
                    "eine Zahl — verworfen"
                )
            rad[name] = float(wert)

    # Ein Name auf beiden Seiten haette beim Zusammenlegen einen Wert
    # verschluckt — lautlos, und das Rad saehe vollstaendig aus.
    erwartet: int = len(verschachtelt["hoch"]) + len(verschachtelt["runter"])
    if len(rad) != erwartet:
        return None, (
            f"{len(rad)} Speichen nach dem Zusammenlegen, erwartet waren "
            f"{erwartet} fuer Paar '{paar}' — ein Name kommt auf beiden Seiten "
            "vor, verworfen"
        )

    return rad, ""


def _neutrales_rad() -> dict[str, float]:
    """Das Rad eines Paares, ueber das noch nichts erhoben wurde.

    Zwoelf Speichen, alle auf 0.0 — **die anfaenglich vorurteilsfreie
    Haltung**, nicht ein fehlender Wert. Entschieden am 22.08.2026 zu
    `NEUER-NUTZER-OHNE-UMFANGSVORGABE`: Ohne dieses Rad bekam ein neuer
    Nutzer gar keine Haltung und damit keine Umfangsvorgabe — gemessen an
    fuenf frischen Kennungen **9 von 9 Turns ohne Regie**.

    **Die Speichennamen kommen aus der Destillation und werden hier nicht
    wiederholt.** Zwei Orte fuer dieselbe Namensliste driften auch dann, wenn
    heute niemand den zweiten liest; der Import steht deshalb in der Funktion
    und nicht im Modulkopf — dieselbe Bauart wie in `graph/nodes/verfasser.py`
    fuer `ei.dreischicht`, und aus demselben Grund: Der Speicher soll nicht
    beim Laden schon an einem Agenten haengen.

    Vorbedingung: keine.
    Nachbedingung: ein flaches Rad mit den Speichen beider Seiten, jede 0.0.
    """
    # ── Verarbeitung ────────────────────────────
    from agents.charakter.destillation import RAD_LEER

    # ── Ausgabe ─────────────────────────────────
    return {
        name: 0.0
        for seite in ("hoch", "runter")
        for name in RAD_LEER[seite]
    }


def nutzer_gewichtung_rad_laden(
    postgres_url: str, user_id: str,
) -> tuple[dict[str, float] | None, str]:
    """Laedt die zwoelf Speichen von Novas Zuwendung zum Nutzer.

    Die Schwester von `nutzer_gewichtung_laden`, die denselben Datensatz auf
    seinen Faktor reduziert. Der Haltungsraum braucht die Speichen selbst: Ein
    Faktor von 0.95 kann aus Wissbegier oder aus Pflicht entstanden sein, und
    die beiden wirken auf Umfang und Fragen verschieden
    (novaberg-haltungsraum_k.md §2).

    Gelesen wird dieselbe Zeile (ASSISTANT_USER_ID, user_id) und aus demselben
    Grund: Die Gegenzeile traegt SEINE Zuwendung zu ihr, und die sagt ueber
    ihre Haltung nichts.

    Args:
        postgres_url: Verbindungszeichenkette.
        user_id:      der Nutzer, dem ihre Zuwendung gilt.

    Returns:
        (rad, quelle) — `rad` flach als Speichenname -> Auspraegung ueber beide
        Seiten, `quelle` aus {'destilliert', 'default', 'neutral'}. Bei jedem
        **Lesefehler** (None, 'fehlt') und **nicht** ein leeres Rad: Ein Rad
        ohne Auspraegung ist eine Messung, ein nicht gelesenes ist keine. Wer
        beides gleich behandelt, laesst einen Lesefehler wie einen Charakter
        ohne Zuwendung aussehen.

    **Der dritte Fall ist seit dem 22.08.2026 keiner der beiden** (`NEUER-NUTZER-OHNE-UMFANGSVORGABE`):
        Wer noch **keine Zeile** hat, ist kein Lesefehler und keine Messung —
        er ist neu. Dafuer kommt das neutrale Rad zurueck, mit der eigenen
        Herkunft `'neutral'`. Die Begruendung ist keine technische: Ein Rad
        aus Nullen ist die **anfaenglich vorurteilsfreie Haltung** gegenueber
        einer Person, ueber die noch nichts erhoben wurde — nicht ein
        fehlender Wert, sondern der richtige.

        **Die Herkunft bleibt trotzdem unterscheidbar**, und das ist der Grund
        fuer den dritten Wert statt `'default'`: Ein gespeichertes Nullrad
        wurde erhoben und ergab nichts; ein neutrales wurde nie erhoben. Wer
        beides `'default'` nennt, kann spaeter nicht mehr zaehlen, wie viele
        Paare ueberhaupt schon einmal durch die Destillation gelaufen sind.

    Fehlerfaelle: leere user_id, leere Spalte, unlesbares JSON, fehlende
        Seite, nicht-numerische Auspraegung — je eine Meldung mit dem Wert und
        (None, 'fehlt'). Eine **fehlende Zeile** ist seit dem 22.08.2026
        keiner mehr, siehe oben.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nutzer_gewichtung_rad_laden: user_id leer — verworfen")
        return None, "fehlt"

    # ── Verarbeitung ────────────────────────────
    paar: str = f"{ASSISTANT_USER_ID}/{user_id}"
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nutzer_gewichtung_rad, nutzer_gewichtung_quelle "
            "FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (ASSISTANT_USER_ID, user_id),
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: nutzer_gewichtung_rad_laden: Abruf fuer "
            f"Paar '{paar}' fehlgeschlagen"
        )
        return None, "fehlt"

    if not row:
        # Kein Lesefehler, sondern ein neues Paar: Die neutrale Haltung ist
        # hier die richtige, nicht die fehlende (Entscheidung 22.08.2026).
        # `info` statt `error` — ein erster Turn ist kein Stoerfall, und die
        # Zeile bleibt trotzdem im Protokoll, weil die Herkunft eine Aussage
        # ueber die Antwort dieses Turns ist.
        logger.info(
            f"nutzer_gewichtung_rad_laden: keine charakter_hash-Zeile fuer Paar "
            f"'{paar}' — neutrales Rad, dieses Paar ist neu"
        )
        return _neutrales_rad(), "neutral"

    # `.get`-artige Defaults greifen hier nicht: Die Spalte kann NULL tragen,
    # und ein NULL ist etwas anderes als eine fehlende Zeile.
    roh: str | None = row[0]
    quelle: str     = row[1] or "default"
    if not roh:
        logger.error(
            f"nutzer_gewichtung_rad_laden: Spalte nutzer_gewichtung_rad ist leer "
            f"fuer Paar '{paar}', Herkunft '{quelle}' — Rad nicht ermittelbar"
        )
        return None, "fehlt"

    rad, grund = _rad_flach_machen(roh, paar)
    if rad is None:
        logger.error(f"nutzer_gewichtung_rad_laden: {grund}")
        return None, "fehlt"

    logger.debug(
        f"nutzer_gewichtung_rad_laden: {len(rad)} Speichen "
        f"(Herkunft '{quelle}') fuer Paar '{paar}'"
    )
    return rad, quelle


def initiative_versatz_laden(postgres_url: str, user_id: str) -> tuple[float | None, str]:
    """Laedt Novas Initiative-Versatz — den Wert des zweiten Charakter-Rads.

    Gelesen wird dieselbe Zeile wie beim ersten Rad: (ASSISTANT_USER_ID,
    user_id), also **Novas** Neigung, dem Nutzer die Fuehrung zu ueberlassen.
    Die Gegenzeile traegt seine Neigung und hat keinen Verbraucher; wer sie
    laese, verschoebe die Achse nach dem falschen Charakter.

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: (versatz, quelle) mit versatz in
        [-INITIATIVE_RAD_SPANNE, +INITIATIVE_RAD_SPANNE] und quelle aus
        {'default', 'destilliert'}.
    Fehlerfaelle: leere user_id, fehlender Datensatz oder DB-Fehler — dann
        (None, 'fehlt'). Ausdruecklich NICHT (0.0, 'default'): Ein Versatz von
        0.0 ist ein gueltiges Messergebnis (die Speichen heben sich auf), und
        ein Lesefehler darf nicht so aussehen.

    Returns:
        (Versatz oder None, Herkunft).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("initiative_versatz_laden: user_id leer — verworfen")
        return None, "fehlt"

    # ── Verarbeitung ────────────────────────────
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT initiative_versatz, initiative_versatz_quelle FROM charakter_hash "
            "WHERE user_id = %s AND character_id = %s",
            (ASSISTANT_USER_ID, user_id),
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: initiative_versatz_laden: Abruf fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' fehlgeschlagen"
        )
        return None, "fehlt"

    if not row:
        logger.error(
            f"initiative_versatz_laden: keine charakter_hash-Zeile fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' — Versatz nicht ermittelbar"
        )
        return None, "fehlt"

    versatz: float = float(row[0])
    quelle:  str   = row[1] or "default"

    # ── Ausgabe-Verifikation ────────────────────
    # Die Destillation kappt beim Schreiben. Greift die Pruefung hier trotzdem,
    # steht ein Wert in der Tabelle, den kein Rad erzeugt haben kann.
    if not -INITIATIVE_RAD_SPANNE <= versatz <= INITIATIVE_RAD_SPANNE:
        logger.warning(
            f"initiative_versatz_laden: Versatz {versatz:+.4f} ausserhalb "
            f"+/-{INITIATIVE_RAD_SPANNE} fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' — gekappt, Herkunft '{quelle}'"
        )
        versatz = max(-INITIATIVE_RAD_SPANNE, min(INITIATIVE_RAD_SPANNE, versatz))

    logger.debug(
        f"initiative_versatz_laden: {versatz:+.4f} (Herkunft '{quelle}') "
        f"fuer Paar '{ASSISTANT_USER_ID}/{user_id}'"
    )
    return versatz, quelle
