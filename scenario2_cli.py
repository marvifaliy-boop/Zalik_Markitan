# scenario2_cli.py (використовує school_entities.py)

import pandas as pd
from school_entities import Director, Teacher, Guard, Employee
from typing import List
import sys


def scenario_2_run():
    """Сценарій 2. Керування зарплатами працівників школи (CLI)."""
    print("\n" + "=" * 50)
    print("--- Сценарій 2: Керування зарплатами працівників школи (CLI) ---")
    print("=" * 50 + "\n")

    # 1. Створіть програмно об’єкти різних працівників
    employees: List[Employee] = [
        Director(
            last_name="Шевченко",
            first_name="Лариса",
            patronymic="Вікторівна",
            base_salary=15000.0,
            pedagogical_experience=25,
            management_experience=10
        ),
        Teacher(
            last_name="Бова",
            first_name="Сергій",
            patronymic="Миколайович",
            base_salary=12000.0,
            pedagogical_experience=15
        ),
        Teacher(
            last_name="Дрібна",
            first_name="Тетяна",
            patronymic="Михайлівна",
            base_salary=12000.0,
            pedagogical_experience=8
        ),
        Teacher(
            last_name="Клунник",
            first_name="Ольга",
            patronymic="Сергіївна",
            base_salary=12000.0,
            pedagogical_experience=2
        ),
        Guard(
            last_name="Стороженко",
            first_name="Роман",
            patronymic="Романович",
            base_salary=11000.0,
            general_experience=5
        )
    ]

    print("✅ Об'єкти працівників створено.")

    # 2. Розрахунок зарплати
    salary_data = []
    print("\n💰 Розрахунок зарплат...")

    for emp in employees:
        emp.calculate_salary()  # Виклик поліморфного методу

        data = {
            'Посада': emp.position,
            'ПІБ': f"{emp.last_name} {emp.first_name[0]}.{emp.patronymic[0]}.",
            'Базова Ставка': emp.base_salary,
            'Розрахована Зарплата': emp.salary,
            # Отримання специфічних полів
            'Педагогічний Стаж': getattr(emp, 'pedagogical_experience', None),
            'Стаж Керування': getattr(emp, 'management_experience', None),
            'Загальний Досвід': getattr(emp, 'general_experience', None)
        }
        salary_data.append(data)

    print("✅ Розрахунок завершено.")

    # Виведення результату у командний рядок (таблиця)
    df_salaries = pd.DataFrame(salary_data).fillna('')

    print("\n" + "-" * 50)
    print("--- Таблиця Розрахованих Зарплат ---")
    # Використовуємо to_markdown для гарного виводу в консоль
    print(df_salaries.to_markdown(index=False, floatfmt=".2f"))
    print("-" * 50)

    # 3. Збережіть таблицю розрахованих зарплат у файл CSV.
    output_file = "employee_salaries_calculated.csv"
    df_salaries.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Таблицю збережено у файл: {output_file}")


if __name__ == "__main__":
    scenario_2_run()