from nlp import (
    clean_text,
    compute_match,
    extract_experience_years,
    extract_skills,
    get_experience_level,
    get_grade,
)


def test_clean_text_reduces_noise():
    cleaned = clean_text("Python, SQL!!! Developer 2024.")
    assert "python" in cleaned
    assert "2024" not in cleaned


def test_extract_skills_detects_keywords():
    text = "Experienced in Python, SQL and Docker automation"
    skills = extract_skills(text)
    assert "python" in skills
    assert "sql" in skills
    assert "docker" in skills


def test_extract_experience_years_from_text():
    assert extract_experience_years("5 years of Python experience") == 5.0
    assert extract_experience_years("Senior software engineer") == 6.0
    assert extract_experience_years("Entry level developer") == 1.0


def test_get_experience_level_classifies_years():
    assert get_experience_level(9) == "Senior"
    assert get_experience_level(5) == "Mid-level"
    assert get_experience_level(2) == "Junior"
    assert get_experience_level(0) == "Unknown"


def test_compute_match_scores_reasonably():
    score, matched, missing, experience_years, experience_level = compute_match(
        "Python SQL Flask",
        "Experienced Python developer with SQL and Flask experience",
    )
    assert score >= 75
    assert "python" in matched
    assert "sql" in matched
    assert "flask" in matched
    assert missing == []
    assert experience_years == 0.0
    assert experience_level == "Unknown"


def test_get_grade_categories():
    assert get_grade(80)["label"] == "Excellent"
    assert get_grade(60)["label"] == "Good"
    assert get_grade(40)["label"] == "Average"
    assert get_grade(10)["label"] == "Low Match"
