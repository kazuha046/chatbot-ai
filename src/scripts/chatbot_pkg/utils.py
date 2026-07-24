"""Utility handlers: translator and UUID generator."""

import re
import uuid


def handle_translate(sentence: str) -> str | None:
    """Translate text between Russian and English.

    Detects direction from keywords: «переведи/перевести на английский/русский».

    Args:
        sentence: User input text.

    Returns:
        Translated text, or None if not a translate command.
    """
    lower = sentence.lower()

    if "переведи" not in lower and "перевести" not in lower and "перевод" not in lower:
        return None

    match = re.search(
        r"(?:переведи|перевести|перевод)\s+(?:на\s+)?(английск\w*|русск\w*)\s*[:\s]*(.+)",
        lower,
    )

    if not match:
        return "Формат: «переведи на английский привет мир» или «переведи на русский hello world»"

    target_lang = "en" if "английск" in match.group(1) else "ru"
    text = match.group(2).strip()

    if not text:
        return "Напиши текст для перевода."

    try:
        from deep_translator import GoogleTranslator

        result = GoogleTranslator(source="auto", target=target_lang).translate(text)
        lang_name = "английский" if target_lang == "en" else "русский"

        return f"Перевод на {lang_name}: {result}"
    except ImportError:
        return "Модуль перевода не установлен. Установи: pip install deep-translator"
    except (ValueError, ConnectionError) as e:
        return f"Ошибка перевода: {e}"


def handle_uuid(sentence: str) -> str | None:
    """Generate a UUID4.

    Args:
        sentence: User input text.

    Returns:
        UUID string, or None if not a UUID request.
    """
    keywords = ["uuid", "ууид", "сгенерируй uuid", "генератор uuid"]

    if not any(kw in sentence.lower() for kw in keywords):
        return None

    return f"UUID4: {uuid.uuid4()}"
