from flask import Flask, jsonify, request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

ALLOWED_ORIGINS = {
    "https://rate-flow-olive.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

ALLOWED_CURRENCIES = ["USD", "EUR", "TRY", "GBP"]
FRANKFURTER_URL = "https://api.frankfurter.app/latest"
REQUEST_TIMEOUT_SECONDS = 20

session = requests.Session()
retry_strategy = Retry(
    total=2,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"

    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def home():
    return jsonify({"message": "RateFlow backend calisiyor"})


@app.route("/convert", methods=["POST", "OPTIONS"])
def convert_currency():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON veri gonderilmedi"}), 400

    base = str(data.get("base", "")).upper()
    quote = str(data.get("quote", "")).upper()
    amount = data.get("amount")

    if base not in ALLOWED_CURRENCIES or quote not in ALLOWED_CURRENCIES:
        return jsonify({"error": "Gecersiz para birimi"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Gecersiz miktar"}), 400

    if amount < 0:
        return jsonify({"error": "Miktar negatif olamaz"}), 400

    try:
        response = session.get(
            FRANKFURTER_URL,
            params={"from": base, "to": quote},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        api_data = response.json()
    except requests.Timeout:
        return jsonify({"error": "Doviz servisi zaman asimina ugradi"}), 504
    except requests.RequestException:
        return jsonify({"error": "Doviz verisi alinamadi"}), 500

    rates = api_data.get("rates", {})
    rate = rates.get(quote)

    if rate is None:
        return jsonify({"error": "Kur bilgisi bulunamadi"}), 500

    result = amount * float(rate)

    return jsonify(
        {
            "base": base,
            "quote": quote,
            "amount": amount,
            "rate": float(rate),
            "result": round(result, 2),
            "date": api_data.get("date"),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
