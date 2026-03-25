from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

ALLOWED_CURRENCIES = ["USD", "EUR", "TRY", "GBP"]
FRANKFURTER_URL = "https://api.frankfurter.app/latest"


@app.route("/")
def home():
    return jsonify({"message": "RateFlow backend calisiyor"})


@app.route("/convert", methods=["POST"])
def convert_currency():
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
        response = requests.get(
            FRANKFURTER_URL,
            params={"from": base, "to": quote},
            timeout=10,
        )
        response.raise_for_status()
        api_data = response.json()
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
