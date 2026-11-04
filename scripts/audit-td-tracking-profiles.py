"""Report every original fine-point station, including the tracker's stopped tails.

Descriptive audit using the frozen 50m/range/residual rules, no new acceptance gate.
"""
import json
import math
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
s=runpy.run_path(str(Path(__file__).with_name('td-tracking-selector.py')))


def audit(data):
    rows=[];corners=[]
    for case in data['cases']:
        if case['scale']!=1:continue
        for attempt in case['attempts']:
            c=attempt['candidate'];sample=s['field'](attempt['bands'])
            origin=(c['col']*256+128,c['row']*256+128);axis=[256*v for v in c['axis']]
            centers=[dict(point=[origin[i]+t*axis[i] for i in (0,1)]) for t in range(-2,3)]
            for center in centers:
                center['height']=sample(*center['point'])
                center['margins']=s['margins'](sample,center['point'],axis,c['sign'])
            original=s['continuity'](centers,[p['margins'] for p in centers])
            runs=attempt['diagnosis']['runs']
            compact=lambda p:{k:v for k,v in p.items() if k!='decisions'}
            rows.append(dict(seed=case['seed'],split=case['split'],kind=c['kind'],original_stations=centers,
                original_fine_point_strict=original,
                original_two_sided_stations=sum(min(p['margins'])>=50 for p in centers),
                localized_two_sided_stations=len(runs['localized']['stations']),
                tracked_two_sided_stations=len(runs['tracked']['stations']),
                frozen_original_straight_result=compact(runs['straight']),
                frozen_localized_result=compact(runs['localized']),frozen_tracked_result=compact(runs['tracked'])))
            for observation in case['observations']:
                for key in ('target_fine_tile','anchor_fine_tile'):
                    tile=observation[key];value=sample(tile['x0'],tile['z0'])
                    if value is None:continue
                    quantized=max(-32768,min(32767,math.floor(value)))
                    corners.append(dict(seed=case['seed'],kind=c['kind'],query=[observation['x'],observation['z']],
                        tile=key,native_corner=[tile['x0'],tile['z0']],patch_elevation_metres=value,
                        patch_quantized=quantized,tile_corner_height=tile['samples'][0],equal=quantized==tile['samples'][0]))
    return dict(rows=rows,tile_origin_corner_checks=corners,
        role='Descriptive full-station/corner audit, not a postinspection replacement acceptance rule',
        thresholds_changed=False,geological_selection='abstain')


if __name__=='__main__':
    data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())
    (ROOT/'docs/evidence/td-tracking-profiles.json').write_text(json.dumps(audit(data),indent=2)+'\n')
