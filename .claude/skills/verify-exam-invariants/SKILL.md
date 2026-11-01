---
name: verify-exam-invariants
description: Formally verify Quesy national examination invariants (RULE-01 progressive grading, RULE-02 option anchor, RULE-03 passage contiguity, and section integrity) via Z3 SMT and bounded exhaustive checking. Use whenever modifying exam shuffling, variant generation, option ordering, or scoring logic.
---

# Verify Exam Invariants (Formal Verification)

Run this skill whenever a change touches exam shuffling, option permuting, passage grouping, or scoring logic. It mathematically proves that national examination invariants (Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT) hold for all inputs within stated bounds, not merely for hand-written unit tests.

## Covered Code & Sync Commit

- **Sync Commit**: `a5b8106ce68dd5cb0f3bf54cfd91c8092644e558`
- **Covered Files & Functions**:
  - `backend/services/grading.py`: `calculate_true_false_score`, `PROGRESSIVE_SCORE_SCALE`
  - `backend/services/shuffling.py`: `is_fixed_option`, `shuffle_question_options`, `shuffle_exam_questions`, `generate_exam_variants`
  - `backend/services/shuffling_engine.py`: `calculate_rule01_score`, `is_anchor_option`, `shuffle_options_with_anchor_rule`, `generate_shuffled_variants`

If any of these files have changed since the sync commit, run this verification immediately to ensure no invariants were compromised.

---

## The Invariants & The Harm

1. **RULE-01: Decision 764 Progressive Grading Invariant**
   - **Property**: For any True/False 4-substatement question with `max_points > 0`, the score is strictly monotonic in correct count ($s_0 < s_1 < s_2 < s_3 < s_4$), bounded in $[0, \text{max\_points}]$, with exact ratios:
     - 0 correct $\to 0.0$
     - 1 correct $\to 0.10 \times \text{max\_points}$
     - 2 correct $\to 0.25 \times \text{max\_points}$
     - 3 correct $\to 0.50 \times \text{max\_points}$
     - 4 correct $\to 1.00 \times \text{max\_points}$
   - **Harm if broken**: Candidates in high-stakes national examinations receive incorrect progressive scores, failing Ministry of Education and Training (MOET) standards.

2. **RULE-02: Option Anchor Invariant**
   - **Property**: Any option with `is_fixed=True` or containing position-dependent phrases (`Cả A và B`, `Tất cả các đáp án trên`, `Không có đáp án nào`, `All/None of the above`) is strictly locked at the final position (Slot D / index 3). It never leaks to slots A, B, or C under any seed or permutation. Content multiset is preserved bijectively.
   - **Harm if broken**: A question displaying "A. Cả A và B đều đúng" is nonsensical and invalidates the exam variant.

3. **RULE-03: Passage Integrity & Contiguity Invariant**
   - **Property**: For any reading comprehension passage bundle, all child questions appear strictly contiguously ($\max(\text{indices}) - \min(\text{indices}) + 1 = \text{count}$). No standalone or other passage question is interleaved between them.
   - **Harm if broken**: Students reading a passage encounter an unrelated question in the middle of a passage block.

4. **Section Integrity & Ordering Invariant**
   - **Property**: Section I (SINGLE_CHOICE) strictly precedes Section II (TRUE_FALSE_GROUP), which strictly precedes Section III (SHORT_ANSWER).
   - **Harm if broken**: Exam formats are jumbled, breaking OMR optical answer sheet alignment and standardized national layout.

---

## How to Run

Execute the formal verification suite from the project root:

```bash
python scripts/formal_verification_exam_invariants.py
```

### Expected Output

```
======================================================================
QUESY FORMAL VERIFICATION SUITE: EXAM SHUFFLING & GRADING INVARIANTS
======================================================================

* RULE-01: Decision 764 Progressive Grading Invariant: PASSED [OK]
  Cases verified: 1024
  Details: Verified Z3 SMT monotonicity & bounds + 1024 exhaustive student/key combinations.

* RULE-02: Option Anchor Invariant (Final Slot Locking & Bijectivity): PASSED [OK]
  Cases verified: 6400
  Details: Verified across 6400 option permutation states (all anchor phrases & positions).

* RULE-03: Passage Integrity & Contiguity Invariant: PASSED [OK]
  Cases verified: 500
  Details: Verified across 500 multi-passage configurations & random seeds.

* Section Integrity & Ordering Invariant: PASSED [OK]
  Cases verified: 100
  Details: Verified across 100 random seeds; sections maintain strict partition.

* Self-Test: Fault-Injection & Defect Detectability: PASSED [OK]
  Cases verified: 4
  Details: Verified that all 4 defect types are immediately caught and flagged with counterexamples.

======================================================================
ALL INVARIANTS MATHEMATICALLY & FORMALLY VERIFIED (8028 total cases verified).
======================================================================
```

---

## Triaging Verification Failures

If the script exits with code 1 and outputs `FAILED [X]`:

1. **Read the Counterexample**:
   The output prints a concrete minimal counterexample (e.g. `Anchor option violated! Expected anchor 'Cả A và B' at slot D, but got '...' at slot A`).
2. **Determine Cause**:
   - **Real Bug in Code**: If someone modified `shuffle_question_options` or `shuffle_exam_questions` and altered the partitioning logic, the counterexample reflects an actual defect in `backend/services/shuffling.py` or `shuffling_engine.py`. Fix the production code to satisfy the invariant.
   - **Intentional Model Change**: If Ministry regulations change (e.g., scoring scale update in a future circular), update both `scripts/formal_verification_exam_invariants.py` and the covered backend services, verify all pass, and advance the sync commit in this file.

---

## Scope & Bounds

- **Verified**:
  - Z3 SMT proof of monotonicity and exact boundary conditions across all real numbers `max_points > 0`.
  - Bounded exhaustive search of all 16 student answer vectors $\times$ 16 key vectors (256 pairs) across 4 scaling factors (1024 states) for True/False scoring.
  - Exhaustive anchor permutations across 8 canonical anchor patterns, 4 starting slots, 4 correct answer positions, and 50 random seeds (6,400 states).
  - Multi-passage permutations across 5 bundling structures and 100 seeds (500 states).
- **Out of Scope**:
  - Database connection timeouts and SQL transaction rollbacks (handled by SQLAlchemy/Postgres).
  - UI rendering and LaTeX math font compilation (handled by ReportLab/Tectonic).
