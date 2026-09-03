import os
import json
import sqlite3

# Remove possible proxy environment variables that can interfere with httpx
for key in [
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy"
]:
    os.environ.pop(key, None)

try:
    from google import genai
except ImportError:
    raise SystemExit("Missing package. Run: pip install --upgrade google-genai")

import pandas as pd
from sklearn.ensemble import IsolationForest

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise SystemExit(
        "GEMINI_API_KEY not set. In PowerShell run:\n"
        '$env:GEMINI_API_KEY="your-key-here"\n'
        "then re-run this script in the SAME terminal."
    )

FORECAST_PATH = "forecast_output.json"
DB_PATH = "orders.db"


def load_forecast():
    if not os.path.exists(FORECAST_PATH):
        raise SystemExit(
            f"{FORECAST_PATH} not found. Run demand_forecast.py first."
        )

    with open(FORECAST_PATH, "r") as f:
        return json.load(f)


def compute_anomalies():
    conn = sqlite3.connect(DB_PATH)

    try:
        df = pd.read_sql_query(
            "SELECT * FROM order_events",
            conn
        )
    finally:
        conn.close()

    if df.empty:
        return []

    event_count = (
        df.groupby("order_id")
        .size()
        .reset_index(name="event_count")
    )

    # IsolationForest needs enough records to work reliably
    if len(event_count) < 2:
        return []

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    model.fit(event_count[["event_count"]])

    event_count["prediction"] = model.predict(
        event_count[["event_count"]]
    )

    event_count["status"] = event_count["prediction"].apply(
        lambda x: "Normal" if x == 1 else "Anomaly"
    )

    anomalies = event_count[
        event_count["status"] == "Anomaly"
    ][["order_id", "event_count"]].to_dict(
        orient="records"
    )

    return anomalies


def build_prompt(forecast, anomalies):
    baseline = forecast.get("baseline", [])
    spike = forecast.get("seasonal_spike", [])
    shock = forecast.get("demand_shock", [])

    baseline_summary = (
        f"{baseline[0]['yhat']:.0f} -> "
        f"{baseline[-1]['yhat']:.0f} orders/day"
        if baseline else "N/A"
    )

    spike_summary = (
        f"{spike[0]['yhat']:.0f} -> "
        f"{spike[-1]['yhat']:.0f} orders/day"
        if spike else "N/A"
    )

    shock_summary = (
        f"{shock[0]['yhat']:.0f} -> "
        f"{shock[-1]['yhat']:.0f} orders/day"
        if shock else "N/A"
    )

    anomaly_text = (
        ", ".join(
            f"Order #{a['order_id']} "
            f"({a['event_count']} events)"
            for a in anomalies
        )
        if anomalies
        else "None detected this period."
    )

    return f"""You are an order operations analyst writing a weekly intelligence
briefing for a commercial operations team.

Using ONLY the data below, write a concise executive summary of approximately
150-200 words covering:

1) The 14-day demand outlook across the three scenarios
2) Any anomalies flagged and what they might mean operationally
3) One concrete recommended action for the fulfilment team

DATA:
- Baseline demand forecast (14-day trend): {baseline_summary}
- Seasonal spike scenario: {spike_summary}
- Demand shock scenario: {shock_summary}
- Anomalies detected (IsolationForest): {anomaly_text}

Write in plain business language, no markdown headers, as one flowing narrative.
"""


def main():
    forecast = load_forecast()
    anomalies = compute_anomalies()
    prompt = build_prompt(forecast, anomalies)

    client = genai.Client(api_key=API_KEY)

    print("Calling Gemini 3.6 Flash...")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
    except Exception as e:
        print("\nGemini API request failed.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        raise

    narrative = response.text

    print("\n=== AI-Generated Weekly Order Intelligence Narrative ===\n")
    print(narrative)

    output = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "anomalies_detected": anomalies,
        "narrative": narrative,
    }

    with open("ai_narrative_report.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\nSaved: ai_narrative_report.json")


if __name__ == "__main__":
    main()