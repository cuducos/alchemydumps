from unittest import TestCase

from flask_alchemydumps.helper.backup import CommonTools


class TestBackup(TestCase):

    def setUp(self):
        self.backup = CommonTools()

    def test_get_timestamp(self):
        name = 'BRA-19940717123000-ITA.gz'
        self.assertEqual('19940717123000', self.backup.get_timestamp(name))

    def test_parse_timestamp(self):
        timestamp = '19940717123000'
        expected = 'Jul 17, 1994 at 12:30:00'
        self.assertEqual(expected, self.backup.parse_timestamp(timestamp))
