"""Offline partial-client replay; no client or TD execution."""
import io
import json
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
E = runpy.run_path(str(ROOT/'scripts/export-navigation-supplement.py'))


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = (ROOT/'docs/evidence/td-navigation-supplement.zip').read_bytes()
        cls.summary = json.loads((ROOT/'docs/evidence/td-navigation-supplement.json').read_text())
        assert E['sha'](data) == cls.summary['archive_sha256']
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            cls.members = {n:z.read(n) for n in z.namelist()}

    def reject(self, name, data):
        m = dict(self.members)
        m[name] = data
        with self.assertRaises(AssertionError):
            E['audit'](m)

    def test_replay(self):
        self.assertEqual({n:E['sha'](b) for n,b in self.members.items()}, self.summary['members'])
        for n,v in E['audit'](self.members).items():
            self.assertEqual(v, self.summary[n])

    def test_forbidden_class(self):
        n = 'raw/attempt-01/class-load.log'
        self.reject(n, self.members[n]+b'ai.onnxruntime.OrtEnvironment')

    def test_floor_coordinates(self):
        n = 'raw/attempt-01/console.log'
        self.reject(n, self.members[n].replace(b'block 2922 13824', b'block 2923 13824'))

    def test_continuing_save(self):
        n = 'raw/attempt-01/inventory.json'
        v = json.loads(self.members[n]); v['saves/continuing/level.dat'] = {}
        self.reject(n, json.dumps(v).encode())

    def test_records(self):
        n = 'raw/attempt-01/executed/retained-map.tsv'
        self.reject(n, self.members[n]+b'changed')

    def test_guard(self):
        n = 'raw/attempt-01/logs/debug.log'
        self.reject(n, self.members[n].replace(b'Mixing Keys', b'Missing Keys'))

    def test_cleanup(self):
        n = 'raw/pid-cleanup.json'
        v = json.loads(self.members[n]); v['absent'] = False
        self.reject(n, json.dumps(v).encode())


if __name__ == '__main__':
    unittest.main()
