import streamlit as st
import pandas as pd
import plotly.express as px
from data import to_excel
from services.metrics_calculator import (calculate_avg_temp, calculate_median_temp,
                                         calculate_precip_days, calculate_avg_wind_speed)
from utils.column_names import COLUMN_NAMES, NUMBERS_FEATURES


def create_line_plot(df: pd.DataFrame, x: str = "date", y: str = "avg_temp_c",
                     color: str = "city_name") -> px.line:
    """Создаёт линейный график."""
    return px.line(
        df, x=x, y=y, color=color,
        labels={x: COLUMN_NAMES.get(x, x), y: COLUMN_NAMES.get(y, y),
                color: COLUMN_NAMES.get(color, color)},
        title=f"{COLUMN_NAMES.get(y, y)} по {COLUMN_NAMES.get(x, x)}"
    )


def create_scatter_plot(df: pd.DataFrame, x: str = "date",
                        y: str = "precipitation_mm", color: str = "season") -> px.scatter:
    """Создаёт диаграмму рассеяния."""
    return px.scatter(
        df, x=x, y=y, color=color,
        labels={x: COLUMN_NAMES.get(x, x), y: COLUMN_NAMES.get(y, y),
                color: COLUMN_NAMES.get(color, color)},
        title=f"{COLUMN_NAMES.get(y, y)} vs {COLUMN_NAMES.get(x, x)}"
    )


def create_histogram(df: pd.DataFrame, x: str = "avg_temp_c",
                     nbins: int = 20) -> px.histogram:
    """Создаёт гистограмму."""
    return px.histogram(
        df, x=x, nbins=nbins,
        marginal="rug",
        labels={x: COLUMN_NAMES.get(x, x)},
        title=f"Распределение {COLUMN_NAMES.get(x, x)}"
    )


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
    x_var_line = st.selectbox(
        "Ось X",
        ["date", *NUMBERS_FEATURES],
        index=0,  # "date" по умолчанию
        key="line_x",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    y_var_line = st.selectbox(
        "Ось Y",
        NUMBERS_FEATURES,
        index=0,  # "avg_temp_c" по умолчанию
        key="line_y",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    fig_line = create_line_plot(df, x=x_var_line, y=y_var_line)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Диаграмма рассеяния")
    x_var_scatter = st.selectbox(
        "Ось X (scatter)",
        ["date", *NUMBERS_FEATURES],
        index=1,  # "avg_temp_c" по умолчанию
        key="scatter_x",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    y_var_scatter = st.selectbox(
        "Ось Y (scatter)",
        NUMBERS_FEATURES,
        index=1,  # "precipitation_mm" по умолчанию
        key="scatter_y",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    color_scatter = st.selectbox(
        "Окраска (scatter)",
        ["city_name", "season"],
        index=1,  # "season" по умолчанию
        key="scatter_color",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    fig_scatter = create_scatter_plot(df, x=x_var_scatter, y=y_var_scatter, color=color_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Гистограмма")
    hist_var = st.selectbox(
        "Переменная",
        NUMBERS_FEATURES,
        index=2,  # "avg_wind_speed_kmh" по умолчанию
        key="hist_var",
        format_func=lambda x: COLUMN_NAMES[x]
    )
    nbins = st.number_input("Количество столбцов", min_value=5, max_value=100, value=50,
                            key="hist_nbins")
    fig_hist = create_histogram(df, x=hist_var, nbins=nbins)
    st.plotly_chart(fig_hist, use_container_width=True)


def display_table(df: pd.DataFrame):
    """Отображает таблицу данных."""
    st.subheader("Данные")
    st.dataframe(
        df[["date", "city_name", "season", *NUMBERS_FEATURES]],
        column_config=COLUMN_NAMES
    )


def display_download_button(df: pd.DataFrame):
    """Отображает кнопку для скачивания данных."""
    st.download_button(
        label="Скачать данные в .xlsx",
        data=to_excel(df[["date", "city_name", "season", *NUMBERS_FEATURES]]),
        file_name="weather_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
