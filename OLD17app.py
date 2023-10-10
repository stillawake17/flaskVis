from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def load_and_process_data():
    # Loading the dataset for arrivals
    df = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
    
    # Convert LandedDate and LandedTime to a single datetime column
    df["FullLandedTime"] = pd.to_datetime(df["LandedDate"].astype(str) + ' ' + df["LandedTime"])

    # Extract the hour and minute information
    df["Hour"] = df["FullLandedTime"].dt.hour
    df["Minute"] = df["FullLandedTime"].dt.minute

    # Categorize flights by time
    df["Time_Category"] = "Regular arrivals"
    df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

    return df

def generate_plot(df):
    logging.info("Generating plot...")

    # Generate a simple bar plot based on the flight categories for the selected date
    plt.figure(figsize=(10, 6))
    counts = df["Time_Category"].value_counts()
    counts.plot(kind='bar', color='c')
    plt.title("Flight Categories")
    plt.ylabel('Number of Flights')
    plt.xlabel('Time Category')
    plt.tight_layout()

    # Convert the plot to a PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image to base64 to display it in the HTML template
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

@app.route('/', methods=['GET'])
def index():
    df = load_and_process_data()
    plot_url = generate_plot(df)
    return render_template('index.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
