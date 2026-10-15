"""AI Vector Deduplication Service implementing RULE-05 according to Circular 32/2018
and BRD/SRS Specifications (Cosine similarity >= 0.90 duplicate warning).
"""
import math
from enum import Enum
from typing import List, Dict, Any, Optional


class DuplicateStatus(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    DUPLICATE = "DUPLICATE"


def calculate_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate the cosine similarity between two numeric vectors.
    
    Formula: (A . B) / (||A|| * ||B||)
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    sim = dot_product / (norm_a * norm_b)
    # Clamp floating point rounding errors to [-1.0, 1.0]
    return max(-1.0, min(1.0, float(sim)))


def check_duplicate_question(
    new_embedding: List[float],
    existing_questions: List[Dict[str, Any]],
    threshold: float = 0.90,
    warning_threshold: float = 0.80,
) -> Dict[str, Any]:
    """RULE-05: Verify cosine similarity calculation flags duplicate questions.
    
    - Similarity >= threshold (0.90): Duplicate question flagged (status: DUPLICATE, is_duplicate: True)
    - warning_threshold <= Similarity < threshold: Warning flagged (status: WARNING, is_duplicate: False)
    - Similarity < warning_threshold: Normal (status: OK, is_duplicate: False)
    """
    if not new_embedding or not existing_questions:
        return {
            "is_duplicate": False,
            "similarity": 0.0,
            "matched_question_id": None,
            "status": DuplicateStatus.OK,
            "warning": None,
        }

    max_sim = -1.0
    matched_id = None
    matched_stem = None

    for q in existing_questions:
        q_emb = q.get("embedding")
        if not q_emb:
            continue
        sim = calculate_cosine_similarity(new_embedding, q_emb)
        if sim > max_sim:
            max_sim = sim
            matched_id = q.get("id")
            matched_stem = q.get("stem")

    if max_sim >= threshold:
        pct = round(max_sim * 100)
        return {
            "is_duplicate": True,
            "similarity": round(max_sim, 4),
            "matched_question_id": matched_id,
            "matched_stem": matched_stem,
            "status": DuplicateStatus.DUPLICATE,
            "warning": f"Cảnh báo: Phát hiện câu hỏi trùng lặp {pct}% với câu hỏi [{matched_id}]",
        }
    elif max_sim >= warning_threshold:
        pct = round(max_sim * 100)
        return {
            "is_duplicate": False,
            "similarity": round(max_sim, 4),
            "matched_question_id": matched_id,
            "matched_stem": matched_stem,
            "status": DuplicateStatus.WARNING,
            "warning": f"Lưu ý: Phát hiện câu hỏi tương tự {pct}% với câu hỏi [{matched_id}]",
        }
    else:
        return {
            "is_duplicate": False,
            "similarity": max(0.0, round(max_sim, 4)),
            "matched_question_id": None,
            "status": DuplicateStatus.OK,
            "warning": None,
        }
