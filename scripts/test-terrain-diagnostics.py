"""Diagnostic classifier gates: mixed neighborhoods must not become rock labels."""
from pathlib import Path
import runpy
import unittest

classify = runpy.run_path(str(Path(__file__).with_name('summarize-terrain-diagnostics.py')))['classify']


class DiagnosticTests(unittest.TestCase):
    def test_signs_and_abstention(self):
        for values, expected in [([-1]*9,'ocean'), ([-1]+[100]*8,'coast'), ([0]*9,'land'),
                                 ([-1]*8+[0],'coast'), ([1]*9,'land')]:
            result = classify({'elevations':values,'p5_used':False})
            self.assertEqual(result['terrain_tendency'], expected)
            self.assertIsNone(result['stone_selection'])
            self.assertEqual(result['geological_confidence'], 'unestablished')
            self.assertGreater(len(result['synthetic_geological_hypotheses']), 1)

    def test_unavailable_or_p5_cannot_classify(self):
        for values, p5 in [([0]*8,False), ([float('nan')]*9,False),
                           ([float('inf')]*9,False), ([0]*9,True)]:
            with self.assertRaises(RuntimeError):
                classify({'elevations':values,'p5_used':p5})


if __name__ == '__main__': unittest.main()
