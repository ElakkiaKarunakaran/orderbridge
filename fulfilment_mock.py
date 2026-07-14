from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

fulfilment_events = [
    {"order_id": 1, "domain": "fulfilment", "event_type": "allocated", "timestamp": "2026-07-01T10:00:00Z"},
    {"order_id": 2, "domain": "fulfilment", "event_type": "packed", "timestamp": "2026-07-02T11:30:00Z"},
    {"order_id": 3, "domain": "fulfilment", "event_type": "allocated", "timestamp": "2026-07-03T12:00:00Z"},
    {"order_id": 4, "domain": "fulfilment", "event_type": "cancelled", "timestamp": "2026-07-04T09:00:00Z"},
    {"order_id": 5, "domain": "fulfilment", "event_type": "dispatched", "timestamp": "2026-07-05T15:00:00Z"},
    {"order_id": 6, "domain": "fulfilment", "event_type": "packed", "timestamp": "2026-07-06T17:00:00Z"}
]

@app.route('/fulfilment')
def get_fulfilment():
    return jsonify(fulfilment_events)

if __name__ == '__main__':
    app.run(port=4000)