import humanize
import datetime


def ends_in(until):
    return humanize.naturaldelta((datetime.datetime.utcnow() - until))