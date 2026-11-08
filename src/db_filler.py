"""Модуль для заполнения базы данных."""
from __future__ import annotations

import os

import psycopg2
from dotenv import load_dotenv

from src.api import HHAPI

load_dotenv()


class DBFiller:
    """Класс для заполнения БД данными о компаниях и вакансиях."""

    def __init__(self, api: HHAPI) -> None:
        self.api = api
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.dbname = os.getenv("DB_NAME", "hh_vacancies")

    def _connect(self):
        return psycopg2.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, dbname=self.dbname,
        )

    def fill_employers(self, ids: list[int]) -> None:
        """Заполняет таблицу employers."""
        conn = self._connect()
        with conn:
            with conn.cursor() as cur:
                for emp_id in ids:
                    try:
                        data = self.api.get_employer(emp_id)
                    except Exception as e:
                        print(f"Ошибка при получении компании {emp_id}: {e}")
                        continue
                    cur.execute("""
                        INSERT INTO employers (employer_id, name, url, open_vacancies)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (employer_id) DO NOTHING;
                    """, (data["id"], data["name"],
                          data.get("alternate_url", ""), data.get("open_vacancies", 0)))
        conn.close()
        print("✅ Данные о работодателях добавлены в БД.")

    def fill_vacancies(self, ids: list[int]) -> None:
        """Заполняет таблицу vacancies."""
        conn = self._connect()
        with conn:
            with conn.cursor() as cur:
                for emp_id in ids:
                    try:
                        vacancies = self.api.get_vacancies(emp_id)
                    except Exception as e:
                        print(f"Ошибка при получении вакансий {emp_id}: {e}")
                        continue
                    for v in vacancies:
                        salary = v.get("salary") or {}
                        # Берем дату публикации (первые 10 символов, формат YYYY-MM-DD)
                        pub_date = v.get("published_at", "")[:10] or None

                        cur.execute("""
                            INSERT INTO vacancies
                                (employer_id, name, salary_from, salary_to, currency, url, published_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            emp_id,
                            v.get("name", "Без названия"),
                            salary.get("from"),
                            salary.get("to"),
                            salary.get("currency"),
                            v.get("alternate_url", ""),
                            pub_date
                        ))
        conn.close()
        print("✅ Данные о вакансиях добавлены в БД.")
