import pytz
import logging
import sys


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
