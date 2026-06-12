from flask import Flask, request, jsonify
import os, time, hmac, base64, hashlib, requests
from openai import OpenAI

app = Flask(__name__)

# 读取环境变量
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_FLAG = os.getenv("OKX_FLAG", "1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 打印调试日志，部署后可在 Console 里看到
print("=== Environment Variables ===")
print("OKX_API_KEY:", OKX_API_KEY[:6] + "..." if OKX_API_KEY else "None")
print("OKX_SECRET_KEY:", OKX_SECRET_KEY[:6] + "..." if OKX_SECRET_KEY else "None")
print("OKX_PASSPHRASE:", OKX_PASSPHRASE[:6] + "..." if OKX_PASSPHRASE else "None")
print("OPENAI_API_KEY:", OPENAI_API_KEY[:6] + "..." if OPENAI_API_KEY else "None")
print("=============================")

# OKX 请求头生成
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

@app.route("/")
def home():
    return "TV-OKX-GPT Bot Running"

@app.route("/test-openai")
def test_openai():
    if not OPENAI_API_KEY:
        return jsonify({"ok": False, "error": "OPENAI_API_KEY 没有读取到"})

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        r = client.responses.create(
            model="gpt-4.1-mini",
            input="只回复：OpenAI API 正常"
        )
        return jsonify({"ok": True, "result": r.output_text})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route("/test-okx")
def test_okx():
    path = "/api/v5/account/balance"
    url = "https://www.okx.com" + path
    headers = okx_headers("GET", path)
    r = requests.get(url, headers=headers, timeout=10)
    return jsonify(r.json())

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
