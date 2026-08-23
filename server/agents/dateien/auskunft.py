"""Die Auskunft — was der Dienst zurückgibt, und woran man ihre Herkunft sieht.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.2, §10 · §1a.4.

**Dieses Modul entscheidet nichts. Es beschriftet.** Der Text, den es baut,
wandert über `management_result` in den Aufgabenblock des Verfassers — und ist
damit das Letzte, was zwischen dem Dateiinhalt und ihrer Antwort steht.

> **Jede Zeile trägt ihre Fundstelle** (§10). Nicht damit sie zitierfähig ist,
> sondern damit *„das steht so in den Unterlagen"* von *„so ist es"*
> unterscheidbar bleibt. Am 18.08.2026 gemessen: Die Zuschreibung hält, wenn
> die Fundstelle im Text steht — sie überlebt sogar den Übergang ins Gedächtnis
> (§1a.4). Was nicht dasteht, kann auch nicht überleben.

**Kein Dateizugriff, keine Abfrage.** Was hier ankommt, hat `suche.py` gefunden
und `zoom.py` gelesen.
"""

import logging

from utils.etikett import mit_etikett

from agents.dateien.suche import KANAL_NAME, KANAL_STICHWORT, KANAL_VEKTOR
from agents.dateien.zoom import STUFE_BLOCK, STUFE_KARTE, STUFE_NADEL

logger = logging.getLogger("ki_server.agents.dateien.auskunft")

#: Wie der Kanal im Text heißt. Der Mensch darf wissen, wie sicher der Treffer
#: ist: Ein Name trifft exakt, ein Fachbegriff trifft exakt, eine Bedeutung
#: wird geschätzt — und eine Schätzung kann danebenliegen.
_KANAL_TEXT: dict[str, str] = {
    KANAL_NAME:      "über den Dateinamen",
    KANAL_STICHWORT: "über einen Fachbegriff",
    KANAL_VEKTOR:    "über die Bedeutung, also geschätzt",
}

#: Höchstzahl der Nadeltreffer im Text. Was darüber liegt, wird gezählt statt
#: gezeigt — eine Antwort mit vierzig Zeilen ist keine Auskunft mehr.
TREFFER_IM_TEXT: int = 12

#: Höchstzahl der Blocküberschriften, die als Angebot genannt werden.
KARTE_IM_TEXT: int = 10


def fundstelle(kandidat: dict) -> str:
    """Der Ort einer Datei, wie ein Mensch ihn nennt.

    Vorbedingung: `kandidat` stammt aus `suche.py` und trägt `pfad` und `wurzel`.
    Nachbedingung: Ein Pfad aus Wurzel und relativem Pfad — oder der relative
    Pfad allein mit Meldung, wenn die Wurzel fehlt. **Nie eine leere
    Zeichenkette**: Eine Auskunft ohne Ort ist genau die Aussage, gegen die
    dieses Modul gebaut ist.

    **Eine archivierte Datei traegt ihr Etikett** (`utils/etikett.py`).
    Die Regel steht dort und nicht hier, weil der Enricher-Weg dieselbe
    Angabe baut: Zwei getippte Fassungen derselben Regel laufen auseinander,
    und die Haelfte ohne Etikett gibt Widerrufenes als geltend aus.
    """
    # ── Eingabe-Validierung ─────────────────────
    pfad: str = (kandidat.get("pfad") or "").strip()
    wurzel: str = (kandidat.get("wurzel") or "").strip()

    if not pfad:
        logger.error(
            "Auskunft: Kandidat ohne Pfad — die Fundstelle fehlt und die "
            "Herkunft der Auskunft ist damit nicht mehr ablesbar"
        )
        return "(Fundstelle unbekannt)"

    # ── Ausgabe ─────────────────────────────────
    if not wurzel:
        logger.warning(
            "Auskunft: Kandidat '%s' ohne Wurzel — nur der relative Pfad", pfad,
        )
        return mit_etikett(pfad, pfad)
    return mit_etikett(f"{wurzel.rstrip('/')}/{pfad.lstrip('/')}", pfad)


def _kopfzeile(kandidat: dict, anzahl: int) -> str:
    """Die erste Zeile einer Auskunft: Ort, Thema, Kanal.

    Vorbedingung: `kandidat` stammt aus `suche.py`; `anzahl` ist die Zahl der
    gefundenen Kandidaten.
    Nachbedingung: Eine Zeile, die den Ort nennt und den Kanal, über den er
    gefunden wurde.
    """
    kanal: str = kandidat.get("kanal", "")
    kanal_text: str = _KANAL_TEXT.get(kanal, "auf unbekanntem Weg")
    if kanal not in _KANAL_TEXT:
        logger.error(
            "Auskunft: Kandidat mit unbekanntem Kanal %r — die Verlässlichkeit "
            "des Treffers ist damit nicht mehr angebbar", kanal,
        )

    kosinus = kandidat.get("kosinus")
    naehe: str = f", Nähe {kosinus}" if kosinus is not None else ""
    thema: str = (kandidat.get("thema") or "").strip()
    thema_text: str = f" — Thema: {thema}" if thema else ""

    return (
        f"AUS DEN FREIGEGEBENEN UNTERLAGEN, {anzahl} Kandidat(en), "
        f"gefunden {kanal_text}{naehe}:\n"
        f"Fundstelle: {fundstelle(kandidat)}{thema_text}"
    )


def _weitere(kandidaten: list[dict]) -> str:
    """Nennt die übrigen Kandidaten als Angebot, ohne sie zu lesen.

    Vorbedingung: `kandidaten` ist die volle Trefferliste; der erste ist der
    behandelte.
    Nachbedingung: Eine Zeile oder eine leere Zeichenkette bei nur einem Treffer.
    """
    if len(kandidaten) < 2:
        return ""
    namen: str = ", ".join(fundstelle(k) for k in kandidaten[1:])
    return f"\nWeitere Kandidaten, nicht gelesen: {namen}"


def auskunft_finden(kandidaten: list[dict], karte: list[dict]) -> str:
    """Die Auskunft der Stufe „wo steht etwas" — Fundstellen ohne Dateizugriff.

    Vorbedingung: `kandidaten` ist nicht leer; `karte` ist die Blockkarte des
    ersten Kandidaten und darf leer sein.
    Nachbedingung: Nichtleerer Text mit einer Zeile je Kandidat.
    Fehlerfaelle: keine — eine leere Kandidatenliste ist ein Fall für den
    vierten Ausgang und erreicht diese Funktion nicht.

    **Diese Auskunft kostet keinen Dateizugriff** (§6.4). Sie sagt, wo etwas
    liegt, und ausdrücklich nicht, was dort steht — der Unterschied ist die
    ganze Arbeitsteilung aus §3.0.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        logger.error(
            "Auskunft: `auskunft_finden` ohne Kandidaten aufgerufen — der leere "
            "Fall gehört in den vierten Ausgang und nicht in eine Auskunft"
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = [
        f"AUS DEN FREIGEGEBENEN UNTERLAGEN, {len(kandidaten)} Fundstelle(n) "
        f"— gelesen wurde keine Datei, nur der Index:"
    ]
    for kandidat in kandidaten:
        kanal_text: str = _KANAL_TEXT.get(kandidat.get("kanal", ""), "auf unbekanntem Weg")
        thema: str = (kandidat.get("thema") or "").strip()
        zeilen.append(
            f"- {fundstelle(kandidat)} ({kanal_text})"
            + (f" — {thema}" if thema else "")
        )

    if karte:
        ueberschriften: list[str] = [
            str(block.get("header", "")).strip()
            for block in karte[:KARTE_IM_TEXT]
            if str(block.get("header", "")).strip()
        ]
        if ueberschriften:
            zeilen.append(
                f"Abschnitte der ersten Datei: {' · '.join(ueberschriften)}"
            )

    # ── Ausgabe-Verifikation ────────────────────
    text: str = "\n".join(zeilen)
    if not text.strip():
        logger.error("Auskunft: Fundstellentext ist leer, obwohl Kandidaten vorlagen")
        return ""
    return text


def auskunft_nadel(kandidaten: list[dict], ergebnis: dict, gesucht: str) -> str:
    """Die Auskunft der Stufe „wo steht dieser Satz" — Wortlaut mit Zeilennummer.

    Vorbedingung: `kandidaten` ist nicht leer; `ergebnis` stammt aus
    `zoom.nadel_suchen` und trägt `treffer`, `anzahl` und `gekappt`.
    Nachbedingung: Nichtleerer Text; jede Trefferzeile trägt ihre Zeilennummer.
    Fehlerfaelle: keine Treffer ergibt eine ausdrückliche Zeile — „0 Treffer"
    ist eine Auskunft und kein leerer Text.

    **Die Kappung wird genannt, nicht verschluckt.** Eine stillschweigend
    gekürzte Liste ist von einer vollständigen nicht zu unterscheiden, und der
    Mensch schließt aus ihr auf den Bestand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        logger.error("Auskunft: `auskunft_nadel` ohne Kandidaten aufgerufen")
        return ""

    treffer: list = ergebnis.get("treffer") or []
    anzahl: int = int(ergebnis.get("anzahl") or 0)

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = [_kopfzeile(kandidaten[0], len(kandidaten))]
    zeilen.append(f"Gesucht wurde der Wortlaut: {gesucht!r} — {anzahl} Treffer.")

    for eintrag in treffer[:TREFFER_IM_TEXT]:
        nummer, text = _treffer_zerlegen(eintrag)
        if nummer is None:
            continue
        zeilen.append(f"Zeile {nummer}: {text}")

    if anzahl > TREFFER_IM_TEXT:
        zeilen.append(
            f"({anzahl - TREFFER_IM_TEXT} weitere Treffer nicht gezeigt.)"
        )
    if ergebnis.get("gekappt"):
        zeilen.append(
            "(Die Werkzeugschicht hat die Trefferliste gekappt — es können mehr sein.)"
        )

    zeilen.append(_weitere(kandidaten).lstrip("\n"))

    # ── Ausgabe-Verifikation ────────────────────
    text_gesamt: str = "\n".join(z for z in zeilen if z)
    if "Zeile " not in text_gesamt and anzahl > 0:
        logger.error(
            "Auskunft: %d Nadeltreffer gemeldet, aber keine Zeile im Text — die "
            "Trefferform passt nicht zu dieser Auskunft", anzahl,
        )
    return text_gesamt


def _treffer_zerlegen(eintrag: object) -> tuple[int | None, str]:
    """Zerlegt einen Nadeltreffer in Zeilennummer und Wortlaut.

    Vorbedingung: `eintrag` stammt aus `datei_grep` — ein Paar aus Nummer und
    Zeile, als Liste, Tupel oder Wörterbuch.
    Nachbedingung: Nummer und Text, oder `(None, "")` mit Meldung. **Ein
    unlesbarer Treffer wird verworfen und nicht ohne Nummer gezeigt**: Eine
    Zeile ohne Fundstelle ist genau die Aussage, die dieses Modul verhindert.
    """
    # ── Eingabe-Validierung ─────────────────────
    if isinstance(eintrag, dict):
        roh_nummer = eintrag.get("zeile", eintrag.get("nummer"))
        roh_text = eintrag.get("inhalt", eintrag.get("text", ""))
    elif isinstance(eintrag, (list, tuple)) and len(eintrag) >= 2:
        roh_nummer, roh_text = eintrag[0], eintrag[1]
    else:
        logger.error(
            "Auskunft: Nadeltreffer ist %s und trägt kein Paar aus Nummer und "
            "Zeile — verworfen", type(eintrag).__name__,
        )
        return None, ""

    # ── Verarbeitung ────────────────────────────
    try:
        nummer: int = int(roh_nummer)
    except (TypeError, ValueError):
        logger.exception(
            "Auskunft: Zeilennummer %r ist keine Zahl — der Treffer wird "
            "verworfen, weil er ohne Fundstelle nichts belegt", roh_nummer,
        )
        return None, ""

    # ── Ausgabe ─────────────────────────────────
    return nummer, str(roh_text).strip()


def auskunft_block(kandidaten: list[dict], ergebnis: dict, header: str) -> str:
    """Die Auskunft der Stufe „was steht in diesem Abschnitt" — der Wortlaut.

    Vorbedingung: `kandidaten` ist nicht leer; `ergebnis` stammt aus
    `zoom.block_holen` und trägt `inhalt`.
    Nachbedingung: Nichtleerer Text mit Fundstelle, Überschrift und Inhalt.
    Fehlerfaelle: ein leerer Inhalt wird gemeldet — er darf diese Funktion
    nicht erreichen, weil `zoom.block_holen` ihn bereits als kein Ergebnis
    behandelt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        logger.error("Auskunft: `auskunft_block` ohne Kandidaten aufgerufen")
        return ""

    inhalt: str = (ergebnis.get("inhalt") or "").strip()
    if not inhalt:
        logger.error(
            "Auskunft: Block '%s' ohne Inhalt — eine Auskunft ohne Wortlaut ist "
            "genau die Karte-statt-Gebiet-Lage aus §8.1a", header,
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = [
        _kopfzeile(kandidaten[0], len(kandidaten)),
        f"Abschnitt: {header}",
        "Wortlaut:",
        inhalt,
    ]
    if ergebnis.get("rest"):
        zeilen.append(
            f"(Der Abschnitt ist gefenstert; es folgen noch {ergebnis['rest']} Zeilen.)"
        )
    zeilen.append(_weitere(kandidaten).lstrip("\n"))

    # ── Ausgabe-Verifikation ────────────────────
    return "\n".join(z for z in zeilen if z)


def auskunft_karte(kandidaten: list[dict], karte: list[dict]) -> str:
    """Die Auskunft der Stufe „welche Abschnitte hat die Datei" — das Angebot.

    Vorbedingung: `kandidaten` ist nicht leer.
    Nachbedingung: Nichtleerer Text. Trägt die Zeile keine Karte, sagt der Text
    genau das — eine fehlende Karte ist eine Auskunft über den Index und kein
    Fehler des Zooms.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        logger.error("Auskunft: `auskunft_karte` ohne Kandidaten aufgerufen")
        return ""

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = [_kopfzeile(kandidaten[0], len(kandidaten))]

    ueberschriften: list[str] = [
        str(block.get("header", "")).strip()
        for block in karte[:KARTE_IM_TEXT]
        if str(block.get("header", "")).strip()
    ]
    if ueberschriften:
        zeilen.append("Abschnitte dieser Datei:")
        zeilen.extend(f"- {u}" for u in ueberschriften)
        if len(karte) > KARTE_IM_TEXT:
            zeilen.append(f"({len(karte) - KARTE_IM_TEXT} weitere Abschnitte.)")
        zeilen.append(
            "Der Inhalt wurde NICHT gelesen — nenne einen Abschnitt oder einen "
            "Begriff, dann wird nachgesehen."
        )
    else:
        zusammenfassung: str = (kandidaten[0].get("zusammenfassung") or "").strip()
        zeilen.append(
            "Diese Datei trägt keine Abschnittskarte im Index. Bekannt ist nur, "
            "worum es geht, nicht was im Text steht"
            + (f": {zusammenfassung}" if zusammenfassung else ".")
        )

    zeilen.append(_weitere(kandidaten).lstrip("\n"))

    # ── Ausgabe-Verifikation ────────────────────
    return "\n".join(z for z in zeilen if z)


def auskunft_bauen(
    stufe: str, kandidaten: list[dict], ergebnis: object, karte: list[dict],
    gesucht: str,
) -> str:
    """Wählt die Auskunft zur gelaufenen Stufe.

    Vorbedingung: `stufe` liegt in den Stufen des Zooms; `kandidaten` ist nicht
    leer.
    Nachbedingung: Nichtleerer Text, oder eine leere Zeichenkette bei einer
    unbekannten Stufe — dann hat der Aufrufer einen Defekt und keine Auskunft.
    Fehlerfaelle: unbekannte Stufe wird gemeldet.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kandidaten:
        logger.error("Auskunft: `auskunft_bauen` ohne Kandidaten aufgerufen")
        return ""

    # ── Verarbeitung ────────────────────────────
    if stufe == STUFE_NADEL and isinstance(ergebnis, dict):
        return auskunft_nadel(kandidaten, ergebnis, gesucht)
    if stufe == STUFE_BLOCK and isinstance(ergebnis, dict):
        return auskunft_block(kandidaten, ergebnis, gesucht)
    if stufe == STUFE_KARTE:
        return auskunft_karte(kandidaten, karte)

    # ── Ausgabe-Verifikation ────────────────────
    logger.error(
        "Auskunft: unbekannte Stufe %r mit Ergebnis %s — kein Text gebaut",
        stufe, type(ergebnis).__name__,
    )
    return ""
