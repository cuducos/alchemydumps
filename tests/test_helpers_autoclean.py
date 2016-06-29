# coding: utf-8

from datetime import date
from unittest import TestCase

from flask_alchemydumps.helpers.autoclean import BackupAutoClean


class TestAutocleanHelper(TestCase):

    def test_get_last_month_length(self):
        backup_list = BackupAutoClean([], date(2012, 3, 1))
        self.assertEqual(29, backup_list.get_last_month_length())

    def test_get_last_year_length(self):
        backup_list = BackupAutoClean([], date(2013, 3, 1))
        self.assertEqual(366, backup_list.get_last_year_length())

    def test_filter_dates(self):
        backup_list = BackupAutoClean()
        dates_none = []
        dates_w = ['20141120000000', '20141119000000']
        dates_m = ['20131101000000', '20131130000000']
        dates_y = ['20111231000000', '20110101000000']
        calc_none = list(backup_list.filter_dates(dates_none, 'week'))
        calc_w = list(backup_list.filter_dates(dates_w, 'week'))
        calc_m = list(backup_list.filter_dates(dates_m, 'month'))
        calc_y = list(backup_list.filter_dates(dates_y, 'year'))
        self.assertEqual(calc_none, [])
        self.assertEqual(calc_w, ['20141120000000'])
        self.assertEqual(calc_m, ['20131101000000'])
        self.assertEqual(calc_y, ['20111231000000'])

    def test_run(self):
        date_ids = [
            '20110824045557',
            '20100106120931',
            '20090728192328',
            '20070611074712',
            '20130729044443',
            '20070611090332',
            '20090927181422',
            '20060505063150',
            '20090608052756',
            '20050413201344',
            '20111015194547',
            '20090711221957',
            '20140425202739',
            '20130808133229',
            '20120111210958',
            '20120419224811',
            '20060519170013',
            '20090111042034',
            '20100112115416'
        ]
        white_list = [
            '20140425202739',
            '20130808133229',
            '20130729044443',
            '20120419224811',
            '20111015194547',
            '20100112115416',
            '20090927181422',
            '20070611090332',
            '20060519170013',
            '20050413201344'
        ]
        black_list = [
            '20120111210958',
            '20110824045557',
            '20100106120931',
            '20090728192328',
            '20090711221957',
            '20090608052756',
            '20090111042034',
            '20070611074712',
            '20060505063150'
        ]
        backup_list = BackupAutoClean(date_ids, date(2014, 4, 25))
        self.assertEqual(len(backup_list.white_list), 10)
        self.assertEqual(len(backup_list.black_list), 9)
        self.assertEqual(backup_list.white_list, white_list)
        self.assertEqual(backup_list.black_list, black_list)
