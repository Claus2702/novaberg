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
from utils.etikett import mit_etikett
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
    #: Wessen Material hinter der Wurzel liegt: "nutzer" | "figur" |
    #: "gemischt". Sie **erbt** es von der Wurzel, wie das Paar (§2.2) —
    #: eine Datei hat keinen Eigentuemer, eine Freigabe schon.
    #:
    #: **Der Block im Prompt haengt daran** (§1a.2). Bis zum 22.08.2026 gab
    #: es das Feld nicht, und der Block behauptete von jedem Treffer, er sei
    #: fremd. Fuer die Unterlagen des Menschen stimmt das; fuer die
    #: Recherchen, die ihr eigener Hintergrundprozess ablegt, ist es die
    #: Anweisung, das eigene Material einem anderen zuzuschreiben.
    eigentum: str = "nutzer"


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
    #: Welcher Kanal die Treffer geliefert hat: "scharf" | "dense" | "" (keine).
    #: Gehoert in das Protokoll, weil ein Treffer ueber den exakten Begriff
    #: anders verlaesslich ist als einer ueber geschaetzte Naehe — und weil
    #: sonst unbemerkt bleibt, welcher der beiden Kanaele traegt.
    kanal: str = ""


def _fundstelle_bauen(bezeichnung: str, wurzel: str, pfad: str) -> str:
    """Baut die Herkunftsangabe eines Treffers.

    Vorbedingung: `pfad` ist nicht leer — er ist der Teil, der die Datei
    benennt.
    Nachbedingung: Ein Text, der die Datei innerhalb ihrer Freigabe
    bezeichnet. Traegt die Freigabe eine Bezeichnung, steht sie davor: Sie
    ist das, was ein Mensch beim Freigeben gesagt hat, und damit die Form,
    unter der er die Ablage wiedererkennt.

    **Eine archivierte Datei traegt ihr Etikett hier und nicht spaeter.**
    Der Index kennt keinen Unterschied zwischen abgelegt und geltend — er
    haelt beide gleich gut. Wer den Auszug in den Prompt bekommt, saehe
    sonst ein widerrufenes Konzept in derselben Form wie ein geltendes
    (`utils/etikett.py`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not pfad.strip():
        meldung: str = "_fundstelle_bauen: leerer Pfad — die Datei waere unbenannt"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    ort: str = bezeichnung.strip() or wurzel.strip()
    return mit_etikett(f"{ort}/{pfad}" if ort else pfad, pfad)


#: Welcher Kanal einen Treffer geliefert hat. Geschlossene Menge.
KANAL_SCHARF: str = "scharf"
KANAL_DENSE: str = "dense"
KANAELE: frozenset[str] = frozenset({KANAL_SCHARF, KANAL_DENSE})


def _bestand_zaehlen(user_id: str, character_id: str) -> int:
    """Zaehlt die aktiven Indexzeilen des Paares — das `N` der Pruefregel.

    Vorbedingung: beide Kennungen sind gesetzt.
    Nachbedingung: Die Zahl, oder 0 mit Fehlermeldung.

    **Eigens gezaehlt und nicht aus der Trefferzahl abgeleitet:** Ohne `N` ist
    "drei Treffer" nicht von "drei Dateien insgesamt" zu unterscheiden, und
    genau daran haengt die Aussage, ob die Kappung oder der Boden ausgewaehlt
    hat (§3.0a).
    """
    # ── Verarbeitung ────────────────────────────
    try:
        zeile: dict | None = db_manager.select_one(
            """
            SELECT COUNT(*) AS anzahl
            FROM   dateien_index i
            JOIN   dateien_wurzeln w ON w.id = i.wurzel_id
            WHERE  w.user_id = %s AND w.character_id = %s
              AND  w.aktiv = TRUE AND i.aktiv = TRUE
            """,
            (user_id, character_id),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Aufzeichnungen: Bestandszaehlung fehlgeschlagen — die "
            "Pruefregel aus §3.0a laeuft diesen Turn ohne Bezugsgroesse",
            type(fehler).__name__,
        )
        return 0

    # ── Ausgabe-Verifikation ────────────────────
    return int(zeile["anzahl"]) if zeile else 0


def _fund_bauen(zeilen: list[dict], bestand: int, kanal: str) -> Aufzeichnungsfund:
    """Baut den Fund aus Datenbankzeilen — die eine Stelle fuer beide Kanaele.

    Vorbedingung: `zeilen` stammen aus einer der beiden Abfragen und tragen
    `pfad`, `thema`, `wurzel` und `kosinus`; `kanal` ist aus `KANAELE`.
    Nachbedingung: Ein Fund, dessen Treffer alle eine Fundstelle und ein Thema
    haben. Zeilen ohne Thema werden gemeldet und uebersprungen.
    Fehlerfaelle: Ein unbekannter Kanal wird gemeldet — der Fund entsteht
    trotzdem, aber die Herkunftsangabe waere sonst still falsch.

    **Eine Stelle fuer beide Kanaele, damit sie nicht auseinanderlaufen.** Zwei
    Bauwege fuer dieselbe Struktur waeren zwei Formeln fuer dieselbe Spalte —
    der Fall, den `F-EMBED-1` fuer Einbettungstexte beschreibt, hier fuer den
    Prompt-Eintrag.
    """
    # ── Eingabe-Validierung ─────────────────────
    if kanal not in KANAELE:
        logger.error(
            "Aufzeichnungen: unbekannter Kanal %r — der Fund entsteht, aber "
            "seine Herkunft ist nicht belegbar", kanal,
        )

    # ── Verarbeitung ────────────────────────────
    treffer: list[Aufzeichnung] = []
    for zeile in zeilen:
        thema: str = (zeile.get("thema") or "").strip()
        if not thema:
            # Eine Zeile ohne Thema behauptet eine Erschliessung, die nicht
            # stattgefunden hat — der Waechter laesst sie gar nicht erst zu.
            logger.error(
                "Aufzeichnungen: Indexzeile %r ohne Thema uebersprungen — sie "
                "traegt einen Kanal, aber nichts, was sie benennt",
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
            kosinus         = round(float(zeile.get("kosinus") or 0.0), 4),
            eigentum        = (zeile.get("eigentum") or "nutzer").strip(),
        ))

    fund = Aufzeichnungsfund(
        treffer       = treffer,
        bestand       = bestand,
        schlechtester = treffer[-1].kosinus if treffer else 0.0,
        kanal         = kanal if treffer else "",
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Die Pruefregel aus §3.0a, als Protokollzeile: Trefferzahl UND Kosinus des
    # schlechtesten gelieferten Treffers, gegen den Bestand — dazu der Kanal,
    # denn ein exakter Begriff und eine geschaetzte Naehe sind nicht dasselbe.
    if treffer:
        logger.info(
            "Aufzeichnungen: %d von %d Indexzeilen über den Kanal '%s' "
            "(bester %.4f, schlechtester gelieferter %.4f, Kappung %d)%s",
            len(treffer), bestand, kanal,
            treffer[0].kosinus, fund.schlechtester, AUFZEICHNUNGEN_KAPPUNG,
            " — AUF DER KAPPUNG" if len(treffer) == AUFZEICHNUNGEN_KAPPUNG else "",
        )
    else:
        logger.debug(
            "Aufzeichnungen: kein Treffer über Kanal '%s' bei %d Indexzeilen "
            "— kein Block in diesem Turn", kanal, bestand,
        )

    return fund

#: Mindestlaenge eines Lexems, das als scharfer Begriff zaehlt. Kuerzere sind
#: fast immer Funktionswoerter, die die Zerlegung durchgelassen hat.
_LEXEM_MINDESTLAENGE: int = 4


def _scharfe_treffer(
    user_id: str, character_id: str, frage: str, vektor_str: str,
) -> list[dict]:
    """Findet Indexzeilen, deren lexikalischer Kanal einen Begriff der Frage traegt.

    Vorbedingung: `frage` ist der Wortlaut des Turns; `vektor_str` ist der
    pgvector-Text des Suchschluessels oder leer.
    Nachbedingung: Hoechstens `AUFZEICHNUNGEN_KAPPUNG` Zeilen, nach Kosinus
    geordnet, **ohne Bodenpruefung**. Leer, wenn die Frage keinen
    unterscheidenden Begriff traegt oder keiner im Bestand vorkommt.
    Fehlerfaelle: Datenbankfehler werden protokolliert und ergeben eine leere
    Liste — der dense Kanal laeuft danach ohnehin.

    **Warum hier kein Boden gilt:** Der Boden beantwortet *„ist ueberhaupt
    etwas einschlaegig"* fuer den **dense** Kanal, wo Naehe geschaetzt wird.
    Ein exakter Begriff schaetzt nicht: Steht `Schrühbrand` in den
    Stichwoertern der Datei und in der Frage, ist die Datei einschlaegig, und
    kein Kosinus muss das bestaetigen.

    **Warum die Zerlegung Postgres macht und kein Modell:** `to_tsvector`
    liefert die Lexeme ohne Stoppwoerter und ohne Kosten. Gemessen am
    18.08.2026: *„Bei welcher Temperatur laeuft der Schrühbrand?"* ergibt drei
    Lexeme, *„Wie war dein Tag?"* ergibt **keins** — der Kanal loest also von
    selbst nicht aus, wo nichts zu finden ist.

    **Und warum ein Wort unterscheidend sein muss:** Ein Begriff, der die
    Haelfte des Bestandes trifft, sagt nichts ueber die einzelne Datei. Er
    wuerde den Block mit beliebigen Zeilen fuellen und ihm eine
    Einschlaegigkeit andichten, die es nicht gibt — der teuerste denkbare
    Fehler dieses Bauteils (§3.0a-bis).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not frage.strip():
        logger.debug("Aufzeichnungen: kein Wortlaut im Turn — kein scharfer Kanal")
        return []

    # ── Verarbeitung ────────────────────────────
    # Ohne Suchschluessel gibt es nichts zu ordnen; dann entscheidet der Pfad,
    # damit die Reihenfolge wenigstens stabil ist.
    kosinus_ausdruck: str = (
        "1 - (b.themen_embedding <=> %s::vector)" if vektor_str else "0.0"
    )
    ordnung: str = "kosinus DESC" if vektor_str else "b.pfad"

    parameter: list = [user_id, character_id, frage, _LEXEM_MINDESTLAENGE]
    if vektor_str:
        parameter.append(vektor_str)
    parameter.append(AUFZEICHNUNGEN_KAPPUNG)

    try:
        zeilen: list[dict] = db_manager.select(
            f"""
            WITH bestand AS (
                SELECT i.pfad, i.thema, i.zusammenfassung, i.suchtext,
                       i.stichwoerter, i.themen_embedding,
                       w.pfad AS wurzel, w.bezeichnung, w.eigentum
                FROM   dateien_index i
                JOIN   dateien_wurzeln w ON w.id = i.wurzel_id
                WHERE  w.user_id = %s AND w.character_id = %s
                  AND  w.aktiv = TRUE AND i.aktiv = TRUE
                  AND  i.suchtext IS NOT NULL
            ),
            -- Der Treffer braucht BEIDES: den Begriff im lexikalischen Kanal
            -- (das nutzt den GIN-Index und engt ein) UND in den **erhobenen
            -- Stichwoertern** (das entscheidet). Der Grund ist gemessen:
            -- "Temperatur" steht im `suchtext` von `sterntypen.md`, weil es in
            -- der Zusammenfassung vorkommt, und trifft nur 1 von 13 Dateien —
            -- es kommt also durch jeden Haeufigkeitsriegel. Zur Toepferfrage
            -- lieferte der Kanal deshalb eine Sterndatei.
            -- **Seltenheit ist nicht Einschlaegigkeit.** Die Stichwoerter sind
            -- das, was das Modell beim Indizieren als Schluesselbegriffe der
            -- Datei benannt hat; sie tragen die Aussage, der Volltext nicht.
            frage AS (
                SELECT DISTINCT lexeme AS wort
                FROM   unnest(to_tsvector('german', %s))
                WHERE  length(lexeme) >= %s
            ),
            je_wort AS (
                SELECT f.wort, count(*) AS anzahl
                FROM   frage f
                JOIN   bestand b ON (b.suchtext @@ plainto_tsquery('german', f.wort)
                       AND to_tsvector('german',
                               array_to_string(b.stichwoerter, ' '))
                           @@ plainto_tsquery('german', f.wort))
                GROUP  BY f.wort
            ),
            scharf AS (
                SELECT wort FROM je_wort
                WHERE  anzahl <= GREATEST(1, (SELECT count(*) FROM bestand) / 2)
            )
            SELECT DISTINCT b.pfad, b.thema, b.zusammenfassung,
                   b.wurzel, b.bezeichnung, b.eigentum,
                   {kosinus_ausdruck} AS kosinus
            FROM   bestand b
            JOIN   scharf s ON (b.suchtext @@ plainto_tsquery('german', s.wort)
                       AND to_tsvector('german',
                               array_to_string(b.stichwoerter, ' '))
                           @@ plainto_tsquery('german', s.wort))
            ORDER  BY {ordnung}
            LIMIT  %s
            """,  # noqa: S608 — `kosinus_ausdruck` und `ordnung` sind Code-Literale,
            # die ein Boolescher Wert auswaehlt; jede Eingabe laeuft als Parameter,
            tuple(parameter),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Aufzeichnungen: scharfer Kanal fehlgeschlagen — der dense "
            "Kanal entscheidet allein",
            type(fehler).__name__,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    if zeilen:
        logger.info(
            "Aufzeichnungen: scharfer Kanal → %d Treffer ohne Bodenpruefung "
            "(bester Kosinus %.4f)",
            len(zeilen), float(zeilen[0].get("kosinus") or 0.0),
        )
    return zeilen

def aufzeichnungen_suchen(
    such_vektor: list[float], user_id: str, character_id: str, frage: str = "",
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
    if not such_vektor and not frage.strip():
        # Kein Fehler: Kaltstart, oder ein Turn ohne Wortlaut und ohne
        # Gedaechtnissuche. **Der Wortlaut allein genuegt aber**, seit der
        # scharfe Kanal existiert — er braucht keinen Vektor.
        logger.debug(
            "Aufzeichnungen: weder Suchschluessel noch Wortlaut — keine Abfrage",
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
    vektor_str: str = embedding_zu_pgvector_str(such_vektor) if such_vektor else ""
    bestand: int = _bestand_zaehlen(user_id, character_id)

    # **Scharf vor unscharf** (§6.3, seit dem 18.08.2026 auch auf diesem Weg).
    # Der Anlass ist gemessen und widerlegt den Boden von vormittags: `Schrühbrand`
    # steht in den Stichwoertern von `toepferei.md` und erreicht auf dem dense
    # Kanal nur **0,2899** — darunter. Der Einbettungstext mittelt einen exakten
    # Begriff weg; der lexikalische Kanal findet ihn. 7 von 8 Fachbegriffen trafen
    # dort genau eine Datei, und die richtige.
    scharfe: list[dict] = _scharfe_treffer(user_id, character_id, frage, vektor_str)
    if scharfe:
        return _fund_bauen(scharfe, bestand, KANAL_SCHARF)

    if not vektor_str:
        logger.debug(
            "Aufzeichnungen: kein Suchschluessel — der dense Kanal entfaellt, "
            "und der scharfe hat nichts gefunden"
        )
        return Aufzeichnungsfund(bestand=bestand)

    try:
        zeilen: list[dict] = db_manager.select(
            """
            SELECT i.pfad, i.thema, i.zusammenfassung,
                   w.pfad AS wurzel, w.bezeichnung, w.eigentum,
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
        return Aufzeichnungsfund(bestand=bestand)

    # ── Ausgabe-Verifikation ────────────────────
    return _fund_bauen(zeilen, bestand, KANAL_DENSE)
