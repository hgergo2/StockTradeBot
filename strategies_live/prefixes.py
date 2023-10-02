from datetime import datetime


def time_prefix():
    return datetime.now().strftime("%H:%M:%S")