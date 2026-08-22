"""CRUD ueber die Verzeichnis-Freigaben — die fuenf Aktionen aus §2a.2.

Spezifikation: docs/novaberg-agent-dateien_k.md §2a.

Der Dienst schreibt in die Wurzeltabelle und **nie** in eine Datei. Er legt
kein Verzeichnis an und loescht keines; was er aendert, sind Zeilen ueber
Verzeichnisse. Deshalb importiert dieses Modul aus `aussenrand` nur die
Pruefung — es gibt hier keinen Schreibpfad ins Dateisystem, und das ist die
Zusicherung aus §7 Regel 2.
"""

import logging
from dataclasses import dataclass

from tools.db_manager import db_manager

from agents.base import AgentState, Korrektur
from agents.crud_validation import ValidationResult
from agents.dateien_wurzeln.aussenrand import (
    WurzelBefund,
    dateizahl_text,
    rand_text,
    wurzel_pruefen,
)

logger = logging.getLogger("ki_server.agents.dateien_wurzeln.crud")

#: Geschlossene Menge der Aktionen dieses Dienstes. Kanon nach EVA — eine
#: Teilmengen-Pruefung koennte einen unbekannten Wert nicht von einem
#: gueltigen Nein unterscheiden (`11_EVA` §2).
AKTIONEN_KANON: frozenset[str] = frozenset(
    {"create", "read", "update", "delete", "reactivate"}
)


@dataclass(frozen=True)
class Paar:
    """Mensch und Figur — die Zuordnung, an der eine Freigabe haengt.

    Die beiden reisen immer zusammen (§2.2): Eine Freigabe gehoert einem
    Menschen **und** einer Figur, und die halbe Angabe machte aus zwei
    Freigaben eine. Als Paar uebergeben statt als zwei Zeichenketten, damit
    keine Aufrufstelle nur die eine Haelfte weiterreicht.
    """

    user_id: str
    character_id: str

    @classmethod
    def aus_state(cls, state: AgentState) -> "Paar":
        """Liest das Paar aus dem Kontext eines Auftrags."""
        return cls(
            user_id=state["kontext"].get("user_id", ""),
            character_id=state["kontext"].get("character_id", ""),
        )


# ============================================================
# Lese-Funktionen (auch von klassifikation.py genutzt)
# ============================================================

def _read_aktive(paar: Paar) -> list[dict]:
    """Liest die aktiven Freigaben des Paares.

    Vorbedingung: beide Haelften des Paares sind gesetzt; die Pruefung
    erfolgt beim Aufrufer (Dispatch).
    Nachbedingung: Liste, moeglicherweise leer.
    """
    return db_manager.select(
        "SELECT id, pfad, bezeichnung, erstellt_am FROM dateien_wurzeln "
        "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE "
        "ORDER BY erstellt_am",
        (paar.user_id, paar.character_id),
    )


def _read_inaktive(paar: Paar) -> list[dict]:
    """Liest die stillgelegten Freigaben des Paares (fuer reactivate)."""
    return db_manager.select(
        "SELECT id, pfad, bezeichnung, erstellt_am, geaendert_am FROM dateien_wurzeln "
        "WHERE user_id = %s AND character_id = %s AND aktiv = FALSE "
        "ORDER BY geaendert_am DESC LIMIT 10",
        (paar.user_id, paar.character_id),
    )


def _read_by_id(wurzel_id: int) -> dict | None:
    """Liest eine einzelne Freigabe per ID."""
    return db_manager.select_one(
        "SELECT id, user_id, character_id, pfad, bezeichnung, aktiv, "
        "erstellt_am, geaendert_am FROM dateien_wurzeln WHERE id = %s",
        (wurzel_id,),
    )


def _read_by_pfad(paar: Paar, pfad: str) -> dict | None:
    """Findet eine Freigabe des Paares ueber den aufgeloesten Pfad.

    Der Pfad ist der Schluessel und nicht die Bezeichnung: Zwei Menschen
    duerfen dasselbe Verzeichnis verschieden nennen, aber dasselbe Paar hat
    darauf genau eine Freigabe (Eindeutigkeitsindex im Schema).
    """
    return db_manager.select_one(
        "SELECT id, pfad, bezeichnung, aktiv FROM dateien_wurzeln "
        "WHERE user_id = %s AND character_id = %s AND pfad = %s",
        (paar.user_id, paar.character_id, pfad),
    )


def _suche_by_stichwort(paar: Paar, stichwort: str, aktiv: bool) -> list[dict]:
    """Sucht Freigaben ueber Pfad oder Bezeichnung.

    Ein Mensch spricht seine Freigabe ueber die Bezeichnung an ("meine
    Projektdoku") und nicht ueber den Pfad — deshalb suchen beide Spalten.
    """
    return db_manager.select(
        "SELECT id, pfad, bezeichnung FROM dateien_wurzeln "
        "WHERE user_id = %s AND character_id = %s AND aktiv = %s "
        "AND (pfad ILIKE %s OR COALESCE(bezeichnung, '') ILIKE %s) "
        "ORDER BY erstellt_am DESC LIMIT 5",
        (paar.user_id, paar.character_id, aktiv, f"%{stichwort}%", f"%{stichwort}%"),
    )


# ============================================================
# Validierung gegen DB-Zustand und Aussenrand — das Tor
# ============================================================


#: Was die Validierung zurueckgibt: das Ergebnis und, wenn es eine
#: **Ablehnung** ist, deren drei Teile.
#:
#: **Ein Fehler ist eine Stoerung und geht den Betreiber an, eine Ablehnung
#: ist ein Urteil und geht den Auftraggeber an** (`agents/base.py`). Ein Pfad
#: ausserhalb des Randes ist kein Betriebsproblem — er ist eine Bitte, die
#: dieser Dienst nicht erfuellen darf, und der Mensch soll erfahren, was
#: stattdessen ginge.
#:
#: `[gemessen]` — 18.08.2026 im Betrieb: Die Randablehnung kam als
#: `status='fehler'` zurueck. Das ist Verstossform 8.5 der Anmeldekonvention
#: und macht das Urteil zur Stoerung.
Befund = tuple[ValidationResult, Korrektur | None]


def _ablehnung(befund: str, beleg: str, vorschlag: str) -> Befund:
    """Baut eine Ablehnung mit ihren drei Teilen.

    Vorbedingung: alle drei Teile sind nichtleer.
    Nachbedingung: Ein `ValidationResult` mit `ok=False` und eine
    `Korrektur`. Ohne Befund weiss der Auftraggeber nicht, was nicht
    stimmt; ohne Beleg nicht, woran der Dienst es erkannt hat; ohne
    Vorschlag hat er eine Sackgasse.
    """
    return (
        ValidationResult(ok=False, grund=befund),
        Korrektur(befund=befund, beleg=beleg, vorschlag=vorschlag),
    )


def _stoerung(grund: str) -> Befund:
    """Baut eine Stoerung — sie geht den Betreiber an, nicht den Menschen."""
    return (ValidationResult(ok=False, grund=grund), None)


def _durchlass(grund: str, frage: str = "", korrektur_aktion: str = "") -> Befund:
    """Baut ein Ergebnis, das weitergeht — mit oder ohne Torfrage."""
    return (
        ValidationResult(
            ok=True,
            grund=grund,
            korrektur=korrektur_aktion or None,
            bestaetigung_noetig=bool(frage),
            bestaetigung_text=frage or None,
        ),
        None,
    )


def validieren_gegen_db(state: AgentState) -> Befund:
    """Prueft die klassifizierte Aktion gegen Aussenrand und Bestand.

    Vorbedingung: `state["parameter"]["action"]` liegt in AKTIONEN_KANON;
    `kontext` traegt `user_id` und `character_id`.
    Nachbedingung: Ein `Befund` — Ergebnis und, bei einer Ablehnung, deren
    drei Teile. Bei jeder Schreiboperation ist
    `bestaetigung_noetig` gesetzt — der Mensch bestaetigt, bevor geschrieben
    wird (§2a.2), und beim Anlegen bestaetigt er den **aufgeloesten** Pfad
    samt Dateizahl und nicht seine Eingabe (§7 Regel 3b).

    Der Aussenrand wird hier geprueft und nicht erst beim Ausfuehren: Ein
    Pfad ausserhalb darf gar nicht erst ans Tor kommen, sonst stuende dort
    eine Bestaetigungsfrage zu etwas, das auch mit Ja nicht geschieht.
    """
    # ── Eingabe-Validierung ─────────────────────
    action: str = state["parameter"].get("action", "")
    if action not in AKTIONEN_KANON:
        logger.error(
            "dateien_wurzeln: Aktion '%s' nicht im Kanon %s — Validierung "
            "abgebrochen", action, sorted(AKTIONEN_KANON),
        )
        return _stoerung(f"Unbekannte Aktion: {action}")

    paar: Paar = Paar.aus_state(state)
    genannter_pfad: str = state["parameter"].get("pfad", "") or ""
    bezeichnung: str = state["parameter"].get("bezeichnung", "") or ""
    stichwort: str = state["parameter"].get("stichwort", "") or ""
    target_id: int | None = state["parameter"].get("target_id")

    # ── Verarbeitung ────────────────────────────
    if action == "read":
        return _durchlass("Leseoperation")

    if action == "create":
        return _validieren_create(paar, genannter_pfad, bezeichnung)

    if action == "update":
        return _validieren_update(paar, target_id, stichwort, bezeichnung)

    if action == "delete":
        return _validieren_zustandswechsel(paar, target_id, stichwort, aktiv_erwartet=True)

    return _validieren_zustandswechsel(paar, target_id, stichwort, aktiv_erwartet=False)


def _validieren_create(
    paar: Paar, genannter_pfad: str, bezeichnung: str,
) -> Befund:
    """Prueft eine neue Freigabe gegen Rand und Bestand.

    Nachbedingung: Bei `ok=True` steht der aufgeloeste Pfad im Grund und
    `bestaetigung_noetig` ist gesetzt. Eine Ablehnung wegen des Randes ist
    endgueltig — sie traegt `bestaetigung_noetig=False`, weil eine
    Bestaetigung daran nichts aendert (§7 Regel 3a).
    """
    befund: WurzelBefund = wurzel_pruefen(genannter_pfad)
    if not befund.ok:
        # Kein zulaessiger Bereich konfiguriert ist ein Betriebszustand und
        # geht den Betreiber an; alles andere ist ein Urteil ueber die Bitte.
        if befund.aufgeloest is None and "Bereich konfiguriert" in befund.grund:
            return _stoerung(befund.grund)
        return _ablehnung(
            befund=befund.grund,
            beleg=(
                f"'{genannter_pfad}' loest auf zu {befund.aufgeloest}; "
                f"zulaessig ist {befund.rand}"
            ),
            vorschlag=(
                f"Nenn mir ein Verzeichnis unterhalb von {rand_text()} — "
                f"oder frag mich, worauf ich schon Zugriff habe."
            ),
        )

    aufgeloest: str = str(befund.aufgeloest)
    vorhanden: dict | None = _read_by_pfad(paar, aufgeloest)

    if vorhanden and vorhanden["aktiv"]:
        logger.info(
            "dateien_wurzeln: '%s' ist bereits freigegeben (ID %d) — keine "
            "zweite Zeile", aufgeloest, vorhanden["id"],
        )
        return _ablehnung(
            befund=f"{aufgeloest} ist bereits freigegeben.",
            beleg=f"Freigabe ID {vorhanden['id']} steht seit ihrer Anlage auf aktiv.",
            vorschlag="Frag mich mit 'worauf hast du Zugriff', was schon offen ist.",
        )

    if vorhanden and not vorhanden["aktiv"]:
        return _durchlass(
            grund=(
                f"Stillgelegte Freigabe auf {aufgeloest} gefunden "
                f"(ID {vorhanden['id']}) — auto-korrigiert zu reactivate"
            ),
            frage=(
                f"Auf {aufgeloest} gab es schon einmal eine Freigabe, sie ist "
                f"stillgelegt. Soll ich sie wieder aufnehmen? "
                f"({dateizahl_text(befund)})"
            ),
            korrektur_aktion="reactivate",
        )

    name: str = f" als '{bezeichnung}'" if bezeichnung else ""
    return _durchlass(
        grund=f"Freigabe auf {aufgeloest}, {dateizahl_text(befund)}",
        frage=(
            f"Ich habe {dateizahl_text(befund)} unter {aufgeloest} gefunden — "
            f"dieses Verzeichnis{name} freigeben?"
        ),
    )


def _validieren_update(
    paar: Paar, target_id: int | None, stichwort: str, bezeichnung: str,
) -> Befund:
    """Prueft die Umbenennung einer Freigabe."""
    if not bezeichnung:
        return _ablehnung(
            befund="Fuer die Umbenennung fehlt die neue Bezeichnung.",
            beleg="Die Aeusserung nennt kein neues Wort fuer das Verzeichnis.",
            vorschlag="Sag mir, wie ich es nennen soll, etwa 'nenn das meine Projektdoku'.",
        )

    treffer, befund = _ziel_aufloesen(
        paar, target_id, stichwort, aktiv_erwartet=True, vorgang="umbenennen",
    )
    if befund is not None:
        return befund

    return _durchlass(
        grund=f"Umbenennung von ID {treffer['id']} auf '{bezeichnung}'",
        frage=f"Soll ich {treffer['pfad']} ab jetzt '{bezeichnung}' nennen?",
    )


def _validieren_zustandswechsel(
    paar: Paar, target_id: int | None, stichwort: str, aktiv_erwartet: bool,
) -> Befund:
    """Prueft Ruecknahme (aktiv_erwartet=True) oder Wiederaufnahme (False)."""
    vorgang: str = "zurueckziehen" if aktiv_erwartet else "wieder aufnehmen"
    treffer, befund = _ziel_aufloesen(
        paar, target_id, stichwort, aktiv_erwartet, vorgang,
    )
    if befund is not None:
        return befund

    if aktiv_erwartet:
        # Die zweite Form des Entzugs — das Vergessen der indizierten
        # Inhalte (§2a.3) — hat heute keinen Gegenstand: Die Indextabelle
        # existiert nicht. Der Text sagt das, statt eine Wahl vorzugaukeln,
        # die keine ist.
        text: str = (
            f"Soll ich die Freigabe auf {treffer['pfad']} zuruecknehmen? "
            f"Ich sehe dann nicht mehr hinein."
        )
    else:
        text = f"Soll ich {treffer['pfad']} wieder freigeben?"

    return _durchlass(grund=f"Freigabe ID {treffer['id']} {vorgang}", frage=text)


def _ziel_aufloesen(
    paar: Paar, target_id: int | None, stichwort: str,
    aktiv_erwartet: bool, vorgang: str,
) -> tuple[dict | None, Befund | None]:
    """Loest die gemeinte Freigabe auf — ueber ID oder Stichwort.

    Nachbedingung: Entweder (Treffer, None) oder (None, Ergebnis mit Grund).
    Genau eine der beiden Haelften ist gesetzt; der Aufrufer prueft die
    zweite und gibt sie durch.

    Mehrdeutigkeit endet in einer Rueckfrage mit den Kandidaten und nicht in
    einer Auswahl — welche Freigabe gemeint ist, weiss der Mensch.
    """
    if target_id:
        eintrag: dict | None = _read_by_id(target_id)
        if not eintrag:
            return None, _ablehnung(
                befund=f"Freigabe mit der Nummer {target_id} gibt es nicht.",
                beleg="Unter dieser Nummer steht keine Zeile.",
                vorschlag="Frag mich mit 'worauf hast du Zugriff' nach den Nummern.",
            )
        if eintrag["user_id"] != paar.user_id or eintrag["character_id"] != paar.character_id:
            logger.error(
                "dateien_wurzeln: Freigabe ID %s gehoert zu (%s x %s), "
                "angefragt von (%s x %s) — abgewiesen",
                target_id, eintrag["user_id"], eintrag["character_id"],
                paar.user_id, paar.character_id,
            )
            return None, _ablehnung(
                befund=f"Freigabe mit der Nummer {target_id} gibt es nicht.",
                beleg="Die Nummer gehoert zu einem anderen Paar.",
                vorschlag="Frag mich mit 'worauf hast du Zugriff' nach deinen Freigaben.",
            )
        if eintrag["aktiv"] != aktiv_erwartet:
            zustand: str = "bereits aktiv" if eintrag["aktiv"] else "bereits stillgelegt"
            return None, _ablehnung(
                befund=f"{eintrag['pfad']} ist {zustand}.",
                beleg=f"Zeile ID {eintrag['id']} traegt aktiv={eintrag['aktiv']}.",
                vorschlag="Frag mich mit 'worauf hast du Zugriff' nach dem Stand.",
            )
        return eintrag, None

    if not stichwort:
        return None, _ablehnung(
            befund=f"Es ist nicht erkennbar, welche Freigabe ich {vorgang} soll.",
            beleg="Die Aeusserung nennt weder eine Nummer noch eine Bezeichnung.",
            vorschlag="Nenn mir den Pfad oder den Namen, unter dem du sie kennst.",
        )

    treffer: list[dict] = _suche_by_stichwort(paar, stichwort, aktiv_erwartet)
    if not treffer:
        return None, _ablehnung(
            befund=f"Zu '{stichwort}' finde ich keine Freigabe, die ich {vorgang} koennte.",
            beleg=f"Weder Pfad noch Bezeichnung einer Zeile enthaelt '{stichwort}'.",
            vorschlag="Frag mich mit 'worauf hast du Zugriff', was ich habe.",
        )
    if len(treffer) > 1:
        zeilen: str = "\n".join(
            f"  [{t['id']}] {t['pfad']}" + (f" ({t['bezeichnung']})" if t["bezeichnung"] else "")
            for t in treffer
        )
        return None, (
            ValidationResult(
                ok=False,
                grund=f"Mehrere Freigaben passen zu '{stichwort}'",
                bestaetigung_noetig=True,
                bestaetigung_text=f"Mehrere passen:\n{zeilen}\n\nWelche meinst du?",
            ),
            None,
        )

    return treffer[0], None


# ============================================================
# Verifikation — der DB-Read nach dem Write
# ============================================================

def _verifizieren(action: str, wurzel_id: int | None, aktiv_erwartet: bool) -> bool:
    """Prueft, ob die Operation den erwarteten Effekt hatte.

    Vorbedingung: `action` liegt in AKTIONEN_KANON.
    Nachbedingung: True nur, wenn die Zeile existiert und ihr `aktiv` dem
    erwarteten Zustand entspricht. Ein gelungener Aufruf ist nicht dasselbe
    wie eine geschriebene Zeile.
    """
    if wurzel_id is None:
        logger.error("dateien_wurzeln: Verifikation ohne ID nach '%s'", action)
        return False

    eintrag: dict | None = _read_by_id(wurzel_id)
    if not eintrag:
        logger.error(
            "dateien_wurzeln: Verifikation — Zeile ID %d nach '%s' nicht "
            "gefunden", wurzel_id, action,
        )
        return False

    if eintrag["aktiv"] != aktiv_erwartet:
        logger.error(
            "dateien_wurzeln: Verifikation — Zeile ID %d traegt aktiv=%s, "
            "erwartet %s nach '%s'",
            wurzel_id, eintrag["aktiv"], aktiv_erwartet, action,
        )
        return False

    return True


# ============================================================
# Die fuenf Aktionen
# ============================================================

def ausfuehren(state: AgentState) -> dict:
    """Fuehrt die freigegebene Aktion aus.

    Vorbedingung: Das Tor ist durchlaufen — bei jeder Schreiboperation hat
    der Mensch bestaetigt.
    Nachbedingung: Ein State-Update mit `status`, `ergebnis` und einem
    Schritt im Audit-Pfad. Jeder Rueckkehrpfad setzt beide.
    """
    action: str = state["parameter"].get("action", "")
    logger.debug("dateien_wurzeln.ausfuehren: Einstieg — action='%s'", action)

    verteiler = {
        "create": _create,
        "read": _read,
        "update": _update,
        "delete": _delete,
        "reactivate": _reactivate,
    }
    handler = verteiler.get(action)
    if handler is None:
        logger.error("dateien_wurzeln: unbehandelte Aktion '%s'", action)
        return {
            "status": "fehler",
            "fehler": f"Unbehandelte Aktion: {action}",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "unbehandelt"}
            ],
        }

    return handler(state)


def _rand_urteil(state: AgentState, befund: WurzelBefund, genannt: str) -> dict:
    """Formt eine Randablehnung waehrend der Ausfuehrung als vierten Ausgang.

    Vorbedingung: `befund.ok` ist False.
    Nachbedingung: Ein State-Update mit `status="abgelehnt"` und den drei
    Teilen der Korrektur — ausser der Rand ist gar nicht konfiguriert; das
    ist ein Betriebszustand und geht den Betreiber an.
    """
    if befund.aufgeloest is None and "Bereich konfiguriert" in befund.grund:
        return {
            "status": "fehler",
            "fehler": befund.grund,
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "kein_rand"}
            ],
        }

    return {
        "status": "abgelehnt",
        "fehler": befund.grund,
        "parameter": {
            **state["parameter"],
            "korrektur": Korrektur(
                befund=befund.grund,
                beleg=f"'{genannt}' loest auf zu {befund.aufgeloest}; zulaessig ist {befund.rand}",
                vorschlag=(
                    f"Nenn mir ein Verzeichnis unterhalb von {rand_text()} — "
                    f"oder frag mich, worauf ich schon Zugriff habe."
                ),
            ),
        },
        "schritte": state["schritte"] + [
            {"node": "ausfuehren", "ergebnis": "rand_abgewiesen"}
        ],
    }


def _create(state: AgentState) -> dict:
    """Legt eine Freigabe an — nach erneuter Randpruefung.

    Der Rand wird hier ein zweites Mal geprueft, und das ist keine
    Verdopplung: Zwischen Tor und Bestaetigung liegt eine Antwort des
    Menschen und damit beliebig viel Zeit. Was geschrieben wird, ist der
    Pfad, den DIESE Pruefung aufgeloest hat — nicht der, den das Tor gezeigt
    hat.
    """
    paar: Paar = Paar.aus_state(state)
    genannter_pfad: str = state["parameter"].get("pfad", "") or ""
    bezeichnung: str | None = state["parameter"].get("bezeichnung") or None

    # ── Eingabe-Validierung ─────────────────────
    befund: WurzelBefund = wurzel_pruefen(genannter_pfad)
    if not befund.ok:
        logger.error("dateien_wurzeln: create abgewiesen — %s", befund.grund)
        return _rand_urteil(state, befund, genannter_pfad)

    # ── Verarbeitung ────────────────────────────
    aufgeloest: str = str(befund.aufgeloest)
    # `eigentum` bleibt auf dem Vorgabewert 'nutzer' und wird hier bewusst
    # nicht gesetzt: Was ein Mensch im Gespraech freigibt, ist sein Material.
    # Die Wurzel der Figur — ihr eigener Wissensspeicher — entsteht nicht
    # ueber diesen Weg, sondern beim Aufbau des Schemas.
    ergebnis_zeile: dict | None = db_manager.execute_returning(
        "INSERT INTO dateien_wurzeln (user_id, character_id, pfad, bezeichnung) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (paar.user_id, paar.character_id, aufgeloest, bezeichnung),
    )
    wurzel_id = ergebnis_zeile["id"] if ergebnis_zeile else None

    # ── Ausgabe-Verifikation ────────────────────
    verifiziert: bool = _verifizieren("create", wurzel_id, aktiv_erwartet=True)
    logger.info(
        "dateien_wurzeln: Freigabe angelegt (ID %s) auf '%s' fuer (%s x %s), "
        "%s, verifiziert=%s",
        wurzel_id, aufgeloest, paar.user_id, paar.character_id,
        dateizahl_text(befund), verifiziert,
    )

    name: str = f" ('{bezeichnung}')" if bezeichnung else ""
    return {
        "ergebnis": (
            f"Verzeichnis freigegeben: {aufgeloest}{name} — {dateizahl_text(befund)}."
        ),
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren", "ergebnis": "freigegeben",
            "id": wurzel_id, "verifiziert": verifiziert,
        }],
    }


def _read(state: AgentState) -> dict:
    """Listet die aktiven Freigaben des Paares auf."""
    aktive: list[dict] = _read_aktive(Paar.aus_state(state))

    if not aktive:
        return {
            "ergebnis": "Es ist mir kein Verzeichnis freigegeben.",
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "leer", "anzahl": 0}
            ],
        }

    zeilen: list[str] = []
    for eintrag in aktive:
        zeile: str = f"- [{eintrag['id']}] {eintrag['pfad']}"
        if eintrag.get("bezeichnung"):
            zeile += f" ({eintrag['bezeichnung']})"
        zeilen.append(zeile)

    return {
        "ergebnis": "Freigegebene Verzeichnisse:\n" + "\n".join(zeilen),
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [
            {"node": "ausfuehren", "ergebnis": "gelesen", "anzahl": len(aktive)}
        ],
    }


def _update(state: AgentState) -> dict:
    """Aendert die Bezeichnung einer Freigabe — nie ihren Pfad.

    Ein geaenderter Pfad waere eine neue Freigabe und muesste durch das Tor
    und ueber den Rand. Eine Umbenennung, die das umginge, waere der
    billigste Weg an der Schranke vorbei.
    """
    wurzel_id, fehler = _ziel_id(state, aktiv_erwartet=True)
    if fehler is not None:
        return fehler

    bezeichnung: str = state["parameter"].get("bezeichnung", "") or ""
    if not bezeichnung:
        logger.error("dateien_wurzeln: update ohne Bezeichnung (ID %s)", wurzel_id)
        return {
            "status": "fehler",
            "fehler": "Keine neue Bezeichnung angegeben.",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "keine_bezeichnung"}
            ],
        }

    db_manager.execute(
        "UPDATE dateien_wurzeln SET bezeichnung = %s, geaendert_am = NOW() WHERE id = %s",
        (bezeichnung, wurzel_id),
    )

    # ── Ausgabe-Verifikation ────────────────────
    nachher: dict | None = _read_by_id(wurzel_id)
    if not nachher or nachher.get("bezeichnung") != bezeichnung:
        logger.error(
            "dateien_wurzeln: Verifikation — Zeile ID %s traegt Bezeichnung "
            "%r, geschrieben wurde %r",
            wurzel_id, nachher.get("bezeichnung") if nachher else None, bezeichnung,
        )
        return {
            "status": "fehler",
            "fehler": "Die Umbenennung ist nicht angekommen.",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "nicht_verifiziert", "id": wurzel_id}
            ],
        }

    logger.info(
        "dateien_wurzeln: Freigabe ID %s heisst jetzt '%s'", wurzel_id, bezeichnung,
    )
    return {
        "ergebnis": f"{nachher['pfad']} heisst ab jetzt '{bezeichnung}'.",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [
            {"node": "ausfuehren", "ergebnis": "umbenannt", "id": wurzel_id, "verifiziert": True}
        ],
    }


def _delete(state: AgentState) -> dict:
    """Nimmt eine Freigabe zurueck — Soft-Delete wie bei den Direktiven."""
    return _zustand_setzen(state, aktiv_neu=False)


def _reactivate(state: AgentState) -> dict:
    """Nimmt eine stillgelegte Freigabe wieder auf.

    Der Rand wird dabei erneut geprueft: Zwischen Stilllegung und
    Wiederaufnahme kann der Rand enger geworden sein, und eine alte Zeile
    ist kein Recht.
    """
    wurzel_id, fehler = _ziel_id(state, aktiv_erwartet=False)
    if fehler is not None:
        return fehler

    eintrag: dict | None = _read_by_id(wurzel_id)
    if eintrag is None:
        logger.error("dateien_wurzeln: reactivate — Zeile ID %s verschwunden", wurzel_id)
        return {
            "status": "fehler",
            "fehler": f"Freigabe mit der Nummer {wurzel_id} gibt es nicht.",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "nicht_gefunden"}
            ],
        }

    befund: WurzelBefund = wurzel_pruefen(eintrag["pfad"])
    if not befund.ok:
        logger.error(
            "dateien_wurzeln: reactivate abgewiesen — die gespeicherte Wurzel "
            "'%s' haelt dem heutigen Rand nicht stand: %s",
            eintrag["pfad"], befund.grund,
        )
        return _rand_urteil(state, befund, eintrag["pfad"])

    return _zustand_setzen(state, aktiv_neu=True, vorab_id=wurzel_id)


def _zustand_setzen(state: AgentState, aktiv_neu: bool, vorab_id: int | None = None) -> dict:
    """Setzt `aktiv` einer Freigabe und verifiziert das Ergebnis."""
    if vorab_id is not None:
        wurzel_id: int | None = vorab_id
    else:
        wurzel_id, fehler = _ziel_id(state, aktiv_erwartet=not aktiv_neu)
        if fehler is not None:
            return fehler

    db_manager.execute(
        "UPDATE dateien_wurzeln SET aktiv = %s, geaendert_am = NOW() WHERE id = %s",
        (aktiv_neu, wurzel_id),
    )

    # ── Ausgabe-Verifikation ────────────────────
    vorgang: str = "reactivate" if aktiv_neu else "delete"
    verifiziert: bool = _verifizieren(vorgang, wurzel_id, aktiv_erwartet=aktiv_neu)
    if not verifiziert:
        return {
            "status": "fehler",
            "fehler": "Die Aenderung an der Freigabe ist nicht angekommen.",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "nicht_verifiziert", "id": wurzel_id}
            ],
        }

    nachher: dict | None = _read_by_id(wurzel_id)
    pfad: str = nachher["pfad"] if nachher else "?"
    logger.info(
        "dateien_wurzeln: Freigabe ID %s auf '%s' %s",
        wurzel_id, pfad, "wieder aufgenommen" if aktiv_neu else "zurueckgenommen",
    )

    ergebnis: str = (
        f"{pfad} ist wieder freigegeben."
        if aktiv_neu
        else f"Die Freigabe auf {pfad} ist zurueckgenommen — ich sehe dort nicht mehr hinein."
    )
    return {
        "ergebnis": ergebnis,
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "wieder_aufgenommen" if aktiv_neu else "zurueckgenommen",
            "id": wurzel_id, "verifiziert": True,
        }],
    }


def _ziel_id(state: AgentState, aktiv_erwartet: bool) -> tuple[int | None, dict | None]:
    """Ermittelt die ID der gemeinten Freigabe fuer die Ausfuehrung.

    Nachbedingung: Entweder (ID, None) oder (None, State-Update mit Fehler).
    Die Aufloesung wiederholt die des Tores, weil der Auftrag ueber Redis
    und eine Nutzerantwort hierher gekommen sein kann — der Bestand darf
    sich in der Zwischenzeit geaendert haben.
    """
    target_id: int | None = state["parameter"].get("target_id")
    stichwort: str = state["parameter"].get("stichwort", "") or ""

    treffer, befund = _ziel_aufloesen(
        Paar.aus_state(state), target_id, stichwort, aktiv_erwartet,
        vorgang="behandeln",
    )
    if befund is not None:
        ergebnis, korrektur = befund
        logger.error("dateien_wurzeln: Ziel nicht aufloesbar — %s", ergebnis.grund)
        # Ein unauffindbares Ziel ist ein Urteil ueber die Bitte, keine
        # Stoerung des Betriebs — es geht ueber den vierten Ausgang hinaus.
        return None, {
            "status": "abgelehnt" if korrektur else "fehler",
            "fehler": ergebnis.grund,
            "parameter": {**state["parameter"], "korrektur": korrektur},
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "ziel_unklar"}
            ],
        }

    return treffer["id"], None
