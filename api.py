"""
OrderBridge Portal API
Serves merged order data, fulfilment tracking, AI demand forecast, and
anomaly detection results to the 4-screen dashboard (index.html).

Run with:
python api.py

Listens on port 6001.
"""

import sqlite3
import json
import os
from flask import Flask, jsonify
from flask_cors import CORS

try:
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")
FORECAST_PATH = os.path.join(
    os.path.dirname(__file__),
    "forecast_output.json"
)


def get_all_events():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT order_id, domain, event_type, timestamp
        FROM order_events
        ORDER BY order_id, timestamp
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return rows


@app.route("/api/orders")
def api_orders():
    """Screen 1 — Latest status for every order."""

    events = get_all_events()
    latest = {}

    for e in events:
        oid = e["order_id"]

        if oid not in latest or e["timestamp"] > latest[oid]["timestamp"]:
            latest[oid] = e

    result = sorted(
        latest.values(),
        key=lambda x: x["order_id"]
    )

    return jsonify(result)


@app.route("/api/history")
def api_history():
    """Screen 2 — Full order event history."""

    return jsonify(get_all_events())


@app.route("/api/tracking")
def api_tracking():
    """Screen 3 — Fulfilment and logistics tracking."""

    events = [
        e for e in get_all_events()
        if e["domain"] in ("fulfilment", "logistics")
    ]

    grouped = {}

    for e in events:
        grouped.setdefault(
            e["order_id"],
            []
        ).append(e)

    for oid in grouped:
        grouped[oid].sort(
            key=lambda x: x["timestamp"]
        )

    return jsonify(grouped)


@app.route("/api/forecast")
def api_forecast():
    """Screen 4 — AI demand forecast."""

    if not os.path.exists(FORECAST_PATH):
        return jsonify({
            "error": "forecast_output.json not found. Run demand_forecast.py first."
        }), 404

    with open(FORECAST_PATH, "r") as f:
        data = json.load(f)

    return jsonify(data)


@app.route("/api/anomalies")
def api_anomalies():
    """Screen 4 — IsolationForest anomaly detection."""

    if not SKLEARN_AVAILABLE:
        return jsonify({
            "error": "scikit-learn / pandas not installed"
        }), 500

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM order_events",
        conn
    )

    conn.close()

    if df.empty:
        return jsonify([])

    event_count = (
        df.groupby("order_id")
        .size()
        .reset_index(name="event_count")
    )

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    model.fit(
        event_count[["event_count"]]
    )

    event_count["prediction"] = model.predict(
        event_count[["event_count"]]
    )

    event_count["status"] = event_count[
        "prediction"
    ].apply(
        lambda x: "Normal"
        if x == 1
        else "Anomaly"
    )

    result = event_count[
        ["order_id", "event_count", "status"]
    ].to_dict(
        orient="records"
    )

    return jsonify(result)


@app.route("/api/health")
def health():
    """API health check."""

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=6001,
        debug=True
    )