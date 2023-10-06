from flask import Flask, render_template, request
import io
import base64
import pandas as pd
import logging
import matplotlib as mpl
mpl.use('Agg')  # Ensure using the 'Agg' backend for matplotlib
from matplotlib.figure import Figure

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DATA_PATH = "C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx"

def load_and_process_data(filter_type='total'):
    logging.info(f"Filter type: {filter_type}")

    df = pd.DataFrame()
    try:
        df = pd.read_excel(DATA_PATH)
        df["FullLandedTime"] = pd.to_datetime(df["LandedDate"].astype(str) + ' ' + df["LandedTime"].astype(str).str.split('.').str[0])  # Ensure LandedTime is string and remove .0
        original_size = len(df)

        if filter_type == 'monthly':
            df = df[df["FullLandedTime"].dt.month == df["FullLandedTime"].dt.month.max()]
        elif filter_type == 'weekly':
            df = df[df["FullLandedTime"].dt.isocalendar().week == df["FullLandedTime"].dt.isocalendar().week.max()]

        df["Hour"] = df["FullLandedTime"].dt.hour
        df["Minute"] = df["FullLandedTime"].dt.minute

        df["Time_Category"] = "Regular arrivals"
        df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
        df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
        df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
        df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

        logging.info(f"Original data size: {original_size}, Filtered data size: {len(df)}")
        logging.info(f"Head of Filtered Data: \n{df.head()}")

    except Exception as e:
        logging.error(f"Error loading or processing data: {str(e)}")
    
    logging.info(f"Returning from load_and_process_data, df is None: {df is None}, df.empty: {df.empty if df is not None else 'df is None'}")
    
    return df

def generate_plot(df, filter_type):
    logging.info("Generating plot...")
    counts = df["Time_Category"].value_counts()

    logging.info(f"Counts before plotting: {counts}")
    logging.info(f"Data after categorization: \n{df.head()}")
    df.to_csv("debug_data.csv", index=False)


    fig = Figure()
    ax = fig.subplots()
    ax.bar(counts.index, counts.values, color=['blue', 'red', 'yellow'])
    ax.set_xlabel('Flight Category')
    ax.set_ylabel('Number of Flights')
    ax.set_title(f'Number of Flights per Category - Filter: {filter_type}')

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    logging.info(f"Plot URL: {plot_url}")

    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    message = None
    summary = None

    filter_type = request.args.get('filter_type', 'total')  

    df = load_and_process_data(filter_type)
        
    if df is None or df.empty:
        message = f"No data found for the filter: {filter_type}"
    else:
        plot_url = generate_plot(df, filter_type)

    return render_template('index.html', plot_url=plot_url, message=message, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
