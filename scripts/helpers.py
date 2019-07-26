import pytz
import logging
import sys

from sqlalchemy import create_engine
import os
import json

import pandas as pd


def tz_conversion(s):
    return s.dt.tz_localize(pytz.timezone('UTC')).dt.tz_convert('US/Pacific')


def make_logger():
    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)
    return log


def generate_shame_score():
    engine = create_engine(os.getenv('DATABASE_URL'))
    conn = engine.connect()
    query = "SELECT line_ref, direction_ref, stop_point_ref, Extract( EPOCH FROM (scheduled_arrival_time - expected_arrival_time)) AS min_late " \
            "FROM predictions"
    df = pd.read_sql(query, conn)

    group = df.groupby(['line_ref', 'direction_ref', 'stop_point_ref']).agg(
        {'min_late': 'mean'}).reset_index()

    group['prediction_label'] = 'tisk tisk'

    records = (group.groupby(['stop_point_ref', 'direction_ref', 'line_ref'])[
                   ['min_late', 'prediction_label']]
               .apply(lambda x: x.to_dict(orient='records')[0]).reset_index()
               .reset_index()
               .rename(columns={0: 'scores'})
               .groupby(['stop_point_ref', 'direction_ref'])[
                   ['line_ref', 'scores']]
               .apply(lambda x: x.to_dict(orient='records')).reset_index()
               .reset_index()
               .rename(columns={0: 'lines'})
               .drop(labels="index", axis=1)
               .to_dict(orient='records')
               )

    return records


if __name__ == '__main__':
    generate_shame_score()
