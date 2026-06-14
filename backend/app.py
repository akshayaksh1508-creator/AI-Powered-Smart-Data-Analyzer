from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
import json
from datetime import datetime
app = Flask(__name__)
CORS(app)
latest_df = None
chatbot_model = joblib.load("chatbot_model.pkl")
import os
 
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)
vectorizer = joblib.load(
    "vectorizer.pkl"
)

chat_vectors = joblib.load(
    "chat_vectors.pkl"
)

chat_answers = joblib.load(
    "chat_answers.pkl"
)
def is_greeting(text):
    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]

    return text.lower().strip() in greetings

def answer_chatbot(question):
    q = question.lower()

    q_vector = vectorizer.transform([q])

    similarity = cosine_similarity(q_vector, chat_vectors)

    best = similarity.argmax()
    score = similarity[0][best]

    print(score)        # For debugging

    if score > 0.30:
       return chat_answers[best_match]

    return "I'm not sure about that, but I'd be happy to help if you ask in another way."
def is_dataset_question(question):
    dataset_keywords = [
        "dataset",
        "column",
        "columns",
        "row",
        "rows",
        "average",
        "mean",
        "maximum",
        "minimum",
        "highest",
        "lowest",
        "correlation",
        "trend",
        "prediction",
        "forecast",
        "recommendation",
        "summary",
        "anomaly",
        "outlier",
        "total",
        "median",
        "standard deviation",
        "sales",
        "profit",
        "population",
        "density",
        "growth",
        "country",
        "capital",
        "continent",
        "top",
        "highest",
        "lowest",
        "largest",
        "smallest",
        "mean",
        "sum",
        "average",
        "insight",
        "recommendation",
        "forecast"
        
    ]

    q = question.lower()

    for word in dataset_keywords:
        if word in q:
            return True

    return False


@app.route("/chat", methods=["POST"])
def is_greeting(question):
    q = question.lower().strip()

    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "thanks",
        "thank you"
    ]

    return q in greetings


def dataset_answer(df, question):
    if df is None:
        return None

    q = question.lower().strip()

    if is_greeting(q):
        return None

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    dataset_words = [
        "dataset", "data", "rows", "columns",
        "average", "mean", "highest", "maximum",
        "lowest", "minimum", "top", "correlation",
        "relationship"
    ]

    column_words = [col.lower() for col in df.columns]

    is_dataset_question = (
        any(word in q for word in dataset_words)
        or any(col in q for col in column_words)
    )

    if not is_dataset_question:
        return None

    if "rows" in q:
        return f"The dataset contains {df.shape[0]} rows."

    if "columns" in q:
        return "Columns: " + ", ".join(df.columns)

    if "average" in q or "mean" in q:
        for col in numeric_cols:
            if col.lower() in q:
                return f"The average {col} is {df[col].mean():.2f}."

        if numeric_cols:
            col = numeric_cols[0]
            return f"The average {col} is {df[col].mean():.2f}."

    if "highest" in q or "maximum" in q:
        for col in numeric_cols:
            if col.lower() in q:
                return f"The highest {col} is {df[col].max():.2f}."

        if numeric_cols:
            col = numeric_cols[0]
            return f"The highest {col} is {df[col].max():.2f}."

    if "lowest" in q or "minimum" in q:
        for col in numeric_cols:
            if col.lower() in q:
                return f"The lowest {col} is {df[col].min():.2f}."

        if numeric_cols:
            col = numeric_cols[0]
            return f"The lowest {col} is {df[col].min():.2f}."

    if "top" in q or "most" in q:
        categorical_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

        for col in categorical_cols:
            if col.lower() in q:
                value = df[col].value_counts().idxmax()
                count = df[col].value_counts().max()
                return f"The most common value in {col} is {value}, appearing {count} times."

    if "correlation" in q or "relationship" in q:
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr().abs()
            np.fill_diagonal(corr.values, 0)

            pair = corr.stack().idxmax()
            score = corr.stack().max()

            return f"The strongest relationship is between {pair[0]} and {pair[1]} with correlation {score:.2f}."

        return "Not enough numeric columns to calculate correlation."

    return None


@app.route("/chat", methods=["POST"])
def chat():

    global latest_df

    data = request.get_json()
    question = data.get("question", "").strip()

    if question == "":
        return jsonify({
            "answer": "Please enter a question."
        })

    # Dataset questions
    if latest_df is not None and is_dataset_question(question):

        return jsonify({
            "answer": ml_chat_answer(latest_df, question)
        })

    # General chatbot
    return jsonify({
        "answer": answer_chatbot(question)
    })
def clean_data(df):
    cleaned_df = df.copy()

    duplicates_removed = int(cleaned_df.duplicated().sum())
    cleaned_df = cleaned_df.drop_duplicates()

    missing_before = int(cleaned_df.isnull().sum().sum())

    for col in cleaned_df.columns:
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
        else:
            mode_val = cleaned_df[col].mode()
            cleaned_df[col] = cleaned_df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")

    missing_after = int(cleaned_df.isnull().sum().sum())

    return cleaned_df, duplicates_removed, missing_before - missing_after



def detect_domain(df):
    columns = " ".join(df.columns).lower()

    sales = ["sales", "revenue", "profit", "order", "customer", "product", "price", "discount", "quantity", "region"]
    education = ["student", "marks", "score", "attendance", "class", "subject", "exam", "teacher"]
    healthcare = ["patient", "doctor", "hospital", "disease", "medicine", "treatment", "health", "diagnosis"]

    scores = {
        "Business / Sales": sum(word in columns for word in sales),
        "Education": sum(word in columns for word in education),
        "Healthcare": sum(word in columns for word in healthcare),
    }

    domain = max(scores, key=scores.get)
    return domain if scores[domain] > 0 else "General"


def generate_insights(df):
    insights = []
    recommendations = []

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(
    include=["object", "string"]
).columns.tolist()

    for col in numeric_cols[:5]:
        avg = df[col].mean()
        max_val = df[col].max()
        min_val = df[col].min()

        insights.append(f"{col} has an average value of {avg:.2f}.")
        insights.append(f"{col} ranges from {min_val:.2f} to {max_val:.2f}.")

        if max_val > avg * 2:
            insights.append(f"{col} has unusually high values.")
            recommendations.append(f"Investigate high values in {col} because they may be anomalies.")

    for col in categorical_cols[:3]:
        top = df[col].value_counts().idxmax()
        count = int(df[col].value_counts().max())
        insights.append(f"{top} is the most frequent value in {col}, appearing {count} times.")

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()

        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                value = corr.iloc[i, j]

                if value > 0.7:
                    insights.append(f"{numeric_cols[i]} and {numeric_cols[j]} have a strong positive correlation.")
                    recommendations.append(f"Use {numeric_cols[i]} to understand changes in {numeric_cols[j]}.")
                elif value < -0.7:
                    insights.append(f"{numeric_cols[i]} and {numeric_cols[j]} have a strong negative correlation.")
                    recommendations.append(f"When {numeric_cols[i]} increases, {numeric_cols[j]} may decrease.")

    if not recommendations:
        recommendations.append("Focus on columns with strong trends, high values, or unusual patterns.")
        recommendations.append("Use data-driven decisions instead of assumptions.")

    return insights[:6], recommendations[:6]


def detect_anomalies(df):
    anomalies = []
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()

        if std == 0 or pd.isna(std):
            continue

        lower = mean - 3 * std
        upper = mean + 3 * std

        count = df[(df[col] < lower) | (df[col] > upper)].shape[0]

        if count > 0:
            anomalies.append(f"{count} unusual values detected in {col}.")

    return anomalies if anomalies else ["No major anomalies detected."]


def chart_data(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    line_chart = {
        "labels": [],
        "values": []
    }

    bar_chart = {
        "labels": [],
        "values": []
    }

    if numeric_cols:
        col = numeric_cols[0]
        values = df[col].head(12).fillna(0).tolist()
        line_chart["labels"] = [f"Row {i+1}" for i in range(len(values))]
        line_chart["values"] = values

    if categorical_cols:
        col = categorical_cols[0]
        counts = df[col].value_counts().head(5)
        bar_chart["labels"] = counts.index.astype(str).tolist()
        bar_chart["values"] = counts.values.tolist()

    return line_chart, bar_chart


def prediction_data(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_cols) < 1 or len(df) < 5:
        return {
            "next_value": "Not enough data",
            "actual": [],
            "predicted": []
        }

    col = numeric_cols[0]
    y = df[col].fillna(0).values

    X = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    future_x = np.array([[len(y)]])
    next_value = model.predict(future_x)[0]

    actual = y[-6:].tolist()
    pred = model.predict(X)[-6:].tolist()

    return {
        "next_value": round(float(next_value), 2),
        "actual": [round(float(v), 2) for v in actual],
        "predicted": [round(float(v), 2) for v in pred]
    }

def make_json_safe(value):
    if isinstance(value, dict):
        return {k: make_json_safe(v) for k, v in value.items()}

    if isinstance(value, list):
        return [make_json_safe(v) for v in value]

    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return None

    return value
def answer_data_question(df, question):

    question = question.lower().strip()

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # ---------------- Dataset Summary ----------------

    if any(word in question for word in ["summary", "overview", "describe dataset"]):

        return (
            f"The dataset contains {df.shape[0]} rows and "
            f"{df.shape[1]} columns. "
            f"It includes numeric columns such as "
            f"{', '.join(numeric_cols[:5])}."
        )

    # ---------------- Rows / Columns ----------------

    if any(word in question for word in ["rows", "records"]):
        return f"The dataset contains {df.shape[0]} rows."

    if any(word in question for word in ["columns", "features"]):
        return (
            f"The dataset contains {df.shape[1]} columns: "
            f"{', '.join(df.columns)}."
        )

    # ---------------- Missing Values ----------------

    if "missing" in question:

        missing = df.isnull().sum()

        max_missing_col = missing.idxmax()
        max_missing_val = int(missing.max())

        if max_missing_val == 0:
            return "There are no missing values in the cleaned dataset."

        return (
            f"The column with the most missing values is "
            f"{max_missing_col} with {max_missing_val} missing values."
        )

    # ---------------- Average ----------------

    if any(word in question for word in ["average", "mean", "avg"]):

        for col in numeric_cols:
            if col.lower() in question:
                return (
                    f"The average value of {col} is "
                    f"{df[col].mean():.2f}."
                )

        if numeric_cols:
            col = numeric_cols[0]
            return (
                f"The average value of {col} is "
                f"{df[col].mean():.2f}."
            )

    # ---------------- Highest ----------------

    if any(word in question for word in ["highest", "maximum", "max", "largest"]):

        for col in numeric_cols:
            if col.lower() in question:
                return (
                    f"The highest value in {col} is "
                    f"{df[col].max():.2f}."
                )

        if numeric_cols:
            col = numeric_cols[0]
            return (
                f"The highest value in {col} is "
                f"{df[col].max():.2f}."
            )

    # ---------------- Lowest ----------------

    if any(word in question for word in ["lowest", "minimum", "min", "smallest"]):

        for col in numeric_cols:
            if col.lower() in question:
                return (
                    f"The lowest value in {col} is "
                    f"{df[col].min():.2f}."
                )

        if numeric_cols:
            col = numeric_cols[0]
            return (
                f"The lowest value in {col} is "
                f"{df[col].min():.2f}."
            )

    # ---------------- Most Frequent ----------------

    if any(word in question for word in ["top", "most", "frequent", "best"]):

        for col in categorical_cols:
            if col.lower() in question:

                top_value = df[col].value_counts().idxmax()
                count = int(df[col].value_counts().max())

                return (
                    f"The most frequent value in {col} is "
                    f"{top_value}, appearing {count} times."
                )

        if categorical_cols:

            col = categorical_cols[0]

            top_value = df[col].value_counts().idxmax()
            count = int(df[col].value_counts().max())

            return (
                f"The most frequent value in {col} is "
                f"{top_value}, appearing {count} times."
            )

    # ---------------- Correlation ----------------

    if any(word in question for word in [
        "correlation",
        "relationship",
        "affects",
        "impact",
        "related"
    ]):

        if len(numeric_cols) >= 2:

            corr = df[numeric_cols].corr().abs()

            np.fill_diagonal(corr.values, 0)

            max_pair = corr.stack().idxmax()
            max_value = corr.stack().max()

            return (
                f"The strongest relationship is between "
                f"{max_pair[0]} and {max_pair[1]} "
                f"with correlation {max_value:.2f}."
            )

        return "Not enough numeric columns to calculate correlation."

    # ---------------- Trends ----------------

    if any(word in question for word in [
        "trend",
        "growth",
        "pattern"
    ]):

        if numeric_cols:

            col = numeric_cols[0]

            first = df[col].iloc[0]
            last = df[col].iloc[-1]

            if last > first:
                return (
                    f"{col} shows an increasing trend overall."
                )

            elif last < first:
                return (
                    f"{col} shows a decreasing trend overall."
                )

            else:
                return (
                    f"{col} appears relatively stable."
                )

    # ---------------- Recommendations ----------------

    if any(word in question for word in [
        "recommendation",
        "improve",
        "strategy"
    ]):

        return (
            "AI recommends focusing on high-performing categories, "
            "reducing anomaly-causing values, and improving areas "
            "with low trends or weak performance."
        )

    # ---------------- Anomalies ----------------

    if any(word in question for word in [
        "anomaly",
        "outlier",
        "unusual"
    ]):

        anomalies = detect_anomalies(df)

        return " ".join(anomalies)

    # ---------------- Default ----------------

    return (
        "I could not fully understand the question. "
        "Try asking about averages, highest values, trends, "
        "correlations, recommendations, anomalies, rows, columns, "
        "or dataset summary."
    )
@app.route("/")
def home():
    return jsonify({"message": "Backend running"})

def clean_data(df):
    cleaned_df = df.copy()

    duplicates_removed = int(cleaned_df.duplicated().sum())
    cleaned_df = cleaned_df.drop_duplicates()

    missing_before = int(cleaned_df.isnull().sum().sum())

    for col in cleaned_df.columns:
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
        else:
            mode_val = cleaned_df[col].mode()
            cleaned_df[col] = cleaned_df[col].fillna(
                mode_val[0] if not mode_val.empty else "Unknown"
            )

    missing_after = int(cleaned_df.isnull().sum().sum())

    return cleaned_df, duplicates_removed, missing_before - missing_after
def correlation_heatmap_data(df):
    numeric_cols = (
    df.select_dtypes(include=np.number)
    .columns.tolist()[:6]
)

    if len(numeric_cols) < 2:
        return {
            "columns": [],
            "matrix": []
        }

    corr = df[numeric_cols].corr().replace([np.inf, -np.inf], np.nan).fillna(0)

    return {
        "columns": numeric_cols,
        "matrix": corr.round(2).values.tolist()
    }

BASE_DIR = Path(__file__).resolve().parent

MEMORY_FILE = BASE_DIR / "dataset_memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except:
        return []

def save_memory(memory):
    safe_memory = make_json_safe(memory)

    with open(MEMORY_FILE, "w") as file:
        json.dump(
            safe_memory,
            file,
            indent=4
        )

    print("MEMORY SAVED:", len(memory))


def create_dataset_memory(df, file_name, domain):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    numeric_summary = {}

    for col in numeric_cols[:6]:
        numeric_summary[col] = {
            "mean": float(df[col].mean()),
            "min": float(df[col].min()),
            "max": float(df[col].max())
        }

    memory_item = {
        "file_name": file_name,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "domain": domain,
        "numeric_summary": numeric_summary
    }

    return memory_item


def compare_with_previous_memory(current_memory):
    memory = load_memory()

    if len(memory) == 0:
        return "This is the first dataset stored in memory. Future uploads will be compared with this dataset."

    previous = memory[-1]

    insights = []

    if previous["domain"] == current_memory["domain"]:
        insights.append(
            f"This dataset belongs to the same domain as the previous upload: {current_memory['domain']}."
        )
    else:
        insights.append(
            f"Domain changed from {previous['domain']} to {current_memory['domain']}."
        )

    common_cols = set(previous["numeric_summary"].keys()).intersection(
        set(current_memory["numeric_summary"].keys())
    )

    for col in list(common_cols)[:3]:
        old_mean = previous["numeric_summary"][col]["mean"]
        new_mean = current_memory["numeric_summary"][col]["mean"]

        if old_mean != 0:
            change = ((new_mean - old_mean) / old_mean) * 100

            if change > 0:
                insights.append(
                    f"Average {col} improved by {change:.2f}% compared to the previous upload."
                )
            elif change < 0:
                insights.append(
                    f"Average {col} decreased by {abs(change):.2f}% compared to the previous upload."
                )
            else:
                insights.append(
                    f"Average {col} remained stable compared to the previous upload."
                )

    if not insights:
        return "Dataset memory stored successfully, but no matching numeric columns were found for comparison."

    return " ".join(insights)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)
            file_type = ".csv"
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file)
            file_type = ".xlsx"
        else:
            return jsonify({"error": "Only CSV and Excel files are supported"}), 400

        cleaned_df, duplicates_removed, missing_fixed = clean_data(df)
        global latest_df
        latest_df = cleaned_df.copy()
        numeric_cols = cleaned_df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = cleaned_df.select_dtypes(
    include=["object", "string"]
).columns.tolist()
        
        domain = detect_domain(cleaned_df)
        current_memory = create_dataset_memory(cleaned_df, file.filename, domain)
        memory_insight = compare_with_previous_memory(current_memory)

        memory = load_memory()
        memory.append(current_memory)
        save_memory(memory)
        insights, recommendations = generate_insights(cleaned_df)
        anomalies = detect_anomalies(cleaned_df)
        line_chart, bar_chart = chart_data(cleaned_df)
        prediction = prediction_data(cleaned_df)

        heatmap_data = correlation_heatmap_data(cleaned_df)


        simulator_base = get_simulator_base(cleaned_df)

        safe_df = cleaned_df.replace([np.inf, -np.inf], np.nan)
        safe_df = safe_df.where(pd.notnull(safe_df), None)

        chart_columns = {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "all": cleaned_df.columns.tolist()
        }

        chart_dataset = safe_df.head(100).to_dict(orient="records")

        response_data = {
            "file_name": file.filename,
            "file_type": file_type,
            "rows": int(cleaned_df.shape[0]),
            "columns": int(cleaned_df.shape[1]),
            "numeric_columns": len(numeric_cols),
            "domain": domain,
            "confidence": 92 if domain != "General" else 70,
            "duplicates_removed": int(duplicates_removed),
            "missing_values_fixed": int(missing_fixed),
            "insights": insights,
            "recommendations": recommendations,
            "anomalies": anomalies,
            "line_chart": line_chart,
            "bar_chart": bar_chart,
            "prediction": prediction,
            "chart_columns": chart_columns,
            "chart_dataset": chart_dataset,
            "simulator_base": simulator_base,
            "memory_insight": memory_insight,
            "heatmap_data": heatmap_data
        }

        return jsonify(make_json_safe(response_data))

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/memory", methods=["GET"])
def get_dataset_memory():
    try:
        memory = make_json_safe(load_memory())

        if not memory:
            return jsonify({
                "count": 0,
                "insight": "No dataset memory found yet. Upload a dataset first.",
                "memory": []
            })

        latest = memory[-1]

        if len(memory) == 1:
            insight = (
                f"This is the first dataset stored in memory: {latest['file_name']}. "
                "Upload another dataset to compare patterns."
            )
        else:
            previous = memory[-2]
            insights = []

            insights.append(
                f"Latest dataset: {latest['file_name']}"
            )

            if previous["domain"] == latest["domain"]:
                insights.append(
                    f"This dataset belongs to the same domain as the previous upload: {latest['domain']}."
                )
            else:
                insights.append(
                    f"Domain changed from {previous['domain']} to {latest['domain']}."
                )

            common_cols = set(previous["numeric_summary"].keys()).intersection(
                set(latest["numeric_summary"].keys())
            )

            for col in list(common_cols)[:3]:
                old_mean = previous["numeric_summary"][col]["mean"]
                new_mean = latest["numeric_summary"][col]["mean"]

                if old_mean:
                    change = ((new_mean - old_mean) / old_mean) * 100

                    if change > 0:
                        insights.append(
                            f"Average {col} improved by {change:.2f}% compared to the previous upload."
                        )
                    elif change < 0:
                        insights.append(
                            f"Average {col} decreased by {abs(change):.2f}% compared to the previous upload."
                        )
                    else:
                        insights.append(
                            f"Average {col} remained stable."
                        )

            insight = " ".join(insights)

        return jsonify({
            "count": len(memory),
            "insight": insight,
            "memory": memory
        })

    except Exception as e:
        return jsonify({
            "count": 0,
            "insight": f"Memory error: {str(e)}",
            "memory": []
        }), 500
def answer_data_question(df, question):
    question = question.lower().strip()

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    if any(word in question for word in ["summary", "summarize", "overview", "describe"]):
        cols = ", ".join(df.columns[:6])
        return (
            f"This dataset contains {df.shape[0]} rows and {df.shape[1]} columns. "
            f"Some important columns are {cols}. "
            f"Detected domain: {detect_domain(df)}."
        )

    if "rows" in question:
        return f"The dataset contains {df.shape[0]} rows."

    if "columns" in question:
        return f"The dataset contains {df.shape[1]} columns: {', '.join(df.columns)}."

    if "average" in question or "mean" in question:
        if numeric_cols:
            col = numeric_cols[0]
            return f"The average value of {col} is {df[col].mean():.2f}."

    if "highest" in question or "maximum" in question:
        if numeric_cols:
            col = numeric_cols[0]
            return f"The highest value in {col} is {df[col].max():.2f}."

    if "lowest" in question or "minimum" in question:
        if numeric_cols:
            col = numeric_cols[0]
            return f"The lowest value in {col} is {df[col].min():.2f}."

    if "top" in question or "most" in question:
        if categorical_cols:
            col = categorical_cols[0]
            value = df[col].value_counts().idxmax()
            return f"The most frequent value in {col} is {value}."

    if "correlation" in question or "relationship" in question:
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr().abs()
            np.fill_diagonal(corr.values, 0)
            pair = corr.stack().idxmax()
            score = corr.stack().max()
            return f"The strongest relationship is between {pair[0]} and {pair[1]} with correlation {score:.2f}."

    if "recommendation" in question or "improve" in question:
        return "Focus on strong performing values, reduce anomalies, and improve weak trends."

    if "anomaly" in question or "outlier" in question:
        return "No major anomalies detected."

    return "Try asking: summary, rows, columns, averages, highest values, correlations, recommendations, or anomalies."
def ml_chat_answer(df, question):
    intent = chatbot_model.predict([question])[0]

    q = question.lower().strip()

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    def find_numeric_column():
        for col in numeric_cols:
            if col.lower() in q:
                return col
        return numeric_cols[0] if numeric_cols else None

    if intent == "summary":

        return (
            f"The uploaded dataset contains "
            f"{df.shape[0]} rows and {df.shape[1]} columns. "
            f"It belongs to the {detect_domain(df)} domain.\n\n"
            f"Columns include: {', '.join(df.columns)}."
        )

    if intent == "rows":
        return f"The dataset contains {df.shape[0]} rows."

    if intent == "columns":
        return f"The dataset contains {len(df.columns)} columns:\n\n" + ", ".join(df.columns)

    if intent == "average":
        col = find_numeric_column()
        if col:
            return f"The average value of {col} is {df[col].mean():.2f}."

    if intent == "maximum":

        if numeric_cols:

            col = numeric_cols[0]

            return (
                f"The maximum value in "
                f"{col} is {df[col].max():,.2f}."
            )

    if intent == "minimum":

        if numeric_cols:

            col = numeric_cols[0]

            return (
                f"The minimum value in "
                f"{col} is {df[col].min():,.2f}."
            )

    if intent == "total":
        col = find_numeric_column()
        if col:
            return f"The total value of {col} is {df[col].sum():.2f}."

    if intent == "median":
        col = find_numeric_column()
        if col:
            return f"The median value of {col} is {df[col].median():.2f}."

    if intent == "std":
        col = find_numeric_column()
        if col:
            return f"The standard deviation of {col} is {df[col].std():.2f}."

    if intent == "top":
        for col in categorical_cols:
            if col.lower() in q:
                value = df[col].value_counts().idxmax()
                count = int(df[col].value_counts().max())
                return f"The most common value in {col} is {value}, appearing {count} times."

        if categorical_cols:
            col = categorical_cols[0]
            value = df[col].value_counts().idxmax()
            count = int(df[col].value_counts().max())
            return f"The most common value in {col} is {value}, appearing {count} times."

    if intent == "correlation":
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr().abs()
            np.fill_diagonal(corr.values, 0)
            pair = corr.stack().idxmax()
            score = corr.stack().max()
            return (
                f"The strongest relationship is between {pair[0]} and "
                f"{pair[1]} with correlation {score:.2f}."
            )
        return "Not enough numeric columns to calculate correlation."

    if intent == "anomaly":
        anomalies = detect_anomalies(df)
        return " ".join(anomalies)

    if intent == "recommendation":
        return (
            "Focus on improving weak-performing areas, reducing anomalies, "
            "and analyzing highly correlated columns."
        )

    if intent == "trend":

        if numeric_cols:

            col = numeric_cols[0]

            if df[col].iloc[-1] > df[col].iloc[0]:

                return f"{col} shows an increasing trend."

            elif df[col].iloc[-1] < df[col].iloc[0]:

                return f"{col} shows a decreasing trend."

            else:

                return f"{col} remains relatively stable."
    if intent == "prediction":
        prediction = prediction_data(df)
        return f"The predicted next value is {prediction['next_value']}."

    if intent == "insight":
        insights, recommendations = generate_insights(df)
        return " ".join(insights[:3])

    return None

def get_simulator_base(df):
    numeric_df = df.copy()

    # Convert possible numeric columns
    for col in numeric_df.columns:
        converted = pd.to_numeric(numeric_df[col], errors="coerce")

        if converted.notna().sum() > 0:
            numeric_df[col] = converted

    sales_col = None
    profit_col = None
    discount_col = None
    customer_col = None

    for col in numeric_df.columns:
        col_lower = col.lower().strip()

        if any(word in col_lower for word in ["sales", "revenue", "amount", "income"]):
            sales_col = col

        if any(word in col_lower for word in ["profit", "margin", "gain"]):
            profit_col = col

        if any(word in col_lower for word in ["discount", "offer"]):
            discount_col = col

        if any(word in col_lower for word in ["customer", "client", "buyer"]):
            customer_col = col

    def safe_avg(column):
        if column and pd.api.types.is_numeric_dtype(numeric_df[column]):
            return float(numeric_df[column].mean())
        return 0

    base_data = {
        "sales_col": sales_col,
        "profit_col": profit_col,
        "discount_col": discount_col,
        "customer_col": customer_col,
        "avg_sales": safe_avg(sales_col),
        "avg_profit": safe_avg(profit_col),
        "avg_discount": safe_avg(discount_col),
        "customer_count": int(numeric_df[customer_col].nunique()) if customer_col else int(len(numeric_df))
    }

    return base_data


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )