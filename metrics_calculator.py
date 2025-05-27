import pandas as pd


def calculate_avg_temp(df: pd.DataFrame) -> float:
    """Рассчитывает среднюю температуру."""
    return df["avg_temp_c"].mean() if not df.empty else 0.0


def calculate_median_temp(df: pd.DataFrame) -> float:
    """Рассчитывает медиану температуры."""
    return df["avg_temp_c"].median() if not df.empty else 0.0


def calculate_precip_days(df: pd.DataFrame) -> float:
    """Рассчитывает долю дней с осадками."""
    return (df["precipitation_mm"] > 0).sum() / len(df) * 100 if not df.empty else 0.0


def calculate_avg_wind_speed(df: pd.DataFrame) -> float:
    """Рассчитывает среднюю скорость ветра."""
    return df["avg_wind_speed_kmh"].mean() if not df.empty else 0.0
