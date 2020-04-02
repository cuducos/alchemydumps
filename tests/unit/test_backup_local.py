import os
from unittest import TestCase

from flask_alchemydumps.helper.backup import LocalTools


# Python 2 and 3 compatibility (mock)
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestLocalTools(TestCase):

    def setUp(self):
        current_dir = os.path.abspath(os.path.curdir)
        self.backup_dir = os.path.join(current_dir, 'foobar')

    @patch('flask_alchemydumps.backup.os.path.exists')
    @patch('flask_alchemydumps.backup.os.mkdir')
    def test_normalize_path(self, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        backup = LocalTools(self.backup_dir)
        mock_mkdir.assert_called_once_with(self.backup_dir)
        self.assertEqual(self.backup_dir + os.sep, backup.path)

    @patch('flask_alchemydumps.backup.os.path.exists')
    @patch('flask_alchemydumps.backup.os.mkdir')
    @patch('flask_alchemydumps.backup.os.listdir')
    @patch('flask_alchemydumps.backup.os.path.isfile')
    def test_get_files(self, mock_isfile, mock_listdir, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        files = (
            'BRA-19940704123000-USA.gz',
            'BRA-19940709163000-NED.gz',
            'BRA-19940713123XXX-SWE.gz',
            'BRA-19940717123000-ITA.gz',
        )
        mock_listdir.return_value = iter(files)
        mock_isfile.side_effect = (True, True, True, False)
        backup = LocalTools(self.backup_dir)
        files = tuple(backup.get_files())
        expected = (
            'BRA-19940704123000-USA.gz',
            'BRA-19940709163000-NED.gz',
        )
        mock_listdir.assert_called_once_with(backup.path)
        self.assertEqual(4, mock_isfile.call_count)
        self.assertEqual(expected, files)

    @patch('flask_alchemydumps.backup.os.path.exists')
    @patch('flask_alchemydumps.backup.os.mkdir')
    @patch('flask_alchemydumps.backup.gzip.open')
    def test_create_file(self, mock_open, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        mock_handler = mock_open.return_value.__enter__.return_value

        contents = '42'.encode()
        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        created = backup.create_file('foobar.gz', contents)
        mock_open.assert_called_once_with(file_path, 'wb')
        mock_handler.write.assert_called_once_with(contents)
        self.assertEqual(file_path, created)

    @patch('flask_alchemydumps.backup.os.path.exists')
    @patch('flask_alchemydumps.backup.os.mkdir')
    @patch('flask_alchemydumps.backup.gzip.open')
    def test_read_file(self, mock_open, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        mock_handler = mock_open.return_value.__enter__.return_value

        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        backup.read_file('foobar.gz')
        mock_open.assert_called_once_with(file_path, 'rb')
        mock_handler.read.assert_called_once_with()

    @patch('flask_alchemydumps.backup.os.path.exists')
    @patch('flask_alchemydumps.backup.os.mkdir')
    @patch('flask_alchemydumps.backup.os.remove')
    def test_delete_file(self, mock_remove, mock_mkdir, mock_exists):
        mock_exists.return_value = False

        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        backup.delete_file('foobar.gz')
        mock_remove.assert_called_once_with(file_path)
