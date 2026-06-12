from flask import Flask, request, jsonify
import os, time, hmac, base64, hashlib, requests
from openai import OpenAI

app = Flask(__name__)

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_FLAG = os.getenv("OKX_FLAG", "1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


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
    return "TV-OKX-GPT 机器人正在运行"


@app.route("/test-openai")
def test_openai():
    return jsonify({
        "OPENAI_API_KEY_EXISTS": OPENAI_API_KEY is not None,
        "OPENAI_API_KEY_LENGTH": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "OPENAI_API_KEY_PREFIX": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "NONE"
    })
    try:
        if not OPENAI_API_KEY:
            return jsonify({"ok": False, "error": "OPENAI_API_KEY 没有读取到"})

        client = OpenAI(api_key=OPENAI_API_KEY)

        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "只回复：OpenAI API 正常"}
            ]
        )

        return jsonify({
            "ok": True,
            "result": r.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


@app.route("/test-okx")
def test_okx():
    try:
        path = "/api/v5/account/balance"
        url = "https://www.okx.com" + path
        headers = okx_headers("GET", path)
        r = requests.get(url, headers=headers, timeout=10)

        return jsonify({
            "ok": True,
            "status_code": r.status_code,
            "data": r.json()
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("收到TradingView信号:", data)

    return jsonify({
        "ok": True,
        "message": "signal received",
        "data": data
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
