"""Safe Shuffling Engine implementing RULE-02 (Option Anchor Rule)
and RULE-03 (Passage Integrity Rule) according to Circular 32/2018
and Decision 764/QD-BGDDT.
"""
import copy
import random
import re
from typing import List, Dict, Any, Optional

from backend.schemas import (
    Option,
    Question,
    VariantItem,
    VariantOutput,
    ItemFormat,
)

# Anchor phrases that denote position-dependent choices
ANCHOR_PHRASES = [
    r"cả\s+[abcde]\s+và\s+[abcde]",
    r"cả\s+hai\s+đáp\s+án",
    r"tất\s+cả\s+các\s+đáp\s+án",
    r"tất\s+cả\s+các\s+ý\s+trên",
    r"tất\s+cả\s+đều\s+đúng",
    r"không\s+có\s+đáp\s+án\s+nào",
    r"all\s+of\s+the\s+above",
    r"none\s+of\s+the\s+above",
]
ANCHOR_PATTERN = re.compile("|".join(ANCHOR_PHRASES), re.IGNORECASE)

POSITION_LABELS = ["A", "B", "C", "D", "E", "F"]


def is_fixed_option(opt: Option) -> bool:
    """Check if an option is flagged fixed or contains position-dependent keywords."""
    if opt.is_fixed:
        return True
    if ANCHOR_PATTERN.search(opt.content):
        return True
    return False


def shuffle_question_options(
    options: List[Option],
    seed: Optional[int] = None,
) -> List[Option]:
    """RULE-02: Option Anchor Rule.
    
    Fixed options (is_fixed=True or matching anchor phrases like 'Cả A và B', 'Tất cả...')
    are locked at the final position (Position 'D' for 4-choice questions).
    Other options are shuffled and positions are re-indexed.
    """
    if not options:
        return []

    rng = random.Random(seed)

    # Separate fixed options from non-fixed options
    fixed_options: List[Option] = []
    movable_options: List[Option] = []

    for opt in options:
        if is_fixed_option(opt):
            fixed_options.append(opt)
        else:
            movable_options.append(opt)

    # Shuffle the movable options
    shuffled_movable = list(movable_options)
    rng.shuffle(shuffled_movable)

    # Combine: movable first, fixed at the end (e.g. index 3 -> 'D')
    combined = shuffled_movable + fixed_options

    # Re-assign labels (A, B, C, D...)
    result = []
    for idx, opt in enumerate(combined):
        label = POSITION_LABELS[idx] if idx < len(POSITION_LABELS) else chr(65 + idx)
        result.append(
            Option(
                label=label,
                content=opt.content,
                is_correct=opt.is_correct,
                is_fixed=is_fixed_option(opt),
            )
        )

    return result


def shuffle_exam_questions(
    questions: List[Question],
    seed: Optional[int] = None,
) -> List[Question]:
    """RULE-03: Passage Integrity Rule & Section Integrity.
    
    Questions are preserved by Section / ItemFormat.
    Within each format:
    - Questions sharing a `passage_id` form an indivisible atomic block (Passage block).
    - Unrelated single questions can never be interleaved inside a passage's child questions.
    - Shuffling permutes atomic blocks (passages and standalone questions).
    """
    if not questions:
        return []

    rng = random.Random(seed)

    # Group questions by section/item_format to preserve Section Integrity
    sections: Dict[ItemFormat, List[Question]] = {}
    format_order: List[ItemFormat] = []

    for q in questions:
        fmt = q.item_format
        if fmt not in sections:
            sections[fmt] = []
            format_order.append(fmt)
        sections[fmt].append(q)

    final_questions: List[Question] = []

    for fmt in format_order:
        fmt_questions = sections[fmt]

        # Group by passage_id into atomic units
        atomic_units: List[List[Question]] = []
        passage_map: Dict[str, List[Question]] = {}

        for q in fmt_questions:
            if q.passage_id:
                if q.passage_id not in passage_map:
                    unit: List[Question] = []
                    passage_map[q.passage_id] = unit
                    atomic_units.append(unit)
                passage_map[q.passage_id].append(q)
            else:
                atomic_units.append([q])

        # Shuffle atomic units
        shuffled_units = list(atomic_units)
        rng.shuffle(shuffled_units)

        # Flatten atomic units
        for unit in shuffled_units:
            final_questions.extend(unit)

    return final_questions


def generate_exam_variants(
    exam_title: str,
    questions: List[Question],
    num_variants: int = 4,
    variant_codes: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> List[VariantOutput]:
    """Generate multiple shuffled exam variants enforcing RULE-02 and RULE-03."""
    if not variant_codes:
        variant_codes = [f"{101 + i}" for i in range(num_variants)]
    else:
        variant_codes = variant_codes[:num_variants]

    base_seed = seed if seed is not None else random.randint(1000, 999999)
    variants: List[VariantOutput] = []

    for v_idx, code in enumerate(variant_codes):
        variant_seed = base_seed + (v_idx + 1) * 31

        # 1. Shuffle question order while respecting passage integrity
        shuffled_questions = shuffle_exam_questions(questions, seed=variant_seed)

        # 2. For each question, shuffle options while respecting RULE-02
        variant_items: List[VariantItem] = []
        answer_keys: Dict[str, Any] = {}

        for pos_idx, q in enumerate(shuffled_questions):
            pos = pos_idx + 1
            shuffled_options = None
            if q.options:
                opt_seed = variant_seed + pos * 17
                shuffled_options = shuffle_question_options(q.options, seed=opt_seed)

                # Record answer key for single choice
                correct_opts = [opt.label for opt in shuffled_options if opt.is_correct]
                answer_keys[str(pos)] = correct_opts[0] if correct_opts else ""
            elif q.sub_statements:
                # True/False sub-statements key
                tf_key = {s.label: s.is_true for s in q.sub_statements}
                answer_keys[str(pos)] = tf_key
            elif q.short_answer_solution:
                answer_keys[str(pos)] = q.short_answer_solution

            variant_items.append(
                VariantItem(
                    question_id=q.id,
                    stem=q.stem,
                    item_format=q.item_format,
                    passage_id=q.passage_id,
                    options=shuffled_options,
                    sub_statements=q.sub_statements,
                    position=pos,
                )
            )

        variants.append(
            VariantOutput(
                variant_code=code,
                questions=variant_items,
                answer_keys=answer_keys,
            )
        )

    return variants
