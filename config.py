import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class Config:
    BINANCE_API_URL = os.getenv("BINANCE_API_URL", "https://api.binance.com/api/v3")
    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.data.gov.sg/v1/environment/air-temperature")
    GRAPH_FOLDER = os.getenv("GRAPH_FOLDER", "graphs/")
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://test_local:test_local@5613@localhost/FastAPI_test")


config = Config()
