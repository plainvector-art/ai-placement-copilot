"""Unit tests for AI Settings, Dynamic Model Discovery, and Fallbacks."""
import pytest
import sys, os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_client import (
    get_gemini_api_key, get_openai_api_key,
    has_api_key, verify_gemini_connection,
    discover_gemini_models, get_best_available_model,
    verify_api_key, generate_embeddings
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
            sys.modules.pop('google.generativeai', None)

    def test_discover_gemini_models(self):
        mock_genai = MagicMock()
        m1 = MagicMock(supported_generation_methods=["generateContent"])
        m1.name = "models/gemini-1.5-flash"
        m2 = MagicMock(supported_generation_methods=["other"])
        m2.name = "models/unsupported-model"
        
        mock_genai.list_models.return_value = [m1, m2]
        
        sys.modules['google.generativeai'] = mock_genai
        try:
            models = discover_gemini_models("test-key")
            assert "gemini-1.5-flash" in models
            assert "unsupported-model" not in models
        finally:
            sys.modules.pop('google.generativeai', None)

    def test_get_best_available_model_priority(self):
        models = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
        best = get_best_available_model(models)
        # Priority order: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro
        assert best == "gemini-2.0-flash"

    @patch('backend.services.ai_client.get_gemini_api_key')
    @patch('backend.services.ai_client.get_openai_api_key')
    def test_generate_embeddings_local_fallback(self, mock_get_openai, mock_get_gemini):
        mock_get_gemini.return_value = ""
        mock_get_openai.return_value = ""
        
        # Should fall back to local hash-based generator rather than throwing ValueError
        vectors = generate_embeddings(["Test Text"])
        assert len(vectors) == 1
        assert len(vectors[0]) == 768
        assert isinstance(vectors[0][0], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
