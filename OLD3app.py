from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def load_and_process_data(selected_date):
    logging.info(f"Selected date: {selected_date}")
    
    df = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
    df["LandedTime"] = pd.to_datetime(df["LandedTime"], format='%H:%M', errors='coerce')
    
    df = df[df["LandedTime"].dt.date == pd.to_datetime(selected_date).date()]
    logging.info(f"Data shape after filtering by selected date: {df.shape}")
    
    df["Hour"] = df["LandedTime"].dt.hour
    df["Minute"] = df["LandedTime"].dt.minute

    df["Time_Category"] = "Regular arrivals"
    df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

    df.dropna(subset=['LandedTime'], inplace=True)
    
    start_date_arr = df["LandedDate"].dt.date.min() if not df.empty else None
    end_date_arr = df["LandedDate"].dt.date.max() if not df.empty else None
    logging.info(f"Start Date: {start_date_arr}, End Date: {end_date_arr}")
    
    return df, start_date_arr, end_date_arr

def generate_plot(df, start_date_arr, end_date_arr):
    # Rest of plotting code (unchanged for brevity)
    
    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    message = None
    if request.method == 'POST':
        selected_date = request.form['selected_date']
        df, start_date_arr, end_date_arr = load_and_process_data(selected_date)
        if df.empty:
            message = f"No data found for the selected date: {selected_date}"
        else:
            plot_url = generate_plot(df, start_date_arr, end_date_arr)
        
    return render_template('index.html', plot_url=plot_url, message=message)

if __name__ == '__main__':
    app.run(debug=True)
