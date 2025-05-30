import os
import json
import psycopg2
from flask import Flask, request

app = Flask(__name__)

# Database credentials from environment variables
DB_HOST = os.getenv("DB_HOST", "your-db-host")
DB_NAME = os.getenv("DB_NAME", "your-db-name")
DB_USER = os.getenv("DB_USER", "your-db-user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your-db-password")
DB_PORT = os.getenv("DB_PORT", "5432")

@app.route("/", methods=["GET"])
def index():
    return "Server is live", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📥 Received data:")
        print(json.dumps(data, indent=2))

        tool_calls = data.get("data", {}).get("tool_calls", [])
        if tool_calls and isinstance(tool_calls[-1], dict):
            params_json_str = tool_calls[-1].get("params_as_json", "{}")
            try:
                params = json.loads(params_json_str)
                metadata = params.get("metadata", {})
            except json.JSONDecodeError:
                metadata = {}
        else:
            metadata = {}

        print("✅ Extracted metadata:", metadata)

        # Extract variables
        zip_code = metadata.get("zip")
        age = metadata.get("age")
        household_size = metadata.get("household")
        income = metadata.get("income")
        insurance = metadata.get("insurance")
        life_change = metadata.get("lifeChange")
        result = metadata.get("result")
        first_name = metadata.get("first_name")
        phone_number = metadata.get("phone_number")

        print("📦 Preparing to insert:", {
            "zip_code": zip_code,
            "age": age,
            "household_size": household_size,
            "income": income,
            "insurance": insurance,
            "life_change": life_change,
            "result": result,
            "first_name": first_name,
            "phone_number": phone_number
        })

        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.aca_responses (
                zip_code, age, household_size, income,
                insurance, life_change, result, first_name, phone_number
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                zip_code, age, household_size, income,
                insurance, life_change, result, first_name, phone_number
            )
        )
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Data inserted successfully.")

        return "Success", 200

    except Exception as e:
        print("❌ Error occurred:")
        print(str(e))
        return "Internal Server Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
