"""Der Enricher-Weg — was zu diesem Turn in den freigegebenen Dateien liegt.

Spezifikation: docs/novaberg-agent-dateien_k.md §3.0, §3.0a, §3.0a-bis, §1a.2.

**Das ist die Quelle, die kein Dienst ist.** Sie hat keine Zustellart, keinen
Aushang und keine Quote — sie wird nicht gewaehlt, sie laeuft. Der Enricher
ruft sie in jedem Turn, wie er die Bibliothek ruft; das NMCP-Regelwerk nimmt
den Lesepfad heraus (§3.0).

**Sie liest den Index, nicht die Datei.** Ein Treffer bringt Thema und
Zusammenfassung mit — beides steht in der Indexzeile, beides ist beim
Indizieren einmal bezahlt worden. Kein Dateizugriff, kein Modellaufruf, kein
zweites Embedding: Der Suchschluessel ist derselbe `such_vektor`, mit dem in
diesem Turn auch KZG, LZG und die Bibliothek gesucht haben.

**Die Kappung ist die Zusicherung, die Schwelle ist die Feinjustage** (§3.0a).
Der Boden beantwortet "ob ueberhaupt", die Kappung "wie viele". Beide sind
noetig, und sie sind nicht dasselbe: Eine Schwelle allein laesst bei einem
wachsenden Bestand immer mehr durch, eine Kappung allein liefert zu jeder
Frage die besten drei Fehltreffer.

**Das Paar haengt an der Wurzel** (§2.2). Die Indexzeile fuehrt keins; sie
erbt es ueber `wurzel_id`, und deshalb steht hier ein JOIN und keine
Spaltenbedingung.
"""

import logging
from dataclasses import dataclass, field

from config import (
    AUFZEICHNUNGEN_AUSZUG_ZEICHEN,
    AUFZEICHNUNGEN_BODEN,
    AUFZEICHNUNGEN_KAPPUNG,
)
from memory.utils import embedding_zu_pgvector_str
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.dateien_index.aufzeichnungen")


@dataclass(frozen=True)
class Aufzeichnung:
    """Ein Treffer des Enricher-Wegs — eine Datei, nicht ihr Inhalt.

    `fundstelle` ist der Pfad relativ zur Wurzel, ergaenzt um deren
    Bezeichnung. **Sie ist kein Schmuck und keine Zitierhilfe:** Eine
    Aufzeichnung ohne Herkunft ist von einer Behauptung nicht zu
    unterscheiden, und genau das macht "ich habe hier Aufzeichnungen"
    ueberpruefbar statt zur Floskel (§1a.2).
    """

    fundstelle: str
    thema: str
    zusammenfassung: str
    #: Kosinus gegen den `such_vektor` dieses Turns, 0.0 bis 1.0.
    kosinus: float


@dataclass
class Aufzeichnungsfund:
    """Das Ergebnis eines Enricher-Laufs — die Treffer und die Zahlen dazu.

    Die Zahlen sind nicht Zierde: `bestand` und `schlechtester` sind die
    Pruefregel aus §3.0a. **Liegt `len(treffer)` dauerhaft auf der Kappung,
    ist der Boden unbelegt** — dann waehlt die Kappung aus und nicht die
    Schwelle, und genau diesen Zustand hat die Messung bei der Bibliothek
    vorgefunden (40 von 42 Aufrufen).

    Zugleich ist `schlechtester` der Wert, aus dem spaeter die mitlaufende
    Verteilung entsteht (§3.0a-bis): Die wahre Paarung — Anfrage gegen
    Eintrag — faellt in jedem Turn ohnehin an; wer den K-ten Wert mitschreibt,
    sammelt sie ohne zusaetzliche Abfrage.
    """

    treffer: list[Aufzeichnung] = field(default_factory=list)
    #: Wie viele aktive, eingebettete Indexzeilen das Paar ueberhaupt hat.
    bestand: int = 0
    #: Kosinus des schlechtesten **gelieferten** Treffers; 0.0 ohne Treffer.
    schlechtester: float = 0.0


def _fundstelle_bauen(bezeichnung: str, wurzel: str, pfad: str) -> str:
    """Baut die Herkunftsangabe eines Treffers.

    Vorbedingung: `pfad` ist nicht leer — er ist der Teil, der die Datei
    benennt.
    Nachbedingung: Ein Text, der die Datei innerhalb ihrer Freigabe
    bezeichnet. Traegt die Freigabe eine Bezeichnung, steht sie davor: Sie
    ist das, was ein Mensch beim Freigeben gesagt hat, und damit die Form,
    unter der er die Ablage wiedererkennt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not pfad.strip():
        meldung: str = "_fundstelle_bauen: leerer Pfad — die Datei waere unbenannt"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    ort: str = bezeichnung.strip() or wurzel.strip()
    return f"{ort}/{pfad}" if ort else pfad


def aufzeichnungen_suchen(
    such_vektor: list[float], user_id: str, character_id: str,
) -> Aufzeichnungsfund:
    """Sucht die einschlaegigen Indexzeilen dieses Turns.

    Vorbedingung: `such_vektor` traegt den verschobenen Suchschluessel des
    Turns, `user_id` und `character_id` benennen das Paar. Fehlt der
    Suchschluessel, hat in diesem Turn keine Gedaechtnisschicht gesucht —
    dann gibt es auch nichts zu durchsuchen, und der leere Fund ist die
    richtige Antwort und kein Fehler.
    Nachbedingung: Hoechstens `AUFZEICHNUNGEN_KAPPUNG` Treffer, alle mit
    Kosinus **ueber** `AUFZEICHNUNGEN_BODEN` und alle mit nicht-leerer
    Fundstelle. `bestand` und `schlechtester` sind gesetzt, auch wenn kein
    Treffer kam.
    Fehlerfaelle: Ein Datenbankfehler wird protokolliert und ergibt den
    leeren Fund. Der Enricher faengt ihn ohnehin ab — aber dann, ohne zu
    sagen, welcher Teil ausgefallen ist.

    **Ein Turn ohne Treffer ist der Normalfall.** Der Boden ist die
    Cold-Start-Zusicherung: Zu einer Frage, zu der die Ablage nichts hat,
    ist Schweigen die richtige Antwort — ein Block, der drei Fehltreffer als
    "ich habe hier Aufzeichnungen" ausgibt, ist der teuerste denkbare Fehler
    dieses Bauteils (§3.0a-bis).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not such_vektor:
        # Kein Fehler: Kaltstart oder ein Turn ohne Gedaechtnissuche.
        logger.debug(
            "Aufzeichnungen: kein Suchschluessel im State — keine Abfrage",
        )
        return Aufzeichnungsfund()

    if not user_id or not character_id:
        logger.error(
            "Aufzeichnungen: unvollstaendiges Paar (user_id=%r, character_id=%r) "
            "— keine Abfrage. Ohne beide Kennungen stammte der Treffer aus "
            "einer fremden Freigabe",
            user_id, character_id,
        )
        return Aufzeichnungsfund()

    # ── Verarbeitung ────────────────────────────
    vektor_str: str = embedding_zu_pgvector_str(such_vektor)

    try:
        # Der Bestand wird eigens gezaehlt und nicht aus der Trefferzahl
        # abgeleitet: Er ist das `N`, gegen das die Trefferzahl erst etwas
        # aussagt. Ohne ihn ist "drei Treffer" nicht von "drei Dateien
        # insgesamt" zu unterscheiden.
        bestand_zeile: dict | None = db_manager.select_one(
            """
            SELECT COUNT(*) AS anzahl
            FROM   dateien_index i
            JOIN   dateien_wurzeln w ON w.id = i.wurzel_id
            WHERE  w.user_id = %s AND w.character_id = %s
              AND  w.aktiv = TRUE AND i.aktiv = TRUE
              AND  i.themen_embedding IS NOT NULL
            """,
            (user_id, character_id),
        )

        zeilen: list[dict] = db_manager.select(
            """
            SELECT i.pfad, i.thema, i.zusammenfassung,
                   w.pfad AS wurzel, w.bezeichnung,
                   1 - (i.themen_embedding <=> %s::vector) AS kosinus
            FROM   dateien_index i
            JOIN   dateien_wurzeln w ON w.id = i.wurzel_id
            WHERE  w.user_id = %s AND w.character_id = %s
              AND  w.aktiv = TRUE AND i.aktiv = TRUE
              AND  i.themen_embedding IS NOT NULL
              AND  1 - (i.themen_embedding <=> %s::vector) >= %s
            ORDER  BY i.themen_embedding <=> %s::vector
            LIMIT  %s
            """,
            (
                vektor_str, user_id, character_id, vektor_str,
                AUFZEICHNUNGEN_BODEN, vektor_str, AUFZEICHNUNGEN_KAPPUNG,
            ),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Aufzeichnungen: Abfrage des Index fehlgeschlagen — kein "
            "Dateikontext in diesem Turn",
            type(fehler).__name__,
        )
        return Aufzeichnungsfund()

    # ── Ausgabe-Verifikation ────────────────────
    bestand: int = int(bestand_zeile["anzahl"]) if bestand_zeile else 0

    treffer: list[Aufzeichnung] = []
    for zeile in zeilen:
        thema: str = (zeile.get("thema") or "").strip()
        if not thema:
            # Eine Zeile ohne Thema behauptet eine Erschliessung, die nicht
            # stattgefunden hat — der Waechter laesst sie gar nicht erst zu.
            # Steht doch eine da, gehoert sie gemeldet und nicht in den Prompt.
            logger.error(
                "Aufzeichnungen: Indexzeile %r ohne Thema uebersprungen — "
                "sie traegt einen Vektor, aber nichts, was sie benennt",
                zeile.get("pfad"),
            )
            continue

        zusammenfassung: str = (zeile.get("zusammenfassung") or "").strip()
        if len(zusammenfassung) > AUFZEICHNUNGEN_AUSZUG_ZEICHEN:
            zusammenfassung = (
                zusammenfassung[:AUFZEICHNUNGEN_AUSZUG_ZEICHEN].rstrip() + " …"
            )

        treffer.append(Aufzeichnung(
            fundstelle = _fundstelle_bauen(
                zeile.get("bezeichnung") or "",
                zeile.get("wurzel") or "",
                zeile.get("pfad") or "",
            ),
            thema           = thema,
            zusammenfassung = zusammenfassung,
            kosinus         = round(float(zeile["kosinus"]), 4),
        ))

    fund = Aufzeichnungsfund(
        treffer       = treffer,
        bestand       = bestand,
        schlechtester = treffer[-1].kosinus if treffer else 0.0,
    )

    # Die Pruefregel aus §3.0a, als Protokollzeile: Trefferzahl UND Kosinus
    # des schlechtesten gelieferten Treffers, gegen den Bestand. Ohne sie
    # bleibt unbemerkt, dass die Kappung auswaehlt statt des Bodens — der
    # Zustand, in dem die Bibliothek vier Monate lief.
    if treffer:
        logger.info(
            "Aufzeichnungen: %d von %d Indexzeilen ueber dem Boden %.2f "
            "(bester %.4f, schlechtester gelieferter %.4f, Kappung %d)%s",
            len(treffer), bestand, AUFZEICHNUNGEN_BODEN,
            treffer[0].kosinus, fund.schlechtester, AUFZEICHNUNGEN_KAPPUNG,
            " — AUF DER KAPPUNG" if len(treffer) == AUFZEICHNUNGEN_KAPPUNG else "",
        )
    else:
        logger.debug(
            "Aufzeichnungen: kein Treffer ueber dem Boden %.2f bei %d "
            "Indexzeilen — kein Block in diesem Turn",
            AUFZEICHNUNGEN_BODEN, bestand,
        )

    return fund
