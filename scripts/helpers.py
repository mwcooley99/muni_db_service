import pytz


def tz_conversion(s):
    return s.dt.tz_localize(pytz.timezone('UTC')).dt.tz_convert('US/Pacific')
