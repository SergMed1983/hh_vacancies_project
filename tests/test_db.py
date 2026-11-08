"""Тесты для проверки работы класса DBManager."""
import pytest
from dotenv import load_dotenv

from src.db_manager import DBManager

# Загружаем переменные окружения для тестов
load_dotenv()


@pytest.fixture
def db_manager() -> DBManager:
    """Фикстура для создания экземпляра DBManager."""
    return DBManager()


def test_get_companies_and_vacancies_count(db_manager: DBManager) -> None:
    """Проверяем, что метод возвращает список и в нем есть данные."""
    result = db_manager.get_companies_and_vacancies_count()
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0][0], str)
    assert isinstance(result[0][1], int)


def test_get_all_vacancies(db_manager: DBManager) -> None:
    """Проверяем, что метод возвращает список всех вакансий."""
    result = db_manager.get_all_vacancies()
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_avg_salary(db_manager: DBManager) -> None:
    """Проверяем, что средняя зарплата — это число больше нуля."""
    result = db_manager.get_avg_salary()
    assert isinstance(result, float)
    assert result > 0


def test_get_vacancies_with_higher_salary(db_manager: DBManager) -> None:
    """Проверяем фильтрацию по зарплате выше средней."""
    result = db_manager.get_vacancies_with_higher_salary()
    assert isinstance(result, list)


def test_get_vacancies_with_keyword(db_manager: DBManager) -> None:
    """Проверяем поиск по ключевому слову (LIKE)."""
    result = db_manager.get_vacancies_with_keyword("Python")
    assert isinstance(result, list)
    if len(result) > 0:
        assert "python" in result[0][0].lower()
