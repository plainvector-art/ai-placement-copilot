"""Unit tests for ATS Scorer."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ats_scorer import calculate_ats_score, score_skills, score_projects


SAMPLE_PROFILE = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-1234",
    "linkedin": "linkedin.com/in/janesmith",
    "github": "github.com/janesmith",
    "skills": ["Python", "SQL", "Machine Learning", "Docker", "React", "FastAPI"],
    "experience": [{"raw": "Software Engineer at TechCorp 2022-2024. Built APIs serving 10k+ users."}],
    "projects": [
        {"title": "ML Pipeline", "description": "End-to-end ML pipeline", "technologies": ["Python", "scikit-learn"]},
        {"title": "REST API", "description": "FastAPI backend", "technologies": ["FastAPI", "PostgreSQL"]},
    ],
    "education": [{"degree": "B.Tech Computer Science", "year": "2022"}],
    "certifications": ["AWS Solutions Architect", "Google Analytics"],
    "raw_text": "Jane Smith\njane@example.com\n+1-555-1234\nSkills: Python, SQL, Machine Learning, Docker, React, FastAPI\nExperience: Software Engineer at TechCorp 2022-2024. Built APIs serving 10k+ users. Reduced latency by 40%.\nProjects: ML Pipeline, REST API\nEducation: B.Tech Computer Science 2022",
}

EMPTY_PROFILE = {
    "name": None, "email": None, "phone": None, "linkedin": None,
    "github": None, "skills": [], "experience": [], "projects": [],
    "education": [], "certifications": [], "raw_text": "John Doe",
}


class TestATSScorer:
    def test_score_in_range(self):
        result = calculate_ats_score(SAMPLE_PROFILE)
        assert 0 <= result["overall_score"] <= 100

    def test_strong_profile_scores_higher(self):
        strong = calculate_ats_score(SAMPLE_PROFILE)
        weak = calculate_ats_score(EMPTY_PROFILE)
        assert strong["overall_score"] > weak["overall_score"]

    def test_returns_suggestions(self):
        result = calculate_ats_score(EMPTY_PROFILE)
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0

    def test_returns_breakdown(self):
        result = calculate_ats_score(SAMPLE_PROFILE)
        assert "weighted_scores" in result
        assert "skills" in result["weighted_scores"]

    def test_returns_stats(self):
        result = calculate_ats_score(SAMPLE_PROFILE)
        assert result["stats"]["total_skills"] == 6
        assert result["stats"]["total_projects"] == 2

    def test_empty_profile_has_suggestions(self):
        result = calculate_ats_score(EMPTY_PROFILE)
        assert len(result["suggestions"]) >= 3

    def test_score_projects(self):
        score, _ = score_projects(SAMPLE_PROFILE)
        assert score > 0

        score_empty, suggestions = score_projects(EMPTY_PROFILE)
        assert score_empty == 0
        assert len(suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
