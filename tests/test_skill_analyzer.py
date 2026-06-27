"""Unit tests for Skill Analyzer."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.skill_analyzer import analyze_skill_gap, get_available_roles, get_role_info


class TestSkillAnalyzer:
    def test_get_available_roles(self):
        roles = get_available_roles()
        assert isinstance(roles, list)
        assert len(roles) >= 5
        assert "Software Engineer" in roles

    def test_valid_role_analysis(self):
        result = analyze_skill_gap(["Python", "SQL", "pandas", "scikit-learn"], "Data Analyst")
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "coverage" in result

    def test_coverage_in_range(self):
        result = analyze_skill_gap(["Python", "SQL"], "Data Analyst")
        coverage = result["coverage"]["overall"]
        assert 0 <= coverage <= 100

    def test_no_skills(self):
        result = analyze_skill_gap([], "Software Engineer")
        assert result["coverage"]["overall"] == 0
        assert len(result["missing_skills"]) > 0

    def test_all_skills_matched(self):
        role_data = get_role_info("Data Analyst")
        all_required = role_data["required_skills"]
        result = analyze_skill_gap(all_required, "Data Analyst")
        assert result["coverage"]["required"] >= 80

    def test_invalid_role_returns_error(self):
        result = analyze_skill_gap(["Python"], "Non Existent Role XYZ")
        assert "error" in result

    def test_priority_skills_returned(self):
        result = analyze_skill_gap(["Python"], "Data Scientist")
        assert isinstance(result.get("priority_skills"), list)

    def test_get_role_info(self):
        info = get_role_info("Software Engineer")
        assert info is not None
        assert "required_skills" in info
        assert len(info["required_skills"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
