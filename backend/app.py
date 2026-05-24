from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
CORS(app)
latest_df = None
<<<<<<< HEAD
import os
 
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

gemini_key = os.getenv("GEMINI_API_KEY")

print("GEMINI FOUND:", bool(gemini_key))

genai.configure(
    api_key=gemini_key
)

model = genai.GenerativeModel("gemini-2.0-flash")
=======


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

>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15

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
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

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
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

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
<<<<<<< HEAD
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
=======


>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
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
        categorical_cols = cleaned_df.select_dtypes(include=["object"]).columns.tolist()

        domain = detect_domain(cleaned_df)
        insights, recommendations = generate_insights(cleaned_df)
        anomalies = detect_anomalies(cleaned_df)
        line_chart, bar_chart = chart_data(cleaned_df)
        prediction = prediction_data(cleaned_df)
<<<<<<< HEAD
        heatmap_data = correlation_heatmap_data(cleaned_df)
=======
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
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
<<<<<<< HEAD
            "heatmap_data": heatmap_data,
=======
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
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
            "simulator_base": simulator_base
        }

        return jsonify(make_json_safe(response_data))

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"error": str(e)}), 500
<<<<<<< HEAD

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
=======
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
@app.route("/chat", methods=["POST"])
def chat_with_data():
    try:
        global latest_df

        if latest_df is None:
            return jsonify({
                "answer": "Please upload and analyze a dataset first."
            })

        data = request.get_json()
        question = data.get("question", "")

        if question.strip() == "":
            return jsonify({
                "answer": "Please enter a question."
            })

<<<<<<< HEAD
        try:
            columns = ", ".join(latest_df.columns)
            sample_rows = latest_df.head(20).to_string()

            prompt = f"""
You are an AI Data Analyst assistant.

Answer using this uploaded dataset.

Columns:
{columns}

Sample rows:
{sample_rows}

Question:
{question}

Give a clear and useful answer.
"""

            response = model.generate_content(prompt)

            return jsonify({
                "answer": response.text
            })

        except Exception:
            answer = answer_data_question(latest_df, question)

            return jsonify({
                "answer": answer
            })
=======
        answer = answer_data_question(latest_df, question)

        return jsonify({
            "answer": answer
        })
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15

    except Exception as e:
        return jsonify({
            "answer": f"Error: {str(e)}"
        }), 500
<<<<<<< HEAD
=======
    
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
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
    app.run(debug=True)