import io
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, select, and_, Table, MetaData
from sqlalchemy.orm import Session
from pathlib import Path
import logging
from utils.constants import LIMIT_WEATHER_RECORDS

logger = logging.getLogger(__name__)

DB_PATH = Path("./data/db.sqlite")
logger.info(f"Путь к базе данных: {DB_PATH.resolve()}")

try:
    engine = create_engine(f'sqlite:///{DB_PATH}')
except Exception as e:
    logger.error(f"Ошибка при создании подключения к базе данных: {e}")
    raise

metadata = MetaData()

try:
    countries_table = Table("countries", metadata, autoload_with=engine)
    cities_table = Table("cities", metadata, autoload_with=engine)
    weather_table = Table("weather", metadata, autoload_with=engine)
except Exception as e:
    logger.error(f"Ошибка при загрузке таблиц из базы данных: {e}")
    raise

@st.cache_data
def get_countries() -> pd.DataFrame:
    """Возвращает данные о странах."""
    logger.info("Загрузка данных о странах")
    with Session(engine) as session:
        stmt = select(countries_table)
        df = pd.read_sql(stmt, session.bind)
        logger.info(f"Загружено {len(df)} стран")
    return df


@st.cache_data
def get_cities(countries: list[str] | None = None) -> pd.DataFrame:
    """Возвращает данные о городах, возможно отфильтрованные по странам."""
    logger.info(f"Загрузка данных о городах с фильтром по странам: {countries}")
    with Session(engine) as session:
        stmt = select(cities_table)
        if countries:
            stmt = stmt.where(cities_table.c.country.in_(countries))
        df = pd.read_sql(stmt, session.bind)
        logger.info(f"Загружено {len(df)} городов")
    return df


@st.cache_data
def get_weather(
    countries: list[str] | None = None,
    cities: list[str] | None = None,
    seasons: list[str] | None = None,
    start_date=None,
    end_date=None
) -> pd.DataFrame:
    """Возвращает данные о погоде с фильтрами."""
    logger.info("Начало загрузки данных о погоде")
    with Session(engine) as session:
        final_cities = set()
        if cities:
            final_cities.update(cities)
        elif countries:
            cities_stmt = select(
                cities_table.c.city_name
            ).where(cities_table.c.country.in_(countries))
            cities_df = pd.read_sql(cities_stmt, session.bind)
            final_cities.update(cities_df["city_name"].tolist())

        stmt = select(weather_table)
        conditions = []

        if start_date:
            start_date_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
            conditions.append(weather_table.c.date >= start_date_str)
        if end_date:
            end_date_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
            conditions.append(weather_table.c.date <= end_date_str)
        if final_cities:
            conditions.append(weather_table.c.city_name.in_(final_cities))
        if seasons:
            conditions.append(weather_table.c.season.in_(seasons))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(LIMIT_WEATHER_RECORDS)

        logger.info(f"Выполняется запрос с фильтрами: cities={len(final_cities)}, "
                    f"seasons={seasons}, start_date={start_date}, end_date={end_date}")
        try:
            df = pd.read_sql(stmt, session.bind)
            logger.info(f"Загружено {len(df)} записей")
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    df["date"] = pd.to_datetime(df["date"]).dt.date
    logger.info("Завершение загрузки данных о погоде")
    return df


@st.cache_data
def get_weather_for_map(date, metric: str) -> pd.DataFrame:
    """Загружает данные о погоде для карты."""
    logger.info(f"Загрузка данных о погоде для карты на дату: {date} и метрику: {metric}")
    with Session(engine) as session:
        stmt = select(
            weather_table.c.city_name,
            weather_table.c.date,
            weather_table.c[metric]
        ).where(
            weather_table.c.date == pd.to_datetime(date).strftime('%Y-%m-%d')
        )
        logger.info(f"Выполняется запрос для карты с параметром date={date}")
        try:
            df = pd.read_sql(stmt, session.bind)
            logger.info(f"Возвращено строк: {len(df)}")
            logger.info(f"Уникальных городов: {df['city_name'].nunique()}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных для карты: {e}")
            raise
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def to_excel(df: pd.DataFrame, index: bool = False, sheet_name: str = "WeatherData") -> bytes:
    """Конвертирует DataFrame в Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=index, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()
