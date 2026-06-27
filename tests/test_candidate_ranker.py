"""Unit tests for Intelligent Candidate Ranker features."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.signal_scorer import compute_signals, fuse_scores
from backend.services.explainability import explain_rank
from backend.services.semantic_ranker import build_candidate_text, rank_candidates
from backend.services.jd_parser import parse_job_description
from backend.services.recruiter_insights import generate_candidate_insights


SAMPLE_CANDIDATE_1 = {
    "name": "Alice Developer",
    "skills": ["Python", "FastAPI", "Docker", "SQL"],
    "projects": [
        {"title": "E-commerce Backend", "description": "Built using FastAPI and PostgreSQL", "technologies": ["FastAPI", "PostgreSQL"]},
        {"title": "Portfolio Web", "description": "Simple static page", "technologies": []}
    ],
    "summary": "Experienced Backend Developer specialized in API design.",
    "raw_text": "Alice Developer\nalice@example.com\nSkills: Python, FastAPI, Docker, SQL. Developed e-commerce backend achieving 99.9% uptime. 3+ years experience.",
    "github": "github.com/alicedev",
    "linkedin": "linkedin.com/in/alicedev",
    "certifications": ["AWS Certified Cloud Practitioner"]
}

SAMPLE_CANDIDATE_2 = {
    "name": "Bob Analyst",
    "skills": ["SQL", "Excel", "Tableau"],
    "projects": [],
    "summary": "Junior Data Analyst.",
    "raw_text": "Bob Analyst\nbob@example.com\nSkills: SQL, Excel, Tableau. Worked on data analysis tasks.",
    "github": "",
    "linkedin": "linkedin.com/in/bobanalyst",
    "certifications": []
}


class TestSignalScorer:
    def test_compute_signals_alice(self):
        signals = compute_signals(SAMPLE_CANDIDATE_1)
        assert signals["github_present"] is True
        assert signals["linkedin_present"] is True
        assert signals["project_count"] == 2
        # Project 1 has desc and tech (20 pts). Project 2 has no techs. So project_depth_score should be 20
        assert signals["project_depth_score"] == 20.0
        # 4 skills -> skills_breadth_score = 20.0
        assert signals["skills_breadth_score"] == 20.0
        # 99.9% -> 1 match -> quantification_score = 30.0
        assert signals["quantification_score"] == 30.0
        # 1 cert -> certifications_score = 40.0
        assert signals["certifications_score"] == 40.0
        # Weighted composite score
        expected_composite = round(20 * 0.3 + 20 * 0.25 + 30 * 0.25 + 40 * 0.2, 1)
        assert signals["composite_signal_score"] == expected_composite

    def test_compute_signals_bob(self):
        signals = compute_signals(SAMPLE_CANDIDATE_2)
        assert signals["github_present"] is False
        assert signals["linkedin_present"] is True
        assert signals["project_count"] == 0
        assert signals["project_depth_score"] == 0.0
        assert signals["skills_breadth_score"] == 20.0
        assert signals["quantification_score"] == 0.0
        assert signals["certifications_score"] == 0.0
        assert signals["composite_signal_score"] == 5.0  # 20 * 0.25 = 5.0

    def test_fuse_scores(self):
        fused = fuse_scores(semantic_score=80.0, ats_score=70.0, signal_score=60.0)
        assert fused["final_score"] == round(80.0 * 0.5 + 70.0 * 0.3 + 60.0 * 0.2, 1)
        assert fused["semantic_score"] == 80.0
        assert fused["ats_score"] == 70.0
        assert fused["signal_score"] == 60.0
        assert fused["score_breakdown"]["Semantic fit"] == 40.0
        assert fused["score_breakdown"]["ATS quality"] == 21.0
        assert fused["score_breakdown"]["Behavioral signals"] == 12.0


class TestExplainability:
    def test_explain_rank(self):
        signals = compute_signals(SAMPLE_CANDIDATE_1)
        scores = fuse_scores(semantic_score=80.0, ats_score=70.0, signal_score=60.0)
        explanation = explain_rank(
            SAMPLE_CANDIDATE_1,
            signals,
            scores,
            jd_parsed={"role_title": "Python Developer"},
            rank=1
        )
        assert explanation["rank"] == 1
        assert explanation["candidate_name"] == "Alice Developer"
        assert explanation["final_score"] == scores["final_score"]
        assert "Strong semantic alignment with the job description" in explanation["strengths"]
        assert "Active GitHub profile — verifiable code portfolio" in explanation["strengths"]
        assert explanation["recruiter_verdict"] in ["Strong shortlist", "Consider", "Deprioritise"]


class TestSemanticRanker:
    def test_build_candidate_text(self):
        text = build_candidate_text(SAMPLE_CANDIDATE_1)
        assert "Alice Developer" in text
        assert "Python" in text
        assert "E-commerce Backend" in text
        assert "99.9%" in text

    def test_rank_candidates_empty(self):
        assert rank_candidates([], "Python Developer") == []


class TestRecruiterInsights:
    def test_generate_candidate_insights(self):
        scores = fuse_scores(semantic_score=80.0, ats_score=70.0, signal_score=60.0)
        insights = generate_candidate_insights(
            SAMPLE_CANDIDATE_1,
            scores,
            jd_parsed={"role_title": "Python Developer", "required_skills": ["Python", "FastAPI"], "domain": "Backend"}
        )
        assert "fit_analysis" in insights
        assert "technical_vetting_points" in insights
        assert "suggested_interview_questions" in insights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
