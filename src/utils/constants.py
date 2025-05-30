import pandas as pd


MIN_DATE = pd.to_datetime("1750-02-01").date()
MAX_DATE = pd.to_datetime("2023-09-05").date()
DEFAULT_START = pd.to_datetime("2019-01-01").date()
DEFAULT_END = pd.to_datetime("2022-12-31").date()
DAFAULT_TIMELINE_START = pd.to_datetime("2000-01-01").date()

LIMIT_WEATHER_RECORDS = 30_000
CHUNK_SIZE = 100_000
