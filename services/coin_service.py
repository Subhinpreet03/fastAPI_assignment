from config import config
import requests
import matplotlib.pyplot as plt
import os
from fastapi.responses import JSONResponse


def get_coin_data(symbol: str = None):
    url = f"{config.BINANCE_API_URL}/ticker/24hr"
    if symbol:
        url += f"?symbol={symbol.upper()}"

    response = requests.get(url)
    if response.status_code != 200:
        return JSONResponse(content={"error": "Failed to fetch data"}, status_code=500)

    return response.json()


def generate_graph(symbol: str):
    url = f"{config.BINANCE_API_URL}/klines?symbol={symbol.upper()}&interval=1d&limit=30"
    response = requests.get(url)

    if response.status_code != 200 or not response.text:
        return JSONResponse(content={"error": "Invalid response from Binance API"}, status_code=500)

    data = response.json()
    if not isinstance(data, list):
        return JSONResponse(content={"error": "Invalid symbol or no data available"}, status_code=400)

    dates = [item[0] for item in data]
    prices = [float(item[4]) for item in data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker="o", linestyle="-")
    plt.xlabel("Timestamp")
    plt.ylabel("Closing Price")
    plt.title(f"Price Trend for {symbol}")
    plt.grid(True)

    os.makedirs(config.GRAPH_FOLDER, exist_ok=True)
    save_path = f"{config.GRAPH_FOLDER}/{symbol}_trend.png"
    plt.savefig(save_path, format="png")

    return {"symbol": symbol, "file_path": save_path}
