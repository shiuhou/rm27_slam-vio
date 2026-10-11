import unittest
import capture_guard as g
from unittest.mock import patch, MagicMock
import bench_io
import tempfile
from pathlib import Path

class GuardTests(unittest.TestCase):
    def test_download_path_local_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            target=str(Path(folder)/'test.ulg')
            self.assertEqual(g.download_temp_path(target),target+'.part')
            Path(target).touch()
            with self.assertRaises(FileExistsError): g.download_temp_path(target)

    def test_ftp_master_interface_and_dtr(self):
        port=MagicMock()
        with patch('bench_io.serial.Serial',return_value=port):
            link=bench_io.Link()
        self.assertEqual(link.source_system,254)
        self.assertEqual(link.source_component,190)
        self.assertFalse(port.dtr)
        self.assertFalse(port.rts)
        port.open.assert_called_once()

    def test_commands_are_logging_or_readonly_only(self):
        for c in ['logger stop', 'logger on', 'logger off',
                  'logger start -b 64 -t -r 2500', 'logger start -b 64 -t',
                  'logger status', 'commander status', 'sensors status']:
            g.check_command(c)
        for c in ['commander arm', 'param set COM_ARM_CHK 0', 'reboot',
                  'logger on; commander arm', 'logger trigger_watchdog']:
            with self.assertRaises(ValueError): g.check_command(c)

    def test_disarmed_and_fresh_required(self):
        g.check_heartbeat(29, 12, 1, 1, 2.0, 3.0)
        for args in [(157,12,1,1,2,3), (29,3,1,1,2,3),
                     (29,12,2,1,2,3), (29,12,1,1,2,9),
                     (29,12,1,1,None,3)]:
            with self.assertRaises(RuntimeError): g.check_heartbeat(*args)

    def test_mutations_only_exact_temporary_path(self):
        g.check_remote('put', '/fs/microsd/etc/logging/logger_topics.txt')
        g.check_remote('rm', '/fs/microsd/etc/logging/logger_topics.txt')
        g.check_remote('mkdir', '/fs/microsd/etc/logging')
        for path in ['/fs/microsd/log', '/', '/fs/microsd/etc/../parameters']:
            with self.assertRaises(ValueError): g.check_remote('rm',path)
        with self.assertRaises(ValueError): g.check_remote('put','/fs/microsd/test')

if __name__ == '__main__': unittest.main()
