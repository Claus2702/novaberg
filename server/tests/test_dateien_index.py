"""Tests für den Wächter des Dateienindex (`agents/dateien_index/`).

Ziel: Der Index folgt dem Verzeichnis — neue Dateien kommen hinein,
geänderte werden aufgefrischt, verschwundene werden markiert statt gelöscht,
und was nicht indiziert wird, wird **mit Grund** übergangen statt
verschwiegen.

Die Zusicherungen, die hier geprüft werden:

  1. **Der Hash entscheidet, nicht die Zeit.** Eine Datei mit gleicher
     Größe und Zeit, aber anderem Inhalt gilt als geändert; eine Datei mit
     neuer Zeit und gleichem Inhalt nicht.
  2. **Jede gesehene Datei landet in genau einer Menge.** Indiziert oder mit
     Grund übergangen — es gibt keinen dritten Ausgang und kein Schweigen.
  3. **Verschwundene Zeilen bleiben stehen** und werden markiert.
  4. **Eine Erschließung ohne Thema schreibt keine Zeile.** Sonst behauptete
     der Index eine Erschließung, die nicht stattgefunden hat.
  5. **Jeder Pfad wird nach der Auflösung gegen die Wurzel gehalten.**
     `followlinks=False` sperrt nur den Abstieg in ein verlinktes
     Verzeichnis; eine verlinkte **Datei** käme sonst durch — gemessen am
     18.08.2026 von der zweiten Kontrolle, mit Größe, Zeilenzahl und
     Prüfsumme der fremden Datei.
  6. **Was die Obergrenze stehen lässt, steht in der Bilanz.**
  7. **Ein Verzeichnis mit führendem Punkt wird nicht betreten** — und das
     wird gesagt, nicht verschwiegen. Die Dateien darunter tauchen in keiner
     Menge auf, weil sie niemand gesehen hat; das Verzeichnis selbst steht
     mit Grund in der Bilanz.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.dateien_index import wandern as wandern_modul
from agents.dateien_index.indizieren import Erschliessung
from agents.dateien_index.wandern import (
    FALL_GEAENDERT,
    FALL_NEU,
    FALL_UNVERAENDERT,
    GRUND_AUSSERHALB,
    GRUND_GELOESCHT,
    GRUND_VERBORGENE_DATEI,
    GRUND_VERBORGENES_VERZEICHNIS,
    Fund,
    Wanderung,
    _hash_und_zeilen,
    wandern,
)
from config import DATEIEN_INDEX_MAX_BYTES


class _Zeit:
    """Eine Zeitangabe, die sich wie ein Datenbank-Zeitstempel verhält."""

    def __init__(self, wert: float) -> None:
        """Merkt sich den Unix-Zeitpunkt."""
        self._wert = wert

    def timestamp(self) -> float:
        """Liefert den Unix-Zeitpunkt, wie psycopg2 es täte."""
        return self._wert


def _hash_von(datei: Path) -> str:
    """Die Pruefsumme, die der Waechter fuer diese Datei bilden wuerde.

    **Bewusst dieselbe Funktion und keine nachgebaute**: Ein Zeuge, der den
    Hash selbst berechnet, prueft seine eigene Rechnung mit.
    """
    pruefsumme, _zeilen = _hash_und_zeilen(datei)
    return pruefsumme


def _altzeile_ohne_grund(pfad: str, hashwert: str) -> dict:
    """Eine stillgelegte Zeile aus der Zeit vor der Spalte `grund`.

    Sie laesst sich mit `_zeile` nicht bauen, und das ist Absicht: Dort
    haengen `aktiv` und `grund` aneinander, weil sie im Bestand
    zusammengehoeren. Diese Form gibt es nur, weil 145 Zeilen sie am
    23.08.2026 wirklich trugen — nicht als zulaessige Kombination.
    """
    zeile: dict = _zeile(pfad, 9, hashwert, 1000.0)
    zeile["aktiv"] = False
    return zeile


def _zeile(
    pfad: str, groesse: int, hashwert: str, mtime: float, zustand: str | None = None,
) -> dict:
    """Baut eine Indexzeile, wie `bestand_je_wurzel` sie liefert.

    `zustand` ist der `grund` einer stillgelegten Zeile oder None fuer eine
    aktive. Die beiden gehoeren zusammen — eine Zeile mit `grund` und
    `aktiv = True` gibt es im Bestand nicht mehr, seit sie stillgelegt
    wurde, und ein Zeuge sollte sie deshalb nicht herstellen koennen.
    """
    return {
        "id": abs(hash(pfad)) % 100000,
        "pfad": pfad,
        "groesse": groesse,
        "inhalt_hash": hashwert,
        "geaendert_am": _Zeit(mtime),
        "aktiv": zustand is None,
        "grund": zustand,
    }


class WanderungTest(unittest.TestCase):
    """Die drei Fälle, und keine Datei fällt zwischen sie."""

    def setUp(self) -> None:
        """Legt eine Wurzel mit drei Textdateien und einem Fremdformat an."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="index_"))
        (self.wurzel / "eins.md").write_text("# Eins\nInhalt A\n", encoding="utf-8")
        (self.wurzel / "zwei.md").write_text("# Zwei\nInhalt B\n", encoding="utf-8")
        (self.wurzel / "unter").mkdir()
        (self.wurzel / "unter" / "drei.txt").write_text("Inhalt C\n", encoding="utf-8")
        (self.wurzel / "bild.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 40)
        (self.wurzel / "leer.md").write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def test_leerer_bestand_macht_alles_neu(self) -> None:
        """Ohne Index ist jede lesbare Datei neu."""
        lauf: Wanderung = wandern(self.wurzel, {})
        self.assertEqual(lauf.zahlen()["neu"], 3)
        self.assertEqual(lauf.zahlen()["geaendert"], 0)
        self.assertEqual({f.fall for f in lauf.neu}, {FALL_NEU})

    def test_fremdformat_und_leere_datei_werden_mit_grund_uebergangen(self) -> None:
        """Übergangen ist nicht dasselbe wie nicht gesehen."""
        lauf: Wanderung = wandern(self.wurzel, {})
        gruende: dict[str, str] = dict(lauf.uebergangen)
        self.assertIn("bild.png", gruende)
        self.assertIn("leer.md", gruende)
        self.assertIn("kein Text", gruende["bild.png"])
        self.assertEqual(gruende["leer.md"], "leer")

    def test_jede_datei_landet_in_genau_einer_menge(self) -> None:
        """Es gibt keinen dritten Ausgang und kein Schweigen."""
        lauf: Wanderung = wandern(self.wurzel, {})
        zahlen: dict[str, int] = lauf.zahlen()
        summe: int = (
            zahlen["neu"] + zahlen["geaendert"]
            + zahlen["unveraendert"] + zahlen["uebergangen"]
        )
        auf_platte: int = sum(len(d) for _, _, d in os.walk(self.wurzel))
        self.assertEqual(summe, auf_platte)

    def test_gleicher_hash_bleibt_unveraendert(self) -> None:
        """Ein zweiter Lauf über einen unveränderten Bestand indiziert nichts."""
        erst: Wanderung = wandern(self.wurzel, {})
        bestand: dict[str, dict] = {
            f.pfad_relativ: _zeile(f.pfad_relativ, f.groesse, f.inhalt_hash, f.geaendert_am)
            for f in erst.neu
        }
        zweit: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual(zweit.zahlen()["neu"], 0)
        self.assertEqual(zweit.zahlen()["geaendert"], 0)
        self.assertEqual(zweit.zahlen()["unveraendert"], 3)

    def test_der_hash_entscheidet_nicht_die_zeit(self) -> None:
        """Gleiche Größe und Zeit, anderer Inhalt — das ist eine Änderung."""
        datei: Path = self.wurzel / "eins.md"
        alt = datei.stat()
        bestand = {"eins.md": _zeile("eins.md", alt.st_size, "einfremderhash", alt.st_mtime)}

        lauf: Wanderung = wandern(self.wurzel, bestand)

        geaendert = [f for f in lauf.geaendert if f.pfad_relativ == "eins.md"]
        self.assertEqual(len(geaendert), 1)
        self.assertEqual(geaendert[0].fall, FALL_GEAENDERT)

    def test_neue_zeit_bei_gleichem_inhalt_ist_keine_aenderung(self) -> None:
        """Ein Kopiervorgang ändert die Zeit, nicht den Inhalt."""
        erst: Wanderung = wandern(self.wurzel, {})
        vorher = {f.pfad_relativ: f for f in erst.neu}
        datei: Path = self.wurzel / "eins.md"
        os.utime(datei, (0, 0))

        bestand = {
            "eins.md": _zeile(
                "eins.md", vorher["eins.md"].groesse,
                vorher["eins.md"].inhalt_hash, vorher["eins.md"].geaendert_am,
            ),
        }
        lauf: Wanderung = wandern(self.wurzel, bestand)

        treffer = [f for f in lauf.unveraendert if f.pfad_relativ == "eins.md"]
        self.assertEqual(len(treffer), 1, "Der Hash muss die Zeit überstimmen")
        self.assertEqual(treffer[0].fall, FALL_UNVERAENDERT)

    def test_fehlende_datei_gilt_als_verschwunden(self) -> None:
        """Die Zeile bleibt und wird gemeldet, statt zu verschwinden."""
        bestand = {"weg.md": _zeile("weg.md", 12, "hash", 0.0)}
        lauf: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual(len(lauf.verschwunden), 1)
        self.assertEqual(lauf.verschwunden[0]["pfad"], "weg.md")

    def test_bereits_stillgelegte_zeile_wird_nicht_erneut_gemeldet(self) -> None:
        """Was schon als verschwunden markiert ist, meldet der Lauf nicht wieder."""
        bestand = {"weg.md": _zeile("weg.md", 12, "hash", 0.0, GRUND_GELOESCHT)}
        lauf: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual(lauf.verschwunden, [])

    def test_wiederaufgetauchte_datei_gilt_als_geaendert(self) -> None:
        """Eine stillgelegte Zeile mit vorhandener Datei muss wieder aufleben."""
        erst: Wanderung = wandern(self.wurzel, {})
        vorher = {f.pfad_relativ: f for f in erst.neu}["eins.md"]
        bestand = {
            "eins.md": _zeile(
                "eins.md", vorher.groesse, vorher.inhalt_hash,
                vorher.geaendert_am, GRUND_GELOESCHT,
            ),
        }
        lauf: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual([f.pfad_relativ for f in lauf.geaendert], ["eins.md"])

    def test_verknuepfung_nach_draussen_wird_nicht_verfolgt(self) -> None:
        """Sonst brächte ein Verweis Dateien in den Index, die nicht dort liegen."""
        draussen: Path = Path(tempfile.mkdtemp(prefix="index_aussen_"))
        try:
            (draussen / "fremd.md").write_text("# Fremd\n", encoding="utf-8")
            (self.wurzel / "verweis").symlink_to(draussen, target_is_directory=True)

            lauf: Wanderung = wandern(self.wurzel, {})

            pfade: set[str] = {f.pfad_relativ for f in lauf.neu}
            self.assertNotIn("verweis/fremd.md", pfade)
            self.assertEqual(len(lauf.neu), 3)
        finally:
            shutil.rmtree(draussen, ignore_errors=True)

    def test_verknuepfte_datei_nach_draussen_wird_uebergangen(self) -> None:
        """`followlinks=False` sperrt Verzeichnisse — eine verlinkte DATEI nicht."""
        draussen: Path = Path(tempfile.mkdtemp(prefix="index_aussen_"))
        try:
            fremd: Path = draussen / "fremd.md"
            fremd.write_text("# Fremd\nLiegt nicht im Baum.\n", encoding="utf-8")
            (self.wurzel / "zeiger.md").symlink_to(fremd)

            lauf: Wanderung = wandern(self.wurzel, {})

            pfade: set[str] = {f.pfad_relativ for f in lauf.neu}
            self.assertNotIn("zeiger.md", pfade, "Ein Zeiger nach draussen darf nicht hinein")
            gruende: dict[str, str] = dict(lauf.uebergangen)
            self.assertIn("zeiger.md", gruende)
            self.assertIn("aus der Wurzel heraus", gruende["zeiger.md"])
        finally:
            shutil.rmtree(draussen, ignore_errors=True)

    def test_verknuepfung_innerhalb_der_wurzel_bleibt_zulaessig(self) -> None:
        """Ein Zeiger, der drinnen bleibt, ist kein Randbruch."""
        (self.wurzel / "innen.md").symlink_to(self.wurzel / "eins.md")
        lauf: Wanderung = wandern(self.wurzel, {})
        pfade: set[str] = {f.pfad_relativ for f in lauf.neu}
        self.assertIn("innen.md", pfade)

    def test_zu_grosse_datei_wird_mit_zahl_uebergangen(self) -> None:
        """Der Grund nennt die Größe, nicht nur die Tatsache."""
        with patch.object(wandern_modul, "DATEIEN_INDEX_MAX_BYTES", 5):
            lauf: Wanderung = wandern(self.wurzel, {})
        gruende: dict[str, str] = dict(lauf.uebergangen)
        self.assertIn("eins.md", gruende)
        self.assertIn("ueber der Grenze", gruende["eins.md"])

    def test_wurzel_ohne_verzeichnis_liefert_leeren_lauf(self) -> None:
        """Ein fehlendes Verzeichnis ist ein Befund, kein Absturz."""
        lauf: Wanderung = wandern(self.wurzel / "gibtsnicht", {})
        self.assertEqual(lauf.zahlen(), {
            "neu": 0, "geaendert": 0, "unveraendert": 0,
            "verschwunden": 0, "ausserhalb": 0, "uebergangen": 0,
            "uebergangene_verzeichnisse": 0,
        })


class VerborgenesTest(unittest.TestCase):
    """Der führende Punkt — abgeschnitten, und mit Grund benannt.

    Eigene Wurzel statt Erweiterung der `WanderungTest`-Vorlage: Dort prüft
    ein Zeuge die Summe aller Mengen gegen `os.walk`, und ein nicht
    betretenes Verzeichnis bricht genau diese Gleichung — absichtlich. Beide
    Zusicherungen sind richtig, sie gelten nur nicht am selben Bestand.
    """

    def setUp(self) -> None:
        """Legt eine Wurzel mit sichtbarem und verborgenem Inhalt an."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="index_punkt_"))
        (self.wurzel / "sichtbar.md").write_text("# Sichtbar\nA\n", encoding="utf-8")
        (self.wurzel / "unter").mkdir()
        (self.wurzel / "unter" / "tief.md").write_text("# Tief\nB\n", encoding="utf-8")
        (self.wurzel / ".obsidian").mkdir()
        (self.wurzel / ".obsidian" / "notiz.md").write_text("# Werkzeug\nC\n", encoding="utf-8")
        (self.wurzel / ".obsidian" / "themes").mkdir()
        (self.wurzel / ".obsidian" / "themes" / "tief.md").write_text(
            "# Tiefer\nD\n", encoding="utf-8",
        )
        (self.wurzel / "unter" / ".cache").mkdir()
        (self.wurzel / "unter" / ".cache" / "rest.md").write_text("# Rest\nE\n", encoding="utf-8")
        (self.wurzel / ".geheim.md").write_text("# Geheim\nF\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _pfade(self, lauf: Wanderung) -> set[str]:
        """Alle Pfade, die der Lauf in eine der drei Mengen gelegt hat."""
        return {
            fund.pfad_relativ
            for fund in lauf.neu + lauf.geaendert + lauf.unveraendert
        }

    def test_sichtbares_wird_gefunden(self) -> None:
        """Die Gegenprobe zuerst: Das Abschneiden trifft nicht den Bestand."""
        lauf: Wanderung = wandern(self.wurzel, {})
        self.assertEqual(
            self._pfade(lauf), {"sichtbar.md", os.path.join("unter", "tief.md")},
        )

    def test_verborgenes_verzeichnis_wird_nicht_betreten(self) -> None:
        """Was unter dem Punkt liegt, taucht in KEINER Menge auf."""
        lauf: Wanderung = wandern(self.wurzel, {})
        alle: str = " ".join(
            self._pfade(lauf) | {pfad for pfad, _ in lauf.uebergangen},
        )
        self.assertNotIn(".obsidian", alle)
        self.assertNotIn("notiz.md", alle)
        self.assertNotIn(".cache", alle)

    def test_das_uebergangene_verzeichnis_steht_mit_grund_in_der_bilanz(self) -> None:
        """Nicht betreten heißt nicht verschwiegen — und zwar auf jeder Ebene."""
        lauf: Wanderung = wandern(self.wurzel, {})
        gruende: dict[str, str] = dict(lauf.uebergangene_verzeichnisse)
        self.assertEqual(
            set(gruende), {".obsidian", os.path.join("unter", ".cache")},
        )
        self.assertEqual(gruende[".obsidian"], GRUND_VERBORGENES_VERZEICHNIS)
        self.assertEqual(lauf.zahlen()["uebergangene_verzeichnisse"], 2)

    def test_der_ast_wird_einmal_gemeldet_nicht_je_datei(self) -> None:
        """Zwei Dateien unter `.obsidian`, eine Zeile in der Bilanz.

        Das ist der Unterschied zum Übergehen: Ohne das Abschneiden stünden
        `.obsidian` in jedem Lauf mit so vielen Zeilen da, wie es Dateien
        enthält — und keine davon würde je eine andere.
        """
        lauf: Wanderung = wandern(self.wurzel, {})
        obsidian: list[str] = [
            pfad for pfad, _ in lauf.uebergangene_verzeichnisse
            if pfad == ".obsidian"
        ]
        self.assertEqual(len(obsidian), 1)

    def test_verborgene_einzeldatei_wird_gesehen_und_begruendet(self) -> None:
        """Die Datei liegt sichtbar da — sie wird übergangen, nicht übersehen."""
        lauf: Wanderung = wandern(self.wurzel, {})
        gruende: dict[str, str] = dict(lauf.uebergangen)
        self.assertIn(".geheim.md", gruende)
        self.assertEqual(gruende[".geheim.md"], GRUND_VERBORGENE_DATEI)

    def test_altzeile_unter_dem_punkt_ist_ausserhalb_nicht_verschwunden(self) -> None:
        """Was vor der Regel indiziert wurde, ist nicht fort — nur draußen.

        **Dieser Zeuge hielt bis zum 23.08.2026 das Gegenteil fest** und
        sagte in seinem eigenen Text, dass `verschwunden` damit zwei
        Bedeutungen trägt. Genau das war der Defekt
        (VERSCHWUNDEN-DURCH-FILTERWECHSEL), und ein Zeuge, der ihn
        beschreibt statt ihn rot zu machen, hält ihn fest.

        Die Datei liegt unverändert da; `wo war das noch` darf für sie
        nicht mit `sie ist weg` beantwortet werden. Stillgelegt wird die
        Zeile trotzdem (§5.5) — mit `excluded` statt `deleted`.
        """
        pfad: str = os.path.join(".obsidian", "notiz.md")
        bestand: dict[str, dict] = {pfad: _zeile(pfad, 12, "gleichgueltig", 1000.0)}

        lauf: Wanderung = wandern(self.wurzel, bestand)

        self.assertEqual([z["pfad"] for z in lauf.ausserhalb], [pfad])
        self.assertEqual(lauf.verschwunden, [])
        # Die Gegenprobe an derselben Wurzel: Eine Zeile ohne Datei geht
        # weiterhin nach `verschwunden`. Ohne sie prüfte der Zeuge nur, dass
        # die Liste leer ist — und das wäre sie auch, wenn niemand mehr
        # etwas als fort erkennt.
        fort: str = "niemals-dagewesen.md"
        bestand[fort] = _zeile(fort, 12, "gleichgueltig", 1000.0)
        zweiter: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual([z["pfad"] for z in zweiter.verschwunden], [fort])
        self.assertEqual([z["pfad"] for z in zweiter.ausserhalb], [pfad])

    def test_der_punkt_schlaegt_die_endung_als_grund(self) -> None:
        """`.DS_Store` ist nicht wegen seines Formats draußen.

        Beide Regeln träfen zu; die Auskunft soll die genauere sein.
        """
        (self.wurzel / ".DS_Store").write_bytes(b"\x00\x01\x02")
        lauf: Wanderung = wandern(self.wurzel, {})
        gruende: dict[str, str] = dict(lauf.uebergangen)
        self.assertEqual(gruende[".DS_Store"], GRUND_VERBORGENE_DATEI)
        self.assertNotIn("Endung", gruende[".DS_Store"])


class BilanzGehtAufTest(unittest.TestCase):
    """Eine Datei, die am Modell scheitert, steht in der Bilanz — mit Pfad.

    Der Defekt, gegen den dieser Zeuge steht: `erschliessen` gibt bei
    unbrauchbarer Modellantwort ein leeres Ergebnis zurück, der Lauf
    verbrauchte dafür sein Budget, schrieb keine Zeile und meldete nichts.
    `fehler` sammelt nur Ausnahmen je **Wurzel**; ein Fehlschlag je Datei
    hatte dort kein Fach. Sichtbar war der Verlust allein daran, dass die
    Zahlen sich nicht zur Zahl der Kandidaten addieren — und genau diese
    Identität prüft der Zeuge.
    """

    def setUp(self) -> None:
        """Zwei Textdateien, von denen eine am Modell scheitern wird."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="index_bilanz_"))
        (self.wurzel / "geht.md").write_text("# Geht\nA\n", encoding="utf-8")
        (self.wurzel / "scheitert.md").write_text("# Scheitert\nB\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def test_gescheiterte_datei_steht_mit_pfad_in_der_bilanz(self) -> None:
        """Der Fehlschlag bekommt ein Fach, und die Rechnung geht auf."""
        from agents.dateien_index import agent as agent_modul
        from agents.dateien_index.agent import DateienIndexAgent
        from agents.dateien_index.indizieren import Erschliessung
        from agents.dateien_wurzeln.aussenrand import WurzelBefund

        def _erschliessen(pfad: Path, basis: Path, relativ: str) -> Erschliessung:
            """Die eine Datei gelingt, die andere liefert ein leeres Ergebnis."""
            if relativ == "scheitert.md":
                return Erschliessung("", "", [], [], None)
            return Erschliessung("Thema", "Fasst zusammen", ["a"], [], [0.1] * 768)

        befund = WurzelBefund(
            ok=True, aufgeloest=self.wurzel, dateizahl=2,
            gezaehlt_vollstaendig=True, rand=str(self.wurzel), grund="",
        )

        with (
            patch.object(agent_modul, "wurzel_pruefen", return_value=befund),
            patch.object(agent_modul, "bestand_je_wurzel", return_value={}),
            patch.object(agent_modul, "erschliessen", side_effect=_erschliessen),
            patch.object(agent_modul, "zeile_schreiben", return_value=1),
            patch.object(agent_modul, "suchtext_bauen", return_value="such"),
            patch.object(agent_modul, "stilllegen", return_value=None),
        ):
            teil, _budget = DateienIndexAgent()._wurzel_bearbeiten(
                {"id": 7, "pfad": str(self.wurzel)}, 50,
            )

        self.assertEqual(teil["indiziert"], 1)
        self.assertEqual(teil["gescheitert"], 1)
        self.assertEqual(
            teil["gescheitert_gruende"][0]["pfad"], "scheitert.md",
        )
        # Die Identität, an der der Verlust sichtbar wird.
        self.assertEqual(
            teil["neu"], teil["indiziert"] + teil["offen"] + teil["gescheitert"],
        )


class EmbedTextTest(unittest.TestCase):
    """`F-EMBED-1`: eine benannte Stelle, rekonstruierbar aus dem Bestand."""

    def test_text_besteht_nur_aus_persistierten_feldern(self) -> None:
        """Thema und Stichwörter stehen als eigene Spalten — sonst nichts."""
        from agents.dateien_index.indizieren import embed_text_bauen
        text: str = embed_text_bauen("Der Außenrand begrenzt Freigaben", ["Rand", "Pfad"])
        self.assertIn("Der Außenrand begrenzt Freigaben", text)
        self.assertIn("Rand", text)
        self.assertIn("Pfad", text)

    def test_leeres_thema_scheitert_laut(self) -> None:
        """Ein Vektor über nichts wäre eine Ähnlichkeit, die keine ist."""
        from agents.dateien_index.indizieren import embed_text_bauen
        with self.assertRaises(ValueError):
            embed_text_bauen("   ", ["Rand"])

    def test_es_gibt_genau_eine_stelle_die_den_text_baut(self) -> None:
        """Live-Pfad und späteres Wartungswerkzeug dürfen nicht auseinanderlaufen."""
        verbund: Path = Path(__file__).resolve().parents[1] / "agents" / "dateien_index"
        quelltexte: dict[str, str] = {
            modul.name: modul.read_text(encoding="utf-8")
            for modul in sorted(verbund.glob("*.py"))
        }
        alle: str = "".join(quelltexte.values())

        self.assertEqual(
            alle.count("def embed_text_bauen"), 1,
            "Zwei Definitionen wären zwei Einbettungsräume",
        )
        # Der Einbettungsaufruf geht ausschließlich über die benannte Stelle.
        self.assertEqual(alle.count("_embedding_holen("), 2)
        self.assertIn("_embedding_holen(\n        embed_text_bauen(", alle)


class SchreibpfadTest(unittest.TestCase):
    """Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden."""

    def test_kein_modul_des_waechters_importiert_einen_schreiber(self) -> None:
        """Der Wächter liest Dateien und schreibt ausschließlich Zeilen."""
        verbund: Path = Path(__file__).resolve().parents[1] / "agents" / "dateien_index"
        verboten: tuple[str, ...] = (
            "datei_schreiben", "block_ersetzen", "block_anfuegen",
            "block_einfuegen", "str_replace_in_block", "write_text",
            "write_bytes", "shutil", "os.remove", "rmtree", "unlink",
        )
        treffer: list[str] = []
        for modul in sorted(verbund.glob("*.py")):
            text: str = modul.read_text(encoding="utf-8")
            treffer += [f"{modul.name}: {name}" for name in verboten if name in text]
        self.assertEqual(treffer, [], f"Schreibpfad im Waechter: {treffer}")


class AnmeldungTest(unittest.TestCase):
    """Ein Dienst am Zeitplan braucht keinen Aushang — aber eine Lastart."""

    def setUp(self) -> None:
        """Holt den Agenten."""
        from agents.dateien_index.agent import DateienIndexAgent
        self.agent = DateienIndexAgent()

    def test_zustellart_ist_kein_empfang(self) -> None:
        """Er wird nicht gewählt, also braucht er keinen Zettel am Brett."""
        self.assertNotEqual(self.agent.zustellart, "empfang")

    def test_lastart_ist_die_langsame_spur(self) -> None:
        """Wandern ist Rechnung, Thema und Stichwörter sind ein Modellaufruf."""
        self.assertEqual(self.agent.lastart, "llm")

    def test_kein_takt_solange_die_rate_ungemessen_ist(self) -> None:
        """Ein geratener Takt wäre dasselbe wie eine geratene Schwelle."""
        self.assertIsNone(self.agent.periodic_task())

    def test_nur_hintergrund(self) -> None:
        """Ein Wartungslauf gehört nicht in den Gesprächsgraphen."""
        self.assertEqual(self.agent.graph_eignung, ["pixie"])

    def test_grenze_nennt_den_fehlenden_schreibpfad(self) -> None:
        """Was der Dienst nicht tut, gehört in seine Anmeldung."""
        self.assertTrue(any("loescht keine" in g for g in self.agent.grenze))


class ErkennerDeckungTest(unittest.TestCase):
    """Jede Endung, die der Index annimmt, hat einen Gliederungs-Erkenner.

    Der Zeuge stammt aus der zweiten Kontrolle vom 20.08.2026 und prüft ein
    **Kriterium statt einer Aufzählung**: Die beiden Mengen leben in zwei
    Modulen, die einander nicht kennen — `config.DATEIEN_INDEX_ENDUNGEN`
    sagt, was indiziert wird, `operationen._ERKENNER` sagt, was gelesen
    werden kann. Wer die erste erweitert und die zweite vergisst, bekommt
    keine falsche Karte mehr, sondern einen Fehler beim Indizieren — aber
    erst im Betrieb und für jede Datei dieser Endung.
    """

    def test_jede_zugelassene_endung_hat_einen_erkenner(self) -> None:
        """Die Menge der Endungen ist in der Menge der Erkenner enthalten."""
        from config import DATEIEN_INDEX_ENDUNGEN
        from tools.dateien.operationen import _ERKENNER

        ohne: set[str] = set(DATEIEN_INDEX_ENDUNGEN) - set(_ERKENNER)
        self.assertEqual(
            ohne, set(),
            f"Der Index nimmt {sorted(ohne)} an, ohne die Gliederung lesen zu "
            f"können — jede solche Datei wirft beim Indizieren",
        )


class AusserhalbTest(unittest.TestCase):
    """Fuenf Klassen vorhandener Dateien, die der Lauf nicht bewertet.

    Der Eintrag `VERSCHWUNDEN-DURCH-FILTERWECHSEL` nannte eine — den nicht
    betretenen Punkt-Ast. Am 23.08.2026 gegen den Code gemessen waren es
    **fuenf**: Jede Datei lag vor dem Lauf auf der Platte, jede stand im
    Bestand, und alle fuenf meldete der Waechter als `verschwunden`.

    Die Klassen stehen hier einzeln und nicht als eine Schleife ueber eine
    Liste: Ein Zeuge, der fuenf Faelle in einer Zusicherung buendelt, wird
    von jedem einzelnen rot und sagt nicht, von welchem.
    """

    def setUp(self) -> None:
        """Legt fuer jede Klasse eine Datei an, die wirklich da ist."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="index_ausserhalb_"))
        (self.wurzel / ".obsidian").mkdir()
        (self.wurzel / ".obsidian" / "notiz.md").write_text("# A\n", encoding="utf-8")
        (self.wurzel / "bild.png").write_text("kein Text\n", encoding="utf-8")
        (self.wurzel / "gross.md").write_text(
            "x" * (DATEIEN_INDEX_MAX_BYTES + 1), encoding="utf-8",
        )
        (self.wurzel / "leer.md").write_text("", encoding="utf-8")
        (self.wurzel / ".geheim.md").write_text("# F\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Raeumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _lauf_mit(self, relativ: str) -> Wanderung:
        """Laesst den Waechter ueber eine Wurzel laufen, in der `relativ` steht."""
        return wandern(self.wurzel, {relativ: _zeile(relativ, 9, "alt", 1000.0)})

    def _ausserhalb(self, relativ: str) -> None:
        """Die Zusicherung, die alle fuenf Klassen teilen."""
        self.assertTrue(
            (self.wurzel / relativ).exists(),
            "Vorbedingung des Zeugen: Die Datei muss wirklich da liegen",
        )
        lauf: Wanderung = self._lauf_mit(relativ)
        self.assertEqual([z["pfad"] for z in lauf.ausserhalb], [relativ])
        self.assertEqual(lauf.verschwunden, [])

    def test_unter_punkt_verzeichnis_ist_ausserhalb(self) -> None:
        """Der Ast wurde nicht betreten — das ist keine Auskunft ueber die Datei."""
        self._ausserhalb(os.path.join(".obsidian", "notiz.md"))

    def test_fremde_endung_ist_ausserhalb(self) -> None:
        """Eine engere Endungsliste loescht nichts."""
        self._ausserhalb("bild.png")

    def test_ueber_der_groesse_ist_ausserhalb(self) -> None:
        """Eine gesenkte Groessengrenze loescht nichts.

        Der Fall ist nicht theoretisch: Am 23.08.2026 lag die groesste
        indizierte Datei bei 555 536 Bytes und waechst mit jedem Eintrag.
        """
        self._ausserhalb("gross.md")

    def test_leere_datei_ist_ausserhalb(self) -> None:
        """Eine leergeraeumte Datei ist nicht dieselbe wie eine geloeschte."""
        self._ausserhalb("leer.md")

    def test_verborgene_einzeldatei_ist_ausserhalb(self) -> None:
        """Gesehen und mit Grund uebergangen — aber vorhanden."""
        self._ausserhalb(".geheim.md")

    def test_wirklich_fehlende_datei_bleibt_verschwunden(self) -> None:
        """Die Gegenprobe: Der Umbau nimmt dem Waechter nicht das Erkennen.

        Ohne sie pruefte die Reihe oben nur, dass `verschwunden` leer bleibt
        — was auch dann zutraefe, wenn niemand mehr eine fehlende Datei
        bemerkt.
        """
        lauf: Wanderung = self._lauf_mit("fort.md")
        self.assertEqual([z["pfad"] for z in lauf.verschwunden], ["fort.md"])
        self.assertEqual(lauf.ausserhalb, [])

    def test_stillgelegte_zeile_wird_nicht_erneut_gemeldet(self) -> None:
        """Was schon stillgelegt ist, taucht in keiner der beiden Mengen auf."""
        bestand: dict[str, dict] = {
            "bild.png": _zeile("bild.png", 9, "alt", 1000.0, GRUND_AUSSERHALB),
            "fort.md": _zeile("fort.md", 9, "alt", 1000.0, GRUND_GELOESCHT),
        }
        lauf: Wanderung = wandern(self.wurzel, bestand)
        self.assertEqual(lauf.ausserhalb, [])
        self.assertEqual(lauf.verschwunden, [])


class KetteTest(unittest.TestCase):
    """Der Wiedereintritt: Setzt die neue Datei die alte fort oder nicht.

    Die Frage ist nicht kosmetisch. `zeile_schreiben` raeumt bei `created`
    die Spalten, die der alten Datei gehoerten (`entitaet_ids`,
    `timeline_id`, `zuletzt_gelernt_hash`), und laesst sie bei `changed`
    stehen. Wer den Fall falsch bestimmt, vererbt die Beziehungen einer
    geloeschten Datei an eine fremde — still, weil niemand danach sucht.
    """

    def setUp(self) -> None:
        """Eine Wurzel mit genau einer Datei."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="index_kette_"))
        (self.wurzel / "x.md").write_text("# Neu\nInhalt\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Raeumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _fall(self, bestand: dict[str, dict]) -> str:
        """Der Fall, den der Lauf fuer `x.md` vergibt."""
        lauf: Wanderung = wandern(self.wurzel, bestand)
        alle = {f.pfad_relativ: f.fall
                for f in lauf.neu + lauf.geaendert + lauf.unveraendert}
        return alle["x.md"]

    def test_grabstein_mit_anderem_hash_ist_neuanlage(self) -> None:
        """Geloescht, dann ein anderes x — der Zyklus beginnt von vorn."""
        self.assertEqual(
            self._fall({"x.md": _zeile("x.md", 9, "hash-der-alten", 1000.0, GRUND_GELOESCHT)}),
            FALL_NEU,
        )

    def test_grabstein_mit_gleichem_hash_ist_fortsetzung(self) -> None:
        """Dieselbe Datei kam zurueck — sie ist dieselbe."""
        hashwert: str = _hash_von(self.wurzel / "x.md")
        self.assertEqual(
            self._fall({"x.md": _zeile("x.md", 9, hashwert, 1000.0, GRUND_GELOESCHT)}),
            FALL_GEAENDERT,
        )

    def test_ausgeschlossene_zeile_setzt_fort_auch_bei_anderem_hash(self) -> None:
        """Ein zurueckgenommener Filter loescht nichts und erbt alles.

        Der Unterschied zum Grabstein ist der ganze Grund fuer die Spalte:
        Wir haben nie gesehen, dass diese Datei fort war — sie lag die
        ganze Zeit da, wir sahen nur nicht hin.
        """
        self.assertEqual(
            self._fall({"x.md": _zeile("x.md", 9, "hash-von-vorher", 1000.0, GRUND_AUSSERHALB)}),
            FALL_GEAENDERT,
        )

    def test_zeile_ohne_grund_setzt_fort(self) -> None:
        """Bestandszeilen von vor der Spalte werden nicht zu Neuanlagen.

        174 Zeilen tragen am 23.08.2026 `grund IS NULL`. Sie als Neuanlage
        zu behandeln hiesse, ihnen eine Geschichte abzusprechen, ueber die
        wir nichts wissen.
        """
        self.assertEqual(
            self._fall({"x.md": _altzeile_ohne_grund("x.md", "alt")}),
            FALL_GEAENDERT,
        )


class SchreibfallTest(unittest.TestCase):
    """`zeile_schreiben` nimmt nur die zwei Faelle, die es buchen kann.

    Der erste Entwurf hatte hier `GRUND_JE_FALL.get(fall, GRUND_GEAENDERT)`
    — einen stillen Ersatzwert. Ein `unveraendert`, das hierher gelangt,
    waere damit als **Aenderung** in die Datenbank gegangen, samt Datum:
    eine Messung, die niemand vorgenommen hat. **Gefunden nicht vom Bau,
    sondern von einer Nachpruefung quer dazu** (23.08.2026): Der Bau ging
    entlang der neuen Faelle, der stille Ersatzwert lag daneben.
    """

    def test_unveraendert_wird_nicht_als_aenderung_gebucht(self) -> None:
        """Der Fall wird abgewiesen, laut, und ohne Zeile."""
        from agents.dateien_index import speicher as speicher_modul

        fund = Fund(
            pfad_relativ="x.md", pfad_absolut=Path(tempfile.gettempdir()) / "x.md", name="x.md",
            groesse=9, zeilen=1, inhalt_hash="h", geaendert_am=1000.0,
            fall=FALL_UNVERAENDERT,
        )
        erschliessung = Erschliessung(
            thema="Ein Thema", zusammenfassung="", stichwoerter=[],
            embedding=None, struktur=None,
        )

        with (
            patch.object(speicher_modul.db_manager, "execute_returning") as schreiben,
            self.assertLogs("ki_server.agents.dateien_index.speicher", "ERROR") as log,
        ):
            ergebnis = speicher_modul.zeile_schreiben(1, fund, erschliessung, "such")

        self.assertIsNone(ergebnis)
        schreiben.assert_not_called()
        self.assertIn("unveraendert", " ".join(log.output))

    def test_die_beiden_gueltigen_faelle_kommen_durch(self) -> None:
        """Die Gegenprobe: Der Riegel sperrt nicht, was er durchlassen soll."""
        from agents.dateien_index import speicher as speicher_modul

        erschliessung = Erschliessung(
            thema="Ein Thema", zusammenfassung="", stichwoerter=[],
            embedding=None, struktur=None,
        )
        for fall, erwartet in ((FALL_NEU, "created"), (FALL_GEAENDERT, "changed")):
            with self.subTest(fall=fall):
                fund = Fund(
                    pfad_relativ="x.md", pfad_absolut=Path(tempfile.gettempdir()) / "x.md",
                    name="x.md", groesse=9, zeilen=1, inhalt_hash="h",
                    geaendert_am=1000.0, fall=fall,
                )
                with patch.object(
                    speicher_modul.db_manager, "execute_returning",
                    return_value={"id": 5},
                ) as schreiben:
                    self.assertEqual(
                        speicher_modul.zeile_schreiben(1, fund, erschliessung, "such"), 5,
                    )
                # Der geschriebene Grund steht im Parametertupel, nicht im SQL.
                self.assertIn(erwartet, schreiben.call_args[0][1])


if __name__ == "__main__":
    unittest.main()
