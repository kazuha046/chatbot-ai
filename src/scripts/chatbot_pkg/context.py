"""Conversation context management for the chatbot."""

import collections


class ConversationContext:
    """Maintains a sliding window of recent conversation turns.

    Tracks user and bot messages with their associated intents,
    enabling context-aware responses and repetition detection.
    """

    def __init__(self, maxlen: int = 5):
        """Initialize the context deque.

        Args:
            maxlen: Maximum number of conversation turns to remember.
        """
        self._history: collections.deque = collections.deque(maxlen=maxlen)

    def append(self, role: str, text: str, intent: str | None = None) -> None:
        """Add a message to the conversation history.

        Args:
            role: Message sender — "user" or "bot".
            text: The message content.
            intent: Associated intent tag, or None if unclassified.
        """
        self._history.append({"role": role, "text": text, "intent": intent})

    def is_repetition(self, current_text: str, current_intent: str) -> bool:
        """Check if the user is repeating the same message with the same intent.

        Args:
            current_text: The current user message.
            current_intent: The intent classified for the current message.

        Returns:
            True if the user sent the exact same text with the same intent
            earlier in the conversation.
        """
        if len(self._history) < 4:
            return False

        prev = self._history[-4]

        return (
            prev.get("intent") == current_intent
            and current_text.lower().strip() == prev.get("text", "").lower()
            and current_intent not in ("time", "weather", "date")
        )

    def last_intent(self) -> str | None:
        """Return the intent of the most recent bot response.

        Returns:
            Intent tag string, or None.
        """
        if self._history:
            return self._history[-1].get("intent")

        return None

    @property
    def history(self) -> list[dict]:
        """Return the full conversation history as a list."""
        return list(self._history)
