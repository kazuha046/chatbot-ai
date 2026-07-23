import random
import datetime
import collections
import re
import string

import numpy as np
import spacy

from src.scripts.preprocessing import bow
from src.scripts.config import INTENTS, CONFIDENCE_THRESHOLD
from src.scripts.model import load_or_train_model
from src.scripts.settings import load_setting, load_user_data, save_user_data
from src.scripts.weather import get_weather


class ChatBot:
    def __init__(self):
        self.model, self.words, self.classes, self.label_encoder = load_or_train_model()
        self.settings = load_setting() or {}
        self.nlp = spacy.load("ru_core_news_lg")
        self.context: collections.deque = collections.deque(maxlen=5)

    def predict_class(self, sentence: str):
        bow_input = np.array([bow(sentence, self.words)])
        prediction = self.model.predict(bow_input, verbose=0)
        return prediction

    def extract_city(self, sentence):
        """Extract city name via spaCy NER."""
        doc = self.nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == "LOC":
                return ent.lemma_.capitalize()

        # Fallback: try to find city after "в" / "во" preposition
        match = re.search(r"(?:в|во)\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)?)", sentence)
        if match:
            return match.group(1).capitalize()

        return None

    def extract_name(self, sentence: str):
        doc = self.nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == "PER":
                return ent.text.capitalize()
        return None

    def _keyword_weather(self, sentence: str):
        """
        Keyword-based weather detection.
        If the message contains weather-related keywords, handle it directly
        without relying on the neural network.
        """
        weather_keywords = ["погод", "температура", "дождь", "снег", "ветер"]
        lower = sentence.lower()

        if any(kw in lower for kw in weather_keywords):
            city = self.extract_city(sentence)
            if city:
                lang = self.settings.get("lang", "ru")
                units = self.settings.get("units", "metric")
                weather_data = get_weather(city, lang, units)

                if weather_data:
                    return (
                        f"Погода в {weather_data['city_name']}: {weather_data['weather']}, "
                        f"температура: {weather_data['temperature']}°C, "
                        f"влажность: {weather_data['humidity']}%, "
                        f"давление: {weather_data['pressure']} hPa, "
                        f"скорость ветра: {weather_data['wind_speed']} м/с."
                    )
                else:
                    return "Не удалось получить данные о погоде. Проверь название города или попробуй позже."

            return "Укажи название города, например: «погода в Москве»"

        return None

    def _keyword_date(self, sentence: str):
        """Keyword-based date detection."""
        date_keywords = ["число", "дата", "день недели", "какой сегодня день",
                         "какое сегодня число", "сегодня какое число",
                         "день", "месяц", "год"]
        lower = sentence.lower()

        if any(kw in lower for kw in date_keywords):
            now = datetime.datetime.now()
            weekdays = ["понедельник", "вторник", "среда", "четверг",
                        "пятница", "суббота", "воскресенье"]
            months = ["января", "февраля", "марта", "апреля", "мая", "июня",
                      "июля", "августа", "сентября", "октября", "ноября", "декабря"]

            date_str = f"{now.day} {months[now.month - 1]} {now.year}"
            weekday = weekdays[now.weekday()]

            return random.choice([
                f"Сегодня {date_str} ({weekday}).",
                f"Дата: {date_str}, {weekday}.",
                f"По моим данным — {date_str}, {weekday}.",
            ])

        return None

    def _keyword_time(self, sentence: str):
        """Keyword-based time detection."""
        time_keywords = ["время", "час", "который час", "сколько время",
                         "текущее время", "на часах", "сколько сейчас"]
        lower = sentence.lower()

        if any(kw in lower for kw in time_keywords):
            now = datetime.datetime.now().strftime("%H:%M")
            return random.choice([
                f"Текущее время: {now}",
                f"Сейчас: {now}",
                f"На часах: {now}",
                f"Смотри, сейчас {now}",
            ])

        return None

    def respond(self, sentence: str):
        # --- Keyword-based pre-checks (bypass neural network) ---
        weather_response = self._keyword_weather(sentence)
        if weather_response:
            self.context.append({"role": "user", "text": sentence, "intent": "weather"})
            self.context.append({"role": "bot", "text": weather_response, "intent": "weather"})
            return weather_response

        date_response = self._keyword_date(sentence)
        if date_response:
            self.context.append({"role": "user", "text": sentence, "intent": "date"})
            self.context.append({"role": "bot", "text": date_response, "intent": "date"})
            return date_response

        time_response = self._keyword_time(sentence)
        if time_response:
            self.context.append({"role": "user", "text": sentence, "intent": "time"})
            self.context.append({"role": "bot", "text": time_response, "intent": "time"})
            return time_response

        # --- Neural network prediction ---
        predicted_class = self.predict_class(sentence)
        confidence = float(np.max(predicted_class))

        if confidence < CONFIDENCE_THRESHOLD:
            fallback = random.choice([
                "Я не совсем понял. Можешь переформулировать?",
                "Хм, попробуй сказать по-другому.",
                "Я ещё учусь. Спроси что-нибудь другое!",
                "Можешь объяснить иначе?",
                "Я пока не знаю, как на это ответить. Попробуй задать другой вопрос.",
                "Извини, я не понял тебя. Можешь повторить?",
            ])
            self.context.append({"role": "user", "text": sentence, "intent": None})
            self.context.append({"role": "bot", "text": fallback, "intent": None})
            return fallback

        predicted_label = self.label_encoder.inverse_transform(
            [np.argmax(predicted_class)]
        )
        tag = predicted_label[0]

        self.context.append({"role": "user", "text": sentence, "intent": tag})

        for intent in INTENTS:
            if intent["tag"] == tag:
                response = random.choice(intent["responses"])

                # --- Special intent handlers ---
                if tag == "random_number":
                    response = response.replace("{random_number}", str(random.randint(1, 1000)))

                elif tag == "password":
                    chars = string.ascii_letters + string.digits + "!@#$%^&*"
                    password = "".join(random.choices(chars, k=16))
                    response = response.replace("{password}", password)

                elif tag == "acquaintance":
                    name = self.extract_name(sentence)
                    if name:
                        save_user_data({"name": name})
                        response = response.replace("{name}", name)
                    else:
                        response = "Не могу распознать ваше имя. Пожалуйста, повторите."

                elif tag == "user_name":
                    try:
                        name = load_user_data()["name"]
                        if name:
                            response = response.replace("{name}", name)
                        else:
                            response = "Я еще не знаю ваше имя. Давайте познакомимся."
                    except Exception:
                        response = "Я не знаю как вас зовут. Пожалуйста, давайте познакомимся."

                # Context: if user repeats topic, acknowledge it
                if len(self.context) >= 2:
                    prev_intent = self.context[-2].get("intent")
                    if prev_intent == tag and tag not in ("time", "weather", "date"):
                        context_additions = [
                            " Кстати, мы уже об этом говорили!",
                            " Опять об этом? Ладно!",
                            " Какая настойчивость! 😄",
                        ]
                        response += random.choice(context_additions)

                if random.random() < 0.5 and "emoji" in intent:
                    response += f" {random.choice(intent['emoji'])}"

                self.context.append({"role": "bot", "text": response, "intent": tag})
                return response

        fallback = "Извините, я не понимаю вас."
        self.context.append({"role": "bot", "text": fallback, "intent": None})
        return fallback
