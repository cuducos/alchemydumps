# coding: utf-8

from calendar import isleap, monthrange
from datetime import date, datetime, timedelta
from itertools import chain


class BackupAutoClean(object):

    def __init__(self, dates=None, today=None):
        """
        :param dates: list of date ids (in string format)
        :param today: datetime object
        """
        self.dates = sorted(dates, reverse=True) if dates else []
        self.today = today or date.today()
        self.white_list = list()
        self.black_list = list()
        self.run()  # feed self.white_list & self.black_list

    def get_last_month_length(self):
        """
        :return: integer with the number of the days of the previous month
        """
        first_day = date(self.today.year, self.today.month, 1)  # current month
        last_day = first_day - timedelta(days=1)  # last month
        return monthrange(last_day.year, last_day.month)[1]

    def get_last_year_length(self):
        """
        :return: integer with the number of the days of the previous year
        """
        first_day = date(self.today.year, 1, 1)  # current year
        last_day = first_day - timedelta(days=1)  # last year
        return 366 if isleap(last_day.year) else 365

    def filter_dates(self, dates, period):
        """
        :param dates: list of ordered date ids (in string format)
        :param period: a string for comparison (week, month or year)
        :return: list of dates containing the most recent dates of each period
        """
        reference = datetime.strftime(self.today, '%Y%m%d%H%M%S')
        method_mapping = {
            'week': lambda obj: getattr(obj, 'isocalendar')()[1],
            'month': lambda obj: getattr(obj, 'month'),
            'year': lambda obj: getattr(obj, 'year')
        }
        for as_string in dates:
            as_date = datetime.strptime(as_string, '%Y%m%d%H%M%S')
            comparison = method_mapping.get(period)(as_date)
            reference_as_date = datetime.strptime(reference, '%Y%m%d%H%M%S')
            if comparison != method_mapping.get(period)(reference_as_date):
                reference = as_string
                yield as_string

    def run(self):
        """
        Feeds `self.white_list` and `self.black_list` with the dates do be kept
        and deleted (respectively)
        """

        # get last week, month and year dates
        last_w = self.today - timedelta(days=7)
        last_m = self.today - timedelta(days=self.get_last_month_length())
        last_y = self.today - timedelta(days=self.get_last_year_length())

        # create lists for each time period
        backups_week = list()
        backups_month = list()
        backups_year = list()
        backups_older = list()
        for timestamp in self.dates:
            datetime_ = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            date_ = date(datetime_.year, datetime_.month, datetime_.day)
            if date_ >= last_w:
                backups_week.append(timestamp)
            elif date_ >= last_m:
                backups_month.append(timestamp)
            elif date_ >= last_y:
                backups_year.append(timestamp)
            else:
                backups_older.append(timestamp)

        # feed white  list
        self.white_list.extend(chain(
            backups_week,
            self.filter_dates(backups_month, 'week'),
            self.filter_dates(backups_year, 'month'),
            self.filter_dates(backups_older, 'year')
        ))

        # feed black list
        diff_as_list = list(set(self.dates) - set(self.white_list))
        self.black_list.extend(sorted(diff_as_list, reverse=True))
