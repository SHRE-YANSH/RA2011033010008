from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_URL = "http://20.244.56.144/train/trains"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTI3MTAyODIsImNvbXBhbnlOYW1lIjoiVHJhaW4gQ2VudHJhbCIsImNsaWVudElEIjoiZjgxZDQ3ZWQtODZjMS00NzkxLWIyYjUtZTZhZjZkMjg1NmVkIiwib3duZXJOYW1lIjoiIiwib3duZXJFbWFpbCI6IiIsInJvbGxObyI6IlJBMjAxMTAzMzAxMDAwOCJ9.oe-mgkpE_xyvgLSKjsCFcPTP7LxgeD4zSrQtMTNhtCg"# Replace with the actual base URL

@app.route('/trains', methods=['GET'])
def get_trains():
    now = datetime.now()
    next_12_hours = now + timedelta(hours=12)
    payload = {
    "start_time": now.strftime("%Y-%m-%dT%H:%M:%S"),
    "end_time": next_12_hours.strftime("%Y-%m-%dT%H:%M:%S")
}
    headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}"
        }


    response = requests.get(f"{BASE_URL}/trains", params=payload, headers=headers)

    if response.status_code == 200:
        trains = response.json()



        
        filtered_trains = []
        for train in trains:
            departure_time_hours = train['departureTime']['Hours']
            departure_time_minutes = train['departureTime']['Minutes']
            departure_time = now.replace(hour=departure_time_hours, minute=departure_time_minutes, second=0, microsecond=0)
            
            if departure_time > now + timedelta(minutes=30):
                train_entry = {
                    "trainNumber": train['trainNumber'],
                    "trainName": train['trainName'],
                    "departureTime": departure_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "seatsAvailable": {
                        "sleeper": train['seatsAvailable']['sleeper'],
                        "AC": train['seatsAvailable']['AC']
                    },
                    "price": {
                        "sleeper": train['price']['sleeper'],
                        "AC": train['price']['AC']
                    }
                }
                filtered_trains.append(train_entry)

        sorted_trains = sorted(
            filtered_trains,
            key=lambda train: (train['price']['AC'], -train['seatsAvailable']['AC'], train['departureTime']),
            reverse=True
        )

        return jsonify(sorted_trains)

    return jsonify({"message": "Error fetching train data"}), response.status_code



if __name__ == '__main__':
    app.run(debug=True)
