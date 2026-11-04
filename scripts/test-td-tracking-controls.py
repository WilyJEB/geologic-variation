"""Additional analytical ambiguity controls, never counted as actual TD coverage."""
from pathlib import Path
import runpy
import unittest

s=runpy.run_path(str(Path(__file__).with_name('td-tracking-selector.py')))


class AmbiguityControls(unittest.TestCase):
    def assess(self,fn,axis=(0,1),sign=1):
        c=dict(col=-7,row=-9,axis=list(axis),sign=sign)
        x0=c['col']*256+128;z0=c['row']*256+128
        return s['track'](c,lambda x,z:fn(x-x0,z-z0),'tracked')

    def test_unambiguous_diagonal_ridge_and_basin(self):
        for sign in (1,-1):
            result=self.assess(lambda x,z:-sign*.004*(x-z)**2,axis=(1,1),sign=sign)
            self.assertTrue(result['supported']);self.assertEqual(len(result['stations']),5)

    def test_parallel_alternatives_abstain(self):
        result=self.assess(lambda x,z:-.02*min((x-192)**2,(x+192)**2))
        self.assertFalse(result['supported'])
        self.assertTrue(any('alternative' in r for r in result['reasons']))

    def test_flat_and_search_edge_abstain(self):
        for fn in (lambda x,z:0,lambda x,z:-.004*(x-256)**2):
            self.assertFalse(self.assess(fn)['supported'])

    def test_cardinal_orientation_alias_remains_visible(self):
        # Unequal axis lengths can tie on transverse support. Do not retune this
        # conservative false negative into a claimed successful analytical control.
        result=self.assess(lambda x,z:-.004*x*x)
        self.assertFalse(result['supported'])
        self.assertTrue(any('alternative' in r for r in result['reasons']))


if __name__=='__main__':unittest.main()
