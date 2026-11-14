"""Retained evidence and extracted pure method tests; no native helper import/calls."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class OfflineInvestigation(unittest.TestCase):
    def method(self, runner):
        tree = ast.parse((ROOT/'scripts/navigation-process.py').read_text())
        job = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        method = next(n for n in job.body if isinstance(n, ast.FunctionDef) and n.name == 'identities')
        module = ast.Module(body=[method], type_ignores=[])
        scope = dict(json=json, subprocess=SimpleNamespace(run=runner))
        exec(compile(module, '<extracted frozen identities method>', 'exec'), scope)
        return scope['identities']

    def test_exact_timeout_command_propagates_without_retry(self):
        runner = Mock(side_effect=subprocess.TimeoutExpired('mock only', 1))
        with self.assertRaises(subprocess.TimeoutExpired):
            self.method(runner)(None, [27824, 9140])
        runner.assert_called_once_with([
            'powershell.exe', '-NoProfile', '-Command',
            '$ids=@(27824,9140); Get-CimInstance Win32_Process | '
            'Where-Object { $ids -contains $_.ProcessId } | '
            'Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine,WorkingSetSize | ConvertTo-Json -Compress'
        ], capture_output=True, text=True, check=True, timeout=1, creationflags=0x08000000)

    def test_empty_pids_do_not_query(self):
        runner = Mock()
        self.assertEqual(self.method(runner)(None, []), [])
        runner.assert_not_called()

    def test_json_shapes_and_query_errors(self):
        for raw, expected in [('', []), ('{"ProcessId":1}', [dict(ProcessId=1)]),
                              ('[{"ProcessId":1}]', [dict(ProcessId=1)])]:
            self.assertEqual(self.method(Mock(return_value=SimpleNamespace(stdout=raw)))(None, [1]), expected)
        for error in [subprocess.CalledProcessError(1, 'mock'), OSError('mock denied')]:
            with self.subTest(error=error), self.assertRaises(type(error)):
                self.method(Mock(side_effect=error))(None, [1])
        with self.assertRaises(json.JSONDecodeError):
            self.method(Mock(return_value=SimpleNamespace(stdout='invalid')))(None, [1])

    def test_retained_sequence_and_frozen_bytes(self):
        archive = ROOT/'docs/evidence/td-navigation-3-runtime.zip'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         '52319ac3ab554e9d183b004792cc1d5b7a0328f7a1666ab8a50651a033f465a5')
        with zipfile.ZipFile(archive) as z:
            rows = [json.loads(s) for s in z.read('processes.jsonl').splitlines() if s.strip()]
            samples = [json.loads(s) for s in z.read('monitor.jsonl').splitlines() if s.strip()]
            ledger = json.loads(z.read('ledger.json'))
            cleanup = json.loads(z.read('cleanup.json'))
            self.assertEqual(len(rows), 4)
            self.assertEqual([r.get('job_pids') for r in rows], [None, [27824], [27824,9140], [27824,9140]])
            self.assertEqual(len(samples), 3)
            self.assertTrue(all(not s['has_position'] for s in samples))
            self.assertIn('$ids=@(27824,9140)', ledger['failure'])
            self.assertTrue(ledger['failure'].startswith('TimeoutExpired('))
            self.assertEqual(ledger['attempts_remaining'], 0)
            self.assertEqual(cleanup['identity_queries'], [])
            self.assertTrue(cleanup['forced'] and cleanup['job_empty'])
            self.assertEqual(cleanup['remaining_job_pids'], [])
            self.assertEqual(len(cleanup['checks']), 2)
            self.assertTrue(all(c['absent'] for c in cleanup['checks']))
            manifest = json.loads((ROOT/'docs/td-navigation-3-hashes.json').read_bytes())
            # These preserved user repairs are portable inputs, not tracked files.
            external = {'docs/td-region-viewer.html', 'scripts/build-td-region-preview.py'}
            with zipfile.ZipFile(ROOT/'docs/evidence/td-navigation-3-preparation.zip') as prepared:
                for name, digest in manifest['files'].items():
                    with self.subTest(name=name):
                        data = z.read('executed/'+name)
                        self.assertEqual(hashlib.sha256(data).hexdigest(), digest)
                        self.assertEqual(prepared.read(name), data)
                        if name not in external or (ROOT/name).exists():
                            self.assertEqual((ROOT/name).read_bytes(), data)

    def test_clean_checkout_without_external_viewer_repairs(self):
        external = {ROOT/'docs/td-region-viewer.html', ROOT/'scripts/build-td-region-preview.py'}
        original = Path.exists
        with patch.object(Path, 'exists', lambda p: False if p in external else original(p)):
            self.test_retained_sequence_and_frozen_bytes()


if __name__ == '__main__':
    unittest.main()
