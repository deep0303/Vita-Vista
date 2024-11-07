from flask import Flask, render_template
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import os

app = Flask(__name__)

# Sample data similar to your JSON input
data = {
    "days": ["2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06", "2024-10-07"],
    "calories": [2100, 1800, 2000, 2200, 1900, 2300, 2100],
    "heartrate": [72, 75, 80, 78, 77, 76, 74],
    "steps": [8000, 7500, 8200, 9000, 7000, 8500, 8800],
    "sleep": [7, 8, 6.5, 7.5, 6, 8, 7]
}

# Helper function to load the data
def load_data():
    return data

# Function to generate and save charts
def generate_charts():
    data = load_data()

    # Convert 'days' to datetime objects
    dates = [datetime.strptime(day, '%Y-%m-%d') for day in data['days']]
    calories = data['calories']
    heart_rate = data['heartrate']
    steps = data['steps']
    sleep = data['sleep']

    # Create a bar chart for calories
    plt.figure(figsize=(6, 4))
    plt.bar(dates, calories, color='#1f77b4', edgecolor='black')
    plt.title('Calories by Date', fontsize=14, fontweight='bold')
    plt.ylabel('Calories', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/calories_chart.png')

    # Create a scatter plot for heart rate
    plt.figure(figsize=(6, 4))
    plt.scatter(dates, heart_rate, color='#d62728', s=100, edgecolor='black', alpha=0.8)
    plt.title('Heart Rate by Date', fontsize=14, fontweight='bold')
    plt.ylabel('Heart Rate (BPM)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/heart_rate_chart.png')

    # Create an area chart for steps
    plt.figure(figsize=(6, 4))
    plt.fill_between(dates, steps, color='#2ca02c', alpha=0.6)
    plt.plot(dates, steps, marker='o', color='green', linewidth=2, markersize=8, markerfacecolor='white')
    plt.title('Steps Taken Over Time', fontsize=14, fontweight='bold')
    plt.ylabel('Steps', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/steps_chart.png')

    # Create a pie chart for the sleep data distribution
    # Create a line plot for sleep data
    plt.figure(figsize=(6, 4))
    plt.plot(dates, sleep, marker='o', color='#ff9999', linewidth=2, markersize=8, markerfacecolor='black')
    plt.title('Sleep Over Time', fontsize=14, fontweight='bold')
    plt.ylabel('Sleep (hours)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/sleep_line_chart.png')


@app.route('/')
def dashboard():
    # Generate charts
    generate_charts()

    # Load data
    data = load_data()

    # Calculate average values
    avg_sleep = round(sum(data['sleep']) / len(data['sleep']), 2)
    avg_calories = round(sum(data['calories']) / len(data['calories']), 2)
    avg_heart_rate = round(sum(data['heartrate']) / len(data['heartrate']), 2)

    return render_template('dashboard.html', avg_sleep=avg_sleep, avg_calories=avg_calories, avg_heart_rate=avg_heart_rate)

if __name__ == "__main__":
    app.run(debug=True)
