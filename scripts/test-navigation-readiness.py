"""Non-client readiness regression tests. No live sockets required in CI."""
from pathlib import Path
import runpy
import socket
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
M = runpy.run_path(str(ROOT/'scripts/launch-retained-navigation-supplement.py'))


class Readiness(unittest.TestCase):
    def test_failure_before_any_allocation(self):
        for check in (False, True):
            with tempfile.TemporaryDirectory(dir=ROOT) as directory:
                output = Path(directory)/'existing'
                output.mkdir()
                (output/'attempt-01').mkdir()
                (output/'ledger.json').write_bytes(b'frozen exhausted ledger')
                before = sorted(str(p.relative_to(output)) for p in output.rglob('*'))
                with patch.dict(M['main'].__globals__, OUTPUT=output), patch.object(
                        socket, 'socket', side_effect=PermissionError(10013, 'denied')):
                    with self.assertRaisesRegex(RuntimeError, 'no launch slot consumed'):
                        M['main'](check=check)
                self.assertEqual(before, sorted(str(p.relative_to(output)) for p in output.rglob('*')))
                self.assertEqual((output/'ledger.json').read_bytes(), b'frozen exhausted ledger')

    def test_timeouts_and_cleanup_on_connect_failure(self):
        from unittest.mock import MagicMock
        listener, client = MagicMock(), MagicMock()
        listener.__enter__.return_value = listener
        client.__enter__.return_value = client
        client.connect.side_effect = TimeoutError('bounded')
        with patch.object(socket, 'socket', side_effect=[listener, client]):
            with self.assertRaises(RuntimeError):
                M['check_loopback']()
        listener.bind.assert_called_once_with(('127.0.0.1', 0))
        for item in (listener, client):
            item.settimeout.assert_called_once_with(1.0)
            item.__exit__.assert_called_once()

    def test_success_closes_all_sockets(self):
        from unittest.mock import MagicMock
        listener, client, accepted = MagicMock(), MagicMock(), MagicMock()
        for item in (listener, client, accepted):
            item.__enter__.return_value = item
        listener.accept.return_value = (accepted, ('127.0.0.1', 12345))
        accepted.recv.return_value = b'R'
        with patch.object(socket, 'socket', side_effect=[listener, client]):
            M['check_loopback']()
        for item in (listener, client, accepted):
            item.settimeout.assert_called_once_with(1.0)
            item.__exit__.assert_called_once()

    def test_budget_still_exhausted(self):
        source = (ROOT/'scripts/launch-retained-navigation-supplement.py').read_text()
        self.assertIn("len(attempts) < 2", source)
        self.assertIn("sum(v.get('elapsed', 1200) for v in attempts) < 2400", source)


if __name__ == '__main__':
    unittest.main()
