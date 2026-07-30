"""Tests: Der Eingangsknoten des CharacterGraphs befuellt external und internal.

Ziel: Das heutige Verhalten von `db_zugriff` ist festgeschrieben, bevor die
Funktion zerlegt wird. Diese Datei ist ein **Charakterisierungs-Netz**: Sie
behauptet nicht, dass das Verhalten richtig ist, sondern dass es sich durch die
Zerlegung nicht aendert.

Hintergrund: Die Funktion hat 333 Zeilen und elf Verzweigungen, und sie hatte
**keinen einzigen Test**. Drei Dateien nannten `db_zugriff` in ihren Docstrings
und bauten State-Objekte "so, wie db_zugriff sie bauen wuerde" — sie riefen den
Knoten aber nie auf. Ein Grep nach dem Namen sieht wie Abdeckung aus und ist
keine.

Zeugen dieser Datei:
  * **Die Erwartungen stammen aus dem Modul-Docstring und den Datenklassen**,
    nicht aus dem Rumpf der Funktion: Welche Payload-Schluessel auf welche
    Emotion-Felder gehen, steht dort; die Defaults stehen in `Emotion` und
    `Character`.
  * **Die Kopie im Pixie-Pfad wird auf Objektidentitaet geprueft**, nicht nur
    auf Gleichheit. Genau hier bricht eine Zerlegung still: Wer die
    feldweise Kopie durch eine Zuweisung ersetzt, erzeugt einen Alias, und
    eine spaetere Aenderung an `internal` schlaegt dann auf `external` durch.
  * **Die Audit-Aufrufe werden gezaehlt.** Fuenf `log_db_read`, ein
    `log_switch`, je ein `span_start`/`span_end` — die Audit-Pflicht ist
    Verhalten, nicht Beiwerk, und eine Zerlegung, die einen Eintrag verliert,
    faellt hier auf.
  * **Der Cold-Start-Raum wird gegen `_raum_aus_labels` geprueft**, also gegen
    dieselbe Funktion, die der Knoten ruft — hier ist der Zeuge bewusst der
    Code, weil die Zahlen aus einer Tabelle stammen, die der Test nicht
    nachbauen soll. Geprueft wird die **Herkunft** (abgeleitet statt geladen),
    nicht der Wert.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

from graph.nodes.db_zugriff import _raum_aus_labels, db_zugriff
from graph.personality import Character, Emotion, InternalPersonality, Personality

# Ein Payload, dessen Werte sich alle von den Defaults unterscheiden — sonst
# ist eine uebernommene Zuordnung von einem Default nicht zu unterscheiden.
PAYLOAD: dict = {
    "current_emotion":    "begeisterung",
    "current_arousal":    0.9,
    "emotions_vektor":    "aufbluehen",
    "gespraechs_modus":   "fachgespraech",
    "sprach_stil":        "gehoben",
    "beziehungs_dynamik": "vertrauen",
    "tone":               "warm",
    "intent":             "recherche_vertiefen",
    "prompt_thema":       "Gravitation",
}

# Novas persistierter Stand, ebenfalls durchgehend abweichend von den Defaults.
NOVA_STATE: dict = {
    "emotion":              "neugierig",
    "arousal":              "0.7",
    "emotions_vector":      "erholung",
    "mode":                 "lernmodus",
    "language_style":       "sachlich",
    "relationship_dynamic": "dankbar",
    "tone":                 "nuechtern",
    "intent":               "reflexion",
    "prompt_topic":         "Entropie",
    "raum_tiefe":           "0.80",
    "raum_naehe":           "0.60",
}

EXTERNAL_HASH: dict = {
    "kern":              "Kern des Nutzers",
    "adaptiv":           "adaptiv Nutzer",
    "beziehungsprofil":  "Beziehung Nutzer",
    "intentions_profil": "Intentionen Nutzer",
    "emotions_profil":   "Emotionen Nutzer",
}

INTERNAL_HASH: dict = {
    "kern":              "Kern Novas",
    "adaptiv":           "adaptiv Nova",
    "beziehungsprofil":  "Beziehung Nova",
    "intentions_profil": "Intentionen Nova",
    "emotions_profil":   "Emotionen Nova",
}


@dataclass
class Lauf:
    """Ein Testlauf: was im State steht und was die vier Quellen liefern.

    Zusammen gesetzt, zusammen gemockt, zusammen verworfen — deshalb eine
    Klasse und keine acht Parameter (`novaberg-lesson_l_klassen-statt-flache-keys.md`).
    """

    nova_state:   dict | None = None
    payload:      dict | None = None
    event_source: str = "user"
    user_id:      str = "meister"
    character_id: str = "nova"
    identities:   list = field(default_factory=list)
    directives:   list = field(default_factory=list)
    select_wirft: bool = False


class DbZugriffBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: alle vier Quellen sind gemockt."""

    def _fahren(self, lauf: Lauf | None = None) -> tuple[dict, dict]:
        """Ruft `db_zugriff` gegen gemockte Quellen.

        Returns:
            (State nach dem Lauf, Dict der Mocks fuer die Audit-Zaehlung)
        """
        lauf = lauf or Lauf()
        state: dict = {
            "user_id":       lauf.user_id,
            "character_id":  lauf.character_id,
            "turn_id":       "turn-1",
            "event_source":  lauf.event_source,
            "event_payload": PAYLOAD if lauf.payload is None else lauf.payload,
        }

        def _select(sql: str, _args: tuple) -> list:
            if lauf.select_wirft:
                raise RuntimeError
            if "charakter_anweisungen" in sql:
                return [{"anweisung": a} for a in lauf.identities]
            return list(lauf.directives)

        redis = MagicMock()
        redis.hgetall.return_value = (
            NOVA_STATE if lauf.nova_state is None else lauf.nova_state
        )
        dbm = MagicMock()
        dbm.select.side_effect = _select

        with patch("graph.nodes.db_zugriff.redis_client", redis), \
             patch("graph.nodes.db_zugriff.db_manager", dbm), \
             patch("graph.nodes.db_zugriff.charakter_hash_retrieve_dict",
                   return_value=dict(EXTERNAL_HASH)), \
             patch("graph.nodes.db_zugriff.nova_charakter_hash_retrieve_dict",
                   return_value=dict(INTERNAL_HASH)), \
             patch("graph.nodes.db_zugriff.span_start", return_value="span-1") as span_auf, \
             patch("graph.nodes.db_zugriff.span_end") as span_zu, \
             patch("graph.nodes.db_zugriff.log_db_read") as db_read, \
             patch("graph.nodes.db_zugriff.log_switch") as switch:
            ergebnis = db_zugriff(state)

        return ergebnis, {
            "span_start": span_auf, "span_end": span_zu,
            "log_db_read": db_read, "log_switch": switch,
        }


class Ausgabevertrag(DbZugriffBasis):
    """Der Knoten befuellt beide Personality-Kanaele."""

    def test_beide_kanaele_sind_befuellt(self) -> None:
        """Beide Kanaele liegen im State und haben den richtigen Typ."""
        state, _ = self._fahren()
        self.assertIsInstance(state["external"], Personality)
        self.assertIsInstance(state["internal"], InternalPersonality)

    def test_derselbe_state_wird_zurueckgegeben(self) -> None:
        """Der Knoten mutiert den State und gibt ihn zurueck, er baut keinen neuen."""
        state: dict = {
            "user_id": "meister", "character_id": "nova",
            "turn_id": "turn-1", "event_source": "user", "event_payload": PAYLOAD,
        }
        redis = MagicMock()
        redis.hgetall.return_value = dict(NOVA_STATE)
        dbm = MagicMock()
        dbm.select.return_value = []
        with patch("graph.nodes.db_zugriff.redis_client", redis), \
             patch("graph.nodes.db_zugriff.db_manager", dbm), \
             patch("graph.nodes.db_zugriff.charakter_hash_retrieve_dict", return_value={}), \
             patch("graph.nodes.db_zugriff.nova_charakter_hash_retrieve_dict", return_value={}), \
             patch("graph.nodes.db_zugriff.span_start", return_value="s"), \
             patch("graph.nodes.db_zugriff.span_end"), \
             patch("graph.nodes.db_zugriff.log_db_read"), \
             patch("graph.nodes.db_zugriff.log_switch"):
            self.assertIs(db_zugriff(state), state)


class Schritt1ExternalEmotion(DbZugriffBasis):
    """external.emotion entsteht aus dem Event-Payload."""

    def test_payload_schluessel_landen_in_den_feldern(self) -> None:
        """Jeder dokumentierte Payload-Schluessel trifft sein Emotion-Feld."""
        state, _ = self._fahren()
        e = state["external"].emotion
        self.assertEqual(e.emotion,              "begeisterung")
        self.assertEqual(e.arousal,              0.9)
        self.assertEqual(e.emotions_vector,      "aufbluehen")
        self.assertEqual(e.mode,                 "fachgespraech")
        self.assertEqual(e.language_style,       "gehoben")
        self.assertEqual(e.relationship_dynamic, "vertrauen")
        self.assertEqual(e.tone,                 "warm")
        self.assertEqual(e.intent,               "recherche_vertiefen")
        self.assertEqual(e.prompt_topic,         "Gravitation")

    def test_leerer_payload_nimmt_die_dokumentierten_defaults(self) -> None:
        """Ohne Payload stehen die Defaults, nicht leere Zeichenketten."""
        state, _ = self._fahren(Lauf(payload={}))
        e = state["external"].emotion
        self.assertEqual(e.emotion, "neutral")
        self.assertEqual(e.arousal, 0.5)
        self.assertEqual(e.mode,    "alltag")
        self.assertEqual(e.intent,  "smalltalk")


class Schritt2InternalEmotion(DbZugriffBasis):
    """internal.emotion und internal.raum entstehen aus redis:nova_state."""

    def test_persistierter_stand_landet_in_den_feldern(self) -> None:
        """Die Redis-Felder treffen ihre Emotion-Felder, arousal wird zur Zahl."""
        state, _ = self._fahren()
        e = state["internal"].emotion
        self.assertEqual(e.emotion, "neugierig")
        self.assertEqual(e.arousal, 0.7)
        self.assertEqual(e.mode,    "lernmodus")
        self.assertEqual(e.intent,  "reflexion")

    def test_cold_start_nimmt_die_emotion_defaults(self) -> None:
        """Leerer Hash: internal.emotion ist die Standard-Emotion."""
        state, _ = self._fahren(Lauf(nova_state={}))
        self.assertEqual(state["internal"].emotion, Emotion())

    def test_unlesbares_arousal_faellt_auf_0_5(self) -> None:
        """Ein nicht zahlbares arousal stuerzt nicht, es nimmt 0.5.

        Der uebrige Stand bleibt dabei erhalten — der Rueckfall gilt genau
        einem Feld und nicht dem ganzen Hash.
        """
        kaputt = dict(NOVA_STATE, arousal="ziemlich hoch")
        state, _ = self._fahren(Lauf(nova_state=kaputt))
        self.assertEqual(state["internal"].emotion.arousal, 0.5)
        self.assertEqual(state["internal"].emotion.emotion, "neugierig")

    def test_geladener_raum_kommt_aus_dem_hash(self) -> None:
        """Stehen beide Raumwerte im Hash, werden sie uebernommen."""
        state, _ = self._fahren()
        raum = state["internal"].raum
        self.assertAlmostEqual(raum.tiefe, 0.80, places=6)
        self.assertAlmostEqual(raum.naehe, 0.60, places=6)

    def test_fehlender_raum_wird_aus_labels_abgeleitet(self) -> None:
        """Ohne Raumwerte im Hash entsteht der Raum aus den Register-Labels.

        Geprueft wird die Herkunft: Das Ergebnis ist dasselbe wie ein direkter
        Aufruf von `_raum_aus_labels` mit derselben Emotion — nicht ein
        erfundener Default.
        """
        ohne_raum = {k: v for k, v in NOVA_STATE.items() if not k.startswith("raum_")}
        state, _ = self._fahren(Lauf(nova_state=ohne_raum))
        erwartet = _raum_aus_labels(state["internal"].emotion)
        self.assertEqual(state["internal"].raum, erwartet)

    def test_unlesbarer_raum_faellt_auf_labels_und_meldet_es(self) -> None:
        """Unlesbare Raumwerte sind ein Defekt: Rueckfall plus error-Zeile."""
        kaputt = dict(NOVA_STATE, raum_tiefe="tief")
        with self.assertLogs("ki_server.db_zugriff", "ERROR") as log:
            state, _ = self._fahren(Lauf(nova_state=kaputt))
        self.assertEqual(
            state["internal"].raum, _raum_aus_labels(state["internal"].emotion),
        )
        self.assertIn("Raumwerte", log.output[-1])


class Schritt3Charaktere(DbZugriffBasis):
    """Die Hash-Spalten treffen die Character-Felder."""

    def test_externer_hash_landet_in_external_character(self) -> None:
        """Die Hash-Spalten treffen ihre Felder: kern → core, adaptiv → adaptive."""
        state, _ = self._fahren()
        c = state["external"].character
        self.assertEqual(c.core,         "Kern des Nutzers")
        self.assertEqual(c.adaptive,     "adaptiv Nutzer")
        self.assertEqual(c.relationship, "Beziehung Nutzer")
        self.assertEqual(c.intentions,   "Intentionen Nutzer")
        self.assertEqual(c.emotions,     "Emotionen Nutzer")

    def test_interner_hash_landet_in_internal_character(self) -> None:
        """Novas Hash geht in internal, nicht in external."""
        state, _ = self._fahren()
        self.assertEqual(state["internal"].character.core, "Kern Novas")

    def test_leerer_hash_ergibt_leere_felder(self) -> None:
        """Ohne Treffer stehen leere Zeichenketten, kein None."""
        state: dict = {
            "user_id": "meister", "character_id": "nova",
            "turn_id": "t", "event_source": "user", "event_payload": {},
        }
        redis = MagicMock()
        redis.hgetall.return_value = {}
        dbm = MagicMock()
        dbm.select.return_value = []
        with patch("graph.nodes.db_zugriff.redis_client", redis), \
             patch("graph.nodes.db_zugriff.db_manager", dbm), \
             patch("graph.nodes.db_zugriff.charakter_hash_retrieve_dict", return_value={}), \
             patch("graph.nodes.db_zugriff.nova_charakter_hash_retrieve_dict", return_value={}), \
             patch("graph.nodes.db_zugriff.span_start", return_value="s"), \
             patch("graph.nodes.db_zugriff.span_end"), \
             patch("graph.nodes.db_zugriff.log_db_read"), \
             patch("graph.nodes.db_zugriff.log_switch"):
            db_zugriff(state)
        self.assertEqual(state["external"].character, Character())


class Schritt4Anweisungen(DbZugriffBasis):
    """identities und directives kommen aus PostgreSQL."""

    def test_identities_werden_zur_liste_von_zeichenketten(self) -> None:
        """Aus den Zeilen wird die Spalte `anweisung` gezogen."""
        state, _ = self._fahren(Lauf(identities=["sei knapp", "kein Smalltalk"]))
        self.assertEqual(state["internal"].identities, ["sei knapp", "kein Smalltalk"])

    def test_directives_behalten_anweisung_und_kontext(self) -> None:
        """Jede Direktive ist ein Dict mit genau diesen zwei Schluesseln."""
        state, _ = self._fahren(
            Lauf(directives=[{"anweisung": "duze", "kontext": "immer"}]),
        )
        self.assertEqual(
            state["internal"].directives,
            [{"anweisung": "duze", "kontext": "immer"}],
        )

    def test_fehlender_kontext_wird_leere_zeichenkette(self) -> None:
        """Eine Zeile ohne `kontext` ergibt "" und nicht None."""
        state, _ = self._fahren(Lauf(directives=[{"anweisung": "duze"}]))
        self.assertEqual(state["internal"].directives[0]["kontext"], "")

    def test_db_ausfall_laesst_den_knoten_weiterlaufen(self) -> None:
        """Wirft die Abfrage, bleiben die Listen leer und der Graph laeuft.

        Der Modul-Docstring sagt es zu: Der Node bricht nicht ab, damit der
        Graph nicht im Eingangsknoten stirbt.
        """
        with self.assertLogs("ki_server.db_zugriff", "WARNING"):
            state, _ = self._fahren(Lauf(select_wirft=True))
        self.assertEqual(state["internal"].identities, [])
        self.assertEqual(state["internal"].directives, [])
        self.assertIsInstance(state["external"], Personality)


class PixieSonderfall(DbZugriffBasis):
    """Bei event_source != "user" ist external eine Kopie von internal."""

    def test_pixie_pfad_kopiert_die_werte(self) -> None:
        """Novas Charakter und Emotion stehen dann auch in external."""
        state, _ = self._fahren(Lauf(event_source="character"))
        self.assertEqual(state["external"].character.core, "Kern Novas")
        self.assertEqual(state["external"].emotion.emotion, "neugierig")

    def test_pixie_pfad_kopiert_und_verweist_nicht(self) -> None:
        """Die Kopie ist ein eigenes Objekt, kein Alias.

        Der Fallstrick der Zerlegung: Wer die feldweise Kopie durch eine
        Zuweisung ersetzt, macht external.emotion zu demselben Objekt wie
        internal.emotion. Eine spaetere Aenderung an einem von beiden schlaege
        dann auf das andere durch, und kein Gleichheitstest wuerde das sehen.
        """
        state, _ = self._fahren(Lauf(event_source="character"))
        self.assertIsNot(state["external"].emotion,   state["internal"].emotion)
        self.assertIsNot(state["external"].character, state["internal"].character)

    def test_user_pfad_nimmt_die_externen_werte(self) -> None:
        """Bei event_source == "user" bleibt external der Nutzer."""
        state, _ = self._fahren(Lauf(event_source="user"))
        self.assertEqual(state["external"].character.core,  "Kern des Nutzers")
        self.assertEqual(state["external"].emotion.emotion, "begeisterung")

    def test_der_zweig_wird_protokolliert(self) -> None:
        """Beide Pfade schreiben einen log_switch mit ihrem Zweignamen."""
        _, mocks = self._fahren(Lauf(event_source="character"))
        inhalt = mocks["log_switch"].call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["zweig"], "pixie_pfad_external_aus_internal")

        _, mocks = self._fahren(Lauf(event_source="user"))
        inhalt = mocks["log_switch"].call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["zweig"], "user_pfad")


class UnvollstaendigesPaar(DbZugriffBasis):
    """Fehlende Paar-Schluessel werden gemeldet, brechen aber nicht ab."""

    def test_leere_schluessel_melden_und_laufen_weiter(self) -> None:
        """error-Zeile, und der State ist danach trotzdem befuellt."""
        with self.assertLogs("ki_server.db_zugriff", "ERROR") as log:
            state, _ = self._fahren(Lauf(user_id="", character_id=""))
        self.assertIn("Paar-Schluessel unvollstaendig", log.output[0])
        self.assertIsInstance(state["external"], Personality)
        self.assertIsInstance(state["internal"], InternalPersonality)


class AuditPflicht(DbZugriffBasis):
    """Die Protokoll-Aufrufe sind Verhalten, nicht Beiwerk."""

    def test_span_wird_geoeffnet_und_geschlossen(self) -> None:
        """Genau ein span_start und ein span_end je Lauf."""
        _, mocks = self._fahren()
        self.assertEqual(mocks["span_start"].call_count, 1)
        self.assertEqual(mocks["span_end"].call_count,   1)

    def test_jede_gelesene_quelle_wird_protokolliert(self) -> None:
        """Fuenf Lesevorgaenge: nova_state, zwei Hashes, Anweisungen, Direktiven.

        Die Zahl steht hier als Literal, damit eine Zerlegung, die einen
        Eintrag verliert, auffaellt — und eine, die einen hinzufuegt, ebenso.
        """
        _, mocks = self._fahren()
        self.assertEqual(mocks["log_db_read"].call_count, 5)

    def test_die_protokollierten_tabellen_sind_benannt(self) -> None:
        """Jeder Lesevorgang nennt seine Quelle im Feld `tabelle`."""
        _, mocks = self._fahren()
        tabellen = [
            ruf.kwargs["inhalt"]["tabelle"]
            for ruf in mocks["log_db_read"].call_args_list
        ]
        self.assertEqual(
            tabellen,
            ["redis:nova_state", "charakter_hash", "charakter_hash",
             "charakter_anweisungen", "direktiven"],
        )

    def test_die_span_id_wandert_in_jeden_lesevorgang(self) -> None:
        """Alle Lesevorgaenge haengen an derselben span_id."""
        _, mocks = self._fahren()
        for ruf in mocks["log_db_read"].call_args_list:
            self.assertEqual(ruf.kwargs["span_id"], "span-1")


if __name__ == "__main__":
    unittest.main()
