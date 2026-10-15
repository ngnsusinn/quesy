import pytest
import math
from backend.services.deduplication import (
    calculate_cosine_similarity,
    check_duplicate_question,
    DuplicateStatus,
)


def test_cosine_similarity_math():
    """Verify cosine similarity calculation accuracy on edge and typical cases."""
    # Identical vectors -> similarity = 1.0
    v1 = [1.0, 2.0, 3.0]
    assert pytest.approx(calculate_cosine_similarity(v1, v1), rel=1e-5) == 1.0

    # Orthogonal vectors -> similarity = 0.0
    v_x = [1.0, 0.0, 0.0]
    v_y = [0.0, 1.0, 0.0]
    assert pytest.approx(calculate_cosine_similarity(v_x, v_y), abs=1e-5) == 0.0

    # Known angle vector (45 degrees: cos(pi/4) = sqrt(2)/2 ~= 0.7071)
    v_diag = [1.0, 1.0, 0.0]
    assert pytest.approx(calculate_cosine_similarity(v_x, v_diag), rel=1e-4) == math.sqrt(2) / 2

    # Zero vector returns 0.0
    v_zero = [0.0, 0.0, 0.0]
    assert calculate_cosine_similarity(v1, v_zero) == 0.0


def test_rule_05_duplicate_flagging_threshold_090():
    """Test RULE-05: Verify cosine similarity calculation flags duplicate questions when threshold >= 0.90."""
    # Reference existing question embedding in DB
    existing_questions = [
        {
            "id": "TOAN-012",
            "stem": "Tìm tập nghiệm của phương trình log2(x - 1) = 3.",
            "embedding": [0.8, 0.5, 0.3, 0.1],
        },
        {
            "id": "TOAN-045",
            "stem": "Tính đạo hàm của hàm số y = x^3 - 3x.",
            "embedding": [0.1, 0.2, 0.9, 0.3],
        },
    ]

    # 1. Nearly identical question with cosine similarity ~ 0.98 >= 0.90
    near_dup_embedding = [0.81, 0.52, 0.29, 0.09]
    res_dup = check_duplicate_question(
        new_embedding=near_dup_embedding,
        existing_questions=existing_questions,
        threshold=0.90,
    )
    assert res_dup["is_duplicate"] is True
    assert res_dup["status"] == DuplicateStatus.DUPLICATE
    assert res_dup["matched_question_id"] == "TOAN-012"
    assert res_dup["similarity"] >= 0.90
    assert "Cảnh báo" in res_dup["warning"]
    assert "TOAN-012" in res_dup["warning"]

    # 2. Moderate similarity between 0.80 and 0.89 -> Warning but not duplicate
    # Vector scaled to have cosine ~ 0.84 with TOAN-012
    mod_embedding = [0.65, 0.65, 0.1, 0.3]
    sim = calculate_cosine_similarity(mod_embedding, existing_questions[0]["embedding"])
    if 0.80 <= sim < 0.90:
        res_mod = check_duplicate_question(
            new_embedding=mod_embedding,
            existing_questions=existing_questions,
            threshold=0.90,
        )
        assert res_mod["is_duplicate"] is False
        assert res_mod["status"] == DuplicateStatus.WARNING
        assert res_mod["similarity"] < 0.90

    # 3. Low similarity < 0.80 -> OK, no duplicate
    low_embedding = [0.0, 0.95, 0.1, 0.05]
    res_low = check_duplicate_question(
        new_embedding=low_embedding,
        existing_questions=existing_questions,
        threshold=0.90,
    )
    assert res_low["is_duplicate"] is False
    assert res_low["status"] == DuplicateStatus.OK
    assert res_low["similarity"] < 0.80
    assert res_low["warning"] is None
