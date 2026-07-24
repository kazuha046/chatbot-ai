"""Global configuration constants for the Mika chatbot.

Defines file paths, model hyperparameters, confidence thresholds,
and GUI styling constants used across the application.
"""

import json
import os

BOT_NAME = "Mika"
"""Display name of the chatbot."""

APP_NAME = f"Chatbot AI - {BOT_NAME}"
"""Application window title."""

OUTPUT_DIR = "output"
"""Directory for trained model artifacts."""

SRC_PATH = "src"
"""Source code root directory."""

MODEL_PATH = os.path.join(OUTPUT_DIR, "chatbot_model.keras")
"""Path to the saved Keras model file."""

WORDS_PATH = os.path.join(OUTPUT_DIR, "words.pkl")
"""Path to the saved vocabulary (words) pickle file."""

CLASSES_PATH = os.path.join(OUTPUT_DIR, "classes.pkl")
"""Path to the saved classes pickle file."""

LABEL_ENCODER_PATH = os.path.join(OUTPUT_DIR, "label_encoder.pkl")
"""Path to the saved label encoder pickle file."""

JSONS_PATH = os.path.join(SRC_PATH, "jsons")
"""Directory containing JSON data files."""

INTENTS_PATH = os.path.join(JSONS_PATH, "intents.json")
"""Path to the intents definition file."""

SETTINGS_FILE = os.path.join(JSONS_PATH, "settings.json")
"""Path to the user settings file."""

USER_DATA_FILE = os.path.join(JSONS_PATH, "user.json")
"""Path to the persistent user data file."""

WORDS = []
"""Global vocabulary list, populated during preprocessing."""

CLASSES = []
"""Global intent classes list, populated during preprocessing."""

DOCUMENTS = []
"""Global training documents list, populated during preprocessing."""

with open(INTENTS_PATH, "r", encoding="utf-8") as _f:
    INTENTS = json.load(_f)["intents"]
"""Loaded intents data from intents.json."""

MODEL_EPOCHS = 10000
"""Maximum training epochs for the neural network."""

MODEL_PATIENCE = 500
"""Early stopping patience (epochs without improvement)."""

CONFIDENCE_THRESHOLD = 0.30
"""Minimum confidence score to accept a neural network prediction."""
