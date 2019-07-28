from flask import Flask, render_template
import pandas as pd
from flightscraper import flightscraper
from imgconverter import path_to_image_html

app = Flask(__name__)


@app.route("/")
def loading():
    return render_template("loading.html")

@app.route("/results")
def results():
    flights = flightscraper()
    pd.options.display.max_colwidth = 200
    return render_template("flights.html", tables=[flights.to_html(index=False, classes="flights", escape=False, formatters=dict(Type=path_to_image_html, Logo=path_to_image_html))], titles=['Sydney flights'])

if __name__ == "__main__":
    app.run(debug=True)
