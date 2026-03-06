from difflib import SequenceMatcher
from typing import List, Tuple, Optional


def _name_similarity(a: str, b: str) -> float:
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def evaluate_evidence(
    new_sha256: str,
    new_filename: str,
    new_size: int,
    existing_evidences
) -> Tuple[float, List[str], Optional[int]]:
    """
    Retorna:
      score (0..1),
      flags (lista de strings),
      similar_to_id (id de evidencia similar o None)
    """

    # 1) Duplicado EXACTO por hash
    for e in existing_evidences:
        if e.sha256 == new_sha256:
            return 1.0, ["DUPLICATE_HASH"], e.id

    # 2) Similaridad nombre + tamaño
    best_score = 0.0
    best_id = None

    for e in existing_evidences:
        name_sim = _name_similarity(new_filename, e.original_filename)

        if e.size_bytes and new_size:
            size_ratio = min(e.size_bytes, new_size) / max(e.size_bytes, new_size)
        else:
            size_ratio = 0.0

        score = (0.65 * name_sim) + (0.35 * size_ratio)

        if score > best_score:
            best_score = score
            best_id = e.id

    flags = []
    if best_score >= 0.92:
        flags.append("HIGH_SIMILARITY")
    elif best_score >= 0.80:
        flags.append("MEDIUM_SIMILARITY")

    if new_size >= 15 * 1024 * 1024:
        flags.append("LARGE_FILE")

    return float(best_score), flags, best_id