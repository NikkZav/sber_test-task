import pandas as pd


df = pd.read_parquet("data/daily_weather.parquet")

print(df.head())

print(df["date"].min(), df["date"].max())
