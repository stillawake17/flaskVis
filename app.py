import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import datetime

# with open('C:\\Users\\josti\\OneDrive\\Desktop\\Gitlab clone\\OpenSky\\FlightData\\combined_flights_Data.json', 'r') as file:
    # data = json.load(file)

with open('data\combined_flights_data.json', 'r') as file:
    data = json.load(file)

df = pd.DataFrame(data)

# Your Unix timestamp
timestamp = 1691710959  

# Convert to a datetime object
dt_object = datetime.datetime.utcfromtimestamp(timestamp)

# Optionally convert to a string in a desired format
dt_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')

# Convert the 'lastSeen' column to datetime and create a new column 'latestTime'
df['latestTime'] = pd.to_datetime(df['lastSeen'], unit='s')

 # Convert LandedDate and LandedTime to a single datetime column
 # df["FullLandedTime"] = pd.to_datetime(df["LandedDate"].astype(str) + ' ' + df["latestTime"])

# Extract the hour and minute information
df["Hour"] = df["latestTime"].dt.hour
df["Minute"] = df["latestTime"].dt.minute

 # Categorize flights by time
df["Time_Category"] = "Regular arrivals"
df.loc[(df["Hour"] == 23) & (df["Minute"] < 30), "Time_Category"] = "Shoulder hour flights"
df.loc[(df["Hour"] == 23) & (df["Minute"] >= 30), "Time_Category"] = "Night hour arrivals"
df.loc[(df["Hour"] < 6), "Time_Category"] = "Night hour arrivals"
df.loc[(df["Hour"] == 6), "Time_Category"] = "Shoulder hour flights"

# Calculating counts
total_flights = len(df)
shoulder_hour_flights = len(df[df['Time_Category'] == 'Shoulder hour flights'])
night_hour_flights = len(df[df['Time_Category'] == 'Night hour arrivals'])

# Find the first and last date in the data
first_date = df['latestTime'].min().strftime('%Y-%m-%d')
last_date = df['latestTime'].max().strftime('%Y-%m-%d')

# Quotas
quotas = [85000, 3000, 4000]

# Actual counts
actual_counts = [total_flights, shoulder_hour_flights, night_hour_flights]

# Categories
categories = ['Total Flights', 'Shoulder Hour Flights', 'Night Hour Flights']

# Calculating percentages
percentages = [(count/quota)*100 for count, quota in zip(actual_counts, quotas)]

# Colors
colors = ['orange', 'green', 'yellow']

# Plotting
plt.figure(figsize=(10, 6))
bars = plt.barh(categories, percentages, color=colors)

# Adding labels
for bar, percentage in zip(bars, percentages):
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
             f'{percentage:.2f}%', 
             va='center', ha='left', fontsize=10, color='black')



# Labelling and showing the plot
plt.xlabel('Percentage (%)')
plt.ylabel('Category')
plt.title(f'Flight Counts as Percentage of Quotas by Category\nFrom {first_date} to {last_date}')
plt.xlim(0, 100)  # Optional: to limit x-axis to 100%
plt.show()