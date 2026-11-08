"""Точка входа в программу (консольный интерфейс)."""
from __future__ import annotations

from src.db_manager import DBManager


def print_rows(title: str, rows: list) -> None:
    """Печатает строки в человекочитаемом виде."""
    print(f"\n=== {title} ===")
    if not rows:
        print("Нет данных.")
        return
    for i, row in enumerate(rows, 1):
        print(f"{i}. {row}")


def user_interaction() -> None:
    """Интерфейс взаимодействия с пользователем."""
    db = DBManager()

    while True:
        print("\n" + "=" * 40)
        print("Выберите действие:")
        print("1 — Компании и количество вакансий")
        print("2 — Все вакансии")
        print("3 — Средняя зарплата")
        print("4 — Вакансии с зарплатой выше средней")
        print("5 — Поиск вакансий по ключевому слову")
        print("0 — Выход")
        print("=" * 40)
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            print_rows("Компании и количество вакансий", db.get_companies_and_vacancies_count())
        elif choice == "2":
            print_rows("Все вакансии", db.get_all_vacancies())
        elif choice == "3":
            print(f"\nСредняя зарплата: {db.get_avg_salary():.2f} руб.")
        elif choice == "4":
            print_rows("Вакансии с зарплатой выше средней", db.get_vacancies_with_higher_salary())
        elif choice == "5":
            kw = input("Введите ключевое слово (например, Python): ").strip()
            print_rows(f"Вакансии по слову '{kw}'", db.get_vacancies_with_keyword(kw))
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    user_interaction()
