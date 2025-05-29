import pandas as pd


COLUMN_NAMES = {
    "date": "Дата",
    "city_name": "Город",
    "avg_temp_c": "Температура (°C)",
    "min_temp_c": "Минимальная температура (°C)",
    "max_temp_c": "Максимальная температура (°C)",
    "precipitation_mm": "Осадки (мм)",
    "snow_depth_mm": "Глубина снежного покрова (мм)",
    "avg_wind_speed_kmh": "Скорость ветра (км/ч)",
    "avg_wind_dir_deg": "Направление ветра (градусы)",
    "sunshine_total_min": "Продолжительность солнечного света (мин)",
    "season": "Сезон",
}

STATISTICS_NAMES = {
    "sum": "Сумма",
    "mean": "Среднее",
    "median": "Медиана",
    "count": "Количество",
    "min": "Минимум",
    "max": "Максимум",
}

SEASON_NAMES = {
    "Winter": "Зима",
    "Spring": "Весна",
    "Summer": "Лето",
    "Autumn": "Осень",
}

NUMBERS_FEATURES = [
    "avg_temp_c",
    "precipitation_mm",
    "avg_wind_speed_kmh",
    "avg_wind_dir_deg",
    "snow_depth_mm",
]


def rename_column(col, translation_dict: dict):
    """Рекурсивно переименовывает столбец, сохраняя его структуру."""
    if isinstance(col, str):  # Обычный столбец (например, 'season')
        return translation_dict.get(col, col)
    elif isinstance(col, tuple):  # Мультииндекс (например, ('avg_temp_c', 'mean'))
        return tuple(rename_column(field, translation_dict) for field in col)
    else:  # Неожиданный тип
        return col


def rename_columns(columns, translation_dict: dict) -> pd.MultiIndex:
    """Переименовывает все столбцы, используя рекурсию."""
    return pd.MultiIndex.from_tuples(
        rename_column(col, translation_dict) for col in columns
    )
