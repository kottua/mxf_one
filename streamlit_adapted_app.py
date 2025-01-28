import streamlit as st
import pandas as pd
import os
from src.max_bcg import *
from src.max_dp import *
from src.max_calculate_plan import *
from src.connect_and_process import reload_stock_table, process_basic
from src.calendar_func import *

def main():
    st.title("Streamlit адаптація для Maxify")

    # Завантаження файлів
    uploaded_warehouse_file = st.file_uploader("Завантажте файл 'Warehouse' (Excel)", type=["xlsx"])
    uploaded_looks_file = st.file_uploader("Завантажте файл 'Looks worth' (Excel)", type=["xlsx"])
    uploaded_plans_file = st.file_uploader("Завантажте файл 'Plans worth' (Excel)", type=["xlsx"])
    uploaded_income_file = st.file_uploader("Завантажте файл 'Income plan' (Excel)", type=["xlsx"])
    uploaded_class_file = st.file_uploader("Завантажте файл 'Houses' (Excel)", type=["xlsx"])

    if uploaded_warehouse_file and uploaded_looks_file and uploaded_plans_file and uploaded_income_file and uploaded_class_file:
        try:
            data = load_data_from_uploaded_files(
                uploaded_warehouse_file,
                uploaded_looks_file,
                uploaded_plans_file,
                uploaded_income_file,
                uploaded_class_file
            )

            if data:
                warehouse_df, looks_df, plans_df, buildings_set, income_df, class_df = data
                st.success("Файли успішно завантажені!")

                # Вибір ЖК
                selected_building = st.selectbox("Оберіть ЖК:", sorted(buildings_set))

                if selected_building:
                    st.subheader(f"Інформація про ЖК: {selected_building}")

                    # Вивід базової інформації
                    stock_table = reload_stock_table(selected_building, warehouse_df, looks_df, plans_df)
                    display_df = warehouse_df.loc[warehouse_df['Дом'] == selected_building]
                    st.write("Таблиця STOCK:", stock_table)
                    st.write("Інформація про будинок:", display_df)

                    # Обробка базової гіпотези
                    config_path = "config_standart_1.ini"
                    config = load_config(config_path)
                    processed_data = process_basic(stock_table, display_df, config)

                    st.subheader("Базова гіпотеза")
                    st.write(processed_data)

                    # Завантаження результату
                    st.download_button(
                        label="Завантажити оброблену таблицю",
                        data=processed_data.to_csv(index=False).encode('utf-8'),
                        file_name=f"{selected_building}_processed.csv",
                        mime="text/csv",
                    )
            else:
                st.error("Помилка під час обробки файлів. Переконайтеся, що вони містять потрібні дані.")

        except Exception as e:
            st.error(f"Сталася помилка: {str(e)}")
    else:
        st.warning("Будь ласка, завантажте всі необхідні файли.")


def load_data_from_uploaded_files(warehouse_file, looks_file, plans_file, income_file, class_file):
    warehouse_df = pd.read_excel(warehouse_file) if warehouse_file else pd.DataFrame()
    looks_df = pd.read_excel(looks_file) if looks_file else pd.DataFrame()
    plans_df = pd.read_excel(plans_file) if plans_file else pd.DataFrame()
    income_df = pd.read_excel(income_file) if income_file else pd.DataFrame()
    class_df = pd.read_excel(class_file) if class_file else pd.DataFrame()

    if 'Дом' in warehouse_df:
        buildings_set = set(warehouse_df['Дом'].values)
        return warehouse_df, looks_df, plans_df, buildings_set, income_df, class_df
    else:
        st.error("Колонка 'Дом' не знайдена у файлі 'Warehouse'")
        return None, None, None, None, None, None


if __name__ == "__main__":
    main()
