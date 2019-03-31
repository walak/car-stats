import datetime


def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    return datetime.datetime.now().strftime("%H:%M")


def get_current_date_and_time():
    return get_current_date() + " " + get_current_time()
