"""Die Einarbeitung — der Fund kommt an seine Stelle, nicht ans Ende.

Spezifikation: docs/novaberg-agent-dateien_k.md §4b.3 · §4b.2.

> **Einarbeiten ist das Gegenteil von Destillieren.** Der Recherche-Pfad
> komprimiert; dieser Weg reichert an: Fakten ergänzen, an der richtigen
> Stelle, ohne Dopplung, und ohne dass ein vernünftiger Text zerfällt.

**Ohne die Schreibschicht wäre jeder Eingriff ein „ganze Datei neu erzeugen"** —
teuer und verlustbehaftet ohne Alarm. Mit einem chirurgischen Schnitt ist der
Verlust auf den angefassten Absatz begrenzt und über das Archiv umkehrbar.

**Zwei Ausgänge sind Erfolg, und nur einer davon schreibt.** Steht der Fund
schon im Text, ist *nichts tun* die richtige Antwort — eine Wiederholung ist
kein Zuwachs, sondern die Fastdublette, an der nach §4a.2 der Abruf verrottet.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from config import PROMPTS, get_node_config
from services.model_services import ChatRequest, model_service
from tools.dateien.operationen import metadaten_lesen, pfad_pruefen
from tools.dateien.versionierung import Fassung, absatz_einfuegen, aktuell_lesen

logger = logging.getLogger("ki_server.agents.wissen_rueckweg.einarbeitung")

#: Wie viel Text der Datei dem Aufruf vorgelegt wird. Der Anker muss
#: zeichengenau aus diesem Ausschnitt stammen — was das Modell nicht sieht,
#: kann es nicht als Vorbild nennen.
TEXT_KAPPUNG: int = 12000

#: Die Versionsangabe im Kopf der Wissensdatei.
_VERSION_ZEILE: re.Pattern = re.compile(r"^\*\*Version:\*\*\s*(?P<wert>\S+)\s*$", re.M)

#: Vorgabe, wenn eine Datei keine Versionsangabe trägt. Sie ist erkennbar
#: keine gewachsene Zahl — eine Datei ohne Kopf soll nicht so aussehen, als
#: hätte sie schon Eingriffe hinter sich.
VERSION_OHNE_KOPF: str = "0.1"


def naechste_version(version: str) -> str:
    """Zählt die zweite Stelle der Version um eins hoch.

    Vorbedingung: `version` ist die Angabe aus dem Kopf der Datei.
    Nachbedingung: Eine Version derselben Form mit erhöhter zweiter Stelle.
    Fehlerfaelle: Eine Angabe, die sich nicht zerlegen lässt, wird gemeldet
    und um ein Suffix erweitert statt verworfen — eine Datei ohne brauchbare
    Version soll den Eingriff nicht verhindern, aber auch nicht so aussehen,
    als wäre ihre Zählung in Ordnung.

    **Dass die zweite Stelle steigt, ist aus den Beispielen des Konzepts
    abgeleitet und dort ausdrücklich nicht gesetzt** (`novaberg-tool-dateien_k.md`
    §3.4, letzte offene Frage). Die erste Stelle rührt dieser Weg nicht an: Ein
    eingefügter Absatz ist ein Zuwachs, keine neue Fassung des Gegenstands.
    """
    # ── Eingabe-Validierung ─────────────────────
    teile: list[str] = version.strip().split(".")
    if len(teile) != 2 or not all(t.isdigit() for t in teile):
        logger.error(
            "Rückweg-Einarbeitung: Version %r hat nicht die Form <Zahl>.<Zahl> "
            "— der Eingriff läuft, die Zählung der Datei ist aber gerissen",
            version,
        )
        return f"{version.strip()}+1"

    # ── Ausgabe ─────────────────────────────────
    return f"{teile[0]}.{int(teile[1]) + 1}"


def version_fortschreiben(pfad: Path | str, wurzel: Path | str) -> str:
    """Schreibt die Versionsangabe im Kopf der Datei um eins fort.

    Vorbedingung: `pfad` liegt in der Wurzel.
    Nachbedingung: Die Kopfzeile trägt die neue Version, und diese wird
    zurückgegeben. Trägt die Datei keine Angabe, bleibt sie unverändert und
    `VERSION_OHNE_KOPF` kommt zurück.
    Fehlerfaelle: verletzte Wurzelprüfung (ValueError), Schreibfehler (OSError)
    — beide an den Aufrufer.

    **Dieser Schritt läuft VOR dem Einfügen, und die Reihenfolge ist die
    Aussage.** Schlägt das Einfügen danach fehl, steht eine erhöhte Version
    ohne Änderung da — sichtbar und harmlos. Umgekehrt trüge der Archiveintrag
    eine Version, die die Datei nicht zeigt, und das ist ein Widerspruch, den
    später niemand mehr auflösen kann.

    **Die Kopfzeile geht nicht durch die Versionierung**, und das ist kein
    Umgehen: Sie ist der Zähler selbst. Ihn über den Mechanismus zu schreiben,
    den er zählt, wäre ein Kreis.
    """
    # ── Eingabe-Validierung ─────────────────────
    ziel: Path = pfad_pruefen(pfad, wurzel)
    felder: dict[str, str] = metadaten_lesen(ziel, wurzel)
    alt: str = (felder.get("Version") or "").strip()

    if not alt:
        logger.warning(
            "Rückweg-Einarbeitung: %s trägt keine Versionsangabe — der Eingriff "
            "wird mit %s gestempelt und der Kopf bleibt, wie er ist",
            ziel, VERSION_OHNE_KOPF,
        )
        return VERSION_OHNE_KOPF

    # ── Verarbeitung ────────────────────────────
    neu: str = naechste_version(alt)
    roh: str = ziel.read_text(encoding="utf-8")
    ersetzt, anzahl = _VERSION_ZEILE.subn(f"**Version:** {neu}", roh, count=1)

    # ── Ausgabe-Verifikation ────────────────────
    if anzahl != 1:
        logger.error(
            "Rückweg-Einarbeitung: Versionszeile in %s nicht ersetzt (%d Treffer) "
            "— der Kopf nennt %s, der Eingriff wird mit %s gestempelt",
            ziel, anzahl, alt, neu,
        )
        return neu

    ziel.write_text(ersetzt, encoding="utf-8")
    logger.info("Rückweg-Einarbeitung: %s — Version %s → %s", ziel, alt, neu)
    return neu


#: Ein Satz unter dieser Laenge traegt zu wenig, um ueber Neuheit zu
#: entscheiden — *„Das ist bemerkenswert."* steht in vielen Dateien und sagt
#: nichts darueber, ob der Absatz etwas beitraegt.
SATZ_MINDESTLAENGE: int = 40


#: Ab welcher Trigramm-Uebereinstimmung ein Satz als "steht schon da" gilt.
#:
#: **Die Zahl ist an den echten Faellen abgelesen, nicht gesetzt.** Ueber die
#: 232 Einarbeitungen des 24.08.2026, je Absatz die schwaechste
#: Uebereinstimmung seiner Saetze mit dem Bestand:
#:
#:     1.00  12 Faelle   woertliche Kopie
#:     0.65-0.95   6     Umformulierung ohne neuen Gehalt — bei zweien sagt
#:                       die "neue" Fassung sogar WENIGER als die alte
#:     0.50-0.65   6     gemischt: echte Ergaenzungen neben Umformulierungen
#:     unter 0.50  208   echte Funde
#:
#: **Ein sauberes Tal gibt es nicht** — bei 0,65 kippt das Urteil beim Lesen,
#: und zwei Umformulierungen darunter laufen durch.
#:
#: **Die Schwelle liegt bewusst hoch, und der Grund ist die Asymmetrie der
#: Kosten:** Ein durchgelassener Doppelgaenger ist ein doppelter Absatz —
#: sichtbar, zaehlbar, mit einem Werkzeug zuruecknehmbar. Ein faelschlich
#: abgewiesener Fund ist **fort**: `steht_schon_da` reiht nicht wieder ein,
#: und niemand erfaehrt, was verloren ging. Im Zweifel wird eingearbeitet.
#:
#: Geeicht an `pg_trgm.similarity()` (in dieser Datenbank vorhanden) ueber 60
#: echte Paare: groesste Abweichung 0,083, mittlere 0,025, und **0 Paare mit
#: abweichendem Urteil an dieser Schwelle**. Die Rechnung bleibt trotzdem hier
#: und geht nicht in die Datenbank — ein Datenbankaufruf fuer einen reinen
#: Textvergleich fuegt einen Ausfallpfad hinzu, der still waere.
AEHNLICH_GENUG: float = 0.65


def _trigramme(satz: str) -> set[str]:
    """Die Trigramm-Menge eines Satzes — normalisiert wie `pg_trgm`.

    Nachbedingung: Kleinschreibung, keine Satzzeichen, einfacher Leerraum,
        Raender mit einem Leerzeichen gepolstert. Zwei Saetze, die sich nur
        in Zeichensetzung oder Grossschreibung unterscheiden, liefern
        dieselbe Menge.
    """
    rein: str = re.sub(r"[^a-z0-9äöüß ]", " ", satz.lower())
    rein = " " + " ".join(rein.split()) + " "
    return {rein[i:i + 3] for i in range(len(rein) - 2)}


def _aehnlichkeit(a: str, b: str) -> float:
    """Trigramm-Uebereinstimmung zweier Saetze, 0.0 bis 1.0.

    Vorbedingung: beide Saetze sind nicht leer.
    Nachbedingung: Der Jaccard-Quotient ihrer Trigramm-Mengen — 1.0 bei
        gleichem Wortlaut, 0.0 ohne gemeinsame Zeichenfolge.
    Fehlerfaelle: keine; zwei leere Saetze liefern 0.0 statt zu teilen.
    """
    ta: set[str] = _trigramme(a)
    tb: set[str] = _trigramme(b)
    vereinigung: int = len(ta | tb)
    return len(ta & tb) / vereinigung if vereinigung else 0.0


def _saetze(text: str) -> list[str]:
    """Zerlegt einen Text in vergleichbare Saetze — ohne Marken, ohne Leerraum.

    Nachbedingung: Nur Saetze ab `SATZ_MINDESTLAENGE`; Fundmarken `[iN>]` und
    mehrfacher Leerraum sind entfernt, damit ein Satz mit Marke und derselbe
    ohne als gleich gelten.
    """
    ohne_marken: str = re.sub(r"\[i\d+>\]", " ", text)
    roh: list[str] = re.split(r"(?<=[.!?])\s+", ohne_marken)
    return [
        s for s in (" ".join(x.split()) for x in roh)
        if len(s) >= SATZ_MINDESTLAENGE
    ]


def _bringt_neues(absatz: str, text: str) -> tuple[bool, float]:
    """Traegt `absatz` mindestens einen Satz, der so nicht im Text steht?

    Vorbedingung: beide nicht leer.
    Nachbedingung: `(neu, hoechste_uebereinstimmung)`. `neu` ist True, wenn
        wenigstens ein Satz des Absatzes unter `AEHNLICH_GENUG` gegen jeden
        Satz des Textes bleibt. Die Zahl ist die **schwaechste** der besten
        Uebereinstimmungen — also der Wert, an dem die Entscheidung haengt,
        und sie gehoert ins Log, damit die Schwelle aus dem Betrieb
        nachjustierbar bleibt statt aus der Erinnerung.
        **Ein Absatz ohne vergleichbaren Satz gilt als neu** (Rueckgabe
        `(True, 0.0)`) — er ist zu kurz fuer das Urteil, und ein Riegel, der
        im Zweifel verwirft, verloere echte Funde.
    Fehlerfaelle: keine.

    **Verglichen wird auf Aehnlichkeit, nicht auf Gleichheit.** Die erste
    Fassung dieses Riegels (24.08.2026, vormittags) verlangte den exakten
    Wortlaut und fing damit 12 von 18 Doppelgaengern: Die uebrigen sechs
    waren Umformulierungen desselben Satzes, zwei davon **aermer** als das
    Original — ein umgestelltes Wort genuegte, um durchzukommen.
    """
    eigene: list[str] = _saetze(absatz)
    fremde: list[str] = _saetze(text)
    if not eigene or not fremde:
        return True, 0.0

    # Je eigenem Satz seine beste Entsprechung im Text; entschieden wird an
    # der **schwaechsten** davon: Ein Absatz bringt etwas mit, sobald EIN
    # Satz keine Entsprechung hat.
    beste: list[float] = [
        max(_aehnlichkeit(e, f) for f in fremde) for e in eigene
    ]
    schwaechste: float = min(beste)
    return schwaechste < AEHNLICH_GENUG, schwaechste


def absatz_bestimmen(text: str, kern: str) -> dict | None:
    """Fragt Absatz, Anker und Zusammenfassungs-Ergänzung in einem Aufruf ab.

    Vorbedingung: `text` ist der geltende Text der Zieldatei, `kern` der
    sachliche Gehalt des Fundes.
    Nachbedingung: Ein Wörterbuch mit `absatz`, `nach` (oder None) und
    `ergaenzung` — oder None, wenn die Antwort unbrauchbar war.
    **`nach=None` bei gefülltem Absatz heißt „steht schon da"** und ist ein
    Ergebnis, kein Fehlschlag.
    Fehlerfaelle: unbrauchbares JSON, Antwort ohne Objekt, ein Anker, der
    nicht genau einmal im Text vorkommt — jeder Fall gemeldet, Rückgabe None.

    **Der Anker wird hier geprüft und nicht erst beim Schreiben.** Die
    Werkzeugschicht lehnt einen mehrdeutigen Anker ab; ihn vorher zu prüfen
    trennt *„das Modell hat danebengegriffen"* von *„die Datei hat sich
    geändert"* — zwei Befunde, die im Betrieb gleich aussehen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not text.strip():
        logger.error("Rückweg-Einarbeitung: leerer Zieltext — kein Eingriff")
        return None
    if not kern.strip():
        logger.error("Rückweg-Einarbeitung: leerer Kern — nichts einzuarbeiten")
        return None

    # ── Verarbeitung ────────────────────────────
    ausschnitt: str = text[:TEXT_KAPPUNG]
    if len(text) > TEXT_KAPPUNG:
        logger.info(
            "Rückweg-Einarbeitung: Zieltext auf %d von %d Zeichen gekappt — der "
            "Anker kann nur aus dem gezeigten Teil stammen",
            TEXT_KAPPUNG, len(text),
        )

    system_prompt: str = "\n\n".join([
        PROMPTS["rueckweg_einarbeitung.identity"].format(),
        PROMPTS["rueckweg_einarbeitung.task"].format(),
        PROMPTS["rueckweg_einarbeitung.rules"].format(),
    ])
    node_cfg: dict = get_node_config("router")

    try:
        antwort = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content":
                                  f"TEXT DER DATEI:\n{ausschnitt}\n\nFUND:\n{kern.strip()}"}],
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.05),
            expect_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "agent/wissen_rueckweg/einarbeitung",
        ))
        ergebnis: dict = antwort.parsed
    except (json.JSONDecodeError, KeyError, AttributeError) as fehler:
        logger.exception(
            "%s: Rückweg-Einarbeitung: Modellantwort unbrauchbar",
            type(fehler).__name__,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(ergebnis, dict):
        logger.error(
            "Rückweg-Einarbeitung: Modellantwort ist %s statt dict — verworfen",
            type(ergebnis).__name__,
        )
        return None

    absatz: str = (ergebnis.get("absatz", "") or "").strip()
    nach = ergebnis.get("nach")
    ergaenzung: str = (ergebnis.get("ergaenzung", "") or "").strip()

    if nach is None:
        logger.info(
            "Rückweg-Einarbeitung: der Fund steht laut Aufruf schon im Text — "
            "kein Eingriff, und das ist ein Ergebnis"
        )
        return {"absatz": absatz, "nach": None, "ergaenzung": ergaenzung}

    if not absatz:
        logger.error(
            "Rückweg-Einarbeitung: Anker genannt, aber kein Absatz — verworfen"
        )
        return None

    anker: str = str(nach).strip()
    treffer: int = ausschnitt.count(anker)
    if treffer != 1:
        logger.error(
            "Rückweg-Einarbeitung: Anker kommt %dx im Text vor statt genau "
            "einmal (%r) — verworfen statt an der ersten Stelle eingefügt",
            treffer, anker[:80],
        )
        return None

    # **Der Absatz muss etwas mitbringen, das noch nicht dasteht.**
    #
    # Das Modell hat einen Ausgang fuer diesen Fall — `nach=None`, *steht
    # schon da* — und benutzt ihn nicht zuverlaessig: Es schlaegt stattdessen
    # einen Satz als Fund vor, der woertlich im Text liegt, und nennt als
    # Anker den Satz davor. Der Schnitt setzt die Kopie dann direkt neben das
    # Original, Marke dazwischen.
    #
    # `[gemessen]` — 24.08.2026 ueber 474 Wissensdateien: **17 woertlich
    # doppelte Absaetze und 7 unmittelbar wiederholte Saetze in 22 Dateien**,
    # fuenf davon in einem einzigen Durchgang entstanden. Der Fehler ist
    # still: Die Paarungspruefung haelt (Marke und Eintrag stimmen), die
    # Datei waechst, und nur wer den Absatz liest, sieht ihn doppelt.
    neu, naehe = _bringt_neues(absatz, text)
    if not neu:
        logger.info(
            "Rückweg-Einarbeitung: der vorgeschlagene Absatz steht bereits im "
            "Text (Übereinstimmung %.2f, Schwelle %.2f) — als 'steht schon da' "
            "behandelt statt als Einschub (%r)",
            naehe, AEHNLICH_GENUG, absatz[:80],
        )
        return {"absatz": absatz, "nach": None, "ergaenzung": ergaenzung}

    return {"absatz": absatz, "nach": anker, "ergaenzung": ergaenzung}


def einarbeiten(dateipfad: str, wurzel: Path | str, kern: str) -> dict:
    """Arbeitet den Fund in die Zieldatei ein — der vollständige Weg.

    Vorbedingung: `dateipfad` ist die Datei aus der Bibliothekszeile, `wurzel`
    ihr zulässiger Rand, `kern` der sachliche Gehalt des Fundes.
    Nachbedingung: Ein Bericht mit `geschrieben` (bool), `grund`, und bei
    einem Schnitt zusätzlich `marke`, `version` und `ergaenzung`.
    **Jeder Rückkehrpfad setzt `grund`** — sonst ist „nichts geschrieben, weil
    es schon dastand" von „nichts geschrieben, weil der Aufruf scheiterte"
    nicht zu unterscheiden.
    Fehlerfaelle: verletzte Wurzelprüfung, unlesbare Datei, gerissene Paarung
    nach dem Schnitt — alle gemeldet, `geschrieben=False`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not dateipfad.strip() or not kern.strip():
        logger.error(
            "Rückweg-Einarbeitung: Aufruf ohne Datei (%r) oder ohne Kern",
            dateipfad,
        )
        return {"geschrieben": False, "grund": "aufruf_unvollstaendig"}

    try:
        text: str = aktuell_lesen(dateipfad, wurzel)
    except (ValueError, OSError) as fehler:
        logger.exception(
            "%s: Rückweg-Einarbeitung: %s nicht lesbar",
            type(fehler).__name__, dateipfad,
        )
        return {"geschrieben": False, "grund": f"nicht_lesbar/{type(fehler).__name__}"}

    # ── Verarbeitung ────────────────────────────
    vorschlag: dict | None = absatz_bestimmen(text, kern)
    if vorschlag is None:
        return {"geschrieben": False, "grund": "kein_brauchbarer_vorschlag"}

    if vorschlag["nach"] is None:
        return {
            "geschrieben": False, "grund": "steht_schon_da",
            "ergaenzung": vorschlag.get("ergaenzung", ""),
        }

    version: str = version_fortschreiben(dateipfad, wurzel)
    heute: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        ergebnis: dict = absatz_einfuegen(
            dateipfad, wurzel, vorschlag["absatz"],
            Fassung(version, heute), nach=vorschlag["nach"],
        )
    except (ValueError, OSError, RuntimeError) as fehler:
        logger.exception(
            "%s: Rückweg-Einarbeitung: Schnitt in %s fehlgeschlagen",
            type(fehler).__name__, dateipfad,
        )
        return {"geschrieben": False, "grund": f"schnitt_fehlgeschlagen/{type(fehler).__name__}"}

    # ── Ausgabe-Verifikation ────────────────────
    if not ergebnis.get("erfolg"):
        logger.error(
            "Rückweg-Einarbeitung: %s — Vorbild %s (%sx); die Version steht "
            "bereits auf %s und die Datei ist unverändert",
            dateipfad, ergebnis.get("grund"), ergebnis.get("anzahl"), version,
        )
        return {"geschrieben": False, "grund": f"anker_{ergebnis.get('grund')}"}

    logger.info(
        "Rückweg-Einarbeitung: %s — %s eingefügt, Version %s, %s Zeichen",
        dateipfad, ergebnis.get("marke"), version, ergebnis.get("zeichen"),
    )
    return {
        "geschrieben": True, "grund": "eingefuegt",
        "marke": ergebnis.get("marke"), "version": version,
        "ergaenzung": vorschlag.get("ergaenzung", ""),
    }
