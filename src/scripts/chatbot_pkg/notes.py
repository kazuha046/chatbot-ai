"""Persistent notes storage — create, list, read, delete notes.

Notes are stored in a JSON file and survive between sessions.
"""

import json
import os
from datetime import UTC, datetime

NOTES_FILE = "src/jsons/notes.json"


def _load_notes() -> list[dict]:
    """Load all notes from the JSON file.

    Returns:
        List of note dicts with 'id', 'text', and 'created' keys.
    """
    if not os.path.exists(NOTES_FILE):
        return []

    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_notes(notes: list[dict]) -> None:
    """Save all notes to the JSON file.

    Args:
        notes: List of note dicts to save.
    """
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)

    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(text: str) -> str:
    """Create a new note and save it.

    Args:
        text: The note content.

    Returns:
        Confirmation message with the note ID.
    """
    notes = _load_notes()
    note_id = len(notes) + 1

    notes.append(
        {
            "id": note_id,
            "text": text,
            "created": datetime.now(tz=UTC).astimezone().isoformat(),
        }
    )
    _save_notes(notes)

    return f"Заметка #{note_id} сохранена!"


def list_notes() -> str:
    """List all saved notes.

    Returns:
        Formatted string with all notes, or a message if none exist.
    """
    notes = _load_notes()

    if not notes:
        return "У тебя пока нет заметок. Создай первую: «заметка: купить молоко»"

    lines = ["Твои заметки:"]

    for note in notes:
        lines.append(f"  #{note['id']}: {note['text']}")

    return "\n".join(lines)


def read_note(note_id: int) -> str:
    """Read a specific note by its ID.

    Args:
        note_id: The note ID to read.

    Returns:
        The note content, or an error message.
    """
    notes = _load_notes()

    for note in notes:
        if note["id"] == note_id:
            return f"Заметка #{note_id}: {note['text']}"

    return f"Заметка #{note_id} не найдена."


def delete_note(note_id: int) -> str:
    """Delete a note by its ID.

    Args:
        note_id: The note ID to delete.

    Returns:
        Confirmation or error message.
    """
    notes = _load_notes()
    original_len = len(notes)
    notes = [n for n in notes if n["id"] != note_id]

    if len(notes) == original_len:
        return f"Заметка #{note_id} не найдена."

    _save_notes(notes)

    return f"Заметка #{note_id} удалена."


def handle_notes(sentence: str) -> str | None:
    """Detect note-related commands and execute them.

    Supports: «заметка: текст», «заметки», «заметка 3», «удали заметку 3»

    Args:
        sentence: User input text.

    Returns:
        Response string, or None if not a note command.
    """
    lower = sentence.lower().strip()

    if lower in ("заметки", "мои заметки", "список заметок", "покажи заметки"):
        return list_notes()

    if "удали заметку" in lower or "удалить заметку" in lower:
        import re

        match = re.search(r"(\d+)", sentence)

        if match:
            return delete_note(int(match.group(1)))

        return "Укажи номер заметки, например: «удали заметку 3»"

    if ("заметка" in lower or "заметку" in lower) and any(c.isdigit() for c in lower):
        import re

        match = re.search(r"(\d+)", sentence)

        if match:
            return read_note(int(match.group(1)))

    if "заметка:" in lower or "заметка -" in lower or "запиши:" in lower:
        import re

        match = re.search(
            r"(?:заметка[:\s-]+|запиши[:\s]+)(.+)", sentence, re.IGNORECASE
        )

        if match:
            return add_note(match.group(1).strip())

    return None
