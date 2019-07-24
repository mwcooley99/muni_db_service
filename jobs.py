from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app import app, db
from models import Prediction

from dateutil.parser import parse as parse_date
from pytz import timezone


def date_parser(date):
    return parse_date(date)


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


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
        predict_dict['expected_arrival_time'] = None
    except ValueError:
        predict_dict['expected_arrival_time'] = None

    return Prediction(**predict_dict)


def tick(url):
    # Call the API and get data
    resp = requests_retry_session().get(url)
    app.logger.info(f'Response code: {resp.status_code}')

    try:
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

    except KeyError:
        app.logger.error(f'There was an error: {KeyError}')


sched = BlockingScheduler()

API_KEY_511 = os.getenv('API_KEY_511')
url = f"http://api.511.org/transit/StopMonitoring?api_key={API_KEY_511}&agency=SF&format=json"


@sched.scheduled_job('cron', minute='0-59/10')
def timed_job():
    tick(url)


sched.start()
