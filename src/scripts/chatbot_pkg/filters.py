"""Input validation and gibberish detection for user messages."""

import random


def is_gibberish(sentence: str) -> str | None:
    """Check if the input is too short, non-Cyrillic, or otherwise unparseable.

    Args:
        sentence: Raw user input text.

    Returns:
        A fallback response string if the input is gibberish, or None
        if the input looks valid.
    """
    stripped = sentence.strip()

    if len(stripped) < 3:
        return random.choice(
            [
                "Можешь написать подробнее?",
                "Не совсем понял. Развей мысль!",
                "Хм, расскажи больше!",
            ]
        )

    cyrillic_count = sum(
        1 for ch in stripped if "а" <= ch.lower() <= "я" or ch.lower() == "ё"
    )
    total_alpha = sum(1 for ch in stripped if ch.isalpha())

    if total_alpha > 0 and cyrillic_count / total_alpha < 0.3:
        return random.choice(
            [
                "Я понимаю только русский. Напиши по-русски!",
                "Хм, попробуй написать по-русски.",
                "Я пока не знаю других языков. Давай по-русски?",
            ]
        )

    return None
