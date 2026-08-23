"""Die Auskunft des Bibliotheks-Dienstes — und ihre Herkunft.

Spezifikation: docs/novaberg-autonomous-wissen_k.md §7.2, §7.3 ·
docs/novaberg-convention-nmcp.md §6.7, §6.8.

**Jede Zeile trägt ihre Fundstelle.** Der Grund ist gemessen und steht in
`novaberg-agent-dateien_k.md` §8.1a: Eine Auskunft ohne Ort ist von einer
Erfindung nicht zu unterscheiden — dort nannte eine Antwort die Fundstelle
richtig und die Zahl daneben, im selben Satz.

**Und sie sagt, welche Tiefe sie hat.** Dieser Dienst liefert Thema und
Zusammenfassung, nicht den Wortlaut der Ausarbeitung (§7.3 Stufe 2 ist nicht
gebaut). Wer das nicht dazuschreibt, lädt zu genau der Prosa ein, die in die
Lücke zwischen Karte und Gebiet gesetzt wird.
"""

import logging

from memory.repositories.autonomous_wissen_repository import Bibliothekszeile
from utils.etikett import mit_etikett

logger = logging.getLogger("ki_server.agents.wissen.auskunft")

#: Was der Dienst über seine eigene Tiefe sagt. Steht als Konstante und nicht
#: als Zeichenkette im Satzbau, weil es eine Zusicherung ist und keine
#: Formulierung: Solange Stufe 2 fehlt, gilt sie für jede Auskunft.
TIEFE_HINWEIS: str = (
    "Das ist der Stand aus meinen Metadaten — Thema und Zusammenfassung, "
    "nicht der Wortlaut der Ausarbeitung."
)


def auskunft_bauen(zeilen: list[Bibliothekszeile]) -> str:
    """Baut die Auskunft aus den Treffern der Bibliothek.

    Vorbedingung: `zeilen` ist nicht leer und kommt aus
    `AutonomousWissenRepository.suchen`.
    Nachbedingung: nichtleerer Text; je Treffer eine Fundstelle und die
    Nähe als Zahl.
    Fehlerfälle: eine leere Liste ist ein Aufruffehler und wird laut
    gemeldet — der vierte Ausgang ist der Ort für „nichts gefunden",
    nicht diese Funktion.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not zeilen:
        logger.error(
            "wissen.auskunft_bauen: ohne Treffer aufgerufen — 'nichts "
            "gefunden' gehoert in den vierten Ausgang, nicht in eine "
            "leere Auskunft"
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    teile: list[str] = [
        f"Dazu habe ich {len(zeilen)} eigene Ausarbeitung"
        f"{'en' if len(zeilen) != 1 else ''}:"
    ]
    for zeile in zeilen:
        teile.append(
            f"- {zeile.thema}\n"
            f"  {zeile.zusammenfassung}\n"
            f"  (Fundstelle {mit_etikett(zeile.dateipfad, zeile.dateipfad)}, "
            f"Naehe {zeile.cosine:.4f}, "
            f"{zeile.haeufigkeit}x bearbeitet)"
        )
    teile.append(TIEFE_HINWEIS)

    # ── Ausgabe-Verifikation ────────────────────
    return "\n".join(teile)


def beleg_bauen(bestand: int, naechste: Bibliothekszeile | None, schwelle: float) -> str:
    """Baut den Beleg der Ablehnung — mit Zahlen, nicht mit Bedauern.

    Vorbedingung: `bestand` ist die gezählte Zahl aktiver Ausarbeitungen des
    Paares; `naechste` ist die dichteste Zeile **unterhalb** der Schwelle
    oder None, wenn es gar keine gibt.
    Nachbedingung: nichtleerer Text, der `bestand` nennt und — wo vorhanden —
    die Nähe des knappsten Verfehlers.

    **Diese Zahl ist zugleich das Messmaterial für die Schwelle.** Sie steht
    heute bei einem übernommenen Wert und ist nicht gemessen (`config.py`,
    `WISSEN_RETRIEVAL_SCHWELLE`). Jede Ablehnung, die den knappsten
    Verfehler mit seiner Nähe nennt, hinterlässt einen Punkt der Verteilung,
    die für die Messung fehlt — im Protokoll und in der Antwort.
    """
    # ── Verarbeitung ────────────────────────────
    if naechste is None:
        return (
            f"{bestand} eigene Ausarbeitungen im Bestand, keine einzige mit "
            f"einem Vektor zum Vergleichen."
            if bestand > 0 else
            "Ich habe zu gar keinem Thema eigene Ausarbeitungen liegen."
        )

    # ── Ausgabe-Verifikation ────────────────────
    return (
        f"{bestand} eigene Ausarbeitungen durchsucht, keine ueber der Schwelle "
        f"{schwelle:.2f}. Am naechsten liegt {naechste.thema!r} mit {naechste.cosine:.4f}."
    )
