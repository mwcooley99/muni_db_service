from flask import Flask
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)


def tick():
    print(f'The time right now is: {datetime.now()}')


scheduler = BackgroundScheduler()
scheduler.add_job(tick, 'interval', seconds=10)
scheduler.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
