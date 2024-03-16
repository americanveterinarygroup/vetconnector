from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


def start_date():
    dt = date.today().replace(day=1) - relativedelta(months=3)
    return dt



def end_date():
    dt = date.today().replace(day=1) - timedelta(days=1)
    return dt



def run_date():
    dt = datetime.today()
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt



def new_hire_start():
    dt = date.today().replace(day=1) - relativedelta(months=16)
    return dt


def exclude_date():
    dt = date.today().replace(day=1) - relativedelta(months=1)
    return dt