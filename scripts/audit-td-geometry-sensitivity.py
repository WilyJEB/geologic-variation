"""Offline perturbation sensitivity, not a tolerance or TD error bound."""
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
g=runpy.run_path(str(ROOT/'scripts/td-geometry-arc.py'))


def export():
    data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text());rows=[]
    for case in data['cases']:
        if case['scale']!=1:continue
        for attempt in case['attempts']:
            c=attempt['candidate'];origin=(c['col']*256+128,c['row']*256+128)
            runs=[]
            for amplitude in (0,-.1,.1):
                grid=[[v+amplitude*(-1)**(i+j) for j,v in enumerate(b['elevations'])] for i,b in enumerate(attempt['bands'])]
                result=g['track'](g['bilinear'](grid,origin[0]-1536,origin[1]-1536),origin,c['axis'],c['sign'])
                runs.append(dict(perturbation_metres=amplitude,supported=result['supported'],
                    stations=len(result['stations']),reasons=result['reasons'],
                    points=[p['point'] for p in result['stations']]))
            rows.append(dict(seed=case['seed'],kind=c['kind'],role='reused development',runs=runs))
    return dict(rows=rows,td_execution=False,confirmed_extrema=False,
        interpretation='Two checkerboard perturbations are sensitivity cases, not a worst-case bound, tolerance, or repaired strict equality')


if __name__=='__main__':
    (ROOT/'docs/evidence/td-geometry-sensitivity.json').write_text(json.dumps(export(),indent=2)+'\n')
