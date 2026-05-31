import pytest
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import tempfile
import os
import sys

# Create temp dir before any imports
temp_dir = tempfile.mkdtemp()


@pytest.fixture
def temp_db(tmp_path):
    """Create a temp database for testing."""
    db_path = tmp_path / "test.db"
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)

    # Set env vars before importing app modules
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_BASE_URL"] = "https://api.minimax.io/v1"
    os.environ["OPENAI_MODEL"] = "MiniMax-M2.7"
    os.environ["DATA_DIR"] = str(data_dir)
    os.environ["DB_PATH"] = str(db_path)

    # Reload app.config to use test paths
    if "app.config" in sys.modules:
        del sys.modules["app.config"]
    if "app.database" in sys.modules:
        del sys.modules["app.database"]

    import app.config
    app.config.DATA_DIR = data_dir
    app.config.DB_PATH = str(db_path)
    app.config.UPLOAD_DIR = data_dir / "uploads"
    app.config.UPLOAD_DIR.mkdir(exist_ok=True)

    from app.database import init_db, insert_fee, get_all_fees, get_fee_by_id, get_raw_data_by_fee_id, delete_fee

    # Init the test database
    init_db()

    return {
        "db_path": db_path,
        "init_db": init_db,
        "insert_fee": insert_fee,
        "get_all_fees": get_all_fees,
        "get_fee_by_id": get_fee_by_id,
        "get_raw_data_by_fee_id": get_raw_data_by_fee_id,
        "delete_fee": delete_fee,
    }


class TestDatabaseSchema:
    def test_init_db_creates_tables(self, temp_db):
        """init_db should create management_fees and raw_data tables."""
        conn = sqlite3.connect(temp_db["db_path"])
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('management_fees', 'raw_data')
        """)
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert "management_fees" in tables
        assert "raw_data" in tables

    def test_init_db_creates_index(self, temp_db):
        """init_db should create idx_fees_date index."""
        conn = sqlite3.connect(temp_db["db_path"])
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name = 'idx_fees_date'
        """)
        index = cursor.fetchone()
        conn.close()

        assert index is not None


class TestInsertFee:
    def test_insert_fee_returns_fee_id(self, temp_db):
        """insert_fee should return the ID of the inserted fee."""
        fee_data = {
            "date": "2024년 01월분",
            "total_amount": 50000,
            "address": {"building": "101동", "unit": "1001호", "area": 84.5},
            "payment_deadline": "2024-01-25",
            "previous_year_comparison": {
                "electricity": {"current_month_usage": 150}
            },
            "electricity_breakdown": {"total": 30000},
            "heating_breakdown": {"hot_water_usage": 5, "total": 20000},
            "utility_charges": {"household_water": 5000, "수도": 10000},
            "management_fee_details": {"청소비": 10000},
        }
        raw_data = {
            "image_path": "/tmp/test.jpg",
            "extracted_text": "test text",
            "model_used": "test-model",
        }

        fee_id = temp_db["insert_fee"](fee_data, raw_data)

        assert fee_id is not None
        assert isinstance(fee_id, int)
        assert fee_id > 0

    def test_insert_fee_stores_raw_data(self, temp_db):
        """insert_fee should store raw_data linked to fee."""
        fee_data = {
            "date": "2024년 01월분",
            "total_amount": 50000,
 }
        raw_data = {
            "image_path": "/tmp/test.jpg",
            "extracted_text": "extracted text content",
            "model_used": "qwen-model",
        }

        fee_id = temp_db["insert_fee"](fee_data, raw_data)

        conn = sqlite3.connect(temp_db["db_path"])
        cursor = conn.cursor()
        cursor.execute("SELECT image_path, extracted_text, model_used FROM raw_data WHERE fee_id = ?", (fee_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "/tmp/test.jpg"
        assert row[1] == "extracted text content"
        assert row[2] == "qwen-model"


class TestGetAllFees:
    def test_get_all_fees_returns_list(self, temp_db):
        """get_all_fees should return a list."""
        fees = temp_db["get_all_fees"]()
        assert isinstance(fees, list)

    def test_get_all_fees_empty_when_no_data(self, temp_db):
        """get_all_fees should return empty list when no fees stored."""
        fees = temp_db["get_all_fees"]()
        assert fees == []


class TestGetFeeById:
    def test_get_fee_by_id_returns_none_for_nonexistent(self, temp_db):
        """get_fee_by_id should return None for non-existent ID."""
        result = temp_db["get_fee_by_id"](9999)
        assert result is None


class TestDeleteFee:
    def test_delete_fee_removes_fee(self, temp_db):
        """delete_fee should remove the fee and its raw_data."""
        fee_data = {
            "date": "2024년 01월분",
            "total_amount": 50000,
        }
        raw_data = {
            "image_path": "/tmp/test.jpg",
            "extracted_text": "test",
            "model_used": "model",
        }

        fee_id = temp_db["insert_fee"](fee_data, raw_data)
        temp_db["delete_fee"](fee_id)

        fee = temp_db["get_fee_by_id"](fee_id)
        raw = temp_db["get_raw_data_by_fee_id"](fee_id)

        assert fee is None
        assert raw is None


class TestGetRawDataByFeeId:
    def test_get_raw_data_by_fee_id_returns_none_for_nonexistent(self, temp_db):
        """get_raw_data_by_fee_id should return None for non-existent fee_id."""
        result = temp_db["get_raw_data_by_fee_id"](9999)
        assert result is None
