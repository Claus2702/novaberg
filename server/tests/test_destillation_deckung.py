"""Zeugen: Ein Beleg im Profil wird gegen das Material gehalten.

Ziel: Wer im Profil zitiert, hat es aus dem Material — und wer ein Zitat
*durchgehend* nennt, hat es dort mehr als einmal gefunden. Beides wird
beanstandet, wenn es nicht stimmt, und beides steht laut im Log.

`[gemessen]` — 06.09.2026, zwei Klassen am produktiven Bestand:

  * Die Anrede, die das Beziehungsprofil *durchgehend* nannte, steht in
    **1 von 20** Begegnungen des Prompt-Materials.
  * Zwei von zwanzig Laeufen zitierten Wendungen, die im Material **null**mal
    vorkommen.

**Die Pruefung sitzt an der Ausgabe, weil der Prompt gemessen nicht traegt.**
Vier Prompt-Fassungen bewegten bei n = 20 nichts ueber die Streuung
(`labor/2026-09-06_deckung_ergebnis.md`); die Entscheidung des Eigentuemers
lautet: ein Dauerwort wird beanstandet.

Zeugen dieser Datei:
  * **Beide Klassen einzeln**, dazu die beiden Faelle, die *nicht* anschlagen
    duerfen: ein mehrfach belegtes Zitat mit Dauerwort, und ein Einzelbeleg
    ohne Dauerwort. Ohne sie wuerde eine Pruefung, die immer meldet, gruen
    aussehen.
  * **Die Logzeile gehoert zum Zeugen.** Eine Beanstandung, die nur zaehlt und
    nichts sagt, ist im Betrieb nicht auffindbar (`22_STILLE_FEHLER`).
  * **Der Aufrufer wird mitgeprueft.** Eine gebaute und nie gerufene Pruefung
    ist der haeufigste Defekt dieses Bestandes — hier faehrt der Zeuge
    `_llm_call` mit ersetztem Modell und sieht die Zeile im Log.
  * **Alle Belege sind synthetisch.** Ein echtes Zitat aus dem Betrieb traegt
    nichts, was die Zahl nicht schon sagt (`32_VEROEFFENTLICHUNG` §1a).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.charakter.destillation import ZITAT, deckung_beanstanden

#: Der Pfad, unter dem das Modul importiert wird — Ziel jedes `patch`.
_MODUL: str = "agents.charakter.destillation"

#: **Der Logger heisst anders als das Modul.** Er haengt unter `ki_server`,
#: und `assertLogs` auf den Modulpfad faende nie eine Zeile — ein Zeuge, der
#: gruen waere, weil er am falschen Ort horcht. Vom eigenen Lauf gefunden.
_LOGGER: str = "ki_server.agents.charakter.destillation"

#: Ein Materialtext in der Form, die die Prompts erzeugen: Eintraege mit
#: Wortlaut in deutschen Anfuehrungszeichen.
MATERIAL: str = (
    "[Modus: fachlich]\n"
    "  der Nutzer: „Was passiert bei einem Kollaps, Kollege?“\n"
    "  Nova: „Dann faellt der Kern in Sekunden zusammen.“\n"
    "[Modus: fachlich]\n"
    "  der Nutzer: „Und die Huelle, Kollege?“\n"
    "  Nova: „Die wird abgesprengt.“\n"
)


class TestBelegOhneFundstelle(unittest.TestCase):
    """Erste Klasse: Das Profil zitiert, was im Material nicht steht."""

    def test_ein_erfundenes_zitat_wird_beanstandet(self) -> None:
        profil = "Er lacht viel („Hoho“) und fragt sachlich nach."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 1)

    def test_die_zeile_nennt_den_beleg(self) -> None:
        profil = "Er lacht viel („Hoho“) und fragt sachlich nach."
        with self.assertLogs(_LOGGER, level="WARNING") as log:
            deckung_beanstanden(MATERIAL, profil, "Profil")
        self.assertIn("Hoho", "\n".join(log.output))
        self.assertIn("ohne Fundstelle", "\n".join(log.output))

    def test_ein_belegtes_zitat_bleibt_unbeanstandet(self) -> None:
        profil = "Er fragt sachlich nach („Und die Huelle, Kollege?“)."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 0)


class TestEinzelbelegAlsDauerzug(unittest.TestCase):
    """Zweite Klasse: Ein Vorkommen, und das Profil sagt *durchgehend*."""

    def test_einmal_belegt_und_durchgehend_genannt(self) -> None:
        profil = "Er spricht ihn durchgehend als „Und die Huelle, Kollege?“ an."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 1)

    def test_die_zeile_nennt_das_vorkommen(self) -> None:
        profil = "Er spricht ihn durchgehend als „Und die Huelle, Kollege?“ an."
        with self.assertLogs(_LOGGER, level="WARNING") as log:
            deckung_beanstanden(MATERIAL, profil, "Profil")
        self.assertIn("Einzelbeleg", "\n".join(log.output))

    def test_mehrfach_belegt_darf_durchgehend_heissen(self) -> None:
        """Das Wort ist nicht verboten — es braucht Deckung."""
        profil = "Er nennt ihn durchgehend „Kollege“."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 0)

    def test_einzelbeleg_ohne_dauerwort_ist_keine_beanstandung(self) -> None:
        """Ein Beispiel, das als Beispiel dasteht, behauptet nichts."""
        profil = "Einmal fragte er „Und die Huelle, Kollege?“ nach."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 0)


class TestDasMessgeraetSelbst(unittest.TestCase):
    """Die Gegenprobe im eigenen Bauch."""

    def test_das_muster_findet_zitate(self) -> None:
        """Ein Muster ohne Treffer meldet 'keine Beanstandung' und ist blind."""
        self.assertEqual(len(ZITAT.findall(MATERIAL)), 4)

    def test_leere_eingaben_stuerzen_nicht_und_melden_nichts(self) -> None:
        self.assertEqual(deckung_beanstanden("", "irgendwas", "Profil"), 0)
        self.assertEqual(deckung_beanstanden(MATERIAL, "", "Profil"), 0)


class TestDerAufruferExistiert(unittest.TestCase):
    """Eine gebaute und nie gerufene Pruefung meldet nie etwas."""

    def test_llm_call_prueft_die_antwort(self) -> None:
        from agents.charakter import destillation as dest

        antwort = MagicMock()
        antwort.text = "Er lacht viel („Hoho“) und fragt sachlich nach."
        with patch(f"{_MODUL}.model_service") as dienst, \
             patch(f"{_MODUL}.get_node_config", return_value={}):
            dienst.background.submit_sync.return_value = antwort
            with self.assertLogs(_LOGGER, level="WARNING") as log:
                dest._llm_call(MATERIAL, "Profil (test)")
        self.assertIn("Hoho", "\n".join(log.output))


class TestFormatierungIstKeineErfindung(unittest.TestCase):
    """Derselbe Wortlaut in anderer Schreibung bleibt ein Beleg.

    `[gemessen]` 06.09.2026: Unter den unbelegten Belegen eines Messlaufs
    standen ein Zitat mit Auszeichnungs-Sternchen und eines mit einfachen
    Anfuehrungszeichen — beide im Material vorhanden, nur anders geschrieben.
    **Ein Falschalarm dieser Sorte ist teurer als eine verpasste Erfindung:**
    Er wuerde einen echten Beleg entwerten.
    """

    def test_sternchen_zaehlen_nicht(self) -> None:
        profil = "Er sagt *„Die wird abgesprengt.“* und meint es so."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 0)

    def test_einfache_anfuehrungszeichen_zaehlen_nicht(self) -> None:
        profil = "Er fragt „Und die Huelle, ‚Kollege‘?“ zurueck."
        # Der Beleg steht im Material ohne die inneren Zeichen — normalisiert
        # bleibt der Unterschied trotzdem bestehen, weil Zeichen entfernt und
        # nicht Woerter verglichen werden. Der Zeuge haelt die Grenze fest.
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 1)

    def test_grossschreibung_und_leerzeichen_zaehlen_nicht(self) -> None:
        profil = "Er sagt „DIE   WIRD  ABGESPRENGT.“ ganz nebenbei."
        self.assertEqual(deckung_beanstanden(MATERIAL, profil, "Profil"), 0)

    def test_die_normalisierung_veraendert_das_profil_nicht(self) -> None:
        """Sie ist eine Vergleichsform, kein Eingriff in den Text."""
        profil = "Er sagt *„Die wird abgesprengt.“*"
        vorher = profil
        deckung_beanstanden(MATERIAL, profil, "Profil")
        self.assertEqual(profil, vorher)


if __name__ == "__main__":
    unittest.main()
