from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

# ... (Any additional imports and functions like to_rgb, to_hex, lighten_color, etc.)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DATA_PATH = "C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx"

def load_and_process_data(selected_date, filter_type='total'):
    logging.info(f"Selected date: {selected_date}")
    
    # ... (Code for loading and processing data)
    
    if filter_type == 'monthly':
        df = df[df["FullLandedTime"].dt.month == pd.to_datetime(selected_date).month]
    elif filter_type == 'weekly':
        df = df[(df["FullLandedTime"].dt.isocalendar().week == pd.to_datetime(selected_date).isocalendar().week) 
                & (df["FullLandedTime"].dt.year == pd.to_datetime(selected_date).year)]
    # No filtering condition needed for 'total' as it uses all data
    
    # ... (Additional processing if needed)

    return df

def generate_plot(df):
    logging.info("Generating plot...")

    # Count the categories
    counts = df["Time_Category"].value_counts()

    # Bar chart
    img = io.BytesIO()
    plt.bar(counts.index, counts.values, color=['blue', 'red', 'yellow'])
    plt.xlabel('Flight Category')
    plt.ylabel('Number of Flights')
    plt.title('Number of Flights per Category')

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    message = None
    summary = None
    night_hour_percentage = 0

    if request.method == 'POST':
        selected_date = request.form['selected_date']
        filter_type = request.form.get('filter_type', 'total')  # Retrieve filtering type

        df = load_and_process_data(selected_date, filter_type)
        
        if df.empty:
            message = f"No data found for the selected date: {selected_date} and filter: {filter_type}"
        else:
            plot_url = generate_plot(df)
            
            # ... (Additional code for summary, percentages, etc.)

    return render_template('index.html', plot_url=plot_url, message=message, summary=summary, night_hour_percentage=night_hour_percentage)

if __name__ == '__main__':
    app.run(debug=True)
