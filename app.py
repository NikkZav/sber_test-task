import streamlit as st
import pandas as pd
import io
from data_loader import load_countries, load_cities, load_weather
from metrics_calculator import calculate_avg_temp, calculate_median_temp
from metrics_calculator import calculate_precip_days, calculate_avg_wind_speed
from visualizations import (create_line_plot, create_scatter_plot,
                            create_histogram, create_map)


def to_excel(df: pd.DataFrame) -> bytes:
    """Конвертирует DataFrame в Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="WeatherData")
    output.seek(0)
    return output.getvalue()


def get_filters():
    """Создаёт фильтры в боковой панели."""
    st.sidebar.header("Фильтры данных")
    countries_df = load_countries()
    selected_countries = st.sidebar.multiselect(
        "Выберите страны",
        countries_df["country"].unique(),
        default=["Russia"]
    )
    cities_df = load_cities(selected_countries)
    available_cities = cities_df["city_name"].unique()
    default_cities = ["Saint Petersburg"] if "Saint Petersburg" in available_cities else [available_cities[0]]
    selected_cities = st.sidebar.multiselect(
        "Выберите города",
        available_cities,
        default=default_cities
    )
    selected_years = st.sidebar.slider("Выберите годы", 1957, 2023, (2020, 2023))
    seasons = ["Spring", "Summer", "Autumn", "Winter"]
    selected_seasons = st.sidebar.multiselect("Выберите сезоны", seasons, default=seasons)
    date_range = st.sidebar.date_input(
        "Выберите диапазон дат",
        [pd.to_datetime(f"{selected_years[0]}-01-01"), pd.to_datetime(f"{selected_years[1]}-12-31")]
    )
    return selected_countries, selected_cities, selected_years, selected_seasons, date_range


def display_metrics(df: pd.DataFrame):
    """Отображает ключевые метрики."""
    st.subheader("Ключевые метрики")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Средняя температура", f"{calculate_avg_temp(df):.2f} °C")
    with col2:
        st.metric("Медиана температуры", f"{calculate_median_temp(df):.2f} °C")
    with col3:
        st.metric("Доля дней с осадками", f"{calculate_precip_days(df):.2f}%")
    with col4:
        st.metric("Средняя скорость ветра", f"{calculate_avg_wind_speed(df):.2f} км/ч")


def display_visualizations(df: pd.DataFrame):
    """Отображает визуализации."""
    st.subheader("Линейный график")
    x_var_line = st.selectbox("Ось X", ["date", "season"], key="line_x")
    y_var_line = st.selectbox("Ось Y", ["avg_temp_c", "precipitation_mm", "avg_wind_speed_kmh"], key="line_y")
    color_line = st.selectbox("Окраска", ["city_name", "season"], key="line_color")
    fig_line = create_line_plot(df, x=x_var_line, y=y_var_line, color=color_line)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Диаграмма рассеяния")
    x_var_scatter = st.selectbox("Ось X (scatter)", ["avg_temp_c", "precipitation_mm", "avg_wind_speed_kmh"], key="scatter_x")
    y_var_scatter = st.selectbox("Ось Y (scatter)", ["avg_temp_c", "precipitation_mm", "avg_wind_speed_kmh"], key="scatter_y")
    color_scatter = st.selectbox("Окраска (scatter)", ["city_name", "season"], key="scatter_color")
    fig_scatter = create_scatter_plot(df, x=x_var_scatter, y=y_var_scatter, color=color_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Гистограмма")
    hist_var = st.selectbox("Переменная", ["avg_temp_c", "precipitation_mm", "avg_wind_speed_kmh"], key="hist_var")
    nbins = st.number_input("Количество столбцов", min_value=5, max_value=50, value=20, key="hist_nbins")
    fig_hist = create_histogram(df, x=hist_var, nbins=nbins)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Карта")
    metric_map = st.selectbox("Метрика для карты", ["avg_temp_c", "precipitation_mm"], key="map_metric")
    mode_map = st.selectbox("Режим отображения", ["color", "size"], key="map_mode")
    agg_df = df.groupby("city_name")[metric_map].mean().reset_index()
    cities_df = load_cities()
    map_data = pd.merge(agg_df, cities_df[["city_name", "latitude", "longitude"]], on="city_name")
    map_data.rename(columns={"latitude": "lat", "longitude": "lng"}, inplace=True)
    fig_map = create_map(map_data, value_col=metric_map, mode=mode_map)
    st.plotly_chart(fig_map, use_container_width=True)


def display_table(df: pd.DataFrame):
    """Отображает таблицу данных."""
    st.subheader("Данные")
    st.dataframe(
        df[["date", "city_name", "avg_temp_c", "precipitation_mm", "season", "avg_wind_speed_kmh"]],
        column_config={
            "date": "Дата",
            "city_name": "Город",
            "avg_temp_c": "Температура (°C)",
            "precipitation_mm": "Осадки (мм)",
            "season": "Сезон",
            "avg_wind_speed_kmh": "Скорость ветра (км/ч)"
        }
    )


def display_download_button(df: pd.DataFrame):
    """Отображает кнопку для скачивания данных."""
    st.download_button(
        label="Скачать данные в .xlsx",
        data=to_excel(df[["date", "city_name", "avg_temp_c", "precipitation_mm", "season", "avg_wind_speed_kmh"]]),
        file_name="weather_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def main():
    """Основная функция приложения."""
    st.title("Погодный дашборд")
    selected_countries, selected_cities, selected_years, selected_seasons, date_range = get_filters()

    if len(date_range) != 2:
        st.warning("Пожалуйста, выберите полный диапазон дат.")
        return

    weather_df = load_weather(
        years=selected_years,
        countries=selected_countries,
        cities=selected_cities,
        seasons=selected_seasons,
        start_date=date_range[0],
        end_date=date_range[1]
    )

    if weather_df.empty:
        st.warning("Нет данных для выбранных фильтров.")
        return

    display_metrics(weather_df)
    display_visualizations(weather_df)
    display_table(weather_df)
    display_download_button(weather_df)


if __name__ == "__main__":
    main()
