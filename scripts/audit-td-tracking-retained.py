"""Exact repeated-point audit against retained PR51; no tolerance substitution."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def audit(data):
    prior=json.loads((ROOT/'docs/evidence/td-landforms-2026-11-03.json').read_text())
    result=[]
    for c in data['cases']:
        old=next((p for p in prior['cases'] if (p['seed'],p['scale'])==(c['seed'],c['scale'])),None)
        if old is None:continue
        lookup={(p['x'],p['z']):p for p in old['observations']}
        for p in c['observations']:
            if (p['x'],p['z']) not in lookup:continue
            q=lookup[p['x'],p['z']]
            row=dict(seed=c['seed'],scale=c['scale'],x=p['x'],z=p['z'],
                province_equal=p['province']==q['province'],target_tile_equal=p['target_fine_tile']==q['target_fine_tile'],
                anchor_tile_equal=p['anchor_fine_tile']==q['anchor_fine_tile'],policies={})
            for name,value in p['policies'].items():
                oldvalue=q['policies'][name];a=value['matched_native_cell'];b=oldvalue['matched_native_cell']
                row['policies'][name]=dict(coarse_equal=value['coarse']==oldvalue['coarse'],
                    same_native_support=(a['row'],a['col'])==(b['row'],b['col']),
                    native_object_equal=a==b,hash_equal=a['float_sha256']==b['float_sha256'],
                    mean_absolute_difference_metres=abs(a['mean_metres']-b['mean_metres']),
                    relief_absolute_difference_metres=abs(a['fine_cell_relief_metres']-b['fine_cell_relief_metres']),
                    original_float_sha256=b['float_sha256'],current_float_sha256=a['float_sha256'])
            result.append(row)
    return dict(rows=result,exact_hashes_required=True,tolerance_used=False,
        interpretation='Separate cross-run comparison; small numeric differences do not count as exact matches or establish their cause')


if __name__=='__main__':
    data=json.loads((ROOT/'docs/evidence/td-tracking-negative.json').read_text())
    (ROOT/'docs/evidence/td-tracking-retained.json').write_text(json.dumps(audit(data),indent=2)+'\n')
