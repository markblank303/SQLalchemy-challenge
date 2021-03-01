import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


##Home page.
##List all routes that are available.
@app.route('/')
def index():
    return(
        f"<strong>Avaible Routes:</strong><br/>"
        f"<br/>"
        f"<a href=/api/v1.0/precipitation><strong>Precipitation</strong></a><br/>"
        f"(/api/v1.0/percipitation)<br/>"
        f"<a href=/api/v1.0/stations><strong>Stations</strong></a><br/>"
        f"(/api/v1.0/stations)<br/>"
        f"<a href=/api/v1.0/tobs><strong>TOBS</strong></a><br/>"
        f"(/api/v1.0/tobs)<br/>"
        f"<a href=/api/v1.0/start><strong>Start Date</strong></a><br/>"
        f"(/api/v1.0/start (enter as YYYY-MM-DD))<br/>"
        f"<a href=/api/v1.0/start/end><strong>Start Date and End Date</strong></a><br/>"
        f"(/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD))"
    )


##Convert the query results to a Dictionary using date as the key and prcp as the value.
##Return the JSON representation of your dictionary.          
@app.route("/api/v1.0/precipitation")
def precipiation():
        session = Session(engine)
        results = session.query(Measurement.date, Measurement.prcp).all()
        session.close()

        all_prcp = []
        for date, prcp in results:
            prcp_dict = {}
            prcp_dict[date] = prcp
            all_prcp.append(prcp_dict)

        return jsonify(all_prcp)

##Return a JSON list of stations from the dataset.       
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        results = session.query(Station.name).all()
        session.close()
        all_stations = list(np.ravel(results))
        
        return jsonify(all_stations)
        
##Query the dates and temperature observations of the most active station for the last year of data.
##Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    year_ago = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    last_year = session.query(Measurement.date, Measurement.tobs).filter_by(date=year_ago).all()

    session.close()

    return jsonify(last_year)

##Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
##When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    all_dates = []
    for tmin, tavg, tmax in results:
        dates_dict = {}
        dates_dict['tmin'] = tmin
        dates_dict['tavg'] = tavg
        dates_dict['tmax'] = tmax
        all_dates.append(dates_dict)
    
    return jsonify(all_dates)

##When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date >= end).all()

    session.close()

    all_dates = []
    for tmin, tavg, tmax in results:
        dates_dict = {}
        dates_dict['tmin'] = tmin
        dates_dict['tavg'] = tavg
        dates_dict['tmax'] = tmax
        all_dates.append(dates_dict)
    
    return jsonify(all_dates)
        
    
if __name__ == '__main__':
    app.run(debug=True)
