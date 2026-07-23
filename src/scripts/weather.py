import os
import requests


def get_weather(city: str, lang: str, units: str):
    """
    Gets the current weather for a given city.

    Parameters:
        city (str): The name of the city for which to retrieve the weather.
        lang (str): The language to use for the weather data. Defaults to "ru".
        units (str): The system of units to use for the weather data. Defaults to "metric".

    Returns:
        A dictionary containing the city name, temperature, weather description,
        humidity, atmospheric pressure, wind speed, and wind direction.
    """

    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang={lang}&units={units}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            weather = data["weather"][0]["description"]
            city_name = data["name"]
            wind_speed = data["wind"]["speed"]
            wind_deg = data["wind"]["deg"]

            return {
                "city_name": city_name,
                "temperature": temp,
                "weather": weather,
                "humidity": humidity,
                "pressure": pressure,
                "wind_speed": wind_speed,
                "wind_deg": wind_deg,
            }

        else:
            return None
    except Exception as e:
        print(e)
        return None
