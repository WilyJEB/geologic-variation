"""Semantic gates for support accounting, selection and geological abstention."""
from pathlib import Path
import runpy
import unittest

s=runpy.run_path(str(Path(__file__).with_name('summarize-sampling-support.py')))


class SamplingTests(unittest.TestCase):
    def test_prior_is_explicit_and_abstains(self):
        for label in ('ocean','coast','land'):
            a=s['prior'](-123,-3,4,label)
            self.assertEqual(a,s['prior'](-123,-3,4,label))
            self.assertEqual(sum(p['prior_weight'] for p in a['hypotheses']),1)
            self.assertIsNone(a['posterior']);self.assertIsNone(a['stone_selection'])
            self.assertEqual(a['geological_confidence'],'unestablished')
        orders={s['prior'](seed,-3,4,'land')['hypotheses'][0]['name'] for seed in range(20)}
        self.assertEqual(len(orders),2)

    def test_displacement_and_model_error_are_separate(self):
        row={'policies':{'target':{'matched_native_cell':{'mean_metres':10,'below_zero_fraction':0}},
                         'province_anchor':{'coarse':{'elevations':[0]*4+[-30]+[0]*4,'p5_used':False},
                                            'matched_native_cell':{'mean_metres':-20}}}}
        result=s['metrics']([row],'province_anchor')
        self.assertEqual(result['target_mean_absolute_error_metres'],40)
        self.assertEqual(result['matched_support_mean_absolute_error_metres'],10)
        self.assertEqual(result['central_sign_agreements'],0)

    def test_multiple_signed_boundaries(self):
        points=s['d']['boundary_points'](20261103,6)
        self.assertEqual(len(points),12)
        for a,b in zip(points[::2],points[1::2]):
            self.assertEqual(abs(a['x']-b['x'])+abs(a['z']-b['z']),1)
        self.assertTrue(any(p['x']<0 and p['z']<0 for p in points))

    def test_request_counts_reject_duplicated_misses(self):
        value={'coarse':{'row':0,'col':0,'elevations':[1]*9,'p5_used':False},
               'matched_native_cell':{'row':0,'col':0,'samples':65536,'mean_metres':1,'below_zero_fraction':0}}
        import copy
        policies={k:copy.deepcopy(value) for k in s['POLICIES']}
        # Fixed-grid representative is cell (2,2), shared target/anchor cell is (0,0).
        for kind in ('coarse','matched_native_cell'):
            policies['fixed_grid_4'][kind].update(row=2,col=2)
        delta={'coarse_calls':2,'pipeline_data_calls':4,'heightmap_calls':0,'computed_windows':5}
        row={'x':0,'z':0,'policies':policies,'delta':delta,'fine_cache_entries':2,
             'target_fine_tile':{'samples':[1]*25,'width_blocks':256},
             'anchor_fine_tile':{'samples':[1]*25,'width_blocks':256}}
        case={'scale':1,'observations':[row],'before':{k:0 for k in delta},'after':dict(delta),'reverse_deltas':[delta]}
        self.assertEqual(s['validate_counts'](case)['unique_native_cells'],2)
        row['delta']['coarse_calls']=3
        with self.assertRaisesRegex(RuntimeError,'dedup'):s['validate_counts'](case)

    def test_known_elongated_controls_are_signed_and_bounded(self):
        experiment=runpy.run_path(str(Path(__file__).with_name('sampling-reference-fields.py')))['experiment']()
        self.assertEqual(len(experiment['cases']),4)
        for case in experiment['cases']:
            self.assertEqual(len(case['observations']),45)
            self.assertEqual(max(case['sigma_native_pixels'])/min(case['sigma_native_pixels']),16)
            target=case['summary']['target']['mean_absolute_target_tile_error_metres']
            self.assertLess(target,case['summary']['fixed_grid_4']['mean_absolute_target_tile_error_metres'])
            self.assertLess(target,case['summary']['province_anchor']['mean_absolute_target_tile_error_metres'])

    def test_same_cell_coherence_ignores_query_coordinates(self):
        import copy
        value={'x':0,'z':0,'coarse':{'row':0,'col':0,'elevations':[1]*9},'matched_native_cell':{'mean_metres':1}}
        a={'policies':{name:copy.deepcopy(value) for name in s['POLICIES']}}
        b=copy.deepcopy(a)
        for v in b['policies'].values():v['x']=1
        result=s['coherence']([a,b]);self.assertTrue(result['target']['shared_cell_evidence_equal'])
        b['policies']['target']['coarse']['elevations'][4]=2
        with self.assertRaisesRegex(RuntimeError,'incoherent'):s['coherence']([a,b])

    def test_recommendation_requires_held_out_error_and_signs(self):
        import copy
        values={'target':{'target_mean_absolute_error_metres':2,'central_sign_agreements':5},
                'province_anchor':{'target_mean_absolute_error_metres':9,'central_sign_agreements':3},
                'fixed_grid_4':{'target_mean_absolute_error_metres':8,'central_sign_agreements':4}}
        data={'held_out':{group:{'policies':copy.deepcopy(values)} for group in ('coverage','selected_contrasts')}}
        self.assertEqual(s['recommend'](data)['policy'],'target')
        data['held_out']['selected_contrasts']['policies']['fixed_grid_4']['central_sign_agreements']=6
        self.assertEqual(s['recommend'](data)['policy'],'no supported winner')


if __name__=='__main__':unittest.main()
