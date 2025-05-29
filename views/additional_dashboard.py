import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils.column_names import COLUMN_NAMES
from data import get_weather, get_cities, get_weather_for_map
from services.metrics_calculator import (
    calculate_extreme_temp_diff, calculate_temp_anomaly, calculate_avg_precip,
    calculate_temp_precip_corr, calculate_snow_days, calculate_wind_direction_mode,
    calculate_seasonal_trends
)
from utils.constants import MIN_DATE, MAX_DATE

# Настройка логирования
logger = logging.getLogger(__name__)


def create_map(map_df: pd.DataFrame, value_col: str = "avg_temp_c",
               mode: str = "color") -> px.scatter_geo:
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
    # Получаем фильтры из st.session_state
    countries = st.session_state.get("countries_multiselect", ["Russia"])
    cities = st.session_state.get("cities_multiselect", ["Saint Petersburg"])
    seasons = st.session_state.get("seasons_multiselect", ["Spring", "Summer", "Autumn", "Winter"])

    # Запрашиваем исторические данные с теми же фильтрами, но за 2010–2020
    # historical_df = get_weather(
    #     countries=countries,
    #     cities=cities,
    #     seasons=seasons,
    #     start_date="1990-01-01",
    #     end_date="2020-12-31"
    # )
    # logger.info(f"Размер historical_df: {historical_df.shape}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Разница экстремальных температур", f"{calculate_extreme_temp_diff(df):.2f} °C")
        # st.metric("Температурная аномалия", f"{calculate_temp_anomaly(df, historical_df):.2f} °C")
        st.metric("Средний уровень осадков", f"{calculate_avg_precip(df):.2f} мм")
    with col2:
        st.metric("Дни со снегом", calculate_snow_days(df))
        st.metric("Преобладающее направление ветра", calculate_wind_direction_mode(df))
        st.metric("Корреляция температуры и осадков", f"{calculate_temp_precip_corr(df):.2f}")

    st.subheader("Сезонные тренды")
    seasonal_trends = calculate_seasonal_trends(df)
    st.dataframe(
        seasonal_trends,
        column_config={
            "season": "Сезон",
            "avg_temp_c": "Средняя температура (°C)"
        }
    )

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
        ["avg_temp_c", "precipitation_mm", "avg_wind_speed_kmh"],
        key="map_metric",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    map_df = get_weather_for_map(selected_date, metric_map)
    logger.info(f"Map data shape: {map_df.shape}")
    agg_df = map_df.groupby("city_name")[metric_map].mean().reset_index()
    cities_df = get_cities()
    map_data = pd.merge(agg_df, cities_df[["city_name", "latitude", "longitude"]], on="city_name")
    map_data.rename(columns={"latitude": "lat", "longitude": "lng"}, inplace=True)
    fig_map = create_map(map_data, value_col=metric_map, mode="color")
    st.plotly_chart(fig_map, use_container_width=True)
