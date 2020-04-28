from ftplib import error_perm
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask_alchemydumps.backup import Backup


class TestBackup(TestCase):

    FILES = (
        'BRA-19940704123000-USA.gz',
        'BRA-19940709163000-NED.gz',
        'BRA-19940713123000-SWE.gz',
        'BRA-19940717123000-ITA.gz',
    )

    @patch('flask_alchemydumps.backup.decouple.config')
    def setUp(self, mock_config):
        self.tmp = TemporaryDirectory()

        # Respectively: FTP server, FTP user, FTP password, FTP path, local
        # directory for backups and file prefix
        mock_config.side_effect = (None, None, None, None, self.tmp.name, 'BRA')

        # main objects
        self.backup = Backup()
        self.backup.files = tuple(self.files)

    def tearDown(self):
        self.tmp.cleanup()

    @property
    def files(self):
        for name in self.FILES:
            yield Path(self.tmp.name) / name

    def test_get_timestamps(self):
        self.assertEqual(
            sorted((
                '19940704123000',
                '19940709163000',
                '19940713123000',
                '19940717123000'
            )),
            sorted(self.backup.get_timestamps())
        )

    def test_by_timestamp(self):
        self.assertEqual(
            (Path(self.tmp.name) / 'BRA-19940717123000-ITA.gz',),
            tuple(self.backup.by_timestamp('19940717123000'))
        )

    def test_valid(self):
        self.assertTrue(self.backup.valid('19940704123000'))
        self.assertFalse(self.backup.valid('19980712210000'))

    def test_get_name(self):
        self.assertEqual(
            f'BRA-{self.backup.target.TIMESTAMP}-GER.gz',
            self.backup.get_name('GER')
        )


class TestBackupFTPAttemps(TestCase):

    def setUp(self):
        self.tmp = TemporaryDirectory()

        # Respectively: FTP server, FTP user, FTP password, FTP path, local
        # directory for backups and file prefix
        self.config = ('server', 'user', None, 'foobar', self.tmp.name, 'bkp')

    def tearDown(self):
        self.tmp.cleanup()

    @patch('flask_alchemydumps.backup.ftplib.FTP')
    @patch('flask_alchemydumps.backup.decouple.config')
    def test_successful_connection(self, mock_config, mock_ftp):
        mock_config.side_effect = self.config
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '250 foobar'

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        mock_ftp.assert_called_once_with('server', 'user', None)
        mock_ftp.return_value.cwd.assert_called_once_with('foobar')
        self.assertTrue(backup.ftp)

    @patch('flask_alchemydumps.backup.ftplib.FTP')
    @patch('flask_alchemydumps.backup.decouple.config')
    def test_unsuccessful_connection(self, mock_config, mock_ftp):
        mock_config.side_effect = self.config
        mock_ftp.side_effect = error_perm

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        mock_ftp.assert_called_once_with('server', 'user', None)
        self.assertFalse(mock_ftp.return_value.cwd.called)
        self.assertFalse(backup.ftp)

    @patch('flask_alchemydumps.backup.ftplib.FTP')
    @patch('flask_alchemydumps.backup.decouple.config')
    def test_ftp_with_wrong_path(self, mock_config, mock_ftp):
        mock_config.side_effect = self.config
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '404 foobar'

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        mock_ftp.assert_called_once_with('server', 'user', None)
        mock_ftp.return_value.cwd.assert_called_once_with('foobar')
        self.assertFalse(backup.ftp)

    @patch('flask_alchemydumps.backup.ftplib.FTP')
    @patch('flask_alchemydumps.backup.decouple.config')
    def test_close_connection(self, mock_config, mock_ftp):
        mock_config.side_effect = self.config
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '250 foobar'

        backup = Backup()
        backup.close_ftp()

        self.assertEqual(6, mock_config.call_count)
        mock_ftp.assert_called_once_with('server', 'user', None)
        mock_ftp.return_value.quit.called_once_with()
