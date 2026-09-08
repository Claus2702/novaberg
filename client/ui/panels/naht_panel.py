"""
Naht-Panel — Ist-Spanne gegen Zielspanne jeder Naht des Systems.

Liest ``GET /admin/naehte`` und zeichnet je Naht ein Lineal: die
**Zielspanne** als Feld, darin die **gemessene** Spanne als Balken. Die
Achse ist auf die je eigene Zielspanne normiert — dadurch sind Groessen
mit ganz verschiedenen Skalen (``fasz_faktor`` laeuft auf [0,6…1,4],
``neugier_vektor`` auf [0…0,5]) direkt vergleichbar.

Zwei Balken je Zeile, und der Vergleich ist die Aussage:

* **blass** — der Gesamtbestand
* **kraeftig** — die letzten 14 Tage

Eine Naht, die im Gesamtbestand ueberschreitet und im jungen Fenster nicht,
ist behoben; eine, die in beiden ueberschreitet, ist offen. Nur eines von
beidem zu zeigen macht aus diesen zwei Lagen dieselbe Zeile.

**Wozu das Panel da ist.** ``F-NAHT-1`` verlangt, dass zusammengefuehrte
Groessen an der Naht auf derselben Skala liegen. Fuer die
**Ueberschreitung** gibt es im Haltungsraum einen Waechter (``ausserhalb``,
seit dem 31.07.2026 persistiert). Fuer die **Unterschreitung** gibt es
keinen — eine Groesse, die ihre Spanne zu 5 % ausschoepft, verletzt keine
Grenze und loest keine Warnung aus. Sie multipliziert faktisch mit einer
Konstanten und traegt keine Information. Dieses Panel ist dieser Waechter.

Response-Format (siehe ``server/memory/naht_spannen.py``):

    {
        "tage": 14,
        "fehler": 0,
        "naehte": [
            {
                "gruppe": "Haltung", "name": "umfang", "ziel": [0.0, 1.0],
                "gesamt": {"n": …, "min": …, "max": …,
                           "ausschoepfung": …, "ueberschreitung": bool},
                "jung":   { … dasselbe … }
            }, …
        ]
    }
"""

import logging

import gi
import requests

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402

logger = logging.getLogger(__name__)

_RGBA = tuple[float, float, float, float]

#: Die Achse reicht ueber die Zielspanne hinaus, damit eine Ueberschreitung
#: sichtbar wird statt am Rand zu kleben. **Aus der Messung abgeleitet:** Die
#: staerkste gemessene Ueberschreitung liegt bei 155 % (`naehe` im
#: Gesamtbestand), der tiefste Ausreisser bei -0,30 der Zielspanne.
_ACHSE_MIN: float = -0.35
_ACHSE_MAX: float = 1.65

_ZEILE_HOEHE: int = 30
_LINEAL_BREITE: int = 260

#: Unter diesem Anteil gilt eine Naht als **karg** — sie nutzt ihre Spanne
#: kaum. Die Grenze ist gesetzt und nicht gemessen; sie trennt im heutigen
#: Bestand `resonanz` (40,0 %) von `fasz_faktor` (37,9 %) und ist damit die
#: Stelle, an der die Messung selbst noch keine Aussage macht.
_KARG_GRENZE: float = 40.0

_FELD_HEX:      str = "#2b3038"   # Zielspanne
_FELD_RAND_HEX: str = "#454d58"
_JUNG_HEX:      str = "#d8dee6"   # letzte 14 Tage
_ALT_HEX:       str = "#6e7883"   # Gesamtbestand
_UEBER_HEX:     str = "#e8674a"   # verlaesst die Zielspanne
_KARG_HEX:      str = "#7f8894"   # nutzt unter _KARG_GRENZE
_VOLL_HEX:      str = "#56a392"   # schoepft die Spanne aus


def _hex_to_rgba(farbe: str, alpha: float = 1.0) -> _RGBA:
    """Wandelt ``#rrggbb`` in das Tupel, das Cairo erwartet."""
    farbe = farbe.lstrip("#")
    return (
        int(farbe[0:2], 16) / 255.0,
        int(farbe[2:4], 16) / 255.0,
        int(farbe[4:6], 16) / 255.0,
        alpha,
    )


def _normiert(wert: float, ziel: list[float]) -> float:
    """Rechnet einen Messwert in Anteile der Zielspanne um.

    Vorbedingung: ``ziel`` traegt zwei Werte, deren zweiter groesser ist.
    Nachbedingung: 0.0 am unteren, 1.0 am oberen Ende der Zielspanne;
        Werte ausserhalb liegen ausserhalb — **es wird nicht geklemmt**,
        weil genau die Ueberschreitung sichtbar werden soll.
    """
    breite: float = ziel[1] - ziel[0]
    if breite <= 0:
        return 0.0
    return (wert - ziel[0]) / breite


class NahtPanel(PanelBase):
    """Tafel der Nahtspannen — was ueberschreitet, was seine Skala nicht nutzt."""

    PANEL_ID    = "naehte"
    PANEL_LABEL = "📏 Nahtspannen"
    UNIQUE      = True
    CATEGORY    = "on_demand"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 760
    DEFAULT_HEIGHT = 720

    def _build_content(self) -> None:
        """Bilanzzeile, Legende und ein scrollbarer Block je Gruppe."""
        self._bilanz = Gtk.Label()
        self._bilanz.set_xalign(0.0)
        self._bilanz.set_wrap(True)
        self.content_area.append(self._bilanz)

        legende = Gtk.Label()
        legende.set_xalign(0.0)
        legende.set_markup(
            "<small>Achse: die eigene Zielspanne, auf 0…1 normiert · "
            "<b>kräftig</b> = letzte Tage · blass = Gesamtbestand</small>"
        )
        legende.set_opacity(0.7)
        self.content_area.append(legende)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._liste = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scroll.set_child(self._liste)

        platzhalter = Gtk.Label(label="Lade Nahtspannen …")
        platzhalter.set_xalign(0.0)
        self._liste.append(platzhalter)

        self.content_area.append(scroll)

    def load_data(self) -> dict:
        """Holt die Erhebung. Blockiert, laeuft im Hintergrund-Thread."""
        antwort = requests.get(
            f"{SERVER_URL}/admin/naehte", timeout=PANEL_REQUEST_TIMEOUT,
        )
        antwort.raise_for_status()
        return antwort.json()

    def _update_ui(self, daten: dict) -> None:
        """Baut die Tafel neu auf. Laeuft im UI-Thread."""
        kind = self._liste.get_first_child()
        while kind is not None:
            naechstes = kind.get_next_sibling()
            self._liste.remove(kind)
            kind = naechstes

        naehte: list[dict] = daten.get("naehte", [])
        tage: int = daten.get("tage", 0)
        self._bilanz.set_markup(self._bilanz_text(naehte, tage, daten))

        gruppen: list[str] = []
        for n in naehte:
            if n["gruppe"] not in gruppen:
                gruppen.append(n["gruppe"])

        for gruppe in gruppen:
            self._liste.append(self._gruppe_bauen(
                gruppe, [n for n in naehte if n["gruppe"] == gruppe],
            ))

    def _bilanz_text(self, naehte: list[dict], tage: int, daten: dict) -> str:
        """Die drei Zahlen, die vor der Tafel stehen.

        **Behoben ist eine eigene Zahl**, weil sie sonst in *„keine
        Ueberschreitung"* verschwindet: Eine Naht, die frueher ausbrach und
        heute nicht mehr, belegt, dass eine Abhilfe gewirkt hat.
        """
        ueber: int = sum(1 for n in naehte if n["jung"]["ueberschreitung"])
        behoben: int = sum(
            1 for n in naehte
            if n["gesamt"]["ueberschreitung"] and not n["jung"]["ueberschreitung"]
        )
        karg: int = sum(
            1 for n in naehte
            if (n["jung"]["ausschoepfung"] or 0) < _KARG_GRENZE
            and n["jung"]["n"] > 0
        )
        ohne_ziel: int = sum(1 for n in naehte if n["ziel"] is None)

        teile: list[str] = [
            f"<b>{len(naehte)}</b> Nähte · Fenster <b>{tage}</b> Tage",
            f"<span foreground='{_UEBER_HEX}'><b>{ueber}</b> überschreitet</span>",
            f"<b>{behoben}</b> behoben",
            f"<span foreground='{_KARG_HEX}'><b>{karg}</b> unter "
            f"{_KARG_GRENZE:.0f} %</span>",
            f"<b>{ohne_ziel}</b> ohne benannte Zielspanne",
        ]
        if daten.get("fehler"):
            teile.append(
                f"<span foreground='{_UEBER_HEX}'><b>{daten['fehler']}</b> "
                "Abfragen gescheitert</span>"
            )
        return " · ".join(teile)

    def _gruppe_bauen(self, name: str, naehte: list[dict]) -> Gtk.Box:
        """Ein Block mit Überschrift und einer Zeile je Naht."""
        block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        kopf = Gtk.Label()
        kopf.set_xalign(0.0)
        kopf.set_markup(f"<b>{name}</b>")
        kopf.set_margin_top(6)
        block.append(kopf)

        for naht in naehte:
            block.append(self._zeile_bauen(naht))
        return block

    def _zeile_bauen(self, naht: dict) -> Gtk.Box:
        """Name, Lineal und Zahlenspalte einer Naht."""
        zeile = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        name = Gtk.Label()
        name.set_xalign(0.0)
        name.set_width_chars(20)
        name.set_max_width_chars(20)
        name.set_ellipsize(Pango.EllipsizeMode.END)
        name.set_markup(f"<tt>{naht['name']}</tt>")
        name.set_tooltip_text(self._tooltip(naht))
        zeile.append(name)

        flaeche = Gtk.DrawingArea()
        flaeche.set_content_width(_LINEAL_BREITE)
        flaeche.set_content_height(_ZEILE_HOEHE)
        flaeche.set_hexpand(True)
        flaeche.set_draw_func(self._lineal_zeichnen, naht)
        zeile.append(flaeche)

        werte = Gtk.Label()
        werte.set_xalign(1.0)
        werte.set_width_chars(22)
        werte.set_markup(self._werte_markup(naht))
        zeile.append(werte)
        return zeile

    def _tooltip(self, naht: dict) -> str:
        """Die vollen Zahlen beider Fenster — sie passen nicht in die Zeile."""
        g, j = naht["gesamt"], naht["jung"]
        ziel: str = (
            f"{naht['ziel'][0]:g} … {naht['ziel'][1]:g}"
            if naht["ziel"] else "nicht benannt"
        )
        zeilen: list[str] = [f"{naht['name']}  ·  Zielspanne {ziel}"]
        for titel, teil in (("gesamt", g), ("Fenster", j)):
            if teil["n"] and teil["min"] is not None:
                zeilen.append(
                    f"{titel}: {teil['min']:.4f} … {teil['max']:.4f}  "
                    f"(n = {teil['n']})"
                )
            else:
                zeilen.append(f"{titel}: keine Werte")
        if naht["ziel"] is None:
            zeilen.append(
                "Ohne benannte Zielspanne kann keine verletzt werden — "
                "die Naht ist nicht justiert, sondern ungeprüft."
            )
        return "\n".join(zeilen)

    def _werte_markup(self, naht: dict) -> str:
        """Ausschoepfung und Ist-Spanne des jungen Fensters, rechtsbuendig."""
        j = naht["jung"]
        if not j["n"] or j["min"] is None:
            return "<small>keine Werte</small>"
        if j["ausschoepfung"] is None:
            return (
                f"<tt><small>{j['min']:.3f} … {j['max']:.3f}</small></tt>\n"
                "<small>ohne Ziel</small>"
            )
        farbe: str = _JUNG_HEX
        if j["ueberschreitung"]:
            farbe = _UEBER_HEX
        elif j["ausschoepfung"] < _KARG_GRENZE:
            farbe = _KARG_HEX
        elif j["ausschoepfung"] >= 95.0:
            farbe = _VOLL_HEX
        return (
            f"<span foreground='{farbe}'><b>{j['ausschoepfung']:.1f} %</b></span>"
            f"<tt><small>  {j['min']:.3f}…{j['max']:.3f}</small></tt>"
        )

    def _lineal_zeichnen(
        self, flaeche: Gtk.DrawingArea, cr, breite: int, hoehe: int, naht: dict,
    ) -> None:
        """Zeichnet Zielfeld und beide Messbalken einer Naht.

        Eine Naht **ohne** benannte Zielspanne bekommt kein Feld und keinen
        Balken, sondern einen Strich und den Hinweis in der Zahlenspalte —
        sie laesst sich nicht auf eine Skala legen, die es nicht gibt.
        """
        def x(t: float) -> float:
            return ((t - _ACHSE_MIN) / (_ACHSE_MAX - _ACHSE_MIN)) * breite

        if naht["ziel"] is None:
            cr.set_source_rgba(*_hex_to_rgba(_KARG_HEX, 0.35))
            cr.set_line_width(1.0)
            cr.move_to(0, hoehe / 2)
            cr.line_to(breite, hoehe / 2)
            cr.set_dash([3.0, 3.0])
            cr.stroke()
            cr.set_dash([])
            return

        # ── Das Zielfeld ────────────────────────
        cr.set_source_rgba(*_hex_to_rgba(_FELD_HEX, 1.0))
        cr.rectangle(x(0.0), 3, x(1.0) - x(0.0), hoehe - 6)
        cr.fill()
        cr.set_source_rgba(*_hex_to_rgba(_FELD_RAND_HEX, 1.0))
        cr.set_line_width(1.0)
        cr.rectangle(x(0.0), 3, x(1.0) - x(0.0), hoehe - 6)
        cr.stroke()

        # ── Die beiden Messbalken ───────────────
        self._balken(cr, x, naht, naht["gesamt"], y=9, dicke=3.0, blass=True)
        self._balken(cr, x, naht, naht["jung"], y=17, dicke=5.0, blass=False)

    def _balken(self, cr, x, naht: dict, teil: dict,
                y: float, dicke: float, blass: bool) -> None:
        """Ein Messbalken samt Endpunkten, in der Farbe seiner Lage."""
        if not teil["n"] or teil["min"] is None:
            return

        a: float = max(_ACHSE_MIN, _normiert(teil["min"], naht["ziel"]))
        b: float = min(_ACHSE_MAX, _normiert(teil["max"], naht["ziel"]))

        if teil["ueberschreitung"]:
            farbe, deckung = _UEBER_HEX, (0.55 if blass else 1.0)
        elif blass:
            farbe, deckung = _ALT_HEX, 0.55
        elif (teil["ausschoepfung"] or 0) < _KARG_GRENZE:
            farbe, deckung = _KARG_HEX, 1.0
        else:
            farbe, deckung = _JUNG_HEX, 1.0

        cr.set_source_rgba(*_hex_to_rgba(farbe, deckung))
        cr.rectangle(x(a), y, max(x(b) - x(a), 1.0), dicke)
        cr.fill()
        for rand in (a, b):
            cr.arc(x(rand), y + dicke / 2, dicke * 0.85, 0, 2 * 3.14159265)
            cr.fill()
