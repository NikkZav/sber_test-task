import streamlit as st
from repository import get_weather
from views import main_dashboard, additional_dashboard, sidebar
from utils.constants import LIMIT_WEATHER_RECORDS
from utils.logging_config import setup_logging


def main():
    """Основная функция приложения."""
    st.title("Погодный дашборд")

    weather_df = get_weather(*sidebar.get_filters())

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
        main_dashboard.display_metrics(weather_df)
        main_dashboard.display_charts_and_histograms(weather_df)
        main_dashboard.display_table(weather_df)
        main_dashboard.display_download_button(weather_df)
    with tab2:
        additional_dashboard.display_additional_metrics(weather_df)
        additional_dashboard.display_seasonal_statistics(weather_df)
        additional_dashboard.display_download_button(weather_df)
        additional_dashboard.display_map(weather_df)


if __name__ == "__main__":
    setup_logging()
    main()
