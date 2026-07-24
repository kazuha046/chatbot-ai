"""Text preprocessing pipeline for the chatbot.

Handles tokenization and lemmatization using spaCy's Russian model,
stopword removal, bag-of-words vectorization, and training data preparation.
"""

import re

import nltk
import spacy
from nltk.corpus import stopwords

from src.scripts.config import INTENTS

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

_nlp = spacy.load("ru_core_news_lg")
_russian_stopwords = set(stopwords.words("russian"))


def tokenize_and_lemmatize(sentence: str) -> list[str]:
    """Tokenize and lemmatize a Russian sentence using spaCy.

    Strips punctuation, lowercases, removes Russian stopwords,
    and returns lemmatized tokens.

    Args:
        sentence: Input text in Russian.

    Returns:
        List of lemmatized token strings.
    """
    sentence = re.sub(r"[^\w\s]", "", sentence)
    doc = _nlp(sentence.lower())

    tokens = []

    for token in doc:
        if token.text in _russian_stopwords or token.is_punct or token.is_space:
            continue

        tokens.append(token.lemma_)

    return tokens


def clean_up_sentence(sentence: str) -> list[str]:
    """Public wrapper for tokenization and lemmatization.

    Args:
        sentence: Input text in Russian.

    Returns:
        List of lemmatized token strings.
    """
    return tokenize_and_lemmatize(sentence)


def bow(sentence: str, words: list) -> list[int]:
    """Convert a sentence to a bag-of-words binary vector.

    Args:
        sentence: Input text in Russian.
        words: The vocabulary list to vectorize against.

    Returns:
        List of 0s and 1s indicating presence of each vocabulary word.
    """
    sentence_words = tokenize_and_lemmatize(sentence)
    return [1 if w in sentence_words else 0 for w in words]


def preprocess_data() -> tuple[list[str], list[str], list[tuple]]:
    """Preprocess all intents into training data.

    Tokenizes all patterns, lemmatizes with spaCy, removes Russian
    stopwords, deduplicates vocabulary, and collects intent classes.

    Returns:
        Tuple of (words, classes, documents) where:
        - words: sorted unique vocabulary
        - classes: sorted unique intent tags
        - documents: list of (pattern, tag) tuples
    """
    words, classes, documents = [], [], []

    for intent in INTENTS:
        for pattern in intent["patterns"]:
            tokens = tokenize_and_lemmatize(pattern)
            words.extend(tokens)
            documents.append((pattern, intent["tag"]))

        if intent["tag"] not in classes:
            classes.append(intent["tag"])

    words = sorted(set(words))
    classes = sorted(set(classes))

    return words, classes, documents
