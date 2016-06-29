from ftplib import error_perm
from unittest import TestCase

from flask_alchemydumps.helpers.backup import Backup

# Python 2 and 3 compatibility (mock)
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestBackup(TestCase):

    FILES = (
        'BRA-19940704123000-USA.gz',
        'BRA-19940709163000-NED.gz',
        'BRA-19940713123000-SWE.gz',
        'BRA-19940717123000-ITA.gz',
    )

    @patch('flask_alchemydumps.helpers.backup.LocalTools')
    @patch('flask_alchemydumps.helpers.backup.decouple.config')
    def setUp(self, mock_config, mock_backup):
        # (respectively: FTP server, FTP # user, FTP password, FTP path, local
        # directory for backups and file prefix)
        mock_config.side_effect = (None, None, None, None, 'foobar', 'BRA')
        self.backup = Backup()
        self.backup.files = self.FILES

    def test_get_timestamps(self):
        expected = [
            '19940704123000',
            '19940709163000',
            '19940713123000',
            '19940717123000'
        ]
        self.assertEqual(expected, self.backup.get_timestamps())

    def test_by_timestamp(self):
        expected = ['BRA-19940717123000-ITA.gz']
        self.assertEqual(expected, list(self.backup.by_timestamp('19940717123000')))

    def test_valid(self):
        self.assertTrue(self.backup.valid('19940704123000'))
        self.assertFalse(self.backup.valid('19980712210000'))

    def test_get_name(self):
        expected = 'BRA-{}-GER.gz'.format(self.backup.target.TIMESTAMP)
        self.assertEqual(expected, self.backup.get_name('GER'))


class TestBackupFTPAttemps(TestCase):

    # decouple.config mock side effects (respectively: FTP server, FTP
    # user, FTP password, FTP path, local directory for backups and file prefix
    CONFIG = ('server', 'user', None, 'foobar', 'foobar', 'bkp')

    @patch('flask_alchemydumps.helpers.backup.ftplib.FTP')
    @patch('flask_alchemydumps.helpers.backup.decouple.config')
    def test_successful_connection(self, mock_config, mock_ftp):
        mock_config.side_effect = self.CONFIG
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '250 foobar'

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        self.assertTrue(mock_ftp.called)
        self.assertTrue(mock_ftp.return_value.cwd.called)
        self.assertTrue(backup.ftp)

    @patch('flask_alchemydumps.helpers.backup.LocalTools')
    @patch('flask_alchemydumps.helpers.backup.ftplib.FTP')
    @patch('flask_alchemydumps.helpers.backup.decouple.config')
    def test_unsuccessful_connection(self, mock_config, mock_ftp, mock_local):
        mock_config.side_effect = self.CONFIG
        mock_ftp.side_effect = error_perm

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        self.assertTrue(mock_ftp.called)
        self.assertFalse(mock_ftp.return_value.cwd.called)
        self.assertFalse(backup.ftp)

    @patch('flask_alchemydumps.helpers.backup.LocalTools')
    @patch('flask_alchemydumps.helpers.backup.ftplib.FTP')
    @patch('flask_alchemydumps.helpers.backup.decouple.config')
    def test_ftp_with_wrong_path(self, mock_config, mock_ftp, mock_local):
        mock_config.side_effect = self.CONFIG
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '404 foobar'

        backup = Backup()

        self.assertEqual(6, mock_config.call_count)
        self.assertTrue(mock_ftp.called)
        self.assertTrue(mock_ftp.return_value.cwd.called)
        self.assertFalse(backup.ftp)

    @patch('flask_alchemydumps.helpers.backup.ftplib.FTP')
    @patch('flask_alchemydumps.helpers.backup.decouple.config')
    def test_close_connection(self, mock_config, mock_ftp):
        mock_config.side_effect = self.CONFIG
        mock_ftp.return_value = MagicMock()
        mock_ftp.return_value.cwd.return_value = '250 foobar'

        backup = Backup()
        backup.close_ftp()

        self.assertEqual(6, mock_config.call_count)
        self.assertTrue(mock_ftp.called)
        self.assertTrue(mock_ftp.return_value.quit.called)
