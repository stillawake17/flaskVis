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
    #df = pd.read_excel("/mnt/data/Arrivals_August.xlsx")
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

    # Load the entire dataset to calculate total percentages
    df_total = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
    
    #df_total = pd.read_excel("/mnt/data/Arrivals_August.xlsx")
    df_total["FullLandedTime"] = pd.to_datetime(df_total["LandedDate"].astype(str) + ' ' + df_total["LandedTime"])
    df_total["Hour"] = df_total["FullLandedTime"].dt.hour
    df_total["Minute"] = df_total["FullLandedTime"].dt.minute
    df_total["Time_Category"] = "Regular arrivals"
    df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
    df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
    df_total.loc[(df_total["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
    df_total.loc[(df_total["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

    # Calculate percentages for entire dataset
    total_counts = df_total["Time_Category"].value_counts()
    total_percentages = (total_counts / total_counts.sum()) * 100

    # Calculate percentages for specific date
    latest_day_counts = df["Time_Category"].value_counts()
    latest_day_percentages = (latest_day_counts / latest_day_counts.sum()) * 100
    for category in total_counts.index:
        if category not in latest_day_percentages:
            latest_day_percentages[category] = 0.0
    total_percentages = total_percentages.reindex(latest_day_percentages.index)

    color_map = {
        "Shoulder hour flights": "yellow",
        "Night hour arrivals": "red",
        "Regular arrivals": "blue"
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(total_percentages, labels=total_percentages.index, autopct='%1.1f%%', startangle=140, 
           colors=[color_map[cat] for cat in total_percentages.index], wedgeprops=dict(width=0.3, edgecolor='w'))
    ax.pie(latest_day_percentages, labels=None, autopct='%1.1f%%', startangle=140,
           colors=[color_map[cat] for cat in latest_day_percentages.index], radius=0.7, wedgeprops=dict(width=0.3, edgecolor='w'))
    ax.set_title(f"Bristol Airport - Percentage of Planes Landed by Category\\nOuter: Total, Inner: {end_date_arr}")
    plt.tight_layout()

    logging.info("Plot generated, converting to PNG image...")
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
    summary = None

    if request.method == 'POST':
        selected_date = request.form['selected_date']
        df, start_date_arr, end_date_arr = load_and_process_data(selected_date)
        if df.empty:
            message = f"No data found for the selected date: {selected_date}"
        else:
            plot_url = generate_plot(df, start_date_arr, end_date_arr)

             # Load the entire dataset to calculate total percentages
            df_total = pd.read_excel("C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx")
            df_total["FullLandedTime"] = pd.to_datetime(df_total["LandedDate"].astype(str) + ' ' + df_total["LandedTime"])
            df_total["Hour"] = df_total["FullLandedTime"].dt.hour
            df_total["Minute"] = df_total["FullLandedTime"].dt.minute
            df_total["Time_Category"] = "Regular arrivals"
            df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
            df_total.loc[(df_total["Hour"] == 23) & (df_total["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
            df_total.loc[(df_total["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
            df_total.loc[(df_total["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

            # Calculate total percentages
            total_counts = df_total["Time_Category"].value_counts()
            total_percentages = ((total_counts / total_counts.sum()) * 100).round(1)

            # Calculate day percentages
            day_counts = df["Time_Category"].value_counts()
            day_percentages = ((day_counts / day_counts.sum()) * 100).round(1)

            # Create summary table
            summary_df = pd.DataFrame({'Number of Flights (Day)': day_counts, 'Percentage (Day) %': day_percentages,
                                       'Number of Flights (Total)': total_counts, 'Percentage (Total) %': total_percentages})

            # Add total row
            total_day_flights = day_counts.sum()
            total_all_flights = total_counts.sum()
            summary_df.loc['Total'] = [total_day_flights, 100, total_all_flights, 100]  # 100% since it's the total

            # Convert to HTML for rendering
            summary = summary_df.to_html(classes='summary-table')

    return render_template('index.html', plot_url=plot_url, message=message, summary=summary)


if __name__ == '__main__':
    app.run(debug=True)
