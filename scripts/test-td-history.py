"""Portable prefix replay, corruption rejection and analytical alias checks."""
import hashlib
import json
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
a=runpy.run_path(str(ROOT/'scripts/audit-td-history.py'))


class HistoryTests(unittest.TestCase):
    def test_portable_replay(self):
        summary=json.loads((ROOT/'docs/evidence/td-observation-history.json').read_text())
        path=ROOT/'docs/evidence/td-observation-history.zip'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),summary['archive_sha256'])
        with zipfile.ZipFile(path) as z:
            for name,digest in summary['members'].items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
            result=a['evaluate'](z.read)
            self.assertEqual(result,json.loads(z.read('reconstruction.json')))
            self.assertEqual([c['targets'][0]['ordinal'] for c in result['cases']],[326,322])
            self.assertFalse(result['historical_assertion_passed'])
            self.assertIsNone(result['historical_indices_and_ulps'])
            def corrupt(name):
                raw=z.read(name)
                if name=='pr52-results.json':
                    data=json.loads(raw)
                    case=next(c for c in data['cases'] if c['seed']==-2026110411 and c['scale']==1)
                    event=next(e for e in case['events'] if e['command'].startswith('acceptance sampling-compare '))
                    event['result']['delta']['pipeline_data_calls']+=1
                    return json.dumps(data).encode()
                return raw
            with self.assertRaises(AssertionError): a['evaluate'](corrupt)

    def test_nonlinear_trend_is_translated_saddle(self):
        # Existing strong_nonlinear family: exact completion of the square.
        for u in (-512,-256,0,256,512):
            for v in (-256,0,256):
                original=.004*u*u+2*u-.004*v*v
                translated=.004*(u+250)**2-.004*v*v-250
                self.assertAlmostEqual(original,translated,places=10)
        # Shallow saddles/elongated extrema have identical absolute curvature ratio.
        self.assertEqual(abs(.0002)/.004,.05)


if __name__=='__main__': unittest.main()
