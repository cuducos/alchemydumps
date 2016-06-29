import os
from unittest import TestCase
from unittest.mock import patch

from flask_alchemydumps.helpers.backup import LocalTools


class TestLocalTools(TestCase):

    def setUp(self):
        current_dir = os.path.abspath(os.path.curdir)
        self.backup_dir = os.path.join(current_dir, 'foobar')

    @patch('flask_alchemydumps.helpers.backup.os.path.exists')
    @patch('flask_alchemydumps.helpers.backup.os.mkdir')
    def test_normalize_path(self, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        backup = LocalTools(self.backup_dir)
        self.assertTrue(self.backup_dir + os.sep, mock_mkdir.call_args[0][0])
        self.assertEqual(self.backup_dir + os.sep, backup.path)

    @patch('flask_alchemydumps.helpers.backup.os.path.exists')
    @patch('flask_alchemydumps.helpers.backup.os.mkdir')
    @patch('flask_alchemydumps.helpers.backup.os.listdir')
    @patch('flask_alchemydumps.helpers.backup.os.path.isfile')
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
        self.assertTrue(mock_listdir.called)
        self.assertEqual(4, mock_isfile.call_count)
        self.assertEqual(expected, files)

    @patch('flask_alchemydumps.helpers.backup.os.path.exists')
    @patch('flask_alchemydumps.helpers.backup.os.mkdir')
    @patch('flask_alchemydumps.helpers.backup.gzip.open')
    def test_create_file(self, mock_open, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        mock_handler = mock_open.return_value.__enter__.return_value

        contents = '42'.encode()
        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        created = backup.create_file('foobar.gz', contents)
        self.assertEqual(file_path, mock_open.call_args[0][0])
        self.assertEqual(contents, mock_handler.write.call_args[0][0])
        self.assertEqual(file_path, created)

    @patch('flask_alchemydumps.helpers.backup.os.path.exists')
    @patch('flask_alchemydumps.helpers.backup.os.mkdir')
    @patch('flask_alchemydumps.helpers.backup.gzip.open')
    def test_read_file(self, mock_open, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        mock_handler = mock_open.return_value.__enter__.return_value

        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        backup.read_file('foobar.gz')
        self.assertEqual(file_path, mock_open.call_args[0][0])
        self.assertTrue(mock_handler.read.called)

    @patch('flask_alchemydumps.helpers.backup.os.path.exists')
    @patch('flask_alchemydumps.helpers.backup.os.mkdir')
    @patch('flask_alchemydumps.helpers.backup.os.remove')
    def test_delete_file(self, mock_remove, mock_mkdir, mock_exists):
        mock_exists.return_value = False

        file_path = os.path.join(self.backup_dir, 'foobar.gz')

        backup = LocalTools(self.backup_dir)
        backup.delete_file('foobar.gz')
        self.assertEqual(file_path, mock_remove.call_args[0][0])
