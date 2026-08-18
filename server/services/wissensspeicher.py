"""Ablage eines Arbeitsergebnisses in der Wissens-Bibliothek.

Ein abgeschlossener Durchlauf hinterlässt zwei Dateien und eine Metadatenzeile:

| | |
|---|---|
| **Wissen-Datei** | das *Was* — reines Destillat, für Retrieval gebaut |
| **Bericht-Datei** | das *Wie* — Ziel, Suchverlauf, Urteil des Gates |
| **Metadatenzeile** | wo die Datei liegt, worum es geht, wie schwer sie wiegt |

Die Trennung ist nicht Ordnungsliebe: Der Enricher liest Wissen, die
Lagebeurteilung liest Berichte, und ein Bericht im Wissen verwässerte jeden
Vektor mit Prozess-Rauschen.

**Nur die Wissen-Datei hängt am Gate.** Bei `wiederholung` und `fehlschlag`
entsteht kein Wissen, aber sehr wohl ein Bericht — auch ein Fehlschlag ist
ein Ergebnis, und die nächste Lagebeurteilung soll ihn kennen (§5.1).

Spezifikation: docs/novaberg-autonomous-wissen_k.md §2, §3, §4, §5, §6.3, §11.
"""

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from config import POSTGRES_URL, WISSENSSPEICHER_WURZEL
from memory.repositories.autonomous_wissen_repository import (
    AutonomousWissenRepository,
    WissensEintrag,
)
from tools.dateien.schreiben import datei_lesen, datei_schreiben

logger = logging.getLogger("ki_server.services.wissensspeicher")

# Die Status, bei denen eine Wissen-Datei entsteht (§5.1). Die beiden
# übrigen — wiederholung, fehlschlag — bekommen nur einen Bericht.
STATUS_MIT_WISSEN: frozenset[str] = frozenset({"echte_tiefe", "ergaenzung"})

# Novas Bereich der Bibliothek. Der zweite, `user/`, gehört dem DateienAgenten;
# kein Cross-Write (§2.1).
BEREICH: str = "autonomous"

INDEX_DATEI: str = "INDEX.md"

# Obergrenze des Slugs im Dateinamen. Ein Thema kann ein ganzer Satz sein;
# der Dateiname soll trotzdem lesbar bleiben und auf jedem Dateisystem passen.
SLUG_MAX: int = 60


@dataclass
class Arbeitsergebnis:
    """Was ein abgeschlossener Durchlauf der Bibliothek anbietet.

    Reiner Datencontainer. Die Felder des Paar-Schemas tragen keine
    Vorgabewerte — wer ohne Gegenüber ablegt, soll am Aufruf scheitern und
    nicht an einer stillen Annahme (§11.2).

    `queries` und `begruendung` sind für die Bericht-Datei; sie sind das
    Einzige, was die Lagebeurteilung des nächsten Durchlaufs über das *Wie*
    des letzten erfährt.
    """

    thema:            str
    destillat:        str
    status:           str
    modus:            str
    user_id:          str
    character_id:     str
    beobachter:       str
    salienz:          float
    ziel:             str = ""
    begruendung:      str = ""
    themen_embedding: str | None = None
    queries:          list[str] = field(default_factory=list)


def embed_text_bauen(zusammenfassung: str) -> str:
    """Baut den Embed-Text der Spalte `themen_embedding` — die EINZIGE Formel dafür.

    Live-Pfad und spätere Re-Embedding-Werkzeuge rufen dieselbe Funktion; der
    Text ist aus der persistierten Spalte `zusammenfassung` vollständig
    rekonstruierbar. Dieselbe Bauart wie bei `lzg_knoten.embed_text_bauen`.

    Vorbedingung: `zusammenfassung` ist nicht leer.
    Nachbedingung: die unveränderte Zusammenfassung — die Formel ist die
    Identität, und das ist eine Entscheidung, keine Auslassung: Das Konzept
    beschreibt den Vektor als „Embedding der Zusammenfassung" (§7.2).
    Fehlerfälle: leerer Text (ValueError) statt eines Leerstring-Embeddings.
    """
    if not zusammenfassung or not zusammenfassung.strip():
        meldung: str = "embed_text_bauen(autonomous_wissen): zusammenfassung ist leer"
        raise ValueError(meldung)
    return zusammenfassung


def slug_bauen(thema: str) -> str:
    """Formt ein Thema in einen dateinamentauglichen Slug.

    Vorbedingung: `thema` ist nicht leer. Nachbedingung: Das Ergebnis
    besteht aus Kleinbuchstaben, Ziffern und Bindestrichen, ist nicht leer
    und höchstens SLUG_MAX Zeichen lang.
    Fehlerfälle: leeres Thema oder ein Thema, das nach der Normalisierung
    nichts übrig lässt (ValueError) — ein Dateiname aus dem Nichts wäre bei
    jedem zweiten Thema derselbe.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not thema or not thema.strip():
        meldung: str = "slug_bauen: leeres Thema"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    # NFKD zerlegt Umlaute in Grundbuchstabe + Zeichen; das Verwerfen der
    # Nicht-ASCII-Anteile macht daraus a, o, u. Das ist bewusst eine
    # Transliteration und keine Sprachumsetzung — aus "Größe" wird "grosse"
    # nicht, sondern "groe" ... deshalb die ausdrückliche Ersetzung vorher.
    ersetzt: str = (
        thema.lower()
        .replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    )
    zerlegt: str = unicodedata.normalize("NFKD", ersetzt)
    ascii_text: str = zerlegt.encode("ascii", "ignore").decode("ascii")
    slug: str = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")[:SLUG_MAX].strip("-")

    # ── Ausgabe-Verifikation ────────────────────
    if not slug:
        meldung = f"slug_bauen: Thema {thema!r} ergibt nach der Normalisierung keinen Slug"
        raise ValueError(meldung)

    return slug


def dateipfad_bauen(*, charakter: str, context_user: str, thema: str, typ: str, datum: str) -> Path:
    """Baut den Pfad einer Bibliotheksdatei nach dem Namensschema aus §2.2.

    `{wurzel}/autonomous/{charakter}/{datum}_{context_user}_{slug}_{typ}.md`

    Der Charakter ist das Verzeichnis, nicht der Dateiname: Novas Wissen ist
    Novas Wissen. Flach innerhalb des Ordners, nach Datum sortierbar.

    Vorbedingung: Alle Teile sind nicht leer, `typ` steht im Kanon.
    Nachbedingung: Ein absoluter Pfad unterhalb der Wurzel. Ob er beschrieben
    werden darf, entscheidet der Waechter in tools/dateien/schreiben.py.
    Fehlerfälle: leerer Teil oder unbekannter Typ (ValueError).
    """
    # ── Eingabe-Validierung ─────────────────────
    for name, wert in (("charakter", charakter), ("context_user", context_user), ("datum", datum)):
        if not wert or not wert.strip():
            meldung: str = f"dateipfad_bauen: {name} ist leer"
            raise ValueError(meldung)

    if typ not in {"wissen", "bericht"}:
        meldung = f"dateipfad_bauen: typ={typ!r} ist weder 'wissen' noch 'bericht'"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    slug: str = slug_bauen(thema)
    name: str = f"{datum}_{context_user}_{slug}_{typ}.md"

    return Path(WISSENSSPEICHER_WURZEL) / BEREICH / charakter / name


# Der Block, der den lebenden Text trägt. Er bildet mit `## HISTORIE` aus
# `tools/dateien/versionierung.py` ein **Paar**: Jeder sagt, was der andere
# ist. Der Gewinn liegt beim Lesen — der lebende Text hat damit eine
# Adresse, und die Historie wird nie geladen, solange niemand fragt.
WISSEN_STANDARDBLOCK: str = "## AKTUELL"

# Die Anfangsversion jeder neuen Wissensdatei. Ohne sie weiß beim ersten
# Eingriff niemand, gegen welchen Stand er schreibt.
WISSEN_ANFANGSVERSION: str = "1.0"


def wissen_text_bauen(ergebnis: Arbeitsergebnis, datum_lang: str) -> str:
    """Baut den Inhalt der Wissen-Datei — reines Destillat, kein Prozess-Rauschen.

    Vorbedingung: `ergebnis.destillat` ist nicht leer.
    Nachbedingung: Ein Markdown-Text mit Kopfblock, Versionsangabe und
    **mindestens einem adressierbaren Block** unterhalb der Titelzeile.
    Fehlerfälle: leeres Destillat (ValueError) — eine Wissen-Datei ohne
    Wissen ist der Fall, den das Gate abfangen soll; kommt sie hier an, ist
    das ein Defekt im Aufrufer und keine leere Datei.

    **Warum der Block erzwungen wird.** Gemessen am 17.08.2026 trugen
    **223 von 223** Wissensdateien keine einzige `##`-Überschrift, während
    461 von 462 übrigen Dateien welche hatten. Damit hat jedes blockweise
    arbeitende Werkzeug — gezieltes Lesen, chirurgisches Ersetzen, die
    Versionierung — auf genau dem Bestand nichts zu adressieren, für den es
    gebaut ist. Der Zuschnitt ist keine Verschönerung, sondern die
    Vorbedingung dafür, dass eine Datei später *bearbeitet* statt neu
    erzeugt werden kann.

    **Vorhandene Gliederung bleibt erhalten, rückt aber eine Ebene tiefer.**
    Bringt das Destillat eigene `##`-Blöcke mit, werden sie zu `###` und
    liegen damit *innerhalb* von `## AKTUELL`. Ohne diese Absenkung endete
    der lebende Block bei der ersten eigenen Überschrift, und `## AKTUELL`
    trüge nur den Text davor — die Adresse wäre dann eine halbe. Die Absenkung
    ist strukturell und rührt den Wortlaut nicht an.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not ergebnis.destillat.strip():
        meldung: str = f"wissen_text_bauen: leeres Destillat zu {ergebnis.thema!r}"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    # Eigene Gliederung eine Ebene absenken, damit sie unter AKTUELL liegt.
    abgesenkt: list[str] = [
        f"#{zeile.lstrip()}" if zeile.lstrip().startswith("## ") else zeile
        for zeile in ergebnis.destillat.strip().splitlines()
    ]
    rumpf: str = f"{WISSEN_STANDARDBLOCK}\n\n" + "\n".join(abgesenkt)

    text: str = (
        f"# {ergebnis.thema}\n\n"
        f"**Erstellt:** {datum_lang}\n"
        f"**Recherchiert fuer:** {ergebnis.user_id}\n"
        f"**Modus:** {ergebnis.modus}\n"
        f"**Version:** {WISSEN_ANFANGSVERSION}\n\n"
        f"---\n\n"
        f"{rumpf}\n"
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Eine Datei ohne adressierbaren Block ist genau der Zustand, gegen den
    # dieser Zuschnitt gebaut ist — sie darf nicht entstehen. Geprüft wird
    # auf **genau einen** Block der zweiten Ebene: Ein zweiter stünde neben
    # AKTUELL statt darin, und die Absenkung hätte nicht gegriffen.
    zweitrangig: list[str] = [
        z for z in text.splitlines() if z.lstrip().startswith("## ")
    ]
    if len(zweitrangig) != 1 or zweitrangig[0].strip() != WISSEN_STANDARDBLOCK:
        meldung = (
            f"wissen_text_bauen: {ergebnis.thema!r} ergäbe eine Datei mit "
            f"{len(zweitrangig)} Blöcken der zweiten Ebene ({zweitrangig}) — "
            f"erwartet war genau {WISSEN_STANDARDBLOCK}"
        )
        raise RuntimeError(meldung)
    return text


def bericht_text_bauen(ergebnis: Arbeitsergebnis, datum_lang: str) -> str:
    """Baut den Inhalt der Bericht-Datei — das Wie, samt Urteil des Gates.

    Der Bericht trägt nur, was der Durchlauf tatsächlich erhoben hat. Was
    das Konzept in §4 darüber hinaus vorsieht — Dauer, Trefferzahlen,
    verworfene Quellen —, erhebt der RechercheAgent heute nicht; erfundene
    Felder wären hier schlimmer als fehlende, weil die Lagebeurteilung sie
    als Messwerte läse.

    Vorbedingung: keine — ein Bericht entsteht auch zu einem Fehlschlag.
    Nachbedingung: Ein Markdown-Text mit Kopfblock, Ziel, Suchverlauf und
    Klassifikation.
    """
    # ── Verarbeitung ────────────────────────────
    queries_block: str = (
        "\n".join(f"- {q}" for q in ergebnis.queries) if ergebnis.queries
        else "_Keine Suchanfragen protokolliert._"
    )
    ziel_zeile: str = ergebnis.ziel.strip() or "_Kein Ziel protokolliert._"
    begruendung: str = ergebnis.begruendung.strip() or "_Keine Begruendung geliefert._"

    return (
        f"# Bericht: {ergebnis.thema}\n\n"
        f"**Typ:** {ergebnis.modus}\n"
        f"**Datum:** {datum_lang}\n"
        f"**Recherchiert fuer:** {ergebnis.user_id}\n"
        f"**Ausloesende Salienz:** {ergebnis.salienz:.2f}\n\n"
        f"---\n\n"
        f"## Ziel\n\n"
        f"{ziel_zeile}\n\n"
        f"## Suchverlauf\n\n"
        f"{queries_block}\n\n"
        f"## Ergebnis-Klassifikation\n\n"
        f"**{ergebnis.status}** — {begruendung}\n"
    )


def index_aktualisieren(*, charakter: str, thema: str, wissen_pfad: Path, datum_lang: str) -> None:
    """Trägt eine Wissensdatei in die INDEX.md ihres Charakters ein.

    Ein Index, kein Abladeplatz: eine Zeile je Datei, mit Verweis auf die
    Detaildatei (§2.3). Ein bereits vorhandener Verweis auf dieselbe Datei
    wird nicht verdoppelt — die Datei ist ein lebendes Dokument, ihr Eintrag
    im Index ist es auch.

    Vorbedingung: `wissen_pfad` liegt im Verzeichnis dieses Charakters.
    Nachbedingung: Die INDEX.md existiert und enthält genau einen Verweis
    auf `wissen_pfad`.
    Fehlerfälle: Schreib- oder Waechterfehler werden durchgereicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    index_pfad: Path = Path(WISSENSSPEICHER_WURZEL) / BEREICH / charakter / INDEX_DATEI

    # ── Verarbeitung ────────────────────────────
    vorhanden: str = datei_lesen(index_pfad)
    zeile: str = f"- [{thema}]({wissen_pfad.name})"

    if wissen_pfad.name in vorhanden:
        logger.debug(f"index_aktualisieren: {wissen_pfad.name} steht bereits im Index")
        return

    if not vorhanden:
        vorhanden = f"# {charakter} — Wissensindex\n\n"

    # Der Kopf trägt das Datum der letzten Änderung; die alte Zeile wird
    # entfernt und neu geschrieben, damit sie nicht hinter dem Inhalt
    # zurückbleibt — ein Index mit veraltetem Datum sieht gepflegt aus.
    ohne_datum: str = re.sub(
        r"^\*\*Letzte Aktualisierung:\*\*.*\n", "", vorhanden, flags=re.MULTILINE,
    )
    ueberschrift, _, rest = ohne_datum.partition("\n\n")
    eintraege: str = rest.strip()
    neu: str = (
        f"{ueberschrift.strip()}\n\n"
        f"**Letzte Aktualisierung:** {datum_lang}\n\n"
        f"{eintraege}\n{zeile}\n" if eintraege else
        f"{ueberschrift.strip()}\n\n**Letzte Aktualisierung:** {datum_lang}\n\n{zeile}\n"
    )

    datei_schreiben(index_pfad, neu)

    # ── Ausgabe-Verifikation ────────────────────
    if wissen_pfad.name not in datei_lesen(index_pfad):
        logger.error(
            f"index_aktualisieren: {wissen_pfad.name} steht nach dem Schreiben nicht "
            f"in {index_pfad} — der Index ist unvollstaendig"
        )


def ergebnis_ablegen(ergebnis: Arbeitsergebnis) -> dict[str, str]:
    """Legt ein Arbeitsergebnis in der Bibliothek ab und gibt die Pfade zurück.

    Der vollständige Weg nach dem Gate (§6.3, Punkte 1 und 2): Wissen-Datei
    bei `echte_tiefe`/`ergaenzung`, Bericht-Datei immer, INDEX.md nachziehen,
    Metadatenzeile schreiben. Der Stack-Push und die Rückkopplung in die
    Pipeline (Punkte 3 und 4) bleiben beim Aufrufer.

    Vorbedingung: `ergebnis` trägt Paar-Schema, Status aus dem Kanon und
    eine Salienz größer als null. Nachbedingung: Die genannten Dateien
    existieren, und genau eine Metadatenzeile trägt den Pfad der
    maßgeblichen Datei.
    Fehlerfälle: alle an den Aufrufer — ein Schreibfehler in der Bibliothek
    darf nicht als Erfolg durchgehen, und die Recherche selbst ist zu diesem
    Zeitpunkt bereits gültig abgeschlossen.

    **Bei fehlender Wissen-Datei zeigt die Metadatenzeile auf den Bericht.**
    Sonst gäbe es einen Eintrag ohne Datei, und `dateipfad` ist die
    Identität der Zeile.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not ergebnis.thema.strip():
        meldung: str = "ergebnis_ablegen: leeres Thema"
        raise ValueError(meldung)

    jetzt: datetime = datetime.now(timezone.utc)
    datum: str = jetzt.strftime("%Y-%m-%d")
    datum_lang: str = jetzt.strftime("%d.%m.%Y")
    charakter: str = ergebnis.character_id

    # ── Verarbeitung ────────────────────────────
    bericht_pfad: Path = dateipfad_bauen(
        charakter=charakter, context_user=ergebnis.user_id,
        thema=ergebnis.thema, typ="bericht", datum=datum,
    )
    datei_schreiben(bericht_pfad, bericht_text_bauen(ergebnis, datum_lang))

    wissen_pfad: Path | None = None
    if ergebnis.status in STATUS_MIT_WISSEN:
        wissen_pfad = dateipfad_bauen(
            charakter=charakter, context_user=ergebnis.user_id,
            thema=ergebnis.thema, typ="wissen", datum=datum,
        )
        datei_schreiben(wissen_pfad, wissen_text_bauen(ergebnis, datum_lang))
        index_aktualisieren(
            charakter=charakter, thema=ergebnis.thema,
            wissen_pfad=wissen_pfad, datum_lang=datum_lang,
        )

    massgeblich: Path = wissen_pfad or bericht_pfad
    zeilen_id: int = AutonomousWissenRepository.speichern(
        POSTGRES_URL,
        WissensEintrag(
            dateipfad=str(massgeblich),
            user_id=ergebnis.user_id,
            character_id=ergebnis.character_id,
            beobachter=ergebnis.beobachter,
            thema=ergebnis.thema,
            zusammenfassung=ergebnis.destillat.strip()[:500],
            typ="wissen" if wissen_pfad else "bericht",
            modus=ergebnis.modus,
            status=ergebnis.status,
            salienz_anfang=ergebnis.salienz,
            themen_embedding=ergebnis.themen_embedding,
        ),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not bericht_pfad.is_file():
        meldung = f"ergebnis_ablegen: Bericht {bericht_pfad} fehlt nach dem Schreiben"
        raise RuntimeError(meldung)

    if wissen_pfad and not wissen_pfad.is_file():
        meldung = f"ergebnis_ablegen: Wissen-Datei {wissen_pfad} fehlt nach dem Schreiben"
        raise RuntimeError(meldung)

    logger.info(
        f"Bibliothek: '{ergebnis.thema}' abgelegt — Status {ergebnis.status}, "
        f"Zeile {zeilen_id}, Bericht {bericht_pfad.name}"
        + (f", Wissen {wissen_pfad.name}" if wissen_pfad else ", kein Wissen (Gate)")
    )

    return {
        "bericht_pfad": str(bericht_pfad),
        "wissen_pfad":  str(wissen_pfad) if wissen_pfad else "",
        "zeilen_id":    str(zeilen_id),
    }
