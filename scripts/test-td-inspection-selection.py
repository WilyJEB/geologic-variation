"""Focused offline selection checks only; no rendering or historical execution."""
from dataclasses import asdict, FrozenInstanceError
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


M = runpy.run_path(str(Path(__file__).with_name('td-inspection-selection.py')))
Owner = M['InspectionSelection']
CARD = M['_CARD']


class SelectionTests(unittest.TestCase):
    def test_exact_records_and_full_precision(self):
        owner = Owner()
        data = CARD['load']()
        for coordinates, height in zip(CARD['SITES'], (2090.142, -179.61244, -2250.709)):
            selected = owner.select(*coordinates)
            self.assertEqual(selected.state, 'selected')
            self.assertEqual(selected.coordinates, coordinates)
            self.assertEqual(asdict(selected.site), asdict(CARD['lookup'](*coordinates, data)))
            self.assertEqual(selected.site.elevation_metres, height)
            self.assertEqual(selected.site.interpretation, 'abstain')
            self.assertEqual(selected.site.pr59['token'], selected.site.pr59['deep_history'])

    def test_every_retained_site_and_closed_edges(self):
        owner = Owner()
        for row in range(49):
            for column in range(49):
                result = owner.select(2688 + 64*column, 10880 + 64*row)
                self.assertEqual(result.state, 'selected')
                self.assertEqual((result.site.row, result.site.column), (row, column))
                self.assertEqual(result.site.interpretation, 'abstain')

    def test_unsupported_replaces_selection_without_nearest_inference(self):
        owner = Owner()
        for coordinates, expected in (
            ((2689, 10880), 'gap'), ((5759, 13952), 'gap'),
            ((5761, 13953), 'exterior'), ((2687, 10880), 'exterior'),
            ((2688, 13953), 'exterior'), ((5761, 10880), 'exterior'),
            ((2688, 10879), 'exterior'), ((2624, 10880), 'exterior'),
        ):
            owner.select(*CARD['SITES'][0])
            result = owner.select(*coordinates)
            self.assertEqual(result.state, expected)
            self.assertEqual(result.coordinates, coordinates)
            self.assertIsNone(result.site)
            self.assertEqual(result, owner.selection)

    def test_invalid_requests_clear_previous_site(self):
        owner = Owner()
        for x, z in ((2688.0, 10880), (True, 10880), ('2688', 10880),
                     (2688, None), (2688, float('nan')), ([], {})):
            owner.select(*CARD['SITES'][0])
            self.assertEqual(owner.select(x, z), M['Selection']('invalid'))

    def test_reset_is_explicit_idempotent_and_clears_request(self):
        owner = Owner()
        self.assertEqual(owner.selection, M['Selection']('empty'))
        for coordinates in (*CARD['SITES'], *CARD['UNSUPPORTED']):
            owner.select(*coordinates)
            self.assertEqual(owner.reset(), M['Selection']('empty'))
            self.assertEqual(owner.reset(), owner.selection)
        self.assertEqual(owner.select(*CARD['SITES'][1]).state, 'selected')

    def test_independent_owners_and_defensive_snapshots(self):
        first, second = Owner(), Owner()
        snapshot = first.select(*CARD['SITES'][0])
        self.assertEqual(second.selection.state, 'empty')
        with self.assertRaises(FrozenInstanceError):
            snapshot.state = 'empty'
        snapshot.site.pr59['token'] = 'caller mutation'
        self.assertNotEqual(first.selection.site.pr59['token'], 'caller mutation')
        second.select(*CARD['SITES'][1])
        first.reset()
        self.assertEqual(second.selection.coordinates, CARD['SITES'][1])
        self.assertNotEqual(first.select(*CARD['SITES'][0]).site.pr59['token'], 'caller mutation')

    def test_missing_corrupt_inputs_fail_closed_and_lookup_error_clears(self):
        for error in (FileNotFoundError('missing'), ValueError('Archive mismatch')):
            with patch.dict(CARD, load=lambda: (_ for _ in ()).throw(error)):
                with self.assertRaises(type(error)):
                    Owner()
        blobs = {name: (CARD['ROOT']/f'docs/evidence/{name}.zip').read_bytes() for name in CARD['PINS']}
        for name in blobs:
            corrupt = dict(blobs)
            corrupt[name] += b'corrupt'
            with self.assertRaisesRegex(ValueError, 'Archive mismatch'):
                CARD['load'](corrupt)
            missing = dict(blobs)
            del missing[name]
            with self.assertRaises(KeyError):
                CARD['load'](missing)
        owner = Owner()
        owner.select(*CARD['SITES'][0])
        with patch.dict(CARD, lookup=lambda *args: (_ for _ in ()).throw(ValueError('bad record'))):
            with self.assertRaises(ValueError):
                owner.select(*CARD['SITES'][1])
        self.assertEqual(owner.selection, M['Selection']('invalid'))


if __name__ == '__main__':
    unittest.main()
