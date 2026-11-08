"""Модуль для создания базы данных и таблиц."""
from __future__ import annotations

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()


class DatabaseCreator:
    """Класс для автоматического создания БД и таблиц."""

    def __init__(self) -> None:
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.dbname = os.getenv("DB_NAME", "hh_vacancies")

    def create_database(self) -> None:
        """Создает базу данных, если её еще нет."""
        # Подключаемся к стандартной базе postgres, чтобы создать новую
        conn = psycopg2.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.dbname}'")
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE "{self.dbname}"')
                print(f"✅ База данных {self.dbname} успешно создана.")
            else:
                print(f"ℹ️ База данных {self.dbname} уже существует.")
        conn.close()

    def create_tables(self) -> None:
        """Создает таблицы employers и vacancies."""
        conn = psycopg2.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, dbname=self.dbname,
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        employer_id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url VARCHAR(255),
                        open_vacancies INTEGER DEFAULT 0
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        vacancy_id SERIAL PRIMARY KEY,
                        employer_id INTEGER NOT NULL REFERENCES employers(employer_id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(255),
                        published_at DATE
                    );
                """)
        conn.close()
        print("✅ Таблицы employers и vacancies успешно созданы.")
