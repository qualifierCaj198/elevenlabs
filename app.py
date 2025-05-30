from flask import Flask, request
import psycopg2
import os

app = Flask(__name__)

DB_URL = os.environ.get("DATABASE_URL", "postgresql://elevenlabs_user:jFvClHh7MW3SWqlT3HvJSsiZlr9FMYYJ@dpg-d0st7cc9c44c73fgv7pg-a.oregon-postgres.render.com/elevenlabs")

@app.route("/webhook", methods=["POST"])  # <-- updated path
def handle_webhook():
    try:
        data = request.get_json()
        print("Received data:", data)

        extracted = data.get("data", {}).get("analysis", {}).get("extracted_variables", {})

        age = extracted.get("age")
        insurance = extracted.get("insurance")
        zip_code = extracted.get("zip_code")
        income = extracted.get("income")
        household_size = extracted.get("household_size")
        willing_to_talk = extracted.get("Willing_to_talk")
        life_change = extracted.get("life_change")
        qualified = extracted.get("Qualified")

        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO public.aca_responses (
                age, insurance, zip_code, income, household_size, willing_to_talk, life_change, qualified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (age, insurance, zip_code, income, household_size, willing_to_talk, life_change, qualified)
        )
        conn.commit()
        cur.close()
        conn.close()

        return "OK", 200
    except Exception as e:
        print("Error:", str(e))
        return "Error", 500

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
