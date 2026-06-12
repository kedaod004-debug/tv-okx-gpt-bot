from flask import Flask, request, jsonify
import os
import time
import hmac
import base64
import hashlib
import requests
from openai import OpenAI

app = Flask(__name__)

# 环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_FLAG = os.getenv("OKX_FLAG", "1")


# 首页
@app.route("/")
def home():
    return "TV-OKX-GPT 机器人正在运行"


# 查看是否读取到 OpenAI Key
@app.route("/test-openai")
def test_openai():

    try:

        return jsonify({
            "OPENAI_API_KEY_EXISTS": OPENAI_API_KEY is not None,
            "OPENAI_API_KEY_LENGTH": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
            "OPENAI_API_KEY_PREFIX": OPENAI_API_KEY[:10] if OPENAI_API_KEY else "NONE"
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


# 测试 GPT
@app.route("/test-gpt")
def test_gpt():

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "只回复：OpenAI API 正常"
                }
            ]
        )

        return jsonify({
            "ok": True,
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


# OKX签名
def okx_headers(method, path, body=""):

    timestamp = time.strftime(
        "%Y-%m-%dT%H:%M:%S.000Z",
        time.gmtime()
    )

    message = timestamp + method + path + body

    sign = base64.b64encode(
        hmac.new(
            OKX_SECRET_KEY.encode(),
            message.encode(),
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


# 测试OKX
@app.route("/test-okx")
def test_okx():

    try:

        path = "/api/v5/account/balance"

        url = "https://www.okx.com" + path

        headers = okx_headers(
            "GET",
            path
        )

        result = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        return jsonify({
            "status_code": result.status_code,
            "data": result.json()
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        })


# TradingView Webhook
@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.json

        print("收到TradingView信号")
        print(data)

        return jsonify({
            "ok": True,
            "message": "signal received",
            "data": data
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
