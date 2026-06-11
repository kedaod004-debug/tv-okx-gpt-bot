from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "TV-OKX-GPT Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("收到TradingView信号:", data)

    return jsonify({
        "status": "success",
        "message": "signal received",
        "data": data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
