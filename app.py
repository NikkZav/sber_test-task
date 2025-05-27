import streamlit as st
import pandas as pd
import plotly.express as px
import io
from pathlib import Path

# Загрузка данных с оптимизацией
@st.cache_data
def load_data(years=None, cities=None, seasons=None):
    data_path = Path("data/daily_weather.parquet")
    if not data_path.exists():
        st.error("Файл daily_weather.parquet не найден в папке data/")
        return pd.DataFrame()
    
    # Фильтрация по годам, городам, сезонам на этапе загрузки
    filters = []
    if years:
        filters.append(("date", ">=", pd.to_datetime(f"{min(years)}-01-01")))
        filters.append(("date", "<=", pd.to_datetime(f"{max(years)}-12-31")))
    if cities:
        filters.append(("city_name", "in", cities))
    if seasons:
        filters.append(("season", "in", seasons))
    
    df = pd.read_parquet(data_path, filters=filters if filters else None)
    df["date"] = pd.to_datetime(df["date"])
    return df


# Основная функция
def main():
    st.title("Погодный дашборд")

    # Загрузка данных
    years = st.sidebar.slider("Выберите годы", 1957, 2023, (2020, 2023))  # Ограничение по годам
    cities_df = pd.read_csv("data/cities.csv")
    available_cities = cities_df["city_name"].unique()
    default_cities = ["Saint Petersburg"] if "Saint Petersburg" in available_cities \
        else [available_cities[0]]
    cities = st.sidebar.multiselect("Выберите города", available_cities, default=default_cities)
    name_seasons = ["Spring", "Summer", "Autumn", "Winter"]
    seasons = st.sidebar.multiselect("Выберите сезоны", name_seasons, default=name_seasons)

    # Загрузка данных с фильтрацией
    df = load_data(years, cities, seasons)
    
    if df.empty:
        st.warning("Нет данных для выбранных параметров.")
        return

    # Фильтрация данных
    date_range = st.sidebar.date_input("Выберите диапазон дат", [df["date"].min(), df["date"].max()])
    if len(date_range) != 2:
        st.warning("Пожалуйста, выберите полный диапазон дат.")
        return
    
    filtered_df = df[
        (df["date"] >= pd.to_datetime(date_range[0])) & 
        (df["date"] <= pd.to_datetime(date_range[1])) & 
        (df["city_name"].isin(cities)) & 
        (df["season"].isin(seasons))
    ]

    if filtered_df.empty:
        st.warning("Нет данных после применения фильтров.")
        return

    # Метрики
    st.subheader("Ключевые метрики")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_temp = filtered_df["avg_temp_c"].mean()
        st.metric("Средняя температура", f"{avg_temp:.2f} °C")
    with col2:
        median_temp = filtered_df["avg_temp_c"].median()
        st.metric("Медиана температуры", f"{median_temp:.2f} °C")
    with col3:
        precip_days = (filtered_df["precipitation_mm"] > 0).sum() / len(filtered_df) * 100
        st.metric("Доля дней с осадками", f"{precip_days:.2f}%")
    with col4:
        wind_speed = filtered_df["avg_wind_speed_kmh"].mean()
        st.metric("Средняя скорость ветра", f"{wind_speed:.2f} км/ч")

    # Выбор типа графика
    st.subheader("Визуализация")
    plot_type = st.selectbox("Выберите тип графика", ["Линейный", "Scatter", "Гистограмма"])
    
    if plot_type == "Линейный":
        fig = px.line(
            filtered_df, 
            x="date", 
            y="avg_temp_c", 
            color="city_name", 
            title="Динамика средней температуры",
            labels={"avg_temp_c": "Температура (°C)", "date": "Дата", "city_name": "Город"}
        )
    elif plot_type == "Scatter":
        fig = px.scatter(
            filtered_df, 
            x="avg_temp_c", 
            y="precipitation_mm", 
            color="season", 
            title="Температура vs Осадки",
            labels={"avg_temp_c": "Температура (°C)", "precipitation_mm": "Осадки (мм)"}
        )
    else:
        fig = px.histogram(
            filtered_df, 
            x="avg_temp_c", 
            color="city_name", 
            title="Распределение температуры",
            labels={"avg_temp_c": "Температура (°C)"}
        )
    st.plotly_chart(fig, use_container_width=True)

    # Таблица
    st.subheader("Данные")
    st.dataframe(
        filtered_df[["date", "city_name", "avg_temp_c", "precipitation_mm", "season", "avg_wind_speed_kmh"]],
        column_config={
            "date": "Дата",
            "city_name": "Город",
            "avg_temp_c": "Температура (°C)",
            "precipitation_mm": "Осадки (мм)",
            "season": "Сезон",
            "avg_wind_speed_kmh": "Скорость ветра (км/ч)"
        }
    )

    # Скачивание данных в .xlsx
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="WeatherData")
        return output.getvalue()

    st.download_button(
        label="Скачать данные в .xlsx",
        data=to_excel(filtered_df[["date", "city_name", "avg_temp_c", "precipitation_mm", "season", "avg_wind_speed_kmh"]]),
        file_name="weather_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
