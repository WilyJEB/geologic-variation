"""Semantic geometry gates and portable evidence replay; no TD inference in CI."""
import copy
import json
from pathlib import Path
import runpy
import unittest

frozen=runpy.run_path(str(Path(__file__).with_name('summarize-td-landforms.py')))
e=runpy.run_path(str(Path(__file__).with_name('export-negative-td-landforms.py')));s=e['s']


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

    def test_rotations_and_negative_centers(self):
        for dx,dz in s['ORIENTATIONS']:
            for sign in (1,-1):
                c={'axis':[dx,dz],'sign':sign,'row':-7,'col':-9}
                n=dx*dx+dz*dz
                def height(x,z):
                    x+=9;z+=7
                    return -sign*200*((-dz*x+dx*z)/n)**2+20*(dx*x+dz*z)/n
                rows=[{'elevations':[height(col+x,row+z) for z in (-1,0,1) for x in (-1,0,1)]}
                      for row,col in s['stations'](c)]
                self.assertTrue(s['evaluate'](c,rows)['supported'])

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
        data=json.loads(path.read_text());raw=copy.deepcopy(data)
        # Remove derived priors before replaying raw evidence equality.
        for case in raw['cases']:
            for row in case['observations']:row.pop('synthetic_geology',None)
            reverse_case=dict(case,observations=case['reverse'],
                before={k:0 for k in case['before']},
                after={k:sum(x['delta'][k] for x in case['reverse']) for k in case['before']},
                reverse_deltas=[x['delta'] for x in case['observations']])
            e['old']['validate_counts'](reverse_case)
        with self.assertRaisesRegex(RuntimeError,'Paired coarse drift'):
            frozen['evaluate'](copy.deepcopy(raw))
        again=e['evaluate'](raw)
        self.assertEqual(data,again)
        self.assertFalse(data['frozen_paired_scale_assertion']['passed'])
        self.assertFalse(data['coverage_gate']['passed'])
        self.assertEqual(len(data['frozen_paired_scale_assertion']['mismatches']),1)
        bad=copy.deepcopy(raw);bad['cases'][0]['attempts'][0]['evaluation']['supported']=not bad['cases'][0]['attempts'][0]['evaluation']['supported']
        with self.assertRaises(RuntimeError):e['evaluate'](bad)

    def test_screen_to_profile_coherence(self):
        path=e['ROOT']/'docs/evidence/td-landforms-2026-11-03.json'
        if not path.exists():self.skipTest('Runtime evidence not collected yet')
        for case in json.loads(path.read_text())['cases']:
            for i,candidate in enumerate(s['choose'](case['attempts'])):
                dx,dz=candidate['axis']
                for station_index,station in enumerate(candidate['stations']):
                    for side in (-1,0,1):
                        label=f'feature_{i}_{station_index*3+side+1}'
                        row=next(x for x in case['observations'] if label in x['groups'])
                        coarse=row['policies']['target']['coarse']
                        self.assertEqual(coarse['elevations'][4],station['elevations'][(1+side*dx)*3+1-side*dz])
                        if side==0:self.assertEqual(coarse['elevations'],station['elevations'])

    def test_primitive_tile_statistics(self):
        path=e['ROOT']/'docs/evidence/td-landforms-2026-11-03.json'
        if not path.exists():self.skipTest('Runtime evidence not collected yet')
        for case in json.loads(path.read_text())['cases']:
            for row in case['observations']+case['reverse']:
                for field in ('target_fine_tile','anchor_fine_tile'):
                    tile=row[field];values=tile['samples']
                    self.assertEqual(len(values),25)
                    self.assertEqual(tile['mean_metres'],sum(values)/25)
                    self.assertEqual(tile['fine_tile_relief_metres'],max(values)-min(values))

    def test_retained_known_points(self):
        path=e['ROOT']/'docs/evidence/td-landforms-2026-11-03.json'
        if not path.exists():self.skipTest('Runtime evidence not collected yet')
        prior=json.loads((e['ROOT']/'docs/evidence/sampling-support-2026-11-03.json').read_text())
        checks=0
        for case in json.loads(path.read_text())['cases']:
            old=next((x for x in prior['cases'] if (x['seed'],x['scale'])==(case['seed'],case['scale'])),None)
            if old is None:continue
            for row in case['observations']:
                previous=next((x for x in old['observations'] if (x['x'],x['z'])==(row['x'],row['z'])),None)
                if previous is None:continue
                checks+=1
                for key in ('province','policies','target_fine_tile','anchor_fine_tile'):
                    self.assertEqual(row[key],previous[key])
        self.assertEqual(checks,44)


if __name__=='__main__':unittest.main()
