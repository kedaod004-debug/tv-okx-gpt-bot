from flask import Flask, request, jsonify
import os, time, hmac, base64, hashlib, requests
from openai import OpenAI

app = Flask(__name__)

# ===== 环境变量 =====
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_FLAG = os.getenv("OKX_FLAG", "1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ===== OKX 请求头 =====
def okx_headers(method, path, body=""):
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    msg = timestamp + method + path + body
    sign = base64.b64encode(
        hmac.new(
            OKX_SECRET_KEY.encode(),
            msg.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    return {
        "OK-ACCESS-KEY": OKX_API_KEY,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
        "x-simulated-trading": OKX_FLAG
    }


# ===== 根接口 =====
@app.route("/")
def home():
    return "TV-OKX-GPT Bot Running"


# ===== OpenAI 测试接口 =====
@app.route("/test-openai")
def test_openai():
    if not OPENAI_API_KEY:
        return jsonify({
            "ok": False,
            "error": "OPENAI_API_KEY 未读取到"
        })

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input="只回复：OpenAI API 正常"
        )
        return jsonify({
            "ok": True,
            "result": response.output_text
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


# ===== OKX 测试接口 =====
@app.route("/test-okx")
def test_okx():
    try:
        path = "/api/v5/account/balance"
        url = "https://www.okx.com" + path
        headers = okx_headers("GET", path)
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


# ===== TradingView Webhook 接口 =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("收到TradingView信号:", data)

    return jsonify({
        "status": "success",
        "message": "signal received",
        "data": data
    })


# ===== 主程序 =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
