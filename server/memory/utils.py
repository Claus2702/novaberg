"""
Memory-Utilities — kleine, seiteneffektfreie Helfer fuer den Memory-Layer.

Aktuell: zentrale Konvertierung eines Embedding-Vektors in die pgvector-
Literal-Darstellung. Norm-Ziel laut Handbook §5 ist eine funktionale
Bibliothek (lib/vectors/); bis die existiert, lebt der Helfer modul-lokal
hier, analog zu ei/utils.py. Reine stdlib, keine Rueck-Importe aus dem
Memory-Layer (zyklusfrei).
"""


def embedding_zu_pgvector_str(embedding: list[float]) -> str:
    """
    Wandelt einen Embedding-Vektor in die pgvector-Literal-Darstellung
    '[v1,v2,...]'.

    Zentrale Konvertierung — ersetzt das zuvor mehrfach inline duplizierte
    Muster. Byte-identisch zur bisherigen Form: str()-Konvertierung pro
    Komponente, Komma-Trenner ohne Leerzeichen, eckige Klammern.
    (Norm-Ziel laut Handbook §5: lib/vectors/ — Migration via Backlog
    LIB-VECTORS-MIGRATION.)
    """
    return "[" + ",".join(str(x) for x in embedding) + "]"
