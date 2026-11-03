"""Semantic geometry gates and portable evidence replay; no TD inference in CI."""
import copy
import json
from pathlib import Path
import runpy
import unittest

e=runpy.run_path(str(Path(__file__).with_name('summarize-td-landforms.py')));s=e['s']


class LandformTests(unittest.TestCase):
    def terrain(self,fn):
        return [{'row':t,'col':0,'elevations':[fn(x,z) for z in range(t-1,t+2) for x in (-1,0,1)]} for t in range(-2,3)]

    def test_true_ridge_basin_and_bounded_tilt(self):
        for sign in (1,-1):
            c={'axis':[0,1],'sign':sign}
            result=s['evaluate'](c,self.terrain(lambda x,z:-sign*200*x*x+30*z))
            self.assertTrue(result['supported']);self.assertEqual(result['minimum_prominence_or_depth_metres'],200)

    def test_curved_slope_is_not_extremum(self):
        c={'axis':[0,1],'sign':1}
        result=s['evaluate'](c,self.terrain(lambda x,z:500*x-100*x*x))
        self.assertFalse(result['supported'])

    def test_saddle_and_tilt_abstain(self):
        c={'axis':[0,1],'sign':1}
        for fn in (lambda x,z:-200*x*x+300*z*z,lambda x,z:-200*x*x+500*z):
            self.assertFalse(s['evaluate'](c,self.terrain(fn))['supported'])

    def test_failed_fallback_stays_failed(self):
        a={'kind':'ridge','evaluation':{'supported':False},'row':-1,'col':-1,'axis':[0,1]}
        self.assertEqual(s['choose']([a]),[a]);self.assertFalse(s['choose']([a])[0]['evaluation']['supported'])
        self.assertEqual(len(s['profile'](a)),15)

    def test_fine_disagreement_is_visible(self):
        c={'axis':[0,1],'sign':1}
        rows=[{'policies':{'target':{'matched_native_cell':{'mean_metres':200 if i%3==1 else 0}}},
               'target_fine_tile':{'mean_metres':i%3*100}} for i in range(15)]
        result=s['fine_evaluate'](c,rows)
        self.assertTrue(result['native_cell']['supported']);self.assertFalse(result['scaled_tile']['supported'])

    def test_portable_replay(self):
        path=e['ROOT']/'docs/evidence/td-landforms-2026-11-03.json'
        if not path.exists():self.skipTest('Runtime evidence not collected yet')
        data=json.loads(path.read_text());again=e['evaluate'](copy.deepcopy(data))
        self.assertEqual(data,again)
        bad=copy.deepcopy(data);bad['cases'][0]['attempts'][0]['evaluation']['supported']=not bad['cases'][0]['attempts'][0]['evaluation']['supported']
        with self.assertRaises(RuntimeError):e['evaluate'](bad)


if __name__=='__main__':unittest.main()
