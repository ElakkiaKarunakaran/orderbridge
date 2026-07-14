import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest


# Connect database
conn = sqlite3.connect("orders.db")


# Read existing orders
df = pd.read_sql_query(
    "SELECT * FROM order_events",
    conn
)


# Add artificial anomaly order
anomaly_data = []

for i in range(20):
    anomaly_data.append({
        "order_id": 99,
        "domain": "order_capture",
        "event_type": "placed",
        "timestamp": "2026-07-14T15:00:00Z"
    })


anomaly_df = pd.DataFrame(anomaly_data)


# Combine normal + anomaly data
df = pd.concat(
    [df, anomaly_df],
    ignore_index=True
)


conn.close()


print("Total Events:")
print(len(df))


# Create feature: number of events per order

event_count = (
    df.groupby("order_id")
    .size()
    .reset_index(name="event_count")
)


print("\nEvent Count:")
print(event_count)


# Train IsolationForest

model = IsolationForest(
    contamination=0.1,
    random_state=42
)


model.fit(
    event_count[["event_count"]]
)


# Detect anomalies

event_count["prediction"] = model.predict(
    event_count[["event_count"]]
)


# Convert result

event_count["status"] = event_count["prediction"].apply(
    lambda x: "Normal" if x == 1 else "Anomaly"
)


print("\nDetection Result:")
print(
    event_count[
        ["order_id","event_count","status"]
    ]
)