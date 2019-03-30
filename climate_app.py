from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
        f"/api/v1.0/<start>/<end><br/>"
    )

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