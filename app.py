from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_URL = os.getenv("DATABASE_URL", "your-postgres-connection-url")

@app.route("/", methods=["POST"])
def handle_webhook():
    data = request.get_json()

    extracted = data.get("data", {}).get("analysis", {}).get("data_collection_results", {})

    age = extracted.get("age", "")
    insurance = extracted.get("insurance", "")
    zip_code = extracted.get("zip_code", "")
    income = extracted.get("income", "")
    household_size = extracted.get("household_size", "")
    willing_to_talk = extracted.get("Willing_to_talk", "")
    life_change = extracted.get("life_change", "")
    qualified = extracted.get("Qualified", "")

    phone = data.get("data", {}).get("metadata", {}).get("phone_call", {}).get("external_number", "")
    first_name = data.get("data", {}).get("conversation_initiation_client_data", {}).get("dynamic_variables", {}).get("firstname", "")

    try:
        conn = psycopg2.connect(DB_URL, sslmode="require")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO public.aca_responses (
                timestamp, first_name, phone, willing_to_talk, zip_code, age,
                household_size, income, insurance, life_change, qualified
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, phone, willing_to_talk, zip_code, age,
              household_size, income, insurance, life_change, qualified))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
