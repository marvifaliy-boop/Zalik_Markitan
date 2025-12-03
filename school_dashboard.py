import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
import streamlit as st
import os



#ств класів для 1 сценарію
class Student: #ств класу Учень, він зберігає дані та середню оцінку
    def __init__(self, last_name: str, first_name: str, middle_name: str,
                 birth_year: int, gender: str, average_grade: float):
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.birth_year = birth_year
        self.gender = gender
        self.average_grade = average_grade

    def get_full_name(self) -> str: #повернення понвого імені учня
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class SchoolClass: #ств класу у школі, він зберігає інфо про список учнів

    def __init__(self, parallel: int, vertical: str):
        self.parallel = parallel
        self.vertical = vertical
        self.students: List[Student] = []

    def add_student(self, student: Student) -> None:  #додавання учня до класу
        self.students.append(student)

    def get_name(self) -> str:
        return f"{self.parallel}-{self.vertical}" #повертатиме назву класу

    def get_student_count(self) -> int:
        return len(self.students) #повертатиме к-сть учнів у класі

    def promote_class(self) -> None:
        self.parallel += 1 #викор. під час переведення класу на наступний рік


class School: #ств класу
    def __init__(self, name: str):
        self.name = name
        self.classes: Dict[str, SchoolClass] = {}

    def load_data(self, classes_file: str, students_file: str) -> None:
        try:
            classes_df = pd.read_csv(classes_file)
            for _, row in classes_df.iterrows():
                p, v = int(row['parallel']), row['vertical']
                self.classes[f"{p}{v}"] = SchoolClass(parallel=p, vertical=v)

            students_df = pd.read_csv(students_file)
            for _, row in students_df.iterrows():
                student = Student(
                    row['last_name'], row['first_name'], row['middle_name'],
                    int(row['birth_year']), row['gender'], float(row['average_grade'])
                )
                key = f"{int(row['class_parallel'])}{row['class_vertical']}"
                if key in self.classes:
                    self.classes[key].add_student(student)
        except Exception as e:
            st.error(f"Помилка завантаження: {e}")

    def get_all_students_data(self) -> pd.DataFrame:
        data = []
        for cls in self.classes.values():
            for s in cls.students:
                data.append({
                    'class_name': cls.get_name(),
                    'parallel': cls.parallel,
                    'vertical': cls.vertical,
                    'gender': s.gender,
                    'birth_year': s.birth_year,
                    'average_grade': s.average_grade
                })
        return pd.DataFrame(data)

    def display_statistics(self, title: str) -> None:
        st.header(f" {title}")
        st.markdown("---")

        students_df = self.get_all_students_data()
        total_students = len(students_df)

        # 1. Основні метрики
        col1, col2, col3 = st.columns(3)
        col1.metric("Всього учнів", total_students)

        if not students_df.empty:
            g_counts = students_df['gender'].value_counts()
            col2.metric("Хлопці", g_counts.get('Хлопець', 0))
            col3.metric("Дівчата", g_counts.get('Дівчина', 0))

        # 2. Інформація про макс/мін клас
        if self.classes:
            max_class = max(self.classes.values(), key=lambda c: c.get_student_count())
            max_count = max_class.get_student_count()

            min_class = min(self.classes.values(), key=lambda c: c.get_student_count())
            min_count = min_class.get_student_count()

            st.info(f" **Найбільший клас:** {max_class.get_name()} ({max_count} учнів)")
            st.warning(f" **Найменший клас:** {min_class.get_name()} ({min_count} учнів)")

        # 3. ЗАМІНА ТАБЛИЦІ НА ГРАФІК (ОНОВЛЕНО)
        if self.classes:
            st.subheader(" Детальний розподіл по класах")

            # Сортуємо класи, щоб вони йшли по порядку (1-А, 1-Б, 2-А...)
            sorted_classes = sorted(self.classes.values(), key=lambda c: (c.parallel, c.vertical))

            names = [c.get_name() for c in sorted_classes]
            counts = [c.get_student_count() for c in sorted_classes]

            # Будуємо графік
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(names, counts, color='royalblue', edgecolor='black')

            ax.set_ylabel("Кількість учнів")
            ax.set_title("Кількість учнів у кожному класі")
            ax.set_ylim(0, max(counts) + 2)  # Трохи місця зверху
            plt.xticks(rotation=45)  # Повертаємо підписи, щоб не злипалися

            st.pyplot(fig)

    def generate_visualizations(self) -> None:
        st.subheader(" Графічний аналіз")
        df = self.get_all_students_data()
        if df.empty: return

        tab1, tab2, tab3, tab4 = st.tabs(["Паралелі", "Роки народження", "Вертикалі", "Успішність"])

        with tab1:
            st.caption("Розподіл кількості учнів по паралелях")
            fig, ax = plt.subplots(figsize=(8, 4))
            df.groupby('parallel')['gender'].count().plot(kind='bar', ax=ax, color='skyblue')
            ax.set_xlabel("Паралель")
            ax.set_ylabel("Кількість")
            st.pyplot(fig)

        with tab2:
            st.caption("Кількість учнів за роком народження (НОВЕ)")
            fig, ax = plt.subplots(figsize=(8, 4))
            birth_counts = df['birth_year'].value_counts().sort_index()
            birth_counts.plot(kind='bar', ax=ax, color='forestgreen')
            ax.set_xlabel("Рік народження")
            ax.set_ylabel("Кількість")
            st.pyplot(fig)

        with tab3:            # розрахунок середнього для класів А і б
            st.caption("Середня кількість учнів по вертикалях (НОВЕ)")
            class_counts = []
            for cls in self.classes.values():
                class_counts.append({'vertical': cls.vertical, 'count': cls.get_student_count()})

            df_vert = pd.DataFrame(class_counts)
            avg_vert = df_vert.groupby('vertical')['count'].mean()

            fig, ax = plt.subplots(figsize=(6, 4))
            avg_vert.plot(kind='bar', ax=ax, color='coral')
            ax.set_xlabel("Вертикаль")
            ax.set_ylabel("Середня кількість учнів у класі")
            st.pyplot(fig)

        with tab4:
            st.caption("Середня оцінка по класах")
            unique_cls = sorted(self.classes.keys(), key=lambda k: (self.classes[k].parallel, self.classes[k].vertical))
            mapping = {name: i for i, name in enumerate(unique_cls)}

            labels = [self.classes[k].get_name() for k in unique_cls]

            temp_df = df.copy()
            temp_df['lookup_key'] = temp_df.apply(lambda x: f"{x['parallel']}{x['vertical']}", axis=1)
            temp_df['sort_index'] = temp_df['lookup_key'].map(mapping)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(temp_df['sort_index'], temp_df['average_grade'], alpha=0.5, c='purple')
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=90)
            ax.set_xlabel("Клас")
            ax.set_ylabel("Середній бал")
            st.pyplot(fig)

    def promote_all_classes(self) -> None:
        st.toast("Переводимо класи...")
        new_classes = {}
        for key, cls in self.classes.items():
            if cls.parallel == 11:
                continue  # 11-ті випускаються
            cls.promote_class()
            new_key = f"{cls.parallel}{cls.vertical}"
            new_classes[new_key] = cls
        self.classes = new_classes
        st.success(" Переведення класів")


#повний список від користувача
def create_initial_csv_files():
    #if os.path.exists('classes.csv') and os.path.exists('students.csv'):
      # return

 #ствоерння класів 1-11 та паралелей А і Б
    classes_data = [{'parallel': p, 'vertical': v} for p in range(1, 12) for v in ['А', 'Б']]
    pd.DataFrame(classes_data).to_csv('classes.csv', index=False)

#створення повного списку учнів
    cols = ['last_name', 'first_name', 'middle_name', 'birth_year', 'gender', 'average_grade', 'class_parallel',
            'class_vertical']
    data = [
        ['Іванов', 'Петро', 'Сергійович', 2018, 'Хлопець', 10.5, 1, 'А'],
        ['Коваленко', 'Анна', 'Олегівна', 2019, 'Дівчина', 11.2, 1, 'А'],
        ['Мельник', 'Максим', 'Вікторович', 2018, 'Хлопець', 9.8, 1, 'Б'],
        ['Савчук', 'Олена', 'Ігорівна', 2018, 'Дівчина', 10.9, 1, 'Б'],
        ['Бойко', 'Дмитро', 'Павлович', 2018, 'Хлопець', 9.1, 1, 'А'],
        ['Шевченко', 'Ірина', 'Василівна', 2015, 'Дівчина', 10.0, 5, 'А'],
        ['Захарченко', 'Богдан', 'Андрійович', 2015, 'Хлопець', 10.1, 5, 'Б'],
        ['Ткаченко', 'Марія', 'Романівна', 2015, 'Дівчина', 11.5, 5, 'Б'],
        ['Шостак', 'Анджела', 'Констянтинівна', 2015, 'Дівчина', 11.5, 5, 'А'],
        ['Савченко', 'Любомир', 'Андрійович', 2015, 'Хлопець', 11.5, 5, 'Б'],
        ['Кормот', 'Даня', 'Назарович', 2015, 'Хлопець', 11.5, 5, 'А'],
        ['Петришина', 'Рита', 'Олександрівна', 2015, 'Дівчина', 11.5, 5, 'Б'],
        ['Сидоренко', 'Назар', 'Леонідович', 2008, 'Хлопець', 9.5, 11, 'А'],
        ['Степаненко', 'Юрій', 'Ілларіонович', 2008, 'Хлопець', 7.2, 11, 'Б'],
        ['Сойченко', 'Криштіан', 'Апанасійович', 2009, 'Хлопець', 8.5, 11, 'Б'],
        ['Старшенко', 'Сигізмунд', 'Валерійович', 2008, 'Хлопець', 9.8, 11, 'А'],
        ['Волошенко', 'Олег', 'Андріанович', 2008, 'Хлопець', 10.7, 11, 'Б'],
        ['Вогняненко', 'Стефанія', 'Віталіївна', 2009, 'Дівчина', 11.2, 11, 'Б'],
        ['Тульчинська', 'Марта', 'Іванівна', 2009, 'Дівчина', 10.1, 11, 'А'],
        ['Міндіч', 'Яніна', 'Іванівна', 2008, 'Дівчина', 10.7, 11, 'Б'],
        ['Марченко', 'Юлія', 'Іванівна', 2008, 'Дівчина', 10.9, 11, 'Б'],
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
    pd.DataFrame(data, columns=cols).to_csv('students.csv', index=False)



if __name__ == "__main__":
    st.set_page_config(page_title="School Manager", layout="wide")
    create_initial_csv_files()

    st.title(" Терешківський ліцей ")

    school = School("Терешківський ліцей")

    school.load_data('classes.csv', 'students.csv')    #завантаження даних

    school.display_statistics("Статистика до переведення") #вивід статистики до оновлення
    school.generate_visualizations()

    st.markdown("---")

    st.subheader(" Виконати переведення") #кнопка щоб відбулося переведення
    if st.button("Перевести учнів на наступний рік"):
        school.promote_all_classes()
        st.markdown("---")

        school.display_statistics("Статистика оновлена ") #статистика після переведення
        school.generate_visualizations()