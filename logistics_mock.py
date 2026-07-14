from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

logistics_events = [
    {"order_id": 1, "domain": "logistics", "event_type": "in-transit", "timestamp": "2026-07-01T13:00:00Z"},
    {"order_id": 2, "domain": "logistics", "event_type": "out-for-delivery", "timestamp": "2026-07-02T14:00:00Z"},
    {"order_id": 3, "domain": "logistics", "event_type": "in-transit", "timestamp": "2026-07-03T15:00:00Z"},
    {"order_id": 4, "domain": "logistics", "event_type": "returned", "timestamp": "2026-07-04T10:00:00Z"},
    {"order_id": 5, "domain": "logistics", "event_type": "delivered", "timestamp": "2026-07-05T17:30:00Z"},
    {"order_id": 6, "domain": "logistics", "event_type": "in-transit", "timestamp": "2026-07-06T18:00:00Z"}
]

@app.route('/logistics')
def get_logistics():
    return jsonify(logistics_events)

if __name__ == '__main__':
    app.run(port=5000)