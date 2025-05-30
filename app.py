from flask import Flask, request
import psycopg2
import os
import traceback

app = Flask(__name__)

# PostgreSQL connection
DB_URL = os.environ.get("DATABASE_URL")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Received data:", data)

        vars = data.get("analysis", {}).get("extracted_variables", {})
        phone = data.get("data", {}).get("metadata", {}).get("phone_call", {}).get("external_number", "")
        first_name = data.get("data", {}).get("conversation_initiation_client_data", {}).get("dynamic_variables", {}).get("firstname", "")

        age = vars.get("age", "")
        insurance = vars.get("insurance", "")
        zip_code = vars.get("zip_code", "")
        income = vars.get("income", "")
        household_size = vars.get("household_size", "")
        willing_to_talk = vars.get("Willing_to_talk", "")
        life_change = vars.get("life_change", "")
        qualified = vars.get("Qualified", "")

        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO public.aca_responses 
            (first_name, phone, willing_to_talk, zip_code, age, household_size, income, insurance, life_change, qualified) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, phone, willing_to_talk, zip_code, age, household_size, income, insurance, life_change, qualified))
        conn.commit()
        cur.close()
        conn.close()

        return "Success", 200

    except Exception as e:
        print("Error occurred:")
        traceback.print_exc()
        return "Internal Server Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
