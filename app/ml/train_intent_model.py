from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

from app.ml.data.intent_dataset import TRAINING_DATA

# Split data
texts = [item[0] for item in TRAINING_DATA]
labels = [item[1] for item in TRAINING_DATA]

# Vectorizer
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    lowercase=True,
)

X = vectorizer.fit_transform(texts)

# Classifier
model = LogisticRegression(
    max_iter=1000,
)

model.fit(X, labels)

# Save model artifacts
os.makedirs("app/ml/model", exist_ok=True)

with open("app/ml/model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("app/ml/model/intent_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Intent model trained and saved successfully.")
