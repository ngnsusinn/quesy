"""Grading services for Quesy examination system according to Circular 32/2018
and Decision 764/QD-BGDDT (2025 format).
"""
from typing import Dict, Any
from backend.services.shuffling_engine import calculate_rule01_score

PROGRESSIVE_SCORE_SCALE = {
    0: 0.0,
    1: 0.10,
    2: 0.25,
    3: 0.50,
    4: 1.00,
}

calculate_true_false_score = calculate_rule01_score
