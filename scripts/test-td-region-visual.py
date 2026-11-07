"""Portable checks for the one frozen regional illustration; no inference."""
import copy
import json
from pathlib import Path
import runpy
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
B = runpy.run_path(str(ROOT/'scripts/build-td-region-visual.py'))


class RegionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT/'docs/evidence/td-region-visual.zip') as z:
            cls.members = {n: z.read(n) for n in z.namelist()}
        cls.raw = cls.members['input/visual-data.json']
        cls.result = json.loads(cls.members['result.json'])

    def test_portable_replay_and_repeatability(self):
        result = B['evaluate'](self.raw)
        self.assertEqual(B['encoded'](result), self.members['result.json'])
        self.assertEqual(B['encoded'](B['evaluate'](self.raw)), self.members['result.json'])
        self.assertEqual(B['viewer'](result), self.members['viewer.html'])
        self.assertEqual(self.members['viewer.html'], (ROOT/'docs/evidence/td-region-visual.html').read_bytes())
        manifest = json.loads((ROOT/'docs/evidence/td-region-visual.json').read_bytes())
        self.assertEqual(B['sha']((ROOT/'docs/evidence/td-region-visual.zip').read_bytes()), manifest['archive_sha256'])
        for name, digest in manifest['members'].items():
            self.assertEqual(B['sha'](self.members[name]), digest, name)
        image = json.loads(self.members['visual/td-region-visual-image.json'])
        self.assertEqual(image['result_sha256'], B['sha'](self.members['result.json']))
        self.assertEqual(image['png_sha256'], B['sha'](self.members['visual/td-region-visual.png']))
        self.assertEqual(image['renderer_sha256'], B['sha'](self.members['sources/scripts/render-td-region-visual.py']))
        with zipfile.ZipFile(ROOT/'docs/evidence/td-pressure-visual.zip') as z:
            self.assertEqual(z.read('visual-data.json'), self.raw)
            self.assertFalse(json.loads(z.read('result.json'))['reduction_passed'])

    def test_negative_coordinates_boundaries_and_neighbor_bounds(self):
        px, pz = B['phases']()
        for i in range(-5, 6):
            for j in range(-5, 6):
                x, z = px+i*2048, pz+j*2048
                self.assertEqual(B['region'](x, z), (i, j))
                self.assertEqual(B['region'](x-.25, z-.25), (i-1, j-1))
                n = B['neighborhood'](i, j)
                self.assertEqual(len(set(n)), 9)
                self.assertTrue(all(abs(a-i) <= 1 and abs(b-j) <= 1 for a, b in n))
                # Same exact half-open rule under an illustrative shear.
                self.assertEqual(B['region'](x+128, z, 128), (i, j))

    def test_order_independence_and_shared_history(self):
        d = self.result
        for r in reversed(range(49)):
            for c in reversed(range(49)):
                z, x = 10880+64*r, 2688+64*c
                w = B['warp'](z, d['rows'])
                self.assertEqual(list(B['region'](x, z, w)), d['terrain_illustration_ids'][r][c])
        for h in d['histories']:
            self.assertEqual(B['history'](*h['id']), h)
            # Surface and depth both use this single record; no depth RNG.
            self.assertEqual(B['history'](*h['id'])['token'], h['token'])
        self.assertEqual(B['warp'](10879, d['rows']), 0)
        self.assertEqual(B['warp'](13953, d['rows']), 0)

    def test_finite_bounds_and_computed_conceptual_separation(self):
        d = self.result
        self.assertEqual(d['retained_points'], 2401)
        self.assertEqual(d['missing_query_values'], 9440928)
        self.assertLessEqual(d['max_abs_displacement'], 256)
        self.assertEqual(d['rows'][0]['displacement'], 0)
        self.assertEqual(d['rows'][-1]['displacement'], 0)
        self.assertIsNone(d['observation_error'])
        self.assertFalse(d['confirmed_geometry'])
        self.assertFalse(d['production_selector'])
        self.assertFalse(d['gameplay_acceptance'])
        self.assertEqual(d['geological_interpretation'], 'abstain everywhere')
        self.assertEqual(sum(v is None for row in d['computed_descriptors']['max_four_neighbor_difference_metres'] for v in row), 192)
        self.assertEqual(d['support']['warp_max_heights'], 98)
        # Verify centroid from actual points, not old candidate/p5 metadata.
        h = json.loads(self.raw)['elevations'][24]
        weights = [v-min(h) for v in h]
        self.assertEqual(d['rows'][24]['centroid_x'], sum((2688+c*64)*w for c, w in enumerate(weights))/sum(weights))
        for name in ('seed_only_ids', 'terrain_illustration_ids'):
            self.assertEqual(B['topology'](d[name]), d['topology'][0 if name == 'seed_only_ids' else 1])

    def test_mutated_observation_is_rejected(self):
        d = json.loads(self.raw)
        d['elevations'][24][24] += 1
        with self.assertRaisesRegex(AssertionError, 'Immutable PR57'):
            B['evaluate'](B['encoded'](d))


if __name__ == '__main__':
    unittest.main()
