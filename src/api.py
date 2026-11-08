"""Модуль для работы с API hh.ru (с фоллбэком на локальный JSON)."""
from __future__ import annotations

import json
import os
from typing import Any

import requests


class HHAPI:
    """Клиент для получения данных о работодателях и вакансиях с hh.ru."""

    BASE_URL = "https://api.hh.ru"
    LOCAL_FILE = "hh_vacancies.json"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self._use_local = False

    def _load_local_data(self) -> dict[str, Any]:
        """Загружает данные из локального JSON-файла."""
        if not os.path.exists(self.LOCAL_FILE):
            raise FileNotFoundError(f"Файл {self.LOCAL_FILE} не найден!")
        with open(self.LOCAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_employer(self, employer_id: int) -> dict:
        """Возвращает данные о работодателе по его id."""
        if not self._use_local:
            url = f"{self.BASE_URL}/employers/{employer_id}"
            try:
                r = requests.get(url, headers=self.headers, timeout=self.timeout)
                if r.status_code == 403:
                    self._use_local = True
                else:
                    r.raise_for_status()
                    return r.json()
            except requests.RequestException:
                self._use_local = True

        # Фоллбэк: ищем компанию среди вакансий в локальном файле
        data = self._load_local_data()
        for v in data.get("items", []):
            emp = v.get("employer", {})
            if str(emp.get("id")) == str(employer_id):
                return {
                    "id": int(emp.get("id")),
                    "name": emp.get("name"),
                    "alternate_url": emp.get("alternate_url", ""),
                    "open_vacancies": 1,
                }

        return {"id": employer_id, "name": f"Company_{employer_id}", "alternate_url": ""}

    def get_vacancies(self, employer_id: int) -> list[dict]:
        """Возвращает список вакансий работодателя."""
        if not self._use_local:
            url = f"{self.BASE_URL}/vacancies"
            params = {"employer_id": employer_id, "per_page": 100, "page": 0}
            try:
                r = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                if r.status_code == 403:
                    self._use_local = True
                else:
                    r.raise_for_status()
                    return r.json().get("items", [])
            except requests.RequestException:
                self._use_local = True

        # Фоллбэк: фильтруем вакансии из локального файла
        data = self._load_local_data()
        return [
            v for v in data.get("items", [])
            if str(v.get("employer", {}).get("id")) == str(employer_id)
        ]
