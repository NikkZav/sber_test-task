import io
import streamlit as st
import pandas as pd
from pathlib import Path


def load_countries() -> pd.DataFrame:
    """Загружает данные о странах из countries.csv."""
    return pd.read_csv("data/countries.csv")


def load_cities(countries: list = None) -> pd.DataFrame:
    """Загружает данные о городах, фильтруя по странам."""
    df = pd.read_csv("data/cities.csv")
    if countries:
        df = df[df["country"].isin(countries)]
    return df


def load_weather(countries: list = None, cities: list = None,
                 seasons: list = None, start_date=None, end_date=None) -> pd.DataFrame:
    """Загружает погодные данные с фильтрацией."""
    data_path = Path("data/daily_weather.parquet")
    if not data_path.exists():
        return pd.DataFrame()

    filters = []
    if start_date:
        filters.append(("date", ">=", pd.to_datetime(start_date)))
    if end_date:
        filters.append(("date", "<=", pd.to_datetime(end_date)))
    if countries:
        cities_df = load_cities(countries)
        cities_list = cities_df["city_name"].unique().tolist()
        filters.append(("city_name", "in", cities_list))
    if cities:
        filters.append(("city_name", "in", cities))
    if seasons:
        filters.append(("season", "in", seasons))

    df = pd.read_parquet(data_path, filters=filters if filters else None)
    df["date"] = df["date"].dt.date  # Преобразуем в чистую дату
    return df


@st.cache_data
def load_weather_for_map(date, metric):
    filters = [("date", "==", pd.to_datetime(date))]
    columns = ["city_name", "date", metric]
    df = pd.read_parquet("data/daily_weather.parquet", filters=filters, columns=columns)
    df["date"] = df["date"].dt.date
    return df


def to_excel(df: pd.DataFrame) -> bytes:
    """Конвертирует DataFrame в Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="WeatherData")
    output.seek(0)
    return output.getvalue()


def get_filters():
    """Создаёт фильтры в боковой панели."""
    st.sidebar.header("Фильтры данных")
    countries_df = load_countries()
    selected_countries = st.sidebar.multiselect(
        "Выберите страны",
        countries_df["country"].unique(),
        default=["Russia"]
    )
    cities_df = load_cities(selected_countries)
    available_cities = cities_df["city_name"].unique()
    default_cities = ["Saint Petersburg"] if "Saint Petersburg" in available_cities \
        else [available_cities[0]]
    selected_cities = st.sidebar.multiselect(
        "Выберите города",
        available_cities,
        default=default_cities
    )
    min_date = pd.to_datetime("1957-01-01").date()
    max_date = pd.to_datetime("2023-12-31").date()
    default_start = pd.to_datetime("2020-01-01").date()
    default_end = pd.to_datetime("2023-12-31").date()

    # Слайдер в днях
    time_range = st.sidebar.slider(
        "Выберите временной промежуток",
        min_value=min_date,
        max_value=max_date,
        value=(default_start, default_end),
        format="YYYY.MM.DD",
        key="time_range_slider"
    )
    # Уточнение дат
    time_range_exactly = st.sidebar.date_input(
        "Можете уточнить даты",
        time_range,
        min_value=min_date,
        max_value=max_date,
        format="YYYY.MM.DD"
    )
    if len(time_range_exactly) == 2:
        start_date, end_date = time_range_exactly
    else:
        start_date, end_date = max(time_range_exactly[0], time_range[0]), time_range[1]

    seasons = ["Spring", "Summer", "Autumn", "Winter"]
    selected_seasons = st.sidebar.multiselect("Выберите сезоны", seasons, default=seasons)

    return selected_countries, selected_cities, selected_seasons, start_date, end_date
