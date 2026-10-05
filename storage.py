"""
Хранилище результатов анализов в SQLite.
Простое, без ORM — для прототипа.
"""

import sqlite3
import json
import secrets
import string
from pathlib import Path
from datetime import datetime


# Файл базы лежит рядом со storage.py
DB_PATH = Path(__file__).parent / "patients.db"


# Алфавит для генерации ID.
# Исключаем 0, O, 1, I, l — чтобы не путать при чтении вслух.
ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def _get_connection():
    """Открывает соединение с базой. Создаёт таблицу, если её нет."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def generate_patient_id(length: int = 6) -> str:
    """
    Генерирует короткий ID, например 'K7M3PQ'.
    Проверяет, что такого ID ещё нет в базе — если есть, генерирует новый.
    """
    conn = _get_connection()
    try:
        while True:
            code = "".join(secrets.choice(ALPHABET) for _ in range(length))
            row = conn.execute(
                "SELECT 1 FROM patients WHERE patient_id = ?", (code,)
            ).fetchone()
            if row is None:
                return code
    finally:
        conn.close()


def save_patient(result: dict) -> str:
    """
    Сохраняет результат анализа в базу.
    Возвращает сгенерированный ID.
    """
    patient_id = generate_patient_id()
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO patients (patient_id, result_json, created_at) VALUES (?, ?, ?)",
            (patient_id, json.dumps(result, ensure_ascii=False), datetime.utcnow().isoformat()),
        )
        conn.commit()
        return patient_id
    finally:
        conn.close()


def get_patient(patient_id: str) -> dict | None:
    """
    Возвращает результат по ID или None, если не найден.
    ID нормализуем: убираем пробелы, переводим в верхний регистр.
    """
    if not patient_id:
        return None
    code = patient_id.strip().upper().replace(" ", "").replace("-", "")

    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT result_json, created_at FROM patients WHERE patient_id = ?",
            (code,),
        ).fetchone()
        if row is None:
            return None
        return {
            "patient_id": code,
            "result": json.loads(row[0]),
            "created_at": row[1],
        }
    finally:
        conn.close()


def count_patients() -> int:
    """Сколько всего записей в базе. Для отладки."""
    conn = _get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) FROM patients").fetchone()
        return row[0] if row else 0
    finally:
        conn.close()
