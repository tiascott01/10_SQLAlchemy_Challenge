# Import the dependencies.
import numpy as np
import datetime as dt
from datetime import date, timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, select, distinct, inspect, desc
from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
#Create the engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


# General Queries to Make the System Run
first_date = session.query(Measurement.date).order_by(Measurement.date).first()
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
first_date = dt.datetime.strptime(first_date[0], '%Y-%m-%d').date()
last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()
session.close()


# Homepage for routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
       f"<html>"
        f"<head>"
        f"<style>"
        f"body {{ font-family: 'Arial', sans-serif; }}"
        f"h2 {{ color: #333; }}"
        f"p {{ color: #555; }}"
        f"form {{ margin-top: 20px; }}"
        f"label, input {{ margin-bottom: 10px; }}"
        f"</style>"
        f"</head>"
        f"<body>"
        f"<h2>Welcome to Hawaii Climate Analysis</h2>"
        f"<p>List all available API routes:</p>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        f"<li><a href='/api/v1.0/station'>/api/v1.0/station</a></li>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        f"</ul>"
        f"<h3>Search Option 1 - Start Date:</h3>"
        f"<p>Enter a start date between {first_date} and {last_date} to search temperatures after the start date.</p>"
        f"<form action='/api/v1.0/temp/start' method='post'>"
        f"Start date: <input type='date' name='start_date' required>"
        f"<input type='submit' value='Search'>"
        f"</form>"
        f"<h3>Search Option 2 - Start and End Date:</h3>"
        f"<p>Enter a start and end date between {first_date} and {last_date} to search temperatures between the start and end date.</p>"
        f"<form action='/api/v1.0/temp/start/end' method='post'>"
        f"Start date: <input type='date' name='start_date' required><br>"
        f"End date: <input type='date' name='end_date' required>"
        f"<input type='submit' value='Search'>"
        f"</form>"
        f"</body>"
        f"</html>"
    )




#API For Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        # Find the most recent date in the data set
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
        # Perform a query to retrieve the data and precipitation scores
        scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= dt.date(2016, 8, 23)).all()

        # Jsonify the results
        precipitation = {date: prcp for date, prcp in scores}

        # Convert list into a dictionary
        response_dict = {
            "Output": "Results for Precipitation from 2016-08-23 to 2017-08-23",
            "Results": precipitation
        }

        # Return the JSON response
        return jsonify(response_dict)
    
    finally:
        # Close the session in a finally block to ensure it gets closed even if an exception occurs
        session.close()




#API For Stations
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        # Return a list of all stations from the data set
        stations = session.query(Station.station).all()

        # Jsonify the results
        station_data = [Station[0] for Station in stations]

        # Convert list into a dictionary
        response_dict = {
            "Output": "Results for Station Data",
            "Results": station_data
        }

        # Return the JSON response
        return jsonify(response_dict)
    
    finally:
        # Close the session in a finally block to ensure it gets closed even if an exception occurs
        session.close()   




#API For Temperature Obsevations
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    try:
        #Find the most active station
        most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).first()
        
        if most_active_station:
            most_active_station_id = most_active_station[0]

            # Query for temperature observations from the most active station within the previous year
            temperature_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station == most_active_station_id).all()

            # Convert results into a list of dictionaries
            temp_data = [{"date": date, "temperature": tobs} for date, tobs in temperature_data]

            # Create the response dictionary
            response_dict = {
                "output": f"One Year Temperature Results for Most Active Station {most_active_station_id}",
                "results": temp_data
            }

            # Return the JSON response
            return jsonify(response_dict)

        else:
            return jsonify({"error": "No stations found"}), 404

    finally:
        # Close the session in a finally block to ensure it gets closed even if an exception occurs
        session.close()




@app.route("/api/v1.0/temp/start", methods=['POST'])
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        # Parse the start and end dates from the request form
        start_date = dt.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()

        # Enforce that the dates are within the range
        if not (first_date <= start_date <= last_date):
            raise ValueError("Date not in range.")

        # Query to get the min, avg, and max temperatures for a given start date.
        results = session.query(
            Measurement.date,
            func.min(Measurement.tobs).label('min_temp'),
            func.max(Measurement.tobs).label('max_temp'),
            func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date >= start_date).group_by(Measurement.date).all()

        # Store the results in a dictionary
        response_data = [
            {
                result[0]: {
                    "min_temp": result[1],
                    "max_temp": result[2],
                    "avg_temp": result[3]
                }
            } for result in results
        ]

        # Jsonify the results
        return jsonify(response_data)

    except ValueError as e:
        return f"Error: {str(e)} Please enter a date between {first_date} and {last_date}", 422
    
    finally:
        # Close the session in a finally block to ensure it gets closed even if an exception occurs
        session.close()




@app.route("/api/v1.0/temp/start/end", methods=['POST'])
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        # Parse the start and end dates from the request form
        start_date = dt.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        # Enforce that the dates are within the range
        if not (first_date <= start_date <= last_date) or not (first_date <= end_date <= last_date):
            raise ValueError(f"Error: Date not in range. Please enter a date between {first_date} and {last_date}")

        # Query to get the min, avg, and max temperatures for a given start-end range.
        results = session.query(
            Measurement.date,
            func.min(Measurement.tobs).label('min_temp'),
            func.max(Measurement.tobs).label('max_temp'),
            func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date.between(start_date, end_date)).group_by(Measurement.date).all()

        # Store the results in a dictionary
        response_data = [
            {
                result[0]: {
                    "min_temp": result[1],
                    "max_temp": result[2],
                    "avg_temp": result[3]
                }
            } for result in results
        ]

        # Jsonify the results
        return jsonify(response_data)

    except ValueError as e:
        return f"Error: {str(e)} Please enter a date between {first_date} and {last_date}", 422

    finally:
        # Close the session in a finally block to ensure it gets closed even if an exception occurs
        session.close()



if __name__ == '__main__':
    app.run(debug=True, threaded=False)
