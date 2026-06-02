import joblib

from sklearn.feature_extraction.text import TfidfVectorizer

questions = []
answers = []

with open(
    "dialogs.txt",
    "r",
    encoding="utf-8"
) as file:
    for line in file:
        parts = line.strip().split("\t")

        if len(parts) == 2:
            questions.append(parts[0].lower())
            answers.append(parts[1])

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

vectors = vectorizer.fit_transform(
    questions
)

joblib.dump(
    vectorizer,
    "vectorizer.pkl"
)

joblib.dump(
    vectors,
    "chat_vectors.pkl"
)

joblib.dump(
    answers,
    "chat_answers.pkl"
)

print("Training complete")
print("Questions:", len(questions))