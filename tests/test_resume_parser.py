"""
Unit tests for Resume Parser.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.resume_parser import (
    extract_email, extract_phone, extract_skills,
    extract_name, _extract_gpa, _extract_year
)


class TestExtractEmail:
    def test_valid_email(self):
        text = "John Doe\njohn.doe@gmail.com\n+1-555-1234"
        assert extract_email(text) == "john.doe@gmail.com"

    def test_no_email(self):
        text = "No email here"
        assert extract_email(text) is None

    def test_complex_email(self):
        text = "Contact: j.doe+work@company.co.uk"
        email = extract_email(text)
        assert email is not None
        assert "@" in email


class TestExtractPhone:
    def test_standard_phone(self):
        text = "Phone: +1-555-867-5309"
        result = extract_phone(text)
        assert result is not None

    def test_no_phone(self):
        text = "No phone here, just text"
        # May or may not extract — ensure no crash
        result = extract_phone(text)
        assert result is None or isinstance(result, str)


class TestExtractSkills:
    def test_python_detected(self):
        text = "Skills: Python, SQL, Machine Learning, React"
        skills = extract_skills(text)
        assert any("python" in s.lower() for s in skills)

    def test_sql_detected(self):
        text = "Experience with SQL databases and MongoDB"
        skills = extract_skills(text)
        assert any("sql" in s.lower() for s in skills)

    def test_empty_text(self):
        skills = extract_skills("")
        assert isinstance(skills, list)

    def test_multiple_skills(self):
        text = "Python, JavaScript, Docker, Kubernetes, AWS, React, SQL, TensorFlow"
        skills = extract_skills(text)
        assert len(skills) >= 4


class TestExtractGPA:
    def test_valid_gpa(self):
        assert _extract_gpa("GPA: 3.8/4.0") == "3.8"

    def test_no_gpa(self):
        assert _extract_gpa("No GPA here") is None

    def test_cgpa(self):
        assert _extract_gpa("CGPA: 9.2/10") is None  # > 4.0 not extracted


class TestExtractYear:
    def test_year_found(self):
        assert _extract_year("Graduated 2022") == "2022"

    def test_no_year(self):
        assert _extract_year("No year mentioned") is None


class TestExtractName:
    def test_simple_name(self):
        text = "John Doe\njohn@email.com\n+1-555-1234"
        name = extract_name(text)
        assert name is not None

    def test_no_crash_empty(self):
        name = extract_name("")
        assert name is None or isinstance(name, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
