import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("training_data.csv")

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=2000))
])

model.fit(df["question"], df["intent"])

joblib.dump(model, "chatbot_model.pkl")

print("Chatbot model trained successfully")