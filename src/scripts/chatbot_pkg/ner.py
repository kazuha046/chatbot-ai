"""Named Entity Recognition helpers for extracting cities and names."""

import re

import spacy


class NERExtractor:
    """Extracts named entities (cities, person names) from Russian text using spaCy."""

    def __init__(self):
        """Load the spaCy Russian language model."""
        self._nlp = spacy.load("ru_core_news_lg")

    def extract_city(self, sentence: str) -> str | None:
        """Extract a city name from the sentence using NER and regex fallback.

        First tries spaCy NER for LOC entities, then falls back to finding
        a city name after the prepositions "в" / "во".

        Args:
            sentence: User input text.

        Returns:
            Capitalized city name, or None if not found.
        """
        doc = self._nlp(sentence)

        for ent in doc.ents:
            if ent.label_ == "LOC":
                return ent.lemma_.capitalize()

        match = re.search(r"(?:в|во)\s+([а-яёА-ЯЁ]+(?:\s+[а-яёА-ЯЁ]+)?)", sentence)

        if match:
            return match.group(1).capitalize()

        return None

    def extract_name(self, sentence: str) -> str | None:
        """Extract a person's name from the sentence using spaCy NER.

        Args:
            sentence: User input text.

        Returns:
            Capitalized person name, or None if not found.
        """
        doc = self._nlp(sentence)

        for ent in doc.ents:
            if ent.label_ == "PER":
                return ent.text.capitalize()

        return None
