
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Union, Optional
import streamlit as st


class Student: #ств. класу Учень, він зберігає дані та середню оцінку

    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 birth_year: int, gender: str, average_grade: float):
        self.last_name: str = last_name
        self.first_name: str = first_name
        self.middle_name: str = middle_name
        self.birth_year: int = birth_year
        self.gender: str = gender
        self.average_grade: float = average_grade

    def get_full_name(self) -> str: #повернення понвого імені учня
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def __repr__(self) -> str:
        return (f"Student(ПІБ: {self.get_full_name()}, Р.Н.: {self.birth_year}, "
                f"Стать: {self.gender}, Оцінка: {self.average_grade})")


class SchoolClass: #ств. Клас у школі, він зберігає інфо про список учнів

    def __init__(self, parallel: int, vertical: str):
        self.parallel: int = parallel
        self.vertical: str = vertical
        self.students: List[Student] = []

    def add_student(self, student: Student) -> None:  #додавання учня до класу
        self.students.append(student)

    def get_name(self) -> str:
        return f"{self.parallel}{self.vertical}" #повертатиме назву класу

    def get_student_count(self) -> int:
        return len(self.students) #повертатиме к-сть учнів у класі

    def promote_class(self) -> None:
        self.parallel += 1 #викор. під час переведення класу на наступний рік

    def __repr__(self) -> str:
        return f"SchoolClass({self.get_name()}, Учнів: {self.get_student_count()})"


class Employee: #свт. класу для всіх працівників ліцею(загальні атрибути та поліморфізм)

    def __init__(self, full_name: str, base_salary: float):
        self.full_name: str = full_name
        self.base_salary: float = base_salary
        self.salary: Optional[float] = None  # бберігання розрахованої зарплати

    def calculate_salary(self) -> float: #абстрактний метод щоб розрахувати зарплати
        raise NotImplementedError("Цей метод має бути реалізований у дочірніх класах.")

    def __repr__(self) -> str:
        return f"Employee(Посада: {self.__class__.__name__}, ПІБ: {self.full_name})"


class Teacher(Employee): #вчитель успадковує Employee

    def __init__(self, full_name: str, base_salary: float, teaching_experience: int):
        super().__init__(full_name, base_salary)
        self.teaching_experience: int = teaching_experience

    def calculate_salary(self) -> float: #зп вчителів
        self.salary = self.base_salary * self.teaching_experience / 30.0
        return self.salary


class SecurityGuard(Employee):# охоронець успадковує Employee

    def __init__(self, full_name: str, base_salary: float, total_experience: int):
        super().__init__(full_name, base_salary)
        self.total_experience: int = total_experience

    def calculate_salary(self) -> float: #зп охоронця
        self.salary = self.base_salary + self.total_experience * 250.0
        return self.salary


class Director(Employee):  #директор також успадковує Employee

    def __init__(self, full_name: str, base_salary: float, teaching_experience: int, management_experience: int):
        super().__init__(full_name, base_salary)
        self.teaching_experience: int = teaching_experience
        self.management_experience: int = management_experience

    def calculate_salary(self) -> float: #розрахунок зп директора
        self.salary = (self.base_salary * self.teaching_experience / 50.0 +
                       self.management_experience * 500.0)
        return self.salary


class School: #
    def __init__(self, name: str):
        self.name: str = name
        self.classes: Dict[str, SchoolClass] = {}
        self.employees: List[Employee] = []

#1 сценарій
    def load_data(self, classes_file: str, students_file: str) -> None: #завантаження інфо про класи та учнів із csv-файлів

        st.info(f" Завантаження даних для школи '{self.name}'")

        try:
            classes_df = pd.read_csv(classes_file)
            for _, row in classes_df.iterrows():
                parallel = int(row['parallel'])
                vertical = row['vertical']
                key = f"{parallel}{vertical}"
                self.classes[key] = SchoolClass(parallel=parallel, vertical=vertical)
            st.success(f"    Завантажено {len(self.classes)} класів.")
        except Exception as e:
            st.error(f"    Помилка при читанні classes.csv: {e}")
            return

        try:
            students_df = pd.read_csv(students_file)
            for _, row in students_df.iterrows():
                student = Student(
                    last_name=row['last_name'],
                    first_name=row['first_name'],
                    middle_name=row['middle_name'],
                    birth_year=int(row['birth_year']),
                    gender=row['gender'],
                    average_grade=float(row['average_grade'])
                )
                class_key = f"{int(row['class_parallel'])}{row['class_vertical']}"
                if class_key in self.classes:
                    self.classes[class_key].add_student(student)
        except Exception as e:
            st.error(f"    Помилка при читанні students.csv. Перевірте заголовки: {e}")
            return

        st.success("    Усі учні розділені по класах ")

    def get_all_students_data(self) -> pd.DataFrame: #збір даних про учнів для створення графіків
        data = []
        for cls in self.classes.values():
            for student in cls.students:
                data.append({
                    'class_name': cls.get_name(),
                    'parallel': cls.parallel,
                    'vertical': cls.vertical,
                    'gender': student.gender,
                    'birth_year': student.birth_year,
                    'average_grade': student.average_grade
                })
        return pd.DataFrame(data)

    def display_statistics(self, title: str) -> None:

        st.header(f" {title}")
        st.markdown("---")

        students_df = self.get_all_students_data()
        total_students = len(students_df)

        # Виведення основної статистики
        col1, col2, col3 = st.columns(3)
        col1.metric("Загальна кількість учнів:", total_students)

        if total_students == 0 or len(self.classes) == 0:
            st.warning("Недостатньо даних для повної статистики.")
            return

        gender_counts = students_df['gender'].value_counts()
        percent_boys = gender_counts.get('Хлопець', 0) / total_students * 100
        percent_girls = gender_counts.get('Дівчина', 0) / total_students * 100

        col2.metric("Хлопці", f"{percent_boys:.2f}%", delta=f"{gender_counts.get('Хлопець', 0)} осіб") #ств зелених областей зі стрілками
        col3.metric("Дівчата", f"{percent_girls:.2f}%", delta=f"{gender_counts.get('Дівчина', 0)} осіб")

 #середня, макс та мін кількість учнів
        class_stats = [(cls.get_name(), cls.get_student_count()) for cls in self.classes.values()]
        class_counts = [count for _, count in class_stats]

        if class_counts:
            avg_students_per_class = sum(class_counts) / len(class_counts)
            max_students_info = max(class_stats, key=lambda item: item[1])
            min_students_info = min(class_stats, key=lambda item: item[1])

            st.markdown(f"**Середня кількість учнів у класах:** **{avg_students_per_class:.2f}**")
            st.info(
                f"**Максимум:** {max_students_info[1]} учнів (у класі {max_students_info[0]}) | **Мінімум:** {min_students_info[1]} учнів (у класі {min_students_info[0]})")

        st.subheader("Розподіл учнів по класах")
        class_data_for_df = [{'Клас': name, 'Кількість учнів': count} for name, count in class_stats]
        st.dataframe(pd.DataFrame(class_data_for_df))

    def generate_visualizations(self) -> None: #створення графіків

        st.header("  Візуалізація даних ")
        st.markdown("---")

        students_df = self.get_all_students_data()
        if students_df.empty:
            st.warning("Немає даних для візуалізації.")
            return


        class_info = pd.DataFrame([
            (cls.vertical, cls.get_student_count(), cls.parallel)
            for cls in self.classes.values()
        ], columns=['vertical', 'count', 'parallel'])


        st.subheader(" Розділ кількості учнів по паралелях")

        parallel_counts = students_df.groupby('parallel')['gender'].count()

        fig_3a, ax_3a = plt.subplots(figsize=(10, 6))
        parallel_counts.plot(kind='bar', ax=ax_3a, color='skyblue')
        ax_3a.set_title('Розподіл кількості учнів по паралелях')
        ax_3a.set_xlabel('Паралель')
        ax_3a.set_ylabel('Кількість учнів')
        ax_3a.tick_params(axis='x', rotation=0)
        st.pyplot(fig_3a)

        st.subheader("Розділ середньої кількості учнів по вертикалях")

        avg_students_per_vertical = class_info.groupby('vertical')['count'].mean().sort_index()

        fig_3b, ax_3b = plt.subplots(figsize=(8, 6))
        avg_students_per_vertical.plot(kind='bar', ax=ax_3b, color='coral')
        ax_3b.set_title('Середня кількість учнів у класі по вертикалях')
        ax_3b.set_xlabel('Вертикаль (літера)')
        ax_3b.set_ylabel('Середня кількість учнів у класі')
        ax_3b.tick_params(axis='x', rotation=0)
        st.pyplot(fig_3b)


        st.subheader("Графік учнів за роком народження")

        birth_year_counts = students_df['birth_year'].value_counts().sort_index()

        fig_3c, ax_3c = plt.subplots(figsize=(10, 6))
        birth_year_counts.plot(kind='line', marker='o', ax=ax_3c, color='forestgreen')
        ax_3c.set_title('Кількість учнів за роком народження')
        ax_3c.set_xlabel('Рік народження')
        ax_3c.set_ylabel('Кількість учнів')
        ax_3c.set_xticks(birth_year_counts.index)  # Явно вказуємо мітки
        ax_3c.tick_params(axis='x', rotation=45)
        st.pyplot(fig_3c)


        st.subheader("Середня оцінка учнів від класу scatter)")  #графік усіх оцінок

        unique_classes = sorted(self.classes.keys(), key=lambda k: (self.classes[k].parallel, self.classes[k].vertical))
        class_mapping = {name: i for i, name in enumerate(unique_classes)}
        students_df['class_index'] = students_df['class_name'].map(class_mapping)

        fig_3d, ax_3d = plt.subplots(figsize=(12, 7))
        ax_3d.scatter(students_df['class_index'], students_df['average_grade'],
                      alpha=0.6, edgecolors='w', s=70, c='purple')
        ax_3d.set_xticks(list(class_mapping.values()))
        ax_3d.set_xticklabels(list(class_mapping.keys()), rotation=60, ha='right')
        ax_3d.set_title('Залежність середньої оцінки учнів від класу')
        ax_3d.set_xlabel('Клас')
        ax_3d.set_ylabel('Середня оцінка')
        ax_3d.set_ylim(4, 12)

        plt.tight_layout()
        st.pyplot(fig_3d)

        st.success(" Всі графіки створено")

    def promote_all_classes(self) -> None: #переведення класів вперед на рік
        print("\n Виконання переведення класів")
        new_classes: Dict[str, SchoolClass] = {}

        for key, cls in self.classes.items():
            if cls.parallel == 11: # 11 клас випускається
                continue

            cls.promote_class() #кожна паралель збільшується на 1
            new_key = cls.get_name()
            new_classes[new_key] = cls

        self.classes = new_classes

           #1 клас зник, бо відбулося переведення в 2-й
        print( "    Переведення завершено. 11-ті класи випущено, всі інші піднято на 1 паралель (нові 1-ші класи відсутні)")

#  2 сценарій: керування зарплатами працівників
    def initialize_employees(self) -> None: #створення об'єктів різних працівників
        print("\n Ініціалізація працівників")

        # для директора початкова ставка 15000
        director = Director("Шевченко Л.В.", 15000.0, teaching_experience=25, management_experience=10)
        self.employees.append(director)

        #для вчителів початкові ставки 12000
        teacher1 = Teacher("Бова С.М.", 12000.0, teaching_experience=15)
        teacher2 = Teacher("Дрібна Т.М.", 12000.0, teaching_experience=8)
        teacher3 = Teacher("Клунник О.С.", 12000.0, teaching_experience=2)
        self.employees.extend([teacher1, teacher2, teacher3])

        #для охоронця початкова ставка 11000
        guard = SecurityGuard("Стороженко Р.Р.", 11000.0, total_experience=5)
        self.employees.append(guard)

        print(f"   Досліджено {len(self.employees)} працівників")

    def process_salaries(self, output_file: str = 'salaries.csv') -> None: #обрахунок зп та збереження таблиці у csv
        print("\n   Розрахунок зарплат")
        salary_records = []

        for employee in self.employees: #поліморфізм(виклик методу розрахунку)
            salary = employee.calculate_salary()

            #збір інфо для таблиці
            record: Dict[str, Union[str, float, int, Optional[int]]] = {
                'Посада': employee.__class__.__name__,
                'ПІБ': employee.full_name,
                'Базова_Ставка': employee.base_salary,
                'Розрахована_Зарплата': round(salary, 2),
                'Педагогічний_Стаж': None,
                'Стаж_Керування': None,
                'Загальний_Досвід': None
            }

            if isinstance(employee, (Teacher, Director)):
                record['Педагогічний_Стаж'] = employee.teaching_experience
            if isinstance(employee, Director):
                record['Стаж_Керування'] = employee.management_experience
            if isinstance(employee, SecurityGuard):
                record['Загальний_Досвід'] = employee.total_experience

            salary_records.append(record)


        if salary_records:  # збереження таблиці розрахованих зарплат у csv-файл
            salary_df = pd.DataFrame(salary_records)
            salary_df.to_csv(output_file, index=False, encoding='utf-8')

            st.success(f"    Зарплати розраховано та збережено у файл: {output_file}") #я вирішив вивести таблицю зп у streamlit
            st.subheader("Таблиця розрахованих зарплат")
            st.dataframe(salary_df) # st.dataframe викор для відображення
        else:
            st.warning("   Немає даних для збереження.")



#функції для створення csv
def create_initial_csv_files():
    print(" Створення/оновлення CSV файлів для правильного зчитування")


    classes_data = [
        {'parallel': p, 'vertical': v}
        for p in range(1, 12)
        for v in (['А', 'Б'] if p <= 10 else ['А', 'Б'])
    ]


    pd.DataFrame(classes_data).to_csv('classes.csv', index=False, encoding='utf-8')

    #створення students.csv
    students_columns = ['last_name', 'first_name', 'middle_name', 'birth_year', 'gender', 'average_grade',
                        'class_parallel', 'class_vertical']
    students_data = [
        # створення 1 класу
        ['Іванов', 'Петро', 'Сергійович', 2018, 'Хлопець', 10.5, 1, 'А'],
        ['Коваленко', 'Анна', 'Олегівна', 2019, 'Дівчина', 11.2, 1, 'А'],
        ['Мельник', 'Максим', 'Вікторович', 2018, 'Хлопець', 9.8, 1, 'Б'],
        ['Савчук', 'Олена', 'Ігорівна', 2018, 'Дівчина', 10.9, 1, 'Б'],
        ['Бойко', 'Дмитро', 'Павлович', 2018, 'Хлопець', 9.1, 1, 'А'],

        # створення 5 класу
        ['Шевченко', 'Ірина', 'Василівна', 2015, 'Дівчина', 10.0, 5, 'А'],
        ['Захарченко', 'Богдан', 'Андрійович', 2015, 'Хлопець', 10.1, 5, 'Б'],
        ['Ткаченко', 'Марія', 'Романівна', 2015, 'Дівчина', 11.5, 5, 'Б'],
        ['Шостак', 'Анджела', 'Констянтинівна', 2015, 'Дівчина', 11.5, 5, 'А'],
        ['Савченко', 'Любомир', 'Андрійович', 2015, 'Хлопець', 11.5, 5, 'Б'],
        ['Кормот', 'Даня', 'Назарович', 2015, 'Хлопець', 11.5, 5, 'А'],
        ['Петришина', 'Рита', 'Олександрівна', 2015, 'Дівчина', 11.5, 5, 'Б'],

        # ствоерння 11 класу
        ['Сидоренко', 'Назар', 'Леонідович', 2008, 'Хлопець', 9.5, 11, 'А'],
        ['Степаненко', 'Юрій', 'Ілларіонович', 2008, 'Хлопець', 7.2, 11, 'Б'],
        ['Сойченко', 'Криштіан', 'Апанасійович', 2009, 'Хлопець', 8.5, 11, 'Б'],
        ['Старшенко', 'Сигізмунд', 'Валерійович', 2008, 'Хлопець', 9.8, 11, 'А'],
        ['Волошенко', 'Олег', 'Андріанович', 2008, 'Хлопець', 10.7, 11, 'Б'],
        ['Вогняненко', 'Стефанія', 'Віталіївна', 2009, 'Дівчина', 11.2, 11, 'Б'],
        ['Тульчинська', 'Марта', 'Іванівна', 2009, 'Дівчина', 10.1, 11, 'А'],
        ['Міндіч', 'Яніна', 'Іванівна', 2008, 'Дівчина', 10.7, 11, 'Б'],
        ['Марченко', 'Юлія', 'Іванівна', 2008, 'Дівчина', 10.9, 11, 'Б'],

        #інші класи
        ['Григоренко', 'Олег', 'Петрович', 2012, 'Хлопець', 8.9, 7, 'А'],
        ['Соколова', 'Аліна', 'Максименко', 2010, 'Дівчина', 11.8, 9, 'Б'],
        ['Радченко', 'Лариса', 'Миколаївна', 2010, 'Дівчина', 11.8, 9, 'Б'],
        ['Міщенко', 'Єлизаветта', 'Денисович', 2015, 'Дівчина', 7.5, 6, 'А'],
        ['Мачкуренко', 'Ігор', 'Видимович', 2014, 'Хлопець', 3.5, 6, 'А'],
        ['Власенко', 'Максим', 'Валерійович', 2016, 'Хлопець', 7.5, 6, 'Б'],
        ['Кравченко', 'Назарій', 'Павлович', 2017, 'Хлопець', 11.1, 2, 'А'],
        ['Федієнко', 'Мартин', 'Євгенович', 2016, 'Хлопець', 5.5, 3, 'Б'],
        ['Замора', 'Джульєтта', 'Львівна', 2015, 'Хлопець', 7.1, 4, 'Б'],
        ['Бульбаш', 'Тарас', 'Стасович', 2013, 'Хлопець', 6.1, 7, 'Б'],
        ['Чех', 'Максим', 'Оксенович', 2011, 'Хлопець', 9.4, 8, 'А'],
        ['Сова', 'Віталія', 'Вікторівна', 2017, 'Дівчина', 9.1, 3, 'Б'],
        ['Дрозд', 'Семен', 'Сіргійович', 2010, 'Хлопець', 10.1, 10, 'А'],
        ['Жек', 'Франко', 'Артемович', 2010, 'Хлопець', 5.1, 9, 'Б'],
        ['Курлик', 'Посейдоон', 'Файлович', 2011, 'Хлопець', 9.9, 8, 'А'],
        ['Кірічок', 'Софія', 'Вайлентівна', 2017, 'Дівчина', 8.2, 3, 'Б'],
        ['Хрищук', 'Аміна', 'Олегівна', 2018, 'Дівчина', 9.1, 2, 'Б'],
        ['Фастун', 'Дмитро', 'Дмитрович', 2018, 'Хлопець', 9.3, 2, 'Б'],
        ['Заєць', 'Максим', 'Денисович', 2017, 'Хлопець', 7.4, 3, 'А'],
        ['Друг', 'Федір', 'Арсенович', 2017, 'Хлопець', 7.6, 3, 'А'],
        ['Рипун', 'Поліна', 'Олексіївна', 2017, 'Дівчина', 8.1, 3, 'А'],
        ['Шуруп', 'Остап', 'Миколайович', 2017, 'Хлопець', 9.7, 3, 'А'],
        ['Козаченко', 'Яся', 'Степанівна', 2016, 'Дівчина', 11.7, 4, 'А'],
        ['Рибак', 'Денис', 'Петрович', 2016, 'Хлопець', 4.4, 4, 'А'],
        ['Розумака', 'Леся', 'Богданівна', 2016, 'Дівчина', 5.7, 4, 'А'],
        ['Задира', 'Микита', 'Глебович', 2016, 'Хлопець', 11.1, 4, 'А'],
        ['Дрозд', 'Петро', 'Матвійович', 2016, 'Хлопець', 9.9, 4, 'Б'],
        ['Кучер', 'Марина', 'Русланівна', 2016, 'Дівчина', 7.4, 6, 'Б'],
        ['Кучер', 'Маргарита', 'Олександрівна', 2016, 'Дівчина', 7.2, 6, 'Б'],
        ['Коцюбайло', 'Дмитро', 'Арсенович', 2012, 'Хлопець', 8.9, 7, 'А'],
        ['Хмельницький', 'Богдан', 'Петрович', 2012, 'Хлопець', 8.9, 7, 'А'],
        ['Фуцький', 'Тарас', 'Макарович', 2013, 'Хлопець', 6.1, 7, 'Б'],
        ['Молодецький', 'Ярослав', 'Євгенійович', 2013, 'Хлопець', 5.5, 7, 'Б'],
        ['Цись', 'Юлія', 'Іванівна', 2013, 'Дівчина', 5.3, 7, 'Б'],
        ['Малюк', 'Олександра', 'Микитівна', 2011, 'Дівчина', 11.2, 8, 'А'],
        ['Шевченко', 'Дарина', 'Назарівна', 2011, 'Дівчина', 2.2, 8, 'А'],
        ['Ашуркіна', 'Марія', 'Захарова', 2011, 'Дівчина', 5.2, 8, 'Б'],
        ['Курилко', 'Роман', 'Володимирович', 2011, 'Хлопець', 4.9, 8, 'Б'],
        ['Водолаз', 'Мартин', 'Антонович', 2011, 'Хлопець', 9.0, 8, 'Б'],
        ['Цюпа', 'Олександра', 'Рустемівна', 2011, 'Дівчина', 12.0, 8, 'Б'],
        ['Єфіменко', 'Світлана', 'Володимирівна', 2010, 'Дівчина', 4.8, 9, 'А'],
        ['Кабан', 'Ростислав', 'Захарович', 2010, 'Хлопець', 8.8, 9, 'А'],
        ['Антонов', 'Антон', 'Александрович', 2010, 'Хлопець', 7.7, 9, 'А'],
        ['Гудзь', 'Вікторія', 'Олексіївна', 2010, 'Дівчина', 10.1, 10, 'А'],
        ['Усик', 'Алла', 'Максимівна', 2010, 'Дівчина', 11.4, 10, 'А'],
        ['Яковенко', 'Віола', 'Федірівна', 2010, 'Дівчина', 10.5, 10, 'А'],
        ['Коваль', 'Ян', 'Михайлович', 2010, 'Хлопець', 10.4, 10, 'Б'],
        ['Щедра', 'Анна', 'Василівна', 2010, 'Дівчина', 7.7, 10, 'А'],
        ['Гуцуляк', 'Віта', 'Сіргіївна', 2010, 'Дівчина', 7.2, 10, 'Б'],
        ['Чеснакова', 'Леся', 'Андріївна', 2010, 'Дівчина', 6.1, 10, 'Б'],
        ['Стефанчук', 'Володимир', 'Олександрович', 2010, 'Хлопець', 11.2, 10, 'Б'],
    ]
    pd.DataFrame(students_data, columns=students_columns).to_csv('students.csv', index=False, encoding='utf-8')

    print("    Файли classes.csv та students.csv створено/оновлено.")


def main():  # основна функція для виконанння сценаріїв

    st.title(" Проект: керування сутностями ліцею")

    #оновлення csv файлів
    create_initial_csv_files()

    #сценарій 1: ініціалізація та статистика
    my_school = School(name=" Терешківський ліцей ")

    st.subheader("Сценарій 1: ініціалізація та аналіз даних")

    #завантаження даних
    my_school.load_data(classes_file='classes.csv', students_file='students.csv')

    #вивід інфо та створення графіків
    my_school.display_statistics(title="Початкова статистика (до переведення)")
    my_school.generate_visualizations()

    st.subheader(" Переведення класів на наступний рік")
    my_school.promote_all_classes()

    my_school.display_statistics(title="Оновлена статистика (після переведення)")

 #2 сценарій: керування зарплатами працівників
    st.subheader("Сценарій 2: Керування Зарплатами Працівників")
    my_school.initialize_employees()  # створення програмних об'єктів працівників

    my_school.process_salaries()  # розрахунок та збереження зарплат

    st.success("  Усі сценарії виконано! Звіт про зарплати збережено у salaries.csv")

if __name__ == "__main__":

    main()