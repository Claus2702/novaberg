"""Laden der Bildebenen des Avatars — die einzige Stelle, die eine Datei öffnet.

Neun PNG in einem Verzeichnis, je drei Fassungen derselben Zeichnung, zwischen
denen das Bild im Takt der Strichlage wechselt:

- `base<i>.png` — das Grundbild;
- `neck<i>.png` — die Halsebene: das Grundbild, unter dem Kinn mit Hals aufgefüllt;
  sie bleibt fest, wenn sich der Kiefer bewegt;
- `face<i>.png` — die Gesichtsebene: das Grundbild mit Alphakanal, unter der
  Kinnlinie durchsichtig; nur sie wird mit dem Kiefer verzerrt.

Alle Bilder sind `LAYER_SIZE` × `LAYER_SIZE` Pixel. Fehlt das Verzeichnis oder ein
Bild, ist eines kein lesbares PNG, hat es eine andere Größe oder fehlt der
Gesichtsebene der Alphakanal, wirft `load_layers` einen `LayerError` mit dem
Pfad — nie ein leeres oder halbes Gesicht.

Cairo wird erst beim Lesen geladen (`CairoPngSource.read`), GTK gar nicht: Das
Modul lädt und prüft sich ohne pycairo, mit einer Quelle, die Flächen nachbildet.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

LAYER_SIZE = 900  # Kantenlänge jeder Ebene in Pixeln
LAYER_VARIANTS = 3  # Fassungen je Ebene, gewechselt im Takt der Strichlage
LAYER_KINDS = ("base", "neck", "face")
# Wert von `cairo.FORMAT_ARGB32` (Enum `cairo.Format.ARGB32`), als Zahl, damit das
# Modul ohne pycairo lädt; ein PNG ohne Alphakanal liest Cairo als RGB24 (1).
FORMAT_ARGB32 = 0


class LayerError(RuntimeError):
    """Eine Bildebene fehlt oder taugt nicht; die Meldung nennt den Pfad."""


class PngSource(Protocol):
    """Zugriff auf das Dateisystem und das Lesen eines PNG als Cairo-Fläche."""

    def is_dir(self, path: Path) -> bool:
        """Wahr, wenn `path` ein Verzeichnis ist."""
        ...

    def is_file(self, path: Path) -> bool:
        """Wahr, wenn `path` eine Datei ist."""
        ...

    def read(self, path: Path) -> object:
        """Die Fläche des PNG unter `path`; wirft `LayerError`, wenn es keines ist."""
        ...


class CairoPngSource:
    """Die echte Quelle: Dateisystem über `pathlib`, PNG über Cairo."""

    def is_dir(self, path: Path) -> bool:
        """Wahr, wenn `path` ein Verzeichnis ist."""
        return path.is_dir()

    def is_file(self, path: Path) -> bool:
        """Wahr, wenn `path` eine Datei ist."""
        return path.is_file()

    def read(self, path: Path) -> object:
        """Liest das PNG unter `path` als `cairo.ImageSurface`.

        Vorbedingung: `path` ist eine Datei.
        Nachbedingung: eine Fläche mit Breite und Höhe größer null.
        Fehlerfälle: LayerError mit Pfad, wenn Cairo die Datei nicht als PNG liest;
        ImportError ohne pycairo.
        """
        # ── Eingabe-Validierung ──
        if not path.is_file():
            raise LayerError(f"read: {path} ist keine Datei")

        # ── Verarbeitung ──
        import cairo  # erst hier, damit das Modul ohne pycairo lädt

        try:
            surface = cairo.ImageSurface.create_from_png(str(path))
        except (cairo.Error, OSError, MemoryError) as exc:
            raise LayerError(f"read: {path} ist kein lesbares PNG: {exc}") from exc

        # ── Ausgabe-Verifikation ──
        if surface.get_width() <= 0 or surface.get_height() <= 0:
            raise LayerError(f"read: {path} ergibt eine leere Fläche")
        return surface


@dataclass(frozen=True)
class AvatarLayers:
    """Die neun Ebenen als Flächen, je Art ein Tupel der `LAYER_VARIANTS` Fassungen."""

    base: tuple[object, ...]
    neck: tuple[object, ...]
    face: tuple[object, ...]


def load_layers(directory: Path, source: PngSource | None = None) -> AvatarLayers:
    """Lädt `base0..2`, `neck0..2` und `face0..2` aus `directory`.

    `source` ersetzt Dateisystem und Cairo (Zeugen); ohne Angabe gilt `CairoPngSource`.
    Vorbedingung: `directory` ist ein `Path`.
    Nachbedingung: drei Fassungen je Art, jede `LAYER_SIZE` × `LAYER_SIZE` Pixel, die
    Gesichtsebenen mit Alphakanal.
    Fehlerfälle: LayerError mit Pfad, wenn das Verzeichnis oder ein Bild fehlt, ein Bild
    kein PNG ist, eine andere Größe hat oder einer Gesichtsebene der Alphakanal fehlt;
    ValueError, wenn `directory` kein `Path` ist.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(directory, Path):
        raise ValueError(f"load_layers: Verzeichnis {directory!r} ist kein Path")
    files = CairoPngSource() if source is None else source
    if not files.is_dir(directory):
        raise LayerError(f"load_layers: Verzeichnis {directory} fehlt")

    # ── Verarbeitung ──
    loaded: dict[str, tuple[object, ...]] = {}
    for kind in LAYER_KINDS:
        surfaces = []
        for variant in range(LAYER_VARIANTS):
            path = directory / f"{kind}{variant}.png"
            surfaces.append(_load_one(files, path, needs_alpha=kind == "face"))
        loaded[kind] = tuple(surfaces)

    # ── Ausgabe-Verifikation ──
    layers = AvatarLayers(base=loaded["base"], neck=loaded["neck"], face=loaded["face"])
    if any(len(getattr(layers, kind)) != LAYER_VARIANTS for kind in LAYER_KINDS):
        raise RuntimeError("load_layers: nicht jede Art hat alle Fassungen")
    return layers


def _load_one(files: PngSource, path: Path, needs_alpha: bool) -> object:
    """Eine Ebene: Datei vorhanden, als PNG gelesen, Größe und Alphakanal geprüft.

    Vorbedingung: `path` liegt im geprüften Verzeichnis.
    Nachbedingung: eine Fläche von `LAYER_SIZE` × `LAYER_SIZE` Pixeln, bei
    `needs_alpha` im Format ARGB32.
    Fehlerfälle: LayerError mit Pfad bei fehlender Datei, falscher Größe, fehlendem Alpha.
    """
    # ── Eingabe-Validierung ──
    if not files.is_file(path):
        raise LayerError(f"load_layers: Bild {path} fehlt")

    # ── Verarbeitung ──
    surface = files.read(path)
    width, height = surface.get_width(), surface.get_height()

    # ── Ausgabe-Verifikation ──
    if (width, height) != (LAYER_SIZE, LAYER_SIZE):
        raise LayerError(
            f"load_layers: Bild {path} ist {width} × {height}, erwartet "
            f"{LAYER_SIZE} × {LAYER_SIZE}"
        )
    if needs_alpha and surface.get_format() != FORMAT_ARGB32:
        raise LayerError(f"load_layers: Gesichtsebene {path} ohne Alphakanal")
    return surface
