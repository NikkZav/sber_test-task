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


def load_weather(years: list = None, countries: list = None, cities: list = None,
                 seasons: list = None, start_date=None, end_date=None) -> pd.DataFrame:
    """Загружает погодные данные с фильтрацией."""
    data_path = Path("data/daily_weather.parquet")
    if not data_path.exists():
        return pd.DataFrame()

    filters = []
    if years:
        filters.append(("date", ">=", pd.to_datetime(f"{min(years)}-01-01")))
        filters.append(("date", "<=", pd.to_datetime(f"{max(years)}-12-31")))
    if countries:
        cities_df = load_cities(countries)
        cities_list = cities_df["city_name"].unique().tolist()
        filters.append(("city_name", "in", cities_list))
    if cities:
        filters.append(("city_name", "in", cities))
    if seasons:
        filters.append(("season", "in", seasons))
    if start_date:
        filters.append(("date", ">=", start_date))
    if end_date:
        filters.append(("date", "<=", end_date))

    df = pd.read_parquet(data_path, filters=filters if filters else None)
    df["date"] = pd.to_datetime(df["date"])
    return df
