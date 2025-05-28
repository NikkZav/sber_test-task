import streamlit as st
import pandas as pd
import io
from data import load_weather, get_filters
from views.main_dashboard import (display_metrics, display_visualizations,
                                  display_table, display_download_button)
from views.additional_dashboard import display_additional_metrics
from utils.column_names import COLUMN_NAMES


def main():
    """Основная функция приложения."""
    st.title("Погодный дашборд")

    weather_df = load_weather(*get_filters())

    if weather_df.empty:
        st.warning("Нет данных для выбранных фильтров.")
        return

    if len(weather_df) > 50000:
        st.warning("Под текущие параметры попадает слишком много данных "
                   "и они не смогут нормально отобразиться. "
                   "Пожалуйста выберите меньший временной диапазон "
                   "или территориальную область!")
        return

    tab1, tab2 = st.tabs(["Основной дашборд", "Дополнительные метрики"])
    with tab1:
        display_metrics(weather_df)
        display_visualizations(weather_df)
        display_table(weather_df)
        display_download_button(weather_df)
    with tab2:
        display_additional_metrics(weather_df)


if __name__ == "__main__":
    main()
