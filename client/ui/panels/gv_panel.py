"""
Gesprächsvektor-Panel — zeigt GV4-Debug-Daten nach jedem Turn.

Das Panel ist ``turn_reactive`` und holt seine Daten ueber
``GET /drive/gv_detail``. Der Dispatcher schreibt ``gv_detail`` nach jedem
Turn nach Redis; das Panel laedt beim Oeffnen und nach jedem Turn neu.

Anzeige (kompakt):

    Sprünge:    ██░░  2/3
    Neugier:    ████░ 0.63  (Schwelle: 0.15)
    Strategie:  aktiv

    Wissenslücken (3):
      ● Pflänzchen hegen           KZG  rel=1.577
      ● Person zum Lachen bringen  KZG  rel=0.714
      ● Respektvolles Siezen       KZG  rel=0.545

    Initiative:
      Nutzer führt  +0.104  (Schwelle −0.45)
      gemessen +0.104 · Charakter +0.00 · Wollen +1.0 · Bewegung +0.10
      M1 führend  M2 Thema 0.729  M3 Register 0.100

    Repertoire — Cluster Kissenschlacht:
      ★ Impuls (Im)             kern         35%
      ● Bestätigung (Be)        passt        31%
      ✗ Sachbeitrag (Sa)        unpassend    28%
      Korridor: eingehalten

    Verwandte Erinnerungen (2):
      ● Der Ereignishorizont wurde besprochen (direkt zum Thema; ...)
      ● Die Hawking-Strahlung kam zur Sprache (assoziiert ueber 2 ...)

    Farbton:
      Der Nutzer verfolgt einen Wissenspfad ...

Die beiden Wissens-Sektionen stehen bewusst nebeneinander: Wissensluecken
sagen, was Nova nicht weiss, verwandte Erinnerungen, was sie schon erlebt hat.

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Logs deutsch.
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


_GV_LAENGE_MAX:        int   = 3
_GV_LUECKEN_RELEVANZ:  float = 0.15  # GV_LUECKEN_MIN_RELEVANZ aus dem Server

# Der Server kuerzt den Resonanz-Kontext beim Schreiben ins gv_detail
# (gespraechsvektor.py, Schritt 5). Wer die Zahl hier aendert, aendert nur
# den Hinweis — nicht die Kuerzung.
_GV_RESONANZ_MAX_ZEICHEN: int = 500

# GV_INITIATIVE_SCHWELLE aus dem Server. Ueber diesem Wert heisst das
# Achsen-Bit "Nutzer fuehrt". Sie liegt bewusst NICHT auf null — der Median
# erzwaenge einen 50/50-Schnitt, den die Wirklichkeit nicht hergibt.
_GV_INITIATIVE_SCHWELLE: float = -0.45

# STRATEGIE_NAMEN aus ei/dreischicht.py, von Hand uebertragen. Der Client
# importiert nichts aus dem Server, deshalb steht die Tabelle zweimal — wie
# _GV_LUECKEN_RELEVANZ oben. Ein serverseitiger Test haelt fest, dass jedes
# Kuerzel aus CLUSTER_REPERTOIRE hier eine Entsprechung hat.
_STRATEGIE_NAMEN: dict[str, str] = {
    "Sa": "Sachbeitrag",
    "So": "Selbstoffenbarung",
    "Sp": "Spiegelung",
    "Im": "Impuls",
    "Pw": "Perspektivwechsel",
    "Be": "Bestätigung",
    "Pr": "Präsenz",
}

# Marker wie im [WERKZEUGE]-Block des GV-Prompts (dreischicht_prompt_bauen).
# Der Prompt zeigt 'unpassend' gar nicht — das Panel schon: Wer beurteilen
# will, ob der Korridor stimmt, muss sehen, was ausgeschlossen wurde.
_EIGNUNG_MARKER: dict[str, str] = {
    "kern":      "★",
    "passt":     "●",
    "selten":    "○",
    "unpassend": "✗",
}
_EIGNUNG_RANG: dict[str, int] = {"kern": 0, "passt": 1, "selten": 2, "unpassend": 3}


def _strategie_klartext(kuerzel: str) -> str:
    """Loest ein Strategie-Kuerzel auf. Unbekanntes wird laut, nicht still.

    Ein Kuerzel ohne Entsprechung heisst, dass der Server eine Strategie
    kennt, die diese Tabelle nicht hat — das Panel zeigt dann dauerhaft ein
    unlesbares Kuerzel, ohne dass jemand den Grund sieht.
    """
    if not kuerzel:
        return ""
    name: str | None = _STRATEGIE_NAMEN.get(kuerzel)
    if name is None:
        logger.error(
            f"GvPanel: Strategie-Kuerzel '{kuerzel}' ist in _STRATEGIE_NAMEN "
            f"nicht bekannt — Server und Client passen nicht zusammen"
        )
        return kuerzel
    return name


class GvPanel(PanelBase):
    """Anzeige fuer GV4 (Sprünge, Neugier, Strategie, Wissenslücken, Farbton)."""

    PANEL_ID    = "gv"
    PANEL_LABEL = "🧭 Gesprächsvektor"
    UNIQUE      = True
    CATEGORY    = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 520
    DEFAULT_HEIGHT = 600

    def _build_content(self) -> None:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scroll.set_child(self._outer_box)

        placeholder = Gtk.Label(label="Noch kein Turn empfangen")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._outer_box.append(placeholder)

        self.content_area.append(scroll)

    def load_data(self) -> dict:
        """Holt das aktuelle ``gv_detail`` vom Server (Redis-Snapshot)."""
        url: str = f"{SERVER_URL}/drive/gv_detail"
        logger.debug(f"GvPanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json() or {}

    def _update_ui(self, data: dict) -> None:
        """Baut die Sektionen aus dem aktuellen ``gv_detail`` neu auf."""
        _clear_box(self._outer_box)

        if not data:
            placeholder = Gtk.Label(label="Noch kein Turn empfangen")
            placeholder.set_xalign(0.0)
            placeholder.add_css_class("dim-label")
            self._outer_box.append(placeholder)
            return

        laenge: int = int(data.get("laenge", 0) or 0)

        # Der Serverschluessel heisst seit Chat 111 'aufnahmebereitschaft'.
        # Kein stiller Default: Fehlen BEIDE Schluessel, ist das ein Bruch
        # zwischen Server und Client — nicht ein Wert von null. Der alte Name
        # wird uebergangsweise mitgelesen, damit Blobs von vor der Umbenennung
        # nicht als 0.00 erscheinen.
        roh_bereitschaft = data.get("aufnahmebereitschaft",
                                    data.get("effektive_neugier"))
        if roh_bereitschaft is None:
            logger.error(
                "GvPanel: weder 'aufnahmebereitschaft' noch 'effektive_neugier' "
                "im gv_detail — Server und Client passen nicht zusammen"
            )
        aufnahmebereitschaft: float = float(roh_bereitschaft or 0.0)

        strategie_aktiv:   bool  = bool(data.get("strategie_aktiv", False))
        wissensluecken:    list  = data.get("wissensluecken") or []
        farbton:           str   = str(data.get("farbton") or "")

        # Die zweite Wissensquelle des Nodes. Der Serverschluessel heisst seit
        # Chat 115 'resonanz_kontext'; davor 'entity_hops', als die Quelle noch
        # die fakten-Tabelle war. Beide Namen werden gelesen — der Redis-Key
        # hat kein TTL, ein Blob von vor der Umbenennung bleibt bis zum
        # naechsten Turn stehen.
        #
        # Kein stiller Default: Der Server schreibt das Feld immer, notfalls
        # als leeren String. Fehlen BEIDE Schluessel, ist das ein Bruch
        # zwischen Server und Client — nicht ein Turn ohne Erinnerungen.
        roh_resonanz = data.get("resonanz_kontext", data.get("entity_hops"))
        if roh_resonanz is None:
            logger.error(
                "GvPanel: weder 'resonanz_kontext' noch 'entity_hops' im "
                "gv_detail — Server und Client passen nicht zusammen"
            )
        resonanz_kontext: str = str(roh_resonanz or "")

        # Der Korridor: worin gewählt wurde, nicht nur was gewählt wurde.
        # Alle drei Felder schreibt der Node unbedingt; ein fehlender
        # Schlüssel ist deshalb ein Bruch und kein leerer Turn.
        repertoire:          dict = data.get("repertoire") or {}
        charakter_gewichtung: dict = data.get("charakter_gewichtung") or {}
        korridor_verstoesse: list = data.get("korridor_verstoesse") or []

        # Die Initiative-Messung. Der Node schreibt sie als eigenes Objekt;
        # fehlt es, ist der Server aelter als Chat 116 — das wird laut, nicht
        # als leere Anzeige verschluckt.
        initiative: dict | None = data.get("initiative")
        if initiative is None:
            logger.error(
                "GvPanel: 'initiative' fehlt im gv_detail — Server und Client "
                "passen nicht zusammen (Achse seit Chat 116)"
            )

        if "korridor_verstoesse" not in data:
            logger.error(
                "GvPanel: 'korridor_verstoesse' fehlt im gv_detail — "
                "Server und Client passen nicht zusammen"
            )

        # Dreischicht-Felder (Chat 72/73)
        sektor_index:   int  = int(data.get("sektor_index", 0) or 0)
        sektor_name:    str  = str(data.get("sektor_name") or "")
        cluster:        str  = str(data.get("cluster") or "")
        achsen:         dict = data.get("achsen") or {}
        absicht:        str  = str(data.get("absicht") or "")
        strategie_name: str  = str(data.get("strategie") or "")
        vehikel:        str  = str(data.get("vehikel") or "")
        sprung_1:       str  = str(data.get("sprung_1") or "")
        sprung_2:       str  = str(data.get("sprung_2") or "")
        sprung_3:       str  = str(data.get("sprung_3") or "")
        impuls:         str  = str(data.get("impuls") or "")

        resonanz_zeilen: list[str] = [
            z.strip() for z in resonanz_kontext.splitlines() if z.strip()
        ]

        logger.info(
            f"GvPanel: laenge={laenge}, bereitschaft={aufnahmebereitschaft:.3f}, "
            f"strategie={strategie_aktiv}, luecken={len(wissensluecken)}, "
            f"resonanz={len(resonanz_zeilen)} Erinnerung(en)/"
            f"{len(resonanz_kontext)} Zeichen, "
            f"sektor=#{sektor_index} {sektor_name}, cluster={cluster}, "
            f"absicht={absicht}, strat={strategie_name}, vehikel={vehikel}, "
            f"repertoire={len(repertoire)} Strategien, "
            f"gewichtung={'leer' if not charakter_gewichtung else len(charakter_gewichtung)}, "
            f"verstoesse={[v.get('wert') for v in korridor_verstoesse] or 'keine'}"
        )

        # 1. Bestehend: Kennzahlen (Sprünge-Bar, Neugier-Bar, Strategie aktiv/—)
        self._outer_box.append(_build_kennzahlen(
            laenge=laenge,
            neugier=aufnahmebereitschaft,
            strategie_aktiv=strategie_aktiv,
        ))

        # 2. NEU: Dreischicht (Sektor, Cluster, Achsen, Absicht/Strategie/Vehikel)
        self._outer_box.append(_build_dreischicht_section(
            sektor_index=sektor_index,
            sektor_name=sektor_name,
            cluster=cluster,
            achsen=achsen,
            absicht=absicht,
            strategie=strategie_name,
            vehikel=vehikel,
        ))

        # 2b. NEU (Chat 116): Der Korridor — worin gewählt wurde.
        #     Steht direkt hinter der Dreischicht, weil es deren Strategie-Zeile
        #     erklärt: Ohne das Repertoire ist eine Strategiewahl nicht zu
        #     beurteilen, man sieht nur das Ergebnis.
        self._outer_box.append(_build_repertoire_section(
            repertoire=repertoire,
            gewichtung=charakter_gewichtung,
            cluster=cluster,
            gewaehlt=strategie_name,
            verstoesse=korridor_verstoesse,
        ))

        # 2c. NEU (Chat 116): Initiative — woraus das Achsen-Bit entstand.
        self._outer_box.append(_build_initiative_section(initiative))

        # 3. NEU: Sprünge (3 Gedankenschritte)
        self._outer_box.append(_build_spruenge_section(sprung_1, sprung_2, sprung_3))

        # 4. NEU: Impuls (Richtungsangabe für den Responder)
        self._outer_box.append(_build_impuls_section(impuls))

        # 5. Bestehend: Wissenslücken — was Nova nicht weiss
        self._outer_box.append(_build_luecken_section(wissensluecken))

        # 6. NEU (Chat 116): Verwandte Erinnerungen — was sie schon erlebt hat
        self._outer_box.append(_build_resonanz_section(resonanz_zeilen,
                                                       len(resonanz_kontext)))

        # 7. Bestehend: Farbton
        self._outer_box.append(_build_farbton_section(farbton))

    # ═══════════════════════════════════════════════════════════════
    # Turn-Reactive: nach jedem Turn neu vom Server laden
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Wird nach jedem Turn aufgerufen — Refresh holt frische Daten via REST."""
        self.refresh()


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Layout
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_kennzahlen(laenge: int, neugier: float, strategie_aktiv: bool) -> Gtk.Box:
    """Drei-Zeilen-Block: Sprünge | Neugier | Strategie."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    header = Gtk.Label(label="Gesprächsvektor")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    # Sprünge
    laenge_clamped: int = max(0, min(_GV_LAENGE_MAX, laenge))
    spr_row = _build_metric_row(
        label_text="Sprünge",
        bar_min=0.0,
        bar_max=float(_GV_LAENGE_MAX),
        bar_value=float(laenge_clamped),
        wert_text=f"{laenge_clamped}/{_GV_LAENGE_MAX}",
    )
    section.append(spr_row)

    # Neugier
    neugier_clamped: float = max(0.0, min(1.0, neugier))
    neu_row = _build_metric_row(
        label_text="Neugier",
        bar_min=0.0,
        bar_max=1.0,
        bar_value=neugier_clamped,
        wert_text=f"{neugier:.2f}",
        zusatz_text=f"(Schwelle: {_GV_LUECKEN_RELEVANZ:.2f})",
    )
    section.append(neu_row)

    # Strategie
    strat_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    strat_label = Gtk.Label(label="Strategie")
    strat_label.set_xalign(0.0)
    strat_label.set_width_chars(11)
    strat_label.add_css_class("caption")
    strat_row.append(strat_label)

    status_label = Gtk.Label(label="aktiv" if strategie_aktiv else "—")
    status_label.set_xalign(0.0)
    status_label.set_hexpand(True)
    if strategie_aktiv:
        status_label.add_css_class("success")
    else:
        status_label.add_css_class("dim-label")
    strat_row.append(status_label)

    section.append(strat_row)

    return section


def _build_metric_row(
    label_text: str,
    bar_min:    float,
    bar_max:    float,
    bar_value:  float,
    wert_text:  str,
    zusatz_text: str = "",
) -> Gtk.Box:
    """Eine Zeile: Label | LevelBar | Wert | (optional) Zusatz."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    name = Gtk.Label(label=label_text)
    name.set_xalign(0.0)
    name.set_width_chars(11)
    name.add_css_class("caption")
    row.append(name)

    bar = Gtk.LevelBar()
    bar.set_min_value(bar_min)
    bar.set_max_value(bar_max)
    bar.set_value(bar_value)
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)
    row.append(bar)

    wert = Gtk.Label(label=wert_text)
    wert.set_xalign(1.0)
    wert.set_width_chars(6)
    wert.add_css_class("caption")
    row.append(wert)

    if zusatz_text:
        zusatz = Gtk.Label(label=zusatz_text)
        zusatz.set_xalign(0.0)
        zusatz.add_css_class("dim-label")
        zusatz.add_css_class("caption")
        row.append(zusatz)

    return row


def _build_luecken_section(luecken: list) -> Gtk.Box:
    """Sektion 'Wissenslücken (N)' mit kompakten Eintraegen."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label=f"Wissenslücken ({len(luecken)})")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not luecken:
        leer = Gtk.Label(label="(keine qualifizierten Lücken in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
        return section

    for luecke in luecken:
        section.append(_build_luecken_row(luecke))

    return section


def _build_luecken_row(luecke: dict) -> Gtk.Box:
    """● Konzept (gekuerzt)  QUELLE  rel=1.234"""
    konzept:  str   = str(luecke.get("konzept") or "")
    quelle:   str   = str(luecke.get("quelle") or "?").upper()
    relevanz: float = float(luecke.get("relevanz", 0.0) or 0.0)

    auszug: str = konzept if len(konzept) <= 80 else konzept[:77] + "…"

    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    bullet = Gtk.Label(label="●")
    bullet.add_css_class("accent")
    row.append(bullet)

    konzept_label = Gtk.Label(label=auszug)
    konzept_label.set_xalign(0.0)
    konzept_label.set_hexpand(True)
    konzept_label.set_wrap(True)
    konzept_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    row.append(konzept_label)

    quelle_label = Gtk.Label(label=quelle)
    quelle_label.set_width_chars(4)
    quelle_label.add_css_class("caption")
    quelle_label.add_css_class("dim-label")
    row.append(quelle_label)

    rel_label = Gtk.Label(label=f"rel={relevanz:.3f}")
    rel_label.set_xalign(1.0)
    rel_label.add_css_class("caption")
    row.append(rel_label)

    return row



def _build_initiative_section(initiative: dict | None) -> Gtk.Box:
    """Sektion 'Initiative' — wer im Turn die Richtung gesetzt hat.

    Zeigt nicht nur das Ergebnis, sondern woraus es entstand: die drei Masse
    einzeln, die zwei Dimensionen, den Charakter-Versatz und den Rohwert
    daneben. Ein Bit allein waere nicht beurteilbar — dieselbe Lehre wie beim
    Repertoire, wo das Ergebnis ohne den Korridor nichts sagt.

    Der Charakter-Versatz steht getrennt vom Rohwert, damit ablesbar bleibt,
    was gemessen wurde und was der Charakter daraus gemacht hat.

    Eingabe: das `initiative`-Objekt aus dem gv_detail oder None (Server
    aelter als die Achse).
    """
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Initiative")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not initiative:
        leer = Gtk.Label(label="(keine Initiative-Messung in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
        return section

    wert    = initiative.get("wert")
    rohwert = initiative.get("rohwert")
    versatz = float(initiative.get("versatz") or 0.0)
    fehlend = initiative.get("fehlend") or []

    # ── Ergebniszeile ───────────────────────────
    if wert is None:
        kopf = Gtk.Label(label="nicht messbar — das Achsen-Bit ist ein Ausfall")
        kopf.set_xalign(0.0)
        kopf.set_wrap(True)
        kopf.add_css_class("error")
        section.append(kopf)
    else:
        fuehrt: bool = float(wert) > _GV_INITIATIVE_SCHWELLE
        zeile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        wer = Gtk.Label(label="Nutzer führt" if fuehrt else "Nova hält die Initiative")
        wer.set_xalign(0.0)
        wer.add_css_class("success" if fuehrt else "accent")
        zeile.append(wer)

        zahl = Gtk.Label(label=f"{float(wert):+.3f}")
        zahl.set_xalign(0.0)
        zahl.add_css_class("caption")
        zeile.append(zahl)

        schwelle = Gtk.Label(label=f"(Schwelle {_GV_INITIATIVE_SCHWELLE:+.2f})")
        schwelle.set_xalign(0.0)
        schwelle.set_hexpand(True)
        schwelle.add_css_class("dim-label")
        schwelle.add_css_class("caption")
        zeile.append(schwelle)

        section.append(zeile)

    # ── Herkunft: Rohwert und Charakter getrennt ──
    teile: list[str] = []
    if rohwert is not None:
        teile.append(f"gemessen {float(rohwert):+.3f}")
    teile.append(f"Charakter {versatz:+.2f}"
                 + ("" if versatz else " (nicht abgeleitet)"))
    for name, schluessel in (("Wollen", "wollen"), ("Bewegung", "bewegung")):
        w = initiative.get(schluessel)
        if w is not None:
            teile.append(f"{name} {float(w):+.3f}")

    herkunft = Gtk.Label(label="  ·  ".join(teile))
    herkunft.set_xalign(0.0)
    herkunft.set_wrap(True)
    herkunft.add_css_class("caption")
    section.append(herkunft)

    # ── Die drei Masse einzeln ──────────────────
    masse: list[str] = []
    m1 = initiative.get("m1_roh")
    if m1 is not None:
        masse.append(f"M1 {'führend' if m1 else 'folgend'}")
    m2 = initiative.get("m2_roh")
    if m2 is not None:
        masse.append(f"M2 Thema {float(m2):.3f}")
    m3 = initiative.get("m3_roh")
    if m3 is not None:
        masse.append(f"M3 Register {float(m3):.3f}")

    if masse:
        zeile2 = Gtk.Label(label="  ".join(masse))
        zeile2.set_xalign(0.0)
        zeile2.add_css_class("caption")
        zeile2.add_css_class("dim-label")
        zeile2.set_selectable(True)
        section.append(zeile2)

    # ── Fehlendes benennen, nicht verschweigen ──
    if fehlend:
        # "steht auf den übrigen" ist falsch, wenn es keine übrigen gibt —
        # dann ist der Wert gar nicht entstanden.
        rest: str = ("— es blieb keines übrig" if wert is None
                     else "— der Wert steht auf den übrigen")
        hinweis = Gtk.Label(
            label=f"nicht messbar in diesem Turn: {', '.join(fehlend)} {rest}"
        )
        hinweis.set_xalign(0.0)
        hinweis.set_wrap(True)
        hinweis.add_css_class("dim-label")
        hinweis.add_css_class("caption")
        section.append(hinweis)

    return section


def _build_repertoire_section(
    repertoire: dict,
    gewichtung: dict,
    cluster:    str,
    gewaehlt:   str,
    verstoesse: list,
) -> Gtk.Box:
    """Sektion 'Repertoire' — der Korridor, in dem die Strategie gewaehlt wurde.

    Zeigt alle sieben Strategien mit ihrer Eignung im aktuellen Cluster und
    der Charakter-Affinitaet, sortiert wie im GV-Prompt (Eignung, dann
    Affinitaet absteigend). Die gewaehlte Strategie ist hervorgehoben.

    **Zwei bewusste Abweichungen vom Prompt-Block:**

    1. Der Prompt laesst 'unpassend' ganz weg — er soll das LLM nicht in
       Versuchung fuehren. Das Panel zeigt sie mit ✗: Wer beurteilen will, ob
       der Korridor richtig gesetzt war, muss sehen, was ausgeschlossen wurde.
    2. `dreischicht_prompt_bauen` setzt bei fehlender Gewichtung 0.5 ein. Das
       Panel tut das **nicht**. Gemessene Affinitaeten liegen bei 0.195 bis
       0.334 — ein Default von 0.5 laege ueber jedem echten Wert und erschiene
       als beste Passung (GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH in bugs.md,
       offen). Fehlt der Wert, steht hier '—' und sonst nichts.

    Eingabe: `repertoire` Kuerzel → Eignung, `gewichtung` Kuerzel → float,
    `gewaehlt` das Kuerzel der gewaehlten Strategie (darf leer sein — bei
    kurzem Vektor waehlt das LLM keine), `verstoesse` die Liste aus dem Node.
    """
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    kopf: str = "Repertoire"
    if cluster:
        kopf += f" — Cluster {cluster.capitalize()}"
    header = Gtk.Label(label=kopf)
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not repertoire:
        leer = Gtk.Label(label="(kein Repertoire in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
    else:
        geordnet = sorted(
            repertoire.items(),
            key=lambda paar: (
                _EIGNUNG_RANG.get(paar[1], 9),
                -float(gewichtung.get(paar[0], 0.0) or 0.0),
            ),
        )
        for kuerzel, eignung in geordnet:
            section.append(_build_repertoire_row(
                kuerzel=kuerzel,
                eignung=str(eignung),
                affinitaet=gewichtung.get(kuerzel),
                ist_gewaehlt=(kuerzel == gewaehlt),
            ))

        if not gewichtung:
            hinweis = Gtk.Label(
                label="(keine Charakter-Gewichtung in diesem Turn — "
                      "die Reihenfolge steht dann allein auf der Eignung)"
            )
            hinweis.set_xalign(0.0)
            hinweis.set_wrap(True)
            hinweis.add_css_class("dim-label")
            hinweis.add_css_class("caption")
            section.append(hinweis)

    section.append(_build_verstoesse_zeile(verstoesse))

    return section


def _build_repertoire_row(
    kuerzel:      str,
    eignung:      str,
    affinitaet:   float | None,
    ist_gewaehlt: bool,
) -> Gtk.Box:
    """★ Im  Impuls              kern        Charakter 35%"""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    marker = Gtk.Label(label=_EIGNUNG_MARKER.get(eignung, "?"))
    marker.set_width_chars(2)
    row.append(marker)

    name: str = f"{_strategie_klartext(kuerzel)} ({kuerzel})"
    name_label = Gtk.Label(label=name)
    name_label.set_xalign(0.0)
    name_label.set_hexpand(True)
    if ist_gewaehlt:
        name_label.add_css_class("success")
    elif eignung == "unpassend":
        name_label.add_css_class("dim-label")
    row.append(name_label)

    eignung_label = Gtk.Label(label=eignung)
    eignung_label.set_xalign(0.0)
    eignung_label.set_width_chars(10)
    eignung_label.add_css_class("caption")
    eignung_label.add_css_class("dim-label")
    row.append(eignung_label)

    # Kein 0.5-Default: fehlt der Wert, steht ein Strich da. Ein Ausfallwert
    # ueber dem gemessenen Bereich saehe wie die beste Passung aus.
    if affinitaet is None:
        aff_text: str = "—"
    else:
        aff_text = f"{float(affinitaet):.0%}"
    aff_label = Gtk.Label(label=aff_text)
    aff_label.set_xalign(1.0)
    aff_label.set_width_chars(5)
    aff_label.add_css_class("caption")
    row.append(aff_label)

    return row


def _build_verstoesse_zeile(verstoesse: list) -> Gtk.Box:
    """Was das LLM ausserhalb des Korridors gewaehlt hat — und verworfen wurde.

    Der Korridor wurde in Chat 114 gebaut, damit eine Strategie ausserhalb des
    Repertoires nicht mehr als leeres Feld verschwindet. Bis Chat 116 war ein
    Verstoss nur im Server-Log sichtbar.
    """
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    box.set_margin_top(4)

    if not verstoesse:
        ok = Gtk.Label(label="Korridor: eingehalten")
        ok.set_xalign(0.0)
        ok.add_css_class("caption")
        ok.add_css_class("dim-label")
        box.append(ok)
        return box

    kopf = Gtk.Label(label=f"Korridor verletzt ({len(verstoesse)}):")
    kopf.set_xalign(0.0)
    kopf.add_css_class("caption")
    kopf.add_css_class("error")
    box.append(kopf)

    for verstoss in verstoesse:
        feld:  str = str(verstoss.get("feld") or "?")
        wert:  str = str(verstoss.get("wert") or "?")
        grund: str = str(verstoss.get("grund") or "ohne Grund")
        zeile = Gtk.Label(label=f"  {feld} '{wert}' verworfen — {grund}")
        zeile.set_xalign(0.0)
        zeile.set_wrap(True)
        zeile.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        zeile.set_selectable(True)
        zeile.add_css_class("caption")
        box.append(zeile)

    return box


def _build_resonanz_section(zeilen: list[str], roh_laenge: int) -> Gtk.Box:
    """Sektion 'Verwandte Erinnerungen' — die zweite Wissensquelle des Nodes.

    Der Server liefert einen fertig formatierten Block, eine Erinnerung je
    Zeile, aufgebaut in `_resonanz_kontext_laden`:

        <Inhalt> (direkt zum Thema; Themen: …; Faerbung: …)
        <Inhalt> (assoziiert ueber 2 Sprung(e); Themen: …)

    Das Panel formatiert nicht nach, es zeigt die Zeilen und ihre Anzahl.
    Bis Chat 116 war das Feld schreib-only: Ob der Node in einem Turn
    ueberhaupt Wissen bekommen hat, stand nur im Server-Log — und genau
    diese Frage blieb bei GV-ENTITY-HOP-FINDET-NICHTS 45 Laeufe unbeobachtet.

    Eingabe: `zeilen` bereits entleert und getrimmt, `roh_laenge` die
    Zeichenzahl des ungeteilten Blocks (fuer den Kuerzungshinweis).
    """
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label=f"Verwandte Erinnerungen ({len(zeilen)})")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not zeilen:
        leer = Gtk.Label(label="(keine verwandten Erinnerungen in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
        return section

    for zeile in zeilen:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        bullet = Gtk.Label(label="●")
        bullet.set_valign(Gtk.Align.START)
        bullet.add_css_class("accent")
        row.append(bullet)

        text_label = Gtk.Label(label=zeile)
        text_label.set_xalign(0.0)
        text_label.set_hexpand(True)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_selectable(True)
        row.append(text_label)

        section.append(row)

    # Ein am Limit abgeschnittener Block sieht sonst aus wie ein Defekt der
    # Schreibseite. Der Hinweis sagt, dass die Kuerzung Absicht ist.
    if roh_laenge >= _GV_RESONANZ_MAX_ZEICHEN:
        hinweis = Gtk.Label(
            label=f"(vom Server auf {_GV_RESONANZ_MAX_ZEICHEN} Zeichen gekürzt — "
                  f"der GV-Prompt hat den vollen Text bekommen)"
        )
        hinweis.set_xalign(0.0)
        hinweis.set_wrap(True)
        hinweis.add_css_class("dim-label")
        hinweis.add_css_class("caption")
        section.append(hinweis)

    return section


def _build_farbton_section(farbton: str) -> Gtk.Box:
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Farbton")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    frame = Gtk.Frame()
    frame.set_margin_top(2)

    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    inner.set_margin_start(8)
    inner.set_margin_end(8)
    inner.set_margin_top(6)
    inner.set_margin_bottom(6)

    if farbton:
        text_label = Gtk.Label(label=farbton)
        text_label.set_xalign(0.0)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_selectable(True)
    else:
        text_label = Gtk.Label(label="(kein Farbton in diesem Turn)")
        text_label.set_xalign(0.0)
        text_label.add_css_class("dim-label")

    inner.append(text_label)
    frame.set_child(inner)
    section.append(frame)

    return section


def _build_dreischicht_section(
    sektor_index: int,
    sektor_name: str,
    cluster: str,
    achsen: dict,
    absicht: str,
    strategie: str,
    vehikel: str,
) -> Gtk.Box:
    """Sektion Dreischicht: Sektor, Cluster, Achsen, gewaehlte Strategie."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Dreischicht")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    # Sektor + Cluster
    if sektor_name or cluster:
        sektor_text: str = f"#{sektor_index} {sektor_name}" if sektor_name else ""
        if cluster:
            sektor_text += f"  (Cluster: {cluster.capitalize()})"
        sektor_label = Gtk.Label(label=sektor_text.strip())
        sektor_label.set_xalign(0.0)
        sektor_label.set_wrap(True)
        sektor_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        section.append(sektor_label)

    # Absicht / Strategie / Vehikel — kompakte Zeile
    if absicht or strategie or vehikel:
        teile: list[str] = []
        if absicht:
            teile.append(f"Absicht: {absicht.capitalize()}")
        if strategie:
            # Kuerzel aufloesen: 'Sa' allein sagt niemandem etwas, und eine
            # Legende gibt es im Client nicht. Das Kuerzel bleibt in Klammern
            # stehen, weil der Server es in Logs und Prompt so nennt.
            teile.append(f"Strategie: {_strategie_klartext(strategie)} ({strategie})")
        if vehikel:
            teile.append(f"als {vehikel.capitalize()}")
        strat_label = Gtk.Label(label="  ·  ".join(teile))
        strat_label.set_xalign(0.0)
        strat_label.set_wrap(True)
        strat_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        strat_label.add_css_class("caption")
        section.append(strat_label)

    # Achsen — kompakte einzeilige Darstellung
    # Format in Redis: flache Keys, z.B. energie_roh=0.7, energie=1,
    # richtung="plateau", richtung_bin=0, valenz_bin=1 (ohne Rohwert)
    if achsen:
        achsen_teile: list[str] = []
        for kuerzel, roh_key, bin_key in [
            ("E", "energie_roh", "energie"),
            ("R", "richtung",    "richtung_bin"),
            ("N", "naehe_roh",   "naehe"),
            ("V", None,          "valenz_bin"),
            ("T", "tiefe_roh",   "tiefe"),
            ("I", "initiative_roh", "initiative"),
        ]:
            binary = achsen.get(bin_key, "")
            if roh_key is not None:
                raw = achsen.get(roh_key, "")
            else:
                raw = ""
            if raw != "" or binary != "":
                achsen_teile.append(f"{kuerzel}={binary}({raw})")
        # Drive separat (kein binaerer Wert)
        drive: float = float(achsen.get("drive", 0.0) or 0.0)
        achsen_teile.append(f"Drive={drive:.2f}")

        if achsen_teile:
            achsen_label = Gtk.Label(label="  ".join(achsen_teile))
            achsen_label.set_xalign(0.0)
            achsen_label.add_css_class("caption")
            achsen_label.add_css_class("dim-label")
            achsen_label.set_selectable(True)
            section.append(achsen_label)

    # Leer-Zustand
    if not sektor_name and not cluster and not absicht:
        leer = Gtk.Label(label="(keine Dreischicht-Daten in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)

    return section


def _build_spruenge_section(sprung_1: str, sprung_2: str, sprung_3: str) -> Gtk.Box:
    """Sektion mit den drei Gedankenspruengen des GV."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Sprünge")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    hat_spruenge: bool = False
    for nummer, text in [("1", sprung_1), ("2", sprung_2), ("3", sprung_3)]:
        if not text:
            continue
        hat_spruenge = True
        label = Gtk.Label(label=f"{nummer}: {text}")
        label.set_xalign(0.0)
        label.set_wrap(True)
        label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_selectable(True)
        section.append(label)

    if not hat_spruenge:
        leer = Gtk.Label(label="(keine Sprünge in diesem Turn)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)

    return section


def _build_impuls_section(impuls: str) -> Gtk.Box:
    """Sektion mit dem Impuls — Richtungsangabe fuer den Responder."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label="Impuls")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    frame = Gtk.Frame()
    frame.set_margin_top(2)

    inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    inner.set_margin_start(8)
    inner.set_margin_end(8)
    inner.set_margin_top(6)
    inner.set_margin_bottom(6)

    if impuls:
        text_label = Gtk.Label(label=impuls)
        text_label.set_xalign(0.0)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_selectable(True)
    else:
        text_label = Gtk.Label(label="(kein Impuls in diesem Turn)")
        text_label.set_xalign(0.0)
        text_label.add_css_class("dim-label")

    inner.append(text_label)
    frame.set_child(inner)
    section.append(frame)

    return section
