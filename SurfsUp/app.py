from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd
import matplotlib.pyplot as plt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = (pd.to_datetime(last_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    precipitation_data = session.query(measurement.date, measurement.prcp)\
                                .filter(measurement.date >= one_year_ago).all()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station).all()
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = 'USC00519281'  # Replace with the most active station ID
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = (pd.to_datetime(last_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    tobs_data = session.query(measurement.date, measurement.tobs)\
                        .filter(measurement.station == most_active_station_id)\
                        .filter(measurement.date >= one_year_ago).all()
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    temperature_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                                .filter(measurement.date >= start).all()
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    temperature_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                                .filter(measurement.date >= start)\
                                .filter(measurement.date <= end).all()
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)
