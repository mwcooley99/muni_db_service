from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from dateutil.parser import parse as parse_date
from pytz import timezone
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler

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


# Models
class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, unique=True, primary_key=True,
                   autoincrement=True)
    response_time = db.Column(db.DateTime)
    recorded_time = db.Column(db.DateTime)
    line_ref = db.Column(db.String)
    direction_ref = db.Column(db.String)
    stop_point_ref = db.Column(db.Integer)
    scheduled_arrival_time = db.Column(db.DateTime)
    expected_arrival_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Stop: {self.stop_point_ref} Line: {self.line_ref}>'


def date_parser(date):
    return parse_date(date).astimezone(timezone('US/Pacific'))


# Helper functions
def make_prediction(timestamp, stop_data):
    base = stop_data['MonitoredVehicleJourney']
    base_prediction = base['MonitoredCall']

    predict_dict = {
        'response_time': date_parser(timestamp),
        'recorded_time': date_parser(stop_data['RecordedAtTime']),
        'line_ref': base['LineRef'],
        'direction_ref': base['DirectionRef'],
        'stop_point_ref': base_prediction['StopPointRef'],
        'scheduled_arrival_time': date_parser(
            base_prediction['AimedArrivalTime'])
    }
    try:
        predict_dict['expected_arrival_time'] = date_parser(
            base_prediction['ExpectedArrivalTime'])
    except TypeError:
        predict_dict['expected_arrival_time'] = predict_dict[
            'scheduled_arrival_time']

    return Prediction(**predict_dict)


def tick(url):
    # Call the API and get data
    resp = requests.get(url)
    resp.encoding = 'utf-8-sig'
    json_data = resp.json()

    # Filter the data and create objects
    routes = ['7', '38', '14', '2', 'M', 'N', 'T', 'K']
    response_time = json_data['ServiceDelivery']['StopMonitoringDelivery'][
        'ResponseTimestamp']
    prediction_results = \
        json_data['ServiceDelivery']['StopMonitoringDelivery'][
            'MonitoredStopVisit']

    predictions = [make_prediction(response_time, d) for d in
                   prediction_results if
                   d['MonitoredVehicleJourney']['LineRef'] in routes]

    db.session.add_all(predictions)
    db.session.commit()

    app.logger.info(f'commit at: {response_time}')


def run_scheduler():
    # Set up scheduler
    scheduler = BackgroundScheduler()

    # Runs every 15 min
    scheduler.add_job(tick, 'cron', args=[url], minute='0-59/15')
    scheduler.start()


def my_debug(msg, fn="", fl=""):
    print(msg)
    with open("log.txt", "a+") as f:
        f.write(str(msg) + '\n')


run_scheduler()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Prediction=Prediction)


# Routes
@app.route('/')
def hello_world():
    return 'Hello World1!'


if __name__ == '__main__':
    app.run(debug=False)
