import pandas as pd
import streamlit as st
from utils.column_names import COLUMN_NAMES, STATISTICS_NAMES, SEASON_NAMES, rename_columns


def calculate_avg_temp(df: pd.DataFrame) -> float:
    """Рассчитывает среднюю температуру."""
    return df["avg_temp_c"].mean() if not df.empty else 0.0


def calculate_median_temp(df: pd.DataFrame) -> float:
    """Рассчитывает медиану температуры."""
    return df["avg_temp_c"].median() if not df.empty else 0.0


def calculate_precip_days(df: pd.DataFrame) -> float:
    """Рассчитывает долю дней с осадками."""
    days_with_precipitation = df[(df["precipitation_mm"] > 0) | (df["snow_depth_mm"] > 0)]
    return len(days_with_precipitation) / len(df) * 100 if not df.empty else 0.0


def calculate_avg_wind_speed(df: pd.DataFrame) -> float:
    """Рассчитывает среднюю скорость ветра."""
    return df["avg_wind_speed_kmh"].mean() if not df.empty else 0.0


# Дополнительные метрики


def calculate_range_temp(df: pd.DataFrame) -> tuple[float, float]:
    """Рассчитывает диапазон средней температуры."""
    return df["avg_temp_c"].min(), df["avg_temp_c"].max()


def calculate_extreme_temp_diff(df: pd.DataFrame) -> float:
    """Рассчитывает разницу между максимальной и минимальной температурой."""
    return df["max_temp_c"].max() - df["min_temp_c"].min() if not df.empty else 0.0


def calculate_avg_precip(df: pd.DataFrame) -> float:
    """Рассчитывает средний уровень осадков."""
    return df["precipitation_mm"].mean() if not df.empty else 0.0


def calculate_rain_days(df: pd.DataFrame) -> int:
    """Рассчитывает количество дней с дождём."""
    return (df["precipitation_mm"] > 0).sum() if not df.empty else 0


def calculate_snow_days(df: pd.DataFrame) -> int:
    """Рассчитывает количество дней со снегом."""
    return (df["snow_depth_mm"] > 0).sum() if not df.empty else 0


def calculate_wind_direction_mode(df: pd.DataFrame) -> str:
    """Определяет преобладающее направление ветра."""
    if df["avg_wind_dir_deg"].dropna().empty:
        return "Нет данных"
    bins = [0, 45, 90, 135, 180, 225, 270, 315, 360]
    labels = ["Север", "Сев.-Вост.", "Восток", "Юг.-Вост.", "Юг", "Юг.-Зап.", "Запад", "Сев.-Зап."]
    wind_dir = pd.cut(df["avg_wind_dir_deg"], bins=bins, labels=labels, include_lowest=True)
    return wind_dir.mode()[0] if not wind_dir.mode().empty else "Нет данных"


def calculate_max_wind_gust(df: pd.DataFrame) -> float:
    """Определяет максимальную скорость порывов ветра."""
    return df["peak_wind_gust_kmh"].max()


def calculate_temp_precip_corr(df: pd.DataFrame) -> float:
    """Рассчитывает корреляцию между температурой и осадками."""
    return df[["avg_temp_c", "precipitation_mm"]].corr().iloc[0, 1] if not df.empty else 0.0


@st.cache_data
def calculate_seasonal_statistics(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Рассчитывает средни показатели по сезонам."""
    if df.empty:
        return pd.DataFrame()
    seasonal_stat = df[metrics + ["season"]].groupby("season").agg(
        ['mean', 'median', 'min', 'max']
    )
    # Упорядочиваем строки в порядке Зима → Весна → Лето → Осень
    seasonal_stat = seasonal_stat.reindex(SEASON_NAMES.keys())

    # В Streamlit не работает column_config в dataframe когда есть multi-index, поэтому сразу
    # Переводим индекс season на русский
    seasonal_stat.index = [SEASON_NAMES.get(season, season) for season in seasonal_stat.index]
    # Переводим столбцы
    seasonal_stat.columns = rename_columns(seasonal_stat.columns,
                                           translation_dict={**COLUMN_NAMES, **STATISTICS_NAMES})
    print(seasonal_stat.head())
    return seasonal_stat
