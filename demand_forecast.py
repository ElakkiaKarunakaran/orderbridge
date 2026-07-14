import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import json

# Training data — order volumes by date
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

# Scenario 1 — Baseline (normal trend)
print("Running Scenario 1: Baseline forecast...")
model_baseline = Prophet(daily_seasonality=False)
model_baseline.fit(df)
future_baseline = model_baseline.make_future_dataframe(periods=14)
forecast_baseline = model_baseline.predict(future_baseline)

# Scenario 2 — Seasonal spike (multiply recent demand by 1.5)
print("Running Scenario 2: Seasonal spike forecast...")
df_spike = df.copy()
df_spike['y'] = df_spike['y'] * 1.5
model_spike = Prophet(daily_seasonality=False)
model_spike.fit(df_spike)
future_spike = model_spike.make_future_dataframe(periods=14)
forecast_spike = model_spike.predict(future_spike)

# Scenario 3 — Demand shock (sudden surge in last 7 days)
print("Running Scenario 3: Demand shock forecast...")
df_shock = df.copy()
df_shock.loc[df_shock.index[-7:], 'y'] = df_shock.loc[df_shock.index[-7:], 'y'] * 2.5
model_shock = Prophet(daily_seasonality=False)
model_shock.fit(df_shock)
future_shock = model_shock.make_future_dataframe(periods=14)
forecast_shock = model_shock.predict(future_shock)

# Print next 7 days forecast for each scenario
print("\n=== 14-Day Demand Forecast ===\n")
for label, forecast in [
    ("Baseline", forecast_baseline),
    ("Seasonal Spike", forecast_spike),
    ("Demand Shock", forecast_shock)
]:
    print(f"Scenario: {label}")
    print("-" * 45)
    future_only = forecast[forecast['ds'] > df['ds'].max()][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(7)
    for _, row in future_only.iterrows():
        print(f"  {row['ds'].strftime('%Y-%m-%d')} | Predicted: {round(row['yhat'])} orders | Range: {round(row['yhat_lower'])}–{round(row['yhat_upper'])}")
    print()

# Save forecast chart
fig = model_baseline.plot(forecast_baseline)
plt.title("OrderBridge — Baseline Demand Forecast")
plt.savefig("forecast_baseline.png")
print("Chart saved: forecast_baseline.png")

# Save forecast data to JSON
output = {
    "baseline": forecast_baseline[['ds', 'yhat']].tail(14).assign(ds=lambda x: x['ds'].astype(str)).to_dict(orient='records'),
    "seasonal_spike": forecast_spike[['ds', 'yhat']].tail(14).assign(ds=lambda x: x['ds'].astype(str)).to_dict(orient='records'),
    "demand_shock": forecast_shock[['ds', 'yhat']].tail(14).assign(ds=lambda x: x['ds'].astype(str)).to_dict(orient='records')
}

with open("forecast_output.json", "w") as f:
    json.dump(output, f, indent=2)

print("Forecast data saved: forecast_output.json")