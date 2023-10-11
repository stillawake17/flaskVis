import json
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    with open('data/combined_flights_data.json', 'r') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    df['latestTime'] = pd.to_datetime(df['lastSeen'], unit='s')
    df["Hour"] = df["latestTime"].dt.hour
    df["Minute"] = df["latestTime"].dt.minute
    
    df["Time_Category"] = "Regular arrivals"
    df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"
    
    total_flights = len(df)
    shoulder_hour_flights = len(df[df['Time_Category'] == 'Shoulder hour flights'])
    night_hour_flights = len(df[df['Time_Category'] == 'Night hour arrivals'])
    
    categories = ['Total Flights', 'Shoulder Hour Flights', 'Night Hour Flights']
    counts = [total_flights, shoulder_hour_flights, night_hour_flights]

    return render_template("index.html", categories=categories, counts=counts)

if __name__ == "__main__":
    app.run(debug=True)
