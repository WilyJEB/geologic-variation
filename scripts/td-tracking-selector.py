"""Bounded diagnostic tracking. Frozen independently of geology-1 and PR51 criteria."""
import math
import runpy
from pathlib import Path

legacy=runpy.run_path(str(Path(__file__).with_name('td-landform-selector.py')))
SEEDS=[(8675309,'development'),(2026110407,'held_out'),(-2026110411,'held_out')]
# Native pixels. Eight undirected orientations, integer offsets on the 64px grid.
AXES=[(256,0),(256,128),(256,256),(128,256),(0,256),(-128,256),(-256,256),(-256,128)]
MARGIN=50.0


def angle(a,b):
    return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))/math.hypot(*a)/math.hypot(*b)))))


def seeds(scan):
    result=[]
    for kind in ('ridge','basin'):
        options=[c for c in legacy['candidates'](scan) if c['kind']==kind]
        if options:result.append(options[0])
    return result


def field(bands):
    assert len(bands)==49 and [b['band'] for b in bands]==list(range(49))
    c=bands[0];x0=c['col']*256+128-1536;z0=c['row']*256+128-1536
    values=[b['elevations'] for b in bands]
    assert all(len(v)==49 for v in values) and all(math.isfinite(v) for r in values for v in r)
    assert all((b['col'],b['row'],b['full_float_sha256'])==(c['col'],c['row'],c['full_float_sha256']) for b in bands)
    def sample(x,z):
        # Only exact sampled points are used; no interpolation or hidden smoothing.
        if (x-x0)%64 or (z-z0)%64 or not (0<=x-x0<=3072 and 0<=z-z0<=3072):return None
        return values[(z-z0)//64][(x-x0)//64]
    return sample


def margins(sample,p,axis,sign):
    x,z=p;dx,dz=axis;v=[sample(x-dz,z+dx),sample(x,z),sample(x+dz,z-dx)]
    if any(x is None for x in v):return None
    return [sign*(v[1]-v[0]),sign*(v[1]-v[2])]


def continuity(centers,pairs):
    values=[p['height'] for p in centers];minimum=min(v for pair in pairs for v in pair)
    residual=max(abs(v-(values[0]+i*(values[-1]-values[0])/4)) for i,v in enumerate(values)) if len(values)==5 else None
    reasons=[]
    if len(values)!=5:reasons.append('incomplete finite path')
    if minimum<MARGIN:reasons.append('two-sided extremum below 50 m')
    if max(values)-min(values)>2*minimum:reasons.append('longitudinal range exceeds twice weakest side')
    if residual is not None and residual>minimum:reasons.append('longitudinal residual exceeds weakest side')
    return dict(supported=not reasons,reasons=reasons,station_margins_metres=pairs,
        minimum_prominence_or_depth_metres=minimum,longitudinal_range_metres=max(values)-min(values),
        longitudinal_linear_residual_metres=residual)


def track(candidate,sample,mode):
    origin=(candidate['col']*256+128,candidate['row']*256+128)
    axis=tuple(256*v for v in candidate['axis']);sign=candidate['sign'];decisions=[]
    def options(expected,previous_axis,initial=False):
        radius=256 if initial else 128
        out=[]
        offsets=[(0,0)] if mode=='straight' else [(x,z) for z in range(-radius,radius+1,64) for x in range(-radius,radius+1,64) if math.hypot(x,z)<=radius]
        axes=[axis] if mode in ('straight','localized') else AXES
        for ox,oz in offsets:
            p=(expected[0]+ox,expected[1]+oz)
            for a in axes:
                a=tuple(a)
                if sum(x*y for x,y in zip(a,previous_axis))<0:a=tuple(-x for x in a)
                if angle(a,previous_axis)>45.000001:continue
                pair=margins(sample,p,a,sign)
                if pair is not None and min(pair)>=MARGIN:
                    out.append(dict(point=list(p),axis=list(a),height=sample(*p),margins=pair,score=min(pair)))
        out.sort(key=lambda p:(-p['score'],math.dist(p['point'],expected),p['point'],p['axis']))
        return out
    choices=options(origin,axis,True)
    if not choices:return dict(mode=mode,supported=False,reasons=['no bounded central two-sided extremum'],stations=[],decisions=[])
    start=choices[0]
    ambiguous=False
    def ambiguity(opts):
        best=opts[0];dx,dz=best['axis']
        def transverse(p):
            x,z=[p['point'][i]-best['point'][i] for i in (0,1)]
            return abs(-dz*x+dx*z)/math.hypot(dx,dz)
        return any(p['score']>=best['score']-50 and (transverse(p)>128 or angle(p['axis'],best['axis'])>45.000001) for p in opts[1:])
    ambiguous|=ambiguity(choices)
    decisions.append(dict(station=0,alternatives=choices,ambiguous=ambiguity(choices)))
    branches=[];total_turn=0
    for direction in (-1,1):
        branch=[];previous=start;turn=0
        for step in (1,2):
            a=previous['axis']
            expected=tuple(previous['point'][i]+direction*a[i] for i in (0,1))
            opts=options(expected,a)
            # Stay within 256px of the original unlocalized straight station.
            ref=tuple(origin[i]+direction*step*axis[i] for i in (0,1))
            opts=[p for p in opts if math.dist(p['point'],ref)<=256 and angle(p['axis'],a)+turn<=90.000001]
            decisions.append(dict(station=direction*step,alternatives=opts,ambiguous=bool(opts) and ambiguity(opts)))
            if not opts:break
            ambiguous|=ambiguity(opts);p=opts[0];turn+=angle(p['axis'],a);branch.append(p);previous=p
        branches.append(branch);total_turn+=turn
    centers=list(reversed(branches[0]))+[start]+branches[1]
    result=continuity(centers,[p['margins'] for p in centers])
    if ambiguous:result['reasons'].append('branch/intersection or center/orientation alternative within 50 m')
    if total_turn>90.000001:result['reasons'].append('total turning exceeds 90 degrees')
    if math.dist(start['point'],origin)>=256:result['reasons'].append('center reaches search edge')
    result.update(mode=mode,supported=not result['reasons'],stations=centers,decisions=decisions,
        center_displacement_native_pixels=math.dist(start['point'],origin),total_turn_degrees=total_turn,
        localization_grid_uncertainty_native_pixels=32*math.sqrt(2),
        longitudinal_distance_native_pixels=sum(math.dist(a['point'],b['point']) for a,b in zip(centers,centers[1:])))
    if len(centers)==5 and not 768<=result['longitudinal_distance_native_pixels']<=2048:
        result['reasons'].append('finite distance outside 768..2048 native pixels');result['supported']=False
    return result


def diagnose(candidate,bands):
    sample=field(bands);runs={mode:track(candidate,sample,mode) for mode in ('straight','localized','tracked')}
    a,b,c=[runs[k]['supported'] for k in ('straight','localized','tracked')]
    label='straight supported' if a else 'off-center evidence' if b else 'orientation/curvature evidence' if c else 'unresolved interruption or ambiguity at bounded resolution'
    return dict(runs=runs,interpretation=label,geological_selection='abstain')


def profile(candidate,diagnosis):
    path=diagnosis['runs']['tracked']['stations']
    # Incomplete path is retained, never extended by an unbounded fallback.
    return [(p['point'][0]-s*p['axis'][1],p['point'][1]+s*p['axis'][0]) for p in path for s in (-1,0,1)]
