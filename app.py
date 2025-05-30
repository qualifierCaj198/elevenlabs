from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL")

def insert_data(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Extract values from the payload
    zip_code = data.get("zip_code", {}).get("value")
    age = data.get("age", {}).get("value")
    income = data.get("income", {}).get("value")
    household = data.get("household", {}).get("value")
    insurance = data.get("insurance", {}).get("value")
    life_change = data.get("life_change", {}).get("value")
    result = data.get("result", {}).get("value")

    cur.execute(
        """
        INSERT INTO public.aca_responses (zip, age, income, household, insurance, life_change, result)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (zip_code, age, income, household, insurance, life_change, result)
    )

    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["POST"])
def handle_webhook():
    payload = request.json
    try:
        data = payload.get("data", {}).get("analysis", {}).get("data_collection_results", {})
        insert_data(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
