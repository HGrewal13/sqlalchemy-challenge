# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available API routes"""
    return (
        f"Available Routes:<br>" + 
        f"/api/v1.0/precipitation <br>" + 
        f"/api/v1.0/stations <br>" + 
        f"/api/v1.0/tobs <br>" +
        f"/api/v1.0/start <br>" +
        f"/api/v1.0/start/end <br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Find the most recent date in the data set.
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_datetime = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    
    # Calculate the date one year from the last date in data set.
    one_year_prior = most_recent_datetime - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = (
        session.query(measurement.date, measurement.prcp)
        .filter(measurement.date >= one_year_prior.date())
        .all()
    )

    # Convert to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Return JSON
    return jsonify(precipitation_dict)
    

@app.route("/api/v1.0/stations")
def stations():
    
    # Query all stations
    stations_data = session.query(station.station).all()

    # Convert to a list
    stations_list = [station[0] for station in stations_data]

    # Return JSON
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_datetime = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    
    # Calculate the date one year from the last date in data set.
    one_year_prior = most_recent_datetime - dt.timedelta(days=365)
    
    # Design a query to find the most active stations (i.e. which stations have the most rows?)
    # List the stations and their counts in descending order.
    most_active_stations = session.query(measurement.station, func.count(measurement.station)
                                    ).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    most_active_station_id = most_active_stations[0][0]

    tobs_data = (
    session.query(measurement.tobs).filter(measurement.station == most_active_station_id)
    .filter(measurement.date >= one_year_prior.date())
    .all()
    )
    
    # Convert to list
    temps = [temp[0] for temp in tobs_data]

    # return JSON
    return jsonify(temps)

@app.route("/api/v1.0/start")
def start(start):    
    # Temperature calculations
    temp_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)
                     ).filter(measurement.date >= start).all()
    

    # convert to dict
    temp_dict = {
        "temp_min": temp_stats[0][0],
        "temp_max": temp_stats[0][1],
        "temp_avg": temp_stats[0][2]
    }

    # return JSON
    return jsonify(temp_dict)

@app.route("/api/v1.0/start/end")
def start_end(start, end):
    # Temperature calculations
    temp_stats = (
        session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)
                     ).filter(measurement.date >= start and measurement.date <= end).all()
    )

    # convert to dict
    temp_dict = {
        "temp_min": temp_stats[0][0],
        "temp_max": temp_stats[0][1],
        "temp_avg": temp_stats[0][2]
    }

    # return JSON
    return jsonify(temp_dict)

# Close the session
session.close()

if __name__ == "__main__":
    app.run(debug=True)