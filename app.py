import os
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

data = []

api_data = []

API_TOKEN = os.getenv("API_TOKEN")

def update_data():
    """Continuously fetch data from an external API every 8 seconds."""
    global data, api_data
    external_api_url = f"https://api.alerts.in.ua/v1/alerts/active.json?token={API_TOKEN}"  # Replace with your API URL
    while True:
        try:
            response = requests.get(external_api_url)
            if response.status_code == 200:
                api_data = response.json()
                raw_data = response.json()['alerts']
                arr = []
                for alert in raw_data:
                    arr.append(int(alert['location_uid']))
                data = arr
            else:
                data = {
                    "error": "Failed to fetch data",
                    "status": response.status_code
                }
        except Exception as e:
            data = {"error": str(e)}
        time.sleep(8)


@app.route('/data', methods=['GET'])
def get_data():
    """API endpoint to retrieve the latest data."""
    return jsonify(data)

@app.route('/api-data', methods=['GET'])
def get_api_data():
    return jsonify(api_data)

