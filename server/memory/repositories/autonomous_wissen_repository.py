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

from config import BEOBACHTER_KANON, LZG_KNOTEN_REINFORCEMENT_BOOST
from memory.lzg_knoten import gewicht_absolut_berechnen

logger = logging.getLogger("ki_server.memory.repositories.autonomous_wissen")

# Die geschlossenen Wertemengen der beiden Klassifikationsspalten. Sie stehen
# als Konstanten und nicht nur im Kommentar, weil eine Menge ohne deklarierte
# Obermenge benutzbar, aber nicht prüfbar ist (11_EVA §2, Teilmengen-Falle).
# Kein CHECK in der Datenbank — dieselbe Konvention wie bei pipeline_log.art:
# die schreibende Schicht setzt die Werte durch, nicht das Schema.
WISSEN_TYPEN:  frozenset[str] = frozenset({"wissen", "bericht"})

#: Die Perspektive, unter der die Bibliothek gelesen wird — die dritte Spalte
#: der Paar-Partition.
#:
#: **Sie steht als Konstante und nicht als Literal an jeder Lesestelle.** Der
#: Bestand traegt sie heute einheitlich (gemessen am 23.08.2026: **831 von 831**
#: aktiven Zeilen), weil allein die Hintergrund-Agenten schreiben. Genau
#: deshalb ist der Wert an vier Stellen hinzuschreiben verlockend und falsch:
#: Kommt ein zweiter Schreiber dazu, muessen alle vier zugleich wandern, und
#: wer eine vergisst, bekommt fremde Zeilen als eigene Ausarbeitung geliefert
#: — ohne dass irgendetwas anschlaegt.
BIBLIOTHEK_BEOBACHTER: str = "assistant"
WISSEN_MODI:   frozenset[str] = frozenset({"recherche", "vertiefung", "traum", "nachfragen"})
WISSEN_STATUS: frozenset[str] = frozenset(
    {"echte_tiefe", "ergaenzung", "wiederholung", "fehlschlag"}
)

# Kuerzer als das ist kein Gegenstand, sondern ein Rest der Zerlegung: ein
# leeres Glied nach einem doppelten Trennzeichen oder ein einzelnes Zeichen.
#
# **Der Wert ist am Bestand gemessen und war zuerst falsch geraten.** Ein
# erster Ansatz stand auf 4 und haette echte Themen verworfen — gezaehlt ueber
# alle aktiven Themenfelder: `KI` (4 Vorkommen), `AuD` und `AUM` (je 1). Bei
# Laenge 4 stehen bereits 20 Vorkommen, darunter `Gold`, `Igel`, `Uran`,
# `TQFT` und `vLLM`. Das kuerzeste echte Thema des Bestandes hat also ZWEI
# Zeichen, und eine Abkuerzung ist ein Thema wie jedes andere.
#
# Gefunden hat es ein Zeuge mit dem Fall `"Mut; Vertrauen"`, nicht die
# Ueberlegung beim Schreiben der Konstante.
THEMA_MINDESTLAENGE: int = 2


def themen_zerlegen(themenfeld: str) -> list[str]:
    """Zerlegt das Themenfeld einer Ausarbeitung in seine einzelnen Themen.

    **Die eine Quelle fuer Live-Pfad und Wartungswerkzeug** (`F-EMBED-1`).
    Zwei Zerlegungen erzeugten zwei Mengen von Themenvektoren, und der
    Unterschied fiele erst auf, wenn jemand dieselbe Frage zweimal stellt.

    Der Hintergrund steht in `novaberg-convention-embedding.md` §5: Das Feld
    traegt im Mittel 4,37 Themen, hoechstens 17, und 558 von 559 Feldern mehr
    als eines. Ein einziger Vektor darueber liegt in ihrem Schwerpunkt und ist
    keinem davon nah — gemessen 6 von 40 richtigen Antworten auf Rang 1 gegen
    31 von 40 mit einem Vektor je Thema.

    Vorbedingung: `themenfeld` ist eine Zeichenkette. Leer ist zulaessig und
    ergibt eine leere Liste — eine Ausarbeitung ohne Thema ist ein Fall fuer
    den Aufrufer, nicht fuer die Zerlegung.

    Nachbedingung: eine Liste ohne Dubletten, in der Reihenfolge des Feldes,
    jedes Glied mindestens `THEMA_MINDESTLAENGE` Zeichen lang.

    Args:
        themenfeld: Der Inhalt von `autonomous_wissen.thema`.

    Returns:
        Die einzelnen Themen, entdoppelt und in Reihenfolge.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(themenfeld, str):
        meldung = (
            f"themen_zerlegen: themenfeld ist {type(themenfeld).__name__}, "
            f"erwartet str — eine Zerlegung ueber einem Nicht-Text ergaebe "
            f"Themenvektoren aus einer Zufallsdarstellung"
        )
        raise TypeError(meldung)

    # ── Verarbeitung ────────────────────────────
    # Semikolon und Komma trennen beide; das Semikolon kommt selten vor, aber
    # wo es vorkommt, trennt es genauso.
    roh: list[str] = []
    for teil in themenfeld.replace(";", ",").split(","):
        gestutzt: str = teil.strip()
        if len(gestutzt) >= THEMA_MINDESTLAENGE and gestutzt not in roh:
            roh.append(gestutzt)

    # ── Ausgabe-Verifikation ────────────────────
    # Ein nicht-leeres Feld, das nichts ergibt, ist kein leeres Ergebnis,
    # sondern ein Feld, dessen Inhalt die Zerlegung nicht versteht. Still eine
    # leere Liste zurueckzugeben hiesse, die Ausarbeitung unauffindbar zu
    # machen, ohne dass es jemand bemerkt.
    if themenfeld.strip() and not roh:
        logger.warning(
            "themen_zerlegen: '%s' ergab kein einziges Thema — die "
            "Ausarbeitung bekommt keinen Themenvektor und ist ueber den "
            "Bestell-Weg nicht auffindbar",
            themenfeld[:80],
        )

    return roh


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

    `themen_vektoren` bildet **Thema → Vektor-Literal** ab, für die einzelnen
    Themen des Feldes (Konvention 4). Fehlt ein Thema in der Abbildung oder ist
    sie leer, entsteht die Themenzeile trotzdem — mit `embedding = NULL` und
    damit nachbettbar. Das ist Absicht: Die Zeile zu haben und den Vektor
    nachzureichen ist wiederherstellbar, die Zeile gar nicht zu haben nicht,
    weil dann niemand weiß, dass sie fehlt.

    **Nicht dasselbe wie `themen_embedding`, und es ersetzt es nicht.** Das
    eine trägt den Inhalt der Ausarbeitung für lange Anfragen, das andere ihre
    Themen für kurze — siehe `novaberg-convention-embedding.md` §5.
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
    themen_vektoren:  dict[str, str] | None = None


@dataclass
class Bibliotheksfrage:
    """Was ein Eingang von der Bibliothek wissen will — reiner Datencontainer.

    **Ein Container und nicht acht Argumente**, und der Grund ist nicht die
    Zahl: `user_id`, `character_id` und `beobachter` sind drei Zeichenketten
    nebeneinander, und eine Vertauschung ergäbe eine syntaktisch einwandfreie
    Abfrage über eine Beziehung, die es nicht gibt. Am Feldnamen ist sie nicht
    möglich.

    **Die Partition ist dreispaltig, seit dem 23.08.2026 auch beim Lesen.**
    Bis dahin filterte `suchen` auf zwei Spalten, während die Tabelle drei
    führt — folgenlos, solange allein die Hintergrund-Agenten schreiben
    (gemessen am 23.08.2026: **831 von 831** Zeilen `beobachter='assistant'`;
    die 274 des Befundes stammen vom 19.08.2026), und still in dem
    Moment, in dem ein zweiter Schreiber dazukommt: Fremde Zeilen erschienen
    als eigene Ausarbeitung, ohne dass irgendetwas anschlägt
    (`novaberg-convention-paar-schema.md` §3.2).

    **Die Felder zerfallen in zwei Sorten, und die Grenze ist §6a.1:**
    `typ` und `schwelle` bestimmen die **Ordnung** und sind für beide
    Eingänge gleich; `limit` bestimmt die **Tiefe** und ist es nicht.
    """

    postgres_url: str
    user_id:      str
    character_id: str
    beobachter:   str
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

                # **Auch der Verstaerkungszweig zieht die Themenzeilen nach.**
                # Das Themenfeld kann sich zwischen zwei Laeufen aendern; ein
                # Thema, das daraus verschwindet, muss aus der Suche
                # verschwinden, sonst faende die Bibliothek eine Ausarbeitung
                # ueber etwas, das sie nicht mehr behandelt.
                #
                # `[gemessen]` — 19.08.2026: Diese Zeilen fehlten zuerst, weil
                # der Bau nur den INSERT-Zweig auf der Karte hatte. Gefunden
                # hat es ein Zeuge, den die Gegenprobe erzwungen hat: `Alpha,
                # Beta` verstaerkt zu `Alpha, Gamma` behielt `Beta`.
                themen: list[str] = themen_zerlegen(eintrag.thema)
                AutonomousWissenRepository.themenvektoren_schreiben(
                    postgres_url,
                    zeilen_id,
                    [(th, (eintrag.themen_vektoren or {}).get(th)) for th in themen],
                )

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

            # **Die Themenzeilen entstehen HIER und nicht beim Aufrufer.**
            # Es gibt zwei Schreibwege in diese Tabelle (den Recherche-Pfad
            # ueber `ergebnis_ablegen` und den Rueckweg), und ein dritter
            # kaeme ohne Weiteres dazu. Ein Weg, der die Zerlegung vergisst,
            # legt eine Ausarbeitung ab, die ueber den Bestell-Weg unauffindbar
            # ist — und das faellt niemandem auf, weil eine kurze Trefferliste
            # wie ein enger Bestand aussieht.
            #
            # Ohne gelieferten Vektor bleibt `embedding` NULL. Die Zeile ist
            # dann da und die Ausarbeitung nachbettbar; ohne Zeile waere sie
            # es nicht, weil niemand wuesste, dass sie fehlt.
            themen: list[str] = themen_zerlegen(eintrag.thema)
            AutonomousWissenRepository.themenvektoren_schreiben(
                postgres_url,
                int(zeile[0]),
                [(th, (eintrag.themen_vektoren or {}).get(th)) for th in themen],
            )

            return int(zeile[0])
        finally:
            conn.close()

    @staticmethod
    def themenvektoren_schreiben(
        postgres_url: str, wissen_id: int, themen: list[tuple[str, str | None]],
    ) -> int:
        """Schreibt die Themenvektoren einer Ausarbeitung — je Thema eine Zeile.

        **Ersetzt den Bestand dieser Ausarbeitung vollstaendig.** Ein Thema,
        das nicht mehr im Feld steht, verschwindet damit auch aus der Suche;
        bliebe es stehen, faende die Bibliothek eine Ausarbeitung ueber ein
        Thema, das sie nicht mehr behandelt. Der Austausch laeuft in EINER
        Transaktion — ein Abbruch nach dem Loeschen und vor dem Schreiben
        liesse die Ausarbeitung unauffindbar zurueck.

        Vorbedingung: `wissen_id` ist positiv, `themen` traegt Paare aus Thema
        und pgvector-Literal (oder None fuer "noch nicht eingebettet").
        Nachbedingung: Genau `len(themen)` Zeilen tragen diese `wissen_id`.
        Fehlerfaelle: ungueltige Eingabe (ValueError), Datenbankfehler
        (psycopg2.Error) — beide an den Aufrufer.

        Args:
            postgres_url: Verbindung.
            wissen_id: Die Ausarbeitung, zu der die Themen gehoeren.
            themen: Paare (thema, vektor_literal_oder_None).

        Returns:
            Die Zahl geschriebener Zeilen.
        """
        # ── Eingabe-Validierung ─────────────────────
        if wissen_id <= 0:
            meldung = (
                f"themenvektoren_schreiben: wissen_id={wissen_id} ist nicht "
                f"positiv — es gibt keine Ausarbeitung mit dieser Kennung"
            )
            raise ValueError(meldung)

        for thema, _ in themen:
            if not thema or not thema.strip():
                meldung = (
                    f"themenvektoren_schreiben: leeres Thema fuer Ausarbeitung "
                    f"{wissen_id} — ein Vektor ohne Gegenstand zeigt auf alles"
                )
                raise ValueError(meldung)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM autonomous_wissen_thema WHERE wissen_id = %s",
                        (wissen_id,),
                    )
                    for thema, vektor in themen:
                        cur.execute(
                            "INSERT INTO autonomous_wissen_thema "
                            "(wissen_id, thema, embedding) "
                            "VALUES (%s, %s, %s::vector)",
                            (wissen_id, thema.strip(), vektor),
                        )
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        ohne_vektor: int = sum(1 for _, v in themen if v is None)
        if ohne_vektor:
            logger.warning(
                "themenvektoren_schreiben: %d von %d Themen der Ausarbeitung "
                "%d ohne Vektor abgelegt — sie sind ueber den Bestell-Weg "
                "nicht auffindbar, bis eine Nachbettung laeuft",
                ohne_vektor, len(themen), wissen_id,
            )
        logger.info(
            "themenvektoren_schreiben: %d Themen fuer Ausarbeitung %d",
            len(themen), wissen_id,
        )
        return len(themen)

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
        `frage.typ` liegt in WISSEN_TYPEN, `frage.beobachter` in
        BEOBACHTER_KANON, `frage.limit` ist positiv.
        Nachbedingung: höchstens `frage.limit` Zeilen, absteigend nach Nähe,
        alle über der Schwelle und alle aus der angegebenen **dreispaltigen**
        Partition — Subjekt, Gegenüber und Beobachter.
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

        # Gegen den Kanon, nicht gegen `assistant`: Eine Pruefung auf einen
        # einzelnen erwarteten Wert kann einen unbekannten nicht von einem
        # gueltigen zweiten unterscheiden (11_EVA §2, Teilmengen-Falle).
        if frage.beobachter not in BEOBACHTER_KANON:
            meldung = (
                f"AutonomousWissenRepository.suchen: beobachter="
                f"{frage.beobachter!r} steht nicht im Kanon "
                f"{sorted(BEOBACHTER_KANON)} — die Perspektive ist die dritte "
                f"Spalte der Partition und hat keinen Default"
            )
            raise ValueError(meldung)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(frage.postgres_url)
        try:
            with conn.cursor() as cur:
                # Der Vergleich laeuft gegen die EINZELNEN Themen, nicht
                # gegen einen gemittelten Vektor der Zeile (Konvention 4).
                # `max` waehlt je Ausarbeitung ihr bestpassendes Thema: Eine
                # Ausarbeitung ueber fuenf Dinge ist getroffen, sobald EINES
                # davon gefragt war — und nicht erst, wenn der Durchschnitt
                # aller fuenf nahe genug liegt.
                cur.execute(
                    """
                    SELECT w.thema, w.zusammenfassung, w.dateipfad, w.modus,
                           w.status, w.gewicht_decay, w.haeufigkeit,
                           MAX(1 - (t.embedding <=> %s::vector)) AS cosine
                    FROM   autonomous_wissen w
                    JOIN   autonomous_wissen_thema t ON t.wissen_id = w.id
                    WHERE  w.user_id = %s AND w.character_id = %s
                      AND  w.beobachter = %s
                      AND  w.aktiv = TRUE
                      AND  w.typ = %s
                      AND  t.embedding IS NOT NULL
                    GROUP  BY w.id, w.thema, w.zusammenfassung, w.dateipfad,
                              w.modus, w.status, w.gewicht_decay, w.haeufigkeit
                    HAVING MAX(1 - (t.embedding <=> %s::vector)) >= %s
                    ORDER  BY cosine DESC
                    LIMIT  %s
                    """,
                    (
                        frage.vektor_str, frage.user_id, frage.character_id,
                        frage.beobachter, frage.typ, frage.vektor_str,
                        frage.schwelle, frage.limit,
                    ),
                )
                zeilen: list = cur.fetchall()

                # Eine Ausarbeitung ohne Themenvektoren faellt aus dem JOIN
                # und ist ueber diesen Weg unsichtbar — lautlos, denn eine
                # kurze Trefferliste sieht aus wie ein enger Bestand. Die
                # Zahl gehoert deshalb ins Protokoll, nicht in eine Annahme.
                cur.execute(
                    """
                    SELECT count(*) FROM autonomous_wissen w
                    WHERE  w.user_id = %s AND w.character_id = %s
                      AND  w.beobachter = %s
                      AND  w.aktiv = TRUE AND w.typ = %s
                      AND  NOT EXISTS (SELECT 1 FROM autonomous_wissen_thema t
                                       WHERE t.wissen_id = w.id
                                         AND t.embedding IS NOT NULL)
                    """,
                    (frage.user_id, frage.character_id, frage.beobachter,
                     frage.typ),
                )
                unsichtbar: int = int(cur.fetchone()[0])
                if unsichtbar:
                    logger.warning(
                        "AutonomousWissenRepository.suchen: %d Ausarbeitungen "
                        "ohne Themenvektor — sie sind ueber den Bestell-Weg "
                        "unauffindbar, bis eine Nachbettung laeuft",
                        unsichtbar,
                    )
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
        Nachbedingung: die Zahl der aktiven Zeilen dieser **dreispaltigen**
        Partition und dieses Typs — Subjekt, Gegenüber, Beobachter. Die
        Perspektive ist kein Argument, sondern `BIBLIOTHEK_BEOBACHTER`: Die
        Zahl belegt eine Ablehnung der Bibliothek, und die liest genau eine.
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
                    "AND beobachter = %s "
                    "AND typ = %s AND aktiv = TRUE",
                    (user_id, character_id, BIBLIOTHEK_BEOBACHTER, typ),
                )
                zeile = cur.fetchone()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return int(zeile[0]) if zeile else 0
