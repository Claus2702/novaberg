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
    EMOTION_SEKTOR_MAP,
    PRAEGUNG_ALPHA,
    PRAEGUNG_BODEN,
    PRAEGUNG_HALBSTRECKE,
    PRAEGUNG_STRANG_NAEHE,
    PRAEGUNG_TOR_AUSSCHLAG,
    PRAEGUNG_TOR_SALIENZ,
    SEKTOR_GRUPPE,
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

    # Der Strang, **ausserhalb** der Transaktion oben und mit eigenem
    # Fehlerpfad: Die Zuordnung ist eine Rechnung und wiederholbar, das Anlegen
    # des Fadens ist ein Ereignis und nicht. Faellt sie aus, bleibt
    # `strang_id` NULL und `faeden_ohne_strang_zuordnen` holt sie nach — der
    # Faden geht dabei nie verloren (§7.7, dieselbe Entscheidung wie bei der
    # Faltung in §7.4).
    strang_zuordnen(postgres_url, faden_id)

    return faden_id


def _vektor_lesen(roh: str | None) -> list[float] | None:
    """Wandelt ein pgvector-Literal in eine Liste.

    pgvector liefert `'[0.1,0.2,...]'` als Text; psycopg2 kennt den Typ nicht.
    Ein unlesbarer Wert ist ein Fehler und kein Leerfall — er wird gemeldet und
    fuehrt zum Ausfall der Zuordnung, nicht zu einem Nullvektor.
    """
    if not roh:
        return None
    try:
        return [float(t) for t in roh.strip().strip("[]").split(",")]
    except (AttributeError, ValueError) as fehler:
        logger.error(f"Praegung: Vektor unlesbar — {fehler}")
        return None


def _vektor_schreiben(werte: list[float]) -> str:
    """Das pgvector-Literal zu einer Liste."""
    return "[" + ",".join(f"{w:.8f}" for w in werte) + "]"


def strang_zuordnen(postgres_url: str, faden_id: int) -> int | None:
    """Ordnet einen Faden dem naechstliegenden Strang zu oder gruendet einen.

    Konzept §7.7. **Der Strang ist die groessere Runde auf der Themenlandkarte:**
    Faeden, die beieinanderliegen, gehoeren zusammen, und zwanzig Faeden in
    einem engen Bereich sind nicht redundant, sondern der Beleg fuer einen
    starken Strang (§7.6).

    **Das Zentroid wird fortgeschrieben, nicht neu gerechnet.** `zentroid_neu =
    (zentroid × n + faden) / (n + 1)` — mathematisch dasselbe wie das Mittel
    ueber alle n+1 Vektoren, aber ohne Tabellenscan je Turn. Der Divisor ist
    `faden_zahl`, und das ist **Zeilenzahl und ausdruecklich nicht Anlaesse**:
    Die Staerke zaehlt spaeter Anlaesse (§7.7), diese Spalte traegt den
    Mittelwert und sonst nichts.

    **Die Zuordnung ist reihenfolgeabhaengig, und das ist hier zulaessig.**
    §7.6 verwarf die Verdraengung genau deswegen — dort war die Reihenfolge
    beliebig. Hier ist sie **die Zeit**: Ein Faden trifft auf die Straenge, die
    es bei seiner Entstehung gab. Der Nachzug haelt sich daran
    (`faeden_ohne_strang_zuordnen` sortiert nach `entstanden_am`), sonst
    entstuende bei jedem Lauf ein anderer Bestand.

    Vorbedingung: `faden_id` bezeichnet eine Zeile mit Embedding. Ein Faden
        ohne Vektor hat keinen Ort und bekommt keinen Strang — er behaelt
        `strang_id = NULL` und wird beim naechsten Nachzug wieder betrachtet.
    Nachbedingung: `praegung_faden.strang_id` zeigt auf einen Strang desselben
        Paares, dessen `faden_zahl` und `letzter_faden` den Beitritt tragen.
    Fehlerfaelle: Jeder Fehlschlag laesst `strang_id` auf NULL und meldet mit
        Spur. **Ein Faden ohne Strang ist ein wiederholbarer Zustand, ein
        verlorener Faden nicht** — deshalb laeuft diese Funktion ausserhalb der
        Transaktion, die den Faden schreibt (dieselbe Entscheidung wie bei der
        Faltung, §7.4).

    Args:
        postgres_url: Verbindung.
        faden_id: der Faden, der seinen Strang sucht.

    Returns:
        Die Kennung des Strangs, oder None wenn keiner zugeordnet wurde.
    """
    # ── Eingabe ────────────────────────────────
    if faden_id is None or faden_id <= 0:
        logger.error(f"Praegung: Strangzuordnung abgelehnt — faden_id={faden_id}")
        return None

    beigetreten: bool = False
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, character_id, beobachter, embedding::text,
                       entstanden_am, strang_id
                FROM praegung_faden WHERE id = %s
                """,
                (faden_id,),
            )
            zeile = cur.fetchone()
            if zeile is None:
                logger.error(f"Praegung: Faden {faden_id} nicht gefunden")
                return None

            user_id, character_id, beobachter, emb_roh, entstanden_am, vorhandener = zeile

            if vorhandener is not None:
                logger.info(
                    f"Praegung: Faden {faden_id} traegt bereits Strang "
                    f"{vorhandener} — unveraendert"
                )
                return vorhandener

            faden_vektor: list[float] | None = _vektor_lesen(emb_roh)
            if faden_vektor is None:
                logger.warning(
                    f"Praegung: Faden {faden_id} ohne Embedding — kein Ort auf der "
                    f"Landkarte, kein Strang. Bleibt fuer den Nachzug offen"
                )
                return None

            # ── Verarbeitung ───────────────────────────
            # Der naechste Strang desselben Paares. `<=>` ist die
            # Kosinus-Distanz; 1 - d ist die Aehnlichkeit, auf der die Schwelle
            # steht — dieselbe Rechnung wie bei der Reaktivierung.
            cur.execute(
                """
                SELECT id, zentroid::text, faden_zahl,
                       1 - (zentroid <=> %s::vector) AS naehe
                FROM praegung_strang
                WHERE user_id = %s AND character_id = %s AND beobachter = %s
                ORDER BY naehe DESC
                LIMIT 1
                """,
                (_vektor_schreiben(faden_vektor), user_id, character_id, beobachter),
            )
            treffer = cur.fetchone()

            if treffer is not None and treffer[3] >= PRAEGUNG_STRANG_NAEHE:
                strang_id, zentroid_roh, faden_zahl, naehe = treffer
                zentroid: list[float] | None = _vektor_lesen(zentroid_roh)
                if zentroid is None or len(zentroid) != len(faden_vektor):
                    logger.error(
                        f"Praegung: Zentroid von Strang {strang_id} unbrauchbar "
                        f"(Laenge {len(zentroid) if zentroid else 'None'} gegen "
                        f"{len(faden_vektor)}) — Faden {faden_id} bleibt offen"
                    )
                    return None

                neues_zentroid: list[float] = [
                    (alt * faden_zahl + neu) / (faden_zahl + 1)
                    for alt, neu in zip(zentroid, faden_vektor, strict=True)
                ]
                cur.execute(
                    """
                    UPDATE praegung_strang
                       SET zentroid = %s::vector,
                           faden_zahl = faden_zahl + 1,
                           letzter_faden = GREATEST(letzter_faden, %s)
                     WHERE id = %s
                    """,
                    (_vektor_schreiben(neues_zentroid), entstanden_am, strang_id),
                )
                cur.execute(
                    "UPDATE praegung_faden SET strang_id = %s WHERE id = %s",
                    (strang_id, faden_id),
                )
                logger.info(
                    f"Praegung: Faden {faden_id} tritt Strang {strang_id} bei — "
                    f"naehe={naehe:.4f} >= {PRAEGUNG_STRANG_NAEHE}, "
                    f"jetzt {faden_zahl + 1} Faeden"
                )
                beigetreten = True

            else:
                # Kein Strang nah genug: Der Faden gruendet einen. Sein Vektor
                # ist das erste Zentroid — ein Strang aus einem Faden ist der
                # Regelfall am Anfang und kein Sonderfall.
                cur.execute(
                    """
                    INSERT INTO praegung_strang
                        (user_id, character_id, beobachter, zentroid, faden_zahl,
                         erster_faden, letzter_faden)
                    VALUES (%s, %s, %s, %s::vector, 1, %s, %s)
                    RETURNING id
                    """,
                    (user_id, character_id, beobachter,
                     _vektor_schreiben(faden_vektor), entstanden_am, entstanden_am),
                )
                strang_id = cur.fetchone()[0]
                cur.execute(
                    "UPDATE praegung_faden SET strang_id = %s WHERE id = %s",
                    (strang_id, faden_id),
                )
    except Exception as fehler:
        logger.error(
            f"Praegung: Strangzuordnung fuer Faden {faden_id} fehlgeschlagen — "
            f"{fehler}. Der Faden bleibt ohne Strang und wird beim Nachzug "
            f"erneut betrachtet"
        )
        return None

    # ── Ausgabe ────────────────────────────────
    if not beigetreten:
        beste = f"{treffer[3]:.4f}" if treffer is not None else "kein Strang vorhanden"
        logger.info(
            f"Praegung: Faden {faden_id} gruendet Strang {strang_id} — "
            f"beste Naehe {beste} < {PRAEGUNG_STRANG_NAEHE}"
        )

    # Das Histogramm, **ausserhalb** der Transaktion oben und mit eigenem
    # Fehlerpfad: Es ist eine reine Aggregation ueber den Bestand und jederzeit
    # wiederholbar; die Zuordnung ist es nicht. Faellt es aus, steht ein Strang
    # mit veraltetem Histogramm da — und der naechste Beitritt richtet es.
    strang_histogramm_rechnen(postgres_url, strang_id)

    return strang_id


def strang_histogramm_rechnen(postgres_url: str, strang_id: int) -> dict | None:
    """Rechnet das Sektor-Histogramm eines Strangs neu und schreibt es fort.

    Konzept §7.8. **Nicht der Mittelwert:** Sektor 1 und Sektor 5 ergaeben
    gemittelt *neutral*, und die Ambivalenz — der interessante Fall — waere
    ausgeloescht. Also ein Histogramm ueber die acht Plutchik-Sektoren, und
    daraus drei Destillate: dominanter Sektor, Konzentration und Valenz.

    **Gezaehlt werden Faeden, nicht Ausschlaege.** Die Intensitaet hat ihren
    eigenen Platz in der Ladung (`W_SPITZE`); ein Histogramm, das Faerbung und
    Staerke mischt, ist eine Zahl mit zwei Wirkungen.

    **Neu gerechnet, nicht fortgeschrieben** — ausdruecklich anders als beim
    Zentroid. Dort sind es 768 Werte und ein Scan je Turn waere teuer; hier ist
    es ein GROUP BY ueber die Faeden eines Strangs, und eine Neuberechnung kann
    nicht driften.

    **Valenz ist nicht Richtung.** Zwei negative Praegungen koennen
    entgegengesetzte Richtungen haben (§7.7). Die Richtung braucht die
    Annaeherungs-Tabelle und ist nicht gebaut.

    Vorbedingung: `strang_id` bezeichnet eine Zeile in `praegung_strang`.
    Nachbedingung: `sektor_histogramm` traegt acht Zahlen, deren Summe die Zahl
        der Faeden mit kanonischer Emotion ist; `sektor_dominant`,
        `konzentration` und `valenz` sind daraus gerechnet oder NULL, wenn kein
        Faden zaehlbar war.
    Fehlerfaelle: Eine Emotion ausserhalb von `EMOTION_SEKTOR_MAP` wird **nicht
        mitgezaehlt und gemeldet** — stillschweigend auf einen Sektor zu legen
        hiesse, eine unbekannte Faerbung als bekannte auszugeben.

    Args:
        postgres_url: Verbindung.
        strang_id: der Strang, dessen Histogramm neu entsteht.

    Returns:
        `{"histogramm": [...], "dominant": int|None, "konzentration": float|None,
        "valenz": float|None, "unbekannt": int}` oder None bei Fehlschlag.
    """
    # ── Eingabe ────────────────────────────────
    if strang_id is None or strang_id <= 0:
        logger.error(f"Praegung: Histogramm abgelehnt — strang_id={strang_id}")
        return None

    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT emotion, count(*) FROM praegung_faden "
                "WHERE strang_id = %s GROUP BY emotion",
                (strang_id,),
            )
            zeilen: list = cur.fetchall()

            # ── Verarbeitung ───────────────────────────
            histogramm: list[int] = [0] * 8
            unbekannt:  int = 0
            for emotion, anzahl in zeilen:
                sektor = EMOTION_SEKTOR_MAP.get(emotion)
                if sektor is None:
                    unbekannt += anzahl
                    logger.warning(
                        f"Praegung: Strang {strang_id} — Emotion '{emotion}' "
                        f"({anzahl}x) ist in keinem Sektor und faerbt nicht mit"
                    )
                    continue
                histogramm[sektor - 1] += anzahl

            gesamt: int = sum(histogramm)
            if gesamt:
                dominant: int | None = histogramm.index(max(histogramm)) + 1
                konzentration: float | None = max(histogramm) / gesamt
                positiv = sum(
                    n for i, n in enumerate(histogramm, start=1)
                    if SEKTOR_GRUPPE.get(i) == "positiv"
                )
                negativ = sum(
                    n for i, n in enumerate(histogramm, start=1)
                    if SEKTOR_GRUPPE.get(i) == "negativ"
                )
                valenz: float | None = (positiv - negativ) / gesamt
            else:
                dominant, konzentration, valenz = None, None, None

            cur.execute(
                """
                UPDATE praegung_strang
                   SET sektor_histogramm = %s, sektor_dominant = %s,
                       konzentration = %s, valenz = %s
                 WHERE id = %s
                """,
                (histogramm, dominant, konzentration, valenz, strang_id),
            )
    except Exception as fehler:
        logger.error(
            f"Praegung: Histogramm von Strang {strang_id} nicht geschrieben — "
            f"{fehler}"
        )
        return None

    # ── Ausgabe ────────────────────────────────
    logger.info(
        f"Praegung: Strang {strang_id} — Histogramm {histogramm}, "
        f"dominant={dominant}, konzentration="
        f"{f'{konzentration:.3f}' if konzentration is not None else '—'}, "
        f"valenz={f'{valenz:+.3f}' if valenz is not None else '—'}"
        + (f", {unbekannt} ohne Sektor" if unbekannt else "")
    )
    return {
        "histogramm": histogramm, "dominant": dominant,
        "konzentration": konzentration, "valenz": valenz,
        "unbekannt": unbekannt,
    }


def faeden_ohne_strang_zuordnen(postgres_url: str) -> tuple[int, int]:
    """Holt nach, was ohne Strang geblieben ist — in der Reihenfolge der Zeit.

    Konzept §7.7. Die Zuordnung laeuft ausserhalb der Fadentransaktion und darf
    deshalb ausfallen; dieser Lauf ist ihr Rueckweg. Er ist zugleich der Weg,
    auf dem ein Bestand aus der Zeit **vor** der Strangschicht seine Straenge
    bekommt.

    **Die Sortierung ist die Zusicherung, nicht die Bequemlichkeit.** Online-
    Zuordnung ist reihenfolgeabhaengig; `entstanden_am, id` macht sie
    reproduzierbar — zwei Laeufe ueber denselben Bestand ergeben denselben
    Bestand. Ohne sie waere jeder Nachzug ein anderes Ergebnis, und keiner
    davon falsch.

    Nachbedingung: Die zurueckgegebenen Zahlen sind **gezaehlt, nicht
    fortgeschrieben** — `zugeordnet` und `gesamt`. Die Vollstaendigkeit ist die
    Zusicherung dieses Laufs; ohne die zweite Zahl waere `zugeordnet` allein
    von einem Abbruch nicht zu unterscheiden.

    Args:
        postgres_url: Verbindung.

    Returns:
        `(zugeordnet, gesamt)` — wie viele einen Strang bekamen und wie viele
        ohne einen dastanden.
    """
    # ── Eingabe ────────────────────────────────
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM praegung_faden
                 WHERE strang_id IS NULL AND embedding IS NOT NULL
                 ORDER BY entstanden_am, id
                """
            )
            offene: list[int] = [z[0] for z in cur.fetchall()]
    except Exception as fehler:
        logger.error(f"Praegung: Nachzug der Straenge nicht gelesen — {fehler}")
        return (0, 0)

    # ── Verarbeitung ───────────────────────────
    zugeordnet: int = 0
    for faden_id in offene:
        if strang_zuordnen(postgres_url, faden_id) is not None:
            zugeordnet += 1

    # ── Ausgabe ────────────────────────────────
    logger.info(
        f"Praegung: Strang-Nachzug — {zugeordnet} von {len(offene)} Faeden "
        f"zugeordnet"
    )
    return (zugeordnet, len(offene))


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


def alle_faeden_nachfuehren(
    postgres_url: str,
    jetzt:        datetime | None = None,
    stapel:       int = 500,
) -> dict:
    """Faltet den ganzen Bestand — der Verfall zwischen zwei Beruehrungen.

    **Warum es diesen Lauf ueberhaupt gibt.** `ausschlag_aktuell_nachfuehren`
    laeuft, wenn eine Beruehrung entsteht. Der Verfall **zwischen** zwei
    Beruehrungen hat kein Ereignis, an dem er haengen koennte: Ein Faden, den
    seit Wochen niemand angesprochen hat, stuende in der Spalte so hoch wie am
    Tag seiner letzten Auffrischung. `[gemessen]` 01.09.2026: Faden 353 trug
    eine Beruehrung und stand danach unveraendert auf `ausschlag_absolut`, weil
    ihn nach dem Bau des Aufrufers niemand mehr getroffen hat
    (`FALTUNG-OHNE-PERIODISCHEN-LAUF`).

    **Der ganze Bestand, nicht die veralteten.** Welche Zeile veraltet ist,
    waere nur mit einem Zeitstempel der letzten Faltung zu beantworten — den
    gibt es nicht, und ein Schemawechsel dafuer waere teurer als die Rechnung.
    Sie ist billig: ein Lesevorgang und ein `UPDATE` je Faden, ohne Modell und
    ohne Netz.

    **Die Vollstaendigkeit ist die eigentliche Zusicherung.** Zurueckgegeben
    werden `gefaltet` **und** `gesamt`; sind sie gleich, traegt kein Faden einen
    Wert, der aelter ist als der Lauf. Ohne die zweite Zahl waere ein Lauf ueber
    die Haelfte des Bestandes von einem vollstaendigen nicht zu unterscheiden
    (`22_STILLE_FEHLER`).

    Vorbedingung: keine — ein leerer Bestand ist der Regelfall am Anfang.
    Nachbedingung: Jeder Faden traegt einen `ausschlag_aktuell`, der auf
    `jetzt` gerechnet ist; `gefaltet == gesamt`, wenn nichts ausfiel.
    Fehlerfaelle: Ein Lesefehler wird gemeldet und liefert `gesamt = 0` mit
    einem Text in `error`; ein Stapel, der ausfaellt, laesst die uebrigen
    laufen — der Wert ist jederzeit neu rechenbar.

    Args:
        postgres_url: Verbindung.
        jetzt: Bezugszeitpunkt der Rechnung; ohne Angabe die aktuelle Zeit.
        stapel: Wie viele Faeden je Aufruf gerechnet werden.

    Returns:
        `{"gefaltet": int, "gesamt": int, "error": str | None}`.
    """
    # ── Eingabe-Validierung ─────────────────────
    bezug: datetime = jetzt or datetime.now(timezone.utc)
    if stapel < 1:
        logger.error(
            f"Praegung: Stapelgroesse {stapel} ist unbrauchbar — der Lauf "
            f"faellt aus, statt in eine Endlosschleife zu gehen"
        )
        return {"gefaltet": 0, "gesamt": 0, "error": f"stapel={stapel}"}

    # ── Verarbeitung ───────────────────────────
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM praegung_faden ORDER BY id")
            ids: list[int] = [int(z[0]) for z in cur.fetchall()]
    except Exception as fehler:
        logger.exception(
            f"Praegung: Bestandslauf konnte die Faeden nicht lesen "
            f"({type(fehler).__name__}) — kein Wert ist nachgefuehrt"
        )
        return {"gefaltet": 0, "gesamt": 0, "error": str(fehler)}

    gefaltet: int = 0
    for anfang in range(0, len(ids), stapel):
        gefaltet += ausschlag_aktuell_nachfuehren(
            postgres_url, ids[anfang:anfang + stapel], bezug,
        )

    # ── Ausgabe-Verifikation ────────────────────
    # **Die Luecke wird benannt, nicht verschwiegen.** Ein Lauf ueber 40 von 50
    # Faeden sieht in der Zeile darunter aus wie einer ueber 40 von 40.
    if gefaltet < len(ids):
        logger.error(
            f"Praegung: Bestandslauf hat {gefaltet} von {len(ids)} Faeden "
            f"nachgefuehrt — die uebrigen tragen einen Wert von vorher; die "
            f"Rechnung ist wiederholbar, der naechste Lauf holt sie"
        )
    else:
        logger.info(
            "Praegung: Bestandslauf hat alle %d Faeden nachgefuehrt", gefaltet,
        )
    return {
        "gefaltet": gefaltet,
        "gesamt":   len(ids),
        "error":    None if gefaltet == len(ids) else "unvollstaendig",
    }


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
