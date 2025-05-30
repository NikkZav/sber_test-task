import pandas as pd


df = pd.read_parquet("data/daily_weather.parquet")


print("=== Основная информация о датасете ===")
print(f"Размер датасета: {df.shape}")
print("\nПервые 5 строк:")
print(df.head())
print("\nТипы данных:")
print(df.dtypes)
print("\nСтолбцы:", list(df.columns))


print("\n=== Диапазон дат ===")
print(f"Минимальная дата: {df['date'].min()}")
print(f"Максимальная дата: {df['date'].max()}")


print("\n=== Пропуски в данных ===")
missing = df.isna().sum()
missing_percent = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'Пропуски': missing, 'Процент': missing_percent})
print(missing_df[missing_df['Пропуски'] > 0])
print(f"\nВсего строк с хотя бы одним пропуском: {df.isna().any(axis=1).sum()}")


numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
print("\n=== Базовые статистики для числовых столбцов ===")
print(df[numeric_cols].describe().round(2))


print("\n=== Уникальные значения ===")
print(f"Количество уникальных городов: {df['city_name'].nunique()}")
print(f"Уникальные сезоны: {df['season'].unique()}")
print("\nЧастота сезонов:")
print(df['season'].value_counts())


print("\n=== Проверка экстремальных значений ===")
for col in numeric_cols:
    print(f"\nСтолбец: {col}")
    print(f"Минимальное: {df[col].min()}")
    print(f"Максимальное: {df[col].max()}")
    print(f"Среднее: {df[col].mean():.2f}")
    print(f"Медиана: {df[col].median():.2f}")


print("\n=== Корреляция между числовыми столбцами ===")
print(df[numeric_cols].corr().round(2))


print("\n=== Проверка дубликатов ===")
duplicates = df.duplicated(subset=['city_name', 'date']).sum()
print(f"Количество дубликатов (по городу и дате): {duplicates}")
