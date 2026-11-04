"""One frozen analytical validation; offline deterministic portable replay."""
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
a=runpy.run_path(str(Path(__file__).with_name('td-axis-confinement.py')))


def export():
    cases=[]
    for split,angles,translations in (
        ('development',(0,22.5,45,67.5,90),((0,0),(37,-19))),
        ('frozen analytical validation',(11,33,79,123),((-53,29),(101,-67)))):
        for angle in angles:
            for translation in translations:
                for sign in (1,-1):
                    for shape in a['FAMILIES']:
                        sample,axis=a['analytical'](shape,angle,translation,sign)
                        queries=[]
                        def observed(x,z):
                            h=sample(x,z);queries.append([x,z,h]);return h
                        result=a['track'](observed,translation,axis,sign)
                        positive=shape in a['POSITIVE']; decision=result['decision']
                        outcome=('success' if positive else 'false positive') if decision=='support' else (
                            ('false negative' if positive else 'correct rejection') if decision=='reject' else 'abstention')
                        cases.append(dict(split=split,shape=shape,degrees=angle,translation=translation,sign=sign,
                            intended_positive=positive,outcome=outcome,incomplete=len(result['path']['stations'])!=5,
                            result=result,exact_queries=queries))
    retained=[]
    old=json.loads((ROOT/'docs/evidence/td-geometry-arc.json').read_text())
    for row in old['retained']:
        retained.append(dict(seed=row['seed'],kind=row['kind'],role='reused development',
            descriptive=a['assess'](row['diagnosis']),confirmed_extrema=False,coverage_passed=False,
            decision='abstain',reason='Unknown TD interpolation error; no new fine support authorized'))
    summary=[]
    for split in sorted({c['split'] for c in cases}):
        for shape in a['FAMILIES']:
            rows=[c for c in cases if c['split']==split and c['shape']==shape]
            summary.append(dict(split=split,shape=shape,cases=len(rows),
                outcomes={k:sum(c['outcome']==k for c in rows) for k in
                    ('success','false positive','false negative','correct rejection','abstention')},
                incomplete=sum(c['incomplete'] for c in rows)))
    names=('scripts/td-axis-confinement.py','scripts/evaluate-td-axis.py','docs/td-axis-numerical-protocol.md',
           'docs/evidence/td-geometry-arc.json')
    return dict(diagnostic='axis-confinement-1',sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
        cases=cases,summary=summary,retained=retained,td_launches=0,fresh_td_validation=False,
        geological_selection='abstain',gate='Finite-support shallow saddles/closed extrema and unknown TD error remain')


if __name__=='__main__':
    (ROOT/'docs/evidence/td-axis-confinement.json').write_text(json.dumps(export(),indent=2)+'\n')
