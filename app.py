from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler



app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def tick():
    # my_debug(f'The time right now is: {datetime.now()}')
    API_KEY_511 = os.getenv('API_KEY_511')
    url = f"http://api.511.org/transit/StopMonitoring?api_key={API_KEY_511}&agency=SF&format=json"
    resp = requests.get(url)

    resp.encoding = 'utf-8-sig'
    json_data = resp.json()
    my_debug(json_data)




def my_debug(msg, fn="", fl=""):
    print(msg)
    with open("log.txt", "a+") as f:
        f.write(str(msg) + '\n')


# Set up scheduler
scheduler = BackgroundScheduler()
# Runs every on every 10 second time
scheduler.add_job(tick, 'cron', second='0-59/10')
scheduler.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=False)
