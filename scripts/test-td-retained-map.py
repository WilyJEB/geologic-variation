"""Retained and coordinate-only checks; never launches TD."""
import math
from pathlib import Path
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
M=runpy.run_path(str(ROOT/'scripts/build-td-retained-map.py'))
B=runpy.run_path(str(ROOT/'scripts/build-td-region-visual.py'))
S=runpy.run_path(str(ROOT/'scripts/build-td-story.py'))


class RetainedMapTests(unittest.TestCase):
    def test_portable_exact_resource(self):
        M['export'](strict=True)
        rows=M['resource']().decode().splitlines()
        self.assertEqual(sum(r.startswith('P\t') for r in rows),2401)
        self.assertEqual(sum(r.startswith('H\t') for r in rows),7)
        self.assertEqual(sum(r.startswith('L\t') for r in rows),298)
        self.assertLess(len(M['resource']()),2*1024*1024)

    def test_coordinates_and_signed_chunk_edges(self):
        for scale in (1,6):
            for native in (-3073,-64,-16,-1,0,1,16,2688,5760,5761,10880,13952,13953):
                block=native*scale
                self.assertEqual(block/scale,native)
                chunk,local=divmod(block,16)
                self.assertTrue(0<=local<16)
                self.assertEqual(16*chunk+local,block)
            for edge in range(-32,33,16):
                for block in (edge-1,edge,edge+1):
                    self.assertEqual(math.floor((block/scale)*scale),block)
                    self.assertEqual(block//16,math.floor(block/16))
            self.assertEqual((5761-2688)*scale,3073*scale)
            self.assertEqual((13953-10880)*scale,3073*scale)

    def test_exact_ids_traversal_and_shared_history(self):
        obs,base,story=M['records']()
        points=[(r,c) for r in range(49) for c in range(49)]
        def check(order):
            out={}
            for r,c in order:
                x,z=2688+c*64,10880+r*64
                old=B['region'](x,z,B['warp'](z,base['rows']))
                new=S['region'](x,z,story['a'])
                self.assertEqual(list(old),base['terrain_illustration_ids'][r][c])
                self.assertEqual([new],story['ids'][r][c])
                for scale in (1,6):
                    self.assertEqual(S['region']((x*scale)/scale,(z*scale)/scale,story['a']),new)
                out[r,c]=(old,new)
            return out
        self.assertEqual(check(points),check(reversed(points)))
        for h in story['histories']:
            self.assertEqual(h['surface_history'],h['deep_history'])
            self.assertEqual(h['deep_history'],h['token'])
        for h in base['histories']:
            self.assertEqual(h,B['history'](*h['id']))

    def test_contacts_both_sides_and_exact_ties(self):
        obs,base,story=M['records']()
        for z in (10880,10944,12416,13952,-16,0):
            for i in (-3,-2,-1,0):
                x=S['contact'](i,z,story['a'])
                self.assertEqual(S['region'](x,z,story['a']),i)
                self.assertEqual(S['region'](x-.001,z,story['a']),i-1)
                for scale in (1,6):
                    self.assertEqual(S['region'](x*scale/scale,z*scale/scale,story['a']),i)
        for row in base['rows']:
            z=row['z']; w=row['displacement']
            for i in (0,1,2):
                x=base['phases'][0]+i*2048+w
                self.assertEqual(B['region'](x-.001,z,w)[0],i-1)
                self.assertEqual(B['region'](x+.001,z,w)[0],i)
        for j in (4,5,6):
            z=base['phases'][1]+j*2048
            self.assertEqual(B['region'](0,z)[1],j)
            self.assertEqual(B['region'](0,z-.001)[1],j-1)


if __name__=='__main__': unittest.main()
