import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils.column_names import COLUMN_NAMES, MAIN_METRICS
from data import get_cities, get_weather_for_map, to_excel
from services import metrics_calculator as metrics
from utils.constants import MIN_DATE, MAX_DATE

# Настройка логирования
logger = logging.getLogger(__name__)


def create_map(map_df: pd.DataFrame, value_col: str = "avg_temp_c") -> px.scatter_geo:
    """Создаёт карту с городами."""
    map_df = map_df.copy()
    map_df[value_col] = map_df[value_col].fillna(0)  # Заполняем NaN нулями
    fig = px.scatter_geo(
        map_df, lat="lat", lon="lng", hover_name="city_name",
        color=map_df[value_col],
        projection="natural earth",
        title=f"Карта: {COLUMN_NAMES.get(value_col, value_col)}"
    )
    return fig


def display_additional_metrics(df: pd.DataFrame):
    """Отображает дополнительные метрики."""
    logger.info("Отображение дополнительных метрик")
    st.subheader("Дополнительные метрики")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Диапазон средней температуры",
                  '…'.join([f'{temp:+.2f}' for temp in metrics.calculate_range_temp(df)]) + " °C")
        st.metric("Разница экстремальных температур",
                  f"{metrics.calculate_extreme_temp_diff(df):.2f} °C")
        st.metric("Преобладающее направление ветра", metrics.calculate_wind_direction_mode(df))
        st.metric("Максимальный порыв ветра", f"{metrics.calculate_max_wind_gust(df):.2f} км/ч")
    with col2:
        st.metric("Средний уровень осадков", f"{metrics.calculate_avg_precip(df):.2f} мм")
        st.metric("Дни с дождём", metrics.calculate_rain_days(df))
        st.metric("Дни со снегом", metrics.calculate_snow_days(df))
        st.metric("Корреляция температуры и осадков",
                  f"{metrics.calculate_temp_precip_corr(df):.2f}")


def display_seasonal_statistics(df: pd.DataFrame):
    """Отображает статистику по сезонам."""
    logger.info("Отображение статистики по сезонам")
    st.subheader("Статистика по сезонам")

    seasonal_trends = metrics.calculate_seasonal_statistics(df, metrics=MAIN_METRICS)

    st.dataframe(
        seasonal_trends,
        column_config={"widgets": st.column_config.Column(width="small")},
        key="seasonal_trends_table"
    )


def display_download_button(df: pd.DataFrame):
    """Отображает кнопку для скачивания данных."""
    st.download_button(
        label="Скачать данные в .xlsx",
        data=to_excel(df=metrics.calculate_seasonal_statistics(df, metrics=MAIN_METRICS),
                      index=True,
                      sheet_name="SeasonalTrends"),
        file_name="seasonal_trends.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def display_map(df: pd.DataFrame):
    """Отображает карту."""
    logger.info("Отображение карты")
    st.subheader("Карта")

    selected_date = st.date_input(
        "Выберите дату для карты",
        min_value=MIN_DATE,
        max_value=MAX_DATE,
        value=df["date"].min(),
        format="YYYY.MM.DD"
    )
    metric_map = st.selectbox(
        "Метрика для карты",
        MAIN_METRICS,
        index=MAIN_METRICS.index("avg_temp_c"),
        format_func=lambda x: COLUMN_NAMES[x],
        key="map_metric",
    )
    map_df = get_weather_for_map(selected_date, metric_map)
    agg_df = map_df.groupby("city_name")[metric_map].mean().reset_index()
    cities_df = get_cities()
    map_data = pd.merge(agg_df, cities_df[["city_name", "latitude", "longitude"]], on="city_name")
    map_data.rename(columns={"latitude": "lat", "longitude": "lng"}, inplace=True)
    fig_map = create_map(map_data, value_col=metric_map)
    st.plotly_chart(fig_map, use_container_width=True)
