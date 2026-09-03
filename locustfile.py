"""
D-14: Locust load test.
Simulates concurrent users hitting the OrderBridge API to validate it can
handle 5,000+ order events / sustained load without breaking.

Run with: locust -f locustfile.py --host=http://localhost:6000
Then open http://localhost:8089 in your browser to start the test from a UI.

Requires: api.py running on port 6000 first.
"""
from locust import HttpUser, task, between


class OrderBridgeUser(HttpUser):
    # Each simulated user waits 0.5-2s between requests, mimicking real usage
    wait_time = between(0.5, 2)

    @task(3)
    def get_orders(self):
        """Screen 1 — Order Status (most frequently hit, like a real dashboard)."""
        self.client.get("/api/orders", name="/api/orders")

    @task(2)
    def get_history(self):
        """Screen 2 — Order History."""
        self.client.get("/api/history", name="/api/history")

    @task(2)
    def get_tracking(self):
        """Screen 3 — Fulfilment Tracking."""
        self.client.get("/api/tracking", name="/api/tracking")

    @task(1)
    def get_forecast(self):
        """Screen 4 — AI Demand Intelligence (forecast)."""
        self.client.get("/api/forecast", name="/api/forecast")

    @task(1)
    def get_anomalies(self):
        """Screen 4 — AI Demand Intelligence (anomalies) — heaviest endpoint,
        runs IsolationForest live on every call."""
        self.client.get("/api/anomalies", name="/api/anomalies")

    @task(1)
    def health_check(self):
        self.client.get("/api/health", name="/api/health")