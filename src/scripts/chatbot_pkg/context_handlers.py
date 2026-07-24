"""Smart context handlers for follow-up questions.

Detects phrases like "а еще?", "расскажи подробнее", "а что дальше?"
and generates appropriate responses based on conversation history.
"""

import random


def handle_followup(sentence: str, context) -> str | None:
    """Detect and respond to follow-up phrases based on conversation history.

    Looks for phrases like "а еще", "расскажи подробнее", "а что дальше"
    and generates a relevant continuation based on the last topic.

    Args:
        sentence: User input text.
        context: ConversationContext instance with history.

    Returns:
        A follow-up response, or None if not a follow-up phrase.
    """
    followup_keywords = [
        "а еще",
        "а ещё",
        "расскажи подробнее",
        "подробнее",
        "а что дальше",
        "продолжай",
        "и что",
        "ну и",
        "а потом",
        "интересно",
        "а можно еще",
        "а можно ещё",
    ]

    lower = sentence.lower().strip()

    if not any(kw in lower for kw in followup_keywords):
        return None

    last_intent = context.last_intent()

    if not last_intent:
        return random.choice(
            [
                "О чем именно ты хочешь узнать больше?",
                "Уточни, о чем речь — и я расскажу!",
                "Не совсем понял, к чему уточнение.",
            ]
        )

    continuations = {
        "fact": random.choice(
            [
                "А вот еще факт: у кальмаров три сердца и синяя кровь!",
                "Знаешь, а пчёлы могут запоминать лица людей!",
                "Ещё интересное: в Японии есть остров кроликов!",
                "А ещё: бананы — это ягоды, а клубника нет!",
            ]
        ),
        "jokes": random.choice(
            [
                "Вот ещё один: — Почему программист путает Хеллоуин и Рождество? — Потому что Oct 31 == Dec 25!",
                "А ещё: Продавец: — У нас есть рубашки по 1000 и по 2000. Покупатель: — Дайте по дешёвле! Продавец: — Тогда две по 1000!",
                "Ещё шутка: Три инженера ищут ошибку. Первый: — Проблема в питании. Второй: — Нет, в софте. Третий: — Свет выключим и включим.",
            ]
        ),
        "weather": "Хочешь узнать погоду в другом городе? Просто напиши название!",
        "quote": random.choice(
            [
                "Вот ещё цитата: «Единственная настоящая роскошь — это роскошь человеческого общения.» — Коко Шанель",
                "А вот ещё: «Думай как человек действия, а не как человек обстоятельств.» — Роберт Кийосаки",
            ]
        ),
    }

    if last_intent in continuations:
        return continuations[last_intent]

    return random.choice(
        [
            "Можешь уточнить, о чём именно хочешь узнать?",
            "Расскажи подробнее, что тебя интересует!",
            "Хм, уточни вопрос — и я постараюсь помочь!",
        ]
    )
