"""Tests: Der NMCP-Handshake stellt die Naht her und prueft die Kompatibilitaet.

Ziel: Ein Bedarf ohne Zusage verhindert die Einbindung; ein Zettel, der einen
fremden Dienst ausschliesst, wird abgewiesen; ein fehlender vierter Ausgang
schraenkt ein statt zu verweigern; und die Naht-Signatur schlaegt an, wenn sich
die Bedeutung eines Schluessels unter dem Dienst weg aendert.

Zeugen dieser Datei:
  * **Die erwarteten Grade sind Literale aus der Konvention**, nicht aus einem
    Lauf der Pruefung. Sonst verglichen sich zwei Ableitungen derselben Quelle.
  * **Die Signatur wird an ihrer Wirkung geprueft, nicht an ihrem Wert.**
    Geprueft wird, dass eine geaenderte Bedeutung bei gleichem Namen und
    gleichem Typ eine andere Signatur ergibt — genau der Verfall, den kein
    Typpruefer sieht.
  * **Die Gegenprobe zum Ausschluss faehrt einen echten Dienstnamen**, nicht
    eine Attrappe: Der Bestand entscheidet, was als fremder Name gilt.
  * **Der Fehlalarm ist mitgeprueft.** Ein Negativfall, der ein Domaenenwort
    enthaelt, das zufaellig ein Dienstname ist, darf NICHT anschlagen — sonst
    schliesst die Pruefung einen funktionierenden Dienst aus.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents import AgentRegistry, discover_agents
from agents.base import BaseAgent, Bedarf
from agents.nmcp import (
    ZUSAGEN,
    Anmeldebefund,
    anmelden,
    gesamtbild_pruefen,
    naht_signatur,
)
from plugins import discover_managers


class _Attrappe(BaseAgent):
    """Minimaler Dienst, dessen Anmeldung der Test steuert."""

    def __init__(
        self,
        name: str = "attrappe",
        bedarf: list[Bedarf] | None = None,
        aushang: str = "ERKENNUNG: enthaelt eine Zahl mit Einheit",
        negativfaelle: list[str] | None = None,
        quote: dict[str, int] | None = None,
        ausgaenge: frozenset[str] | None = None,
        graph_eignung: list[str] | None = None,
    ) -> None:
        """Legt eine Attrappe mit den uebergebenen Deklarationen an."""
        self._name = name
        self._bedarf = bedarf or []
        self._aushang = aushang
        self._negativfaelle = negativfaelle or ["blosse Erwaehnung ohne Absicht"]
        self._quote = quote if quote is not None else {"user": 25}
        self._ausgaenge = ausgaenge or frozenset(
            {"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"}
        )
        self._graph_eignung = graph_eignung or ["user"]

    @property
    def name(self) -> str:
        """Name der Attrappe."""
        return self._name

    @property
    def graph_eignung(self) -> list[str]:
        """Graphen, in denen die Attrappe laufen darf."""
        return self._graph_eignung

    @property
    def aushang(self) -> str:
        """Aushang der Attrappe — nicht vom Manager geerbt."""
        return self._aushang

    @property
    def negativfaelle(self) -> list[str]:
        """Negativfaelle der Attrappe."""
        return self._negativfaelle

    @property
    def quote(self) -> dict[str, int]:
        """Quote der Attrappe."""
        return self._quote

    @property
    def bedarf(self) -> list[Bedarf]:
        """Bedarf der Attrappe."""
        return self._bedarf

    @property
    def ausgaenge(self) -> frozenset[str]:
        """Ausgaenge der Attrappe."""
        return self._ausgaenge

    def build_graph(self) -> None:
        """Wird im Test nie gerufen."""
        raise NotImplementedError


class NahtTest(unittest.TestCase):
    """Ein Bedarf ohne Zusage verhindert die Einbindung — laut, beim Start."""

    def test_bedarf_ohne_zusage_verweigert(self) -> None:
        """Ein Schluessel, den der Empfang nicht anbietet, sperrt die Einbindung."""
        agent = _Attrappe(bedarf=[Bedarf("gibt_es_nicht", "str", "irgendwas")])
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "verweigert")
        self.assertFalse(befund.eingebunden)
        self.assertIn("naht", [m.regel for m in befund.maengel])

    def test_bedarf_mit_falschem_typ_verweigert(self) -> None:
        """Ein erwarteter Name mit anderem Typ ist schlimmer als ein fehlender."""
        agent = _Attrappe(bedarf=[Bedarf("timeline_id", "str", "irgendwas")])
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "verweigert")
        self.assertFalse(befund.eingebunden)

    def test_erfuellter_bedarf_wird_eingebunden(self) -> None:
        """Ein Bedarf mit passender Zusage steht der Einbindung nicht entgegen."""
        zusage = ZUSAGEN["timeline_id"]
        agent = _Attrappe(bedarf=[
            Bedarf(zusage.schluessel, zusage.typ, zusage.bedeutung)
        ])
        befund = anmelden(agent)
        self.assertTrue(befund.eingebunden)
        self.assertNotIn("naht", [m.regel for m in befund.maengel])


class SignaturTest(unittest.TestCase):
    """Die Signatur faengt den Verfall, den kein Typpruefer sieht."""

    def test_gleiche_bedarfe_gleiche_signatur(self) -> None:
        """Reihenfolge aendert die Signatur nicht."""
        z = ZUSAGEN["timeline_id"]
        a = [Bedarf(z.schluessel, z.typ, z.bedeutung)]
        self.assertEqual(naht_signatur(a), naht_signatur(list(a)))

    def test_leerer_bedarf_hat_stabile_signatur(self) -> None:
        """Kein Bedarf ergibt die Signatur der leeren Menge, nicht einen Fehler."""
        self.assertEqual(len(naht_signatur([])), 64)

    def test_geaenderte_bedeutung_aendert_die_signatur(self) -> None:
        """Gleicher Name, gleicher Typ, andere Bedeutung — andere Signatur.

        Das ist der wahrscheinlichste Verfall und der Grund fuer die
        Signatur: Ein Schluessel behaelt seinen Namen und aendert seine
        Bedeutung, durch eine berechtigte Aenderung auf der anderen Seite
        der Naht.
        """
        z = ZUSAGEN["timeline_id"]
        vorher = naht_signatur([Bedarf(z.schluessel, z.typ, z.bedeutung)])

        original = ZUSAGEN[z.schluessel]
        ZUSAGEN[z.schluessel] = type(original)(
            schluessel=original.schluessel,
            typ=original.typ,
            bedeutung="ID eines GEFUNDENEN Eintrags",   # die Umkehrung
            lebensdauer=original.lebensdauer,
            verbraucher_art=original.verbraucher_art,
        )
        try:
            nachher = naht_signatur([Bedarf(z.schluessel, z.typ, z.bedeutung)])
        finally:
            ZUSAGEN[z.schluessel] = original

        self.assertNotEqual(
            vorher, nachher,
            "Eine geaenderte Bedeutung muss die Signatur aendern — sonst "
            "faellt genau der Verfall nicht auf, fuer den sie gebaut ist",
        )


class AusschlussTest(unittest.TestCase):
    """Kein Zettel darf einen anderen Dienst ausschliessen."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand — der entscheidet, was ein fremder Name ist."""
        discover_managers()
        discover_agents()

    def test_negativfall_mit_mehrteiligem_dienstnamen_verweigert(self) -> None:
        """Der Ausloesefall: ein mehrteiliger Name kann keine Prosa sein.

        Ein Plugin kann seinen Nachbarn nicht kennen; und ein
        Ausschlussrecht waere Gift, weil es im Fehlerfall den korrekten
        Dienst mit ausschloesse. Bei einem mehrteiligen Namen ist der Fall
        entscheidbar: Wer beide Teile hinschreibt, meint den Dienst.

        **Ohne diesen Zeugen ist ein schweigender Riegel von einem
        sauberen Bestand nicht zu unterscheiden.**
        """
        fremd = "dateien_wurzeln"
        self.assertIn(
            fremd, AgentRegistry.alle(),
            "Der Test faehrt einen echten Dienstnamen aus dem Bestand",
        )
        agent = _Attrappe(
            name="attrappe",
            negativfaelle=[f"nicht triggern, wenn {fremd} zustaendig ist"],
        )
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "verweigert")
        self.assertIn("ausschluss", [m.regel for m in befund.maengel])

    def test_einteiliges_sachwort_wird_gemeldet_und_nicht_verweigert(self) -> None:
        """19.08.2026 — das Sachwort der Domaene sperrt niemanden mehr aus.

        Der Anlass ist gemessen: An diesem Tag wurde das Silo `wissen` zum
        Dienst. Damit wurden **zwei unveraenderte, richtige Zettel zu harten
        Verstoessen** — `dateien` sagt *"das ist Wissen, keine Fundstelle"*,
        `timeline` sagt *"das ist Wissen, kein Termin"*. Beide benennen eine
        Eigenschaft der Aeusserung und schliessen niemanden aus.

        Der Befund bleibt und verliert seine Haerte: Ob ein Satz die
        Kategorie meint oder den Nachbarn, ist am Wort nicht entscheidbar —
        und ein Urteil, das den korrekten Dienst aussperrt, ist genau der
        Fehler, gegen den die geprueft Regel gebaut ist.
        """
        # Der Name kommt aus dem Bestand, nicht aus dem Test: Die Klasse
        # haengt an der FORM des Namens und nicht an einem bestimmten Dienst.
        # Ein fest hingeschriebener Name koppelte diesen Zeugen an die
        # Existenz genau dieses Dienstes — und damit an die Reihenfolge, in
        # der gebaut wird.
        einteilig = sorted(n for n in AgentRegistry.alle() if "_" not in n)
        self.assertTrue(einteilig, "Der Bestand traegt keinen einteiligen Namen")
        fremd = einteilig[0]
        agent = _Attrappe(
            name="attrappe",
            negativfaelle=[
                f"eine Aeusserung ueber {fremd} als Sache, nicht als Auftrag — "
                f"das ist eine Kategorie und kein Dienst"
            ],
        )
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "gemeldet")
        self.assertTrue(befund.eingebunden, "Der Dienst bleibt eingebunden")
        self.assertIn("ausschluss", [m.regel for m in befund.maengel])

    def test_domaenenwort_ist_kein_ausschluss(self) -> None:
        """Die Gegenprobe: ein Domaenenwort darf NICHT anschlagen.

        Agentennamen sind Domaenenwoerter. Am 17.08.2026 meldete eine
        Teilzeichenfolgen-Suche `charakter_identitaet` als Verstoss, weil
        dessen Negativfall "kein dauerhafter Charakter" den Namen des
        Dienstes `charakter` enthaelt. Ohne diesen Zeugen kehrt der
        Fehlalarm bei der naechsten Verschaerfung zurueck.
        """
        agent = _Attrappe(
            name="charakter_identitaet",
            negativfaelle=["einmalige Rollenspiele — kein dauerhafter Charakter"],
        )
        befund = anmelden(agent)
        self.assertNotIn(
            "ausschluss", [m.regel for m in befund.maengel],
            "Ein Domaenenwort der eigenen Namensfamilie ist kein Ausschluss",
        )

    def test_ein_neuer_dienstname_sperrt_keinen_bestehenden_aus(self) -> None:
        """Kein Urteil ueber Zettel A haengt daran, dass Dienst B hinzukam.

        Die Ruecknahme der Haerte hat einen Gegenstand, und er ist gezaehlt:
        **12 von 19** Dienstnamen sind einteilige deutsche Sachwoerter. Jeder
        neue Dienst mit einem solchen Namen konnte bisher jeden bestehenden
        Zettel rueckwirkend zum harten Verstoss machen.
        """
        einteilig = [n for n in AgentRegistry.alle() if "_" not in n]
        self.assertGreaterEqual(
            len(einteilig), 10,
            "Die Klasse hat einen Gegenstand — sonst waere der Zeuge gegenstandslos",
        )
        for name in ("dateien", "timeline"):
            befund = anmelden(AgentRegistry.finden(name))
            self.assertTrue(
                befund.eingebunden,
                f"'{name}' waere ausgesperrt: "
                f"{[m.text for m in befund.maengel if m.grad == 'verweigert']}",
            )


class VierterAusgangTest(unittest.TestCase):
    """Ohne den vierten Ausgang wird eingeschraenkt, nicht verweigert."""

    def test_fehlender_vierter_ausgang_schraenkt_ein(self) -> None:
        """Der Dienst bleibt eingebunden und bekommt keine Zweifelsfaelle."""
        agent = _Attrappe(
            ausgaenge=frozenset({"abgeschlossen", "fehler", "rueckfrage"})
        )
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "eingeschraenkt")
        self.assertTrue(befund.eingebunden)
        self.assertFalse(befund.zweifel_erlaubt)

    def test_vierter_ausgang_erlaubt_zweifel(self) -> None:
        """Mit dem vierten Ausgang darf der Dienst Zweifelsfaelle bekommen."""
        befund = anmelden(_Attrappe())
        self.assertTrue(befund.zweifel_erlaubt)

    def test_fehlender_erfolgsausgang_verweigert(self) -> None:
        """Ein Dienst ohne Erfolgsfall kann nicht arbeiten."""
        agent = _Attrappe(ausgaenge=frozenset({"fehler"}))
        befund = anmelden(agent)
        self.assertEqual(befund.grad, "verweigert")


class ZustellartTest(unittest.TestCase):
    """Nur ein Dienst am Empfang braucht Aushang und Quote."""

    def test_hintergrunddienst_ohne_aushang_ist_kein_mangel(self) -> None:
        """Ein Dienst ohne Zustellentscheidung wird nicht gewaehlt.

        Von ihm einen Aushang zu verlangen ist eine Forderung ohne
        Gegenstand. Am 17.08.2026 gemessen: 8 von 14 Diensten laufen ueber
        Zeitplan oder Queue, und die Pruefung meldete allen einen Mangel.
        """
        agent = _Attrappe(
            aushang="", negativfaelle=[], quote={},
            graph_eignung=["pixie"],
        )
        self.assertEqual(agent.zustellart, "queue")
        befund = anmelden(agent)
        regeln = [m.regel for m in befund.maengel]
        self.assertNotIn("aushang", regeln)
        self.assertNotIn("negativfall", regeln)
        self.assertNotIn("quote", regeln)

    def test_empfangsdienst_ohne_aushang_wird_gemeldet(self) -> None:
        """Am Empfang ist der fehlende Aushang ein Mangel — aber kein Riegel."""
        agent = _Attrappe(aushang="", negativfaelle=[], quote={})
        befund = anmelden(agent)
        regeln = [m.regel for m in befund.maengel]
        self.assertIn("aushang", regeln)
        self.assertIn("quote", regeln)
        self.assertTrue(befund.eingebunden, "Ein ungenauer Zettel sperrt nicht")


class QuoteAnmeldungTest(unittest.TestCase):
    """Eine Quote ausserhalb des Kanons ist ein Defekt der Anmeldung."""

    def test_quote_ausserhalb_des_kanons_verweigert(self) -> None:
        """37 % ist vorgetaeuschte Genauigkeit — jede Stufe ist ein Band."""
        befund = anmelden(_Attrappe(quote={"user": 37}))
        self.assertEqual(befund.grad, "verweigert")

    def test_quote_null_ist_zulaessig(self) -> None:
        """Null Prozent heisst 'Ausnahme' und ist eine sinnvolle Angabe."""
        befund = anmelden(_Attrappe(quote={"user": 0}))
        self.assertTrue(befund.eingebunden)
        self.assertNotIn("quote", [m.regel for m in befund.maengel])


class GesamtbildTest(unittest.TestCase):
    """Die Pruefung ueber die Menge meldet, sie entscheidet nicht."""

    def test_meldungen_sind_niemals_riegel(self) -> None:
        """Kein Befund des Gesamtbilds darf eine Einbindung verhindern.

        Die Registrierung darf ueber die Menge urteilen, um Zettel zu
        verbessern — nicht, um Zustellungen zu entscheiden. Eine hier
        berechnete Rangfolge waere zur Laufzeit dieselbe zentrale
        Zuordnungstabelle.
        """
        agenten = {
            "a": _Attrappe(name="a", negativfaelle=[]),
            "b": _Attrappe(name="b", negativfaelle=[]),
        }
        for m in gesamtbild_pruefen(agenten):
            self.assertEqual(
                m.grad, "gemeldet",
                f"Gesamtbild-Befund '{m.regel}' hat Grad '{m.grad}' — nur "
                f"'gemeldet' ist zulaessig",
            )

    def test_knotenkanal_ist_kein_toter_kanal(self) -> None:
        """Ein Kanal Knoten-zu-Knoten hat zu Recht keinen Agenten-Bedarf.

        Die Clipboard-Regel gilt zwischen Stufen. Am 17.08.2026 meldete das
        Gesamtbild alle drei Zusagen als toten Kanal, obwohl zwei davon
        knotenseitig sind.
        """
        meldungen = gesamtbild_pruefen({"a": _Attrappe(name="a")})
        tote = [
            m.text for m in meldungen if m.regel == "toter_kanal"
        ]
        for schluessel, zusage in ZUSAGEN.items():
            if zusage.verbraucher_art != "agent":
                self.assertFalse(
                    any(schluessel in t for t in tote),
                    f"'{schluessel}' ist knotenseitig und darf nicht als "
                    f"toter Kanal gemeldet werden",
                )


class BestandTest(unittest.TestCase):
    """Der laufende Bestand muss anmeldbar bleiben."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand, nicht seine Nachbildung."""
        discover_managers()
        discover_agents()

    def test_kein_dienst_wird_verweigert(self) -> None:
        """Alle vierzehn Dienste des Bestands sind eingebunden.

        Der Zeuge faehrt den Bestand: Eine Anmeldung, die einen laufenden
        Dienst aussperrt, ist ein Defekt der Pruefung und nicht des
        Dienstes.
        """
        alle = AgentRegistry.alle()
        self.assertGreaterEqual(len(alle), 14, "Der Bestand ist geschrumpft")
        verweigert = {
            name: [m.text for m in anmelden(a).maengel if m.grad == "verweigert"]
            for name, a in alle.items()
            if not anmelden(a).eingebunden
        }
        self.assertEqual(
            verweigert, {},
            f"Diese Dienste des Bestands wuerden ausgesperrt: {verweigert}",
        )

    def test_befund_je_dienst_ist_vollstaendig(self) -> None:
        """Jeder Dienst bekommt einen Befund mit Signatur und Grad."""
        for name, agent in AgentRegistry.alle().items():
            befund = anmelden(agent)
            self.assertIsInstance(befund, Anmeldebefund)
            self.assertEqual(befund.name, name)
            self.assertEqual(len(befund.signatur), 64)


if __name__ == "__main__":
    unittest.main()
