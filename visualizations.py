import pandas as pd
import plotly.express as px


def create_line_plot(df: pd.DataFrame, x: str = "date", y: str = "avg_temp_c",
                     color: str = "city_name") -> px.line:
    """Создаёт линейный график."""
    return px.line(
        df, x=x, y=y, color=color,
        labels={x: x, y: y, color: color},
        title=f"{y} по {x}"
    )


def create_scatter_plot(df: pd.DataFrame, x: str = "avg_temp_c",
                        y: str = "precipitation_mm", color: str = "season") -> px.scatter:
    """Создаёт диаграмму рассеяния."""
    return px.scatter(
        df, x=x, y=y, color=color,
        labels={x: x, y: y, color: color},
        title=f"{y} vs {x}"
    )


def create_histogram(df: pd.DataFrame, x: str = "avg_temp_c",
                     nbins: int = 20) -> px.histogram:
    """Создаёт гистограмму."""
    return px.histogram(
        df, x=x, nbins=nbins,
        labels={x: x}, title=f"Распределение {x}"
    )


def create_map(map_df: pd.DataFrame, value_col: str = "avg_temp_c",
               mode: str = "color") -> px.scatter_geo:
    """Создаёт карту с городами."""
    fig = px.scatter_geo(
        map_df, lat="lat", lon="lng", hover_name="city_name",
        size=map_df[value_col] if mode == "size" else None,
        color=map_df[value_col] if mode == "color" else None,
        projection="natural earth",
        title=f"Карта: {value_col}"
    )
    return fig
