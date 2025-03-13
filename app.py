import os
import time
import requests
import threading
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Thread-safe global variables
data_lock = threading.Lock()
location_data = []  # List of location_uid integers
api_data = {}  # Full API response

API_TOKEN = os.getenv("API_TOKEN")
EXTERNAL_API_URL = f"https://api.alerts.in.ua/v1/alerts/active.json?token={API_TOKEN}"


def update_data():
    """Continuously fetch data from an external API every 8 seconds."""
    global location_data, api_data
    session = requests.Session()
    while True:
        try:
            response = session.get(EXTERNAL_API_URL, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            json_data = response.json()
            alerts = json_data.get('alerts', [])
            location_ids = []
            for alert in alerts:
                try:
                    # Safely convert location_uid to an integer
                    location_ids.append(int(alert.get('location_uid', 0)))
                except (ValueError, TypeError):
                    logging.warning("Invalid location_uid encountered: %s", alert.get('location_uid'))

            with data_lock:
                location_data = location_ids
                api_data = json_data

            logging.info("Data updated: %s", location_data)

        except requests.RequestException as e:
            logging.error("Request error: %s", e)
            with data_lock:
                location_data = {"error": "Failed to fetch data", "details": str(e)}
        except Exception as e:
            logging.error("Unexpected error: %s", e)
            with data_lock:
                location_data = {"error": str(e)}
        time.sleep(8)


@app.route('/data', methods=['GET'])
def get_data():
    """API endpoint to retrieve the latest location data."""
    with data_lock:
        return jsonify(location_data)


@app.route('/api-data', methods=['GET'])
def get_api_data():
    """API endpoint to retrieve the full API response."""
    with data_lock:
        return jsonify(api_data)


if __name__ == "__main__":
    # Start update_data in a daemon thread
    threading.Thread(target=update_data, daemon=True).start()
    # Disable the reloader to avoid duplicate thread execution
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
