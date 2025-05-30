import streamlit as st
import pandas as pd
from repository import get_countries, get_cities
from utils.constants import MIN_DATE, MAX_DATE, DEFAULT_START, DEFAULT_END, DAFAULT_TIMELINE_START
import logging

logger = logging.getLogger(__name__)


def get_filters():
    """Создаёт фильтры в боковой панели."""
    st.sidebar.header("Фильтры данных")
    countries_df = get_countries()
    selected_countries = st.sidebar.multiselect(
        "Выберите страны",
        countries_df["country"].unique(),
        default=["Russia"],
        key="countries_multiselect"
    )
    cities_df = get_cities(selected_countries)
    available_cities = cities_df["city_name"].unique()
    default_cities = ["Saint Petersburg"] if "Saint Petersburg" in available_cities \
        else [available_cities[0]]
    selected_cities = st.sidebar.multiselect(
        "Выберите города",
        available_cities,
        default=default_cities,
        key="cities_multiselect"
    )

    full_timeline_checkbox = st.sidebar.checkbox(
        "Показать весь диапазон дат",
        value=False,
        key="full_range_checkbox"
    )

    default_start = st.session_state.get(
        "start_date",
        st.session_state.get("time_range_slider", (DEFAULT_START, DEFAULT_END))[0]
    )
    default_end = st.session_state.get(
        "end_date",
        st.session_state.get("time_range_slider", (DEFAULT_START, DEFAULT_END))[1]
    )
    default_range = default_start, default_end
    # Слайдер в днях
    time_range = st.sidebar.slider(
        "Выберите временной промежуток",
        value=default_range,
        min_value=MIN_DATE if full_timeline_checkbox else DAFAULT_TIMELINE_START,
        max_value=MAX_DATE,
        format="YYYY.MM.DD",
        key="time_range_slider"
    )
    # Уточнение дат
    st.sidebar.text("Уточните даты, если нужно")
    start_date = st.sidebar.date_input(
        "От даты",
        value=time_range[0],
        min_value=MIN_DATE,
        max_value=st.session_state.get("end_date", MAX_DATE),
        format="YYYY.MM.DD",
        key="start_date"
    )
    end_date = st.sidebar.date_input(
        "До даты",
        value=time_range[1],
        min_value=st.session_state.get("start_date", MIN_DATE),
        max_value=MAX_DATE,
        format="YYYY.MM.DD",
        key="end_date"
    )

    selected_days = (end_date - start_date).days
    st.sidebar.title(
        f"Выбран{'о' if selected_days != 1 else ''} {selected_days} "
        f"{'дней' if selected_days > 4 or selected_days == 0
           else ('день' if selected_days == 1 else 'дня')}"
    )

    seasons = ["Spring", "Summer", "Autumn", "Winter"]
    selected_seasons = st.sidebar.multiselect(
        "Выберите сезоны",
        seasons,
        default=seasons,
        key="seasons_multiselect"
    )

    return selected_countries, selected_cities, selected_seasons, start_date, end_date
