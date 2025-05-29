import io
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from pathlib import Path
import logging
from utils.constants import LIMIT_WEATHER_RECORDS

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("data/db.sqlite")


def prepare_data():
    """Подготавливает данные."""
    logger.info("Начало подготовки данных")

    # Проверка существования файлов
    required_files = ["data/countries.csv", "data/cities.csv", "data/daily_weather.parquet"]
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"Файл {file} не найден")
            raise FileNotFoundError(f"Файл {file} не найден")

    engine = create_engine(f'sqlite:///{DB_PATH}')

    # Загружаем данные о странах
    logger.info("Загрузка данных о стран")
    df_countries = pd.read_csv("data/countries.csv")
    df_countries.to_sql("countries", engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_country ON countries (country)"))
        conn.commit()

    # Загружаем данные о городах
    logger.info("Загрузка данных о городах")
    df_cities = pd.read_csv("data/cities.csv")
    df_cities.to_sql("cities", engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_city ON cities (city_name)"))
        conn.commit()

    # Загружаем данные о погоде
    logger.info("Загрузка данных о погоде")
    df_weather = pd.read_parquet("data/daily_weather.parquet")
    logger.info(f"Загружено {len(df_weather)} строк из daily_weather.parquet")

    # Нормализуем столбец date, убирая временную часть
    df_weather["date"] = pd.to_datetime(df_weather["date"]).dt.date

    # Записываем данные в SQLite по частям
    chunksize = 100000  # Размер чанка для записи
    total_rows = len(df_weather)
    for i in range(0, total_rows, chunksize):
        chunk = df_weather[i:i + chunksize]
        logger.info(f"Запись чанка {i // chunksize + 1} ({len(chunk)} строк)")
        chunk.to_sql("weather", engine, if_exists="append" if i > 0 else "replace", index=False)

    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_weather ON weather (date, city_name, season)"))
        conn.commit()

    logger.info("Подготовка данных завершена")


@st.cache_data
def get_countries() -> pd.DataFrame:
    """Возвращает данные о странах."""
    engine = create_engine(f'sqlite:///{DB_PATH}')
    with Session(engine) as session:
        stmt = select("*").select_from(text("countries"))
        df = pd.read_sql(stmt, session.bind)
    return df


@st.cache_data
def get_cities(countries: list = None) -> pd.DataFrame:
    """Возвращает данные о городах, возможно отфильтрованные по странам."""
    engine = create_engine(f'sqlite:///{DB_PATH}')
    with Session(engine) as session:
        if countries:
            # Формируем параметризованный запрос
            placeholders = ', '.join(['?' for _ in countries])
            query = f"SELECT * FROM cities WHERE country IN ({placeholders})"
            df = pd.read_sql(query, session.bind, params=tuple(countries))
        else:
            stmt = select("*").select_from(text("cities"))
            df = pd.read_sql(stmt, session.bind)
    return df


@st.cache_data
def get_weather(countries: list = None, cities: list = None,
                seasons: list = None, start_date=None, end_date=None) -> pd.DataFrame:
    """Возвращает данные о погоде с фильтрами."""
    engine = create_engine(f'sqlite:///{DB_PATH}')
    with Session(engine) as session:
        query = "SELECT * FROM weather"
        conditions = []
        params = []

        if start_date:
            conditions.append("date >= ?")
            params.append(pd.to_datetime(start_date).strftime('%Y-%m-%d'))
        if end_date:
            conditions.append("date <= ?")
            params.append(pd.to_datetime(end_date).strftime('%Y-%m-%d'))

        # Фильтр по городам
        final_cities = set()
        if cities:
            final_cities.update(cities)  # Используем только выбранные города
        elif countries:
            # Если города не выбраны, берём города из выбранных стран
            placeholders = ', '.join(['?' for _ in countries])
            cities_query = f"SELECT city_name FROM cities WHERE country IN ({placeholders})"
            cities_df = pd.read_sql(cities_query, session.bind, params=tuple(countries))
            final_cities.update(cities_df["city_name"].tolist())

        if final_cities:
            placeholders = ', '.join(['?' for _ in final_cities])
            conditions.append(f"city_name IN ({placeholders})")
            params.extend(list(final_cities))

        if seasons:
            placeholders = ', '.join(['?' for _ in seasons])
            conditions.append(f"season IN ({placeholders})")
            params.extend(seasons)

        if conditions:
            query += " WHERE " + " AND ".join(conditions) + f" LIMIT {LIMIT_WEATHER_RECORDS}"

        logger.info(f"Выполняется запрос: {query} с параметрами: {params}")
        df = pd.read_sql(query, session.bind, params=tuple(params))
        logger.info(f"Загружено {len(df)} записей")

    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


@st.cache_data
def get_weather_for_map(date, metric) -> pd.DataFrame:
    """Загружает данные о погоде для карты."""
    logger.info(f"Загрузка данных о погоде для карты на дату: {date} и метрику: {metric}")
    engine = create_engine(f'sqlite:///{DB_PATH}')
    with Session(engine) as session:
        query = f"SELECT city_name, date, {metric} FROM weather WHERE date = ?"
        logger.info(f"Выполняется запрос: {query} с параметром: {date}")
        df = pd.read_sql(query, session.bind, params=(pd.to_datetime(date).strftime('%Y-%m-%d'),))
        logger.info(f"Возвращено строк: {len(df)}")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def to_excel(df: pd.DataFrame, index=False, sheet_name="WeatherData") -> bytes:
    """Конвертирует DataFrame в Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=index, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()


if __name__ == "__main__":
    prepare_data()
