from flask import Flask, request, jsonify
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Logging config
logging.basicConfig(level=logging.INFO)

# Database config (use your Render environment variables or hardcoded values for local testing)
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'your_db'),
    'user': os.getenv('DB_USER', 'your_user'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
}

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logging.info("📥 Received payload: %s", data)

        call_data = data.get("data", {})
        meta = call_data.get("metadata", {})
        analysis = call_data.get("analysis", {})
        collected = analysis.get("data_collection_results", {})
        dynamic = call_data.get("conversation_initiation_client_data", {}).get("dynamic_variables", {})

        def safe_get(key):
            return collected.get(key, {}).get("value")

        values = {
            "conversation_id": call_data.get("conversation_id"),
            "agent_id": call_data.get("agent_id"),
            "zip_code": safe_get("zip_code"),
            "age": safe_get("age"),
            "household_size": safe_get("household_size"),
            "income": safe_get("income"),
            "insurance": safe_get("insurance"),
            "life_change": safe_get("life_change"),
            "qualified": safe_get("Qualified"),
            "willing_to_talk": safe_get("Willing_to_talk"),
            "call_successful": analysis.get("call_successful"),
            "call_duration_secs": meta.get("call_duration_secs"),
            "call_sid": meta.get("phone_call", {}).get("call_sid"),
            "external_number": meta.get("phone_call", {}).get("external_number"),
            "agent_number": meta.get("phone_call", {}).get("agent_number"),
            "result": collected.get("Qualified", {}).get("value"),
            "first_name": safe_get("first_name"),
            "phone_number": safe_get("phone_number")
        }

        logging.info("📤 Extracted values: %s", values)

        insert_into_db(values)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.exception("❌ Webhook processing failed")
        return jsonify({"status": "error", "message": str(e)}), 500

def insert_into_db(values):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO aca_responses (
                    conversation_id, agent_id, zip_code, age, household_size, income,
                    insurance, life_change, qualified, willing_to_talk, call_successful,
                    call_duration_secs, call_sid, external_number, agent_number,
                    result, first_name, phone_number
                )
                VALUES (
                    %(conversation_id)s, %(agent_id)s, %(zip_code)s, %(age)s, %(household_size)s,
                    %(income)s, %(insurance)s, %(life_change)s, %(qualified)s, %(willing_to_talk)s,
                    %(call_successful)s, %(call_duration_secs)s, %(call_sid)s, %(external_number)s,
                    %(agent_number)s, %(result)s, %(first_name)s, %(phone_number)s
                )
            """, values)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
