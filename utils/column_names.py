import pandas as pd


COLUMN_NAMES = {
    "date": "Дата",
    "season": "Сезон",
    "city_name": "Город",
    "avg_temp_c": "Температура (°C)",
    "min_temp_c": "Минимальная температура (°C)",
    "max_temp_c": "Максимальная температура (°C)",
    "precipitation_mm": "Осадки (мм)",
    "snow_depth_mm": "Глубина снежного покрова (мм)",
    "avg_wind_speed_kmh": "Скорость ветра (км/ч)",
    "avg_wind_dir_deg": "Направление ветра (градусы)",
    "peak_wind_gust_kmh": "Порывы ветра (км/ч)",
    "avg_sea_level_pres_hpa": "Атмосферное давление (гПа)",
    "sunshine_total_min": "Продолжительность солнечного света (мин)",
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

MAIN_METRICS = [
    "avg_temp_c",
    "precipitation_mm",
    "avg_wind_speed_kmh",
    "avg_wind_dir_deg",
    "peak_wind_gust_kmh",
    "snow_depth_mm",
    "avg_sea_level_pres_hpa",
    # "sunshine_total_min"   # Не включаем, т.к. очень много пропусков
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
