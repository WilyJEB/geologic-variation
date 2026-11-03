"""Frozen diagnostic geometry; no geology thresholds or production callers."""
import math

SEEDS = [(8675309, 'development'), (2026110317, 'held_out'), (-2026110319, 'held_out')]
ORIENTATIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]  # longitudinal x,z
PROMINENCE = 50.0  # metres, morphology resolution margin, not lithology


def cross(v, axis, sign):
    dx, dz = axis
    # Perpendicular to the longitudinal lattice direction.
    return [sign * (v[4] - v[(1 + side*dx)*3 + 1 - side*dz]) for side in (-1, 1)]


def candidates(scan):
    result = []
    for kind, sign in [('ridge', 1), ('basin', -1)]:
        options = []
        for p in scan:
            v = p['evidence']['elevations']
            for axis in ORIENTATIONS:
                margins = cross(v, axis, sign)
                if min(margins) >= PROMINENCE:
                    options.append(dict(kind=kind, sign=sign, row=p['evidence']['row'],
                                        col=p['evidence']['col'], axis=list(axis),
                                        central_margins_metres=margins))
        options.sort(key=lambda p: (-min(p['central_margins_metres']), p['row'], p['col'], p['axis']))
        # Two distinct native centers per kind, at most four confirmation attempts.
        seen = set()
        for p in options:
            key = p['row'], p['col']
            if key in seen: continue
            seen.add(key); result.append(p)
            if len(seen) == 2: break
    return result


def stations(candidate):
    dx, dz = candidate['axis']
    return [(candidate['row']+t*dz, candidate['col']+t*dx) for t in range(-2, 3)]


def evaluate(candidate, evidence):
    margins = [cross(v['elevations'], candidate['axis'], candidate['sign']) for v in evidence]
    values = [v['elevations'][4] for v in evidence]
    minimum = min(x for pair in margins for x in pair)
    # A planar along-axis tilt is allowed only within a bounded height excursion.
    residual = max(abs(v-(values[0]+i*(values[-1]-values[0])/4)) for i,v in enumerate(values))
    supported = minimum >= PROMINENCE and max(values)-min(values) <= 2*minimum and residual <= minimum
    return dict(supported=supported, station_margins_metres=margins,
                minimum_prominence_or_depth_metres=minimum, longitudinal_range_metres=max(values)-min(values),
                longitudinal_linear_residual_metres=residual,
                longitudinal_distance_native_pixels=1024*math.hypot(*candidate['axis']),
                reason='supported straight lattice feature' if supported else 'abstain: extremum/continuity/tilt criterion failed')


def choose(attempts):
    # Ambiguous opposite interpretations or crossing orientations at the same cell abstain.
    winners = []
    for kind in ('ridge', 'basin'):
        eligible = [a for a in attempts if a['kind']==kind and a['evaluation']['supported']]
        eligible.sort(key=lambda a: (-a['evaluation']['minimum_prominence_or_depth_metres'], a['row'], a['col'], a['axis']))
        if eligible: winners.append(eligible[0])
        else:
            failed = [a for a in attempts if a['kind']==kind]
            if failed: winners.append(failed[0])
    if len(winners)==2 and (winners[0]['row'], winners[0]['col'])==(winners[1]['row'], winners[1]['col']): return []
    return winners


def profile(candidate):
    dx,dz = candidate['axis']; row,col = candidate['row'],candidate['col']
    # Five longitudinal centers; cross shoulders at all five stations: 15 cells.
    return [(row+t*dz+s*dx, col+t*dx-s*dz) for t in range(-2,3) for s in (-1,0,1)]


def fine_evaluate(candidate, observations):
    def assess(field):
        values = []
        for r in observations:
            values.append(r['policies']['target']['matched_native_cell']['mean_metres'] if field=='native_cell' else r['target_fine_tile']['mean_metres'])
        margins = [[candidate['sign']*(values[i+1]-values[i]),candidate['sign']*(values[i+1]-values[i+2])] for i in range(0,15,3)]
        centers = [values[i] for i in range(1,15,3)]
        minimum=min(x for p in margins for x in p)
        residual=max(abs(v-(centers[0]+i*(centers[-1]-centers[0])/4)) for i,v in enumerate(centers))
        return dict(station_margins_metres=margins,minimum_prominence_or_depth_metres=minimum,
                    longitudinal_range_metres=max(centers)-min(centers),longitudinal_linear_residual_metres=residual,
                    supported=minimum>=PROMINENCE and max(centers)-min(centers)<=2*minimum and residual<=minimum)
    return {field:assess(field) for field in ('native_cell','scaled_tile')}
