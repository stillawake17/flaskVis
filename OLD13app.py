from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

DATA_PATH = "C:/Users/josti/OneDrive/Documents/01 - Joanna/Local council/0000 - Bristol Airport/Arrivals_August.xlsx"

def to_rgb(color):
    "Convert a hex color string to an RGB tuple."
    color = color.lstrip('#')
    return tuple(int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def to_hex(rgb):
    "Convert an RGB tuple to a hex color string."
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def lighten_color(color, factor=0.5):
    r, g, b = to_rgb(color)
    r = min(1, r + (1 - r) * factor)
    g = min(1, g + (1 - g) * factor)
    b = min(1, b + (1 - b) * factor)
    return to_hex((r, g, b))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def load_and_process_data(selected_date):
    logging.info(f"Selected date: {selected_date}")

    # Loading the dataset for arrivals
    df = pd.read_excel(DATA_PATH)
    
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

def generate_progress_bars_v3(actual_values, quotas, categories, active_color, muted_color):
    "Generate a plot with progress bars for given actual values, quotas, and categories."
    img = io.BytesIO()
    plt.bar(categories, actual_values, color=active_color, label="Actual Values")
    plt.bar(categories, quotas, color=muted_color, label="Quotas", bottom=actual_values)
    plt.legend()
    plt.savefig(img, format='png')
    img.seek(0)
    return img

def generate_plot(df, start_date_arr, end_date_arr):
    logging.info("Generating plot...")

    # Load the entire dataset to calculate total percentages
    df_total = pd.read_excel(DATA_PATH)
    
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

    # The rest of the code for this function seems to be missing or was truncated in the provided input.
    # It might need to be added back in later.

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    message = None
    summary = None
    night_hour_percentage = 0
    allowed_quota = 4000
    image_filename = 'default_image.png'

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


    return render_template('index.html', plot_url=plot_url, message=message, summary=summary, night_hour_percentage=night_hour_percentage, image_filename=image_filename)

if __name__ == '__main__':
    app.run(debug=True)