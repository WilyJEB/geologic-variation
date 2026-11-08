"""Portable story-1 invariants and adversarial checks; no terrain execution."""
import json
from pathlib import Path
import random
import runpy
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
S=runpy.run_path(str(ROOT/'scripts/build-td-story.py'))


class StoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT/'docs/evidence/td-story.zip') as z:
            cls.m={n:z.read(n) for n in z.namelist()}
        cls.d=json.loads(cls.m['result.json'])
        cls.raw=cls.m['input/visual-data.json']
        cls.base=json.loads(cls.m['input/pr58-result.json'])

    def test_replay_and_portable_integrity(self):
        for _ in range(2):
            self.assertEqual(S['encoded'](S['evaluate'](self.raw,self.base)),self.m['result.json'])
        manifest=json.loads((ROOT/'docs/evidence/td-story.json').read_bytes())
        self.assertEqual(S['sha']((ROOT/'docs/evidence/td-story.zip').read_bytes()),manifest['archive_sha256'])
        for n,digest in manifest['members'].items(): self.assertEqual(S['sha'](self.m[n]),digest,n)
        S['export'](strict=True)
        with zipfile.ZipFile(ROOT/'docs/evidence/td-region-visual.zip') as z:
            self.assertEqual(z.read('result.json'),self.m['input/pr58-result.json'])
        with zipfile.ZipFile(ROOT/'docs/evidence/td-pressure-visual.zip') as z:
            self.assertFalse(json.loads(z.read('result.json'))['reduction_passed'])

    def test_traversal_and_actual_components(self):
        sites=[(r,c) for r in range(49) for c in range(49)]
        for order in (sites[::-1],random.Random(0).sample(sites,len(sites))):
            for r,c in order:
                self.assertEqual([S['region'](2688+64*c,10880+64*r,self.d['a'])],self.d['ids'][r][c])
        self.assertEqual(S['B']['topology'](self.d['ids']),self.d['topology'])
        self.assertTrue(all(v==1 for v in self.d['topology']['sample_components'].values()))

    def test_signed_ties_contacts_and_neighborhood(self):
        # Independent signed arithmetic expectations; test exact ties at z=0.
        for i in range(-100,101):
            x=S['PHASE']+2048*i
            self.assertEqual(S['region'](x,0,self.d['a']),i)
            self.assertEqual(S['region'](x-.25,0,self.d['a']),i-1)
            self.assertEqual(S['neighborhood'](i),[i-1,i,i+1])
            for z in (-13952,-64,64,13952):
                edge=S['contact'](i,z,self.d['a'])
                self.assertEqual(S['region'](edge-.01,z,self.d['a']),i-1)
                self.assertEqual(S['region'](edge+.01,z,self.d['a']),i)
        # Every observed adjacent transition crosses precisely one exported contact.
        for r in range(49):
            for c in range(48):
                i,j=self.d['ids'][r][c][0],self.d['ids'][r][c+1][0]
                if i!=j:
                    edge=S['contact'](j,10880+64*r,self.d['a'])
                    self.assertTrue(2688+64*c < edge <= 2688+64*(c+1))

    def test_shared_history_and_authored_event_support(self):
        h=json.loads(self.raw)['elevations']
        for v in self.d['histories']:
            i=v['id'];values=[h[r][c] for r in range(49) for c in range(49) if self.d['ids'][r][c]==[i]]
            self.assertEqual(v['surface_history'],v['deep_history'])
            self.assertEqual(v['token'],S['token'](f'history|{i}'))
            self.assertEqual(v['mean_contrast_metres'],sum(values)/len(values)-self.d['mean_elevation'])
            self.assertEqual(v['authored_event'],'greater stripping / exposure' if v['mean_contrast_metres']>0 else 'cover preservation' if v['mean_contrast_metres']<0 else 'unresolved')
        self.assertEqual(self.d['support']['heights'],2401)
        self.assertEqual(self.d['support']['regional_ids'],3)
        self.assertLessEqual(abs(self.d['a']),.5)
        self.assertIsNone(self.d['observation_error'])
        self.assertFalse(self.d['production_selector'])

    def test_corruption_and_script_free_viewer(self):
        changed=json.loads(self.raw);changed['elevations'][0][0]+=1
        with self.assertRaisesRegex(AssertionError,'Immutable'): S['evaluate'](S['encoded'](changed),self.base)
        base=dict(self.base);base['side']=7
        with self.assertRaisesRegex(AssertionError,'baseline'): S['evaluate'](self.raw,base)
        page=self.m['viewer.html'].decode().split('<script>')[0]
        self.assertEqual(page.count('<circle '),4802)
        self.assertEqual(page.count('<svg '),2)
        self.assertIn('Shared surface / deep meaning',page)
        self.assertIn('9440928',json.dumps(self.d))
        self.assertNotIn('src="http',page)


if __name__=='__main__': unittest.main()
