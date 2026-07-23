import os

import numpy as np
import pickle

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import LabelEncoder
from src.scripts.config import *
from src.scripts.preprocessing import preprocess_data, bow


def create_model(input_size: int, output_size: int):
    """
    3-layer network with batch normalisation and dropout.
    """
    model = Sequential()

    model.add(Dense(256, input_shape=(input_size,), activation="relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.4))

    model.add(Dense(128, activation="relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))

    model.add(Dense(output_size, activation="softmax"))

    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer=Adam(learning_rate=0.001),
        metrics=["accuracy"],
    )
    return model


def load_or_train_model(force_retrain=False):
    """
    Loads a cached model or trains a new one from scratch.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not force_retrain and all(
        os.path.exists(path)
        for path in [MODEL_PATH, WORDS_PATH, CLASSES_PATH, LABEL_ENCODER_PATH]
    ):
        model = load_model(MODEL_PATH)
        words = pickle.load(open(WORDS_PATH, "rb"))
        classes = pickle.load(open(CLASSES_PATH, "rb"))
        label_encoder = pickle.load(open(LABEL_ENCODER_PATH, "rb"))
    else:
        words, classes, documents = preprocess_data()

        training_data = [bow(doc[0], words) for doc in documents]
        training_labels = [doc[1] for doc in documents]

        label_encoder = LabelEncoder()
        training_labels = label_encoder.fit_transform(training_labels)

        pickle.dump(label_encoder, open(LABEL_ENCODER_PATH, "wb"))

        model = create_model(len(words), len(classes))

        early_stopping = EarlyStopping(
            monitor="loss", patience=50, restore_best_weights=True
        )

        model.fit(
            np.array(training_data),
            np.array(training_labels),
            epochs=500,
            batch_size=32,
            verbose=1,
            callbacks=[early_stopping],
        )

        model.save(MODEL_PATH)
        pickle.dump(words, open(WORDS_PATH, "wb"))
        pickle.dump(classes, open(CLASSES_PATH, "wb"))

    return model, words, classes, label_encoder
