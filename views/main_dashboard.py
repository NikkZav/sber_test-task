import streamlit as st
import pandas as pd
import plotly.express as px
from data import to_excel
from services import metrics_calculator as metrics
from utils.column_names import COLUMN_NAMES, MAIN_METRICS


def create_line_plot(
    df: pd.DataFrame, x: str = "date", y: str = "avg_temp_c", color: str = "city_name"
) -> px.line:
    """Создаёт линейный график."""
    return px.line(
        df,
        x=x,
        y=y,
        color=color,
        labels={
            x: COLUMN_NAMES.get(x, x),
            y: COLUMN_NAMES.get(y, y),
            color: COLUMN_NAMES.get(color, color),
        },
        title=f"{COLUMN_NAMES.get(y, y)} по {COLUMN_NAMES.get(x, x)}",
    )


def create_scatter_plot(
    df: pd.DataFrame,
    x: str = "date",
    y: str = "precipitation_mm",
    color: str = "season",
) -> px.scatter:
    """Создаёт диаграмму рассеяния."""
    return px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        labels={
            x: COLUMN_NAMES.get(x, x),
            y: COLUMN_NAMES.get(y, y),
            color: COLUMN_NAMES.get(color, color),
        },
        title=f"{COLUMN_NAMES.get(y, y)} vs {COLUMN_NAMES.get(x, x)}",
    )


def create_histogram(
    df: pd.DataFrame, x: str = "avg_temp_c", nbins: int = 20
) -> px.histogram:
    """Создаёт гистограмму."""
    return px.histogram(
        df,
        x=x,
        nbins=nbins,
        marginal="rug",
        labels={x: COLUMN_NAMES.get(x, x)},
        title=f"Распределение {COLUMN_NAMES.get(x, x)}",
    )


def display_metrics(df: pd.DataFrame):
    """Отображает ключевые метрики."""
    st.subheader("Ключевые метрики")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Средняя температура", f"{metrics.calculate_avg_temp(df):+.2f} °C")
    with col2:
        st.metric("Медиана температуры", f"{metrics.calculate_median_temp(df):+.2f} °C")
    with col3:
        st.metric("Доля дней с осадками", f"{metrics.calculate_precip_days(df):.2f}%")
    with col4:
        st.metric("Средняя скорость ветра", f"{metrics.calculate_avg_wind_speed(df):.2f} км/ч")


def display_line_plot(df: pd.DataFrame, default_x="date", default_y="avg_temp_c"):
    """Отображает линейный график."""
    st.subheader("Линейный график")

    x_options = ["date", *MAIN_METRICS]
    x_var_line = st.selectbox(
        "Ось X",
        options=x_options,
        index=x_options.index(default_x),
        format_func=lambda x: COLUMN_NAMES[x],
        key="line_x",
    )
    y_var_line = st.selectbox(
        "Ось Y",
        MAIN_METRICS,
        index=MAIN_METRICS.index(default_y),
        format_func=lambda x: COLUMN_NAMES[x],
        key="line_y",
    )
    fig_line = create_line_plot(df, x=x_var_line, y=y_var_line)
    st.plotly_chart(fig_line, use_container_width=True)


def display_scatter_plot(df: pd.DataFrame,
                         default_x="avg_temp_c", default_y="avg_sea_level_pres_hpa",
                         default_color="season"):
    """Отображает диаграмму рассеяния."""
    st.subheader("Диаграмма рассеяния")

    x_options = ["date", *MAIN_METRICS]
    x_var_scatter = st.selectbox(
        "Ось X (scatter)",
        options=x_options,
        index=x_options.index(default_x),
        format_func=lambda x: COLUMN_NAMES[x],
        key="scatter_x",
    )
    y_var_scatter = st.selectbox(
        "Ось Y (scatter)",
        MAIN_METRICS,
        index=MAIN_METRICS.index(default_y),
        format_func=lambda x: COLUMN_NAMES[x],
        key="scatter_y",
    )
    color_options = ["city_name", "season"]
    color_scatter = st.selectbox(
        "Окраска (scatter)",
        options=color_options,
        index=color_options.index(default_color),
        format_func=lambda x: COLUMN_NAMES[x],
        key="scatter_color",
    )
    fig_scatter = create_scatter_plot(
        df, x=x_var_scatter, y=y_var_scatter, color=color_scatter
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


def display_histogram(df: pd.DataFrame, default_var="avg_wind_speed_kmh", default_nbins=50):
    """Отображает гистограмму."""
    st.subheader("Гистограмма")

    hist_var = st.selectbox(
        "Переменная",
        MAIN_METRICS,
        index=MAIN_METRICS.index(default_var),
        format_func=lambda x: COLUMN_NAMES[x],
        key="hist_var",
    )
    nbins = st.number_input(
        "Количество столбцов",
        min_value=5,
        max_value=100,
        value=default_nbins,
        key="hist_nbins"
    )
    fig_hist = create_histogram(df, x=hist_var, nbins=nbins)
    st.plotly_chart(fig_hist, use_container_width=True)


def display_charts_and_histograms(df: pd.DataFrame):
    """Отображает графики и диаграммы."""
    display_line_plot(df, default_x="date", default_y="avg_temp_c")
    display_scatter_plot(df, default_x="avg_temp_c", default_y="avg_sea_level_pres_hpa",
                         default_color="season")
    display_histogram(df, default_var="avg_wind_speed_kmh", default_nbins=50)


def display_table(df: pd.DataFrame):
    """Отображает таблицу данных."""
    st.subheader("Данные")
    all_metrics = st.checkbox("Выбрать все метрики", value=False, key="all_metrics")
    selected_metrics = st.multiselect(
        "Выберите метрики для таблицы",
        options=list(COLUMN_NAMES.keys()),
        default=list(COLUMN_NAMES.keys()) if all_metrics else ["date", "city_name", "season",
                                                               *MAIN_METRICS],
        format_func=lambda x: COLUMN_NAMES[x],
        key="selected_table_metrics"
    )
    st.dataframe(
        df[selected_metrics],
        column_config=COLUMN_NAMES,
        key="wether_records_table",
    )


def display_download_button(df: pd.DataFrame):
    """Отображает кнопку для скачивания данных."""
    st.download_button(
        label="Скачать данные в .xlsx",
        data=to_excel(df[st.session_state.selected_table_metrics]),
        file_name="weather_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
