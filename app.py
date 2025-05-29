import streamlit as st
from data import get_weather
from views.main_dashboard import (display_metrics, display_charts_and_histograms,
                                  display_table, display_download_button)
from views.additional_dashboard import display_additional_metrics
from views.sidebar import get_filters
from utils.constants import LIMIT_WEATHER_RECORDS


def main():
    """Основная функция приложения."""
    st.title("Погодный дашборд")

    weather_df = get_weather(*get_filters())

    if weather_df.empty:
        st.warning("Нет данных для выбранных фильтров.")
        return

    if len(weather_df) == LIMIT_WEATHER_RECORDS:
        st.warning(f"Под текущие параметры попадает слишком много данных "
                   f"поэтому они были ограничены первыми {LIMIT_WEATHER_RECORDS} записями.")
        st.warning("Пожалуйста выберите меньший временной диапазон "
                   "или территориальную область, чтобы получить результат целиком!")

    tab1, tab2 = st.tabs(["Основной дашборд", "Дополнительные метрики"])
    with tab1:
        display_metrics(weather_df)
        display_charts_and_histograms(weather_df)
        display_table(weather_df)
        display_download_button(weather_df)
    with tab2:
        display_additional_metrics(weather_df)


if __name__ == "__main__":
    main()
