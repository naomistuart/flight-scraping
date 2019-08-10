from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
import pandas as pd
from flightscraper2 import flightscraper2
from imgconverter import path_to_image_html
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import time
from datetime import datetime

# Set up Flask app
app = Flask(__name__)
# Uncomment below lines for local testing using SQLite database
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

# Define Flight table schema
class Flight(db.Model):
    __tablename__ = 'flights'

    #id = db.Column(db.Integer, primary_key=True)
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
    # Delete rows in table corresponding to terminal and journey type
    flight_type_str = 'static/images/{}_{}.png'.format(terminal, journey)
    Flight.query.filter(Flight.flight_type==flight_type_str).delete()
    db.session.commit()

    # Get new data
    flights = flightscraper2(terminal=terminal, journey=journey)

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


# Set up cron schedules to refresh data
schedules = ["0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55",
             "1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56",
             "2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57",
             "3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58"]
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(refresh_flights, "cron", args=["international", "arrival"], minute=schedules[0])
scheduler.add_job(refresh_flights, "cron", args=["international", "departure"], minute=schedules[1])
scheduler.add_job(refresh_flights, "cron", args=["domestic", "arrival"], minute=schedules[2])
scheduler.add_job(refresh_flights, "cron", args=["domestic", "departure"], minute=schedules[3])

atexit.register(lambda: scheduler.shutdown())

# Define app routes
@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/refreshdata")
def refresh_data():
    num_rows_deleted = Flight.query.delete()
    db.session.commit()
    print("deleted {} rows".format(num_rows_deleted))
    
    flights = flightscraper(returnDataFrame=False)
    
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
    
    return "END OF DATA LOAD"

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
    flights.sort_values(by=['Scheduled time'], inplace=True)

    pd.options.display.max_colwidth = 200
    return render_template("flights.html", tables=[flights.to_html(index=False, classes="flights", escape=False, formatters=dict(Type=path_to_image_html, Logo=path_to_image_html))], titles=['Sydney flights'])

if __name__ == "__main__":
    app.run(debug=True)
