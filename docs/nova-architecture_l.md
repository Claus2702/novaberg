# 07_L_a — Lesson: ROCm-Versionsinkompatibilität

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned — ROCm-Versionsinkompatibilität bei Ollama in Docker
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-architecture_l.md
**Ursprung:** nova-07-l-a.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 1 (12. März 2026)

---

## 1. Was passierte?

Beim initialen Setup sollte Ollama als Docker-Container laufen, wie alle anderen Services. Der Container wurde gebaut, Ollama installiert, Modelle geladen — aber die GPU wurde nicht erkannt. Ollama fiel auf CPU-Inferenz zurück, obwohl eine AMD Radeon 7900 XTX mit ROCm auf dem Host verfügbar war.

## 2. Diagnose

Der Container enthielt ein leeres `rocm/`-Verzeichnis — Ollamas Standard-Installationsscript (`install.sh`) hatte keine ROCm-Binaries heruntergeladen. Auch der explizite Download des ROCm-Tarballs (`ollama-linux-amd64-rocm.tgz`) löste das Problem nicht: Die ROCm-Version im Container (6.x) war inkompatibel mit dem Host-Kernel-Treiber (ROCm 7.1.1 auf Nobara Linux).

**Kernproblem:** ROCm hat eine strikte Kopplung zwischen Kernel-Treiber und Userspace-Bibliotheken. Der Host läuft mit ROCm 7.1.1 (Nobara/Fedora), aber der Ollama-Docker-Container bringt ROCm 6.x mit. Die Versionen sind nicht mischbar.

## 3. Verworfene Lösungsversuche

| Versuch | Ergebnis |
|---------|----------|
| Standard `install.sh` in Docker | Kein ROCm-Binary im Container |
| Expliziter ROCm-Tarball in Docker | ROCm 6.x im Container vs. 7.1.1 auf Host → GPU nicht erkannt |
| `--device /dev/kfd --device /dev/dri` | Geräte sichtbar, aber Versionskonflikt bleibt |

## 4. Lösung

Ollama läuft host-native, nicht in Docker. Alle anderen Services (FastAPI, PostgreSQL, Redis) bleiben in Docker. Die Container erreichen Ollama über `host.docker.internal`.

```
Docker: server, postgres, redis
    │
    └──► http://host.docker.internal:11434  → Ollama GPU (host-native)
    └──► http://host.docker.internal:11435  → Ollama CPU (host-native)
```

Ollama muss per systemd-Override auf `0.0.0.0` gebunden werden, da der Default (`127.0.0.1`) nur localhost-Verbindungen erlaubt und Docker-Container nicht als localhost gelten.

## 5. Erkenntnis

**ROCm + Docker ist auf AMD aktuell nicht produktionsreif.** Die Versionskopplung zwischen Host-Treiber und Container-Userspace macht containerisiertes GPU-Computing mit AMD fragil. NVIDIA hat dieses Problem mit dem NVIDIA Container Toolkit gelöst; ein AMD-Äquivalent existiert nicht in vergleichbarer Reife.

**Pragmatismus vor Purismus:** Der Wunsch, alles in Docker zu haben, ist architektonisch sauber — aber wenn eine Komponente unter Docker nicht funktioniert, ist host-native die richtige Entscheidung. Ein hybrides Deployment (Docker + Host-native) ist besser als ein kaputtes uniformes.

**Zukunft:** Wenn ROCm 7.x in Ollamas Docker-Images unterstützt wird oder ein AMD Container Toolkit erscheint, kann Ollama zurück in Docker wandern. Bis dahin bleibt es host-native — und das funktioniert zuverlässig.

---

→ Tech-Stack & Deployment: `07_A`
→ Pixie-Konzept (Dual-LLM): `05_K`
