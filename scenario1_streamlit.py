# scenario1_streamlit.py (ОНОВЛЕНА ВЕРСІЯ: відображає обидва стани)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy # Потрібно для створення глибокої копії об'єктів
import sys
# Імпортуємо класи з файлу school_entities.py
from school_entities import School, load_classes_and_students_from_csv, SchoolClass

# Налаштування сторінки Streamlit
st.set_page_config(layout="wide", page_title="Шкільна Статистика")


# --- Допоміжні функції (залишаються без змін) ---

def get_class_data_df(school: School) -> (pd.DataFrame, pd.DataFrame):
    """Створює DataFrame з даними по класам і по учням."""
    data_classes = []
    all_students_data = []

    for cls in school.classes:
        if cls.student_count > 0:
            avg_grade = sum(s.average_grade for s in cls.students) / cls.student_count
            data_classes.append({
                'Клас_Назва': cls.name,
                'Паралель': cls.parallel,
                'Вертикаль': cls.vertical,
                'Кількість учнів': cls.student_count,
                'Середня оцінка класу': round(avg_grade, 2)
            })
            for s in cls.students:
                all_students_data.append({
                    'Клас_Назва': cls.name,
                    'Паралель': cls.parallel,
                    'Вертикаль': cls.vertical,
                    'Рік_Народження': s.birth_year,
                    'Стать': s.gender,
                    'Середня_Оцінка': s.average_grade
                })

    df_classes = pd.DataFrame(data_classes).sort_values(by=['Паралель', 'Вертикаль']).reset_index(drop=True)
    df_students = pd.DataFrame(all_students_data)

    return df_classes, df_students

def display_stats(school: School, title: str, state_key: str):
    """Виводить статистичну інформацію та графіки."""

    with st.expander(title, expanded=True if state_key == 'initial' else False):
        st.header(f"📊 {title}")

        df_classes, df_students = get_class_data_df(school)

        if df_students.empty:
            st.warning("У школі немає учнів для відображення статистики.")
            return

        total_students = school.total_students

        # --- Пункт 2: Статистична інформація (Метрики) ---
        gender_counts = df_students['Стать'].value_counts()
        male_percent = round(gender_counts.get('Хлопець', 0) / total_students * 100, 2)
        female_percent = round(gender_counts.get('Дівчина', 0) / total_students * 100, 2)
        avg_students_per_class = round(df_classes['Кількість учнів'].mean(), 2) if not df_classes.empty else 0

        if not df_classes.empty:
            max_row = df_classes.loc[df_classes['Кількість учнів'].idxmax()]
            max_info = f"{max_row['Кількість учнів']} (Клас: {max_row['Клас_Назва']})"
            min_row = df_classes.loc[df_classes['Кількість учнів'].idxmin()]
            min_info = f"{min_row['Кількість учнів']} (Клас: {min_row['Клас_Назва']})"
        else:
            max_info = "N/A"
            min_info = "N/A"

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("**Загальна к-сть учнів**", total_students)
        with col2: st.metric("**% Хлопців**", f"{male_percent}%")
        with col3: st.metric("**% Дівчат**", f"{female_percent}%")
        with col4: st.metric("**Сер. к-сть учнів у класі**", avg_students_per_class)
        with col5: st.metric("**Клас з max к-стю учнів**", max_info)

        st.subheader("📚 Деталізація по класах")
        st.dataframe(df_classes, use_container_width=True)

        # --- Пункт 3: Графіки ---
        st.subheader("📈 Візуалізація Даних")

        colA, colB = st.columns(2)

        # 3.a. Розподіл кількості учнів по паралелях.
        with colA:
            st.caption("3.a. Розподіл учнів по Паралелях")
            df_parallel_stats = df_classes.groupby('Паралель')['Кількість учнів'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(df_parallel_stats['Паралель'].astype(str), df_parallel_stats['Кількість учнів'], color='skyblue')
            ax.set_xlabel('Паралель')
            ax.set_ylabel('Кількість учнів')
            st.pyplot(fig)
            plt.close(fig)

        # 3.b. Розподіл середньої кількості учнів по вертикалях.
        with colB:
            st.caption("3.b. Розподіл кількості учнів по Вертикалях (Box Plot)")
            fig, ax = plt.subplots(figsize=(8, 4))
            df_classes.boxplot(column=['Кількість учнів'], by='Вертикаль', ax=ax, grid=False)
            ax.set_xlabel('Вертикаль')
            ax.set_ylabel('Кількість учнів')
            plt.suptitle('')
            st.pyplot(fig)
            plt.close(fig)

        colC, colD = st.columns(2)

        # 3.c. Лінійний графік кількості учнів від року народження.
        with colC:
            st.caption("3.c. Кількість учнів за Роком Народження")
            df_birth_year = df_students.groupby('Рік_Народження').size().reset_index(name='Кількість_учнів')
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(df_birth_year['Рік_Народження'], df_birth_year['Кількість_учнів'], marker='o', linestyle='-', color='green')
            ax.set_xlabel('Рік Народження')
            ax.set_ylabel('Кількість учнів')
            ax.set_xticks(df_birth_year['Рік_Народження'])
            st.pyplot(fig)
            plt.close(fig)

        # 3.d. Графік залежності scatter середньої оцінки учнів від класу.
        with colD:
            st.caption("3.d. Середня Оцінка учнів від Класу (Scatter)")

            class_order = df_classes.sort_values(by='Паралель')['Клас_Назва'].unique()
            df_students['Клас_Назва'] = pd.Categorical(df_students['Клас_Назва'], categories=class_order, ordered=True)
            df_students_sorted = df_students.sort_values('Клас_Назва')

            fig, ax = plt.subplots(figsize=(8, 5))

            for gender, data in df_students_sorted.groupby('Стать'):
                ax.scatter(data['Клас_Назва'], data['Середня_Оцінка'], label=gender, alpha=0.7)

            ax.set_xlabel('Клас')
            ax.set_ylabel('Середня Оцінка')
            ax.legend(title='Стать')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# --- Основна логіка Сценарію 1 ---

st.title("🏫 Проєкт Керування Сутностями Школи")
st.subheader("Сценарій 1: Ініціалізація, Статистика та Переведення")

# 1. Завантаження інформації та ініціалізація
if 'initial_school' not in st.session_state:

    # 1. Завантажуємо початкові дані
    initial_classes = load_classes_and_students_from_csv("classes.csv", "students.csv")
    st.session_state['initial_school'] = School(name="Ліцей (Початковий)", classes=initial_classes)

    # Створюємо глибоку копію для переведення, щоб не змінювати початкові дані
    promoted_classes_copy = copy.deepcopy(initial_classes)
    st.session_state['promoted_school'] = School(name="Ліцей (Після переведення)", classes=promoted_classes_copy)

    # 4. Виконуємо переведення одразу
    if st.session_state['promoted_school'].classes:
        st.session_state['promoted_school'].promote_classes()
        st.session_state['promoted'] = True
    else:
        st.session_state['promoted'] = False

    # Перезавантаження для відображення змін (якщо Streamlit цього потребує)
    st.rerun()


# Виведення початкової та оновленої інформації
if not st.session_state['initial_school'].classes:
    st.error("Не вдалося завантажити дані класів або учнів. Перевірте наявність та формат CSV файлів.")
else:
    col_init, col_promo = st.columns(2)

    with col_init:
        # 2. Виведення початкової інформації
        display_stats(st.session_state['initial_school'],
                      "1️⃣ Початкова Статистика (До переведення)",
                      'initial')

    if st.session_state['promoted']:
        with col_promo:
            # 5. Виведення інформації після переведення
            display_stats(st.session_state['promoted_school'],
                          "2️⃣ Оновлена Статистика (Після переведення)",
                          'promoted')

            # Перевірка коректності переведення
            df_classes, _ = get_class_data_df(st.session_state['promoted_school'])
            current_parallels = df_classes['Паралель'].unique()

            st.markdown("### ✅ Перевірка коректності")
            if 1 in current_parallels:
                st.error("1-й клас має бути відсутній.")
            elif any(p > 11 for p in current_parallels):
                st.error("Усі класи, що стали 12-ми, мають бути видалені.")
            else:
                st.success("Переведення виконано коректно.")