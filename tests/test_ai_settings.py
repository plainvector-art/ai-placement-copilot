"""Unit tests for AI Settings and API Key Management."""
import pytest
import sys, os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_client import (
    get_gemini_api_key, get_openai_api_key,
    has_api_key, verify_gemini_connection
)


class TestAISettings:
    @patch('streamlit.session_state', {}, create=True)
    @patch('backend.services.ai_client.get_secret')
    def test_get_gemini_api_key_from_env(self, mock_get_secret):
        mock_get_secret.return_value = "env_gemini_key"
        key = get_gemini_api_key()
        assert key == "env_gemini_key"
        mock_get_secret.assert_called_with("GEMINI_API_KEY", "")

    @patch('backend.services.ai_client.get_secret')
    def test_get_gemini_api_key_from_session_state(self, mock_get_secret):
        session_state = {"gemini_api_key": "session_gemini_key"}
        with patch('streamlit.session_state', session_state, create=True):
            key = get_gemini_api_key()
            assert key == "session_gemini_key"
            mock_get_secret.assert_not_called()

    @patch('streamlit.session_state', {}, create=True)
    @patch('backend.services.ai_client.get_secret')
    def test_get_openai_api_key_from_env(self, mock_get_secret):
        mock_get_secret.return_value = "env_openai_key"
        key = get_openai_api_key()
        assert key == "env_openai_key"
        mock_get_secret.assert_called_with("OPENAI_API_KEY", "")

    @patch('backend.services.ai_client.get_secret')
    def test_get_openai_api_key_from_session_state(self, mock_get_secret):
        session_state = {"openai_api_key": "session_openai_key"}
        with patch('streamlit.session_state', session_state, create=True):
            key = get_openai_api_key()
            assert key == "session_openai_key"
            mock_get_secret.assert_not_called()

    @patch('streamlit.session_state', {}, create=True)
    @patch('backend.services.ai_client.get_secret')
    def test_has_api_key_false(self, mock_get_secret):
        mock_get_secret.return_value = ""
        assert not has_api_key()

    @patch('backend.services.ai_client.get_secret')
    def test_has_api_key_true(self, mock_get_secret):
        session_state = {"gemini_api_key": "test_key"}
        with patch('streamlit.session_state', session_state, create=True):
            assert has_api_key()

    def test_verify_gemini_connection_empty(self):
        success, msg = verify_gemini_connection("")
        assert not success
        assert "empty" in msg.lower()

    def test_verify_gemini_connection_success(self):
        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_model.generate_content.return_value = MagicMock(text="Pong")
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Inject mock into sys.modules
        sys.modules['google.generativeai'] = mock_genai
        try:
            success, msg = verify_gemini_connection("AIzaSyValidKey")
            assert success
            assert "connected successfully" in msg.lower()
            mock_genai.configure.assert_called_once_with(api_key="AIzaSyValidKey")
        finally:
            # Clean up sys.modules
            sys.modules.pop('google.generativeai', None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
