import pytz
import logging
import sys
import pickle

from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras import backend as K

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


def get_shame_data(db, time=1.5):
    query = "SELECT line_ref, direction_ref, stop_point_ref, Extract( EPOCH FROM (scheduled_arrival_time - expected_arrival_time)) AS min_late " \
            "FROM predictions"

    df = pd.read_sql(query, db.engine)

    group = df.groupby(['line_ref', 'direction_ref', 'stop_point_ref']).agg(
        {'min_late': 'mean'}).reset_index()
    group.fillna('n/a', inplace=True)

    group['prediction_label'] = generate_shame_score(group, time)

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

    return {'results': records}


def generate_shame_score(group, time=1.5):
    # Load the model and the lookup tables

    with open('static/time_encoder.pkl', "rb") as file_path:
        time_encoder = pickle.load(file_path)

    with open('static/model_encoder.pkl', 'rb') as file_path:
        model = pickle.load(file_path)

    with open('static/lookup_frames.pkl', 'rb') as file_path:
        lookup_frames = pickle.load(file_path)

    # Encode the time, if the time isn't in the encoder, give default value
    try:
        encoded_time = time_encoder.transform([float(time)])
    except:
        encoded_time = time_encoder.transform([6.3])

    group['time_encoded'] = encoded_time[0]

    # encode the data
    group_merged = group
    refs = ['line_ref', 'direction_ref', 'stop_point_ref']
    for ref in refs:
        group_merged = pd.merge(group_merged, lookup_frames[ref], on=ref,
                                how='left')

    # Get the encoded data
    model_cols = ['line_encoded', 'direction_encoded', 'stop_encoded',
                  'time_encoded']
    data = group_merged[model_cols].values

    # run the model to generate predictions
    results = pd.DataFrame(data=model.predict_classes(data),
                           columns=['late_class'])

    results_merged = pd.merge(results, lookup_frames['late_ref'],
                              on='late_class', how='left')

    K.clear_session()

    return results_merged['late bin'].values
