from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def load_and_process_data(selected_date):
    logging.info(f"Selected date: {selected_date}")

    # Loading the dataset for arrivals
    df = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
    
    # Convert LandedDate and LandedTime to a single datetime column
    df["FullLandedTime"] = pd.to_datetime(df["LandedDate"].astype(str) + ' ' + df["LandedTime"])

    # Filter the data by the selected date
    df = df[df["FullLandedTime"].dt.date == pd.to_datetime(selected_date).date()]
    logging.info(f"Data shape after filtering by selected date: {df.shape}")

    # Extract the hour and minute information
    df["Hour"] = df["FullLandedTime"].dt.hour
    df["Minute"] = df["FullLandedTime"].dt.minute

    # Categorize flights by time
    df["Time_Category"] = "Regular arrivals"
    df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

    start_date_arr = df["FullLandedTime"].dt.date.min()
    end_date_arr = df["FullLandedTime"].dt.date.max()
    logging.info(f"Start Date: {start_date_arr}, End Date: {end_date_arr}")

    return df, start_date_arr, end_date_arr

def generate_plot(df, start_date_arr, end_date_arr):
    logging.info("Generating plot...")

    # Generate a simple bar plot based on the flight categories for the selected date
    plt.figure(figsize=(10, 6))
    day_counts = df["Time_Category"].value_counts()
    day_counts.plot(kind='bar', color='c')
    plt.title(f"Flight Categories for {start_date_arr} to {end_date_arr}")
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

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    message = None
    summary = None

    if request.method == 'POST':
        selected_date = request.form['selected_date']
        df, start_date_arr, end_date_arr = load_and_process_data(selected_date)
        if df.empty:
            message = f"No data found for the selected date: {selected_date}"
        else:
            plot_url = generate_plot(df, start_date_arr, end_date_arr)

            df_total = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
            df_total["FullLandedTime"] = pd.to_datetime(df_total["LandedDate"].astype(str) + ' ' + df_total["LandedTime"])
            df_total["Hour"] = df_total["FullLandedTime"].dt.hour
            df_total["Minute"] = df_total["FullLandedTime"].dt.minute
            df_total["Time_Category"] = "Regular arrivals"
            df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
            df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
            df_total.loc[(df_total["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
            df_total.loc[(df_total["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

            # Calculate the percentage of night hour flights used up from the quota
            night_hour_flights_count = df_total[df_total["Time_Category"] == "Night hour arrivals"].shape[0]
            percentage_used = (night_hour_flights_count / 4000) * 100
            # Determine the image filename based on the percentage
            rounded_percentage = 5 * round(percentage_used / 5)
            image_filename = f"image_{rounded_percentage}.png"

            # Create summary table for the rendered template
            total_counts = df_total["Time_Category"].value_counts()
            total_percentages = ((total_counts / total_counts.sum()) * 100).round(1)
            day_counts = df["Time_Category"].value_counts()
            day_percentages = ((day_counts / day_counts.sum()) * 100).round(1)
            summary_df = pd.DataFrame({'Number of Flights (Day)': day_counts, 'Percentage (Day) %': day_percentages,
                                       'Number of Flights (Total)': total_counts, 'Percentage (Total) %': total_percentages})
            summary_df.loc['Total'] = [day_counts.sum(), 100, total_counts.sum(), 100]
            summary = summary_df.to_html(classes='summary-table')

    return render_template('index.html', plot_url=plot_url, message=message, summary=summary, image_filename=image_filename)

if __name__ == '__main__':
    app.run(debug=True)
