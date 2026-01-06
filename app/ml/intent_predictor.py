import pickle
import os
from typing import Tuple

MODEL_DIR = "app/ml/model"

_vectorizer = None
_model = None


def load_model():
    global _vectorizer, _model

    if _vectorizer is None or _model is None:
        with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
            _vectorizer = pickle.load(f)

        with open(os.path.join(MODEL_DIR, "intent_model.pkl"), "rb") as f:
            _model = pickle.load(f)


def predict_intent(text: str) -> Tuple[str, float]:
    """
    Returns (intent, confidence)
    """

    load_model()

    X = _vectorizer.transform([text])
    probs = _model.predict_proba(X)[0]

    best_idx = probs.argmax()
    intent = _model.classes_[best_idx]
    confidence = probs[best_idx]

    return intent, float(confidence)
