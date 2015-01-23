# coding: utf-8

from datetime import date, datetime, timedelta


def bw_lists(dates):
    """
    :param dates: list of different date ids from existing backups
    :return: dictionary with white (to be kept) and black (to be deleted) list
    """

    # get key dates
    dates = sorted(dates, reverse=True)
    today = datetime.now()
    last_m_len = get_last_month_length(today)
    last_y_len = get_last_year_length(today)
    last_w = (today + timedelta(days=-7))
    last_m = (today + timedelta(days=last_m_len))
    last_y = (today + timedelta(days=last_y_len))

    # create lists for each time period
    backups_week = list()
    backups_month = list()
    backups_year = list()
    backups_older = list()
    for i in range(0, len(dates)):
        d = datetime.strptime(dates[i], '%Y%m%d%H%M%S')
        if d >= last_w:
            backups_week.append(dates[i])
        elif d >= last_m:
            backups_month.append(dates[i])
        elif d >= last_y:
            backups_year.append(dates[i])
        else:
            backups_older.append(dates[i])

    # include all backups
    white_list = backups_week
    white_list = white_list + filter_dates(backups_month, 'week')
    white_list = white_list + filter_dates(backups_year, 'month')
    white_list = white_list + filter_dates(backups_older, 'year')

    # return
    black_list = sorted(list(set(dates) - set(white_list)), reverse=True)
    return {'white_list': white_list, 'black_list': black_list}


# helpers functions


def get_last_month_length(today):
    """
    :param today: datetime object
    :return: integer with the number of the days of the previous month
    """
    m = today.month
    y = today.year
    now = date(y, m, 1)
    if today.month == 1:
        previous_month = 12
        previous_year = y - 1
    else:
        previous_month = m - 1
        previous_year = y
    one_month_earlier = date(previous_year, previous_month, 1)
    return (one_month_earlier - now).days


def get_last_year_length(today):
    """
    :param today: datetime object
    :return: integer with the number of the days of the previous year
    """
    now = date(today.year, 1, 1)
    one_year_earlier = date(today.year - 1, 1, 1)
    return (one_year_earlier - now).days


def filter_dates(dates, period):
    """
    :param dates: list of date ids in string format
    :param period: a string for comparison (week, month or year)
    :return: a list of dates filtered according the period
    """
    output = list()
    control = False
    for i in range(0, len(dates)):
        dt = datetime.strptime(dates[i], '%Y%m%d%H%M%S')
        if period == 'week':
            comparison = dt.isocalendar()[1]
        elif period == 'month':
            comparison = dt.month
        elif period == 'year':
            comparison = dt.year
        else:
            return output
        if comparison != control:
            output.append(dates[i])
            control = comparison
    return output
