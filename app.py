from flask import Flask, send_from_directory, make_response

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from dateutil.parser import parse as parse_date
from pytz import timezone
import os

from scripts.helpers import tz_conversion

import pandas as pd

import requests

app = Flask(__name__)

# Set some paths and config options
basedir = os.path.abspath(os.path.dirname(__file__))
API_KEY_511 = os.getenv('API_KEY_511')
url = f"http://api.511.org/transit/StopMonitoring?api_key={API_KEY_511}&agency=SF&format=json"

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'sqlite:///' + os.path.join(basedir, 'data.sqlite')

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'postgres://localhost:5432/muni_service'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add functionality to the app
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Prediction


#
# def run_scheduler():
#     # Set up scheduler
#     scheduler = BackgroundScheduler()
#
#     # Runs every 15 min
#     scheduler.add_job(tick, 'cron', args=[url], minute='0-59/10')
#     scheduler.start()


def my_debug(msg, fn="", fl=""):
    print(msg)
    with open("log.txt", "a+") as f:
        f.write(str(msg) + '\n')


# run_scheduler()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Prediction=Prediction)


# Routes
@app.route('/')
def hello_world():
    return 'Hello World2!'


@app.route('/data')
def all_data():
    query = Prediction.query
    df = pd.read_sql(query.statement, query.session.bind)

    date_cols = ['response_time', 'recorded_time', 'scheduled_arrival_time',
                 'expected_arrival_time']

    df[date_cols] = df[date_cols].apply(tz_conversion)

    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"

    return resp


if __name__ == '__main__':
    app.run(debug=False)
