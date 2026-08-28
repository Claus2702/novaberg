"""Datenzugriffsschicht für die shadow_auftrag-Tabelle (Shadow-Queue).

Keine Business-Logik — reine CRUD-Operationen plus die Salienz-Rechnung, die
zur Tabelle gehört.

Die Queue lag bis zum 15.08.2026 als Redis-Liste unter `shadow_queue:{user_id}`.
Sie ist hierher gezogen, weil das Verfallsmodell eine Zeile braucht, die einen
deaktivierten Auftrag aufbewahrt, ohne ihn im Auswahlpfad mitzulesen.

**Drei Wege aus der Queue, und nur einer ist ein Löschen:** Ein erledigter
Auftrag wird entfernt, ein nach drei Versuchen gescheiterter ebenso — ein
verfallener wird auf `aktiv = FALSE` gesetzt und bleibt.

Spezifikation: docs/novaberg-queue-verfall_k.md §5, §6, §8, §12.
"""

import logging
import math
from dataclasses import dataclass, field

import psycopg2
import psycopg2.extras

from config import (
    QUEUE_DAEMPFUNG_EXP,
    QUEUE_DECAY_RATE,
    QUEUE_SALIENZ_CAP,
    QUEUE_SCHWELLE,
    QUEUE_VERSTAERKUNG_BOOST,
)

logger = logging.getLogger("ki_server.memory.repositories.shadow_auftrag")

# Die Spalten, die der Auswahlpfad und der Dispatcher brauchen. Als Konstante,
# damit Abfrage und Auswertung nicht getrennt voneinander driften.
LESE_SPALTEN: str = (
    "id, user_id, character_id, beobachter, aufgabe, thema, kontext, "
    "intentionen, emotion, modus, arousal, salienz_roh, salienz_absolut, "
    "salienz_decay, haeufigkeit, aktiv, erstellt_am, verstaerkt_am, "
    "decay_am, versuche, bezug_id, ausloeser_turn_id"
)

# Warum eine Zeile stillliegt — die geschlossene Wertemenge der Spalte `grund`.
#
# **`aktiv` und `grund` beantworten zwei Fragen** (`F-STILLLEGUNG-1`): das eine,
# **ob** die Zeile noch gesucht wird, das andere, **warum** sie ist, wie sie
# ist. Ein NULL genuegt nicht — es sagt, dass kein Wert da ist, nicht welcher
# fehlt.
#
# Der Altbestand traegt die leere Zeichenkette. Sie ist kein dritter Grund,
# sondern die Auskunft *vor dem 23.08.2026 stillgelegt, Ausgang unbekannt* —
# eine rueckwirkende Zuordnung waere geraten und nicht gemessen.
GRUND_VERFALL:     str = "verfall"
GRUND_FEHLVERSUCH: str = "fehlversuch"
GRUND_KANON: frozenset[str] = frozenset({"", GRUND_VERFALL, GRUND_FEHLVERSUCH})


def salienz_absolut_berechnen(salienz_roh: float) -> float:
    """Dämpft die frei wachsende `salienz_roh` auf den gesättigten Anker.

    Formel: `cap · sin(min(roh/cap, 1) · π/2) ^ exp` — dieselbe Kurve wie
    `gewicht_absolut_berechnen` der Knoten und wie der KZG-Aufbau, aber mit den
    **Queue-Konstanten**. Die Funktion ist bewusst nicht wiederverwendet: Cap
    ist hier 1,0 statt 10,0, und geteilte Konstanten hießen, dass eine
    Kalibrierung des Gedächtnisses den Auftragshaushalt mitverschiebt.

    Vorbedingung: `salienz_roh` ist nicht negativ.
    Nachbedingung: Ergebnis liegt in [0, cap].

    Args:
        salienz_roh: der Akkumulator.

    Returns:
        Der gedämpfte Anker.
    """
    # ── Eingabe-Validierung ─────────────────────
    if salienz_roh < 0:
        logger.error(
            "salienz_absolut_berechnen: negativer Rohwert %.4f — auf 0 geklemmt",
            salienz_roh,
        )
        salienz_roh = 0.0

    # ── Verarbeitung ────────────────────────────
    anteil: float = min(salienz_roh / QUEUE_SALIENZ_CAP, 1.0)
    absolut: float = QUEUE_SALIENZ_CAP * (
        math.sin(anteil * math.pi / 2) ** QUEUE_DAEMPFUNG_EXP
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 <= absolut <= QUEUE_SALIENZ_CAP:
        logger.error(
            "salienz_absolut_berechnen: Ergebnis %.4f ausserhalb [0, %.2f] "
            "(roh=%.4f) — geklemmt", absolut, QUEUE_SALIENZ_CAP, salienz_roh,
        )
        absolut = max(0.0, min(QUEUE_SALIENZ_CAP, absolut))
    return absolut


def salienz_roh_zurueckrechnen(salienz_absolut: float) -> float:
    """Die Umkehrung von `salienz_absolut_berechnen`.

    Gebraucht an zwei Stellen: bei der Übernahme eines Bestands, der nur den
    gedämpften Wert kennt, und beim Einreihen — die eingehende KZG-Salienz ist
    bereits gedämpft, und eine spätere Verstärkung muss auf der Kurve
    **weiterlaufen** statt bei null zu beginnen.

    Vorbedingung: `salienz_absolut` liegt in [0, cap].
    Nachbedingung: Ergebnis liegt in [0, cap] und erfüllt
        `salienz_absolut_berechnen(ergebnis) == salienz_absolut`.

    Args:
        salienz_absolut: der gedämpfte Wert.

    Returns:
        Der Rohwert, der zu diesem Anker führt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0.0 <= salienz_absolut <= QUEUE_SALIENZ_CAP:
        logger.error(
            "salienz_roh_zurueckrechnen: %.4f ausserhalb [0, %.2f] — geklemmt",
            salienz_absolut, QUEUE_SALIENZ_CAP,
        )
        salienz_absolut = max(0.0, min(QUEUE_SALIENZ_CAP, salienz_absolut))

    # ── Verarbeitung / Ausgabe ──────────────────
    anteil: float = (salienz_absolut / QUEUE_SALIENZ_CAP) ** (1 / QUEUE_DAEMPFUNG_EXP)
    return QUEUE_SALIENZ_CAP * (math.asin(min(anteil, 1.0)) * 2 / math.pi)


def halbreaktivierungs_wert(salienz_absolut: float) -> float:
    """Der Wert, auf den ein ruhender Auftrag beim Wecken springt.

    `(anker + schwelle) / 2` — die Mitte zwischen Deaktivierungsschwelle und
    Anker, also **50 % des Bandes über der Schwelle**. Übernommen aus
    `novaberg-memory-synapsen_k.md` §9.3.

    **Nicht `anker × 0,5`:** Ein halbierter Anker läge bei einem schwachen
    Auftrag unter der Schwelle und deaktivierte ihn in dem Zug, in dem er
    geweckt wird.

    Vorbedingung: keine.
    Nachbedingung: Ergebnis liegt echt über `QUEUE_SCHWELLE`, solange der
        Anker es tut.

    Args:
        salienz_absolut: der Anker des ruhenden Auftrags.

    Returns:
        Die Präsenz nach dem Wecken.
    """
    # ── Verarbeitung / Ausgabe ──────────────────
    return (salienz_absolut + QUEUE_SCHWELLE) / 2


@dataclass
class ShadowAuftrag:
    """Ein Auftrag der Shadow-Queue — reiner Datencontainer.

    Keine Vorgabewerte für Paar-Tripel, Gegenstand und Salienz: Die Spalten
    haben in der Datenbank keinen, und ein Container, der hier einen anböte,
    machte die Zusicherung des Schemas wieder rückgängig. Genau so entstanden
    233 Aufträge mit Salienz 0,0 (`KANDIDATEN-PRIORITAET-STILLE-NULL`).
    """

    user_id:      str
    character_id: str
    beobachter:   str
    aufgabe:      str
    thema:        str
    salienz:      float
    kontext:      str = ""
    intentionen:  list[str] = field(default_factory=list)
    emotion:      str = ""
    modus:        str = ""
    # **None heisst unbekannt und wird nie zu einer Zahl.** Anders als die
    # beiden Nachbarn hat die Erregung keinen leeren Ersatzwert: Eine 0.5
    # saehe wie eine Messung aus und hoebe beim Einwurf Novas Zustand auf
    # eine erfundene Zahl (Bauteil B).
    arousal:      float | None = None
    #: Die Zeile, aus der der Auftrag entstand — heute `autonomous_wissen.id`
    #: beim Verweis. **Kein Fremdschluessel** (`F-VERFALL-1` b: eine ID, die
    #: anderswo als Fremdschluessel dient, verfaellt nicht mehr) und deshalb
    #: auch keine Zusicherung, dass die Zeile noch existiert. Ihr einziger
    #: Leser benutzt sie als **Ausschluss**; eine ins Leere zeigende ID
    #: kostet dort einen Kandidaten zu viel und sonst nichts.
    bezug_id:     int | None = None
    #: Der Turn, aus dem der Auftrag entstand — das erste Glied der
    #: Sachlage-Bruecke (`novaberg-thinking-lage_k.md` §4, Scheibe 4). `None`
    #: heisst unbekannt; ein Erzeuger ohne Turnbezug (Promotion-Queue,
    #: Verweis) traegt keinen, und der Leser faellt auf die Vektorsuche
    #: zurueck. Kein Fremdschluessel: Turns haben keine Tabelle.
    ausloeser_turn_id: str | None = None


class ShadowAuftragRepository:
    """Datenzugriffsschicht für die shadow_auftrag-Tabelle. Keine Business-Logik."""

    @staticmethod
    def einreihen(postgres_url: str, auftrag: ShadowAuftrag) -> tuple[int, str]:
        """Reiht einen Auftrag ein — oder verstärkt den vorhandenen zum selben Gegenstand.

        Drei Ausgänge, und der Rückgabewert benennt, welcher eintrat:

        | Lage | Wirkung | Vorgang |
        |---|---|---|
        | kein Auftrag zum Gegenstand | neue Zeile | `"angelegt"` |
        | vorhanden und aktiv | `salienz_roh += BOOST`, Uhr zurück | `"verstaerkt"` |
        | vorhanden und ruhend | Halbreaktivierung, Uhr zurück | `"reaktiviert"` |

        **Ein leeres `thema` ist von der Dublettenerkennung ausgenommen** (§6.2):
        Am 15.08.2026 trugen 145 von 1036 Aufträgen keins, und über
        `aufgabe + thema` bildeten sie eine einzige Gruppe. Ohne die Ausnahme
        verschmölzen 141 unverwandte Aufträge zu einem, dessen `haeufigkeit`
        auf 141 stiege — aus einem fehlenden Wert würde der wichtigste Eintrag
        der Queue.

        **Die Wirkung der Verstärkung sitzt in `verstaerkt_am`**, nicht im
        Boost: Der Auftrag bekommt volle 30 Tage neu, der Boost hebt den Anker
        um Bruchteile (§12.2).

        Vorbedingung: `auftrag` trägt Paar-Tripel, Aufgabe und Salienz.
        Nachbedingung: Genau eine Zeile trägt den Gegenstand, und ihre Uhr
            steht auf jetzt.
        Fehlerfälle: Datenbankfehler werden protokolliert und weitergereicht —
            ein stillschweigend verlorener Auftrag wäre teurer als ein lauter
            Abbruch.

        Args:
            postgres_url: Verbindungsstring.
            auftrag: der einzureihende Auftrag.

        Returns:
            (id der Zeile, Vorgang).
        """
        # ── Eingabe-Validierung ─────────────────────
        if not auftrag.user_id or not auftrag.character_id or not auftrag.beobachter:
            raise ValueError(f"einreihen: unvollstaendiges Paar-Tripel — {auftrag!r}")
        if not auftrag.aufgabe:
            raise ValueError(f"einreihen: Auftrag ohne Aufgabenart — {auftrag!r}")

        absolut: float = max(0.0, min(QUEUE_SALIENZ_CAP, auftrag.salienz))
        roh:     float = salienz_roh_zurueckrechnen(absolut)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                vorhanden = None
                if auftrag.thema.strip():
                    cur.execute(
                        """
                        SELECT id, salienz_roh, salienz_absolut, aktiv
                        FROM   shadow_auftrag
                        WHERE  user_id = %s AND character_id = %s
                          AND  aufgabe = %s AND thema = %s
                        ORDER BY id
                        LIMIT 1
                        """,
                        (auftrag.user_id, auftrag.character_id,
                         auftrag.aufgabe, auftrag.thema),
                    )
                    vorhanden = cur.fetchone()

                if vorhanden is None:
                    cur.execute(
                        """
                        INSERT INTO shadow_auftrag
                            (user_id, character_id, beobachter, aufgabe, thema,
                             kontext, intentionen, emotion, modus, arousal,
                             salienz_roh, salienz_absolut, salienz_decay,
                             bezug_id, ausloeser_turn_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (auftrag.user_id, auftrag.character_id, auftrag.beobachter,
                         auftrag.aufgabe, auftrag.thema, auftrag.kontext,
                         auftrag.intentionen, auftrag.emotion, auftrag.modus,
                         auftrag.arousal, roh, absolut, absolut,
                         auftrag.bezug_id, auftrag.ausloeser_turn_id),
                    )
                    neue_id: int = cur.fetchone()[0]
                    conn.commit()
                    logger.info(
                        "Queue: '%s' fuer '%s' angelegt (salienz=%.4f) — %s",
                        auftrag.aufgabe, auftrag.user_id, absolut,
                        auftrag.thema[:60] or "<ohne Thema>",
                    )
                    return neue_id, "angelegt"

                zeile_id, alt_roh, alt_absolut, war_aktiv = vorhanden
                neu_roh:     float = alt_roh + QUEUE_VERSTAERKUNG_BOOST
                neu_absolut: float = salienz_absolut_berechnen(neu_roh)
                # Ein ruhender Auftrag wird geweckt statt fortgeschrieben: Er
                # springt auf die Mitte des Bandes ueber der Schwelle, nicht
                # auf seinen alten Anker (§6).
                neu_decay: float = (
                    neu_absolut if war_aktiv else halbreaktivierungs_wert(alt_absolut)
                )
                # **Das Wecken raeumt `grund` und `versuche` mit.** Beide
                # beschreiben den **vorigen** Ausgang, und eine aktive Zeile
                # hat keinen: Der Kanon der Spalte kennt `''`, `verfall` und
                # `fehlversuch`, und die letzten beiden sind Aussagen ueber
                # eine ruhende Zeile.
                #
                # **Bei `versuche` haengt Verhalten daran, und zwar erst seit
                # dem 23.08.2026.** Bis dahin loeschte `versuch_zaehlen` an der
                # Grenze hart — eine gescheiterte Zeile war fort, und ein
                # neuer Anlass legte eine frische mit `versuche = 0` an. Seit
                # sie stillgelegt statt geloescht wird, weckt `einreihen`
                # genau diese Zeile wieder auf; ohne Ruecksetzung traegt sie
                # ihr volles Fehlversuchsbudget von damals, und der naechste
                # Fehlschlag erfuellt `versuche >= grenze` sofort. Der Weckpfad
                # bekaeme damit ein Retry-Budget von **null** statt drei.
                cur.execute(
                    """
                    UPDATE shadow_auftrag
                    SET    salienz_roh     = %s,
                           salienz_absolut = %s,
                           salienz_decay   = %s,
                           haeufigkeit     = haeufigkeit + 1,
                           aktiv           = TRUE,
                           grund           = '',
                           versuche        = 0,
                           verstaerkt_am   = NOW(),
                           decay_am        = NOW()
                    WHERE  id = %s
                    """,
                    (neu_roh, neu_absolut, neu_decay, zeile_id),
                )
                conn.commit()
                vorgang: str = "verstaerkt" if war_aktiv else "reaktiviert"
                logger.info(
                    "Queue: '%s' fuer '%s' %s (id=%s, salienz %.4f -> %.4f) — %s",
                    auftrag.aufgabe, auftrag.user_id, vorgang, zeile_id,
                    alt_absolut, neu_decay, auftrag.thema[:60],
                )
                return zeile_id, vorgang
        except psycopg2.Error:
            conn.rollback()
            logger.exception(
                "Queue: Einreihen fehlgeschlagen — aufgabe='%s', user='%s', thema='%s'",
                auftrag.aufgabe, auftrag.user_id, auftrag.thema[:60],
            )
            raise
        finally:
            conn.close()

    @staticmethod
    def bester_kandidat(
        postgres_url: str,
        user_id:      str,
        character_id: str,
    ) -> dict | None:
        """Der dringlichste aktive Auftrag eines Paares.

        **Die Rangfolge ist Dringlichkeit, und weil der Verfall sie über die
        Zeit senkt, ist der jüngste Auftrag zugleich der dringlichste** (§12.3).
        Das kehrt die Ordnung der Redis-Fassung um, die unter Gleichständen
        den ältesten Eintrag nahm — dort war das keine Entscheidung, sondern
        eine Folge der Einfügereihenfolge.

        Vorbedingung: Paar-Kennungen sind gesetzt.
        Nachbedingung: Der gelieferte Auftrag ist aktiv, oder es ist keiner da.
        Fehlerfälle: Datenbankfehler werden protokolliert; die Funktion liefert
            dann None und der Aufrufer sieht eine leere Queue — deshalb steht
            die Fehlerzeile auf `error` und nicht auf `debug`.

        Args:
            postgres_url: Verbindungsstring.
            user_id: Subjekt des Paares.
            character_id: Gegenüber des Paares.

        Returns:
            Der Auftrag als Dict, oder None wenn keiner wartet.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not user_id or not character_id:
            logger.error(
                "bester_kandidat: unvollstaendiges Paar (user='%s', character='%s')",
                user_id, character_id,
            )
            return None

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT {LESE_SPALTEN}
                    FROM   shadow_auftrag
                    WHERE  user_id = %s AND character_id = %s AND aktiv = TRUE
                    ORDER BY salienz_decay DESC, id DESC
                    LIMIT 1
                    """,  # noqa: S608 — LESE_SPALTEN ist eine Konstante, kein Eingabewert
                    (user_id, character_id),
                )
                zeile = cur.fetchone()
        except psycopg2.Error:
            logger.exception(
                "Queue: Kandidatensuche fehlgeschlagen (user='%s') — "
                "der Aufrufer sieht eine leere Queue", user_id,
            )
            return None
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if zeile is None:
            return None
        if not zeile["aktiv"]:
            logger.error(
                "Queue: Kandidat id=%s ist inaktiv, obwohl die Abfrage darauf "
                "filtert — Auftrag verworfen", zeile["id"],
            )
            return None
        return dict(zeile)

    @staticmethod
    def entfernen(postgres_url: str, auftrag_id: int) -> bool:
        """Nimmt einen erledigten Auftrag aus der Queue.

        **Das ist das einzige Löschen, das keiner Begründung bedarf** (§12.1):
        Was abgearbeitet wurde, ist erledigt. Der Verfall löscht nie, er
        deaktiviert.

        Gegenüber der Redis-Fassung ändert sich die Technik und damit die
        Verlässlichkeit: `LREM key 1 <rohsatz>` traf den Eintrag über seinen
        **exakten JSON-Wortlaut** und war bei jeder Abweichung wirkungslos und
        stumm. Ein Primärschlüssel kann das nicht.

        Vorbedingung: `auftrag_id` ist positiv.
        Nachbedingung: Die Zeile existiert nicht mehr.
        Fehlerfälle: Trifft die Löschung keine Zeile, wird das **gemeldet** —
            es heißt, dass jemand anders sie schon entfernt hat.

        Args:
            postgres_url: Verbindungsstring.
            auftrag_id: Primärschlüssel der Zeile.

        Returns:
            True, wenn genau eine Zeile entfernt wurde.
        """
        # ── Eingabe-Validierung ─────────────────────
        if auftrag_id <= 0:
            logger.error("entfernen: ungueltige id %s", auftrag_id)
            return False

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM shadow_auftrag WHERE id = %s", (auftrag_id,))
                getroffen: int = cur.rowcount
            conn.commit()
        except psycopg2.Error:
            conn.rollback()
            logger.exception("Queue: Entfernen von id=%s fehlgeschlagen", auftrag_id)
            return False
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if getroffen != 1:
            logger.error(
                "Queue: Entfernen von id=%s traf %s Zeilen statt einer — der "
                "Auftrag war bereits weg", auftrag_id, getroffen,
            )
            return False
        logger.debug("Queue: Auftrag id=%s entfernt (erledigt)", auftrag_id)
        return True

    @staticmethod
    def versuch_zaehlen(postgres_url: str, auftrag_id: int, grenze: int) -> str:
        """Zählt einen Fehlversuch — und legt den Auftrag an der Grenze still.

        **Seit dem 23.08.2026 kein Löschpfad mehr.** Bis dahin führte dieser
        Weg ein `DELETE`, formal gedeckt: Die Verfallskonvention hatte hartes
        Löschen für den *Verfall* verworfen, und ein gescheiterter Auftrag ist
        ein Ausführungsfehler, kein Verfall (§14). Gegen die Messung vom
        16.08.2026 hielt die Abgrenzung nicht — über 582 aktive
        `recherche`-Einträge stieg die mittlere `salienz_roh` monoton mit der
        Zahl der Versuche (0,867 · 0,947 · 0,990), weil der Wichtigste zuerst
        gezogen wird und das meiste Material hat. **Der Verfall entfernte weich,
        was niemanden interessiert; der Fehlversuch hart, was am meisten
        interessiert.**

        Stillgelegt wird mit Grund, nicht nur mit `aktiv = FALSE`: Ohne ihn
        wäre ein gescheiterter Auftrag von einem verfallenen nicht zu
        unterscheiden, und die Zeile behauptete etwas Falsches über ihren
        eigenen Ausgang.

        Gegenüber der Redis-Fassung entfällt eine Lücke: Dort wurde der Eintrag
        entfernt und neu ans Ende geschrieben — stürzte der Dienst zwischen
        beiden Schritten ab, war der Auftrag weg.

        Vorbedingung: `grenze` ist positiv.
        Nachbedingung: Der Zähler ist erhöht, oder die Zeile trägt
        `aktiv = FALSE` und `grund = GRUND_FEHLVERSUCH` — sie bleibt lesbar.

        Args:
            postgres_url: Verbindungsstring.
            auftrag_id: Primärschlüssel der Zeile.
            grenze: Zahl der Versuche, ab der verworfen wird.

        Returns:
            `"gezaehlt"`, `"verworfen"` oder `"fehler"`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if grenze <= 0:
            logger.error("versuch_zaehlen: ungueltige Grenze %s", grenze)
            return "fehler"

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE shadow_auftrag SET versuche = versuche + 1 "
                    "WHERE id = %s RETURNING versuche, aufgabe",
                    (auftrag_id,),
                )
                zeile = cur.fetchone()
                if zeile is None:
                    conn.rollback()
                    logger.error(
                        "Queue: Fehlversuch fuer id=%s, aber die Zeile existiert "
                        "nicht mehr", auftrag_id,
                    )
                    return "fehler"

                versuche, aufgabe = zeile
                if versuche >= grenze:
                    cur.execute(
                        "UPDATE shadow_auftrag SET aktiv = FALSE, grund = %s "
                        "WHERE id = %s",
                        (GRUND_FEHLVERSUCH, auftrag_id),
                    )
                    conn.commit()
                    logger.warning(
                        "Queue: Auftrag '%s' (id=%s) nach %s Fehlversuchen "
                        "stillgelegt (grund=%s) — die Zeile bleibt lesbar",
                        aufgabe, auftrag_id, versuche, GRUND_FEHLVERSUCH,
                    )
                    return "verworfen"

                conn.commit()
                logger.info(
                    "Queue: Fehlversuch %s/%s fuer '%s' (id=%s)",
                    versuche, grenze, aufgabe, auftrag_id,
                )
                return "gezaehlt"
        except psycopg2.Error:
            conn.rollback()
            logger.exception("Queue: Versuchszaehlung fuer id=%s fehlgeschlagen", auftrag_id)
            return "fehler"
        finally:
            conn.close()

    @staticmethod
    def verfall_lauf(
        postgres_url: str,
        decay_rate:   float | None = None,
        schwelle:     float | None = None,
    ) -> dict:
        """Materialisiert `salienz_decay` für alle aktiven Aufträge und deaktiviert die schwachen.

        Zwei Anweisungen in einer Transaktion, nach dem Vorbild von
        `run_node_decay`:

            salienz_decay = salienz_absolut · exp(−rate · Tage seit verstaerkt_am)
            aktiv = FALSE, wo salienz_decay < schwelle

        `salienz_absolut` bleibt **unangetastet** — sie ist die Erinnerung
        daran, wie dringlich der Auftrag einmal war, und die Bezugsgröße der
        Halbreaktivierung.

        **Der Wert wird materialisiert, nicht bei der Abfrage gerechnet.** Der
        Auswahlpfad liest die Spalte über einen Index; eine Berechnung zur
        Abfragezeit machte den Index wertlos.

        Vorbedingung: Rate und Schwelle sind nicht negativ.
        Nachbedingung: Kein aktiver Auftrag liegt unter der Schwelle.
        Fehlerfälle: Datenbankfehler werden protokolliert und im Ergebnis
            benannt — der Aufrufer schreibt daraus seinen Audit-Eintrag.

        Args:
            postgres_url: Verbindungsstring.
            decay_rate: Verfallsrate je Tag. None -> Konfigurationswert.
            schwelle: Deaktivierungsschwelle. None -> Konfigurationswert.

        Returns:
            dict mit `verarbeitet`, `deaktiviert`, `deaktivierte_ids`, `error`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if decay_rate is None:
            decay_rate = QUEUE_DECAY_RATE
        if schwelle is None:
            schwelle = QUEUE_SCHWELLE

        ergebnis: dict = {
            "verarbeitet": 0, "deaktiviert": 0, "deaktivierte_ids": [], "error": None,
        }
        if decay_rate < 0 or schwelle < 0:
            fehler: str = f"ungueltige Parameter: rate={decay_rate}, schwelle={schwelle}"
            logger.error("Queue-Verfall abgebrochen: %s", fehler)
            ergebnis["error"] = fehler
            return ergebnis

        logger.info(
            "Queue-Verfall startet: rate=%.5f/Tag, schwelle=%.2f", decay_rate, schwelle,
        )

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE shadow_auftrag
                    SET    salienz_decay = salienz_absolut
                             * exp(-%s * (EXTRACT(EPOCH FROM (NOW() - verstaerkt_am)) / 86400.0)),
                           decay_am = NOW()
                    WHERE  aktiv = TRUE
                    """,
                    (decay_rate,),
                )
                verarbeitet: int = cur.rowcount

                # Liest die eben geschriebenen Werte — dieselbe Transaktion.
                cur.execute(
                    "UPDATE shadow_auftrag SET aktiv = FALSE, grund = %s "
                    "WHERE aktiv = TRUE AND salienz_decay < %s RETURNING id",
                    (GRUND_VERFALL, schwelle),
                )
                deaktivierte_ids: list[int] = [z[0] for z in cur.fetchall()]
            conn.commit()
        except psycopg2.Error as ex:
            conn.rollback()
            logger.exception("Queue-Verfall fehlgeschlagen")
            ergebnis["error"] = f"{type(ex).__name__}: {ex}"
            return ergebnis
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if len(deaktivierte_ids) > verarbeitet:
            logger.error(
                "Queue-Verfall: %s deaktiviert bei %s verarbeiteten — "
                "unmoeglich, bitte pruefen", len(deaktivierte_ids), verarbeitet,
            )
        ergebnis["verarbeitet"] = verarbeitet
        ergebnis["deaktiviert"] = len(deaktivierte_ids)
        ergebnis["deaktivierte_ids"] = deaktivierte_ids
        logger.info(
            "Queue-Verfall abgeschlossen: %s verarbeitet, %s deaktiviert",
            verarbeitet, len(deaktivierte_ids),
        )
        return ergebnis

    @staticmethod
    def bestand(postgres_url: str, user_id: str, character_id: str) -> dict:
        """Zählt aktive und ruhende Aufträge eines Paares.

        Für Messung und Audit — der Verfallslauf meldet, was er tat, und diese
        Funktion belegt, was danach liegt.

        Vorbedingung: keine.
        Nachbedingung: Die Summe beider Zahlen ist der Gesamtbestand.

        Args:
            postgres_url: Verbindungsstring.
            user_id: Subjekt des Paares.
            character_id: Gegenüber des Paares.

        Returns:
            dict mit `aktiv` und `ruhend`.
        """
        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FILTER (WHERE aktiv),
                           COUNT(*) FILTER (WHERE NOT aktiv)
                    FROM   shadow_auftrag
                    WHERE  user_id = %s AND character_id = %s
                    """,
                    (user_id, character_id),
                )
                aktiv, ruhend = cur.fetchone()
        except psycopg2.Error:
            logger.exception("Queue: Bestandszaehlung fuer '%s' fehlgeschlagen", user_id)
            return {"aktiv": 0, "ruhend": 0, "error": "Zaehlung fehlgeschlagen"}
        finally:
            conn.close()

        # ── Ausgabe ─────────────────────────────────
        return {"aktiv": aktiv, "ruhend": ruhend}
