"""Unit tests verifying production hardening features (Indian resume support, Circuit Breakers, Lazy DB, and ATS scoring)."""
import pytest
import sys, os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.resume_parser import extract_phone, _extract_gpa, _extract_backlogs, _detect_indian_education_metadata
from backend.services.ats_scorer import score_skills
from backend.services.ai_client import CircuitBreaker, validate_schema
from backend.database.db import get_db, init_db


class TestIndianResumeSupport:
    def test_indian_phone_number_extraction(self):
        assert extract_phone("My phone number is +91-9876543210") == "+91-9876543210"
        assert extract_phone("Contact: 9876543210") == "9876543210"
        assert extract_phone("Reach out at 07777777777") == "07777777777"

    def test_indian_cgpa_and_percentage_extraction(self):
        assert _extract_gpa("Graduated with 8.5 CGPA") == "8.5/10"
        assert _extract_gpa("Secured 85.5% in high school") == "85.5%"
        assert _extract_gpa("GPA was 9.4/10.0") == "9.4/10"
        assert _extract_gpa("Pointer: 7.8") == "7.8/10"

    def test_backlogs_detection(self):
        assert _extract_backlogs("No active backlogs or KTs.") == 0
        assert _extract_backlogs("Have 2 active backlogs from sem 3.") == 2
        assert _extract_backlogs("Cleared all prior KTs.") == 0
        assert _extract_backlogs("History of 1 backlog.") == 1

    def test_indian_education_metadata(self):
        meta = _detect_indian_education_metadata("Studied at Anna University under CBSE board in India.")
        assert "CBSE" in meta["boards"]
        assert "ANNA UNIVERSITY" in meta["universities"]
        assert meta["is_indian_context"]


class TestCircuitBreaker:
    def test_circuit_breaker_flow(self):
        cb = CircuitBreaker("TestBreaker", failure_threshold=2, recovery_time=0.5)
        assert cb.can_execute()
        
        # Record failures
        cb.record_failure()
        assert cb.can_execute()
        
        cb.record_failure()
        # Breaker should open now
        assert not cb.can_execute()
        
        # Success should reset it but we can't execute to try until recovery time or explicitly reset
        import time
        time.sleep(0.6)
        # Should be HALF-OPEN now, allowing execution
        assert cb.can_execute()
        cb.record_success()
        assert cb.state == "CLOSED"


class TestSchemaValidation:
    def test_validate_schema_correctness(self):
        schema = {
            "name": str,
            "skills": list,
            "score": int
        }
        valid_data = {
            "name": "Alex",
            "skills": ["python"],
            "score": 95
        }
        invalid_data = {
            "name": "Alex",
            "skills": "python", # should be list
            "score": 95
        }
        assert validate_schema(valid_data, schema)
        assert not validate_schema(invalid_data, schema)


class TestATSScoringUpgrades:
    def test_role_specific_skill_scoring(self):
        profile = {
            "skills": ["Python", "SQL", "Git"]
        }
        # software engineer expects Python, Java, C++, JS, TS, Git, SQL
        score, suggestions = score_skills(profile, "Software Engineer")
        assert score < 100
        assert any("Software Engineer" in sug for sug in suggestions)


class TestLazyDBInitialization:
    def test_lazy_db_engine_setup(self):
        # Trigger explicit startup DB setup or first session acquisition
        init_db()
        generator = get_db()
        db_session = next(generator)
        assert db_session is not None
        db_session.close()


class TestSecurity:
    def test_upload_restrictions(self):
        from backend.utils.file_handler import save_uploaded_file
        # Test oversized file (11MB)
        with pytest.raises(ValueError) as excinfo:
            save_uploaded_file(b"a" * (11 * 1024 * 1024), "test.pdf")
        assert "exceeds the maximum limit" in str(excinfo.value)

        # Test invalid suffix
        with pytest.raises(ValueError) as excinfo:
            save_uploaded_file(b"dummy content", "test.exe")
        assert "Unsupported file format" in str(excinfo.value)

