# :airplane: flight-scraping
The goal of this project is to build a web application to scrap Sydney Airport's [flight listing pages](https://www.sydneyairport.com.au/flights/), and to display all of today's flights in a single HTML page.

## Table of Contents
**[Background](#Background)**<br>
**[Features of the completed web app](#Features-of-the-completed-web-app)**<br>
**[Built with](#Build-with)**<br>
**[Method](#Method)**<br>
**[How to use](#How-to-use)**<br>
**[Tricky bits and challenges](#Tricky-bits-and-challenges)**<br>
**[References](#References)**<br>

## Background
Sydney Airport's [flight listing page](https://www.sydneyairport.com.au/flights/) enables a user to choose between Arrivals or Departures, and between Domestic or International flights. However, this is no option to display all flights on a single page. For plane spotting purposes, it would be helpful to have a complete listing of the current day's flights in a single place.


## Features of the completed web app
- Dynamic loading screen while data is fetched
- Results page displays complete listing of today's flights at Sydney Airport. Icons are used to differentiate between arrivals and departures, and between domestic and international flights
- Data is refreshed every 15 minutes and synced to a PostgreSQL database
- Web application is [deployed to heroku](https://sydneyflights.herokuapp.com/)


## Built with
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Python library used to scrap HTML pages
- [Selenium](https://pypi.org/project/selenium/) [ChromeDriver](http://chromedriver.chromium.org/getting-started) - used to automate Chrome browser interaction from Python
- [Flask](https://flask.palletsprojects.com/en/1.0.x/) - Python framework used to build the web application
- [APScheduler](https://apscheduler.readthedocs.io/en/latest/) - Python library used to schedule automatic cron refreshes of the flight data
- [Heroku Postgres](https://www.heroku.com/postgres) - used to cache flight data


## Method
A brief description of the steps used to create the web app:

### 1. Web scraping
- Use [Selenium](https://pypi.org/project/selenium/) [ChromeDriver](http://chromedriver.chromium.org/getting-started) to grab HTML content from Sydney Airport's flight listing page. There are four possible combinations of domestic / international and arrival / departures, so there are four HTML pages to grab
- Use [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse the HTML content and pull out relevant information. For each flight, relevant info includes its origin / destination, stopover (if any), airline, flight number, status (arrived, departed, delayed, cancelled etc.), scheduled time, and estimated time
- Store parsed data in a Pandas dataframe. Each row corresponds to a single flight today.

### 2. Build Flask app
- Create [Flask](https://flask.palletsprojects.com/en/1.0.x/) app with two routes - one for loading screen while waiting for data to be fetched, and one to display the results table
- Use CSS templates to style the loading and result pages.

### 3. Connect to database
- Set up a SQLite database for local testing
- Write python function to store scraped data in the database table, and use [APScheduler](https://apscheduler.readthedocs.io/en/latest/) library to schedule automatic refreshes of the flight data
- Connect the `/results` route of the Flask app to fetch data from the database, instead of performing a fresh web scrap every time this endpoint is called.

### 4. Deploy to Heroku
- Define a `Procfile` to declare the command to be executed to start the app. [Gunicorn](https://gunicorn.org/) is used as the web server.
- Define a `requirements.txt` to specify the Python package dependencies on Heroku via pip
- Create a new Heroku app and set up the [PostgreSQL database add-on](https://www.heroku.com/postgres)
- Deploy by connecting to GitHub repository.


## How to use

### Local use
1. Uncomment the following lines of code in `main.py` to configure the SQLite database for local testing.
    ```python
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    ```

2. Navigate to the project root directory and run the following commands:
    ```console
    $ pip install -r requirements.txt
    $ python main.py
    ```
3. Open localhost `http://127.0.0.1:5000/`. You should see the webpage rendered.


### On the web
Go to [https://sydneyflights.herokuapp.com/](https://sydneyflights.herokuapp.com/).

## Tricky bits and challenges
### Scraping dynamic HTML pages
- Initially attempted to simply use the `get()` function from Python's `requests` library to grab HTML content from Sydney Airport's flight listing page
- This did not work - close examination of the scraped content showed that not all HTML from the web page was fetched. Specifically, the scraped content was missing the HTML tables for the individual flight listings
- This is because the airport's flight listings are not static HTML pages - rather the content is dynamically generated by JavaScript
- As a result, `webdriver.chrome()` from the `Selenium` library was needed to perform dynamic scraping.
 
### Truncated content in dataframe
- When using `pandas.DataFrame.to_html` to render the flights dataframe as an HTML table, some of the content (specifically URLs for the airline logos) was truncated.
- This resulted in the airline logos not displaying correctly in the table
- Interestingly, this issue only materialised when rendering the HTML table on a browser. There was no issue when rendering an identical table in Jupyter Notebook
- `pd.options.display.max_colwidth = 200` was used to adjust the display settings of the dataframe, and successfully fixed the issue.

### Running Chrome Driver on Heroku
- Configuring Chrome Driver to work on Heroku was challenging
- Chrome Driver was downloaded as an `.exe` file - this worked fine while testing locally, but posed problems when attempting to deploy to Heroku
- Successful solution, based on Andres Sevilla's [YouTube video](https://www.youtube.com/watch?v=Ven-pqwk3ec&fbclid=IwAR2zpRZK8rdvqgzsOPcwMZMzpp8N-hE6YlMcW-mQivaxy2u7iXmwCDe-Mcw):  
**1. Initialise instance of Chrome Driver:**
    ```python
    from selenium import webdriver
    import os

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    ```

    **2. Add the following buildpacks to the Heroku app:**
    - [https://github.com/heroku/heroku-buildpack-google-chrome](https://github.com/heroku/heroku-buildpack-google-chrome)
    - [https://github.com/heroku/heroku-buildpack-chromedriver](https://github.com/heroku/heroku-buildpack-chromedriver)
    
    Note: Buildpacks can be easily added by going to the **Settings** tab of the app on Heroku

    **3. Add the following config vars to the Heroku app:**
    - `CHROMEDRIVER_PATH = /app/.chromedriver/bin/chromedriver`
    - `GOOGLE_CHROME_BIN = /app/.apt/usr/bin/google-chrome`
    
    Note: Config vars can be easily edited by going to the **Settings** tab of the app on Heroku

### Heroku dyno sleeping
- This app uses a free web dyno on Heroku. The app [goes to sleep](https://devcenter.heroku.com/articles/free-dyno-hours#dyno-sleeping) if the dyno receives no web traffic in a 30-minute period
- This poses a problem for the database's scheduled updates - the data will not be updated unless the python code is running on a server
- To solve this, a function was added to ping the app every 20 minutes
- This ensures the database always contains up-to-date data, and users encounter minimal load times when opening the app.


### Heroku memory quotas
- Heroku has [memory restrictions](https://devcenter.heroku.com/articles/limits) (maximum 512 MB per app for a free web dyno), and exceeding this causes a "Memory quota exceeded" error
- This can sometimes prevent successful scraping and database updates
- Have experimented with reducing the frequency of scheduled database updates to circumvent the memory quota issue
- It appears the chromedriver used for web scraping causes an excessive memory load, and the problem cannot be completely solved unless upgrading to a paid Heroku tier.


## References

### Key tutorials
- [How to build a web application using Flask and deploy it to the cloud](https://www.freecodecamp.org/news/how-to-build-a-web-application-using-flask-and-deploy-it-to-the-cloud-3551c985e492/)
- [Tutorial: Web Scraping and BeautifulSoup](https://www.dataquest.io/blog/web-scraping-beautifulsoup/)

### Chrome Driver examples & trouble-shooting
- [chromedriver-heroku project by sonyasha](https://github.com/sonyasha/chromedriver-heroku)
- [Running ChromeDriver with Python Selenium on Heroku](https://www.youtube.com/watch?v=Ven-pqwk3ec&fbclid=IwAR2zpRZK8rdvqgzsOPcwMZMzpp8N-hE6YlMcW-mQivaxy2u7iXmwCDe-Mcw)

### Image sources
- [Airplane loading gif](https://www.pinterest.se/pin/261631059581218212/)
- [Favicon](https://www.flaticon.com/free-icon/travel_201623)
- [Earth icon](https://www.flaticon.com/free-icon/worldwide_814513)
- [Australia icon](https://www.flaticon.com/free-icon/australia_297029)