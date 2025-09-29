import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests



def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city using a free API.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    try:
        # Step 1: Get latitude/longitude from Open-Meteo Geocoding API
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=5)

        if geo_resp.status_code != 200:
            return {"status": "error", "error_message": "Failed to fetch location data."}

        geo_data = geo_resp.json()
        if "results" not in geo_data or not geo_data["results"]:
            return {"status": "error", "error_message": f"City '{city}' not found."}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Step 2: Fetch weather from Open-Meteo API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {"latitude": lat, "longitude": lon, "current_weather": True}
        weather_resp = requests.get(weather_url, params=weather_params, timeout=5)

        if weather_resp.status_code != 200:
            return {"status": "error", "error_message": "Failed to fetch weather data."}

        weather_data = weather_resp.json()
        if "current_weather" not in weather_data:
            return {
                "status": "error",
                "error_message": f"Weather information for '{city}' is not available.",
            }

        current = weather_data["current_weather"]
        temperature = current["temperature"]
        windspeed = current["windspeed"]

        report = (
            f"The weather in {city} is {temperature}°C with windspeed of {windspeed} km/h."
        )
        return {"status": "success", "report": report}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)