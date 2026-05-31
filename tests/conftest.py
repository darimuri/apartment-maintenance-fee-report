import pytest
import sys
import os
from pathlib import Path
import tempfile

# Create a conftest that sets up environment BEFORE any app modules are imported
# This ensures test environment variables are used

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment before any app imports."""
    # Set test environment variables
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_BASE_URL"] = "https://api.minimax.io/v1"
    os.environ["OPENAI_MODEL"] = "MiniMax-M2.7"

    # Create temp data dir
    temp_dir = tempfile.mkdtemp()
    os.environ["DATA_DIR"] = temp_dir
    os.environ["DB_PATH"] = os.path.join(temp_dir, "test.db")

    yield

    # Cleanup after all tests
    pass
