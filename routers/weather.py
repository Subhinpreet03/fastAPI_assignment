from fastapi import APIRouter, HTTPException
from services.weather_service import get_weather_data
from models.weather import Weather

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/", response_model=list[Weather])
def get_weather():
    """Fetch weather data for all locations."""
    data = get_weather_data()
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    locations = []
    # Ensure the expected structure before accessing it
    try:
        for item in data:
            location = item.get("location")
            temperature = item.get("temperature")

            # Ensure the necessary fields are present
            if location is not None and temperature is not None:
                locations.append(Weather(location=location, temperature=temperature))

        # Return the list of Weather objects
        return locations

    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing expected data: {str(e)}")
