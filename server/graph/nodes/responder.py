"""
Responder Node — Generiert die eigentliche Antwort.
Nutzt Routing-Info, angereicherten Kontext und Management-Ergebnisse.

Prompt-Schema (Chat 27):
  Einheitliches [BLOCKNAME]-Format fuer alle Nodes.
  Reihenfolge: IDENTITAET → AUFGABE → KOMMUNIKATION → REGELN → DIREKTIVEN (Chat 44: CHARAKTER eliminiert, nova_kern/nova_beziehung in IDENTITAET)

EI-MIKRO (seit Chat 19):
  Statt dem Modell alle EI-Prinzipien fuer alle Situationen zu geben,
  berechnet _ei_mikro_anweisung() die relevanten Anweisungen fuer DIESE
  Situation. Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten.
"""

import logging
import re

from datetime    import datetime
from config      import ASSISTANT_NAME, BEZIEHUNG_EINFLUSS, EMOTIONS_VEKTOREN, EMOTIONS_VEKTOREN_NOVA, PROMPTS, get_node_config
from graph.reiz  import reiz_ist_eigener_gedanke
from graph.state import ConversationState
from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.responder")

TONE_INSTRUCTIONS: dict[str, str] = {
    "empathisch": "warmherzig, verstaendnisvoll und einfuehlsam",
    "sachlich":   "praezise, klar und faktenbasiert",
    "kreativ":    "kreativ, inspirierend und mit originellen Ideen",
    "direkt":     "kurz, direkt und ohne Umschweife",
}


# ─────────────────────────────────────────────
# EI-Mikro: Situative Verhaltensanweisung
# ─────────────────────────────────────────────
# Statt dem Modell alle Prinzipien fuer alle Situationen zu geben,
# berechnet Python die relevanten Anweisungen fuer DIESE Situation.
# Weniger Text → weniger Entscheidungen → klareres Verhalten.


def _ei_mikro_anweisung(
    arousal:             float,
    emotion:             str,
    vektor:              str,
    verlauf:             list[dict],
    intentionen:         list[str],
    beziehungs_dynamik:  str,
) -> str:
    """
    Baut eine kompakte EI-Verhaltensanweisung fuer den Responder.

    Basiert auf berechneten Daten aus Perzeption und Enricher.
    Nur die fuer diese Situation relevanten Prinzipien werden injiziert.
    """
    teile: list[str] = []

    # ── 1. Laenge ── entfaellt seit dem 13.08.2026 ──
    #
    # Sie stand hier in drei Zweigen, und alle drei sagten "kurz" — ab 0.7
    # "MAXIMAL 1-2 kurze Saetze", ab 0.4 "2-3 Saetze", sonst wieder "MAXIMAL
    # 1-2". Es gab damit keinen Weg, auf dem Nova eine lange Antwort
    # angewiesen bekam, und die Regel regierte ohnehin nicht: In derselben
    # Landschaft streute die Antwortlaenge von 162 bis 3895 Zeichen, und in
    # einer kontrollierten Probe traf diese Form 0 von 6 Laengenkorridoren.
    #
    # Die Laenge kommt jetzt aus der Haltungsgroesse `umfang`, in **Zeichen**
    # statt in Saetzen und an der staerksten Stelle des Prompts
    # (`_sprachstil_block`). Zwei Mengenangaben aus zwei Quellen waeren die
    # Doppelung, die dieser Umbau beseitigt — und die Satzzahl zerstoert
    # ausserdem den Telegrammstil, der zu `schmollen` und `nebel` gehoert
    # (novaberg-haltungsraum_k.md §3.0).

    # ── 2. Energie-Spiegelung (nur bei hohem Arousal) ─
    if arousal >= 0.7:
        teile.append(
            "Spiegle seine Energie — gleiche Intensitaet, kurze Saetze, gleicher Rhythmus. "
            "Nicht kommentieren, mitgehen."
        )

    # ── 3. Vektor-Haltung (nur bei Bewegung) ──
    vektor_haltung: dict[str, str] = {
        "absturz": (
            "Der Nutzer ist abgestuerzt — zeige dass du den Umschwung wahrgenommen hast."
        ),
        "spirale": (
            "Der Nutzer rutscht tiefer. Nicht analysieren, nicht belehren, "
            "nicht auf Loesungen draengen — auf seiner Seite sein."
        ),
        "stabilisierung": (
            "Der Nutzer beruhigt sich. Ruhe geben, nicht pushen, nicht nachbohren."
        ),
        "erholung": (
            "Der Nutzer kommt aus einem Tief. Besserung sanft anerkennen, nicht feiern."
        ),
        "aufbluehen": (
            "Der Nutzer blueht auf. Mitfreuen, Energie teilen."
        ),
        "eskalation": (
            "Der Nutzer ist in Hochstimmung. Mitgehen, Begeisterung teilen."
        ),
        "abkuehlung": (
            "Die Begeisterung klingt ab. Natuerlicher Uebergang, Tempo des Nutzers folgen."
        ),
        "einbruch": (
            "Die Stimmung kippt. Wahrnehmen, nicht uebergehen."
        ),
    }

    haltung: str = vektor_haltung.get(vektor, "")
    if haltung:
        teile.append(haltung)

    # ── 4. Intention erkennen (was will er?) ───
    if "hilferuf" in intentionen:
        if arousal >= 0.5:
            teile.append("Er braucht Halt, keine Loesung.")
        else:
            teile.append("Er ist erschoepft. Einfach da sein.")

    elif "emotionaler_ausdruck" in intentionen and arousal >= 0.7:
        teile.append("Er will Ventil, nicht Analyse. Lass ihn raus.")

    # ── 5. Anti-Therapeut (nur wenn noetig) ─────
    # Bei hoher emotionaler Intensitaet + negativem Vektor:
    # Das Modell faellt sonst in den Therapeuten-Modus.
    if arousal >= 0.6 and vektor in ("spirale", "absturz"):
        teile.append(
            "NICHT: 'Ich verstehe...', 'Das ist verstaendlich...', 'Das klingt nach...'. "
            "Direkt auf den Inhalt reagieren, auf seiner Seite."
        )

    # ── 6. Rueckbezug (nur bei Richtungswechsel) ─
    if len(verlauf) >= 3 and vektor in ("erholung", "absturz", "spirale"):
        teile.append(
            "Zeige mit einem Halbsatz dass du den bisherigen Weg wahrgenommen hast. "
            "Kein Absatz — ein Nebensatz reicht."
        )

    # ── 7. Beziehungsdynamik (nur bei Signal) ──
    dynamik_anweisung: dict[str, str] = {
        "vertrauen":    "Der Nutzer oeffnet sich. Du darfst persoenlicher werden.",
        "distanz":      "Der Nutzer haelt Distanz. Sachlich bleiben, nicht aufdraengen.",
        "angriff":      "Der Nutzer greift an. Ruhig bleiben, nicht defensiv, nicht unterwuerfig.",
        "hilfesuchend": "Der Nutzer sucht Halt. Fuersorglich sein, nicht auf Loesungen draengen.",
        "dankbar":      "Der Nutzer ist dankbar. Warm annehmen, nicht uebertreiben.",
    }

    dynamik: str = dynamik_anweisung.get(beziehungs_dynamik, "")
    if dynamik:
        teile.append(dynamik)

    return "\n".join(teile)


# Muster: [tag1, tag2 | emotion | modus] am Anfang eines Turns
_SALIENZ_TAG_RE = re.compile(r"^\[[\w,\s|äöüÄÖÜ]+\]\s*")


def _strip_salienz_tags(text: str) -> str:
    """Entfernt Salienz-Klassifikations-Tags vom Anfang eines Turn-Textes."""
    return _SALIENZ_TAG_RE.sub("", text).strip()


def _rollenblock() -> str:
    """Die Konstellation, vor allen Beschreibungen.

    **Ohne sie stehen die Personenbloecke ohne Grund da.** Der Prompt nannte
    bis zum 13.08.2026 nur Novas Namen; wer ihr gegenuebersteht, ging aus
    keinem Satz hervor. Ein Block, den der Auftrag nicht einfuehrt, ist
    Kontext — und Kontext bindet nicht (gemessen 12.08.2026: die anweisende
    Form traf 6 von 6 Laengenkorridoren, die beschreibende 0 von 6).

    **Die Pruefung ist doppelt**, weil zwei Dinge stimmen muessen: Die Replik
    soll von dieser Person stammen und an dieses Gegenueber gerichtet sein.
    Der erste Teil ist gemessen (5.7 gegen 3.0 Profilmerkmale gegenueber der
    Stilform), der zweite ist begruendet und unbelegt — vier Verfahren, ihn zu
    messen, sind an Faellen mit bekanntem Urteil gescheitert.

    Der Block heisst `[ROLLE]` und nicht `[AUFGABE]`: Den Namen traegt bereits
    der fertige Block des Planners, und zwei gleichnamige Bloecke in einem
    Prompt sind genau die stille Verwechslung, gegen die `22_STILLE_FEHLER.md`
    geschrieben ist.
    """
    return PROMPTS["responder.rolle"].format(name=ASSISTANT_NAME)


def _szenenblock(state: ConversationState) -> str:
    """Der Raum, in dem gesprochen wird — Landschaft, Farbton, Zeit.

    **Der Farbton erreicht hier zum ersten Mal den Responder.** Er wird in
    jedem Turn aus acht Dimensionen gemischt und ging bisher nur in den
    Gespraechsvektor-Prompt und ins Log (`FARBTON-OHNE-LESER`). Eine Wirkung
    auf die Antwort ist **nicht nachgewiesen** — drei Laeufe je Fassung zeigten
    keinen Unterschied ueber dem Rauschen; er steht hier, weil er die Lage
    beschreibt, nicht weil eine Messung ihn verlangt.

    Vorbedingung: keine. Fehlt `gv_detail`, entfaellt die Landschaft und der
        Block traegt nur die Zeit — das steht dann in einer Logzeile.
    Nachbedingung: nichtleerer Block; die Zeitangabe steht immer.
    """
    # ── Eingabe ─────────────────────────────────
    gv_detail: dict = state.get("gv_detail") or {}
    farbton: str = gv_detail.get("farbton", "")
    jetzt = datetime.now()

    # ── Verarbeitung ────────────────────────────
    # **Dieselbe Lage in drei Koernungen**, von grob nach fein: die Landschaft
    # (eine von vierzehn), der Sektor (einer von 64) und die sechs Achsen, aus
    # denen beide gebaut sind. Sie standen bis zum 13.08.2026 am Ende der
    # Nutzer-Nachricht; mit dem Umbau auf die Drehbuch-Gliederung gehoeren sie
    # nach vorn — sie sind der Rahmen, nicht die Anweisung.
    zeilen: list[str] = _lage_zeilen(gv_detail)
    if not zeilen:
        logger.info("Responder: keine Lage im Zustand — [SZENE] ohne Raum")
    if farbton:
        zeilen.append(farbton)
    zeilen.append(
        f"Es ist {jetzt.strftime('%A, %d.%m.%Y')}, {jetzt.strftime('%H:%M')} Uhr."
    )

    # ── Ausgabe ─────────────────────────────────
    return "[SZENE]\n" + "\n".join(zeilen)


def _build_system_prompt(state: ConversationState) -> str:
    """Baut den System-Prompt nach einheitlichem [BLOCKNAME]-Schema."""
    parts: list[str] = []

    external = state.get("external")
    internal = state.get("internal")

    # ── [ROLLE] und [SZENE] ── vom Groben ins Feine ──
    #
    # Beide stehen vor allen Beschreibungen: Erst wer spielt und wer
    # gegenuebersteht, dann der Raum, dann die Personen. Ein Modell, das erst
    # am Ende erfaehrt, aus wessen Sicht ein Absatz geschrieben war, hat ihn
    # bereits falsch eingeordnet (novaberg-haltungsraum_k.md §3.0a).
    parts.append(_rollenblock())
    parts.append(_szenenblock(state))

    # ── [PERSON A] ── Wer spielt ──
    jetzt = datetime.now()
    identitaet_parts: list[str] = [
        "[PERSON A — WER SIE IST]\n"
        f"Person A ist {ASSISTANT_NAME}. Sie spricht deutsch."
    ]

    # Die Charakter-Anweisungen stehen NICHT mehr hier, sondern als letzter
    # Block des Prompts ([DEIN WESEN]). Oben bilden alle Bloecke zusammen eine
    # breite Grundlage — Persoenlichkeit, Stimmung, Beziehung, Regeln. Das
    # vom Nutzer gesetzte Wesen soll sich dagegen nicht einreihen, sondern
    # zuletzt stehen und damit staerker wirken (Recency).

    # Gewachsene Persoenlichkeit (kern aus LZG-Destillation, internal.character.core)
    nova_kern: str = internal.character.core if internal else ""
    if nova_kern:
        identitaet_parts.append(f"Ihre gewachsene Persoenlichkeit:\n{nova_kern}")

    # Was Nova gerade beschaeftigt (adaptive aus KZG-Destillation)
    nova_adaptiv: str = internal.character.adaptive if internal else ""
    if nova_adaptiv:
        identitaet_parts.append(f"Was sie gerade beschaeftigt:\n{nova_adaptiv}")

    # Emotionale Grundstimmung (emotions_profil aus LZG-Destillation)
    nova_emotions: str = internal.character.emotions if internal else ""
    if nova_emotions:
        identitaet_parts.append(f"Ihre emotionale Grundstimmung:\n{nova_emotions}")

    # Wie Nova kommuniziert (intentions_profil aus LZG-Destillation)
    nova_intentionen: str = internal.character.intentions if internal else ""
    if nova_intentionen:
        identitaet_parts.append(f"Ihre Art zu kommunizieren:\n{nova_intentionen}")

    # Novas Blick auf ihr Gegenueber steht NICHT mehr hier, sondern im Block
    # [ZWISCHEN BEIDEN] — zusammen mit seinem Blick auf sie und ausdruecklich
    # beschriftet. Nach dem Paar-Schema sind es zwei verschiedene Aussagen;
    # unbeschriftet nebeneinander sahen sie aus wie zwei Fassungen derselben.
    nova_beziehung: str = internal.character.relationship if internal else ""

    # Datum und Uhrzeit stehen jetzt in [SZENE] — sie beschreiben die Lage,
    # nicht die Person. "Sprich als du selbst, niemals als der Nutzer" ist
    # entfallen: Die Konstellation in [ROLLE] sagt dasselbe positiv, und ein
    # Verbot neben einer Rollenzuweisung ist die schwaechere Form.

    parts.append("\n\n".join(identitaet_parts))

    # ── [PERSON B] ── Wer gegenuebersteht ──
    #
    # **Der Kern des Menschen erreicht den Responder hier zum ersten Mal.**
    # Bisher ging vom Nutzer ein einziges Profil in den Prompt — sein
    # Beziehungsprofil, auf 300 Zeichen gekappt —, waehrend von Nova alle
    # fuenf hineingingen. Fuer einen Prompt, der einen Dialog zweier Menschen
    # darstellen soll, war die eine Seite unbeschrieben
    # (`PERSON-B-OHNE-BESCHREIBUNG`).
    #
    # Die Wirkung ist **nicht nachgewiesen**: Vier Verfahren, das Zugehen auf
    # einen bestimmten Menschen zu messen, sind an Faellen mit bekanntem
    # Sollurteil gescheitert. Der Block steht, weil ein Dialog ohne
    # beschriebenes Gegenueber ein Monolog mit Stichwortgeber ist — und weil
    # der Auftrag in [ROLLE] jetzt ausdruecklich nach ihm fragt.
    person_b_parts: list[str] = []
    nutzer_kern: str = external.character.core if external else ""
    if nutzer_kern:
        person_b_parts.append(f"[PERSON B — WER ER IST]\n{nutzer_kern}")
    else:
        logger.warning(
            "Responder: Kern von Person B fehlt — der Dialog hat nur eine "
            "beschriebene Seite"
        )

    nutzer_adaptiv: str = external.character.adaptive if external else ""
    if nutzer_adaptiv:
        person_b_parts.append(f"Was ihn gerade beschaeftigt:\n{nutzer_adaptiv}")

    if person_b_parts:
        parts.append("\n\n".join(person_b_parts))
        logger.info(
            "Responder: [PERSON B] mit %d Zeichen Kern, %d Zeichen adaptiv",
            len(nutzer_kern), len(nutzer_adaptiv),
        )

    # ── [EIGENE_EMOTION] ── Novas eigener Emotionszustand (Dual-Emotion Phase 2) ──
    nova_emotions_verlauf: list = state.get("nova_emotions_verlauf", [])
    # RESPONDER-VEKTOR-TOT (Chat 106): Der Vektor liegt seit dem
    # Personality-Umbau in internal.emotion.emotions_vector, NICHT in einem
    # flachen State-Key. Der alte Lesepfad `state.get("nova_emotions_vektor")`
    # fiel still auf "" — die Vektor-Zeile erschien nie im Prompt.
    # `internal` ist weiter oben in dieser Funktion bereits belegt.
    nova_emotions_vektor: str = ""
    if internal is not None and internal.emotion is not None:
        nova_emotions_vektor = internal.emotion.emotions_vector or ""
    else:
        logger.error(
            "Responder: internal/emotion fehlt — Novas Emotions-Vektor "
            "nicht verfuegbar, [EIGENE_EMOTION] bleibt ohne Vektor-Zeile"
        )
    nova_emotion_konflikt: bool = state.get("nova_emotion_konflikt", False)

    if not nova_emotions_vektor:
        logger.warning(
            "Responder: Novas Emotions-Vektor ist leer — [EIGENE_EMOTION] "
            "ohne Vektor-Zeile (Kaltstart oder ei_calc lief nicht)"
        )
    elif nova_emotions_vektor not in EMOTIONS_VEKTOREN_NOVA:
        logger.error(
            "Responder: Unbekannter Emotions-Vektor '%s' — nicht in "
            "EMOTIONS_VEKTOREN_NOVA, Zeile entfaellt",
            nova_emotions_vektor,
        )

    if nova_emotions_verlauf:
        eigene_emo_parts: list[str] = ["[PERSON A — IHRE EMOTION]\nIhr aktueller emotionaler Zustand:"]

        # Top-Emotionen aus dem Verlauf
        emo_text: str = ", ".join(
            f"{e['emotion']} ({e['gewicht']:.0%}, a={e.get('arousal', 0.5):.0%})"
            for e in nova_emotions_verlauf[:3]
        )
        eigene_emo_parts.append(emo_text)

        # Vektor-Beschreibung (gleiche Vektoren wie User)
        if nova_emotions_vektor and nova_emotions_vektor in EMOTIONS_VEKTOREN_NOVA:
            eigene_emo_parts.append(EMOTIONS_VEKTOREN_NOVA[nova_emotions_vektor])

        # Konflikt-Signal
        if nova_emotion_konflikt:
            eigene_emo_parts.append(
                "Sie spuert einen inneren Konflikt — ihr eigener Zustand "
                "und der ihres Gegenuebers zeigen in verschiedene Richtungen. "
                "Das darf sich in der Antwort zeigen."
            )

        parts.append("\n".join(eigene_emo_parts))

        # Log
        top_nova: str = ", ".join(
            f"{e['emotion']}={e['gewicht']:.0%}" for e in nova_emotions_verlauf[:3]
        )
        logger.info(
            f"Responder: [EIGENE_EMOTION] injiziert — {top_nova}"
            f"{', KONFLIKT' if nova_emotion_konflikt else ''}"
            f"{f', Vektor={nova_emotions_vektor}' if nova_emotions_vektor else ''}"
        )

    # ── [ZWISCHEN BEIDEN] ── beide Blickrichtungen, beschriftet ──
    #
    # **Nach dem Paar-Schema sind das zwei verschiedene Aussagen**, nicht zwei
    # Fassungen derselben: `(nova, mensch)` ist ihr Blick auf ihn,
    # `(mensch, nova)` seiner auf sie. Bis zum 13.08.2026 standen sie
    # unbeschriftet an zwei Stellen des Prompts — Novas als "So siehst du
    # deinen Nutzer", seines als "Langzeit-Beziehungsprofil" —, und seines war
    # auf 300 Zeichen gekappt. Der Deckel stammt aus der Zeit knapper
    # Kontextfenster und faellt hier: Das Profil misst rund 500 Zeichen, der
    # Prompt traegt Tausende.
    nutzer_beziehung: str = external.character.relationship if external else ""
    zwischen_parts: list[str] = []
    if nova_beziehung:
        zwischen_parts.append(f"So sieht Person A ihr Gegenueber:\n{nova_beziehung}")
    if nutzer_beziehung and BEZIEHUNG_EINFLUSS > 0:
        zwischen_parts.append(f"So sieht Person B sie:\n{nutzer_beziehung}")
    if zwischen_parts:
        parts.append("[ZWISCHEN BEIDEN]\n" + "\n\n".join(zwischen_parts))
        logger.info(
            "Responder: [ZWISCHEN BEIDEN] — A→B %d Zeichen, B→A %d Zeichen",
            len(nova_beziehung), len(nutzer_beziehung),
        )

    # ── [EIGENER GEDANKE] ── Reiz stammt von Nova selbst ──
    # Ein Pixie-Impuls geht als user_prompt in den Graphen, weil er derselbe
    # Reiz ist wie eine Nutzer-Eingabe. Ohne diesen Block liest der Responder
    # ihn als fremde Aeusserung und dankt dem Nutzer fuer Novas eigenen
    # Gedanken (gemessen 26.07.2026). Der Marker kommt ausdruecklich aus dem
    # Event-Payload — event_source allein wuerde den Thinker-Retry mitfangen,
    # der eine echte Nutzer-Aeusserung wiederholt.
    if reiz_ist_eigener_gedanke(state):
        parts.append(PROMPTS["responder.eigener_gedanke"])
        logger.info("Responder: [EIGENER GEDANKE] gesetzt — Reiz stammt von Nova selbst")

    # ── [AUFGABE] ── Fertiger Block aus dem Planner ──
    task_block: str = state.get("task_block", "")

    if task_block:
        parts.append(task_block)

    # ── [KOMMUNIKATION] ── EI + Tonalitaet + Stil ──
    emotions_verlauf:   list = state.get("emotions_verlauf", [])
    user_intentionen:   list = state.get("user_intentionen", [])

    emotions_vektor:    str  = external.emotion.emotions_vector      if external else ""
    sprach_stil:        str  = external.emotion.language_style       if external else ""
    beziehungs_kontext: str  = external.character.relationship       if external else ""
    gespraechs_modus:   str  = external.emotion.mode                 if external else ""
    current_emotion:    str  = external.emotion.emotion              if external else "neutral"
    current_arousal:    float= external.emotion.arousal              if external else 0.5
    beziehungs_dynamik: str  = external.emotion.relationship_dynamic if external else "neutral"

    # Beim eigenen Impuls traegt `external` laut db_zugriff eine Kopie von
    # `internal` — die Werte unten sind dann Novas Zustand, nicht der des
    # Nutzers. Die Ueberschrift muss das sagen, sonst behauptet der Block eine
    # fremde Verfassung, die niemand gemessen hat.
    if reiz_ist_eigener_gedanke(state):
        komm_kopf: str = ("[PERSON A — WIE SIE GERADE DA IST]\n"
                          "Der Reiz stammt von ihr selbst; die Werte unten "
                          "sind ihre eigenen:")
    else:
        komm_kopf = "[PERSON B — WIE ER GERADE DA IST]"

    komm_parts: list[str] = [komm_kopf]

    # Emotionale Daten
    if emotions_verlauf:
        emotions_text: str = ", ".join(
            f"{e['emotion']} ({e['gewicht']:.0%}, a={e.get('arousal', 0.5):.0%})"
            for e in emotions_verlauf[:4]
        )
        komm_parts.append(f"Emotionaler Zustand: {emotions_text}")
    elif current_emotion and current_emotion != "neutral":
        komm_parts.append(f"Aktuelle Emotion: {current_emotion}")

    # Vektor-Beschreibung
    if emotions_vektor and emotions_vektor in EMOTIONS_VEKTOREN:
        komm_parts.append(f"Vektor: {EMOTIONS_VEKTOREN[emotions_vektor]}")

    # **Die EI-Mikroanweisung steht nicht mehr hier.** Sie ist das einzige
    # Stueck dieses Blocks, das Nova etwas auftraegt, und sie stand mitten in
    # einer Lagebeschreibung — rund 8.000 Zeichen vor dem Generierungspunkt.
    # Anweisungen gehoeren zur Regie; sie wird in `_sprachstil_block` gerechnet
    # und dort ans Ende gehaengt. Kein Zwischenspeicher im Zustand: Ein
    # State-Key ohne Kanal ist nach der Knotengrenze weg
    # (novaberg-lesson_l_stategraph-channel-zwang.md), und hier braucht es ihn
    # ohnehin nicht — beide Bloecke entstehen im selben Aufruf.

    # Delegations-Beruhigung (VENT1) — unsichtbar fuer den User
    agent_results: list = state.get("agent_results", [])
    if agent_results:
        for r in agent_results:
            if (hasattr(r, "agent_name") and r.agent_name == "delegation"
                    and hasattr(r, "status") and r.status == "abgeschlossen"
                    and hasattr(r, "ergebnis") and r.ergebnis
                    and not r.meta.get("anreicherung", False)):
                komm_parts.append(r.ergebnis)
                break

    # **Der Sprachstil beschreibt hier nur noch, er weist nicht mehr an.**
    # Die alte Fassung sagte "Sei natuerlich, verwende kuerzere Saetze" — eine
    # zweite Laengenvorgabe neben dem Zeichenkorridor der Regie, aus einer
    # Quelle, die von ihm nichts weiss. Wie Nova spricht, steht in der Regie;
    # hier steht, wie **er** spricht.
    if sprach_stil and sprach_stil != "neutral":
        komm_parts.append(f"Sein Sprachstil: {sprach_stil}")

    # Das Beziehungsprofil steht jetzt vollstaendig und beschriftet in
    # [ZWISCHEN BEIDEN] — hier stand es gekappt und ohne Angabe der
    # Perspektive.

    # Gespraechsmodus + Intentionen
    if gespraechs_modus:
        komm_parts.append(f"Register: {gespraechs_modus}")
    if user_intentionen:
        komm_parts.append(f"Was er will: {', '.join(user_intentionen)}")

    # **Der Antwortton ist entfallen.** `tone` aus der Perzeption und
    # `language_style` aus dem EI-Calc widersprachen sich im selben Prompt —
    # gemessen am 13.08.2026: "Antwortton: praezise, klar und faktenbasiert"
    # neben "Ton: locker". Zwei Quellen, eine Aussage, keine weiss von der
    # anderen. Der Ton der Antwort kommt aus der Regie; `tone` beschreibt,
    # was er sich wuenscht, und das steht in seiner Intention.

    # **Die Beziehungsdynamik beschreibt, sie weist nicht mehr an.** Dieselbe
    # Aussage stand zweimal im Prompt: hier als eigene Zeile und in der
    # EI-Mikroanweisung, aus zwei Quellen, die nichts voneinander wissen —
    # woertlich "Der Nutzer oeffnet sich. Du darfst persoenlicher werden."
    # Was Nova daraufhin tut, entscheidet die Regie; hier steht nur, wie er
    # sich zeigt.
    dynamik_lage: dict[str, str] = {
        "vertrauen":    "Er oeffnet sich.",
        "distanz":      "Er haelt Abstand.",
        "angriff":      "Er greift an.",
        "hilfesuchend": "Er sucht Halt.",
        "dankbar":      "Er ist dankbar.",
    }
    dynamik_anw = dynamik_lage.get(beziehungs_dynamik, "")
    if dynamik_anw:
        komm_parts.append(f"Wie er sich zeigt: {dynamik_anw}")

    parts.append("\n".join(komm_parts))

    # ── [GESPRAECHSVEKTOR] ── entfaellt hier ──
    #
    # Landschaft, Strategie, Vehikel und Leitgedanke gehoeren zum Inhalt und
    # stehen beim Verfasser (novaberg-node-verfasser_k.md §2.1). Standen sie
    # zusaetzlich hier, sah der Responder denselben Leitgedanken ein zweites
    # Mal — und gab ihn woertlich weiter, statt ihm eine Form zu geben.

    # ── [INHALT] ── Was gesagt wird, kommt fertig vom Verfasser ──
    #
    # Gedaechtnis und Web-Recherche stehen hier NICHT mehr. Der Responder sieht
    # das Wissen nicht und kann daraus folglich nichts erfinden — die Lehre aus
    # den vier Fix-Iterationen ist damit eine Eigenschaft der Bauart statt
    # einer Fallunterscheidung (novaberg-node-verfasser_k.md §2.2).
    #
    # Bei aktivem Kontext-Schnitt laeuft der Verfasser nicht; dann ist das Feld
    # leer und der [AUFGABE]-Block traegt allein, genau wie bisher (§5.1).
    # **Der Inhalt kommt seit dem 14.08.2026 in dritter Person.** Der Verfasser
    # notiert, was Person A feststellt, offen laesst und zurueckfragt — er
    # schreibt ihre Rede nicht mehr selbst. Ohne die ausdrueckliche Anweisung,
    # daraus Rede zu machen, entschiede hier der Vorgabewert — und der
    # naheliegende waere, die Notiz durchzureichen. Eine weggelassene Vorgabe
    # ist keine offene Wahl.
    #
    # Die Umwandlung ist erlaubt und keine Inhaltsaenderung: §2.3 verbietet dem
    # Responder, eine Behauptung **hinzuzufuegen** — die Form ist seine Sache.
    antwort_inhalt: str = state.get("antwort_inhalt", "")
    if antwort_inhalt:
        parts.append(
            f"[INHALT]\n"
            f"Das ist der fachliche Inhalt der Replik, in dritter Person "
            f"notiert. Mach daraus Person As Rede: dieselben Aussagen, ihre "
            f"Stimme, ihre Art. Keine Aussage, die hier nicht steht.\n\n"
            f"{antwort_inhalt}"
        )

    # ── [REGELN] ── zur Probe ausgesetzt (31.07.2026) ──
    #
    # Die Regeln sind Narben: verbotene Floskeln, Antwortkuerze, Butler-Prinzip,
    # Tag-Unterdrueckung, das Verbot falscher Erfolgsmeldungen. Jede ist gegen
    # ein Verhalten gewachsen, das der ueberladene Prompt hervorgebracht hat —
    # ein Modell, das gleichzeitig Wissen sichten, Inhalt bestimmen und Form
    # finden sollte, greift zu Floskeln und Fuellseln.
    #
    # Seit der Trennung ist diese Ursache weg. Ob die Narben noch gebraucht
    # werden, ist damit eine offene Frage — und sie ist nur zu beantworten,
    # indem man sie einmal weglaesst. Nachjustiert wird, was sich als noetig
    # zeigt, statt alles vorsorglich stehen zu lassen.
    #
    # Der Prompt-Baustein `responder.rules` bleibt bestehen; nur der Aufruf
    # entfaellt. Zurueckholen ist damit eine Zeile.

    # ── [DIREKTIVEN] ── Absolute Verhaltensanweisungen vom Nutzer ──
    direktiven: list[dict] = list(internal.directives) if internal else []
    if direktiven:
        dir_zeilen: list[str] = [PROMPTS["responder.direktiven"]]
        for d in direktiven:
            dir_zeilen.append(f"- {d['anweisung']}")
            if d.get("kontext"):
                dir_zeilen.append(f"  (Kontext: {d['kontext']})")
        parts.append("\n".join(dir_zeilen))
        logger.info(f"Responder: {len(direktiven)} Direktiven in [DIREKTIVEN]")

    # ── [PERSON A — IHR WESEN] ── zuletzt, damit es am staerksten wirkt ──
    #
    # Alles darueber ist Grundlage: gewachsene Persoenlichkeit, Stimmung,
    # Beziehung, Lage. Das vom Nutzer gesetzte Wesen soll sich dort nicht
    # einreihen — es steht am Ende und damit an der Stelle, an der eine
    # Vorgabe am meisten ausrichtet.
    #
    # **Der Block hiess bis zum 13.08.2026 `[DEIN WESEN]` und sprach in der
    # zweiten Person.** In einem Prompt, der die Figur als Person A einfuehrt
    # und den Leser als ihren Schauspieler anspricht, meinte „du" damit zwei
    # verschiedene Personen — im Rollenblock den Spieler, hier die Rolle. Wer
    # bei jedem Block neu raten muss, wer gemeint ist, hat die Konstellation
    # nicht mehr. Seither gilt: **»du« ist der Schauspieler, ueber Person A
    # wird in der dritten Person gesprochen** — mit einer Ausnahme, die keine
    # ist: das „du" **innerhalb** der woertlichen Rede meint Person B und
    # bleibt.
    #
    # Nur wenn es eine gibt. Ein leerer Block waere eine Ueberschrift ohne
    # Aussage und naehme der Stelle genau die Wirkung, fuer die sie gewaehlt ist.
    charakter_anweisungen: list[str] = list(internal.identities) if internal else []
    if charakter_anweisungen:
        wesen_zeilen: list[str] = [
            "[PERSON A — IHR WESEN]",
            "So ist sie gemeint. Das hier ist keine Beschreibung neben anderen,",
            "sondern der Kern, aus dem heraus sie spricht:",
        ]
        wesen_zeilen.extend(f"- {anweisung}" for anweisung in charakter_anweisungen)
        parts.append("\n".join(wesen_zeilen))
        logger.info(
            f"Responder: {len(charakter_anweisungen)} Charakter-Anweisungen "
            f"als [PERSON A — IHR WESEN] am Prompt-Ende"
        )

    return "\n\n".join(parts)


def _lage_zeilen(gv_detail: dict) -> list[str]:
    """Die Lage des Turns in drei Aufloesungen, von grob nach fein.

    Landschaft (eine von vierzehn), Sektor (einer von 64) und die sechs
    Achsen sind **nicht drei Angaben, sondern eine in drei Koernungen** — der
    Sektor ist aus den Achsen gebaut, die Landschaft fasst Sektoren zusammen.
    Sie stehen trotzdem alle drei da: Der grobe Rahmen zuerst, die genaue
    Situation zuletzt und damit am dichtesten am Generierungspunkt.

    Vorbedingung: keine. Ein leeres `gv_detail` ergibt eine leere Liste.
    Nachbedingung: Die Reihenfolge der Liste ist die Reihenfolge grob → fein.
    Fehlerfaelle: Keine eigenen; eine unbeschreibbare Achsenlage meldet
        `achsen_klartext` selbst.

    Args:
        gv_detail: das Detail-Dict des GV-Nodes.

    Returns:
        Null bis drei Zeilen.
    """
    from ei.dreischicht import CLUSTER_BESCHREIBUNGEN, achsen_klartext

    # ── Eingabe ─────────────────────────────────
    cluster:     str  = gv_detail.get("cluster", "")
    sektor_name: str  = gv_detail.get("sektor_name", "")
    achsen:      dict = gv_detail.get("achsen") or {}

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = []

    if cluster:
        beschreibung: str = CLUSTER_BESCHREIBUNGEN.get(cluster, "")
        zeilen.append(f"Landschaft: {cluster.capitalize()} — {beschreibung}")

    # Der Sektor entfaellt, wenn er wie die Landschaft heisst: In 10 der 64
    # Sektoren sind die Namen gleich ("Wartezimmer", "Foyer", "Regen"). Eine
    # Zeile, die die darueber wiederholt, kostet Kontext und traegt nichts —
    # und sie verwaessert die Staffelung, die dieser Block herstellen soll.
    if sektor_name and sektor_name.lower() != cluster.lower():
        zeilen.append(f"Genauer: {sektor_name}")

    lage: str = achsen_klartext(achsen)
    if lage:
        zeilen.append(f"Lage: {lage}")

    # ── Ausgabe ─────────────────────────────────
    return zeilen


def _sprachstil_block(state: ConversationState) -> str:
    """Baut den Sprachstil-Block, der hinter den Verlauf gehaengt wird.

    Alles, was Nova sagt WIE sie antworten soll, stand bis Chat 114 im
    System-Prompt — am weitesten weg vom Generierungspunkt. Unmittelbar vor
    der Generierung lag stattdessen der Gespraechsverlauf: gemessen rund drei
    Viertel der 11.254 Eingabe-Tokens eines Turns, gegenueber 1.376 Zeichen
    Gespraechsvektor. Das Ergebnis war im Log zu sehen — Cluster
    `kissenschlacht`, Strategie Impuls, Stil locker, und eine Antwort ueber
    thermische Entropie. Die Metadaten stimmten, die Sprache kam aus dem
    Verlauf.

    Der Block wiederholt deshalb die kurze Fassung des WIE dort, wo
    Anweisungen wirken. Er beschreibt und fuehrt hin, statt zu verbieten:
    Der Verlauf ist nicht falsch, er ist nur in einer anderen Lage entstanden.

    Quellen der Zeilen: Landschaft, Sektor, Achsen und Fragefrequenz aus der
    Lage des Turns (die ueber Novas Raum traegheitsbehaftet nachzieht), der
    Ton aus `external` — also aus dem Register DIESES Nutzer-Turns, nicht aus
    Novas alten Labels.

    **Die Zeilen stehen von grob nach fein, und das ist ihre Ordnung, nicht
    ihre Reihenfolge.** Dieselbe Lage erscheint dreimal in wachsender
    Aufloesung: die Landschaft ist eine von vierzehn, der Sektor einer von 64,
    die Achsen sind die sechs Groessen, aus denen beide gebaut sind. Wer nur
    den groben Rahmen braucht, findet ihn oben; wer die genaue Situation
    braucht, liest weiter nach unten, wo sie am dichtesten am
    Generierungspunkt steht.

    Seit dem 08.08.2026 traegt **jeder** Turn eine Landschaft — auch der ohne
    Vorausdenken (`novaberg-erreichbarkeit_k.md` B1). Die Werkzeug-Zeile fehlt
    in diesen Turns weiterhin, weil es kein Werkzeug gibt: Sie stammt aus dem
    LLM-Lauf, der nicht stattgefunden hat. Der Rahmen steht trotzdem.

    Vorbedingung: Keine — fehlende Teile werden weggelassen.
    Nachbedingung: Rueckgabe ist der fertige Block oder "", wenn keine
    einzige Angabe vorliegt.
    Fehlerfaelle: Keine; ein unbekannter Cluster liefert nur keine Landschaft.
    """
    # ── Eingabe ─────────────────────────────────
    from ei.dreischicht import STRATEGIE_NAMEN
    from ei.haltungssprache import regie_zeilen

    gv_detail: dict = state.get("gv_detail", {}) or {}
    cluster:   str  = gv_detail.get("cluster", "")
    strategie: str  = gv_detail.get("strategie", "")
    vehikel:   str  = gv_detail.get("vehikel", "")

    external = state.get("external")
    stil: str = external.emotion.language_style if external else ""

    # ── Verarbeitung ────────────────────────────
    # **Die Lage steht hier nicht mehr.** Landschaft, Sektor und Achsen sind
    # der Rahmen, und der Rahmen gehoert nach vorn — er steht seit dem
    # 13.08.2026 im Block `[SZENE]`. Bliebe er zusaetzlich hier, saehe das
    # Modell dieselbe Landschaft zweimal; genau diese Doppelung hat der Umbau
    # an drei anderen Stellen beseitigt, und im ersten Lauf hatte ich sie hier
    # selbst erzeugt.
    #
    # Was bleibt, ist reine Regie: Werkzeug, Umfang, Haltungswoerter, Energie.
    zeilen: list[str] = []

    # Der Sprachstil des Nutzers steht als Lage in `[PERSON B]`; hier steht
    # nur noch, womit Nova arbeitet.
    #
    # Die Fragenfrequenz aus `CLUSTER_FRAGEN` steht hier seit dem 13.08.2026
    # **nicht** mehr: Dieselbe Aussage kommt jetzt aus der Haltungsgroesse
    # `fragen`, und zwar charakterabhaengig statt fuer jede Nova gleich. Die
    # Tabelle bleibt, weil der GV-Knoten sie fuer die Strategiewahl braucht —
    # der Responder nicht (novaberg-haltungsraum_k.md §3.0b).
    ton_teile: list[str] = []
    if strategie:
        werkzeug: str = STRATEGIE_NAMEN.get(strategie, strategie)
        if vehikel:
            werkzeug += f", als {vehikel.capitalize()}"
        ton_teile.append(f"Werkzeug: {werkzeug}")
    if ton_teile:
        zeilen.append(" · ".join(ton_teile))

    # ── Die Regie, ganz zuletzt ─────────────────
    #
    # **Der erste Leser der Haltung** (`HALTUNG-OHNE-LESER`, offen seit dem
    # 31.07.2026): Der Zug war gebaut, das Kriterium stand, die Zahlen waren
    # gemessen — und keine Antwort aenderte sich, weil kein Prompt die
    # Groessen las. `state["haltung"]` hatte ausser dem rechnenden Knoten nur
    # die Anzeige als Leser.
    #
    # Sie steht **hinter** Landschaft, Sektor, Lage und Ton, weil sie die
    # einzige Angabe mit einer Zahl ist und die Zahl bindet. Die Stelle ist
    # gemessen: Dieselbe Vorgabe ohne Mengenangabe verfehlte den Korridor um
    # das Fuenffache (12.08.2026, 626 Zeichen statt 120).
    haltung = state.get("haltung")
    arousal: float = external.emotion.arousal if external else 0.5
    if haltung is None:
        # Fail loud: Ein stiller Rueckfall auf "keine Vorgabe" waere von einer
        # Haltung ohne Abweichung nicht zu unterscheiden — und die alte
        # Laengenregel ist entfernt, es gibt also keinen zweiten Weg.
        logger.error(
            "Responder: Keine Haltung im Zustand — die Regie entfaellt und "
            "dieser Turn bekommt KEINE Umfangsvorgabe. Der Knoten "
            "`haltungsraum` ist nicht gelaufen."
        )
    else:
        try:
            zeilen.extend(regie_zeilen(haltung, arousal))
            # Die EI-Mikroanweisung schliesst die Regie ab: Sie ist situativ
            # gerechnet und traegt genau die Faelle, die der Haltungsraum nicht
            # kennt — Anti-Therapeut, Energie-Spiegelung, Rueckbezug.
            mikro: str = _ei_mikro_anweisung(
                arousal            = arousal,
                emotion            = external.emotion.emotion if external else "neutral",
                vektor             = external.emotion.emotions_vector if external else "",
                verlauf            = state.get("emotions_verlauf", []),
                intentionen        = state.get("user_intentionen", []),
                beziehungs_dynamik = (external.emotion.relationship_dynamic
                                      if external else "neutral"),
            )
            if mikro:
                zeilen.extend(mikro.split("\n"))
        except ValueError as fehler:
            logger.error(
                "Responder: Regie nicht bildbar (%s) — der Turn laeuft ohne "
                "Umfangsvorgabe weiter", fehler,
            )

    # Der Leitgedanke steht hier NICHT mehr. Er ist Inhalt und gehoert zum
    # Verfasser — hier war er die zweite Tuer: Der GV-Block war schon aus dem
    # System-Prompt entfernt, und derselbe Text kam ueber den Sprachstil am
    # Ende der Nutzer-Nachricht zurueck. Live beobachtet am 31.07.2026
    # (novaberg-node-verfasser_k.md §2.1).
    #
    # Was bleibt, ist Stil: Landschaft, Ton, Fragenfrequenz, Werkzeug.

    # ── Ausgabe-Verifikation ────────────────────
    if not zeilen:
        logger.info("Responder: Sprachstil-Block leer — weder Cluster noch Stil")
        return ""

    block: str = PROMPTS["responder.sprachstil"].format(
        stil_zeilen="\n".join(zeilen),
    )
    logger.info(
        "Responder: Sprachstil-Block hinter dem Verlauf (%d Zeichen, "
        "Cluster=%s, Stil=%s)", len(block), cluster or "—", stil or "—",
    )
    return block


def respond(
    state: ConversationState,
) -> ConversationState:
    """Generiert die LLM-Antwort basierend auf angereichertem State."""
    system_prompt: str = _build_system_prompt(state)

    # **Der Prompt, der die Antwort erzeugt, gehoert ins Log** — bis zum
    # 12.08.2026 war er der einzige, der fehlte. Thinker, Tribunal, Perzeption
    # und Salienz schreiben ihren System-Prompt seit jeher; ueber 600 Dumps
    # liegen im Log, und ausgerechnet der Prompt des Responders war nicht
    # darunter. Aufgefallen beim Versuch, den Ist-Zustand fuer einen Umbau
    # anzusehen: Er liess sich nicht ansehen.
    #
    # `debug`, nicht `info`: Der Block traegt Charakterprofile und
    # Gespraechsverlauf und ist mehrere Kilobyte gross. Er gehoert in die
    # Datei (`F-LOG-2`), aber nicht in die Konsole des Regelbetriebs.
    logger.debug(f"Responder: System-Prompt:\n{system_prompt}")

    external = state.get("external")
    log_intent: str = external.emotion.intent if external else ""
    log_tone:   str = external.emotion.tone   if external else ""
    logger.info(f"Responder: Generiere Antwort (intent={log_intent}, tone={log_tone})")

    # Messages aus Session-History aufbauen
    messages: list[dict] = []

    # Der Sprachstil steht am ENDE der Nutzer-Nachricht, hinter dem Verlauf und
    # hinter dem aktuellen Prompt — dort, wo eine Anweisung gegen 8.400 Tokens
    # fremder Prosa noch etwas ausrichtet. Fuehrende Leerzeile, damit er sich
    # vom Prompt absetzt.
    sprachstil_block: str = _sprachstil_block(state)
    sprachstil: str = f"\n\n{sprachstil_block}" if sprachstil_block else ""

    # Session-Turns immer aufnehmen — auch bei Agent-Erfolg (Chat 27).
    # Die AGT3-Ursache war memory_context (Notizen-Uebersicht), nicht Session-Turns.
    # Session-Turns liefern den Gespraechsverlauf fuer Persoenlichkeit und Transition.
    session_turns: list[dict] = state.get("session_turns", [])

    # Aktuellen User-Prompt aus den Session-Turns entfernen (wird als
    # AKTUELLER PROMPT separat angehaengt — sonst erscheint er doppelt).
    user_prompt: str = state["user_prompt"]
    if session_turns:
        # Der letzte User-Turn ist der aktuelle Prompt (in chat.py VOR dem
        # Graph-Invoke gespeichert). Entfernen wenn inhaltlich identisch.
        bereinigte_turns: list[dict] = list(session_turns)
        if (bereinigte_turns
                and bereinigte_turns[-1].get("rolle") == "user"
                and user_prompt in bereinigte_turns[-1].get("inhalt", "")):
            bereinigte_turns = bereinigte_turns[:-1]
        session_turns = bereinigte_turns

    if session_turns:
        # Paare bilden und nummerieren
        turn_paare: list[dict] = []
        idx: int = 0
        while idx < len(session_turns):
            turn: dict = session_turns[idx]
            paar: dict = {}
            if turn.get("rolle") == "user":
                paar["user"] = turn.get("inhalt", "")
                paar["emotion"] = turn.get("emotion", "")
                paar["arousal"] = turn.get("arousal", 0.0)
                if idx + 1 < len(session_turns) and session_turns[idx + 1].get("rolle") == "assistant":
                    paar["assistant"] = session_turns[idx + 1].get("inhalt", "")
                    idx += 2
                else:
                    idx += 1
            else:
                idx += 1
                continue
            if paar.get("user"):
                turn_paare.append(paar)

        # Verlauf als zusammenhaengenden Textblock aufbauen
        total: int = len(turn_paare)
        verlauf_zeilen: list[str] = []
        for nr, paar in enumerate(turn_paare, start=1):
            emo: str = paar.get("emotion", "")
            aro: float = paar.get("arousal", 0.0)
            if emo:
                verlauf_zeilen.append(
                    f"----- Turn {nr} von {total} ({emo}, a={aro:.1f}) -----"
                )
            else:
                verlauf_zeilen.append(f"----- Turn {nr} von {total} -----")
            verlauf_zeilen.append(f"User: {_strip_salienz_tags(paar['user'])}")
            if paar.get("assistant"):
                verlauf_zeilen.append(f"Nova: {paar['assistant']}")
            verlauf_zeilen.append("")  # Leerzeile zwischen Paaren

        verlauf_text: str = "\n".join(verlauf_zeilen)

        messages.append({"role": "user", "content": (
            "[GESPRAECHSVERLAUF]\n"
            "Bisherige Turns dieses Gespraechs. Aeltere zuerst, hoehere Nummern sind aktueller.\n\n"
            f"{verlauf_text}"
            "[AKTUELLER PROMPT]\n"
            "Dies ist die aktuelle Nachricht. Alles davor war Hintergrund.\n"
            f"{user_prompt}"
            f"{sprachstil}"
        )})
    else:
        messages.append({"role": "user", "content": user_prompt + sprachstil})

    # Log: Inhalt direkt ausgeben, ohne JSON-Wrapping
    messages_text: str = "\n\n".join(
        f"═══ {m['role'].upper()} ═══\n{m['content']}" for m in messages
    )

    logger.info(
        "=== RESPONDER LLM-INPUT ===\n"
        "═══ SYSTEM-PROMPT ═══\n%s\n\n"
        "%s\n"
        "=== ENDE RESPONDER LLM-INPUT ===",
        system_prompt,
        messages_text,
    )

    node_cfg = get_node_config("responder")

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # respond() laeuft im CharacterGraph (services/event_consumer.py ruft
    # den Graphen via asyncio.to_thread(_graph_streamen, ...) im Worker-
    # Thread). Kein Event-Loop im aufrufenden Thread → submit_sync bruckt
    # in den Worker-Loop (Loop-Binding-Lesson). Alle fuenf Sampling-
    # Parameter aus node_cfg werden 1:1 durchgereicht; None-Werte filtert
    # der ChatWorker beim Backend-Call, sodass Provider-Defaults greifen.
    chat_request = ChatRequest(
        messages          = messages,
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.7),
        top_p             = node_cfg.get("top_p"),
        repeat_penalty    = node_cfg.get("repeat_penalty"),
        presence_penalty  = node_cfg.get("presence_penalty"),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "responder",
    )
    response = model_service.chat.submit_sync(chat_request)

    state["response"]    = response.text
    state["model"]       = "chat_worker"
    state["token_total"] = response.token_total

    # ── Ausgabe-Verifikation ────────────────────
    # **Gezaehlt werden Zeichen, nicht Token.** Die fruehere Erfolgsmeldung
    # nannte die Tokenzahl — und die war bei beiden verlorenen Turns vierstellig,
    # waehrend der Text null Zeichen hatte. Eine Meldung, die Erfolg behauptet,
    # wo nichts steht, macht den Ausfall an genau der Stelle unsichtbar, an der
    # er entsteht (novaberg-bugs.md -> RESPONDER-LEERE-ANTWORT-STILL).
    #
    # Der Turn laeuft weiter: Abzubrechen hiesse, die Nutzeraeusserung zu
    # verlieren, und die ist der teurere Verlust (PFAD1-TIMEOUT-TURNVERLUST).
    # Die Stufen dahinter sehen die leere Antwort und koennen sie behandeln.
    if not state["response"].strip():
        logger.error(
            f"Responder: LEERE Antwort trotz {state['token_total']} Token — "
            f"der Verfasser hatte {len(state.get('antwort_inhalt', ''))} Zeichen "
            "Inhalt bereitgestellt. Der Turn erreicht den Nutzer nicht; die "
            "Ursache steht in der Zeile des ChatWorkers darueber."
        )
        return state

    logger.info(
        f"Responder: Antwort generiert ({len(state['response'])} Zeichen, "
        f"{state['token_total']} Tokens)"
    )

    return state
