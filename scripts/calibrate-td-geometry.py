"""Offline analytical controls and explicitly reused development fields."""
import hashlib
import json
import math
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
g=runpy.run_path(str(Path(__file__).with_name('td-geometry-arc.py')))


def export():
    controls=[]
    for degrees in (0,22.5,45,67.5,90):
        a=math.radians(degrees)
        for offset in (0,37):
            for sign in (1,-1):
                for shape in ('straight','curve','trend','slope','isolated','saddle','crossing','parallel','gap'):
                    def fn(x,z):
                        u=x*math.cos(a)+z*math.sin(a);v=-x*math.sin(a)+z*math.cos(a)-offset
                        ridge=-.004*v*v
                        if shape=='curve':ridge=-.004*(v-.0003*u*u)**2
                        if shape=='trend':ridge+=2*u
                        if shape=='slope':ridge=2*v
                        if shape=='isolated':ridge-=.004*u*u
                        if shape=='saddle':ridge+=.004*u*u
                        if shape=='crossing':ridge=-.004*min(v*v,u*u)
                        if shape=='parallel':ridge=-.004*min((v-192)**2,(v+192)**2)
                        if shape=='gap' and abs(u)>200:ridge=.004*v*v
                        return sign*ridge
                    values=[[fn(x,z) for x in range(-1536,1537,64)] for z in range(-1536,1537,64)]
                    sample=g['bilinear'](values,-1536,-1536)
                    result=g['track'](sample,(0,0),(math.cos(a),math.sin(a)),sign)
                    queried=[p for opts in result['decisions'] for p in opts]
                    points=[(p['point'][0]-p['axis'][1]*d,p['point'][1]+p['axis'][0]*d) for p in queried for d in (-256,0,256)]
                    error=max((abs(sample(*p)-fn(*p)) for p in points),default=0)
                    controls.append(dict(degrees=degrees,translation=offset,sign=sign,shape=shape,
                        supported=result['supported'],reasons=result['reasons'],stations=len(result['stations']),
                        interpolation_max_error_metres=error,
                        arc_residual_metres=result.get('arc_endpoint_residual_metres'),
                        legacy_height_range_passed=result.get('legacy_height_range_passed')))
    prior=ROOT/'docs/evidence/td-tracking-negative.json';data=json.loads(prior.read_text())
    retained=[]
    for case in data['cases']:
        if case['scale']!=1:continue
        for attempt in case['attempts']:
            c=attempt['candidate'];bands=attempt['bands'];origin=(c['col']*256+128,c['row']*256+128)
            sample=g['bilinear']([b['elevations'] for b in bands],origin[0]-1536,origin[1]-1536)
            result=g['track'](sample,origin,c['axis'],c['sign'])
            retained.append(dict(seed=case['seed'],role='reused development',kind=c['kind'],
                candidate=c,diagnosis=result,confirmed_extrema=False,coverage_passed=False,
                abstention='Unknown between-grid error; interpolated contrast alone is insufficient'))
    old=runpy.run_path(str(ROOT/'scripts/td-tracking-selector.py'))
    cardinal=old['track'](dict(col=0,row=0,axis=[0,1],sign=1),lambda x,z:-.004*(x-128)**2,'tracked')
    return dict(diagnostic='geometry-arc-1',controls=controls,retained=retained,
        old_cardinal_false_negative=cardinal,
        sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('scripts/td-geometry-arc.py','scripts/calibrate-td-geometry.py','docs/td-geometry-numerics-protocol.md','docs/evidence/td-tracking-negative.json')},
        td_launches=0,fresh_validation=False,geological_selection='abstain',
        gate='Unknown TD interpolation error and analytical confounders require stronger observed-extremum/axis identification before held-out execution')


if __name__=='__main__':
    (ROOT/'docs/evidence/td-geometry-arc.json').write_text(json.dumps(export(),indent=2)+'\n')
