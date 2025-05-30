from flask import Flask, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Read DB and port from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
PORT = int(os.environ.get("PORT", 5000))  # Fallback for local testing

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        extracted = data.get("data", {}).get("extracted_variables", {})

        # Pull extracted variables (fallback to 'unknown')
        age = extracted.get("age", "unknown")
        insurance = extracted.get("insurance", "unknown")
        zip_code = extracted.get("zip_code", "unknown")
        income = extracted.get("income", "unknown")
        household_size = extracted.get("household_size", "unknown")
        willing_to_talk = extracted.get("Willing_to_talk", "unknown")
        life_change = extracted.get("life_change", "unknown")
        qualified = extracted.get("Qualified", "unknown")

        # Insert into Postgres
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO public.aca_responses (
                age, insurance, zip_code, income, household_size, willing_to_talk, life_change, qualified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (age, insurance, zip_code, income, household_size, willing_to_talk, life_change, qualified))
        conn.commit()
        cur.close()
        conn.close()

        return "Logged", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
