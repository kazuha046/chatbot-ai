"""Keyword-based intent handlers that bypass the neural network.

Each handler checks the user input for specific keywords and returns
a response directly, providing fast and reliable answers for common
queries like weather, time, date, math, and name recall.
"""

import datetime
import random
import re

from src.scripts.settings import load_user_data
from src.scripts.weather import get_weather


def handle_weather(sentence: str, extractor, settings: dict) -> str | None:
    """Detect weather queries and return formatted weather data.

    Checks for weather-related keywords, extracts the city name via NER,
    and fetches weather from OpenWeatherMap.

    Args:
        sentence: User input text.
        extractor: NERExtractor instance for city extraction.
        settings: User settings dict with 'lang' and 'units' keys.

    Returns:
        Formatted weather string, or None if not a weather query.
    """
    keywords = ["погод", "температура", "дождь", "снег", "ветер"]

    lower = sentence.lower()

    if not any(kw in lower for kw in keywords):
        return None

    city = extractor.extract_city(sentence)

    if not city:
        return "Укажи название города, например: «погода в Москве»"

    lang = settings.get("lang", "ru")
    units = settings.get("units", "metric")
    weather_data = get_weather(city, lang, units)

    if not weather_data:
        return "Не удалось получить данные о погоде. Проверь название города или попробуй позже."

    return (
        f"Погода в {weather_data['city_name']}: {weather_data['weather']}, "
        f"температура: {weather_data['temperature']}°C, "
        f"влажность: {weather_data['humidity']}%, "
        f"давление: {weather_data['pressure']} hPa, "
        f"скорость ветра: {weather_data['wind_speed']} м/с."
    )


def handle_random_number(sentence: str) -> str | None:
    """Generate a random number in response to number requests.

    Args:
        sentence: User input text.

    Returns:
        A string containing a random number (1–1000), or None.
    """
    keywords = [
        "случайное число",
        "назови число",
        "сгенерируй число",
        "число от",
        "random number",
        "случайный числа",
    ]

    if not any(kw in sentence.lower() for kw in keywords):
        return None

    num = random.randint(1, 1000)

    return random.choice(
        [
            f"Случайное число: {num}",
            f"Выбираю... {num}!",
            f"Вот твоё число: {num}",
        ]
    )


def handle_calculator(sentence: str) -> str | None:
    """Evaluate a math expression from user input.

    Extracts the mathematical expression after known keywords,
    sanitizes it, and evaluates using Python's eval() with
    restricted builtins.

    Args:
        sentence: User input text.

    Returns:
        The calculation result as a string, or None if not a math query.
    """
    patterns = [
        "сколько будет",
        "посчитай",
        "вычисли",
        "реши",
        "сколько равно",
        "чему равно",
    ]
    lower = sentence.lower()

    if not any(p in lower for p in patterns):
        return None

    expr = sentence

    for p in patterns:
        if p in lower:
            idx = lower.index(p)
            expr = sentence[idx + len(p) :].strip()

            break

    expr_clean = re.sub(r"[^0-9+\-*/().%^ ]", "", expr).strip()

    if not expr_clean:
        return "Не нашёл математическое выражение. Напиши, например: «сколько будет 243 * 6»"

    expr_clean = expr_clean.replace("^", "**")

    try:
        result = eval(expr_clean, {"__builtins__": {}}, {})
        return random.choice(
            [
                f"Результат: {result}",
                f"{expr_clean} = {result}",
                f"Ответ: {result} 🔢",
            ]
        )
    except ZeroDivisionError:
        return "Нельзя делить на ноль!"
    except (TypeError, SyntaxError, NameError):
        return f"Не могу вычислить «{expr_clean}». Проверь выражение."


def handle_user_name(sentence: str) -> str | None:
    """Recall the user's previously saved name.

    Args:
        sentence: User input text.

    Returns:
        A greeting using the saved name, or a prompt to introduce themselves.
    """
    keywords = [
        "как меня зовут",
        "какое у меня имя",
        "помнишь мое имя",
        "как ты меня называешь",
        "можешь сказать, как меня зовут",
        "мое имя",
    ]

    if not any(kw in sentence.lower() for kw in keywords):
        return None

    try:
        name = load_user_data().get("name")
        if name:
            return random.choice(
                [
                    f"Тебя зовут {name}!",
                    f"Я тебя знаю как {name}!",
                    f"Твоё имя — {name}.",
                ]
            )

        return "Я еще не знаю твоё имя. Расскажи, как тебя зовут?"
    except (FileNotFoundError, KeyError):
        return "Я не знаю как тебя зовут. Пожалуйста, давай познакомимся."


def handle_date(sentence: str) -> str | None:
    """Return the current date and weekday in Russian.

    Args:
        sentence: User input text.

    Returns:
        A formatted date string, or None if not a date query.
    """
    keywords = [
        "дата",
        "день недели",
        "какой сегодня день",
        "сегодня какое число",
        "какое сегодня число",
        "какой день",
        "какой месяц",
        "какой год",
        "число сегодня",
        "день сегодня",
    ]

    if not any(kw in sentence.lower() for kw in keywords):
        return None

    now = datetime.datetime.now(tz=datetime.UTC).astimezone()
    weekdays = [
        "понедельник",
        "вторник",
        "среда",
        "четверг",
        "пятница",
        "суббота",
        "воскресенье",
    ]
    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]

    date_str = f"{now.day} {months[now.month - 1]} {now.year}"
    weekday = weekdays[now.weekday()]

    return random.choice(
        [
            f"Сегодня {date_str} ({weekday}).",
            f"Дата: {date_str}, {weekday}.",
            f"По моим данным — {date_str}, {weekday}.",
        ]
    )


def handle_time(sentence: str) -> str | None:
    """Return the current time in Russian.

    Args:
        sentence: User input text.

    Returns:
        A formatted time string, or None if not a time query.
    """
    keywords = [
        "время",
        "час",
        "который час",
        "сколько время",
        "текущее время",
        "на часах",
        "сколько сейчас",
    ]

    if not any(kw in sentence.lower() for kw in keywords):
        return None

    now = datetime.datetime.now(tz=datetime.UTC).astimezone().strftime("%H:%M")

    return random.choice(
        [
            f"Текущее время: {now}",
            f"Сейчас: {now}",
            f"На часах: {now}",
            f"Смотри, сейчас {now}",
        ]
    )
