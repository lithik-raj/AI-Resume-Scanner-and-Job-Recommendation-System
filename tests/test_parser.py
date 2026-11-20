from pathlib import Path
import pytest
import os
import time

from utils.resume_parser import (
    ResumeParseError,
    extract_text,
    extract_resume_text,
    extract_text_from_txt,
    extract_text_fast,
    extract_text_legacy,
    get_parsing_stats,
)
from utils.skill_extractor import extract_skills, skill_exists
from utils.ats_score import get_ats_details


def test_extract_text_from_txt(tmp_path):
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text(
        "Python Machine Learning FastAPI",
        encoding="utf-8",
    )

    text = extract_text_from_txt(str(resume_file))

    assert "Python" in text
    assert "Machine Learning" in text
    assert "FastAPI" in text


def test_missing_file_raises_error(tmp_path):
    resume_file = Path(tmp_path / "missing.pdf")

    with pytest.raises(ResumeParseError):
        extract_resume_text(str(resume_file))


def test_parsing_stats_on_txt(tmp_path):
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text(
        "Senior Software Engineer specializing in Python, Docker, and AWS.",
        encoding="utf-8",
    )

    stats = get_parsing_stats(str(resume_file))

    assert "Senior Software Engineer" in stats["text"]
    assert stats["engine"] == "text_decoder"
    assert stats["char_count"] > 0
    assert stats["latency_ms"] >= 0
    assert "68%+" in stats["performance_badge"]


def test_accelerated_pdf_parsing_if_samples_available():
    base_dir = Path(__file__).resolve().parent.parent
    sample_pdf = base_dir / "uploads" / "sample_resume.pdf"

    if sample_pdf.exists():
        # Test fast extraction
        text, engine, pages = extract_text_fast(str(sample_pdf))
        assert len(text) > 20
        assert pages >= 1
        assert "pypdf" in engine or "pdfplumber" in engine or "fitz" in engine

        # Compare with legacy
        legacy_text = extract_text_legacy(str(sample_pdf))
        assert len(legacy_text) > 20

        # Verify skill extraction fidelity
        skills_fast = extract_skills(text)
        skills_legacy = extract_skills(legacy_text)
        assert len(skills_fast) > 0
        assert set(skills_fast) == set(skills_legacy)


def test_speed_improvement_benchmark_exceeds_threshold():
    """Verify that accelerated parsing demonstrates substantial (>50% to >68%) speed improvement."""
    base_dir = Path(__file__).resolve().parent.parent
    sample_pdf = base_dir / "uploads" / "sample_resume.pdf"

    if sample_pdf.exists():
        # Warmup
        _ = extract_text_legacy(str(sample_pdf))
        _ = extract_text_fast(str(sample_pdf))

        # Measure legacy
        t0 = time.perf_counter()
        for _ in range(5):
            _ = extract_text_legacy(str(sample_pdf))
        dt_legacy = time.perf_counter() - t0

        # Measure fast
        t0 = time.perf_counter()
        for _ in range(5):
            _ = extract_text_fast(str(sample_pdf))
        dt_fast = time.perf_counter() - t0

        speedup = ((dt_legacy - dt_fast) / dt_legacy) * 100
        # Accelerated parsing should show significant speedup
        assert speedup > 50.0, f"Expected speedup > 50%, got {speedup:.2f}%"
