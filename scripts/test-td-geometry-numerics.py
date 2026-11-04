"""Portable calibration, exact bit comparison, and failure-preservation checks."""
import copy
import json
from pathlib import Path
import runpy
import struct
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
c=runpy.run_path(str(ROOT/'scripts/calibrate-td-geometry.py'))
n=runpy.run_path(str(ROOT/'scripts/export-td-numerics.py'))


class CalibrationTests(unittest.TestCase):
    def test_calibration_replay_and_visible_confounders(self):
        data=json.loads((ROOT/'docs/evidence/td-geometry-arc.json').read_text())
        self.assertEqual(data,json.loads(json.dumps(c['export']())))
        self.assertFalse(data['old_cardinal_false_negative']['supported'])
        controls=data['controls']
        self.assertEqual(len(controls),180)
        for shape in ('straight','curve','trend'):
            self.assertTrue(all(x['supported'] for x in controls if x['shape']==shape))
        for shape in ('slope','crossing','parallel','gap'):
            self.assertFalse(any(x['supported'] for x in controls if x['shape']==shape))
        # These failures of discrimination are the reason fresh validation is gated.
        self.assertTrue(any(x['supported'] for x in controls if x['shape']=='isolated'))
        self.assertTrue(all(x['supported'] for x in controls if x['shape']=='saddle'))
        self.assertFalse(any(x['coverage_passed'] for x in data['retained']))
        for row in data['retained']:
            distances=row['diagnosis'].get('path_distances',[])
            for a,b in zip(distances,distances[1:]):self.assertAlmostEqual(b-a,256,places=8)

    def test_ulp_bits_and_quantization_are_separate(self):
        pack=lambda *v:b''.join(struct.pack('>I',x) for x in v)
        result=n['compare'](pack(0x3f800000,0xbf800000),pack(0x3f800001,0xbf800001))
        self.assertEqual(result['maximum_ulp_difference'],1)
        self.assertEqual(result['differing_indices'],[0,1])
        self.assertEqual(result['quantized_differing_indices'],[1])

    def test_sensitivity_replay(self):
        audit=runpy.run_path(str(ROOT/'scripts/audit-td-geometry-sensitivity.py'))
        data=json.loads((ROOT/'docs/evidence/td-geometry-sensitivity.json').read_text())
        self.assertEqual(data,json.loads(json.dumps(audit['export']())))

    def test_portable_bit_replay_and_corruption(self):
        archive=ROOT/'docs/evidence/td-numerics.zip'
        data=json.loads((ROOT/'docs/evidence/td-numerics.json').read_text())
        self.assertEqual(n['sha'](archive.read_bytes()),data.pop('portable_archive_sha256'))
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(n['evaluate'](z.read),data)
            self.assertTrue(all(r['versus_first_same_mode']['exact_equal'] for r in data['comparisons']))
            self.assertTrue(any(not r['versus_first_same_process']['exact_equal'] for r in data['comparisons']))
            def corrupt(name):
                raw=z.read(name)
                return bytes([raw[0]^1])+raw[1:] if name.endswith('.bin') else raw
            with self.assertRaises(AssertionError):n['evaluate'](corrupt)


if __name__=='__main__':unittest.main()
