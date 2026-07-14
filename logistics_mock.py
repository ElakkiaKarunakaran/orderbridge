from flask import Flask, jsonify

app = Flask(__name__)

logistics_events = [
    {"order_id": 1, "domain": "logistics", "event_type": "in-transit", "timestamp": "2026-07-14T12:00:00Z"},
    {"order_id": 2, "domain": "logistics", "event_type": "out-for-delivery", "timestamp": "2026-07-14T13:30:00Z"}
]

@app.route('/logistics')
def get_logistics():
    return jsonify(logistics_events)

if __name__ == '__main__':
    app.run(port=5000)