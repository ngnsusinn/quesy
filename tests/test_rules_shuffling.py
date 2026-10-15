import itertools
import pytest

from backend.schemas import (
    Option,
    SubStatement,
    Question,
    CognitiveLevel,
    ItemFormat,
)
from backend.services.grading import calculate_true_false_score
from backend.services.shuffling import (
    shuffle_question_options,
    shuffle_exam_questions,
    generate_exam_variants,
)


# -----------------------------------------------------------------
# RULE-01: True/False 4-substatement progressive grading logic
# -----------------------------------------------------------------

def test_rule_01_progressive_grading_all_16_combinations():
    """Test RULE-01: True/False 4-statement progressive grading logic with all 16 possible combinations.
    
    Grading scale:
    - 0 statements correct: 0.0
    - 1 statement correct: 0.1
    - 2 statements correct: 0.25
    - 3 statements correct: 0.5
    - 4 statements correct: 1.0
    """
    labels = ["a", "b", "c", "d"]
    # Reference answer key: a=True, b=True, c=False, d=True
    answer_key = {"a": True, "b": True, "c": False, "d": True}

    score_map = {
        0: 0.0,
        1: 0.1,
        2: 0.25,
        3: 0.5,
        4: 1.0,
    }

    tested_combinations = 0
    # Generate all 2^4 = 16 boolean permutations for student answers
    for student_bools in itertools.product([True, False], repeat=4):
        student_answers = dict(zip(labels, student_bools))
        
        # Count expected correct statements
        correct_count = sum(
            1 for lbl in labels if student_answers[lbl] == answer_key[lbl]
        )
        expected_score = score_map[correct_count]

        actual_score = calculate_true_false_score(student_answers, answer_key)
        assert pytest.approx(actual_score, rel=1e-5) == expected_score, (
            f"Failed for student_answers={student_answers}, key={answer_key}: "
            f"expected {expected_score} for {correct_count} correct statements, got {actual_score}"
        )
        tested_combinations += 1

    assert tested_combinations == 16, f"Expected 16 combinations, tested {tested_combinations}"


# -----------------------------------------------------------------
# RULE-02: Option Anchor Rule (Cả A và B / is_fixed)
# -----------------------------------------------------------------

def test_rule_02_option_anchor_100_iterations():
    """Test RULE-02: Run 100 iterations of variant shuffling on questions with
    'Cả A và B đều đúng' and is_fixed=True, asserting it is ALWAYS at position D in 100% of variants.
    """
    options = [
        Option(label="A", content="Phương án 1", is_correct=False, is_fixed=False),
        Option(label="B", content="Phương án 2", is_correct=False, is_fixed=False),
        Option(label="C", content="Phương án 3", is_correct=False, is_fixed=False),
        Option(label="D", content="Cả A và B đều đúng", is_correct=True, is_fixed=True),
    ]

    for iteration in range(100):
        shuffled = shuffle_question_options(options, seed=iteration)
        assert len(shuffled) == 4
        # Assert that the fixed option is ALWAYS at position index 3 (Position D)
        assert shuffled[3].label == "D"
        assert shuffled[3].content == "Cả A và B đều đúng"
        assert shuffled[3].is_fixed is True

        # Assert positions A, B, C contain the first three options (in some permutation)
        first_three_contents = {opt.content for opt in shuffled[:3]}
        assert first_three_contents == {"Phương án 1", "Phương án 2", "Phương án 3"}

    # Also test when fixed option is provided at an arbitrary initial position (e.g. index 1)
    options_misplaced = [
        Option(label="A", content="Phương án 1", is_correct=False, is_fixed=False),
        Option(label="B", content="Cả A và B đều đúng", is_correct=True, is_fixed=True),
        Option(label="C", content="Phương án 2", is_correct=False, is_fixed=False),
        Option(label="D", content="Phương án 3", is_correct=False, is_fixed=False),
    ]
    for iteration in range(100):
        shuffled = shuffle_question_options(options_misplaced, seed=iteration + 1000)
        assert shuffled[3].label == "D"
        assert shuffled[3].content == "Cả A và B đều đúng"


# -----------------------------------------------------------------
# RULE-03: Passage Integrity Rule (Conscutive Child Questions)
# -----------------------------------------------------------------

def test_rule_03_passage_integrity_in_all_variants():
    """Test RULE-03: Verify passage parent and child questions are consecutive in all variants."""
    # Create passage child questions
    passage_id = "passage-group-01"
    child_questions = [
        Question(
            id=f"child-{i}",
            stem=f"Câu hỏi con {i} dựa vào đoạn văn đọc hiểu",
            subject_id="subj-anh",
            grade_id="grade-12",
            learning_outcome_id="TIENGANH12.DH.01",
            cognitive_level=CognitiveLevel.COMPREHENSION,
            item_format=ItemFormat.PASSAGE_GROUP,
            passage_id=passage_id,
            options=[
                Option(label="A", content=f"Opt A{i}"),
                Option(label="B", content=f"Opt B{i}"),
                Option(label="C", content=f"Opt C{i}"),
                Option(label="D", content=f"Opt D{i}"),
            ],
        )
        for i in range(1, 5)  # 4 child questions
    ]

    # Create 10 standalone questions
    single_questions = [
        Question(
            id=f"single-{i}",
            stem=f"Câu hỏi đơn lẻ độc lập số {i}",
            subject_id="subj-anh",
            grade_id="grade-12",
            learning_outcome_id="TIENGANH12.DH.01",
            cognitive_level=CognitiveLevel.RECOGNITION,
            item_format=ItemFormat.SINGLE_CHOICE,
            options=[
                Option(label="A", content="A"),
                Option(label="B", content="B"),
                Option(label="C", content="C"),
                Option(label="D", content="D"),
            ],
        )
        for i in range(1, 11)
    ]

    all_questions = single_questions[:5] + child_questions + single_questions[5:]

    # Run shuffling over 50 iterations / seeds with multiple variants
    for seed in range(50):
        variants = generate_exam_variants(
            exam_title="Đề thi Tiếng Anh 12",
            questions=all_questions,
            num_variants=4,
            variant_codes=["101", "102", "103", "104"],
            seed=seed,
        )

        for variant in variants:
            # Locate all child question positions in the variant
            child_indices = [
                idx for idx, q in enumerate(variant.questions)
                if q.passage_id == passage_id
            ]

            assert len(child_indices) == 4, (
                f"Variant {variant.variant_code} lost child questions! Found {len(child_indices)}/4"
            )

            # Assert all child questions are strictly consecutive
            min_idx = min(child_indices)
            expected_indices = list(range(min_idx, min_idx + 4))
            assert child_indices == expected_indices, (
                f"Variant {variant.variant_code} violated RULE-03 (Passage Integrity)! "
                f"Child indices {child_indices} are not strictly consecutive."
            )

            # Ensure no single question is interleaved inside child indices
            for idx in expected_indices:
                assert variant.questions[idx].passage_id == passage_id
