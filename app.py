# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table

Station = Base.classes.station
Measurement = Base.classes.measurement

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;")

#Query results from precipitation analyis
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Import dates
    end_date = dt.date(2017, 8, 23)
    start_date = end_date - dt.timedelta(days=365)
    #Calculate precipitation date for last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()
    #Add results to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

#Return a JSON list of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    # Calculate total number of stations
    station_list = session.query(Station.station, Station.name).all()

    # Add results to dictionary
    stations_dict = {}
    for station in station_list:
        stations_dict[station[0]] = station[1]

    return jsonify(stations_dict)

#Query the dates and temp observations from most-active station
@app.route("/api/v1.0/tobs")
def tobs():
     # Define the start date
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Find most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    most_active = active_stations[0][0]
    #Query dates and temp observations
    temp_stats = session.query(Measurement.station, Measurement.tobs).\
                filter(Measurement.station == most_active).\
                filter(Measurement.date >= start_date).all()
    
    # Add results to dictionary
    tobs_data = []
    for station, tobs in temp_stats:
        temp_dict = {'station': station, 'temperature': tobs}
        tobs_data.append(temp_dict)

    return jsonify(tobs_data)

#Return a JSON list of min, avg, max temps for specified start 
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Convert start date to datetine object
    starting_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    # Query temp statistics for start date
    start_temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= starting_date).all()
    # Convert temps to a list
    start_temps_list = list(np.ravel(start_temps))

    return jsonify({
        "min_temperature": start_temps_list[0],
        "max_temperature": start_temps_list[1],
        "avg_temperature": start_temps_list[2]
    })
 #Return a JSON list of min, avg, max temps for specified start-end   
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Convert start and end date to datetine object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    # Query temp statistics for start-end date
    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    # Convert temps to a list
    min_temp, max_temp, avg_temp = temp_stats[0]

    return jsonify({
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "min_temperature": min_temp,
        "max_temperature": max_temp,
        "avg_temperature": avg_temp
    })
    
if __name__ == '__main__':
    app.run()