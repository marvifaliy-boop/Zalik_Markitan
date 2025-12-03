# school_entities.py

from dataclasses import dataclass, field
from typing import List, Optional
import csv


# --- Сутності ---

@dataclass
class Student:
    """Сутність Учень."""
    last_name: str
    first_name: str
    patronymic: str
    birth_year: int
    gender: str  # 'Хлопець' або 'Дівчина'
    average_grade: float

    def __str__(self):
        return f"{self.last_name} {self.first_name[0]}. - {self.birth_year}, Сер.Оц.: {self.average_grade}"


@dataclass
class SchoolClass:
    """Сутність Клас."""
    parallel: int  # Паралель (1-11)
    vertical: str  # Вертикаль (А, Б, В...)
    students: List[Student] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Назва класу (наприклад, '7А')."""
        return f"{self.parallel}{self.vertical}"

    @property
    def student_count(self) -> int:
        """Кількість учнів у класі."""
        return len(self.students)

    def next_year(self):
        """Переводить клас на наступну паралель."""
        self.parallel += 1
        print(f"Клас {self.name} переведено до {self.parallel}{self.vertical}")


@dataclass
class Employee:
    """Базовий клас для Працівника."""
    last_name: str
    first_name: str
    patronymic: str
    base_salary: float
    position: str = "Працівник"
    salary: Optional[float] = None

    def calculate_salary(self):
        """Метод для розрахунку зарплати (буде перевизначено)."""
        self.salary = self.base_salary
        return self.salary

    def __str__(self):
        return f"{self.position}: {self.last_name} {self.first_name[0]}. {self.patronymic[0]}. - ЗП: {self.salary if self.salary is not None else 'Не розраховано'}"



class Teacher(Employee):
    """Сутність Вчитель."""
    pedagogical_experience: int  # Педагогічний стаж у роках
    position: str = "Вчитель"

    def calculate_salary(self):
        """Розрахунок ЗП для вчителя: базова ставка * пед. стаж / 30."""
        # Умова: Вчитель: зарплата=базова ставка * педагогічний стаж / 30
        if self.pedagogical_experience == 0:
            self.salary = self.base_salary  # Базова, якщо стаж 0
        else:
            self.salary = self.base_salary * self.pedagogical_experience / 30
        self.salary = round(self.salary, 2)
        return self.salary



class Director(Teacher):
    """Сутність Директор (наслідує Вчителя)."""
    management_experience: int  # Стаж керування у роках
    position: str = "Директор"

    def calculate_salary(self):
        """Розрахунок ЗП для директора: базова * пед. стаж / 50 + стаж керування * 500."""
        # Умова: Директор: зарплата = базова ставка * педагогічний стаж / 50 + стаж керування * 500
        ped_part = self.base_salary * self.pedagogical_experience / 50
        mgmt_part = self.management_experience * 500
        self.salary = ped_part + mgmt_part
        self.salary = round(self.salary, 2)
        return self.salary



class Guard(Employee):
    """Сутність Охоронець."""
    general_experience: int  # Загальний досвід роботи у роках
    position: str = "Охоронець"

    def calculate_salary(self):
        """Розрахунок ЗП для охоронця: базова ставка + загальний досвід * 250."""
        # Умова: Охоронець: зарплата=базова ставка + загальний досвід * 250
        self.salary = self.base_salary + self.general_experience * 250
        self.salary = round(self.salary, 2)
        return self.salary


@dataclass
class School:
    """Сутність Школа - агрегує всі інші сутності."""
    name: str
    classes: List[SchoolClass] = field(default_factory=list)
    employees: List[Employee] = field(default_factory=list)

    @property
    def total_students(self) -> int:
        """Загальна кількість учнів у школі."""
        return sum(c.student_count for c in self.classes)

    def get_all_students(self) -> List[Student]:
        """Отримує список всіх учнів."""
        all_students = []
        for school_class in self.classes:
            all_students.extend(school_class.students)
        return all_students

    def promote_classes(self):
        """Виконує 'переведення' всіх класів на рік вперед."""
        print("--- Початок переведення класів ---")

        # 1. 11 клас зникає.
        # Видаляємо всі класи, які були 11-ми (паралель 11)
        self.classes = [c for c in self.classes if c.parallel < 11]

        # 2. Кожна паралель збільшується на 1 (7А стає 8А)
        for school_class in self.classes:
            school_class.next_year()

        # 3. 1 клас відсутній (після переведення він має бути мінімум 2)
        # Це вже забезпечується, оскільки 1-ші класи стають 2-ми, і ми не додаємо нові 1-ші.

        print("--- Переведення класів завершено ---")




def load_classes_and_students_from_csv(classes_file: str, students_file: str) -> List[SchoolClass]:
    """Завантажує класи та учнів з CSV файлів."""

    # 1. Завантаження даних про учнів
    students_data = {}  # {class_name: [Student, ...]}
    try:
        with open(students_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student(
                    last_name=row['Прізвище'],
                    first_name=row['Ім\'я'],
                    patronymic=row['По батькові'],
                    birth_year=int(row['Рік народження']),
                    gender=row['Стать'],
                    average_grade=float(row['Середня оцінка'])
                )
                class_name = row['Клас']
                if class_name not in students_data:
                    students_data[class_name] = []
                students_data[class_name].append(student)
    except FileNotFoundError:
        print(f"Помилка: Файл учнів {students_file} не знайдено.")
        return []
    except Exception as e:
        print(f"Помилка при завантаженні учнів: {e}")
        return []

    # 2. Завантаження даних про класи
    classes: List[SchoolClass] = []
    try:
        with open(classes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                parallel = int(row['Паралель'])
                vertical = row['Вертикаль']
                class_name = f"{parallel}{vertical}"

                # Призначаємо учнів класу
                class_students = students_data.get(class_name, [])

                school_class = SchoolClass(
                    parallel=parallel,
                    vertical=vertical,
                    students=class_students
                )
                classes.append(school_class)
    except FileNotFoundError:
        print(f"Помилка: Файл класів {classes_file} не знайдено.")
        return []
    except Exception as e:
        print(f"Помилка при завантаженні класів: {e}")
        return []

    return classes