import pytest
from utils.scorer import (
    calculate_criterion_score,
    calculate_overall_score,
    ScoringError,
)


def test_calculate_criterion_score():
    assert calculate_criterion_score(5, 20.0) == 20.0
    assert calculate_criterion_score(4, 20.0) == 16.0
    assert calculate_criterion_score(0, 20.0) == 0.0


def test_calculate_criterion_score_invalid_inputs():
    with pytest.raises(ScoringError):
        calculate_criterion_score(-1, 20.0)
    with pytest.raises(ScoringError):
        calculate_criterion_score(6, 20.0)
    with pytest.raises(ScoringError):
        calculate_criterion_score(3, -5.0)
    with pytest.raises(ScoringError):
        calculate_criterion_score("3", 20.0)


def test_calculate_overall_score():
    analysis_results = [
        {
            "criterion": "Python",
            "category": "technical_skills",
            "weight": 50,
            "evidence": "Strong Python experience.",
            "strength": 4,
            "reasoning": "Solid experience.",
        },
        {
            "criterion": "Experience",
            "category": "experience",
            "weight": 20,
            "evidence": "2 years experience.",
            "strength": 3,
            "reasoning": "Moderate experience.",
        },
        {
            "criterion": "Education",
            "category": "education",
            "weight": 10,
            "evidence": "B.S. Computer Science.",
            "strength": 5,
            "reasoning": "Direct match.",
        },
        {
            "criterion": "Projects",
            "category": "projects",
            "weight": 10,
            "evidence": "Multiple ML projects.",
            "strength": 4,
            "reasoning": "Good evidence.",
        },
        {
            "criterion": "Communication",
            "category": "soft_skills",
            "weight": 10,
            "evidence": "Team lead presentation.",
            "strength": 3,
            "reasoning": "Acceptable.",
        },
    ]

    result = calculate_overall_score(analysis_results)
    assert "overall_score" in result
    assert result["overall_score"] > 0
    assert len(result["criteria"]) == 5


def test_calculate_overall_score_empty():
    with pytest.raises(ScoringError):
        calculate_overall_score([])
