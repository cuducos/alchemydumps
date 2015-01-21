# coding: utf-8

from flask.ext.alchemydumps.helpers.identification import (
    get_id, get_ids, get_list
)
from unipath import Path
from unittest import TestCase


class TestIdentificationHelper(TestCase):

    def test_get_id(self):
        file_path = Path('/vagrant/alchemydumps/db-bkp-20141115172107-User.gz')
        assert get_id(file_path) == '20141115172107'

    def test_get_list(self):
        date_ids = ['20141115172107', '20141112113214']
        models = ['User', 'Post']
        prefix = '/vagrant/alchemydumps/'
        files = list()
        for i in date_ids:
            for m in models:
                files.append(Path('{}db-bkp-{}-{}.gz'.format(prefix, i, m)))
        expected = list()
        for m in models:
            path = '{}db-bkp-{}-{}.gz'
            expected.append(Path(path.format(prefix, date_ids[0], m)))
        assert get_list(date_ids[0], files) == expected

    def test_get_ids(self):
        date_ids = ['20141115172107', '20141112113214']
        models = ['User', 'Post']
        prefix = '/vagrant/alchemydumps/'
        files = list()
        for i in date_ids:
            for m in models:
                files.append(Path('{}db-bkp-{}-{}.gz'.format(prefix, i, m)))
        assert get_ids(files) == date_ids