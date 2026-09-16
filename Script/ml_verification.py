# ml_verification.py
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_PATH = MODEL_DIR / "verification_model.pkl"


def load_ml_model():
    return joblib.load(MODEL_PATH)


def predict_credibility(text: str, model=None) -> float:
    """
    Returns a credibility score in [0, 1].
    Higher = more likely to be true/credible.
    """
    if model is None:
        model = load_ml_model()
    proba = model.predict_proba([text])[0]
    # Assuming class 1 = "credible/true"
    return float(proba[1])