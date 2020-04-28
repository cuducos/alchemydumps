from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask_alchemydumps.backup import RemoteTools


class TestRemoteTools(TestCase):

    def setUp(self):
        self.mock_ftp = MagicMock()

    def test_normalize_url(self):
        self.mock_ftp.host = 'f.oo'
        self.mock_ftp.pwd.return_value = '/bar'
        backup = RemoteTools(self.mock_ftp)
        self.assertEqual('ftp://f.oo/bar/', backup.path)

    def test_get_file(self):
        files = (
            'BRA-19940704123000-USA.gz',
            'BRA-19940709163000-NED.gz',
            'BRA-19940713123000-SWE.gz',
            'BRA-19940717123XXX-ITA.gz',
        )
        self.mock_ftp.nlst.return_value = iter(files)

        backup = RemoteTools(self.mock_ftp)
        files = tuple(backup.get_files())

        expected = (
            'BRA-19940704123000-USA.gz',
            'BRA-19940709163000-NED.gz',
            'BRA-19940713123000-SWE.gz',
        )
        self.assertTrue(backup.ftp.nlst.called)
        self.assertEqual(expected, files)

    @patch('flask_alchemydumps.backup.gzip.open')
    def test_create_file(self, mock_open):
        self.mock_ftp.host = 'f.oo'
        self.mock_ftp.pwd.return_value = '/bar'
        mock_handler = mock_open.return_value.__enter__.return_value
        contents = '42'.encode()

        backup = RemoteTools(self.mock_ftp)
        created = backup.create_file('foobar.gz', contents)
        storbinary_args = backup.ftp.storbinary.call_args[0][0]

        self.assertTrue(mock_open.called)
        mock_handler.write.assert_called_once_with(contents)
        self.assertTrue(storbinary_args.startswith('STOR foobar.gz'))
        self.assertEqual(backup.path + 'foobar.gz', created)

    @patch('flask_alchemydumps.backup.gzip.open')
    def test_read_file(self, mock_open):
        mock_handler = mock_open.return_value.__enter__.return_value

        backup = RemoteTools(self.mock_ftp)
        backup.read_file('foobar.gz')

        self.assertTrue(backup.ftp.retrbinary.called)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_handler.read.called)

    def test_delete_file(self):
        backup = RemoteTools(self.mock_ftp)
        backup.delete_file('foobar.gz')
        backup.ftp.delete.assert_called_once_with('foobar.gz')
