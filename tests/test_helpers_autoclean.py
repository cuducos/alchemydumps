# coding: utf-8

from flask.ext.alchemydumps.helpers.autoclean import (
    bw_lists, filter_dates, get_last_month_length, get_last_year_length
)
from datetime import date
from unittest import TestCase


class TestAutocleanHelper(TestCase):

    def test_get_last_month_length(self):
        march2012 = date(2012, 3, 1)
        assert get_last_month_length(march2012) == -29

    def test_get_last_year_length(self):
        march2013 = date(2013, 3, 1)
        assert get_last_year_length(march2013) == -366

    def test_bw_lists(self):
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
            '20120419224811',
            '20111015194547',
            '20100112115416',
            '20090927181422',
            '20070611090332',
            '20060519170013',
            '20050413201344'
        ]
        black_list = [
            '20130729044443',
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
        lists = bw_lists(date_ids)
        assert sorted(lists['white_list']) == sorted(white_list)
        assert sorted(lists['black_list']) == sorted(black_list)

    def test_filter_dates(self):
        dates_w = ['20141120000000', '20141119000000']
        dates_m = ['20131101000000', '20131130000000']
        dates_y = ['20111231000000', '20110101000000']
        assert filter_dates(dates_w, 'week') == ['20141120000000']
        assert filter_dates(dates_m, 'month') == ['20131101000000']
        assert filter_dates(dates_y, 'year') == ['20111231000000']
