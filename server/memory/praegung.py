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
    EMOTION_VALENZ,
    PRAEGUNG_ALPHA,
    PRAEGUNG_ANZAHL_SAETTIGUNG,
    PRAEGUNG_BODEN,
    PRAEGUNG_HALBSTRECKE,
    PRAEGUNG_KONFRONTATION_SCHWELLE,
    PRAEGUNG_PRAESENZ_BODEN,
    PRAEGUNG_PRAESENZ_HALBSTRECKE,
    PRAEGUNG_SEKTOR8_ZUG,
    PRAEGUNG_SEKTOR_FAKTOR,
    PRAEGUNG_SPEICHEN_SCHUETZEND,
    PRAEGUNG_SPEICHEN_WILD,
    PRAEGUNG_STRANG_NAEHE,
    PRAEGUNG_TOR_AUSSCHLAG,
    PRAEGUNG_TOR_SALIENZ,
    PRAEGUNG_W_ANZAHL,
    PRAEGUNG_W_SALIENZ,
    PRAEGUNG_W_VALENZ,
    PRAEGUNG_ZUG_HUB,
    PRAEGUNG_ZUG_UNBESTIMMT,
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
    salienz: float | None = None,
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
        salienz: Wie stark der Reiz draengte, [0,1]. **Nullfaehig:** Wer sie
            nicht kennt, schreibt keine — ein Vorgabewert waere eine erfundene
            Messung, und die Strangstaerke rechnet ohne sie weiter.

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
                     ausschlag_aktuell, herkunft, salienz)
                VALUES (%s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, character_id, beobachter, turn_id, embedding_str,
                 emotion, ausschlag_eingang, ausschlag_absolut,
                 ausschlag_absolut, herkunft, salienz),
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
                # **Die Valenz kommt aus `EMOTION_VALENZ`, nicht aus der
                # Sektorgruppe** (seit 02.09.2026): Sie traegt damit
                # Zwischenstufen statt +1/-1/0. Gerechnet wird ueber die
                # Emotionen, nicht ueber das Histogramm — die Tabelle
                # unterscheidet innerhalb eines Sektors (`begeisterung` 1,00
                # gegen `freude` 0,80), das Histogramm kann das nicht.
                valenz: float | None = sum(
                    EMOTION_VALENZ.get(emotion, 0.0) * anzahl
                    for emotion, anzahl in zeilen
                    if emotion in EMOTION_SEKTOR_MAP
                ) / gesamt
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


def konfrontationsmass(rad: dict[str, float]) -> float | None:
    """Wie weit Nova heute der unangenehmen Sache nachgeht statt sie zu meiden.

    Konzept §7.7. Mittel der vier **wilden** Speichen minus Mittel der vier
    **schuetzenden**, auf [-1, 1]. Vorgabe des Eigentuemers (01.09.2026): Aerger
    und Ekel koennen anziehen, aber ein Gemuet mit Selbsterhaltungsdrang und
    Pflichtbewusstsein schuetzt sich davor — das wilde, furchtlose, neugierige
    Wesen sucht die Konfrontation.

    **Die Speichen kommen aus beiden Raedern**, und das ist Absicht: Wissbegier
    und Pflicht stehen im Zuwendungs-Rad, Eigensinn und Behutsamkeit im
    Initiative-Rad. Wer nur eines liest, sieht die halbe Anlage.

    Vorbedingung: `rad` bildet Speichennamen auf [0, 1] ab — die Vereinigung
        beider Raeder, wie `rad_zusammenfassen` sie liefert.
    Nachbedingung: ein Wert auf [-1, 1], oder None, wenn **eine** der acht
        Speichen fehlt.
    Fehlerfaelle: Eine fehlende Speiche wird gemeldet und macht das Mass
        **ungueltig** statt es aus den uebrigen zu bilden. Ein Mass aus sechs
        von acht Speichen sieht aus wie eines aus acht, und der Unterschied
        waere nirgends ablesbar (`22_STILLE_FEHLER`).

    Args:
        rad: die Speichen beider Raeder, zusammengefasst.

    Returns:
        Das Mass auf [-1, 1], oder None bei unvollstaendigem Rad.
    """
    # ── Eingabe ────────────────────────────────
    fehlend: list[str] = [
        name for name in PRAEGUNG_SPEICHEN_WILD + PRAEGUNG_SPEICHEN_SCHUETZEND
        if name not in (rad or {})
    ]
    if fehlend:
        logger.warning(
            f"Praegung: Konfrontationsmass ungueltig — {len(fehlend)} von 8 "
            f"Speichen fehlen ({', '.join(sorted(fehlend))}). Ein Mass aus "
            f"weniger Speichen saehe aus wie eines aus allen"
        )
        return None

    # ── Verarbeitung ───────────────────────────
    wild:       float = sum(rad[n] for n in PRAEGUNG_SPEICHEN_WILD) / 4
    schuetzend: float = sum(rad[n] for n in PRAEGUNG_SPEICHEN_SCHUETZEND) / 4

    # ── Ausgabe ────────────────────────────────
    mass: float = wild - schuetzend
    logger.info(
        f"Praegung: Konfrontationsmass {mass:+.4f} — wild {wild:.4f}, "
        f"schuetzend {schuetzend:.4f}"
    )
    return mass


def strang_richtung(
    histogramm: list[int],
    konfrontation: float | None,
) -> tuple[str, str]:
    """Zieht dieser Strang Nova an, oder drueckt er sie weg?

    Konzept §7.7. **Die Richtung ist nicht die Valenz:** Zwei negative
    Praegungen koennen entgegengesetzt zeigen — Machtlosigkeit → Macht ist
    Annaeherung, Furcht vor der Dunkelheit ist Vermeidung. Eine Valenzachse
    allein kann Kriegsgeschichte nicht von Dunkelheit unterscheiden.

    **Vier Regeln, in dieser Reihenfolge:**

      1. **Sektor 8 ueber `PRAEGUNG_SEKTOR8_ZUG` → Annaeherung, unbedingt.**
         Vorgabe des Eigentuemers: Starke Neugier zieht immer, und die
         Anwesenheit ueber der Schwelle genuegt — das Rad wird nicht gefragt.
      2. **Furcht (3) und Ueberraschung (4) zusammen → Annaeherung.** Die
         Awe-Dyade, der einzige Fall, den das Konzept selbst vorgibt.
      3. **Dominant positiv (1, 2) → Annaeherung.**
      4. **Sonst entscheidet das Rad.** Ueber `PRAEGUNG_KONFRONTATION_SCHWELLE`
         Annaeherung, darunter Vermeidung.

    **Die Reihenfolge ist Teil der Aussage.** Ein Strang aus Furcht *und* viel
    Neugier ist Annaeherung, gleich wie vorsichtig Nova heute ist; Regel 1 steht
    deshalb vor Regel 4.

    Vorbedingung: `histogramm` traegt acht Zahlen.
    Nachbedingung: `("annaeherung" | "vermeidung" | "unbestimmt", grund)`. Der
        Grund nennt die Regel **und ihre Zahl** — ohne sie waere im Nachhinein
        nicht zu sehen, wie knapp die Entscheidung war (`11_EVA`).
    Fehlerfaelle: Ein leeres Histogramm und ein fehlendes Mass ergeben
        `unbestimmt` — nicht `vermeidung`. Ein Vorgabewert an dieser Stelle
        waere eine Aussage ueber den Charakter, die niemand getroffen hat.

    Args:
        histogramm: die acht Sektorzahlen des Strangs.
        konfrontation: das Mass aus `konfrontationsmass`, oder None.

    Returns:
        Richtung und Grund.
    """
    # ── Eingabe ────────────────────────────────
    if not histogramm or len(histogramm) != 8:
        return ("unbestimmt", f"Histogramm unbrauchbar ({histogramm})")

    gesamt: int = sum(histogramm)
    if gesamt <= 0:
        return ("unbestimmt", "kein Faden im Strang")

    # ── Verarbeitung ───────────────────────────
    anteil8: float = histogramm[7] / gesamt
    if anteil8 >= PRAEGUNG_SEKTOR8_ZUG:
        return (
            "annaeherung",
            f"Neugier {anteil8:.3f} >= {PRAEGUNG_SEKTOR8_ZUG} — sie zieht immer",
        )

    if histogramm[2] > 0 and histogramm[3] > 0:
        return (
            "annaeherung",
            f"Awe-Dyade: Furcht {histogramm[2]} und Ueberraschung "
            f"{histogramm[3]} zusammen",
        )

    positiv: int = histogramm[0] + histogramm[1]
    negativ: int = histogramm[2] + histogramm[4] + histogramm[5] + histogramm[6]
    if positiv > negativ:
        return (
            "annaeherung",
            f"positiv {positiv} ueberwiegt negativ {negativ}",
        )

    if konfrontation is None:
        return (
            "unbestimmt",
            f"negativ {negativ} gegen positiv {positiv}, aber kein Rad — "
            f"ein Vorgabewert waere eine Aussage ueber den Charakter",
        )

    # ── Ausgabe ────────────────────────────────
    if konfrontation > PRAEGUNG_KONFRONTATION_SCHWELLE:
        return (
            "annaeherung",
            f"negativ {negativ}, aber Konfrontationsmass {konfrontation:+.4f} > "
            f"{PRAEGUNG_KONFRONTATION_SCHWELLE}",
        )
    return (
        "vermeidung",
        f"negativ {negativ} und Konfrontationsmass {konfrontation:+.4f} <= "
        f"{PRAEGUNG_KONFRONTATION_SCHWELLE}",
    )


def strang_staerke(postgres_url: str, strang_id: int) -> dict | None:
    """Wie stark ein Strang zieht — Salienz, Valenz, Anzahl, mal Praesenz.

    Konzept §7.7 in der Fassung vom 02.09.2026. **Vorgabe des Eigentuemers:**
    *„Salienz, Valenz, Anzahl Faeden. Das macht den Strang stark."*

        staerke = ( W_SALIENZ · mittel(faden.salienz)
                  + W_VALENZ  · mittel(|valenz_faden|)
                  + W_ANZAHL  · n / (n + K) )
                  × f_praesenz( heute − letzte Beruehrung )

    **Sie wird nicht gespeichert** — dieselbe Entscheidung wie bei der Richtung:
    `f_praesenz` macht sie zeitabhaengig, und eine Spalte truege die Antwort von
    gestern. Die Rechnung ist ein Aggregat ueber die Faeden eines Strangs.

    **`mittel(|valenz|)`, nicht `|mittel(valenz)|`.** Zwei Freude- und zwei
    Trauerfaeden ergeben so 1,0 statt 0. Vorgabe: *„Wenn die sich aufheben
    wuerden, wuerden viele Faeden eigentlich zu einer Nullung fuehren statt zu
    einer Intensivierung der Praegung."* Ein Faden traegt seine Valenz heute nur
    als Sektorzugehoerigkeit (+1, -1, oder 0 bei Ueberraschung); die Groesse
    steht damit **nahezu konstant auf 1,0** und wird erst tragend, wenn Sektor 4
    haeufiger vorkommt. Der Befund steht in der Fundliste, die Absicht ist
    bestaetigt.

    **Additiv, nicht multiplikativ** (Regel a des Konzepts §10.0): Keine Null aus
    einer Multiplikation, nur weil ein Eingang null ist.

    Vorbedingung: `strang_id` bezeichnet eine Zeile in `praegung_strang`.
    Nachbedingung: Ein Wert auf [0, 1] samt seinen drei Eingaengen und der
        Praesenz — **der Bericht traegt die Teile, nicht nur die Summe.** Ohne
        sie ist im Nachhinein nicht zu sehen, welcher Eingang die Zahl gemacht
        hat, und genau das war bei der Salienz am 01.09.2026 die Frage.
    Fehlerfaelle: Ein Strang ohne Faeden ergibt None. Faeden **ohne** Salienz
        zaehlen fuer das Mittel nicht mit und werden gemeldet; steht keiner mit
        Salienz da, ist der Eingang 0,0 und die Zahl daneben sagt es.

    Args:
        postgres_url: Verbindung.
        strang_id: der Strang.

    Returns:
        `{"staerke", "salienz_mittel", "valenz_mittel", "anzahl_term",
        "praesenz", "faden_zahl", "ohne_salienz", "tage_still"}` oder None.
    """
    # ── Eingabe ────────────────────────────────
    if strang_id is None or strang_id <= 0:
        logger.error(f"Praegung: Staerke abgelehnt — strang_id={strang_id}")
        return None

    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            # **Die Beruehrungen stehen in einem eigenen Ausdruck, nicht in
            # einem JOIN.** Ein `LEFT JOIN` auf `praegung_beruehrung`
            # vervielfacht die Fadenzeilen — ein Faden mit drei Beruehrungen
            # erscheint dreimal, `count(*)` zaehlt dann Paare statt Faeden und
            # `avg(salienz)` gewichtet oft beruehrte Faeden staerker.
            # `[gemessen]` 02.09.2026: Die erste Fassung meldete **8 Faeden**
            # fuer einen Strang, der vier hat. Gefunden hat es die Vorhersage
            # vor dem Lauf, nicht die 16 Zeugen — die ersetzen den Cursor und
            # sehen die Abfrage nicht.
            #
            # **Je Emotion eine Zeile**, weil die Valenz aus `EMOTION_VALENZ`
            # kommt und nicht mehr aus einer Dreiwerte-Gruppe: Die Tabelle lebt
            # in Python, also holt die Abfrage die Emotionen und rechnet nicht
            # selbst.
            cur.execute(
                """
                SELECT f.emotion, count(*), count(f.salienz),
                       coalesce(sum(f.salienz), 0.0)
                FROM praegung_faden f
                WHERE f.strang_id = %s
                GROUP BY f.emotion
                """,
                (strang_id,),
            )
            je_emotion: list = cur.fetchall()

            cur.execute(
                """
                SELECT EXTRACT(EPOCH FROM (NOW() - GREATEST(
                           max(f.entstanden_am),
                           coalesce((SELECT max(b.beruehrt_am)
                                       FROM praegung_beruehrung b
                                       JOIN praegung_faden g ON g.id = b.faden_id
                                      WHERE g.strang_id = %s),
                                    max(f.entstanden_am))
                       ))) / 86400.0
                FROM praegung_faden f
                WHERE f.strang_id = %s
                """,
                (strang_id, strang_id),
            )
            tage_still = (cur.fetchone() or [0.0])[0]
    except Exception as fehler:
        logger.error(
            f"Praegung: Staerke von Strang {strang_id} nicht lesbar — {fehler}"
        )
        return None

    faden_zahl:  int   = sum(z[1] for z in je_emotion)
    mit_salienz: int   = sum(z[2] for z in je_emotion)
    salienz_summe: float = sum(float(z[3]) for z in je_emotion)
    if not faden_zahl:
        logger.warning(f"Praegung: Strang {strang_id} hat keine Faeden")
        return None

    # ── Verarbeitung ───────────────────────────
    # **`mittel(|valenz|)` ueber die Tabelle**, nicht ueber die Sektorgruppe.
    # Bis zum 02.09.2026 trug ein Faden ±1 oder 0, und die Groesse stand in
    # 97,05 % der Faelle auf exakt 1,00 — eine Konstante mit Nachkommastellen.
    # Eine Emotion ausserhalb der Tabelle traegt **keine** Ladung und wird
    # gemeldet; ein Vorgabewert waere eine erfundene Faerbung.
    unbekannt: int = 0
    valenz_summe: float = 0.0
    for emotion, anzahl, _mit_sal, _sum_sal in je_emotion:
        wert = EMOTION_VALENZ.get(emotion)
        if wert is None:
            unbekannt += anzahl
            logger.warning(
                f"Praegung: Strang {strang_id} — Emotion '{emotion}' "
                f"({anzahl}x) steht nicht in EMOTION_VALENZ und faerbt nicht"
            )
            continue
        valenz_summe += abs(wert) * anzahl
    valenz_mittel: float = valenz_summe / faden_zahl
    salienz_mittel: float = (
        salienz_summe / mit_salienz if mit_salienz else 0.0
    )
    anzahl_term:   float = faden_zahl / (faden_zahl + PRAEGUNG_ANZAHL_SAETTIGUNG)
    praesenz:      float = _verfall(
        max(0.0, float(tage_still or 0.0)),
        PRAEGUNG_PRAESENZ_BODEN, PRAEGUNG_PRAESENZ_HALBSTRECKE,
    )

    summe: float = (
        PRAEGUNG_W_SALIENZ * float(salienz_mittel)
        + PRAEGUNG_W_VALENZ * valenz_mittel
        + PRAEGUNG_W_ANZAHL * anzahl_term
    )
    staerke: float = summe * praesenz

    # ── Ausgabe ────────────────────────────────
    fehlend: int = faden_zahl - mit_salienz
    if fehlend:
        logger.warning(
            f"Praegung: Strang {strang_id} — {fehlend} von {faden_zahl} Faeden "
            f"ohne Salienz; das Mittel steht auf {float(salienz_mittel):.4f} "
            f"und traegt sie nicht"
        )
    logger.info(
        f"Praegung: Strang {strang_id} Staerke {staerke:.4f} — "
        f"salienz {float(salienz_mittel):.4f}, valenz {valenz_mittel:.4f}, "
        f"anzahl {anzahl_term:.4f} ({faden_zahl} Faeden), "
        f"praesenz {praesenz:.4f} ({float(tage_still or 0):.1f} Tage still)"
    )
    return {
        "staerke":        staerke,
        "salienz_mittel": float(salienz_mittel),
        "valenz_mittel":  valenz_mittel,
        "anzahl_term":    anzahl_term,
        "praesenz":       praesenz,
        "faden_zahl":     faden_zahl,
        "ohne_salienz":   fehlend,
        "ohne_valenz":    unbekannt,
        "tage_still":     float(tage_still or 0.0),
    }


def praegungszug(
    postgres_url: str,
    user_id: str,
    character_id: str,
    reiz_vektor: list[float],
    konfrontation: float | None,
    beobachter: str = "assistant",
) -> dict | None:
    """Wie stark die Praegung diesen Reiz anhebt — verstaerkt nur, daempft nie.

    Konzept §10.3.

        praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )

    **Der Zug ist ein Maximum, keine Summe.** Zwei Straenge, die denselben Reiz
    tragen, ziehen nicht doppelt — es zieht der eine, der am naechsten liegt und
    am staerksten geladen ist.

    **Die Richtung ist der Torfaktor, nicht die Valenz** (§7.7). Ein negativer
    Strang zieht: *Machtlosigkeit → Macht* ist Annaeherung, und Kriegsgeschichte
    kommt als Awe-Dyade herein. Nur der Strang, von dem Nova **wegwill**, traegt
    nichts bei. **Vorgabe des Eigentuemers, 03.09.2026:** *„Was unter Vermeidung
    faellt, ist genau das, was wir nicht als Faszination wollen — wir filtern es
    einfach raus."* `unbestimmt` ist keine Vermeidung, sondern Unkenntnis und
    wiegt `PRAEGUNG_ZUG_UNBESTIMMT`.

    **Die Suche bricht ab, sobald kein Strang mehr gewinnen kann.** Die Zeilen
    kommen nach Aehnlichkeit sortiert, und `gewicht · ladung` liegt auf [0, 1] —
    ein Strang mit `sim <= bestes_produkt` kann das Maximum nicht mehr heben.
    Der Abbruch ist damit **exakt und keine Naeherung**; er haelt den Aufwand bei
    wenigen Zeilen, waehrend die Zahl der Straenge waechst.

    Vorbedingung: `reiz_vektor` traegt die Dimension der Zentroide; das Paar ist
        gesetzt. `konfrontation` ist das Mass aus `konfrontationsmass` oder None
        — ohne Rad entscheidet Regel 4 nicht, und der Strang bleibt
        `unbestimmt` statt auf einen Vorgabewert zu fallen.
    Nachbedingung: `zug` liegt auf [1.0, 1.0 + PRAEGUNG_ZUG_HUB], **durch
        Konstruktion und ohne Kappung** (`F-NAHT-1`). Der Bericht traegt die
        Teile neben der Summe: ohne sie ist im Nachhinein nicht zu sehen, ob ein
        Zug von 1,0 aus fehlender Naehe, fehlender Ladung oder aus lauter
        Vermeidung entstand — drei verschiedene Zustaende mit derselben Zahl.
    Fehlerfaelle: Kein Strang, kein Vektor oder ein Lesefehler ergeben **nicht**
        None, sondern den Zug 1,0 mit `grund` — die Abwesenheit einer Praegung
        ist der Normalfall und kein Fehler. None steht nur fuer eine abgelehnte
        Eingabe.

    Args:
        postgres_url: Verbindung.
        user_id: der Mensch (`novaberg-convention-paar-schema.md` §2).
        character_id: die Figur.
        reiz_vektor: das Embedding des Reizes, an dem der Zug ansetzt.
        konfrontation: das Mass aus `konfrontationsmass`, oder None.
        beobachter: Schreiber der Straenge — dieselbe Achse wie bei der
            Zuordnung (`strang_zuordnen`), sonst zoege ein Strang, den ein
            anderer geschrieben hat.

    Returns:
        `{"zug", "strang_id", "sim", "ladung", "richtung", "gewicht", "produkt",
        "betrachtet", "gerechnet", "grund"}` oder None bei abgelehnter Eingabe.
    """
    # ── Eingabe ────────────────────────────────
    if not user_id or not character_id:
        logger.error(
            f"Praegung: Zug abgelehnt — Paar unvollstaendig "
            f"(user_id={user_id!r}, character_id={character_id!r})"
        )
        return None

    if not reiz_vektor:
        logger.error(
            "Praegung: Zug abgelehnt — kein Reizvektor. Ohne Ort auf der "
            "Landkarte gibt es keine Aehnlichkeit, und ein Zug von 1,0 waere "
            "hier eine Aussage statt einer fehlenden Eingabe"
        )
        return None

    leer: dict = {
        "zug": 1.0, "strang_id": None, "sim": 0.0, "ladung": 0.0,
        "richtung": None, "gewicht": 0.0, "produkt": 0.0,
        "betrachtet": 0, "gerechnet": 0, "grund": "",
    }

    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            # `<=>` ist die Kosinus-Distanz; 1 - d ist die Aehnlichkeit —
            # dieselbe Rechnung wie bei der Zuordnung und der Reaktivierung.
            cur.execute(
                """
                SELECT id, sektor_histogramm,
                       1 - (zentroid <=> %s::vector) AS naehe
                FROM praegung_strang
                WHERE user_id = %s AND character_id = %s AND beobachter = %s
                ORDER BY naehe DESC
                """,
                (_vektor_schreiben(reiz_vektor), user_id, character_id, beobachter),
            )
            straenge: list = cur.fetchall()
    except Exception as fehler:
        logger.error(
            f"Praegung: Straenge fuer den Zug nicht lesbar ({user_id}/"
            f"{character_id}) — {fehler}. Der Zug bleibt bei 1,0"
        )
        return {**leer, "grund": f"Straenge nicht lesbar: {fehler}"}

    if not straenge:
        logger.info(
            f"Praegung: Zug 1.0000 — kein Strang fuer {user_id}/{character_id}"
        )
        return {**leer, "grund": "kein Strang"}

    # ── Verarbeitung ───────────────────────────
    bestes: float = 0.0
    treffer: dict = {}
    gerechnet: int = 0

    for strang_id, histogramm_roh, naehe in straenge:
        # **Der Abbruch traegt zugleich das „verstaerkt nur, daempft nie".**
        # `bestes` startet bei 0,0 und waechst nur ueber Produkte
        # nichtnegativer Groessen; eine negative Kosinusnaehe erfuellt damit
        # `sim <= bestes` und kommt nie in die Rechnung. Eine zusaetzliche
        # Klammer `max(0.0, …)` waere toter Code — sie stand hier und liess
        # sich in der Gegenprobe entfernen, ohne dass ein Zeuge rot wurde
        # (03.09.2026). Ein Schutz, der nie greift, sieht aus wie der Grund
        # fuer eine Zusicherung, die in Wahrheit woanders haengt.
        sim: float = float(naehe)
        if sim <= bestes:
            break

        histogramm: list[int] = list(histogramm_roh or [])
        richtung, grund = strang_richtung(histogramm, konfrontation)
        gewicht: float = {
            "annaeherung": 1.0,
            "unbestimmt":  PRAEGUNG_ZUG_UNBESTIMMT,
            "vermeidung":  0.0,
        }.get(richtung, 0.0)
        gerechnet += 1
        if gewicht <= 0.0:
            logger.debug(
                f"Praegung: Strang {strang_id} traegt nicht zum Zug bei — "
                f"{richtung} ({grund})"
            )
            continue

        ladung_teile: dict = strang_staerke(postgres_url, strang_id) or {}
        ladung: float = float(ladung_teile.get("staerke") or 0.0)
        produkt: float = sim * gewicht * ladung
        if produkt > bestes:
            bestes = produkt
            treffer = {
                "strang_id": strang_id, "sim": sim, "ladung": ladung,
                "richtung": richtung, "gewicht": gewicht, "produkt": produkt,
                "grund": grund,
            }

    zug: float = 1.0 + PRAEGUNG_ZUG_HUB * bestes

    # ── Ausgabe ────────────────────────────────
    # Die Spanne ist durch Konstruktion eingehalten, nicht gekappt. Bricht sie,
    # ist eine der beiden Eingangsskalen verlassen worden — das ist ein Befund
    # und keine Zahl, die man zurechtschneidet.
    if not 1.0 <= zug <= 1.0 + PRAEGUNG_ZUG_HUB + 1e-9:
        logger.error(
            f"Praegung: Zug {zug:.4f} verlaesst die Spanne "
            f"[1.0, {1.0 + PRAEGUNG_ZUG_HUB:.2f}] — sim oder Ladung liegen "
            f"ausserhalb von [0, 1]; die Teile stehen daneben"
        )

    ergebnis: dict = {
        **leer, **treffer, "zug": zug,
        "betrachtet": len(straenge), "gerechnet": gerechnet,
    }
    if not treffer:
        ergebnis["grund"] = "kein Strang mit Zug"
    logger.info(
        f"Praegung: Zug {zug:.4f} fuer {user_id}/{character_id} — "
        f"Strang {ergebnis['strang_id']}, sim {ergebnis['sim']:.4f}, "
        f"Ladung {ergebnis['ladung']:.4f}, {ergebnis['richtung']} "
        f"(Gewicht {ergebnis['gewicht']:.2f}); {gerechnet} von "
        f"{len(straenge)} Straengen gerechnet"
    )
    return ergebnis


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
    zeitfaktor:        float = 1.0,
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

    **Eine Faltung, zwei Zeitachsen** (Konzept §7.9). Ueber `zeitfaktor` liefert
    dieselbe Funktion die zweite Stimme: `ausschlag_aktuell` mit 1,0, die
    **Einfaerbung** mit dem Sektorfaktor. Zwei getrennte Rechnungen waeren zwei
    Kurven, die auseinanderlaufen koennen — hier ist es eine, deren Uhr
    verschieden schnell geht.

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
        zeitfaktor: Streckung der Zeitachse. 1,0 ergibt `ausschlag_aktuell`;
            ein Wert darueber laesst die Zeit schneller laufen und ergibt die
            **Einfaerbung** (§7.9). Er wirkt auf die Abstaende, **nicht** auf
            den Boden und nicht auf Alpha — sonst waeren es zwei Kurven statt
            einer Kurve mit zwei Zeitachsen.

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
        tage: float = (beruehrt_am - letzt).total_seconds() / 86400.0 * zeitfaktor
        anteil = _verfall(
            _verfall_umkehren(anteil, boden, halbstrecke) + tage, boden, halbstrecke,
        )
        anteil = anteil + alpha * (1.0 - anteil)
        letzt = beruehrt_am

    rest_tage: float = (jetzt - letzt).total_seconds() / 86400.0 * zeitfaktor
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


def sektor_faktor(emotion: str) -> tuple[float, int | None]:
    """Wie schnell die Zeit fuer den Affekt dieses Sektors laeuft.

    Konzept §7.9, §8.4. Negative Sektoren stehen ueber 1,0 — der
    Fading-Affect-Bias, und ausdruecklich nur auf der Einfaerbung.

    Vorbedingung: keine.
    Nachbedingung: `(faktor, sektor)`. Eine unbekannte Emotion ergibt **1,0 und
        None** — die neutrale Zeitachse, nicht eine erfundene Beschleunigung —
        und wird gemeldet: Ein Vorgabewert ueber 1,0 waere eine Aussage ueber die
        Valenz einer Emotion, die in keiner Tabelle steht.
    Fehlerfaelle: siehe Nachbedingung; der Aufrufer laeuft weiter.

    Args:
        emotion: Die Emotion des Fadens.

    Returns:
        Der Zeitfaktor und der Sektor, oder `(1.0, None)`.
    """
    # ── Eingabe ────────────────────────────────
    sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion or "")
    if sektor is None or not 1 <= sektor <= len(PRAEGUNG_SEKTOR_FAKTOR):
        logger.warning(
            f"Praegung: Emotion '{emotion}' hat keinen Sektor — die Einfaerbung "
            f"laeuft auf der neutralen Zeitachse (1,0). Ein Vorgabewert darueber "
            f"waere eine Aussage ueber ihre Valenz"
        )
        return (1.0, None)

    # ── Ausgabe ────────────────────────────────
    return (PRAEGUNG_SEKTOR_FAKTOR[sektor - 1], sektor)


def einfaerbung_falten(
    ausschlag_absolut: float,
    emotion:           str,
    entstanden_am:     datetime,
    beruehrungen:      list[datetime],
    jetzt:             datetime,
) -> dict:
    """Die zweite Stimme: wie stark der Faden noch **fuehlt**.

    Konzept §7.9. Dieselbe Faltung wie `ausschlag_aktuell`, nur mit
    `t x sektor_faktor` — **eine Kurve, zwei Uhren**:

        ausschlag_aktuell : Faltung mit t                  → Ladung, Faszination
        einfaerbung       : Faltung mit t x sektor_faktor  → Ziele, LZG, EI-Calc

    **Die Trennung ist bindend, und sie ist der Grund fuer die ganze Groesse.**
    Der Fading-Affect-Bias darf die Ladung nicht erreichen: Sonst verloere
    Kriegsgeschichte ueber Monate gegen Gartenkraeuter, und die Valenzblindheit
    der Faszination fiele nicht durch einen Rechenfehler, sondern durch Absicht
    (§2.5). **Das alte Unrecht zieht schwaecher am Gefuehl und gleich stark an
    der Aufmerksamkeit.**

    **Sie wird nicht gespeichert** — dieselbe Entscheidung wie bei Richtung und
    Ladung: Der Wert haengt am heutigen Tag, eine Spalte truege die Antwort von
    gestern. Die Eingaenge stehen alle im Bestand, die Rechnung ist von Grund auf
    wiederholbar (`novaberg-convention-abgeleitete-werte.md` Regel 1, 3, 4).

    Vorbedingung: `beruehrungen` liegen nach `entstanden_am`.
    Nachbedingung: `einfaerbung <= ausschlag_aktuell` fuer jeden Sektor mit
        Faktor >= 1,0, und **gleich** bei 1,0 — der Bericht traegt beide, weil
        die Aussage der Groesse ihr **Abstand** ist und nicht ihr Betrag.
    Fehlerfaelle: Eine Emotion ohne Sektor ergibt die neutrale Zeitachse; der
        Bericht sagt es ueber `sektor = None`.

    Args:
        ausschlag_absolut: Der Eingangswert des Fadens.
        emotion: Die Emotion des Fadens — sie bestimmt den Sektor.
        entstanden_am: Wann der Faden entstand.
        beruehrungen: Die Zeitpunkte der Reaktivierungen.
        jetzt: Der Bezugszeitpunkt der Rechnung.

    Returns:
        `{"einfaerbung", "ausschlag_aktuell", "abstand", "sektor", "faktor"}`.
    """
    # ── Eingabe ────────────────────────────────
    faktor, sektor = sektor_faktor(emotion)

    # ── Verarbeitung ───────────────────────────
    gemeinsam: dict = {
        "ausschlag_absolut": ausschlag_absolut,
        "entstanden_am":     entstanden_am,
        "beruehrungen":      beruehrungen,
        "jetzt":             jetzt,
        "alpha":             PRAEGUNG_ALPHA,
        "halbstrecke":       PRAEGUNG_HALBSTRECKE,
        "boden":             PRAEGUNG_BODEN,
    }
    ausschlag:   float = ausschlag_aktuell_falten(**gemeinsam)
    einfaerbung: float = ausschlag_aktuell_falten(**gemeinsam, zeitfaktor=faktor)

    # ── Ausgabe ────────────────────────────────
    # **Der Abstand ist die Aussage, nicht der Betrag.** Ein Faden aus Sektor 5
    # und einer aus Sektor 1 koennen dieselbe Einfaerbung tragen, wenn der eine
    # juenger ist; was der Bias behauptet, ist der Abstand zum eigenen Ausschlag.
    if einfaerbung > ausschlag + 1e-9:
        logger.error(
            f"Praegung: Einfaerbung {einfaerbung:.6f} liegt ueber dem Ausschlag "
            f"{ausschlag:.6f} (Sektor {sektor}, Faktor {faktor}) — ein Faktor "
            f"unter 1,0 laesst den Affekt langsamer verblassen als die Ladung, "
            f"und das behauptet der Bias nicht"
        )
    return {
        "einfaerbung":       einfaerbung,
        "ausschlag_aktuell": ausschlag,
        "abstand":           ausschlag - einfaerbung,
        "sektor":            sektor,
        "faktor":            faktor,
    }


def alle_einfaerbungen(postgres_url: str, jetzt: datetime | None = None) -> dict:
    """Rechnet die Einfaerbung jedes Fadens und berichtet die Reihe.

    **Der Aufrufer, damit keine Rechenfunktion ohne einen dasteht.** Die
    Einfaerbung hat ihre eigentlichen Leser noch nicht — Ziele, LZG-Erinnerungen
    und EI-Calc (§8) sind nicht gebaut. Bis dahin laeuft sie einmal taeglich
    ueber den Bestand und schreibt ihre Reihe ins Log; genau daran wird
    `PRAEGUNG_SEKTOR_FAKTOR` kalibrierbar, und dieselbe Bauart tragen Richtung,
    Ladung und der Praegungszug.

    **Kein Schreibvorgang, kein Schemawechsel.** Der Lauf liest und rechnet.

    Vorbedingung: keine — ein leerer Bestand ist der Regelfall am Anfang.
    Nachbedingung: `{"gerechnet", "gesamt", "je_sektor", "abstand_max", "error"}`.
        **`gerechnet` und `gesamt` stehen nebeneinander**, weil ein Lauf ueber
        die Haelfte des Bestandes sonst aussaehe wie ein vollstaendiger.
    Fehlerfaelle: Ein Lesefehler wird gemeldet und liefert `gesamt = 0` mit Text
        in `error`; der Tageslauf laeuft weiter.

    Args:
        postgres_url: Verbindung.
        jetzt: Bezugszeitpunkt der Rechnung; ohne Angabe die aktuelle Zeit.

    Returns:
        Die Bilanz des Laufs.
    """
    # ── Eingabe ────────────────────────────────
    bezug: datetime = jetzt or datetime.now(timezone.utc)

    # ── Verarbeitung ───────────────────────────
    try:
        with psycopg2.connect(postgres_url) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT f.id, f.emotion, f.ausschlag_absolut, f.entstanden_am,
                       coalesce(
                           array_agg(b.beruehrt_am ORDER BY b.beruehrt_am)
                           FILTER (WHERE b.beruehrt_am IS NOT NULL),
                           '{}'
                       )
                FROM praegung_faden f
                LEFT JOIN praegung_beruehrung b ON b.faden_id = f.id
                GROUP BY f.id
                ORDER BY f.id
                """,
            )
            zeilen: list = cur.fetchall()
    except Exception as fehler:
        logger.exception(
            f"Praegung: Einfaerbungslauf konnte die Faeden nicht lesen "
            f"({type(fehler).__name__}) — keine Reihe entstanden"
        )
        return {"gerechnet": 0, "gesamt": 0, "je_sektor": {},
                "abstand_max": 0.0, "error": str(fehler)}

    je_sektor:   dict[int | None, int] = {}
    abstand_max: float = 0.0
    gerechnet:   int   = 0
    for faden_id, emotion, absolut, entstanden_am, beruehrungen in zeilen:
        teile: dict = einfaerbung_falten(
            ausschlag_absolut = float(absolut),
            emotion           = emotion,
            entstanden_am     = entstanden_am,
            beruehrungen      = list(beruehrungen or []),
            jetzt             = bezug,
        )
        je_sektor[teile["sektor"]] = je_sektor.get(teile["sektor"], 0) + 1
        abstand_max = max(abstand_max, teile["abstand"])
        gerechnet += 1
        logger.info(
            f"Praegung: Faden {faden_id} ({emotion}, Sektor {teile['sektor']}, "
            f"Faktor {teile['faktor']}) — Ausschlag "
            f"{teile['ausschlag_aktuell']:.6f}, Einfaerbung "
            f"{teile['einfaerbung']:.6f}, Abstand {teile['abstand']:.6f}"
        )

    # ── Ausgabe ────────────────────────────────
    logger.info(
        f"Praegung: Einfaerbungslauf {gerechnet} von {len(zeilen)} Faeden, "
        f"groesster Abstand {abstand_max:.6f}, Sektoren {je_sektor}"
    )
    return {
        "gerechnet":   gerechnet,
        "gesamt":      len(zeilen),
        "je_sektor":   je_sektor,
        "abstand_max": abstand_max,
        "error":       None if gerechnet == len(zeilen) else "unvollstaendig",
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
