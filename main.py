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

from models import Flight

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
