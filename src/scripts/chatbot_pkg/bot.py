"""Core ChatBot class — orchestrates keyword handlers, neural network, and context."""

import random
import string

import numpy as np

from src.scripts.chatbot_pkg.context import ConversationContext
from src.scripts.chatbot_pkg.filters import is_gibberish
from src.scripts.chatbot_pkg.keywords import (
    handle_calculator,
    handle_date,
    handle_random_number,
    handle_time,
    handle_user_name,
    handle_weather,
)
from src.scripts.chatbot_pkg.ner import NERExtractor
from src.scripts.config import CONFIDENCE_THRESHOLD, INTENTS
from src.scripts.model import load_or_train_model
from src.scripts.preprocessing import bow
from src.scripts.settings import load_setting, load_user_data, save_user_data


class ChatBot:
    """Main chatbot class — processes user input and generates responses.

    Combines keyword-based pre-checks for fast reliable answers with
    a neural network classifier for open-ended conversation.
    """

    def __init__(self):
        """Initialize the chatbot: load model, spaCy, settings, and context."""
        self.model, self.words, self.classes, self.label_encoder = load_or_train_model()
        self.settings = load_setting() or {}
        self.ner = NERExtractor()
        self.context = ConversationContext()

    def predict_class(self, sentence: str) -> np.ndarray:
        """Classify the user sentence into an intent using the neural network.

        Args:
            sentence: User input text.

        Returns:
            Numpy array of class probabilities from the model.
        """
        bow_input = np.array([bow(sentence, self.words)])
        return self.model.predict(bow_input, verbose=0)

    def _handle_special_intent(self, tag: str, sentence: str, response: str) -> str:
        """Process special intents that need dynamic response generation.

        Handles random_number, password, acquaintance, and user_name intents
        by replacing template placeholders with generated values.

        Args:
            tag: The matched intent tag.
            sentence: Original user input.
            response: Template response string.

        Returns:
            The response with placeholders filled in.
        """
        if tag == "random_number":
            return response.replace("{random_number}", str(random.randint(1, 1000)))

        if tag == "password":
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password = "".join(random.choices(chars, k=16))

            return response.replace("{password}", password)

        if tag == "acquaintance":
            name = self.ner.extract_name(sentence)

            if name:
                save_user_data({"name": name})
                return response.replace("{name}", name)

            return "Не могу распознать ваше имя. Пожалуйста, повторите."

        if tag == "user_name":
            try:
                name = load_user_data()["name"]

                if name:
                    return response.replace("{name}", name)

                return "Я еще не знаю ваше имя. Давайте познакомимся."
            except (FileNotFoundError, KeyError):
                return "Я не знаю как вас зовут. Пожалуйста, давайте познакомимся."

        return response

    def _make_fallback(self, sentence: str, reason: str = "unknown") -> str:
        """Generate a fallback response and record it in context.

        Args:
            sentence: The user input that triggered the fallback.
            reason: Why the fallback was triggered (for context tracking).

        Returns:
            A random fallback response string.
        """
        fallbacks = {
            "low_confidence": [
                "Я не совсем понял. Можешь переформулировать?",
                "Хм, попробуй сказать по-другому.",
                "Я ещё учусь. Спроси что-нибудь другое!",
                "Можешь объяснить иначе?",
                "Я пока не знаю, как на это ответить. Попробуй задать другой вопрос.",
                "Извини, я не понял тебя. Можешь повторить?",
            ],
            "gibberish": [
                "Я понимаю только русский. Напиши по-русски!",
                "Хм, попробуй написать по-русски.",
                "Я пока не знаю других языков. Давай по-русски?",
            ],
        }

        response = random.choice(fallbacks.get(reason, fallbacks["low_confidence"]))
        self.context.append("user", sentence, None)
        self.context.append("bot", response, None)

        return response

    def respond(self, sentence: str) -> str:
        """Process a user message and return the bot's response.

        Applies keyword-based pre-checks first (weather, date, time,
        random number, calculator, name recall), then falls back to
        the neural network classifier.

        Args:
            sentence: Raw user input text.

        Returns:
            The bot's response string.
        """
        # --- Keyword-based pre-checks (bypass neural network) ---

        keyword_handlers = [
            ("weather", lambda: handle_weather(sentence, self.ner, self.settings)),
            ("date", lambda: handle_date(sentence)),
            ("time", lambda: handle_time(sentence)),
            ("random_number", lambda: handle_random_number(sentence)),
            ("calculator", lambda: handle_calculator(sentence)),
            ("user_name", lambda: handle_user_name(sentence)),
        ]

        for intent_tag, handler in keyword_handlers:
            result = handler()

            if result:
                self.context.append("user", sentence, intent_tag)
                self.context.append("bot", result, intent_tag)

                return result

        # --- Input validation ---

        gibberish_response = is_gibberish(sentence)

        if gibberish_response:
            self.context.append("user", sentence, None)
            self.context.append("bot", gibberish_response, None)

            return gibberish_response

        # --- Neural network prediction ---

        predicted_class = self.predict_class(sentence)
        confidence = float(np.max(predicted_class))

        if confidence < CONFIDENCE_THRESHOLD:
            return self._make_fallback(sentence, "low_confidence")

        predicted_label = self.label_encoder.inverse_transform(
            [np.argmax(predicted_class)]
        )
        tag = predicted_label[0]

        self.context.append("user", sentence, tag)

        for intent in INTENTS:
            if intent["tag"] != tag:
                continue

            response = random.choice(intent["responses"])
            response = self._handle_special_intent(tag, sentence, response)

            # Acknowledge repeated topics
            if self.context.is_repetition(sentence, tag):
                response += random.choice(
                    [
                        " Кстати, мы уже об этом говорили!",
                        " Опять об этом? Ладно!",
                        " Какая настойчивость! 😄",
                    ]
                )

            # Random emoji decoration
            if random.random() < 0.5 and "emoji" in intent:
                response += f" {random.choice(intent['emoji'])}"

            self.context.append("bot", response, tag)
            return response

        return self._make_fallback(sentence)
