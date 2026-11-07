"""Exact analytical/bit replay with corruption, bounds and failed-gate checks."""
import copy
import hashlib
import json
import math
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
e=runpy.run_path(str(ROOT/'scripts/evaluate-td-axis.py'))
n=runpy.run_path(str(ROOT/'scripts/export-td-identical.py'))


class BoundedTests(unittest.TestCase):
    def test_frozen_analytical_replay_and_limits(self):
        summary=json.loads((ROOT/'docs/evidence/td-axis-summary.json').read_text())
        archive=ROOT/'docs/evidence/td-axis-confinement.zip'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),summary['archive_sha256'])
        with zipfile.ZipFile(archive) as z:
            data=json.loads(z.read('analytical.json'))
            self.assertEqual(data,json.loads(json.dumps(e['export']())))
            for name,digest in data['sources'].items():
                self.assertEqual(hashlib.sha256(z.read('sources/'+name)).hexdigest(),digest)
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(len(data['cases']),540)
        self.assertEqual(sum(c['split']=='frozen analytical validation' for c in data['cases']),240)
        self.assertTrue(any(c['outcome']=='false positive' for c in data['cases']))
        self.assertTrue(any(c['outcome']=='false negative' for c in data['cases']))
        self.assertTrue(any(c['incomplete'] for c in data['cases']))
        for shape in ('isolated','saddle'):
            self.assertTrue(all(c['result']['decision']=='reject' for c in data['cases'] if c['shape']==shape))
        for case in data['cases']:
            path=case['result']['path'];distance=path.get('path_distances',[])
            for a,b in zip(distance,distance[1:]):self.assertAlmostEqual(b-a,256,places=8)
            self.assertTrue(all(math.isfinite(q[2]) for q in case['exact_queries']))
        # Trends pass new geometry while original height rules remain failed.
        self.assertTrue(any(c['shape']=='linear' and c['result']['decision']=='support' and
            not c['result']['path']['legacy_height_range_passed'] for c in data['cases']))
        self.assertTrue(all(r['decision']=='abstain' and not r['confirmed_extrema'] for r in data['retained']))

    def test_exact_numerical_replay_and_corruption(self):
        archive=ROOT/'docs/evidence/td-identical.zip'
        expected=json.loads((ROOT/'docs/evidence/td-identical.json').read_text())
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),expected.pop('archive_sha256'))
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(n['evaluate'](z.read),expected)
            self.assertEqual(expected['direct_requests'],26)
            self.assertEqual(expected['unique_native_supports'],2)
            def corrupt(name):
                raw=z.read(name)
                return bytes([raw[0]^1])+raw[1:] if name.endswith('.bin') else raw
            with self.assertRaises(AssertionError):n['evaluate'](corrupt)
            def wrong_bounds(name):
                if name!='results.json':return z.read(name)
                data=json.loads(z.read(name))
                ev=next(e for e in data['cases'][0]['events'] if 'file' in e['result'])
                ev['result']['requests'][0][0]+=1
                return json.dumps(data).encode()
            with self.assertRaises(AssertionError):n['evaluate'](wrong_bounds)


if __name__=='__main__':unittest.main()
