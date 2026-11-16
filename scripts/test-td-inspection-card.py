"""New card data/layout checks only; no historical execution or runtime claims."""
from dataclasses import asdict
import io
import json
from pathlib import Path
import runpy
import unittest
from PIL import Image

B = runpy.run_path(str(Path(__file__).with_name('build-td-inspection-card.py')))


class Cards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = B['load']()
        cls.cards = [B['lookup'](x, z, cls.data) for x, z in B['SITES']]
        cls.outputs = B['build']()
        cls.record = json.loads(cls.outputs['td-inspection-card.json'])

    def test_exact_semantics_independent_of_rounding(self):
        s, baseline, d = self.data
        for card, expected in zip(self.cards, (2090.142, -179.61244, -2250.709)):
            self.assertEqual(card.elevation_metres, expected)
            self.assertEqual(card.elevation_metres, d['elevations'][card.row][card.column])
            self.assertEqual(card.pr59, next(h for h in s['histories'] if h['id'] == s['ids'][card.row][card.column][0]))
            self.assertEqual(card.pr58, next(h for h in baseline['histories'] if h['id'] == baseline['terrain_illustration_ids'][card.row][card.column]))
            self.assertEqual(card.pr59['token'], card.pr59['surface_history'])
            self.assertEqual(card.pr59['token'], card.pr59['deep_history'])
        self.assertEqual(self.record['cards'], [asdict(c) for c in self.cards])
        self.assertNotEqual(self.cards[1].elevation_metres, round(self.cards[1].elevation_metres, 3))
        self.assertEqual([c.pr59['observed_sites'] for c in self.cards], [196, 1458, 747])
        self.assertEqual([c.pr59['mean_contrast_metres'] for c in self.cards], [2693.8252599591056, -220.98168578350578, -275.49993718826454])

    def test_all_sites_and_unsupported_abstain(self):
        for r in range(49):
            for c in range(49):
                self.assertEqual(B['lookup'](2688+64*c, 10880+64*r, self.data).interpretation, 'abstain')
        for x,z in (*B['UNSUPPORTED'], (2624,10880), (2688,14016), (2688.0,10880)):
            self.assertIsNone(B['lookup'](x,z,self.data))
        self.assertEqual(self.record['unsupported'], [dict(x=x,z=z,observation=None) for x,z in B['UNSUPPORTED']])

    def test_corrupt_and_missing_inputs_fail_closed(self):
        blobs = {n:(B['ROOT']/f'docs/evidence/{n}.zip').read_bytes() for n in B['PINS']}
        for name in blobs:
            corrupt = dict(blobs)
            corrupt[name] += b'corruption'
            with self.assertRaisesRegex(ValueError, 'Archive mismatch'):
                B['load'](corrupt)
            missing = dict(blobs)
            del missing[name]
            with self.assertRaises(KeyError):
                B['load'](missing)

    def test_shared_event_distinct_identity_negative_finding(self):
        a,b = self.cards[1:]
        self.assertNotEqual(a.pr59['id'], b.pr59['id'])
        self.assertNotEqual(a.pr59['token'], b.pr59['token'])
        self.assertEqual(a.pr59['authored_event'], b.pr59['authored_event'])
        self.assertIn('no demonstrated geological necessity', self.record['comparison'])
        self.assertIn('did not establish better', self.record['comparison'])
        self.assertEqual(self.record['regional_summaries']['a'], -0.5)
        self.assertEqual(self.record['regional_summaries']['slope_ratio'], -1.007309667825724)
        self.assertTrue(self.record['regional_summaries']['clamp_active'])

    def test_bounds_caveat_reservation_no_overlap_and_pngs(self):
        for name, layout in self.record['images'].items():
            with Image.open(io.BytesIO(self.outputs[name])) as im:
                self.assertEqual(im.size, (layout['width'],layout['height']))
                self.assertEqual(im.format, 'PNG')
            self.assertEqual(layout['card_allocation'], [360,760])
            boxes = layout['text_boxes']
            for box in boxes:
                l,t,r,b = box['allocation']
                x0,y0,x1,y1 = box['bounds']
                self.assertTrue(l <= x0 <= x1 <= r and t <= y0 <= y1 <= b)
                self.assertGreaterEqual(box['size'],16)
                if box['role'] in ('section heading','body'):
                    self.assertLessEqual(y1,646)
                if box['role'].startswith('reserved caveat'):
                    self.assertGreaterEqual(y0,660)
            for i,a in enumerate(boxes):
                for b in boxes[i+1:]:
                    x0,y0,x1,y1 = a['bounds']
                    u0,v0,u1,v1 = b['bounds']
                    self.assertFalse(max(x0,u0)<min(x1,u1) and max(y0,v0)<min(y1,v1), (a,b))

    def test_glyph_and_overflow_rejection(self):
        raw = B['FONT'].read_bytes()
        B['glyphs_present'](raw, 'Observation: -0.5; invented history.')
        with self.assertRaisesRegex(ValueError, 'Missing font glyph'):
            B['glyphs_present'](raw, '\U0010ffff')
        with self.assertRaisesRegex(ValueError, 'Unbreakable'):
            B['wrap']('unbreakable', B['renderer']()[16], 1)

    def test_saved_outputs_match(self):
        for name, raw in self.outputs.items():
            self.assertEqual((B['ROOT']/'docs/evidence'/name).read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
