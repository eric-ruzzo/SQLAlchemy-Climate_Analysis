from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/><br/>"
        f"Enter dates in yyyy-mm-dd format"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date = dt.date(2017, 8, 23)

    one_year_ago = latest_date - dt.timedelta(days=365)
    
    # Perform a query to retrieve the date and precipitation scores
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.desc()).all()

    dates = []
    for date in precip:
        date_dict = {}
        date_dict["date"] = date.date
        date_dict["prcp"] = date.prcp
        dates.append(date_dict)

    return jsonify(dates)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name).\
        filter(Station.station == Measurement.station).\
        group_by(Station.station).\
        order_by(func.count(Measurement.station).desc()).all()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date = dt.date(2017, 8, 23)

    one_year_ago = latest_date - dt.timedelta(days=365)
    
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).all()

    all_tobs = list(np.ravel(tobs))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_only(start):
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = latest_date[0]

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= latest_date).all()

    (tmin, tavg, tmax) = temp_data[0]

    temp_dict = (f"Temperature data for {start} to {latest_date}", {"Minimum temperature": tmin, "Average temperature": round(tavg, 2), "Maximum temperature": tmax})

    if start <= latest_date:
        return jsonify(temp_dict)

    else:
        return jsonify(f"ERROR: No temperature data found for {start}"), 404

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    (tmin, tavg, tmax) = temp_data[0]

    temp_dict = (f"Temperature data for {start} to {end}", {"Minimum temperature": tmin, "Average temperature": round(tavg, 2), "Maximum temperature": tmax})

    if start <= end:
        return jsonify(temp_dict)

    else:
        return jsonify(f"ERROR: No temperature data found for {start}"), 404


if __name__ == "__main__":
    app.run(debug=True)