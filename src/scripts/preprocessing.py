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


def tokenize_and_lemmatize(sentence: str):
    """Tokenize with spaCy and lemmatize (Russian only)."""
    sentence = re.sub(r"[^\w\s]", "", sentence)
    doc = _nlp(sentence.lower())

    tokens = []
    for token in doc:
        if token.text in _russian_stopwords or token.is_punct or token.is_space:
            continue
        tokens.append(token.lemma_)
    return tokens


def clean_up_sentence(sentence: str):
    """Public wrapper for tokenization."""
    return tokenize_and_lemmatize(sentence)


def bow(sentence: str, words: list):
    """Bag-of-words vector."""
    sentence_words = tokenize_and_lemmatize(sentence)
    return [1 if w in sentence_words else 0 for w in words]


def preprocess_data():
    """
    Tokenises all patterns, lemmatises with spaCy, removes Russian
    stopwords, deduplicates, and returns (words, classes, documents).
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
