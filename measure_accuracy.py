"""
D-15: Prophet forecast accuracy metric (MAPE).
Holdout backtest: train on the first 23 days of known order-volume data,
forecast the next 7 days, and compare against the actual held-out values
to compute Mean Absolute Percentage Error.

Run with: python measure_accuracy.py
Requires: prophet, pandas (same as demand_forecast.py)
"""
import pandas as pd
from prophet import Prophet
import json

# Same training data as demand_forecast.py (order volumes by date)
data = {
    'ds': [
        '2026-06-01', '2026-06-02', '2026-06-03', '2026-06-04', '2026-06-05',
        '2026-06-06', '2026-06-07', '2026-06-08', '2026-06-09', '2026-06-10',
        '2026-06-11', '2026-06-12', '2026-06-13', '2026-06-14', '2026-06-15',
        '2026-06-16', '2026-06-17', '2026-06-18', '2026-06-19', '2026-06-20',
        '2026-06-21', '2026-06-22', '2026-06-23', '2026-06-24', '2026-06-25',
        '2026-06-26', '2026-06-27', '2026-06-28', '2026-06-29', '2026-06-30'
    ],
    'y': [
        12, 15, 10, 18, 22, 20, 25, 19, 17, 23,
        28, 30, 27, 24, 31, 35, 33, 29, 38, 40,
        36, 32, 41, 45, 43, 39, 47, 50, 48, 44
    ]
}
df = pd.DataFrame(data)
df['ds'] = pd.to_datetime(df['ds'])
df['y'] = df['y'].astype(float)

HOLDOUT_DAYS = 7
train = df.iloc[:-HOLDOUT_DAYS].copy()
actual_holdout = df.iloc[-HOLDOUT_DAYS:].copy()

print(f"Training on {len(train)} days, holding out last {HOLDOUT_DAYS} days for validation...")
model = Prophet(daily_seasonality=False)
model.fit(train)

future = model.make_future_dataframe(periods=HOLDOUT_DAYS)
forecast = model.predict(future)
predicted_holdout = forecast[['ds', 'yhat']].tail(HOLDOUT_DAYS).reset_index(drop=True)

actual_holdout = actual_holdout.reset_index(drop=True)
comparison = actual_holdout[['ds', 'y']].merge(predicted_holdout, on='ds')
comparison['abs_pct_error'] = (comparison['y'] - comparison['yhat']).abs() / comparison['y']

mape = comparison['abs_pct_error'].mean() * 100

print("\n=== Holdout Validation: Actual vs Predicted ===")
for _, row in comparison.iterrows():
    print(f"  {row['ds'].date()} | Actual: {int(row['y'])} | Predicted: {round(row['yhat'],1)} | Error: {round(row['abs_pct_error']*100,1)}%")

print(f"\nMAPE (Mean Absolute Percentage Error): {mape:.2f}%")
print(f"Target (per proposal): MAPE < 15%")
print(f"Result: {'PASS' if mape < 15 else 'FAIL'}")

# Save result for evidence / doc reference
with open("accuracy_report.json", "w") as f:
    json.dump({
        "holdout_days": HOLDOUT_DAYS,
        "mape_percent": round(mape, 2),
        "target_percent": 15,
        "pass": bool(mape < 15),
        "details": comparison.assign(ds=lambda x: x['ds'].astype(str)).to_dict(orient='records')
    }, f, indent=2)
print("\nSaved: accuracy_report.json")