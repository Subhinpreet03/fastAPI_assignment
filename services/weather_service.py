import requests
from fastapi.responses import JSONResponse
from config import config


def get_weather_data():
    """Fetch weather data from the external API."""
    try:
        response = requests.get(config.WEATHER_API_URL)
        response.raise_for_status()
        data = response.json()

        if "items" not in data or not data["items"]:
            return JSONResponse(content={"error": "Unexpected API response structure"}, status_code=500)

        locations = []
        for reading in data["items"][0].get("readings", []):
            location = reading.get("station_id")
            temperature = reading.get("value")
            if location and temperature is not None:
                locations.append({"location": location, "temperature": temperature})

        return locations
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
