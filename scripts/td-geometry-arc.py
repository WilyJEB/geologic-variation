"""geometry-arc-1: constant support, interpolated diagnostic, never TD extrema proof."""
import math

AXES = [(math.cos(i*math.pi/8), math.sin(i*math.pi/8)) for i in range(16)]


def bilinear(values, x0, z0, step=64):
    def sample(x, z):
        u, v = (x-x0)/step, (z-z0)/step
        if not (0 <= u <= len(values[0])-1 and 0 <= v <= len(values)-1):
            return None
        c, r = min(int(u), len(values[0])-2), min(int(v), len(values)-2)
        a, b = u-c, v-r
        return ((1-a)*(1-b)*values[r][c]+a*(1-b)*values[r][c+1]
                +(1-a)*b*values[r+1][c]+a*b*values[r+1][c+1])
    return sample


def angle(a, b):
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x,y in zip(a,b))))))


def track(sample, origin, axis, sign):
    norm=math.hypot(*axis); axis=tuple(v/norm for v in axis)
    decisions=[]
    def options(expected, previous, initial=False):
        offsets=[(x,z) for z in range(-128,129,64) for x in range(-128,129,64)
                 if math.hypot(x,z)<=128] if initial else [(-previous[1]*v,previous[0]*v) for v in (-64,0,64)]
        out=[]
        for dx,dz in offsets:
            p=(expected[0]+dx,expected[1]+dz)
            for a in AXES:
                if angle(a,previous)>22.500001:continue
                points=[(p[0]-a[1]*d,p[1]+a[0]*d) for d in (-256,0,256)]
                h=[sample(*q) for q in points]
                if any(v is None for v in h):continue
                sides=[sign*(h[1]-h[0]),sign*(h[1]-h[2])]
                if min(sides)>=50:
                    out.append(dict(point=p,axis=a,height=h[1],sides=sides,score=min(sides)))
        out.sort(key=lambda p:(-p['score'],math.dist(p['point'],expected),p['point'],p['axis']))
        return out
    ambiguous=False
    def choose(opts):
        nonlocal ambiguous
        if not opts:return None
        best=opts[0]; a=best['axis']
        ambiguous |= any(p['score']>=best['score']-10 and
            (abs(-(p['point'][0]-best['point'][0])*a[1]+(p['point'][1]-best['point'][1])*a[0])>128
             or angle(p['axis'],a)>45.000001) for p in opts[1:])
        return best
    opts=options(origin,axis,True);decisions.append(opts);start=choose(opts)
    if start is None:return dict(supported=False,reasons=['no bounded central contrast'],stations=[],decisions=decisions)
    branches=[];total_turn=0
    for direction in (-1,1):
        previous=start;branch=[]
        for step in (1,2):
            expected=tuple(previous['point'][i]+direction*256*previous['axis'][i] for i in (0,1))
            ref=tuple(origin[i]+direction*step*256*axis[i] for i in (0,1))
            opts=[p for p in options(expected,previous['axis']) if math.dist(p['point'],ref)<=256]
            decisions.append(opts);p=choose(opts)
            if p is None:break
            total_turn+=angle(p['axis'],previous['axis']);branch.append(p);previous=p
        branches.append(branch)
    path=list(reversed(branches[0]))+[start]+branches[1]
    distance=[0.0]
    for a,b in zip(path,path[1:]):distance.append(distance[-1]+math.dist(a['point'],b['point']))
    h=[p['height'] for p in path];weak=min(p['score'] for p in path)
    residual=max(abs(v-(h[0]+d/distance[-1]*(h[-1]-h[0]))) for d,v in zip(distance,h)) if distance[-1] else 0
    reasons=[]
    if len(path)!=5:reasons.append('incomplete path; no gap bridging')
    if ambiguous:reasons.append('alternative branch/center')
    if total_turn>90.000001:reasons.append('turn limit')
    if math.dist(start['point'],origin)>=128-1e-6:reasons.append('center search edge')
    # Deliberately separate geometric contrast from legacy longitudinal-height criteria.
    return dict(supported=not reasons,reasons=reasons,stations=path,decisions=decisions,
        path_distances=distance,total_turn_degrees=total_turn,weakest_side_metres=weak,
        height_range_metres=max(h)-min(h),arc_endpoint_residual_metres=residual,
        legacy_height_range_passed=max(h)-min(h)<=2*weak,
        arc_height_residual_passed=residual<=weak,
        support='interpolated point contrast; no confirmed unsampled extremum',
        geological_selection='abstain')
