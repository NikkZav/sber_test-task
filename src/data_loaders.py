import pandas as pd
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pathlib import Path
from utils.constants import CHUNK_SIZE
from utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

DB_PATH = Path("./data/db.sqlite")


def check_files_exist(required_files: list[str]) -> None:
    """ Проверяет наличие необходимых файлов."""
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"Файл {file} не найден")
            raise FileNotFoundError(f"Файл {file} не найден")


def load_countries(engine: Engine) -> None:
    """Загружает данные о странах в базу данных."""
    logger.info("Загрузка данных о странах")
    df_countries = pd.read_csv("data/countries.csv")
    df_countries.to_sql("countries", engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_country ON countries (country)"))
        conn.commit()


def load_cities(engine: Engine) -> None:
    """Загружает данные о городах в базу данных."""
    logger.info("Загрузка данных о городах")
    df_cities = pd.read_csv("data/cities.csv")
    df_cities.to_sql("cities", engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_city ON cities (city_name)"))
        conn.commit()


def load_weather(engine: Engine) -> None:
    """Загружает данные о погоде в базу данных по частям."""
    logger.info("Загрузка данных о погоде")
    try:
        df_weather = pd.read_parquet("data/daily_weather.parquet")
        logger.info(f"Загружено {len(df_weather)} строк из daily_weather.parquet")
    except Exception as e:
        logger.error(f"Ошибка при чтении daily_weather.parquet: {e}")
        raise

    df_weather["date"] = pd.to_datetime(df_weather["date"]).dt.date

    total_rows = len(df_weather)
    for i in range(0, total_rows, CHUNK_SIZE):
        chunk = df_weather[i:i + CHUNK_SIZE]
        logger.info(f"Запись чанка {i // CHUNK_SIZE + 1} ({len(chunk)} строк)")
        chunk.to_sql("weather", engine, if_exists="append" if i > 0 else "replace", index=False)

    with engine.connect() as conn:
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_weather ON weather (date, city_name, season)"
        ))
        conn.commit()


def prepare_data() -> None:
    """Подготавливает данные, загружая страны, города и погоду в базу данных."""
    logger.info("Начало подготовки данных")

    required_files = ["data/countries.csv", "data/cities.csv", "data/daily_weather.parquet"]
    check_files_exist(required_files)

    engine = create_engine(f'sqlite:///{DB_PATH}')
    load_countries(engine)
    load_cities(engine)
    load_weather(engine)

    logger.info("Подготовка данных завершена")


if __name__ == "__main__":
    setup_logging()
    prepare_data()
