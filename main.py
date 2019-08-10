from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from flightscraper2 import flightscraper2
from imgconverter import path_to_image_html
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import time
from datetime import datetime
from requests import get

# Set up Flask app
app = Flask(__name__)
# Uncomment below lines for local testing using SQLite database
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

# Initialise instance of Chrome driver
chrome_options = webdriver.ChromeOptions()
if (os.environ.get("GOOGLE_CHROME_BIN") is None) | (os.environ.get("CHROMEDRIVER_PATH") is None):
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
else:
   chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
   chrome_options.add_argument("--headless")
   chrome_options.add_argument("--disable-dev-shm-usage")
   chrome_options.add_argument("--no-sandbox")
   driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

# Define Flight table schema
class Flight(db.Model):
    __tablename__ = 'flights'

    flight_type = db.Column(db.String(), primary_key=True)
    journey = db.Column(db.String())
    stopover = db.Column(db.String())
    airline = db.Column(db.String())
    airline_logo = db.Column(db.String())
    flight_number = db.Column(db.String(), primary_key=True)
    status = db.Column(db.String())
    scheduled_time = db.Column(db.String())
    estimated_time = db.Column(db.String())
    time_modified = db.Column(db.String())

    def __init__(self, flight_type, journey, stopover, airline, airline_logo, flight_number, status, scheduled_time, estimated_time, time_modified):
        self.flight_type = flight_type
        self.journey = journey
        self.stopover = stopover
        self.airline = airline
        self.airline_logo = airline_logo
        self.flight_number = flight_number
        self.status = status
        self.scheduled_time = scheduled_time
        self.estimated_time = estimated_time
        self.time_modified = time_modified

    def __repr__(self):
        return '<flight number {}>'.format(self.flight_number)

    def serialise(self):
        return {
            'flight_type': self.flight_type,
            'journey': self.journey,
            'stopover': self.stopover,
            'airline': self.airline,
            'airline_logo': self.airline_logo,
            'flight_number': self.flight_number,
            'status': self.status,
            'scheduled_time': self.scheduled_time,
            'estimated_time': self.estimated_time,
            'time_modified': self.time_modified
        }

# Function to refresh flight data - this will be run on cron schedule
def refresh_flights(terminal, journey):
    # Get new data
    flights = flightscraper2(terminal=terminal, journey=journey, driver=driver)
    
    # Check if returned data is not empty
    if len(flights['Type']) > 0:
        # Delete rows in table corresponding to terminal and journey type
        flight_type_str = 'static/images/{}_{}.png'.format(terminal, journey)
        Flight.query.filter(Flight.flight_type==flight_type_str).delete()
        db.session.commit()

        # Save new data in database
        for i in range(0, len(flights["Type"])):
            try:
                flight = Flight(
                    flight_type=flights["Type"][i],
                    journey=flights["Journey"][i],
                    stopover=flights["Stopover"][i],
                    airline=flights["Airline"][i],
                    airline_logo=flights["Logo"][i],
                    flight_number=flights["Flight number"][i],
                    status=flights["Status"][i],
                    scheduled_time=flights["Scheduled time"][i],
                    estimated_time=flights["Estimated time"][i],
                    time_modified=str(datetime.now())
                )

                db.session.add(flight)
                db.session.commit()
                print("Flight added, flight number={}".format(flight.flight_number))
            
            except Exception as e:
                print(str(e))

# Function to ping Heroku app every 20 minutes so it doesn't go to sleep
def ping_app():
    url = "https://sydneyflights.herokuapp.com/"
    get(url)


# Set up cron schedules to refresh data
# schedules = ["0",
#              "15",
#              "30",
#              "45",
#              "20, 40, 59"]

schedules = ["0, 12, 24, 36, 48",
             "3, 15, 27, 39, 51",
             "6, 18, 30, 42, 54",
             "9, 21, 33, 45, 57",
             "1, 22, 43"]
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(refresh_flights, "cron", args=["international", "arrival"], minute=schedules[0])
scheduler.add_job(refresh_flights, "cron", args=["international", "departure"], minute=schedules[1])
scheduler.add_job(refresh_flights, "cron", args=["domestic", "arrival"], minute=schedules[2])
scheduler.add_job(refresh_flights, "cron", args=["domestic", "departure"], minute=schedules[3])
scheduler.add_job(ping_app, "cron", minute=schedules[4])

atexit.register(lambda: scheduler.shutdown())

# Define app routes
@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/results")
def newresults():
    flights = pd.read_sql(Flight.query.statement, db.session.bind)
    flights.rename(columns={
        "flight_type": "Type", 
        "journey": "Journey",
        "stopover": "Stopover",
        "airline": "Airline",
        "airline_logo": "Logo",
        "flight_number": "Flight number",
        "status": "Status",
        "scheduled_time": "Scheduled time",
        "estimated_time": "Estimated time",
        "time_modified": "Time Modified"}, inplace=True)
    
    flights.drop(columns=["Time Modified"], inplace=True)
    flights.sort_values(by=['Scheduled time'], inplace=True)

    pd.options.display.max_colwidth = 200
    return render_template("flights.html", tables=[flights.to_html(index=False, classes="flights", escape=False, formatters=dict(Type=path_to_image_html, Logo=path_to_image_html))], titles=['Sydney flights'])

if __name__ == "__main__":
    app.run(debug=True)
