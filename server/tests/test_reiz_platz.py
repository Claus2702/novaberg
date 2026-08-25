"""Tests: Ein leerer Reiz-Platz ist kein Ausfall, sondern eine Auskunft.

Gegenstand ist die Abloesung von `user_prompt` auf dem Impulsweg. Der
Reiz-Platz traegt, was das **Gegenueber** gesagt hat. Auf einem Impuls-Turn hat
niemand gesprochen — dort steht Novas Gedanke in `eigener_gedanke`, und der
Reiz-Platz ist leer.

**Warum das ueberhaupt eine eigene Datei braucht.** Vier Prompt-Anlaeufe ueber
Monate sind daran gescheitert, dass ein eigener Gedanke auf dem Platz der
fremden Rede ankommt. Der Weg da heraus fuehrt ueber einen leeren Reiz-Platz —
und genau der wird heute an einem Dutzend Stellen als Ausfall gelesen: Der
Verfasser bricht ab, die Salienz meldet ein leeres Bewertungsobjekt, das
Embedding entsteht ueber einer leeren Zeichenkette. Die laute Zuschreibung
gegen einen stillen Turnverlust zu tauschen waere kein Fortschritt.

Zeugen dieser Datei:
  * **Der Gedanke ist ein Literal**, keine Ableitung aus dem Pruefobjekt. Er
    steht einmal oben und wird an jeder Stelle wiedererkannt.
  * **Beide Richtungen werden geprueft.** Dass der Impuls durchkommt, ist erst
    eine Aussage, wenn derselbe Aufruf auf einem Nutzer-Turn weiterhin die
    Nutzer-Aeusserung nimmt — sonst waere auch ein Zugang gruen, der immer den
    Gedanken liefert.
  * **Der Leerfall bleibt ein Leerfall.** Ein Impuls ohne Gedanken ist ein
    Defekt und muss laut bleiben; ein Rueckfall auf den Reiz-Platz waere die
    stille Variante davon.
  * **Die Session bekommt den Gedanken nicht.** Sie ist die eine Stelle, die
    fragt „was hat der Mensch gesagt", und dort ist leer die richtige Antwort.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.kzg.dispatch import dispatch_kzg
from agents.kzg.verdichtung import verdichten
from graph.nodes import dispatcher as disp_mod
from graph.nodes import enricher as enr_mod
from graph.nodes import router as router_mod
from graph.nodes import salience as sal_mod
from graph.nodes import verfasser as verf_mod
from graph.nodes.thinker import _retry_nutzlast
from graph.personality import Emotion, InternalPersonality, Personality
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from graph.state import ConversationState
from services import shadow_delivery

# Von Hand gesetzt, nicht aus dem Pruefobjekt gelesen. Der Satz kommt aus dem
# Gegenstand des Konzepts — ein Rechercheergebnis, wie es auf dem Stapel liegt.
GEDANKE: str = (
    "Der Schatten eines Schwarzen Lochs erscheint groesser als sein "
    "Ereignishorizont, weil die Lichtablenkung den Rand nach aussen zieht."
)
AEUSSERUNG: str = "Was ist eigentlich ein Ereignishorizont?"
ANTWORT: str = "Sie beschreibt die Grenze, hinter der kein Signal mehr zurueckkommt."


def _impuls(**felder: object) -> dict:
    """Ein Impuls-Turn nach dem Umbau: Reiz-Platz leer, Gedanke im eigenen Feld."""
    basis: dict = {
        "user_prompt":     "",
        "eigener_gedanke": GEDANKE,
        "event_source":    "character",
        "event_payload":   {"reiz_herkunft": "eigener_impuls"},
    }
    basis.update(felder)
    return basis


def _nutzer_turn(**felder: object) -> dict:
    """Ein Nutzer-Turn: Reiz-Platz belegt, kein eigener Gedanke."""
    basis: dict = {
        "user_prompt":     AEUSSERUNG,
        "eigener_gedanke": "",
        "event_source":    "user",
        "event_payload":   {},
    }
    basis.update(felder)
    return basis


# ═══════════════════════════════════════════════════════════════════
# Der Kanal
# ═══════════════════════════════════════════════════════════════════

class DerKanalIstDeklariertTest(unittest.TestCase):
    """Der Kanal ist deklariert und hat einen Erzeuger.

    Ein Schluessel, der nicht im Zustandstyp steht, wird an der Knotengrenze
    stillschweigend verworfen — der Wert war da und ist weg.
    """

    def test_eigener_gedanke_steht_im_zustandsschema(self) -> None:
        """Ohne diese Zeile geht der Wert an der Knotengrenze verloren."""
        self.assertIn("eigener_gedanke", ConversationState.__annotations__)

    def test_eigener_gedanke_wird_initialisiert(self) -> None:
        """Deklariert genuegt nicht — ein fehlender Startwert bricht `.get`-freie Leser."""
        from graph.base import GraphBase

        quelle: str = GraphBase.create_state.__code__.co_consts.__str__()
        self.assertIn("eigener_gedanke", quelle)

    def test_der_kanal_hat_eine_quelle_ausserhalb_seiner_selbst(self) -> None:
        """Wer bringt den Wert von aussen herein? Die Zustellung, sonst niemand.

        Ein Kanal, dessen einzige Schreiber aus ihm selbst lesen, ist dauerhaft
        leer — und von jeder Einzelstelle aus sieht die Verkabelung vollstaendig
        aus. Der Zeuge nennt den Erzeuger namentlich.
        """
        import inspect

        from services import shadow_delivery

        quelle: str = inspect.getsource(
            shadow_delivery._impuls_in_den_charaktergraph,
        )
        self.assertIn('"eigener_gedanke"', quelle)


# ═══════════════════════════════════════════════════════════════════
# Der Zugang
# ═══════════════════════════════════════════════════════════════════

class DerZugangTest(unittest.TestCase):
    """`reiz_text` beantwortet eine Frage, die `user_prompt` nicht beantwortet."""

    def test_impuls_liefert_den_gedanken(self) -> None:
        """Der Fall, fuer den der Zugang gebaut wurde."""
        self.assertEqual(reiz_text(_impuls()), GEDANKE)

    def test_nutzer_turn_liefert_die_aeusserung(self) -> None:
        """Die Gegenrichtung — sonst waere auch ein blinder Zugang gruen."""
        self.assertEqual(reiz_text(_nutzer_turn()), AEUSSERUNG)

    def test_ein_gedanke_ohne_herkunftsmarke_ist_kein_reiz(self) -> None:
        """Der Marker entscheidet, nicht die Belegung des Feldes.

        Sonst wuerde ein liegengebliebener Gedanke im Zustand einen echten
        Nutzer-Turn ueberschreiben.
        """
        zustand: dict = _nutzer_turn(eigener_gedanke=GEDANKE)
        self.assertEqual(reiz_text(zustand), AEUSSERUNG)

    def test_impuls_ohne_gedanken_faellt_nicht_auf_den_reiz_platz_zurueck(self) -> None:
        """Ein Ausfall darf nicht wie ein Treffer aussehen.

        Der Rueckfall waere hier besonders verfuehrerisch: Er liefe, und der
        Turn bewertete den falschen Text — ohne dass irgendwo etwas fehlt.
        """
        zustand: dict = _impuls(eigener_gedanke="", user_prompt=AEUSSERUNG)
        self.assertEqual(reiz_text(zustand), "")


# ═══════════════════════════════════════════════════════════════════
# Die vier genannten Stellen
# ═══════════════════════════════════════════════════════════════════

def _verfasser_state(**felder: object) -> dict:
    basis: dict = {
        "user_id": "u", "character_id": "c", "turn_id": "t",
        "memory_context": "", "web_context": "",
        "session_turns": [], "task_block": "", "task_context_cut": False,
        "gespraechsvektor": "", "gv_detail": {}, "antwort_inhalt": "",
        "external": None, "internal": None,
    }
    basis.update(felder)
    return basis


class DerVerfasserMeldetKeinenAusfallTest(unittest.TestCase):
    """Die Leerpruefung der ersten Stufe — die vierte der genannten Stellen."""

    def _lauf(self, zustand: dict) -> tuple:
        antwort = SimpleNamespace(text="URTEIL: keiner\n\nEin Inhalt.", token_total=7)
        with patch.object(verf_mod.model_service.chat, "submit_sync",
                          return_value=antwort) as ruf:
            ergebnis: dict = verf_mod.verfassen(zustand)
        return ergebnis, ruf

    def test_impuls_bricht_nicht_ab(self) -> None:
        """Der leere Reiz-Platz kostet den Turn nicht mehr."""
        ergebnis, ruf = self._lauf(_verfasser_state(**_impuls()))
        self.assertEqual(ruf.call_count, 1)
        self.assertNotEqual(ergebnis["antwort_inhalt"], "")

    def test_der_gedanke_erreicht_die_stufe_als_material(self) -> None:
        """Nicht abbrechen genuegt nicht — der Gedanke muss ankommen.

        **Diese Zusicherung ist am 14.08.2026 umgedreht worden, nicht
        geloescht.** Sie prueft dieselbe Frage — kommt der Gedanke an? — und
        hat nur die Antwort gewechselt: Vorher stand er in der
        Nachrichtenfolge, jetzt als Block im System-Prompt. Der zweite Teil
        ist der eigentliche Zeuge und stand vorher nicht da.
        """
        _, ruf = self._lauf(_verfasser_state(**_impuls()))
        auftrag = ruf.call_args.args[0]
        nachrichten: str = "".join(m["content"] for m in auftrag.messages)

        self.assertIn(GEDANKE, auftrag.system)
        self.assertNotIn(GEDANKE, nachrichten)

    def test_der_platz_des_gegenuebers_traegt_den_gedanken_nicht(self) -> None:
        """Der Kern von Bauteil E, und er ist nicht im Prompttext pruefbar.

        Vier Anlaeufe im Prompttext waren gruen, waehrend das Verhalten blieb.
        Geprueft wird deshalb die **Nachrichtenfolge**: keine Nachricht in der
        Rolle des Gegenuebers traegt den Gedankentext. Dass eine Nachricht dort
        steht, ist erlaubt — ein Auftrag ist keine fremde Rede.
        """
        _, ruf = self._lauf(_verfasser_state(**_impuls()))
        for nachricht in ruf.call_args.args[0].messages:
            if nachricht["role"] == "user":
                self.assertNotIn(GEDANKE, nachricht["content"])

    def test_auf_einem_nutzer_turn_ist_es_unveraendert_umgekehrt(self) -> None:
        """Die Aeusserung des Menschen bleibt auf dem Platz des Menschen."""
        _, ruf = self._lauf(_verfasser_state(**_nutzer_turn()))
        auftrag = ruf.call_args.args[0]
        nachrichten: str = "".join(m["content"] for m in auftrag.messages)

        self.assertIn(AEUSSERUNG, nachrichten)
        self.assertNotIn(AEUSSERUNG, auftrag.system)

    def test_impuls_ohne_gedanken_bleibt_laut(self) -> None:
        """Der positive Zwilling zur Zusicherung oben: Der Riegel wirkt noch."""
        zustand: dict = _verfasser_state(**_impuls(eigener_gedanke="   "))
        with self.assertLogs("ki_server.verfasser", level="ERROR") as log:
            ergebnis: dict = verf_mod.verfassen(zustand)
        self.assertEqual(ergebnis["antwort_inhalt"], "")
        self.assertIn("herkunft=eigener_impuls", "".join(log.output))


class DerResponderBekommtDasselbeMaterialTest(unittest.TestCase):
    """Beide Stufen, nicht eine.

    Ein Zeuge, der nur die erste Stufe sieht, bleibt gruen, waehrend die
    zweite den Gedanken weiter auf den Platz der fremden Rede legt — und
    genau dort hat der Schutz schon einmal ins Leere gegriffen, nur
    andersherum.
    """

    def _auftrag(self, zustand: dict):
        from types import SimpleNamespace

        from graph.nodes import responder as resp_mod

        voll: dict = {
            "gv_detail": {}, "session_turns": [], "memory_context": "",
            "web_context": "", "task_block": "", "antwort_inhalt": "Ein Inhalt.",
            "gespraechsvektor": "", "emotions_verlauf": [],
            "nova_emotions_verlauf": [], "user_intentionen": [],
            "agent_results": [], "user_id": "u", "character_id": "c",
            "turn_id": "t", "external": None, "internal": None,
        }
        voll.update(zustand)
        antwort = SimpleNamespace(text="Eine Antwort.", token_total=3, model="m")
        with patch.object(resp_mod.model_service.chat, "submit_sync",
                          return_value=antwort) as ruf:
            resp_mod.respond(voll)
        return ruf.call_args.args[0]

    def test_der_gedanke_steht_im_system_prompt(self) -> None:
        """Als Material neben Gedaechtnis und Recherche."""
        self.assertIn(GEDANKE, self._auftrag(_impuls()).system)

    def test_keine_nutzer_nachricht_traegt_den_gedanken(self) -> None:
        """Der Platz des Gegenuebers bleibt leer, auch in der zweiten Stufe."""
        for nachricht in self._auftrag(_impuls()).messages:
            if nachricht["role"] == "user":
                self.assertNotIn(GEDANKE, nachricht["content"])

    def test_auf_einem_nutzer_turn_bleibt_es_umgekehrt(self) -> None:
        """Die Aeusserung steht in der Nachricht und nicht im System-Prompt."""
        auftrag = self._auftrag(_nutzer_turn())
        nachrichten: str = "".join(m["content"] for m in auftrag.messages)
        self.assertIn(AEUSSERUNG, nachrichten)
        self.assertNotIn(AEUSSERUNG, auftrag.system)


def _salienz_state(zustand: dict) -> dict:
    basis: dict = {
        "graph_rolle": "character", "ei_calc_rolle": "character",
        "response": ANTWORT, "pending_writes": [], "token_total": 0,
        "turn_id": "t-reiz", "character_id": "nova",
        "gravitationsterm": 0.0, "internal": None,
    }
    basis.update(zustand)
    return basis


class DieSalienzBewertetNichtIsLeereTest(unittest.TestCase):
    """Erste der genannten Stellen: das Lagebild des Reaktions-Laufs."""

    def _lauf(self, zustand: dict) -> dict:
        antwort = MagicMock()
        antwort.parsed = {"salienz": 0.5, "themen": ["Kosmologie"],
                          "dimension": "wissen"}
        antwort.token_total = 0
        antwort.text = "{}"
        gefangen: dict = {}

        def _fangen(auftrag: object) -> object:
            gefangen.setdefault("nachrichten", []).append(auftrag.messages)
            return antwort

        with patch.object(sal_mod.model_service.chat, "submit_sync",
                          side_effect=_fangen):
            with patch.object(sal_mod, "span_start", return_value="s"), \
                 patch.object(sal_mod, "span_end"), \
                 patch.object(sal_mod, "log_switch"), \
                 patch.object(sal_mod, "log_berechnung"), \
                 patch.object(sal_mod, "log_fehler"):
                sal_mod.analyze(zustand, MagicMock(), "meister")
        return gefangen

    def test_impuls_traegt_den_gedanken_ins_lagebild(self) -> None:
        """Der Hintergrund der Reaktion ist der Gedanke, auf den sie folgt."""
        gefangen: dict = self._lauf(_salienz_state(_impuls()))
        inhalte: str = "".join(
            m["content"] for folge in gefangen["nachrichten"] for m in folge
        )
        self.assertIn(GEDANKE, inhalte)

    def test_nutzer_turn_traegt_weiter_die_aeusserung(self) -> None:
        """Und nur sie — sonst blutete der Gedanke in fremde Turns."""
        gefangen: dict = self._lauf(_salienz_state(_nutzer_turn()))
        inhalte: str = "".join(
            m["content"] for folge in gefangen["nachrichten"] for m in folge
        )
        self.assertIn(AEUSSERUNG, inhalte)
        self.assertNotIn(GEDANKE, inhalte)


class DieVerdichtungBekommtDenReizTest(unittest.TestCase):
    """Zweite der genannten Stellen — ueber den Dispatcher, der ihn reicht."""

    def _parameter(self, zustand: dict) -> dict:
        agent = MagicMock()
        agent.invoke.return_value = {"parameter": {"kern": "k"}, "status": "fertig"}
        writes: list = [{"ziel": "kzg", "aktion": "create", "daten": {
            "salienz_obj": {"salienz": 0.5}, "segment": "", "beschreibung": "",
        }}]
        voll: dict = {
            "user_id": "meister", "character_id": "nova",
            "ei_calc_rolle": "character", "graph_rolle": "character",
            "turn_id": "t-reiz", "response": ANTWORT,
            "internal": None, "external": None,
        }
        voll.update(zustand)
        with patch("agents.kzg.dispatch.AgentRegistry.finden", return_value=agent):
            with patch("agents.kzg.dispatch.cfg_redis_client", MagicMock()):
                dispatch_kzg(voll, writes)
        return agent.invoke.call_args.args[0]["parameter"]

    def test_der_dispatcher_reicht_den_gedanken(self) -> None:
        """Die Verdichtung sieht nur, was der Dispatcher ihr gibt."""
        self.assertEqual(self._parameter(_impuls())["reiz"], GEDANKE)

    def test_der_dispatcher_reicht_beim_nutzer_turn_die_aeusserung(self) -> None:
        """Dieselbe Stelle, andere Herkunft, anderes Ergebnis."""
        self.assertEqual(self._parameter(_nutzer_turn())["reiz"], AEUSSERUNG)

    def test_die_verdichtung_stellt_den_reiz_ins_lagebild(self) -> None:
        """Der Kernsatz braucht den Hintergrund, aus dem er stammt."""
        zustand: dict = {
            "aufgabe": "kzg_verarbeitung",
            "kontext": {"user_id": "meister", "character_id": "nova",
                        "beobachter": "assistant", "graph_rolle": "character"},
            "parameter": {"reiz": GEDANKE, "response": ANTWORT, "segment": ANTWORT,
                          "segment_index": 0, "segment_gesamt": 1},
            "schritte": [], "ergebnis": None, "status": "laufend",
            "rueckfrage": None, "fehler": None,
        }
        antwort = SimpleNamespace(text="ein Kern")
        with patch("agents.kzg.verdichtung.model_service.chat.submit_sync",
                   return_value=antwort) as ruf:
            verdichten(zustand)
        nachricht: str = ruf.call_args.args[0].messages[0]["content"]
        self.assertIn(GEDANKE, nachricht.split("[BEWERTUNGSOBJEKT]", 1)[0])


class DieAblageTest(unittest.TestCase):
    """Dritte der genannten Stellen — und die Grenze daneben.

    Der Rohturn ist die Quelle jeder Messreihe ueber Reiz und Reaktion; faellt
    seine Reiz-Haelfte auf einem Impuls-Turn aus, sind die Zahlen vom
    14.08.2026 nicht mehr fortschreibbar. Der Session-Turn dagegen darf ihn
    ausdruecklich **nicht** bekommen.
    """

    def _ablage_state(self, zustand: dict) -> dict:
        basis: dict = {
            "user_id": "meister", "character_id": "nova", "turn_id": "t-reiz",
            "response": ANTWORT,
            "external": Personality(emotion=Emotion()),
            "internal": InternalPersonality(emotion=Emotion()),
            "antwort_inhalt": "", "graph_rolle": "character",
            "session_turn_kern": "", "user_intentionen": [],
            "prompt_embedding": [],
        }
        basis.update(zustand)
        return basis

    def test_der_rohturn_traegt_den_gedanken_als_reiz(self) -> None:
        """Sonst waeren die Messreihen ueber Impuls-Turns nicht fortschreibbar."""
        with patch.object(disp_mod, "log_turn_roh") as ruf:
            disp_mod._turn_roh_schreiben(self._ablage_state(_impuls()))
        self.assertEqual(ruf.call_args.kwargs["inhalt"]["user_prompt"], GEDANKE)
        self.assertEqual(ruf.call_args.kwargs["inhalt"]["herkunft"], "eigener_impuls")

    def test_der_rohturn_traegt_beim_nutzer_turn_die_aeusserung(self) -> None:
        """Die Gegenrichtung, samt Herkunftsmarke."""
        with patch.object(disp_mod, "log_turn_roh") as ruf:
            disp_mod._turn_roh_schreiben(self._ablage_state(_nutzer_turn()))
        self.assertEqual(ruf.call_args.kwargs["inhalt"]["user_prompt"], AEUSSERUNG)
        self.assertEqual(ruf.call_args.kwargs["inhalt"]["herkunft"], "nutzer_turn")

    def test_der_gedanke_wird_nie_als_nutzer_turn_abgelegt(self) -> None:
        """Er staende sonst als fremde Rede im Verlauf, aus dem der naechste liest."""
        zustand: dict = self._ablage_state(_impuls(response=""))
        with patch.object(disp_mod, "session_turn_store") as ruf:
            disp_mod._session_turn_schreiben(zustand)
        self.assertEqual(ruf.call_count, 0)

    def test_eine_echte_aeusserung_wird_weiterhin_abgelegt(self) -> None:
        """Der positive Zwilling: Die Ablage ist nicht einfach abgeschaltet."""
        zustand: dict = self._ablage_state(_nutzer_turn(response=""))
        with patch.object(disp_mod, "session_turn_store") as ruf, \
             patch.object(disp_mod, "session_summarize_if_needed"):
            disp_mod._session_turn_schreiben(zustand)
        self.assertEqual(ruf.call_count, 1)
        self.assertEqual(ruf.call_args.kwargs["inhalt"], AEUSSERUNG)


# ═══════════════════════════════════════════════════════════════════
# Die fuenf Stellen, die im Konzept nicht standen
# ═══════════════════════════════════════════════════════════════════

class DerSuchschluesselTest(unittest.TestCase):
    """Das Embedding speist Gedaechtnissuche und Zielaktivierung.

    Ein Vektor ueber einer leeren Zeichenkette ist kein Ausfall, den irgendwer
    meldet — er ist ein gueltiger Vektor an der falschen Stelle im Raum.

    **Umgezogen am 20.08.2026, nicht abgeschwaecht.** Bis dahin bettete
    `_create_prompt_embedding` den Reiz selbst ein und war damit die Stelle,
    an der die Zusicherung griff. Seit dem Query Rewriting nimmt sie den Text
    entgegen, den `_suchtext_bauen` geformt hat — **dort** wird der Reiz-Platz
    jetzt gelesen, und dort steht die Zusicherung. Der dritte Zeuge deckt den
    Rest ab: Das Embedding nimmt, was es bekommt, und nichts anderes.
    """

    def _text(self, zustand: dict) -> str:
        """Der Text, den `_suchtext_bauen` ohne Rewrite aus dem Zustand holt."""
        # Ein einzelner Turn: zu wenig Verlauf, kein Modellaufruf, rohe
        # Aeusserung — genau der Pfad, auf dem der Reiz-Platz allein zaehlt.
        text, herkunft = enr_mod._suchtext_bauen(zustand, [{"role": "user", "content": "x"}])
        assert herkunft == "zu_wenig_verlauf", herkunft
        return text

    def test_impuls_wird_ueber_den_gedanken_gebildet(self) -> None:
        """Der Suchschluessel des Gedaechtnisses ist der Gedanke selbst."""
        self.assertEqual(self._text(_impuls()), GEDANKE)

    def test_nutzer_turn_wird_ueber_die_aeusserung_gebildet(self) -> None:
        """Die Gegenrichtung."""
        self.assertEqual(self._text(_nutzer_turn()), AEUSSERUNG)

    def test_das_embedding_nimmt_den_uebergebenen_text(self) -> None:
        """Und keinen anderen — sonst waere der Umzug oben wirkungslos."""
        antwort = SimpleNamespace(embedding=[0.0] * 768, duration_seconds=0.0)
        with patch.object(enr_mod.model_service.embed, "submit_sync",
                          return_value=antwort) as ruf:
            enr_mod._create_prompt_embedding(_nutzer_turn(), "ein ganz anderer Text")
        self.assertEqual(ruf.call_args.args[0].text, "ein ganz anderer Text")


class DerRouterEntscheidetNichtUeberNichtsTest(unittest.TestCase):
    """Der Router bestimmt Gedaechtnis, Web und Zeitachse dieses Turns."""

    def _nachricht(self, zustand: dict) -> str:
        antwort = SimpleNamespace(parsed={}, text="{}", token_total=0)
        voll: dict = {"user_id": "", "character_id": ""}
        voll.update(zustand)
        with patch("tools.redis_manager.redis_manager.get_json", return_value=None):
            with patch.object(router_mod.model_service.chat, "submit_sync",
                              return_value=antwort) as ruf:
                router_mod.route(voll)
        return ruf.call_args.args[0].messages[0]["content"]

    def test_impuls_wird_ueber_den_gedanken_geroutet(self) -> None:
        """Der Router entscheidet ueber Gedaechtnis, Web und Zeitachse."""
        self.assertEqual(self._nachricht(_impuls()), GEDANKE)

    def test_nutzer_turn_wird_ueber_die_aeusserung_geroutet(self) -> None:
        """Die Gegenrichtung."""
        self.assertEqual(self._nachricht(_nutzer_turn()), AEUSSERUNG)


class DieLandschaftHatEinenGegenstandTest(unittest.TestCase):
    """Der GV-Node vermisst die Lage — aus dem Reiz, nicht aus dem Platz."""

    def _nachricht(self, zustand: dict) -> str:
        from graph.nodes import gespraechsvektor as gv_mod

        voll: dict = {
            "user_id": "meister", "character_id": "nova",
            "session_turns": [], "user_intentionen": [],
            "external": Personality(emotion=Emotion()),
            "internal": InternalPersonality(emotion=Emotion()),
            "aktivierte_ziele": [],
        }
        voll.update(zustand)
        antwort = SimpleNamespace(text="Eine Lage.", token_total=0)
        with patch.object(gv_mod.model_service.chat, "submit_sync",
                          return_value=antwort) as ruf:
            gv_mod._hypothese_destillieren(voll, 200, "")
        return ruf.call_args.args[0].messages[0]["content"]

    def test_der_gedanke_steht_im_aktuellen_prompt(self) -> None:
        """Die Landschaft entsteht am Reiz — ohne ihn misst sie nichts."""
        self.assertIn(GEDANKE, self._nachricht(_impuls()))

    def test_die_aeusserung_steht_im_aktuellen_prompt(self) -> None:
        """Die Gegenrichtung."""
        self.assertIn(AEUSSERUNG, self._nachricht(_nutzer_turn()))


class DerAgentGraphBekommtDieHerkunftTest(unittest.TestCase):
    """Der direkt gerufene Graph liest den Gedanken wie jeder andere.

    **Der Umbau vom 15.08.2026 stellte elf Leser im CharacterGraph um; dieser
    Weg lag quer dazu.** `shadow_delivery` ruft den AgentGraph nicht ueber ein
    Ereignis, sondern direkt — er trug deshalb kein `event_payload`,
    `reiz_ist_eigener_gedanke` lieferte dort `False`, und jeder Leser hielt
    Novas Gedanken fuer eine Aeusserung des Menschen. Am 23.08.2026
    nachgezogen: `F-REIZ-1` gilt auch fuer den direkten Aufruf.

    Zwei Zeugen, und sie pruefen Verschiedenes: der erste die **Aufrufstelle**
    (traegt sie die Marke?), der zweite die **Wirkung** (kommt der Gedanke
    beim Zugang an?). Ein Feld richtig zu belegen und trotzdem falsch gelesen
    zu werden ist genau der Fall, der hier zwei Monate lief.
    """

    def _create_state_aufruf(self) -> ast.Call:
        """Der `create_state`-Aufruf in `_delivery_ausfuehren`, aus dem Quelltext.

        Vorbedingung: keine.
        Nachbedingung: der Knoten des Aufrufs.

        **Gelesen und nicht nachgebaut.** Ein Zeuge, der die Argumente selbst
        zusammenstellt, prueft seine eigene Vorstellung von der Aufrufstelle
        und bleibt gruen, wenn sie sich aendert.
        """
        quelle: str = inspect.getsource(shadow_delivery)
        baum = ast.parse(quelle)
        aufrufe: list[ast.Call] = [
            knoten for knoten in ast.walk(baum)
            if isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Attribute)
            and knoten.func.attr == "create_state"
        ]
        self.assertEqual(
            len(aufrufe), 1,
            f"{len(aufrufe)} create_state-Aufrufe in shadow_delivery — der "
            f"Zeuge deckt einen ab",
        )
        return aufrufe[0]

    def test_die_aufrufstelle_traegt_gedanke_und_marke(self) -> None:
        """Der Gedanke steht nicht mehr auf dem Reiz-Platz."""
        argumente: dict = {
            wort.arg: wort.value
            for wort in self._create_state_aufruf().keywords
            if wort.arg
        }
        self.assertIn("eigener_gedanke", argumente)
        self.assertIn("event_payload", argumente)

        reiz = argumente.get("user_prompt")
        self.assertIsInstance(reiz, ast.Constant)
        self.assertEqual(
            reiz.value, "",
            "Der Reiz-Platz des AgentGraph-Aufrufs traegt wieder einen Text",
        )

    def test_die_marke_nennt_die_eigene_herkunft(self) -> None:
        """Ein Payload ohne `reiz_herkunft` waere eine leere Geste."""
        argumente: dict = {
            wort.arg: wort.value
            for wort in self._create_state_aufruf().keywords
            if wort.arg
        }
        self.assertIn(
            "event_payload", argumente,
            "Der AgentGraph-Aufruf traegt kein Ereignis-Payload — ohne es ist "
            "die Herkunft nicht markierbar",
        )
        payload = argumente["event_payload"]
        self.assertIsInstance(payload, ast.Dict)
        eintraege: dict = {
            schluessel.value: wert.value
            for schluessel, wert in zip(payload.keys, payload.values, strict=True)
            if isinstance(schluessel, ast.Constant) and isinstance(wert, ast.Constant)
        }
        self.assertEqual(eintraege.get("reiz_herkunft"), "eigener_impuls")

    def test_der_zugang_liefert_daraus_den_gedanken(self) -> None:
        """Die Wirkung, nicht die Belegung — derselbe Zugang wie jeder Knoten."""
        zustand: dict = {
            "user_prompt":     "",
            "eigener_gedanke": GEDANKE,
            "event_payload":   {"reiz_herkunft": "eigener_impuls"},
        }
        self.assertTrue(reiz_ist_eigener_gedanke(zustand))
        self.assertEqual(reiz_text(zustand), GEDANKE)


class DerRetryBehaeltSeineHerkunftTest(unittest.TestCase):
    """Ein wiederholter Impuls bleibt ein Impuls.

    Legte der Thinker den Gedanken auf den Reiz-Platz des Folge-Ereignisses,
    waere der zweite Versuch ein Nutzer-Turn — und die Herkunft, die der
    Rohturn traegt, ab dann falsch. Die Verwechslung faellt nicht auf, weil ein
    Nutzer-Turn mit Text vollstaendig aussieht.
    """

    def test_der_folgelauf_eines_impulses_traegt_gedanke_und_marke(self) -> None:
        """Ein wiederholter Impuls bleibt ein Impuls."""
        nutzlast: dict = _retry_nutzlast(_impuls(turn_id="t-retry"))
        self.assertEqual(nutzlast["eigener_gedanke"], GEDANKE)
        self.assertEqual(nutzlast["reiz_herkunft"], "eigener_impuls")
        self.assertEqual(nutzlast["user_prompt"], "")
        self.assertEqual(nutzlast["turn_id"], "t-retry")

    def test_der_folgelauf_eines_nutzer_turns_bleibt_ein_nutzer_turn(self) -> None:
        """Die Gegenrichtung — der Retry erbt keine fremde Herkunft."""
        nutzlast: dict = _retry_nutzlast(_nutzer_turn(turn_id="t-retry"))
        self.assertEqual(nutzlast["user_prompt"], AEUSSERUNG)
        self.assertEqual(nutzlast["eigener_gedanke"], "")
        self.assertNotEqual(nutzlast["reiz_herkunft"], "eigener_impuls")

    def test_die_nutzlast_laeuft_durch_denselben_zugang(self) -> None:
        """Der Folgelauf liest seinen Reiz genauso wie dieser Lauf.

        Der Zeuge ist nicht die Belegung eines Feldes, sondern die Auskunft,
        die der naechste Durchlauf daraus zieht — dieselbe Funktion, die jeder
        Knoten benutzt.
        """
        for bauer, erwartet in ((_impuls, GEDANKE), (_nutzer_turn, AEUSSERUNG)):
            with self.subTest(reiz=erwartet[:20]):
                nutzlast: dict = _retry_nutzlast(bauer())
                folgelauf: dict = {
                    "user_prompt":     nutzlast["user_prompt"],
                    "eigener_gedanke": nutzlast["eigener_gedanke"],
                    "event_payload":   nutzlast,
                }
                self.assertEqual(reiz_text(folgelauf), erwartet)


if __name__ == "__main__":
    unittest.main()
