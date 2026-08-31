"""Praegungsschicht — Faeden und ihre Beruehrungen.

Die dritte Charakterschicht neben dem Zuwendungs-Rad (relational) und den
Werte-Knoten (normativ): Sie ist **thematisch**. Ein Faden ist ein
einschneidendes, embeddingbezogenes Ereignis.

Konzept: `novaberg-thinking-faszination_k.md` §7.

**Die tragende Unterscheidung gegenueber dem LZG:** Das LZG ist auf Vergessen
ausgerichtet, die Praegung auf Intensitaet. Dort waechst das Gewicht durch
Wiederverwendung; hier wird die Intensitaet im Moment des Erlebens vergeben und
**nie ueberboten** — Wiedererinnern macht *Star Wars 1977* nicht intensiver, es
haelt die Episode frisch.
"""

import logging
import math

import psycopg2

from config import (
    PRAEGUNG_TOR_AUSSCHLAG,
    PRAEGUNG_TOR_SALIENZ,
)

logger = logging.getLogger("ki_server.praegung")

HERKUNFT_KANON: frozenset[str] = frozenset({"erlebt", "bewertet", "geschlossen"})
AUSGANG_KANON:  frozenset[str] = frozenset({"offen", "erfolg", "misserfolg"})


def ausschlag_absolut_berechnen(ausschlag_eingang: float) -> float:
    """Formt den Eingangswert eines Fadens ueber die Formkurve.

    Eigene Funktion, weil die Kurve sonst nur hinter einem Schreibpfad
    erreichbar waere — ein Zeuge muesste sie dann nachrechnen statt aufrufen und
    bliebe gruen, wenn sich die echte Rechnung aendert (Fundliste 30.08.2026).

    Die Kurve ist `sin(x * pi/2) ** 2`: punktsymmetrisch um 0,5, Abflachung an
    **beiden** Enden, Trennschaerfe im Bereich 0,5–0,8, wo die meisten Faeden
    liegen werden. **Der Exponent weicht bewusst vom `sin^0.5` der Faszination
    ab** (§10.6): Dort entsteht der Wert aus einem Produkt vieler Faktoren und
    soll auch schwach sichtbar werden, hier aus einem einzelnen Erlebnis und
    soll trennen. Der Preis steht im Konzept und ist bezahlt: zwischen 0,9 und
    1,0 bleiben nur 0,024 Unterschied.

    Kein MAXIMUM, kein Cap: Der Eingang laeuft auf die volle Skala, weil er die
    volle Skala **ist**.

    Args:
        ausschlag_eingang: Emotionsstaerke bei Entstehung, [0,1].

    Returns:
        Geformter Wert auf [0,1].

    Raises:
        ValueError: Wenn der Eingang ausserhalb von [0,1] liegt.
    """
    # ── Eingabe ────────────────────────────────
    if not 0.0 <= ausschlag_eingang <= 1.0:
        raise ValueError(
            f"ausschlag_eingang={ausschlag_eingang} liegt ausserhalb [0,1] — "
            f"die Formkurve setzt die volle Skala voraus, und ein Wert darueber "
            f"hiesse, dass die liefernde Groesse eine andere Skala hat"
        )

    # ── Verarbeitung ───────────────────────────
    return math.sin(ausschlag_eingang * math.pi / 2) ** 2


def tor_urteil(salienz: float, ausschlag: float) -> tuple[bool, str]:
    """Entscheidet, ob ein Turn einen Faden hinterlaesst.

    **Zwei Bedingungen, und Arousal ist keine davon** (§7.3): hohe Salienz und
    hoher Emotionsausschlag. Der EI-Arousal ist ein Mischwert (Dynamik 0,40,
    Intent 0,35, Tone 0,25) und schleppte Beziehungsdynamik in ein Tor, das von
    Themenbindung handelt; er steckt ohnehin im Emotionswert, weil der Decay des
    Verlaufs arousal-abhaengig ist.

    **Das Tor traegt die volle Last** — es ist das einzige, was die Fadenkarte
    von *jeder Turn ist ein Faden* trennt.

    Args:
        salienz: Erinnerungswuerdigkeit des Turns, [0,1].
        ausschlag: Staerke der fuehrenden Emotion, [0,1].

    Returns:
        (durchgelassen, Grund) — der Grund wird protokolliert, auch bei Nein.
    """
    if salienz < PRAEGUNG_TOR_SALIENZ:
        return False, f"salienz {salienz:.2f} < {PRAEGUNG_TOR_SALIENZ}"
    if ausschlag < PRAEGUNG_TOR_AUSSCHLAG:
        return False, f"ausschlag {ausschlag:.2f} < {PRAEGUNG_TOR_AUSSCHLAG}"
    return True, f"salienz {salienz:.2f}, ausschlag {ausschlag:.2f}"


def faden_anlegen(
    postgres_url: str,
    *,
    user_id: str,
    character_id: str,
    emotion: str,
    ausschlag_eingang: float,
    embedding_str: str | None = None,
    turn_id: str | None = None,
    herkunft: str = "erlebt",
    beobachter: str = "assistant",
) -> int | None:
    """Legt einen Faden an und gibt seine Kennung zurueck.

    **Alle Faeden werden geschrieben** (§7.6). Ein frueherer Entwurf sah
    Verdraengung im Umkreis vor; das ist pfadabhaengig und nicht idempotent —
    drei Faeden in Kettenabstand ergaeben je nach Reihenfolge verschiedene
    Bestaende. Zwanzig Faeden in einem engen Bereich sind kein Problem, sondern
    der **Beleg** fuer einen starken Strang.

    Vorbedingung: `herkunft` aus dem Kanon; `geschlossen` ohne `turn_id`, weil
    an der `turn_id` die Grenze der Rueckwirkung verlaeuft (§7.5).
    Nachbedingung: Eine Zeile in `praegung_faden`, deren `ausschlag_aktuell`
    gleich `ausschlag_absolut` ist — die Faltung beginnt beim Ursprungswert.

    Args:
        postgres_url: Verbindung.
        user_id: Subjekt der Praegung.
        character_id: Gegenueber.
        emotion: Kanonischer Sektor.
        ausschlag_eingang: Emotionsstaerke bei Entstehung, [0,1].
        embedding_str: Ort auf der Themenlandkarte, als pgvector-Literal.
        turn_id: Rueckbezug auf die Quelle.
        herkunft: erlebt | bewertet | geschlossen.
        beobachter: Schreiber der Zeile.

    Returns:
        Die Kennung des Fadens, oder None bei verletzter Vorbedingung.
    """
    # ── Eingabe ────────────────────────────────
    if herkunft not in HERKUNFT_KANON:
        logger.error(
            f"Praegung: Faden abgelehnt — herkunft='{herkunft}' nicht im Kanon "
            f"{sorted(HERKUNFT_KANON)}; user_id={user_id}, character_id={character_id}"
        )
        return None

    if not user_id or not character_id:
        logger.error(
            f"Praegung: Faden abgelehnt — Paar unvollstaendig "
            f"(user_id='{user_id}', character_id='{character_id}'). Eine Praegung "
            f"ist Novas Eigenschaft gegenueber jemandem, nicht global"
        )
        return None

    if not emotion or emotion == "neutral":
        logger.error(
            f"Praegung: Faden abgelehnt — emotion='{emotion}'. Ein Faden ohne "
            f"besetzten Sektor traegt kein Histogramm und keinen Verfall"
        )
        return None

    try:
        ausschlag_absolut: float = ausschlag_absolut_berechnen(ausschlag_eingang)
    except ValueError as fehler:
        logger.error(f"Praegung: Faden abgelehnt — {fehler}")
        return None

    # ── Verarbeitung ───────────────────────────
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO praegung_faden
                    (user_id, character_id, beobachter, turn_id, embedding,
                     emotion, ausschlag_eingang, ausschlag_absolut,
                     ausschlag_aktuell, herkunft)
                VALUES (%s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, character_id, beobachter, turn_id, embedding_str,
                 emotion, ausschlag_eingang, ausschlag_absolut,
                 ausschlag_absolut, herkunft),
            )
            faden_id: int = cur.fetchone()[0]
    except Exception as fehler:
        logger.error(
            f"Praegung: Faden nicht geschrieben — {fehler}; user_id={user_id}, "
            f"character_id={character_id}, emotion={emotion}"
        )
        return None

    # ── Ausgabe ────────────────────────────────
    logger.info(
        f"Praegung: Faden {faden_id} angelegt — {emotion}, "
        f"eingang={ausschlag_eingang:.2f} -> absolut={ausschlag_absolut:.3f}, "
        f"herkunft={herkunft}, turn={turn_id or 'ohne'}"
    )
    return faden_id


def beruehrung_anlegen(postgres_url: str, faden_id: int, quelle: str) -> bool:
    """Haelt eine Reaktivierung fest.

    Die Zeile ist der Rohstoff der Faltung: `ausschlag_aktuell` wird aus der
    Beruehrungstabelle gerechnet, nicht fortgeschrieben. Damit bleiben Alpha und
    Halbstrecke Parameter eines **Laufs**, nicht eines Schreibvorgangs.

    Args:
        postgres_url: Verbindung.
        faden_id: Der beruehrte Faden.
        quelle: Was die Reaktivierung ausgeloest hat.

    Returns:
        True, wenn die Zeile steht.
    """
    # ── Eingabe ────────────────────────────────
    if not quelle:
        logger.error(
            f"Praegung: Beruehrung abgelehnt — ohne Quelle waere im Nachhinein "
            f"nicht zu sagen, was den Faden {faden_id} aufgefrischt hat"
        )
        return False

    # ── Verarbeitung ───────────────────────────
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO praegung_beruehrung (faden_id, quelle) VALUES (%s, %s)",
                (faden_id, quelle),
            )
    except Exception as fehler:
        logger.error(f"Praegung: Beruehrung nicht geschrieben — {fehler}")
        return False

    # ── Ausgabe ────────────────────────────────
    return True
