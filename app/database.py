import sqlite3
import json
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from app.config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS management_fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_amount INTEGER,
                address_building TEXT,
                address_unit TEXT,
                address_area REAL,
                payment_deadline TEXT,
                electricity_kwh REAL,
                electricity_amount INTEGER,
                gas_kg REAL,
                gas_amount INTEGER,
                water_cbm REAL,
                water_amount INTEGER,
                heating_kwh REAL,
                heating_amount INTEGER,
                management_fee_details TEXT,
                utility_charges TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fee_id INTEGER,
                image_path TEXT,
                extracted_text TEXT,
                parsed_json TEXT,
                model_used TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (fee_id) REFERENCES management_fees(id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fees_date ON management_fees(date)
        """)


def insert_fee(fee_data: dict, raw_data: dict) -> int:
    init_db()
    now = datetime.now().isoformat()

    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO management_fees (
                date, total_amount, address_building, address_unit, address_area,
                payment_deadline, electricity_kwh, electricity_amount,
                gas_kg, gas_amount, water_cbm, water_amount,
                heating_kwh, heating_amount, management_fee_details, utility_charges, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fee_data.get("date"),
            fee_data.get("total_amount"),
            fee_data.get("address", {}).get("building"),
            fee_data.get("address", {}).get("unit"),
            fee_data.get("address", {}).get("area"),
            fee_data.get("payment_deadline"),
            fee_data.get("previous_year_comparison", {}).get("electricity", {}).get("current_month_usage"),
            fee_data.get("electricity_breakdown", {}).get("total"),
            fee_data.get("previous_year_comparison", {}).get("hot_water", {}).get("current_month_usage"),
            fee_data.get("heating_breakdown", {}).get("hot_water_usage"),
            fee_data.get("previous_year_comparison", {}).get("water", {}).get("current_month_usage"),
            fee_data.get("utility_charges", {}).get("household_water"),
            fee_data.get("previous_year_comparison", {}).get("heating", {}).get("current_month_usage"),
            fee_data.get("heating_breakdown", {}).get("total"),
            json.dumps(fee_data.get("management_fee_details", {})),
            json.dumps(fee_data.get("utility_charges", {})),
            now
        ))
        fee_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO raw_data (
                fee_id, image_path, extracted_text, parsed_json, model_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            fee_id,
            raw_data.get("image_path"),
            raw_data.get("extracted_text"),
            json.dumps(fee_data),
            raw_data.get("model_used"),
            now
        ))

        return fee_id


def get_all_fees():
    init_db()
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT id, date, total_amount, address_building, address_unit,
                   electricity_kwh, electricity_amount, gas_kg, gas_amount,
                   water_cbm, water_amount, heating_kwh, heating_amount, created_at
            FROM management_fees ORDER BY date DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_fee_by_id(fee_id: int) -> Optional[dict]:
    init_db()
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM management_fees WHERE id = ?", (fee_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


def get_raw_data_by_fee_id(fee_id: int) -> Optional[dict]:
    init_db()
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM raw_data WHERE fee_id = ?", (fee_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


def delete_fee(fee_id: int):
    init_db()
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM raw_data WHERE fee_id = ?", (fee_id,))
        cursor.execute("DELETE FROM management_fees WHERE id = ?", (fee_id,))