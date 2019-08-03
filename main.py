from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
import pandas as pd
from flightscraper import flightscraper
from imgconverter import path_to_image_html

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    flight_type = db.Column(db.String())
    journey = db.Column(db.String())
    stopover = db.Column(db.String())
    airline = db.Column(db.String())
    airline_logo = db.Column(db.String())
    flight_number = db.Column(db.String())
    status = db.Column(db.String())
    scheduled_time = db.Column(db.String())
    estimated_time = db.Column(db.String())

    def __init__(self, flight_type, journey, stopover, airline, airline_logo, flight_number, status, scheduled_time, estimated_time):
        self.flight_type = flight_type
        self.journey = journey
        self.stopover = stopover
        self.airline = airline
        self.airline_logo = airline_logo
        self.flight_number = flight_number
        self.status = status
        self.scheduled_time = scheduled_time
        self.estimated_time = estimated_time

    def __repr__(self):
        return '<flight number {}>'.format(self.flight_number)

    def serialise(self):
        return {
            'id': self.id,
            'flight_type': self.flight_type,
            'journey': self.journey,
            'stopover': self.stopover,
            'airline': self.airline,
            'airline_logo': self.airline_logo,
            'flight_number': self.flight_number,
            'status': self.status,
            'scheduled_time': self.scheduled_time,
            'estimated_time': self.estimated_time
        }


@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/refreshdata")
def refresh_data():
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
                estimated_time=flights["Estimated time"][i]
            )

            db.session.add(flight)
            db.session.commit()
            return "Flight added, flight number={}".format(flight.flight_number)
        
        except Exception as e:
            return(str(e))

@app.route("/results")
def results():
    flights = flightscraper(returnDataFrame=True)
    pd.options.display.max_colwidth = 200
    return render_template("flights.html", tables=[flights.to_html(index=False, classes="flights", escape=False, formatters=dict(Type=path_to_image_html, Logo=path_to_image_html))], titles=['Sydney flights'])

if __name__ == "__main__":
    app.run(debug=True)
