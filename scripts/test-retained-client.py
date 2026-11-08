"""Portable evidence checks, with corruptions that must fail. No client/TD startup."""
import copy
import io
import json
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
MODULE=runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))


class ClientEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=(ROOT/'docs/evidence/td-client-map.zip').read_bytes()
        cls.summary=json.loads((ROOT/'docs/evidence/td-client-map.json').read_text())
        assert MODULE['sha'](data)==cls.summary['archive_sha256']
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            cls.members={n:z.read(n) for n in z.namelist()}

    def test_exact_archive_and_runtime_audit(self):
        self.assertEqual({n:MODULE['sha'](b) for n,b in self.members.items()},self.summary['members'])
        result=MODULE['audit'](self.members)
        for n,v in result.items():self.assertEqual(v,self.summary[n])

    def test_forbidden_loaded_class_rejected(self):
        m=dict(self.members)
        m['raw/attempt-02/class-load.log']+=b'\nai.onnxruntime.OrtEnvironment\n'
        with self.assertRaises(AssertionError):MODULE['audit'](m)

    def test_changed_record_rejected(self):
        m=dict(self.members);m['raw/attempt-02/executed/retained-map.tsv']+=b'changed'
        with self.assertRaises(AssertionError):MODULE['audit'](m)

    def test_save_write_rejected(self):
        m=dict(self.members)
        name='raw/attempt-03/inventory.json'
        inv=json.loads(m[name]);inv['saves/unsafe/level.dat']={}
        m[name]=json.dumps(inv).encode()
        with self.assertRaises(AssertionError):MODULE['audit'](m)

    def test_missing_guard_rejected(self):
        m=dict(self.members);name='raw/attempt-03/logs/debug.log'
        m[name]=m[name].replace(b'Mixing SaveBarrier',b'Missing SaveBarrier')
        with self.assertRaises(AssertionError):MODULE['audit'](m)


if __name__=='__main__':unittest.main()
