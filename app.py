
from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection info from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT", "5432")

def insert_into_db(data):
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO public.aca_responses (
            conversation_id,
            first_name,
            phone_number,
            age,
            insurance,
            zip_code,
            income,
            household_size,
            willing_to_talk,
            life_change,
            qualified
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            data.get("conversation_id"),
            data.get("first_name"),
            data.get("phone_number"),
            data.get("age"),
            data.get("insurance"),
            data.get("zip_code"),
            data.get("income"),
            data.get("household_size"),
            data.get("willing_to_talk"),
            data.get("life_change"),
            data.get("qualified")
        )
    )
    conn.commit()
    cur.close()
    conn.close()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        extracted_vars = payload.get("data", {}).get("metadata", {})

        data_to_store = {
            "conversation_id": payload.get("data", {}).get("conversation_id"),
            "first_name": extracted_vars.get("first_name"),
            "phone_number": extracted_vars.get("phone_number"),
            "age": extracted_vars.get("age"),
            "insurance": extracted_vars.get("insurance"),
            "zip_code": extracted_vars.get("zip_code"),
            "income": extracted_vars.get("income"),
            "household_size": extracted_vars.get("household_size"),
            "willing_to_talk": extracted_vars.get("willing_to_talk"),
            "life_change": extracted_vars.get("life_change"),
            "qualified": extracted_vars.get("qualified")
        }

        insert_into_db(data_to_store)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
