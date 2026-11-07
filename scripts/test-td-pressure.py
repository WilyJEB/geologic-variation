"""Portable lineage replay, failed reduction preservation and negative checks."""
import io
import copy
import json
from pathlib import Path
import runpy
import unittest
from types import SimpleNamespace
import zipfile

ROOT=Path(__file__).resolve().parents[1]
a=runpy.run_path(str(ROOT/'scripts/analyze-td-pressure.py'))


class PressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z=zipfile.ZipFile(ROOT/'docs/evidence/td-pressure-visual.zip')

    @classmethod
    def tearDownClass(cls):
        cls.z.close()

    def test_manifest_and_exact_portable_replay(self):
        summary=json.loads((ROOT/'docs/evidence/td-pressure-visual.json').read_bytes())
        self.assertEqual(a['sha']((ROOT/'docs/evidence/td-pressure-visual.zip').read_bytes()),summary['archive_sha256'])
        for name,digest in summary['members'].items():
            self.assertEqual(a['sha'](self.z.read(name)),digest,name)
        with zipfile.ZipFile(io.BytesIO(self.z.read('inputs/td-window-history.zip'))) as old:
            result,traces=a['evaluate'](old.read)
        self.assertEqual(a['encoded'](result),self.z.read('result.json'))
        for name,raw in traces.items():
            self.assertEqual(raw,self.z.read(name),name)
        self.assertFalse(result['reduction_passed'])
        self.assertFalse(result['runtime_experiment_justified'])
        self.assertIsNone(result['historical_indices_and_ulps'])
        self.assertEqual([len(s['requests']) for s in result['selections']],[18,14])

    def test_corrupt_counter_stops_before_reduction(self):
        with zipfile.ZipFile(io.BytesIO(self.z.read('inputs/td-window-history.zip'))) as old:
            raw={n:old.read(n) for n in old.namelist()}
        case=json.loads(raw['reconstruction.json'])
        e=next(e for e in case['cases'][0]['events_through_last_target']
               if 'delta' in e['result'])
        e['result']['delta']['computed_windows']+=1
        raw['reconstruction.json']=a['encoded'](case)
        with self.assertRaisesRegex(AssertionError,'Frozen counter gate'):
            a['evaluate'](raw.__getitem__)

    def test_lineage_is_sensitive_to_group_members_not_only_size(self):
        one=a['Trace']();one.slice('init',(0,0,1,1))
        two=a['Trace']();two.slice('init',(0,32,1,33))
        self.assertEqual(one.total,two.total)
        common=lambda m:next(n for n in m.nodes if n['stage']=='init' and n['key']==(0,0))
        self.assertEqual(len(common(one)['batch']),len(common(two)['batch']))
        self.assertNotEqual(common(one)['batch'],common(two)['batch'])
        self.assertNotEqual(common(one)['fingerprint'],common(two)['fingerprint'])

    def test_visual_is_exact_retained_first_field(self):
        raw=self.z.read('inputs/td-tracking-negative.json')
        actual=a['visual_data'](raw)
        self.assertEqual(a['encoded'](actual),self.z.read('visual-data.json'))
        self.assertTrue(actual['abstained_everywhere'])
        self.assertFalse(actual['confirmed_geometry'])
        h=actual['elevations']; d=actual['max_four_neighbor_difference_metres']
        self.assertIsNone(d[0][24]);self.assertIsNone(d[24][-1])
        self.assertEqual(d[24][24],max(abs(h[24][24]-v) for v in
            (h[23][24],h[25][24],h[24][23],h[24][25])))
        image=json.loads(self.z.read('visual/td-pressure-visual-image.json'))
        self.assertEqual(a['sha'](self.z.read('visual/td-pressure-visual.png')),image['png_sha256'])
        self.assertEqual(a['sha'](self.z.read('visual-data.json')),image['visual_data_sha256'])
        self.assertEqual(a['sha'](self.z.read('sources/scripts/render-td-pressure-visual.py')),image['renderer_sha256'])
        self.assertEqual((ROOT/'docs/evidence/td-pressure-visual.png').read_bytes(),
                         self.z.read('visual/td-pressure-visual.png'))

    def test_access_order_change_fails_with_same_membership_and_counts(self):
        full=SimpleNamespace(**json.loads(self.z.read('6-full.json')))
        with zipfile.ZipFile(io.BytesIO(self.z.read('inputs/td-window-history.zip'))) as old:
            case=json.loads(old.read('reconstruction.json'))['cases'][1]
        self.assertTrue(a['compare'](full,full,case)['passed'])
        changed=copy.deepcopy(full)
        snapshot=next(c['before_target'] for c in changed.checkpoints if c['ordinal']==322)
        entries=snapshot['init']
        left=next(i for i,e in enumerate(entries) if e['key']==[-16,-8])
        right=next(i for i,e in enumerate(entries) if e['key']==[-16,-7])
        entries[left],entries[right]=entries[right],entries[left]
        self.assertEqual(full.total,changed.total)
        outcome=a['compare'](full,changed,case)['target_comparisons'][0]['checks']
        self.assertFalse(outcome['relevant_membership_access_order'])
        self.assertTrue(outcome['target_batch_membership'])
        self.assertTrue(outcome['target_dependency_creation_ancestry'])


if __name__=='__main__':
    unittest.main()
