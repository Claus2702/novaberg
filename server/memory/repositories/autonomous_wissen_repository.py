"""Datenzugriffsschicht für die autonomous_wissen-Tabelle (Wissens-Bibliothek).

Keine Business-Logik — reine CRUD-Operationen.

Die Tabelle trägt die Metadaten der Bibliothek, nicht ihren Inhalt: wo die
Datei liegt, worum es geht, wie schwer sie wiegt. Der Inhalt liegt als Datei
außerhalb des Arbeitsbaums (tools/dateien/schreiben.py).

Spezifikation: docs/novaberg-autonomous-wissen_k.md §7.2 und §11.
"""

import logging
from dataclasses import dataclass

import psycopg2
from config import LZG_KNOTEN_REINFORCEMENT_BOOST

from memory.lzg_knoten import gewicht_absolut_berechnen

logger = logging.getLogger("ki_server.memory.repositories.autonomous_wissen")

# Die geschlossenen Wertemengen der beiden Klassifikationsspalten. Sie stehen
# als Konstanten und nicht nur im Kommentar, weil eine Menge ohne deklarierte
# Obermenge benutzbar, aber nicht prüfbar ist (11_EVA §2, Teilmengen-Falle).
# Kein CHECK in der Datenbank — dieselbe Konvention wie bei pipeline_log.art:
# die schreibende Schicht setzt die Werte durch, nicht das Schema.
WISSEN_TYPEN:  frozenset[str] = frozenset({"wissen", "bericht"})
WISSEN_MODI:   frozenset[str] = frozenset({"recherche", "vertiefung", "traum", "nachfragen"})
WISSEN_STATUS: frozenset[str] = frozenset(
    {"echte_tiefe", "ergaenzung", "wiederholung", "fehlschlag"}
)


@dataclass
class WissensEintrag:
    """Die Metadaten einer Datei der Bibliothek — reiner Datencontainer.

    Trägt genau die Felder, die eine Zeile in `autonomous_wissen` ausmachen.
    Keine Vorgabewerte für Paar-Schema und Salienz: Die Spalten haben in der
    Datenbank keinen, und ein Container, der hier einen anböte, machte die
    Zusicherung des Schemas wieder rückgängig (§11.2, §11.4).

    `themen_embedding` ist die pgvector-Literal-Darstellung "[v1,v2,...]" oder
    None. None ist ein zulässiger Zustand — die Spalte ist nullbar, und eine
    Zeile ohne Vektor ist über Thema und Paar weiterhin auffindbar.
    """

    dateipfad:        str
    user_id:          str
    character_id:     str
    beobachter:       str
    thema:            str
    zusammenfassung:  str
    typ:              str
    modus:            str
    status:           str
    salienz_anfang:   float
    themen_embedding: str | None = None


@dataclass
class Bibliotheksfrage:
    """Was ein Eingang von der Bibliothek wissen will — reiner Datencontainer.

    **Ein Container und nicht sieben Argumente**, und der Grund ist nicht die
    Zahl: `user_id` und `character_id` sind zwei Zeichenketten nebeneinander,
    und eine Vertauschung ergäbe eine syntaktisch einwandfreie Abfrage über
    eine Beziehung, die es nicht gibt. Am Feldnamen ist sie nicht möglich.

    **Die Felder zerfallen in zwei Sorten, und die Grenze ist §6a.1:**
    `typ` und `schwelle` bestimmen die **Ordnung** und sind für beide
    Eingänge gleich; `limit` bestimmt die **Tiefe** und ist es nicht.
    """

    postgres_url: str
    user_id:      str
    character_id: str
    vektor_str:   str
    typ:          str
    schwelle:     float
    limit:        int


@dataclass
class Bibliothekszeile:
    """Ein Treffer der Bibliothek — reiner Datencontainer.

    Trägt, was beide Eingänge brauchen: den Inhalt (Thema, Zusammenfassung),
    die Fundstelle (Dateipfad) und die beiden Zahlen, an denen ein Treffer
    beurteilt werden kann — sein Gewicht im Gedächtnis und seine Nähe zur
    Frage. Der Kosinus steht ausdrücklich mit dabei: Er ist die Zahl, die
    eine Ablehnung belegbar macht (`novaberg-convention-nmcp.md` §6.8).
    """

    thema:           str
    zusammenfassung: str
    dateipfad:       str
    modus:           str
    status:          str
    gewicht_decay:   float
    haeufigkeit:     int
    cosine:          float


class AutonomousWissenRepository:
    """Datenzugriffsschicht für die autonomous_wissen-Tabelle. Keine Business-Logik."""

    @staticmethod
    def speichern(postgres_url: str, eintrag: WissensEintrag) -> int:
        """Legt die Metadatenzeile einer Wissensdatei an oder verstärkt die vorhandene.

        Ein Dateipfad hat genau eine Zeile (UNIQUE). Trifft ein Schreibvorgang
        auf einen vorhandenen Pfad — dieselbe Recherche zum selben Thema am
        selben Tag —, ist das eine **Verstärkung**: `haeufigkeit` steigt,
        `gewicht_roh` wächst um den Boost, die abgeleiteten Gewichte werden
        neu gerechnet und `verstaerkt_am` rückt vor.

        Die Gewichte folgen der Bauart des lzg_knoten und benutzen dessen
        Konstanten ausdrücklich mit (§11.6): Das erarbeitete Wissen ist
        Langzeitgedächtnis in Dateiform und soll mitgehen, wenn dessen
        Verfall je nachkalibriert wird.

        Vorbedingung: Alle Pflichtfelder sind nicht leer, `salienz_anfang`
        liegt in [0.0, 1.0] und ist echt größer als null — die Spalte hat
        keinen Vorgabewert, und ein Schreiber ohne Salienz soll laut
        scheitern statt eine Null abzulegen (§11.4).
        Nachbedingung: Genau eine Zeile trägt diesen Dateipfad; ihre ID wird
        zurückgegeben.
        Fehlerfälle: leeres Pflichtfeld oder Salienz außerhalb der Spanne
        (ValueError), fehlende RETURNING-Zeile (RuntimeError),
        Datenbankfehler (psycopg2.Error) — alle an den Aufrufer.

        `gewicht_decay` wird materialisiert, nicht bei Abfrage gerechnet.
        Beim Anlegen ist keine Zeit vergangen, der Wert ist deshalb gleich
        `gewicht_absolut`; fortgeschrieben wird er vom Tageslauf (WIS-5).
        """
        # ── Eingabe-Validierung ─────────────────────
        pflicht: dict[str, str] = {
            "dateipfad":       eintrag.dateipfad,
            "user_id":         eintrag.user_id,
            "character_id":    eintrag.character_id,
            "beobachter":      eintrag.beobachter,
            "thema":           eintrag.thema,
            "zusammenfassung": eintrag.zusammenfassung,
            "typ":             eintrag.typ,
            "modus":           eintrag.modus,
            "status":          eintrag.status,
        }
        leer: list[str] = [name for name, wert in pflicht.items() if not (wert or "").strip()]
        if leer:
            meldung: str = (
                f"AutonomousWissenRepository.speichern: Pflichtfelder leer — "
                f"{', '.join(leer)}; Pfad {eintrag.dateipfad or '(keiner)'}"
            )
            raise ValueError(meldung)

        # Zugehörigkeit zum Kanon, nicht nur zu einer Teilmenge: Ein
        # unbekannter Wert ist ein Defekt und kein gültiges Nein.
        kanon: list[tuple[str, str, frozenset[str]]] = [
            ("typ",    eintrag.typ,    WISSEN_TYPEN),
            ("modus",  eintrag.modus,  WISSEN_MODI),
            ("status", eintrag.status, WISSEN_STATUS),
        ]
        for feld, wert, erlaubt in kanon:
            if wert not in erlaubt:
                meldung = (
                    f"AutonomousWissenRepository.speichern: {feld}={wert!r} steht nicht im "
                    f"Kanon {sorted(erlaubt)} — Pfad {eintrag.dateipfad}"
                )
                raise ValueError(meldung)

        if not 0.0 < eintrag.salienz_anfang <= 1.0:
            meldung = (
                f"AutonomousWissenRepository.speichern: "
                f"salienz_anfang={eintrag.salienz_anfang!r} liegt ausserhalb der Spanne "
                f"(0.0, 1.0] — Pfad {eintrag.dateipfad}. Die Spalte hat keinen "
                f"Vorgabewert; ein Schreiber ohne Salienz scheitert hier statt eine "
                f"Null abzulegen"
            )
            raise ValueError(meldung)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()

            # Lesen und Schreiben in einer Transaktion: Die Sinus-Dämpfung
            # steht in Python und nicht in SQL, deshalb kein ON CONFLICT DO
            # UPDATE über die Formel. FOR UPDATE hält die Zeile so lange, wie
            # der neue Wert gerechnet wird.
            cursor.execute(
                "SELECT id, gewicht_roh, haeufigkeit FROM autonomous_wissen "
                "WHERE dateipfad = %s FOR UPDATE",
                (eintrag.dateipfad,),
            )
            vorhanden = cursor.fetchone()

            if vorhanden:
                zeilen_id:   int   = vorhanden[0]
                gewicht_roh: float = float(vorhanden[1]) + LZG_KNOTEN_REINFORCEMENT_BOOST
                haeufigkeit: int   = int(vorhanden[2]) + 1
                gewicht_absolut: float = gewicht_absolut_berechnen(gewicht_roh)

                cursor.execute(
                    """
                    UPDATE autonomous_wissen
                    SET    thema           = %s,
                           zusammenfassung = %s,
                           themen_embedding = COALESCE(%s::vector, themen_embedding),
                           status          = %s,
                           modus           = %s,
                           gewicht_roh     = %s,
                           gewicht_absolut = %s,
                           gewicht_decay   = %s,
                           haeufigkeit     = %s,
                           aktiv           = TRUE,
                           verstaerkt_am   = NOW(),
                           decay_am        = NOW()
                    WHERE  id = %s
                    """,
                    (
                        eintrag.thema, eintrag.zusammenfassung, eintrag.themen_embedding,
                        eintrag.status, eintrag.modus,
                        gewicht_roh, gewicht_absolut, gewicht_absolut, haeufigkeit,
                        zeilen_id,
                    ),
                )
                conn.commit()
                logger.info(
                    f"autonomous_wissen: Zeile {zeilen_id} verstaerkt — "
                    f"Durchlauf {haeufigkeit}, roh {gewicht_roh:.2f}, "
                    f"absolut {gewicht_absolut:.2f}, Pfad {eintrag.dateipfad}"
                )
                return zeilen_id

            gewicht_roh = eintrag.salienz_anfang
            gewicht_absolut = gewicht_absolut_berechnen(gewicht_roh)

            cursor.execute(
                """
                INSERT INTO autonomous_wissen
                    (dateipfad, user_id, character_id, beobachter, thema,
                     zusammenfassung, themen_embedding, typ, modus, status,
                     salienz_anfang, gewicht_roh, gewicht_absolut, gewicht_decay)
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    eintrag.dateipfad, eintrag.user_id, eintrag.character_id,
                    eintrag.beobachter, eintrag.thema, eintrag.zusammenfassung,
                    eintrag.themen_embedding, eintrag.typ, eintrag.modus, eintrag.status,
                    eintrag.salienz_anfang, gewicht_roh, gewicht_absolut, gewicht_absolut,
                ),
            )
            zeile = cursor.fetchone()
            conn.commit()

            # ── Ausgabe-Verifikation ────────────────
            if not zeile:
                meldung = (
                    f"AutonomousWissenRepository.speichern: INSERT ohne RETURNING-Zeile "
                    f"fuer {eintrag.dateipfad}"
                )
                raise RuntimeError(meldung)

            logger.info(
                f"autonomous_wissen: Zeile {zeile[0]} angelegt — "
                f"Salienz {eintrag.salienz_anfang:.2f}, absolut {gewicht_absolut:.2f}, "
                f"Typ {eintrag.typ}, Status {eintrag.status}, Pfad {eintrag.dateipfad}"
            )
            return int(zeile[0])
        finally:
            conn.close()

    @staticmethod
    def suchen(frage: Bibliotheksfrage) -> list[Bibliothekszeile]:
        """Findet Bibliothekszeilen über die Nähe zum Suchschlüssel.

        **Die eine Suche für beide Eingänge** (`novaberg-convention-nmcp.md`
        §6a.1). Die Bibliothek ist über zwei Wege erreichbar — als Quelle, die
        bei jedem Turn beifließt, und seit dem 19.08.2026 als bestellbarer
        Dienst. Zwei Abfragen über denselben Bestand ergäben zwei Rangfolgen,
        die auseinanderlaufen, und die Abweichung fiele erst auf, wenn jemand
        dieselbe Frage zweimal stellt und zwei Antworten bekommt.

        **Was der Eingang wählen darf, ist die Tiefe — nicht die Ordnung.**
        `limit` sagt, wie weit unten gelesen wird; `schwelle` und die
        Sortierung sind für beide dieselben.

        Vorbedingung: `frage.vektor_str` ist eine pgvector-Literaldarstellung,
        `frage.typ` liegt in WISSEN_TYPEN, `frage.limit` ist positiv.
        Nachbedingung: höchstens `frage.limit` Zeilen, absteigend nach Nähe,
        alle über der Schwelle und alle aus dem angegebenen Paar.
        Fehlerfälle: ein Datenbankfehler wird **nicht** verschluckt, sondern
        weitergereicht. Der Grund steht in §6a.2: Wer hier die leere Liste
        zurückgibt, macht *„nichts gefunden"* von *„ich konnte nicht"*
        ununterscheidbar — und genau diese beiden gehören in zwei
        verschiedene Ausgänge.
        """
        # ── Eingabe-Validierung ─────────────────────
        if frage.typ not in WISSEN_TYPEN:
            meldung = (
                f"AutonomousWissenRepository.suchen: typ={frage.typ!r} steht "
                f"nicht im Kanon {sorted(WISSEN_TYPEN)}"
            )
            raise ValueError(meldung)

        if frage.limit <= 0:
            meldung = (
                f"AutonomousWissenRepository.suchen: limit={frage.limit} ist "
                f"nicht positiv — eine Abfrage ohne Obergrenze ist keine Suche"
            )
            raise ValueError(meldung)

        if not frage.user_id or not frage.character_id:
            meldung = (
                f"AutonomousWissenRepository.suchen: unvollstaendiges Paar "
                f"(user_id={frage.user_id!r}, character_id={frage.character_id!r}) "
                f"— ein Treffer ohne Paar kaeme aus einer fremden Beziehung"
            )
            raise ValueError(meldung)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(frage.postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT thema, zusammenfassung, dateipfad, modus, status,
                           gewicht_decay, haeufigkeit,
                           1 - (themen_embedding <=> %s::vector) AS cosine
                    FROM   autonomous_wissen
                    WHERE  user_id = %s AND character_id = %s
                      AND  aktiv = TRUE
                      AND  typ = %s
                      AND  themen_embedding IS NOT NULL
                      AND  1 - (themen_embedding <=> %s::vector) >= %s
                    ORDER  BY themen_embedding <=> %s::vector
                    LIMIT  %s
                    """,
                    (
                        frage.vektor_str, frage.user_id, frage.character_id,
                        frage.typ, frage.vektor_str, frage.schwelle,
                        frage.vektor_str, frage.limit,
                    ),
                )
                zeilen: list = cur.fetchall()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return [
            Bibliothekszeile(
                thema=thema,
                zusammenfassung=zusammenfassung,
                dateipfad=dateipfad,
                modus=modus or "",
                status=status or "",
                gewicht_decay=float(gewicht),
                haeufigkeit=int(haeufigkeit),
                cosine=float(cosine),
            )
            for thema, zusammenfassung, dateipfad, modus, status,
                gewicht, haeufigkeit, cosine in zeilen
        ]

    @staticmethod
    def zaehlen(postgres_url: str, user_id: str, character_id: str, typ: str) -> int:
        """Zählt die aktiven Zeilen eines Paares — der Beleg der Ablehnung.

        Eine Ablehnung ohne Zahl ist eine Behauptung: *„dazu liegt nichts vor"*
        sagt nicht, ob die Bibliothek leer ist oder die Frage danebenlag
        (`novaberg-convention-nmcp.md` §6.8).

        Vorbedingung: `typ` liegt in WISSEN_TYPEN.
        Nachbedingung: die Zahl der aktiven Zeilen dieses Paares und Typs.
        Fehlerfälle: ein Datenbankfehler wird weitergereicht — derselbe Grund
        wie bei `suchen`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if typ not in WISSEN_TYPEN:
            meldung = (
                f"AutonomousWissenRepository.zaehlen: typ={typ!r} steht nicht im "
                f"Kanon {sorted(WISSEN_TYPEN)}"
            )
            raise ValueError(meldung)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM autonomous_wissen "
                    "WHERE user_id = %s AND character_id = %s "
                    "AND typ = %s AND aktiv = TRUE",
                    (user_id, character_id, typ),
                )
                zeile = cur.fetchone()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return int(zeile[0]) if zeile else 0
