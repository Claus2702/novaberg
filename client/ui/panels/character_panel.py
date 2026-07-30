"""
Charakter-Panel — die zwei Charakter-Räder und die 5 destillierten Profile.

Liest ``GET /gedaechtnis/hash/{user_id}`` und rendert oben die beiden
Räder des gewählten Subjekts als Radar-Diagramme, darunter die 5 Profile
("Kern", "Adaptiv", "Intentionen", "Emotionen", "Beziehung").

**Beide Räder beschreiben dasselbe Subjekt gegenüber seinem Gegenüber,
beantworten aber verschiedene Fragen.** Die Zuwendung (12 Speichen,
``novaberg-salienz-berechnung_k.md`` §5) fragt, wie sehr ihm das Gegenüber
gilt; der Initiative-Versatz (10 Speichen, ``novaberg-gv-initiative_k.md``
§6) fragt, ob er im Gespräch die Führung überlässt oder behält. Deshalb
zwei Diagramme nebeneinander und nicht eines mit 22 Achsen.

Welches Subjekt gezeigt wird, entscheidet der Perspektive-Selector: Auf
``(nova, meister)`` steht Novas Rad — der Wert, den die Salienz-Formel
liest —, auf ``(meister, nova)`` spiegelbildlich das des Nutzers.

Response-Format (siehe ``server/api/gedaechtnis.py``):

    {
        "kern_hash":                str,
        "adaptive_hash":            str,
        "intentions_profil":        str,
        "emotions_profil":          str,
        "beziehungsprofil":         str,
        "kern_aktualisiert":        str,   # ISO-Timestamp
        "adaptive_aktualisiert":    str,
        "intentions_aktualisiert":  str,
        "emotions_aktualisiert":    str,
        "beziehung_aktualisiert":   str,
        "zuwendung":  {"wert": float|None, "quelle": str,
                       "erhoben_am": str, "rad": dict, "lesbar": bool},
        "initiative": {...dieselbe Form...},
    }
"""

import logging
from dataclasses import dataclass

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.formatierung import zeit_kurz  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402
from ui.widgets.radar_chart import RadarChart  # noqa: E402


logger = logging.getLogger(__name__)


# (Überschrift, Daten-Schlüssel, Schlüssel des Timestamps — "" falls keiner).
_SECTIONS: list[tuple[str, str, str]] = [
    ("Kern",        "kern_hash",         "kern_aktualisiert"),
    ("Adaptiv",     "adaptive_hash",     "adaptive_aktualisiert"),
    ("Intentionen", "intentions_profil", "intentions_aktualisiert"),
    ("Emotionen",   "emotions_profil",   "emotions_aktualisiert"),
    ("Beziehung",   "beziehungsprofil",  "beziehung_aktualisiert"),
]


@dataclass(frozen=True)
class RadDefinition:
    """Bauplan eines Charakter-Rades für die Anzeige.

    Hält Titel, Datenschlüssel und die Speichen beider Seiten in
    **Zeichenreihenfolge**. Die Reihenfolge steht hier und wird nicht aus
    dem JSON übernommen: Ein Dict hat zwar seit Python 3.7 eine stabile
    Reihenfolge, aber sie ist die des Erzeugers — änderte der Server seine
    Speichen-Definition, wanderten die Achsen still, und das Diagramm
    zeigte weiter etwas Plausibles.

    Attributes:
        titel:      Überschrift über dem Diagramm.
        schluessel: Schlüssel des Blocks in der Server-Antwort.
        hoch:       Speichen der Zuwendungs- bzw. Folgen-Seite als
                    (JSON-Name, Achsen-Kurzform, Anzeigename).
        runter:     Speichen der Gegenseite, gleiche Form.
        format:     Format-String für den gerechneten Wert.
    """

    titel: str
    schluessel: str
    hoch: tuple[tuple[str, str, str], ...]
    runter: tuple[tuple[str, str, str], ...]
    format: str

    @property
    def speichen(self) -> tuple[tuple[str, str, str], ...]:
        """Alle Speichen in Achsenreihenfolge: erst hoch, dann runter.

        Damit liegt die Zuwendungs-Seite auf der rechten Hälfte des Sterns
        und die Abwendungs-Seite auf der linken — ein Rad, das nach rechts
        ausschlägt, ist zugewandt.
        """
        return self.hoch + self.runter

    @property
    def achsen(self) -> list[str]:
        """Die Kurzformen für die Achsenbeschriftung, in Zeichenreihenfolge."""
        return [kurz for _name, kurz, _lang in self.speichen]


# Die zwölf Speichen der Zuwendung. Züge und Reihenfolge nach
# novaberg-salienz-berechnung_k.md §5; die Namen sind die JSON-Schlüssel aus
# RAD_ZUG_HOCH / RAD_ZUG_RUNTER (server/agents/charakter/destillation.py).
_ZUWENDUNG = RadDefinition(
    titel="Zuwendung",
    schluessel="zuwendung",
    hoch=(
        ("treue",          "Tr", "Treue"),
        ("dienst",         "Di", "Dienst"),
        ("pflicht",        "Pf", "Pflicht"),
        ("aufmerksamkeit", "Au", "Aufmerksamkeit"),
        ("wissbegier",     "Wi", "Wissbegier"),
        ("wohlwollen",     "Wo", "Wohlwollen"),
    ),
    runter=(
        ("widerspenstig",  "Wd", "Widerspenstigkeit"),
        ("gleichgueltig",  "Gl", "Gleichgültigkeit"),
        ("selbstbezogen",  "Sb", "Selbstbezogenheit"),
        ("langeweile",     "La", "Langeweile"),
        ("distanz",        "Dz", "Distanz"),
        ("misstrauen",     "Ms", "Misstrauen"),
    ),
    format="{:.2f}",
)

# Die zehn Speichen des Initiative-Versatzes, nach
# novaberg-gv-initiative_k.md §6.2. Vorzeichen im Format, weil ein Versatz
# von +0.02 und einer von −0.02 entgegengesetzte Aussagen sind.
_INITIATIVE = RadDefinition(
    titel="Initiative",
    schluessel="initiative",
    hoch=(
        ("folgsamkeit",       "Fo", "Folgsamkeit"),
        ("anschlussfreude",   "Af", "Anschlussfreude"),
        ("zurueckhaltung",    "Zu", "Zurückhaltung"),
        ("antwortende_rolle", "Ar", "Antwortende Rolle"),
        ("behutsamkeit",      "Be", "Behutsamkeit"),
    ),
    runter=(
        ("lenkungsdrang",      "Le", "Lenkungsdrang"),
        ("eigensinn",          "Ei", "Eigensinn"),
        ("assoziationsdrang",  "As", "Assoziationsdrang"),
        ("widerspruchsfreude", "Wf", "Widerspruchsfreude"),
        ("gespraechsdistanz",  "Gd", "Gesprächsdistanz"),
    ),
    format="{:+.3f}",
)

_RAEDER: tuple[RadDefinition, ...] = (_ZUWENDUNG, _INITIATIVE)


class CharacterPanel(PanelBase):
    """Zeigt die 5 Profile des Charakter-Hash."""

    PANEL_ID = "charakter"
    # Der Text ist zugleich der Schluessel, ueber den die Toolbar den Button
    # mit diesem Panel verbindet (`ui/main_window.py`, `_TOOLBAR_PANELS`).
    # Wer ihn hier aendert, aendert ihn dort mit — sonst oeffnet der Button
    # nichts mehr, und zwar ohne Fehler.
    PANEL_LABEL = "🧬 Charakter"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = True
    PERSPEKTIVE_BIDIREKTIONAL = True  # Beide Richtungen: User-Hash + Nova-Hash
    DEFAULT_WIDTH = 520
    DEFAULT_HEIGHT = 720

    def _build_content(self) -> None:
        """Scroll-Container: oben die zwei Räder, darunter die 5 Sektionen."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(self._outer_box)

        # Die Diagramme werden einmal gebaut und danach nur noch befüllt —
        # ein Neubau bei jedem Refresh liesse sie sichtbar flackern.
        radar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        radar_box.set_halign(Gtk.Align.CENTER)

        self._radare: dict[str, RadarChart] = {}
        for definition in _RAEDER:
            chart = RadarChart(
                definition.achsen, title=definition.titel, size=190,
            )
            self._radare[definition.schluessel] = chart
            radar_box.append(chart)

        self._outer_box.append(radar_box)

        # Kennzahl, Herkunft und Speichen — wird bei jedem Refresh ersetzt.
        self._rad_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._outer_box.append(self._rad_box)

        # Trennlinie zwischen dem letzten Rad und dem ersten Profil. Sie steht
        # hier und nicht in einer der beiden Boxen, weil sie zu keiner von
        # beiden gehoert — und weil `_outer_box` denselben Abstand fuehrt wie
        # die Boxen darin, sitzt sie damit im selben Raster wie die
        # Trennlinien zwischen den Profilen.
        self._outer_box.append(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        )

        self._profil_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._outer_box.append(self._profil_box)

        placeholder = Gtk.Label(label="Lade Charakter …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._profil_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Charakter-Hash-Profile fuer das aktuell gewaehlte Gespraechspaar.

        Filtert nach ``user_id`` + ``character_id`` (Paar-Schema seit Chat 62).
        """
        params: dict = self._get_api_params()
        url: str = f"{SERVER_URL}/gedaechtnis/hash/{params['user_id']}"
        query: dict = {"character_id": params["character_id"]}
        logger.debug(f"CharacterPanel: GET {url} {query}")
        response = requests.get(url, params=query, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Befüllt die zwei Räder und baut pro Profil eine Sektion."""
        befuellte: int = sum(1 for _, key, _ in _SECTIONS if data.get(key))
        logger.info(
            f"CharacterPanel '{self.user_id}': "
            f"{befuellte}/{len(_SECTIONS)} Profile befüllt"
        )

        self._update_raeder(data)

        _clear_box(self._profil_box)

        for idx, (titel, data_key, ts_key) in enumerate(_SECTIONS):
            if idx > 0:
                self._profil_box.append(
                    Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                )

            inhalt: str = str(data.get(data_key, "") or "")
            roh: str = str(data.get(ts_key, "") or "") if ts_key else ""

            self._profil_box.append(
                _build_profile_section(titel, inhalt, zeit_kurz(roh))
            )

    def _update_raeder(self, data: dict) -> None:
        """Setzt beide Radar-Diagramme und baut die Kennzahl-Sektionen darunter.

        Ein Rad, das der Server als nicht lesbar meldet, wird **nicht**
        gezeichnet: Zwölf Nullen sähen aus wie ein Charakter ohne jede
        Zuwendung, und genau diese Verwechslung ist die Fehlerklasse, gegen
        die das Herkunftsfeld gebaut wurde.
        """
        _clear_box(self._rad_box)

        for idx, definition in enumerate(_RAEDER):
            # Dieselbe Trennung wie zwischen den Profilen: eine Linie zwischen
            # den Bloecken, keine davor und keine danach.
            if idx > 0:
                self._rad_box.append(
                    Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                )

            block: dict = data.get(definition.schluessel) or {}
            chart: RadarChart = self._radare[definition.schluessel]

            werte, fehlend = _speichen_lesen(block, definition, self.user_id)
            if werte is None:
                # set_unbekannt raeumt den Nabenversatz mit ab — ohne
                # Speichen gibt es keine Bilanz aus ihnen.
                chart.set_unbekannt(_leer_grund(block))
            else:
                chart.set_data(werte)
                chart.set_nabe_versatz(
                    _nabe_versatz(block, self.user_id, definition.schluessel)
                )

            self._rad_box.append(_build_rad_section(definition, block, fehlend))


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Räder
# ═══════════════════════════════════════════════════════════════════
def _leer_grund(block: dict) -> str:
    """Formuliert, warum ein Rad keine Daten hat — für die Diagramm-Mitte."""
    if not block:
        return "kein Datenblock"
    if not block.get("rad"):
        return "nicht erhoben"
    return "nicht lesbar"


def _nabe_versatz(block: dict, subjekt: str, rad: str) -> float | None:
    """Rechnet den Abstand des Ergebnisses von der Nabe in einen Anteil um.

    Beide Räder haben eine Nabe und zwei Grenzen, und **beide Seiten sind
    verschieden weit**: Das Zuwendungs-Rad reicht 0.60 nach oben und 0.40
    nach unten. Ein Anteil, der beide Seiten durch dieselbe Spanne teilte,
    zeigte volle Auslenkung nach unten kürzer als nach oben, obwohl beide
    ihre Grenze exakt treffen. Deshalb wird je Seite gegen ihre eigene
    Spanne normiert.

    Nabe und Grenzen kommen vom Server. Sie sind dort über die Umgebung
    einstellbar; eine Kopie hier wäre eine zweite Quelle derselben Größe.

    Args:
        block:   Der Rad-Block der Server-Antwort.
        subjekt: ``user_id`` der Perspektive, nur für die Logausgabe.
        rad:     Name des Rades, nur für die Logausgabe.

    Returns:
        Anteil in [−1.0, +1.0], oder ``None``, wenn kein Wert vorliegt oder
        die Grenzen fehlen — dann wird nichts gezeichnet statt geraten.
    """
    # ── Eingabe ──────────────────────────────────────────────────────
    wert = block.get("wert")
    nabe = block.get("nabe")
    unten = block.get("minimum")
    oben = block.get("maximum")

    if wert is None or nabe is None or unten is None or oben is None:
        logger.warning(
            f"CharacterPanel '{subjekt}': Rad '{rad}' ohne Wert oder Grenzen "
            f"(wert={wert}, nabe={nabe}, min={unten}, max={oben}) — "
            f"Nabenversatz wird nicht gezeichnet"
        )
        return None

    # ── Verarbeitung ─────────────────────────────────────────────────
    spanne: float = (float(oben) - float(nabe)) if wert >= nabe else (float(nabe) - float(unten))

    if spanne <= 0.0:
        logger.error(
            f"CharacterPanel '{subjekt}': Rad '{rad}' hat auf der belegten "
            f"Seite keine Spanne (nabe={nabe}, min={unten}, max={oben})"
        )
        return None

    # ── Ausgabe ──────────────────────────────────────────────────────
    return max(-1.0, min(1.0, (float(wert) - float(nabe)) / spanne))


def _speichen_lesen(
    block: dict, definition: RadDefinition, subjekt: str,
) -> tuple[list[float] | None, list[str]]:
    """Liest die Speichen eines Rades in Achsenreihenfolge aus dem Datenblock.

    Gelesen wird **nach Namen**, nicht nach Position: Die Reihenfolge im
    JSON ist die des Erzeugers, die Reihenfolge der Achsen gehört der
    Anzeige. Fehlt eine Speiche, wird das gemeldet und nicht mit 0.0
    überdeckt — eine ergänzte Null ist von einer gemessenen nicht zu
    unterscheiden, sobald sie einmal im Diagramm steht.

    Args:
        block:      Der Rad-Block der Server-Antwort.
        definition: Bauplan mit Namen und Reihenfolge der Speichen.
        subjekt:    ``user_id`` der Perspektive, nur für die Logausgabe.

    Returns:
        ``(werte, fehlend)``. ``werte`` ist ``None``, wenn der Server das
        Rad als nicht lesbar meldet; ``fehlend`` nennt die Speichen, die im
        gelieferten Rad keinen Eintrag hatten.
    """
    # ── Eingabe ──────────────────────────────────────────────────────
    if not block.get("lesbar"):
        logger.warning(
            f"CharacterPanel '{subjekt}': Rad '{definition.schluessel}' "
            f"nicht lesbar (quelle={block.get('quelle', '?')})"
        )
        return None, []

    rad: dict = block.get("rad") or {}

    # ── Verarbeitung ─────────────────────────────────────────────────
    werte:   list[float] = []
    fehlend: list[str] = []

    for seite, speichen in (("hoch", definition.hoch), ("runter", definition.runter)):
        seiten_werte: dict = rad.get(seite) or {}
        for name, _kurz, lang in speichen:
            if name not in seiten_werte:
                fehlend.append(lang)
                werte.append(0.0)
                continue
            werte.append(float(seiten_werte[name]))

    # ── Ausgabe ──────────────────────────────────────────────────────
    if fehlend:
        logger.error(
            f"CharacterPanel '{subjekt}': Rad '{definition.schluessel}' — "
            f"{len(fehlend)} von {len(definition.speichen)} Speichen fehlen "
            f"im gelieferten JSON: {', '.join(fehlend)}"
        )

    return werte, fehlend


def _build_rad_section(
    definition: RadDefinition, block: dict, fehlend: list[str],
) -> Gtk.Box:
    """Baut Kennzahl, Herkunft und Speichenliste unter einem Radar-Diagramm."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    # ── Kopfzeile: Titel, Wert, Herkunft ─────────────────────────────
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    titel = Gtk.Label(label=definition.titel)
    titel.set_xalign(0.0)
    titel.add_css_class("heading")
    head.append(titel)

    wert = block.get("wert")
    wert_label = Gtk.Label(
        label=definition.format.format(wert) if wert is not None else "—"
    )
    wert_label.set_xalign(0.0)
    wert_label.set_hexpand(True)
    head.append(wert_label)

    # Die Herkunft steht neben dem Wert und nicht im Log: 'default' heisst,
    # dass nie erhoben wurde, und sieht als Zahl genau wie ein Messergebnis
    # aus (novaberg-lesson_l_default-wie-fehlschlag.md).
    quelle: str = str(block.get("quelle") or "unbekannt")
    zeit: str = zeit_kurz(str(block.get("erhoben_am") or ""))
    herkunft = Gtk.Label(
        label=f"{quelle}{f' · {zeit}' if zeit else ''}"
    )
    herkunft.set_xalign(1.0)
    herkunft.add_css_class("dim-label")
    if quelle != "destilliert":
        herkunft.add_css_class("emotion-negativ")
    head.append(herkunft)

    section.append(head)

    # ── Warnung bei unvollständigem Rad ──────────────────────────────
    if fehlend:
        warnung = Gtk.Label(
            label=f"⚠ {len(fehlend)} Speichen fehlen: {', '.join(fehlend)}"
        )
        warnung.set_xalign(0.0)
        warnung.set_wrap(True)
        warnung.add_css_class("emotion-negativ")
        section.append(warnung)

    # ── Speichen, beide Seiten getrennt ──────────────────────────────
    if not block.get("lesbar"):
        hinweis = Gtk.Label(label=f"({_leer_grund(block)})")
        hinweis.set_xalign(0.0)
        hinweis.add_css_class("dim-label")
        section.append(hinweis)
        return section

    rad: dict = block.get("rad") or {}
    for seite, speichen, ueberschrift in (
        ("hoch",   definition.hoch,   "▲ hoch"),
        ("runter", definition.runter, "▼ runter"),
    ):
        kopf = Gtk.Label(label=ueberschrift)
        kopf.set_xalign(0.0)
        kopf.add_css_class("dim-label")
        kopf.add_css_class("caption")
        section.append(kopf)

        seiten_werte: dict = rad.get(seite) or {}
        for name, kurz, lang in speichen:
            section.append(
                _build_speiche_row(kurz, lang, seiten_werte.get(name))
            )

    return section


def _build_speiche_row(kurz: str, lang: str, wert: float | None) -> Gtk.Box:
    """Baut eine Speichen-Zeile: Kurzform | Name | Wert | LevelBar.

    Ein fehlender Wert erscheint als ``—`` mit leerem Balken, nicht als 0.00.
    """
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    kurz_label = Gtk.Label(label=f"  {kurz}")
    kurz_label.set_xalign(0.0)
    kurz_label.set_width_chars(4)
    kurz_label.add_css_class("dim-label")
    row.append(kurz_label)

    name_label = Gtk.Label(label=lang)
    name_label.set_xalign(0.0)
    name_label.set_width_chars(18)
    row.append(name_label)

    wert_label = Gtk.Label(label="—" if wert is None else f"{float(wert):.1f}")
    wert_label.set_xalign(1.0)
    wert_label.set_width_chars(4)
    row.append(wert_label)

    bar = Gtk.LevelBar()
    bar.set_min_value(0.0)
    bar.set_max_value(1.0)
    bar.set_value(0.0 if wert is None else max(0.0, min(1.0, float(wert))))
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)
    row.append(bar)

    return row


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Profile
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_profile_section(titel: str, inhalt: str, timestamp: str) -> Gtk.Box:
    """Baut eine Profil-Sektion: Überschrift [+ Zeitstempel] + Fließtext."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    # Kopfzeile: Titel (fett) + optional Zeitstempel rechts.
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    title_label = Gtk.Label(label=titel)
    title_label.set_xalign(0.0)
    title_label.set_hexpand(True)
    title_label.add_css_class("heading")
    head.append(title_label)

    if timestamp:
        ts_label = Gtk.Label(label=f"aktualisiert: {timestamp}")
        ts_label.set_xalign(1.0)
        ts_label.add_css_class("dim-label")
        head.append(ts_label)

    section.append(head)

    # Inhalt — umbrechend, selektierbar. Bei leerem Profil dim-Hinweis.
    if inhalt:
        body = Gtk.Label(label=inhalt)
        body.set_xalign(0.0)
        body.set_wrap(True)
        body.set_selectable(True)
        section.append(body)
    else:
        leer = Gtk.Label(label="(leer)")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)

    return section
