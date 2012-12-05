from datetime import datetime
from django.utils.timezone import utc

def to_timestamp(dt):
    UNIX_EPOCH = datetime(1970, 1, 1, 0, 0).replace(tzinfo=utc)
    delta = dt - UNIX_EPOCH
    seconds = delta.total_seconds()
    # ms = seconds * 1000
    return seconds