def flightscraper2(terminal, journey, driver):

    from datetime import datetime
    from bs4 import BeautifulSoup
    import numpy as np
    import pandas as pd
    import os
    import time

    # Define query strings for url
    today = datetime.today().strftime('%Y-%m-%d')

    # Initialise empty lists
    journies = []
    types = []
    stopovers = []
    airlines = []
    airline_logos = []
    flight_numbers = []
    statuses = []
    scheduled_times = []
    estimated_times = []

    # Loop through each combination of (domestic/international) x (arrival/departure)
    url = "https://www.sydneyairport.com.au/flights/?query=&flightType=" + journey + "&terminalType=" + terminal + "&date=" + today + "&sortColumn=scheduled_time&ascending=true&showAll=true"
    print("Getting data for {}_{} flights".format(terminal, journey))
    driver.get(url)
    
    html_soup = BeautifulSoup(driver.page_source, "html.parser")
    flight_containers = html_soup.find_all("div", attrs={"class": "flight-card"})[2:]
    
    # Loop through all containers (one for each flight) to extract and store info
    for container in flight_containers:
        
        # International / domestic and Arrival / departure
        types.append('static/images/{}_{}.png'.format(terminal, journey))

        # Origin / Destinations
        journies.append(container.find("div", attrs={"class": "destination-name"}).text)

        # Stopovers (if any)
        if container.find("div", attrs={"class": "city-via"}) is not None:
            stopovers.append(container.find("div", attrs={"class": "city-via"}).text)
        else:
            stopovers.append("-")

        # Airlines
        airlines.append(container.find("span", attrs={"class": "with-image"}).text)

        # Airline logos
        airline_logos.append("https://www.sydneyairport.com.au" + container.img['src'])

        # Flight numbers
        flight_numbers.append(container.find("div", attrs={"class": "heading-medium"}).text)

        # Statuses
        statuses.append(container.find("div", attrs={"class": "status"}).text)

        # Scheduled times
        scheduled_times.append(container.find("div", attrs={"class": "large-scheduled-time"}).text[0:5])

        # Estimated times
        estimated_times.append(container.find("div", attrs={"class": "estimated-time"}).text[0:5])
    
    # Create dictionary of flights
    flights = {
        'Type': types,
        'Journey': journies,
        'Stopover': stopovers,
        'Airline': airlines,
        'Logo': airline_logos,
        'Flight number': flight_numbers,
        'Status': statuses,
        'Scheduled time': scheduled_times,
        'Estimated time': estimated_times 
    }
    
    print("Finished getting data for {}_{} flights".format(terminal, journey))

    return flights