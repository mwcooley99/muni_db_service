from flask import Flask
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['DEBUG'] = False


def tick():
    print(f'The time right now is: {datetime.now()}')


# Set up scheduler
scheduler = BackgroundScheduler()
# Runs every on every 10 second time
scheduler.add_job(tick, 'cron', second='0-59/10')
scheduler.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
