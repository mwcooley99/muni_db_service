from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
API_KEY_511 = os.getenv('API_KEY_511')
url = f"http://api.511.org/transit/StopMonitoring?api_key={API_KEY_511}&agency=SF&format=json"

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


def make_prediction(timestamp, stop_data):
    print(stop_data)
    base = stop_data['MonitoredVehicleJourney']
    base_prediction = base['MonitoredCall']

    predict_dict = {
        'response_time': timestamp,
        'recorded_time': stop_data['RecordedAtTime'],
        'line_ref': base['LineRef'],
        'direction_ref': base['DirectionRef'],
        'stop_point_ref': base_prediction['StopPointRef'],
        'scheduled_arrival_time': base_prediction['AimedArrivalTime'],
        'expected_arrival_time': base_prediction['ExpectedArrivalTime']
    }

    return Prediction(**predict_dict)


# TODO - have it save to a db instead
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
    print(predictions)


def my_debug(msg, fn="", fl=""):
    print(msg)
    with open("log.txt", "a+") as f:
        f.write(str(msg) + '\n')


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    # Set up scheduler
    scheduler = BackgroundScheduler()
    # Runs every on every 10 second time
    # TODO - change run time
    scheduler.add_job(url, 'cron', second='0-59/10')
    scheduler.start()
    app.run(debug=False)
