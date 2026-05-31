import pytest
import sys
from pathlib import Path
import tempfile
import os

# Create temp dir and set env BEFORE importing app modules
temp_dir = tempfile.mkdtemp()
os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_BASE_URL"] = "https://api.minimax.io/v1"
os.environ["OPENAI_MODEL"] = "MiniMax-M2.7"

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOCRService:
    def test_extract_text_raises_error_without_api_key(self, monkeypatch):
        """extract_text should raise ValueError when API key is not set."""
        # Reload modules with cleared API key
        if "app.services.ocr_service" in sys.modules:
            del sys.modules["app.services.ocr_service"]
        if "app.config" in sys.modules:
            del sys.modules["app.config"]

        monkeypatch.setenv("OPENROUTER_API_KEY", "")

        from app.services.ocr_service import OCRService

        ocr = OCRService()
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            ocr.extract_text("/tmp/nonexistent.jpg")

    def test_ocr_service_initialization(self, monkeypatch):
        """OCRService should initialize with config values."""
        # Reload modules with test API key
        if "app.services.ocr_service" in sys.modules:
            del sys.modules["app.services.ocr_service"]
        if "app.config" in sys.modules:
            del sys.modules["app.config"]

        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        monkeypatch.setenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
        monkeypatch.setenv("OPENROUTER_MODEL", "qwen/qwen3-vl-32b-instruct")

        from app.services.ocr_service import OCRService

        ocr = OCRService()
        assert ocr.api_key == "test-key"
        assert ocr.api_url == "https://openrouter.ai/api/v1/chat/completions"
        assert ocr.model == "qwen/qwen3-vl-32b-instruct"

    def test_ocr_service_has_extract_text_method(self):
        """OCRService should have extract_text method."""
        from app.services.ocr_service import OCRService

        ocr = OCRService()
        assert hasattr(ocr, "extract_text")
        assert callable(ocr.extract_text)
