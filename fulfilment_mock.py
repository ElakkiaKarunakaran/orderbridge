from flask import Flask, jsonify

app = Flask(__name__)

fulfilment_events = [
    {
        "order_id": 1,
        "domain": "fulfilment",
        "event_type": "allocated",
        "timestamp": "2026-07-14T10:15:00Z"
    },
    {
        "order_id": 2,
        "domain": "fulfilment",
        "event_type": "packed",
        "timestamp": "2026-07-14T11:20:00Z"
    }
]

@app.route("/fulfilment")
def get_fulfilment():
    return jsonify(fulfilment_events)

if __name__ == "__main__":
    app.run(debug=True, port=4000)