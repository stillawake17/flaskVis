from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

app = Flask(__name__)

def load_and_process_data(selected_date):
    # Loading the dataset for arrivals
    df = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
    
    # Filter the data by the selected date
    df = df[df["LandedTime"].dt.date == pd.to_datetime(selected_date).date()]
    
    # Ensure the "LandedTime" column is in datetime format
    df["LandedTime"] = pd.to_datetime(df["LandedTime"], errors='coerce')

    # Extract the hour and minute information
    df["Hour"] = df["LandedTime"].dt.hour
    df["Minute"] = df["LandedTime"].dt.minute

    # Create a new column to categorize each flight by its time
    df["Time_Category"] = "Regular arrivals"
    df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

    # Drop rows where 'LandedTime' is NaN
    df.dropna(subset=['LandedTime'], inplace=True)

    # Find the date range and the time of the last flight in the dataset
    start_date_arr = df["LandedDate"].dt.date.min()
    end_date_arr = df["LandedDate"].dt.date.max()
    
    return df, start_date_arr, end_date_arr

def generate_plot(df, start_date_arr, end_date_arr):
    # Calculate the percentages for the entire dataset
    total_counts = df["Time_Category"].value_counts()
    total_percentages = (total_counts / total_counts.sum()) * 100

    # Filter for the latest day's data
    latest_day_data = df[df["LandedDate"].dt.date == end_date_arr]

    # Calculate the percentages for the latest day
    latest_day_counts = latest_day_data["Time_Category"].value_counts()
    latest_day_percentages = (latest_day_counts / latest_day_counts.sum()) * 100

    # Fill any missing categories with 0 for the latest day (to ensure consistent plotting)
    for category in total_counts.index:
        if category not in latest_day_percentages:
            latest_day_percentages[category] = 0.0

    # Ensure the order is consistent between total and latest day percentages
    total_percentages = total_percentages.reindex(latest_day_percentages.index)

    # Mapping colors to each category
    color_map = {
        "Shoulder hour flights": "yellow",
        "Night hour arrivals": "red",
        "Regular arrivals": "blue"
    }

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Outer Ring (Total Percentages)
    ax.pie(total_percentages, labels=total_percentages.index, autopct='%1.1f%%', startangle=140, 
           colors=[color_map[cat] for cat in total_percentages.index], wedgeprops=dict(width=0.3, edgecolor='w'))

    # Inner Ring (Latest Day Percentages)
    ax.pie(latest_day_percentages, labels=None, autopct='%1.1f%%', startangle=140,
           colors=[color_map[cat] for cat in latest_day_percentages.index], radius=0.7, wedgeprops=dict(width=0.3, edgecolor='w'))

    # Title
    ax.set_title(f"Bristol Airport - Percentage of Planes Landed by Category\nOuter: Total, Inner: {end_date_arr}")

    plt.tight_layout()
    
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
    if request.method == 'POST':
        selected_date = request.form['selected_date']
        df, start_date_arr, end_date_arr = load_and_process_data(selected_date)
        plot_url = generate_plot(df, start_date_arr, end_date_arr)
        
    return render_template('index.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
