# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################


# Create engine for hawaii.sqlite
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define a function that creates a home page, listing all available routes
@app.route("/")
def home():
    print("Server Received Request for 'Home' page...")
    return """
    <h1>Hi! Welcome to my Honolulu Climate API!<h1>
    <h3>The available routes are: <br/><h3>
    <ul>
        <li>Precipitation Data: <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li>Station Data: <a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>
        <li>Temperature Data: <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>
        <li>To find minimum, average, and maximum temperatures for a specific date range, use '/api/v1.0/start/'</li>
    </ul>
    """

# Define a function that returns precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    # Query the data 12 months for the previous year of data
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the data of the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    # Establish a dictionary using [date] as the key and [prcp] as the value
    prcp_dict = {date: prcp for date, prcp in results}

    # Return the dictionary with dates and prcp.
    return jsonify(prcp_dict)

# Define a function that creates a list of stations
@app.route('/api/v1.0/stations')
def get_stations():
    print("Server received request for 'Station' page...")

    stations = session.query(Station.station).all()
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

# Define a function that returns temperature observations for the last 12 months of the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Temperature Observations' page...")

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query temperature observations for the last 12 months of the most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_data = []
    for date, tobs in results:
        tobs_data.append({"date": date, "tobs": tobs})

    return jsonify(tobs_data)

# List of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    print("Server received request for 'Temperature Statistics' page...")

    # Query the database to calculate the minimum, average, and maximum temperatures
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date >= start).all()

    # Create a dictionary to store the temperature statistics
    temp_stats = {}
    temp_stats["start_date"] = start
    if end:
        temp_stats["end_date"] = end
    temp_stats["min_temp"] = results[0][0]
    temp_stats["avg_temp"] = results[0][1]
    temp_stats["max_temp"] = results[0][2]

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)















#######################

# Sample data for stations
stations = [
    {"station_id": 1, "name": "Station A"},
    {"station_id": 2, "name": "Station B"},
    {"station_id": 3, "name": "Station C"}
]

# Route to return a list of stations
@app.route('/stations')
def get_stations():
    return jsonify(stations)

if __name__ == '__main__':
    app.run(debug=True)