"""Portable negative replay: the frozen exact-support assertion must still fail."""
import copy
import json
from pathlib import Path
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
n=runpy.run_path(str(Path(__file__).with_name('export-negative-td-tracking.py')))


class NegativeTrackingTests(unittest.TestCase):
    def test_preserved_rejection_and_complete_replay(self):
        data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())
        with self.assertRaisesRegex(RuntimeError,n['FAILURE']):n['f']['evaluate'](copy.deepcopy(data))
        self.assertEqual(data,n['evaluate'](copy.deepcopy(data)))
        self.assertFalse(data['frozen_matched_native_assertion']['passed'])
        self.assertFalse(data['decision']['tracked_morphology_coverage_passed'])
        self.assertEqual(len(data['frozen_matched_native_assertion']['mismatches']),3)
        self.assertEqual(data['frozen_matched_native_assertion']['distinct_native_cells'],2)
        self.assertEqual(sum(p['policies']['target']['matching_hashes'] for p in data['paired_support']),110)
        print('PRESERVED FAIL: frozen matching-native assertion; three rows / two cells; no tolerance')

    def test_other_failures_remain_fatal(self):
        data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())
        bad=copy.deepcopy(data);bad['cases'][0]['attempts'][0]['diagnosis']['interpretation']='supported'
        with self.assertRaisesRegex(RuntimeError,'Tracker drift'):n['evaluate'](bad)
        bad=copy.deepcopy(data);bad['cases'][0]['observations'][0]['delta']['pipeline_data_calls']+=1
        with self.assertRaises(RuntimeError):n['evaluate'](bad)


if __name__=='__main__':unittest.main()
