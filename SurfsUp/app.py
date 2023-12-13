# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base ()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask (__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
        return (
            f"Welcome to the Homepage<br>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations - List of weather stations<br>"
            f"/api/v1.0/tobs - Temperature observations for the last 12 months<br>"
            f"/api/v1.0/2016-08-23 - Temperature sumamry for a specified start"
            f"/api/v1.0/2016-08-23/2017-08-23 - Temperature summary for a specified start and end date<br>"
        )
        
# Convert query results from precipitation analysis to a dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    prcp_dict = {date: prcp for date, prcp in year_results}
    session.close()
    return jsonify(prcp_dict)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station).all()
    station_list = [station[0] for station in station_results]
    session.close()
    return jsonify(station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = 'USC00519281'
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_results = session.query(Measurement.tobs).filter(Measurement.station == most_active_station).\
    filter(Measurement.date >= prev_year).all()
    temperature_data = [tobs[0] for tobs in station_results]
    session.close()
    return jsonify(temperature_data)

# Return a list of the min temp, avg temp, and max temp for a specified start date
@app.route("/api/v1.0/<start>")
# Return a list of the min temp, avg temp, and max temp for a specifed start-end range
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=None):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
            .group_by(Measurement.date).all())
    else:
        results = (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
            .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).group_by(Measurement.date).all())
        
    dates = []
    for results in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["TMIN"] = result[1]
        date_dict["TAVG"] = result[2]
        date_dict["TMAX"] = result[3]
        dates.append(date_dict)
    session.close()
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)