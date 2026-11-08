"""Модуль с классом DBManager для аналитики по вакансиям."""
from __future__ import annotations

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DBManager:
    """Класс для аналитических запросов к БД с вакансиями."""

    def __init__(self) -> None:
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.dbname = os.getenv("DB_NAME", "hh_vacancies")

    def _connect(self):
        """Вспомогательный метод для подключения к БД."""
        return psycopg2.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, dbname=self.dbname,
        )

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """Список компаний и количество вакансий у каждой (через JOIN)."""
        query = """
            SELECT e.name, COUNT(v.vacancy_id) AS vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancies_count DESC;
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
        conn.close()
        return result

    def get_all_vacancies(self) -> list[tuple]:
        """Все вакансии: компания, название, зарплата, ссылка (через JOIN)."""
        query = """
            SELECT e.name, v.name,
                   COALESCE(v.salary_from, 0) AS salary_from,
                   COALESCE(v.salary_to, 0) AS salary_to,
                   v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id;
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
        conn.close()
        return result

    def get_avg_salary(self) -> float:
        """Средняя зарплата по вакансиям (через AVG)."""
        query = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] is not None else 0.0

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        """Вакансии с зарплатой выше средней (через WHERE)."""
        query = """
            SELECT v.name, e.name,
                   (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 AS avg_salary
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 > (
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            )
            ORDER BY avg_salary DESC;
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
        conn.close()
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple]:
        """Вакансии, в названии которых есть слово (через LIKE/ILIKE)."""
        query = """
            SELECT v.name, e.name
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.name ILIKE %s;
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query, (f"%{keyword}%",))
            result = cur.fetchall()
        conn.close()
        return result
