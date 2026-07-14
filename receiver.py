from flask import Flask, request

app = Flask(__name__)

@app.route("/processOrder", methods=["POST"])
def process_order():
    print("Received Order:")
    print(request.json)

    return {
        "status": "success"
    }

app.run(port=4000)