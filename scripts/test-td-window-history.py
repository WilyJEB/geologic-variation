"""Offline boundary, eviction and portable failure-preservation checks."""
import hashlib
import json
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
a = runpy.run_path(str(ROOT/'scripts/model-td-window-history.py'))


class WindowHistoryTests(unittest.TestCase):
    def test_signed_half_open_intersections(self):
        for start in (-257, -192, -64, -1, 0, 1, 192, 256):
            for size, stride in ((64,48), (64,32), (256,192)):
                bounds = (start,start,start+1,start+1)
                brute = [(i,j) for i in range(-12,12) for j in range(-12,12)
                         if i*stride <= start < i*stride+size and j*stride <= start < j*stride+size]
                self.assertEqual(a['windows'](bounds,size,stride),brute)

    def test_eviction_is_after_assembly_not_ensure(self):
        m = a['Model']()
        m.ensure('coarse', [(0,0,64,48000)])
        self.assertGreater(len(m.cache['coarse'])*7*64*64*4,a['LIMIT'])
        self.assertEqual(m.evictions,[])
        m.slice('coarse',(0,0,1,1))
        self.assertLessEqual(len(m.cache['coarse'])*7*64*64*4,a['LIMIT'])
        self.assertEqual(list(m.cache['coarse'])[-1],(0,0))

    def test_portable_replay(self):
        summary = json.loads((ROOT/'docs/evidence/td-window-history.json').read_text())
        raw = (ROOT/'docs/evidence/td-window-history.zip').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),summary['archive_sha256'])
        with zipfile.ZipFile(ROOT/'docs/evidence/td-window-history.zip') as z:
            for name,digest in summary['members'].items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
            actual = a['evaluate'](z.read)
            # Normalize tuple coordinates after JSON round trip.
            self.assertEqual(json.loads(json.dumps(actual)),json.loads(z.read('result.json')))
            self.assertFalse(actual['runtime_experiment_justified'])
            self.assertFalse(actual['historical_assertion_passed'])
            self.assertIsNone(actual['historical_indices_and_ulps'])
            self.assertEqual(len(actual['controls']),7)
            self.assertTrue(all(c['counter_gate'] for c in actual['controls']+actual['cases']))
            self.assertFalse(actual['reduction']['preserves_either_full_prefix_target_grouping'])
            # A changed counter cannot silently pass or continue the history.
            case = json.loads(z.read('reconstruction.json'))['cases'][0]
            first = next(e for e in case['events_through_last_target'] if 'delta' in e['result'])
            first['result']['delta']['computed_windows'] += 100000
            changed = a['replay'](case)
            self.assertFalse(changed['counter_gate'])
            self.assertTrue(changed['stopped_at_first_mismatch'])

    def test_scale6_padding_and_provider_hit(self):
        m = a['Model']()
        request = dict(ordinal=0,api='fetchHeightmap',bounds=[-25856,-512,-25600,-256])
        m.request(request,6)
        expected = a['Model']()
        expected.pipeline((-4312,-88,-4264,-40),True)
        self.assertEqual(m.count,expected.count)
        count=m.total; batches=len(m.batches)
        m.request(request,6)
        self.assertEqual((m.total,len(m.batches)),(count,batches))


if __name__ == '__main__':
    unittest.main()
