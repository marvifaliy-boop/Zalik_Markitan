import pandas as pd
from typing import List, Optional


class Employee: #свт. класу для всіх працівників ліцею(загальні атрибути та поліморфізм)
    def __init__(self, full_name: str, base_salary: float):
        self.full_name = full_name
        self.base_salary = base_salary
        self.salary: Optional[float] = None
        self.bonus: float = 0.0

    def calculate_salary(self) -> float:
        raise NotImplementedError


class Teacher(Employee): #вчитель успадковує Employee
    def __init__(self, full_name: str, base_salary: float, teaching_experience: int):
        super().__init__(full_name, base_salary)
        self.teaching_experience = teaching_experience

    def calculate_salary(self) -> float: #оброхування зп вчителів
        self.salary = self.base_salary * self.teaching_experience / 30.0
        return self.salary


class SecurityGuard(Employee): #охоронець так само успадковує Employee
    def __init__(self, full_name: str, base_salary: float, total_experience: int):
        super().__init__(full_name, base_salary)
        self.total_experience = total_experience

    def calculate_salary(self) -> float:# зп охоронця
        self.salary = self.base_salary + self.total_experience * 250.0
        return self.salary


class Director(Employee):  #директор також успадковує Employee
    def __init__(self, full_name: str, base_salary: float, teaching_experience: int, management_experience: int):
        super().__init__(full_name, base_salary)
        self.teaching_experience = teaching_experience
        self.management_experience = management_experience

    def calculate_salary(self) -> float: #розрахунок зп директора
        self.salary = (self.base_salary * self.teaching_experience / 50.0 +
                       self.management_experience * 500.0)
        return self.salary


class AccountingSystem:
    def __init__(self):
        self.employees: List[Employee] = []

    def initialize_employees(self):
        # Відновлений список працівників з твого оригінального коду
        print("2 сценарій. Робота із роботягами")

        director = Director("Шевченко Л.В.", 15000.0, teaching_experience=25, management_experience=10)

        t1 = Teacher("Бова С.М.", 12000.0, teaching_experience=15)
        t2 = Teacher("Дрібна Т.М.", 12000.0, teaching_experience=8)
        t3 = Teacher("Клунник О.С.", 12000.0, teaching_experience=2)
        guard = SecurityGuard("Стороженко Р.Р.", 11000.0, total_experience=5)

        self.employees.extend([director, t1, t2, t3, guard])
        print(f"  Кількість співробітників у системі: {len(self.employees)}")

    def run_salary_process(self):
        while True:
            try:
                val = input("\n Введіть суму бонусу у гривнях: ")
                bonus = float(val)
                if bonus < 0:
                    print(" Бонус не може бути меншим за нуль ")
                    continue
                break
            except ValueError:
                print(" Введіть нормальне число")

        records = []
        print("\n" + "=" * 60)
        print(f"{'ПІБ':<20} | {'Посада':<15} | {'Нараховано':<10}")
        print("=" * 60)

        for emp in self.employees:
            emp.bonus = bonus
            sal = emp.calculate_salary()
            total = sal + bonus

            print(f"{emp.full_name:<20} | {emp.__class__.__name__:<15} | {total:.2f} грн")

              records.append({
                "ПІБ": emp.full_name,
                "Посада": emp.__class__.__name__,
                "Ставка": emp.base_salary,
                "Бонус": bonus,
                "До видачі": round(total, 2)
              })

        pd.DataFrame(records).to_csv('salaries.csv', index=False, encoding='utf-8')
        print("=" * 60)
        print(f"  Дані збережено у файл salaries.csv")


if __name__ == "__main__":
    app = AccountingSystem()
    app.initialize_employees()
    app.run_salary_process()