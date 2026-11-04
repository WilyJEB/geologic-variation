"""Analytical controls remain separate from actual TD coverage; portable replay."""
import copy
import json
from pathlib import Path
import runpy
import unittest

s=runpy.run_path(str(Path(__file__).with_name('td-tracking-selector.py')))
ROOT=Path(__file__).resolve().parents[1]


class TrackingTests(unittest.TestCase):
    candidate=dict(col=-16,row=-32,axis=[0,1],sign=1,kind='ridge')
    def run_field(self,fn,mode='tracked'):
        x0=self.candidate['col']*256+128;z0=self.candidate['row']*256+128
        return s['track'](self.candidate,lambda x,z:fn(x-x0,z-z0),mode)

    def test_two_sided_offcenter_and_tilt(self):
        for sign in (1,-1):
            c=dict(self.candidate,sign=sign)
            x0=c['col']*256+128;z0=c['row']*256+128
            fn=lambda x,z:-sign*.004*(x-x0-128)**2+.01*(z-z0)
            self.assertFalse(s['track'](c,fn,'straight')['supported'])
            self.assertTrue(s['track'](c,fn,'localized')['supported'])

    def test_slope_interruption_and_saddle_abstain(self):
        for fn in (lambda x,z:10*x-.004*x*x,lambda x,z:-.004*x*x+.01*z*z,
                   lambda x,z:-.004*x*x if abs(z)<200 else .004*x*x):
            self.assertFalse(self.run_field(fn)['supported'])

    def test_orientation_improves_geometry_without_hiding_ambiguity(self):
        result=self.run_field(lambda x,z:-.004*(x-z/2)**2)
        self.assertEqual(len(result['stations']),5)
        self.assertLessEqual(result['total_turn_degrees'],90)
        self.assertTrue(any(p['axis']!=[0,256] for p in result['stations']))

    def test_finite_grid_and_negative_coordinate_orientation(self):
        bands=[dict(col=-16,row=-32,band=i,full_float_sha256='control',elevations=[i*49+j for j in range(49)]) for i in range(49)]
        field=s['field'](bands)
        self.assertEqual(field(-16*256+128,-32*256+128),24*49+24)
        self.assertIsNone(field(1,1))

    def test_retained_development_failures_not_relabelled(self):
        prior=json.loads((ROOT/'docs/evidence/td-landforms-2026-11-03.json').read_text())
        checks=0
        for case in prior['cases']:
            for a in case['attempts']:
                self.assertEqual(a['evaluation'],s['legacy']['evaluate'](a,a['stations']))
                self.assertFalse(a['evaluation']['supported']);checks+=1
        self.assertEqual(checks,24)
        self.assertFalse(prior['coverage_gate']['passed'])
        self.assertFalse(prior['frozen_paired_scale_assertion']['passed'])

    def test_portable_replay_and_tampering(self):
        path=ROOT/'docs/evidence/td-tracking.json'
        if not path.exists():self.skipTest('No new TD collection yet')
        e=runpy.run_path(str(Path(__file__).with_name('summarize-td-tracking.py')))
        data=json.loads(path.read_text());self.assertEqual(data,e['evaluate'](copy.deepcopy(data)))
        bad=copy.deepcopy(data);bad['cases'][0]['attempts'][0]['diagnosis']['interpretation']='supported'
        with self.assertRaises(RuntimeError):e['evaluate'](bad)
        bad=copy.deepcopy(data);bad['cases'][0]['observations'][0]['delta']['pipeline_data_calls']+=1
        with self.assertRaises(RuntimeError):e['evaluate'](bad)


if __name__=='__main__':unittest.main()
