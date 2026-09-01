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
from datetime import datetime, timezone

import psycopg2

from config import (
    PRAEGUNG_ALPHA,
    PRAEGUNG_BODEN,
    PRAEGUNG_HALBSTRECKE,
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


def _verfall(tage: float, boden: float, halbstrecke: float) -> float:
    """Der relative Anteil nach `tage` ohne Beruehrung.

    **Hyperbolisch, nicht exponentiell** (Konzept §7.4): Die Form hat den fetten
    Schwanz, den Vergessenskurven zeigen — ein Faden faellt schnell aus der
    Frische und danach immer langsamer. Exponentiell waere die Alternative und
    ist nicht durchgerechnet; der offene Punkt steht im Konzept.

    Nachbedingung: Wert in (boden, 1.0]. **Der Boden wird nie unterschritten** —
    ein Faden wird leiser, nie deaktiviert.
    """
    return boden + (1.0 - boden) / (1.0 + max(0.0, tage) / halbstrecke)


def _verfall_umkehren(anteil: float, boden: float, halbstrecke: float) -> float:
    """Wie viele Tage Verfall zu diesem Anteil gehoeren.

    Die Umkehrung von `_verfall`. Sie wird gebraucht, weil eine Beruehrung den
    Anteil **anhebt** und der Verfall danach dort weiterlaufen muss, wo der
    angehobene Wert steht — nicht dort, wo die Uhr steht.

    Nachbedingung: Tage >= 0. Ein Anteil auf oder unter dem Boden liefert eine
    grosse, aber endliche Zahl statt einer Division durch null.
    """
    spanne: float = anteil - boden
    if spanne <= 1e-9:
        return halbstrecke * 1e6
    return halbstrecke * ((1.0 - boden) / spanne - 1.0)


def ausschlag_aktuell_falten(
    ausschlag_absolut: float,
    entstanden_am:     datetime,
    beruehrungen:      list[datetime],
    jetzt:             datetime,
    alpha:             float,
    halbstrecke:       float,
    boden:             float,
) -> float:
    """Rechnet `ausschlag_aktuell` aus der Beruehrungsliste — von Grund auf.

    **Keine Fortschreibung.** Der Wert wird bei jedem Aufruf aus dem Eingang und
    der Ereignisliste neu gefaltet, ohne Kenntnis des vorigen. Damit bleiben
    Alpha, Halbstrecke und Boden Parameter eines **Laufs** und nicht eines
    Schreibvorgangs: Wer sie spaeter aendert, bekommt eine andere Kurve auf
    denselben Daten — statt eines Bestands, dessen alte Zeilen etwas anderes
    bedeuten als seine neuen (Konzept §7.2, §7.4).

    **Eine Beruehrung fuellt die Luecke, sie setzt nicht zurueck.** Ein voller
    Reset machte das Beruehrungsintervall bedeutungslos; die Auffuellung hebt
    proportional zu dem, was noch da war.

    **Der Wert kann `ausschlag_absolut` nie ueberschreiten** — kein Akkumulator,
    kein Deckel noetig. Wiedererinnern macht nicht intensiver.

    Vorbedingung: `beruehrungen` sind Zeitpunkte nach `entstanden_am`; die
    Reihenfolge stellt die Funktion selbst her.
    Nachbedingung: Wert in [ausschlag_absolut × boden, ausschlag_absolut].
    Fehlerfaelle: Keine — eine leere Liste ist der Regelfall und ergibt den
    reinen Verfall.

    Args:
        ausschlag_absolut: Der Eingangswert des Fadens.
        entstanden_am: Wann der Faden entstand.
        beruehrungen: Die Zeitpunkte der Reaktivierungen.
        jetzt: Der Bezugszeitpunkt der Rechnung.
        alpha: Auffuellgrad je Beruehrung.
        halbstrecke: Halbwertszeit des Verfalls in Tagen.
        boden: Anteil, unter den nicht gefallen wird.

    Returns:
        Der gefaltete Ausschlag.
    """
    # ── Eingabe-Validierung ─────────────────────
    anteil: float = 1.0
    letzt:  datetime = entstanden_am

    # ── Verarbeitung ───────────────────────────
    for beruehrt_am in sorted(beruehrungen):
        if beruehrt_am <= letzt:
            # Eine Beruehrung vor der Entstehung ist ein Datenfehler, kein
            # Sonderfall: Sie wuerde negative Tage in den Verfall tragen.
            logger.error(
                f"Praegung: Beruehrung {beruehrt_am.isoformat()} liegt nicht "
                f"nach {letzt.isoformat()} — uebersprungen, die Faltung laeuft "
                f"ohne sie weiter"
            )
            continue
        tage: float = (beruehrt_am - letzt).total_seconds() / 86400.0
        anteil = _verfall(
            _verfall_umkehren(anteil, boden, halbstrecke) + tage, boden, halbstrecke,
        )
        anteil = anteil + alpha * (1.0 - anteil)
        letzt = beruehrt_am

    rest_tage: float = (jetzt - letzt).total_seconds() / 86400.0
    anteil = _verfall(
        _verfall_umkehren(anteil, boden, halbstrecke) + rest_tage, boden, halbstrecke,
    )

    # ── Ausgabe-Verifikation ────────────────────
    return ausschlag_absolut * min(1.0, max(boden, anteil))


def ausschlag_aktuell_nachfuehren(
    postgres_url: str,
    faden_ids:    list[int],
    jetzt:        datetime | None = None,
) -> int:
    """Rechnet `ausschlag_aktuell` der genannten Faeden neu und schreibt ihn.

    **Der Aufrufer, der `ausschlag_aktuell_falten` gefehlt hat.** Die Faltung war
    seit dem 01.09.2026 gebaut und gegen 18 Stuetzstellen des Konzepts bezeugt —
    und wurde von nirgends gerufen (`FALTUNG-OHNE-AUFRUFER`). Vier Beruehrungen
    entstanden im Betrieb, und der Wert, den sie haetten bewegen sollen, stand
    unveraendert auf `ausschlag_absolut`.

    **Von Grund auf, nicht fortgeschrieben.** Gelesen werden `ausschlag_absolut`,
    `entstanden_am` und die vollstaendige Beruehrungsliste; der vorige Wert der
    Spalte geht in die Rechnung nicht ein. Damit ist die Spalte ein
    **materialisiertes Ergebnis** im Sinne von `novaberg-convention-abgeleitete-werte.md`
    Regel 1 — zusaetzlich gespeichert, nie anstelle der Eingaben — und ein
    Wiederholungslauf ueber den ganzen Bestand ist ein zulaessiger
    Wartungsvorgang (Regel 4).

    **Deshalb steht sie ausserhalb der Transaktion, die die Beruehrung schreibt.**
    Faellt sie aus, fehlt kein Ereignis: Die Beruehrungszeile steht, und der
    naechste Lauf holt den Wert nach. Waere sie Teil derselben Transaktion,
    naehme ihr Fehler die Beruehrung mit — ein Rechenfehler wuerde Gedaechtnis
    loeschen.

    **Was sie nicht leistet: den Verfall zwischen zwei Beruehrungen.** Der Wert
    steht danach auf dem Stand seiner letzten Beruehrung und altert in der
    Spalte nicht mit. Wer den heutigen Wert braucht, ruft diese Funktion —
    ein periodischer Lauf ueber den Bestand ist der offene Rest
    (`FALTUNG-OHNE-PERIODISCHEN-LAUF`).

    Vorbedingung: `faden_ids` sind bestehende Zeilen; unbekannte werden still
    uebergangen, weil eine geloeschte Praegung kein Fehler ist.
    Nachbedingung: Je genanntem Faden ein `ausschlag_aktuell` in
    [`ausschlag_absolut` x `PRAEGUNG_BODEN`, `ausschlag_absolut`].
    Fehlerfaelle: Ein Datenbankfehler wird gemeldet und liefert 0; der Aufrufer
    laeuft weiter, der Wert bleibt auf seinem vorigen Stand.

    Args:
        postgres_url: Verbindung.
        faden_ids: Die Faeden, deren Wert neu zu rechnen ist.
        jetzt: Bezugszeitpunkt der Rechnung; ohne Angabe die aktuelle Zeit.

    Returns:
        Die Zahl der geschriebenen Zeilen.
    """
    # ── Eingabe-Validierung ─────────────────────
    ids: list[int] = sorted({int(f) for f in faden_ids})
    if not ids:
        return 0
    bezug: datetime = jetzt or datetime.now(timezone.utc)

    # ── Verarbeitung ───────────────────────────
    geschrieben: int = 0
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT f.id, f.ausschlag_absolut, f.entstanden_am,
                       coalesce(
                           array_agg(b.beruehrt_am ORDER BY b.beruehrt_am)
                           FILTER (WHERE b.beruehrt_am IS NOT NULL),
                           '{}'
                       )
                FROM praegung_faden f
                LEFT JOIN praegung_beruehrung b ON b.faden_id = f.id
                WHERE f.id = ANY(%s)
                GROUP BY f.id
                """,
                (ids,),
            )
            zeilen = cur.fetchall()
            for faden_id, absolut, entstanden_am, beruehrungen in zeilen:
                wert: float = ausschlag_aktuell_falten(
                    ausschlag_absolut = float(absolut),
                    entstanden_am     = entstanden_am,
                    beruehrungen      = list(beruehrungen or []),
                    jetzt             = bezug,
                    alpha             = PRAEGUNG_ALPHA,
                    halbstrecke       = PRAEGUNG_HALBSTRECKE,
                    boden             = PRAEGUNG_BODEN,
                )
                cur.execute(
                    "UPDATE praegung_faden SET ausschlag_aktuell = %s WHERE id = %s",
                    (wert, int(faden_id)),
                )
                geschrieben += 1
    except Exception as fehler:
        logger.exception(
            f"Praegung: Nachfuehrung ausgefallen ({type(fehler).__name__}) — "
            f"{len(ids)} Faden/Faeden behalten ihren vorigen `ausschlag_aktuell`; "
            f"der Wert ist jederzeit neu rechenbar, es fehlt kein Ereignis"
        )
        return 0

    # ── Ausgabe-Verifikation ────────────────────
    # Die Differenz zwischen genannten und geschriebenen Zeilen ist kein
    # Fehler, aber sie gehoert benannt: Sonst waere eine geloeschte Praegung
    # von einer nicht gerechneten nicht zu unterscheiden.
    if geschrieben < len(ids):
        logger.info(
            "Praegung: %d von %d Faden/Faeden nachgefuehrt — die uebrigen "
            "gibt es nicht mehr", geschrieben, len(ids),
        )
    return geschrieben


def beruehrung_aus_reaktivierung(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    kandidaten:   list[tuple[str, list[float]]],
    schwelle:     float,
) -> list[tuple[str, int, float]]:
    """Frischt Faeden auf, die einer reaktivierten Erinnerung nahe stehen.

    **Der thematische Andockweg** (Konzept §7.12). Ein Faden traegt das
    Embedding seines Segments; eine reaktivierte Erinnerung traegt ihres. Liegen
    sie nah genug beieinander, ist die Erinnerung dieselbe Sache — und der Faden
    wird aufgefrischt statt zu verblassen.

    **Die Funktion nimmt Vektoren, keine Kennungen.** Bis zum 01.09.2026 nahm
    sie LZG-Knoten-IDs und holte das Embedding per JOIN aus `lzg_knoten`. Damit
    erreichte sie **den haeufigsten Fall nicht**: `[gemessen]` an diesem Tag
    kamen ueber sieben Betriebsturns eines jungen Paars **alle** aktivierten
    Gravitationspunkte aus dem **Kurzzeitgedaechtnis** — dort steht das
    Embedding in Redis, nicht in der Tabelle. Die Begruendung *„eine
    KZG-Reaktivierung hat kein Embedding"* war falsch; sie hat eines, nur an
    einem anderen Ort. Wer den Vektor beschafft, weiss, woher er kommt — diese
    Funktion muss es nicht wissen.

    **Je Kandidat hoechstens ein Faden, und zwar der naechste.** Eine
    Reaktivierung, die zwei Faeden auffrischt, verdoppelt ein Ereignis; die
    Auffuellregel (§7.4) zaehlt Ereignisse, nicht Aehnlichkeiten.

    **Der strukturelle Andockweg fehlt weiterhin.** §7.12 nennt zwei — thematische
    Naehe und geteilte Qualitaets- oder Wert-Kante. Der zweite braucht die
    abstrakte Schicht, und `lzg_knoten_haltung` traegt null Zeilen. Ferne
    Uebertragungen (*Machtlosigkeit → Waffen*) sind heute nicht moeglich, nur
    nahe (*SciFi-Episode → Heimcomputer*).

    Vorbedingung: `kandidaten` sind (Quellenkennung, Vektor)-Paare; die Kennung
    wandert unveraendert in `praegung_beruehrung.quelle`.
    Nachbedingung: Je getroffenem Faden eine Zeile in `praegung_beruehrung`.
    Rueckgabe ist die Liste (Kennung, Faden-ID, Aehnlichkeit) — **auch fuer die
    Auswertung gedacht**: Ohne sie waere nicht zu sagen, ob eine Reihe ohne
    Beruehrungen an der Schwelle lag oder daran, dass es keine Faeden gibt.
    Fehlerfaelle: Ein Datenbankfehler wird gemeldet und liefert eine leere
    Liste; der Turn laeuft weiter, die Auffrischung faellt aus.

    Args:
        postgres_url: Verbindung.
        user_id: Subjekt des Paars.
        character_id: Gegenueber des Paars.
        kandidaten: Die reaktivierten Erinnerungen als (Kennung, Vektor).
        schwelle: Mindestaehnlichkeit, ab der ein Faden als getroffen gilt.

    Returns:
        Die angelegten Beruehrungen als (Kennung, Faden-ID, Aehnlichkeit).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        return []
    if not user_id or not character_id:
        logger.error(
            f"Praegung: Beruehrung ohne vollstaendiges Paar abgelehnt — "
            f"user_id={user_id!r}, character_id={character_id!r}; eine Praegung "
            f"gehoert einer Beziehung, nicht dem System"
        )
        return []

    # ── Verarbeitung ───────────────────────────
    treffer: list[tuple[str, int, float]] = []
    # **Auch die knappste Verfehlung wird gemeldet.** Eine Reihe ohne
    # Beruehrungen sagt sonst nicht, ob die Schwelle um 0,01 oder um 0,30
    # verfehlt wurde — und genau daran haengt, ob sie zu hoch steht.
    verfehlt: list[tuple[str, int, float]] = []
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            for kennung, vektor in kandidaten:
                if not vektor:
                    logger.error(
                        f"Praegung: Reaktivierung '{kennung}' ohne Vektor — "
                        f"uebersprungen; ohne ihn ist keine Naehe zu rechnen"
                    )
                    continue
                vektor_str: str = "[" + ",".join(str(x) for x in vektor) + "]"
                cur.execute(
                    """
                    SELECT id, 1 - (embedding <=> %s::vector) AS naehe
                    FROM praegung_faden
                    WHERE user_id = %s AND character_id = %s
                      AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT 1
                    """,
                    (vektor_str, user_id, character_id, vektor_str),
                )
                zeile = cur.fetchone()
                if zeile is None:
                    continue
                faden_id, naehe = int(zeile[0]), float(zeile[1])
                verfehlt.append((kennung, faden_id, naehe))
                if naehe < schwelle:
                    continue
                cur.execute(
                    "INSERT INTO praegung_beruehrung (faden_id, quelle) "
                    "VALUES (%s, %s)",
                    (faden_id, kennung),
                )
                treffer.append((kennung, faden_id, naehe))
    except Exception as fehler:
        logger.exception(
            f"Praegung: Auffrischung ausgefallen ({type(fehler).__name__}) — "
            f"{len(kandidaten)} Reaktivierung(en) ohne Wirkung auf die Faeden"
        )
        return []

    # Die Beruehrung allein bewegt nichts — erst die Faltung traegt sie in den
    # Wert. **Ausserhalb der Transaktion oben**, weil sie jederzeit
    # wiederholbar ist: Ein Fehler hier darf die geschriebene Beruehrung nicht
    # mitnehmen (siehe `ausschlag_aktuell_nachfuehren`).
    if treffer:
        ausschlag_aktuell_nachfuehren(
            postgres_url, [faden_id for _k, faden_id, _n in treffer],
        )

    # ── Ausgabe-Verifikation ────────────────────
    if treffer:
        logger.info(
            "Praegung: %d von %d Reaktivierung(en) haben einen Faden getroffen — %s",
            len(treffer), len(kandidaten),
            ", ".join(f"{k} -> Faden {f} ({n:.3f})" for k, f, n in treffer),
        )
    else:
        naechste: str = (
            "; naechste: " + ", ".join(
                f"{k} -> Faden {f} ({n:.3f})"
                for k, f, n in sorted(verfehlt, key=lambda x: -x[2])[:3]
            )
            if verfehlt else " (kein Faden im Paar)"
        )
        logger.info(
            "Praegung: keine der %d Reaktivierung(en) traf einen Faden "
            "(Schwelle %.2f)%s", len(kandidaten), schwelle, naechste,
        )
    return treffer


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

    # **Beide Schreibwege falten, nicht nur der eine.** Am 01.09.2026 bekam
    # `beruehrung_aus_reaktivierung` die Nachfuehrung; dieser zweite Weg haette
    # sie nicht gehabt, und derselbe Defekt stuende an einer anderen Tuer. Wer
    # heute keinen Aufrufer hat, bekommt morgen einen — und dann ohne Wirkung.
    ausschlag_aktuell_nachfuehren(postgres_url, [faden_id])

    # ── Ausgabe ────────────────────────────────
    return True
