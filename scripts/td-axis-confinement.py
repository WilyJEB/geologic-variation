"""Separate finite-support diagnostic; frozen geometry-arc-1 is imported unchanged."""
import math
from pathlib import Path
import runpy

g = runpy.run_path(str(Path(__file__).with_name('td-geometry-arc.py')))


def assess(path):
    result = dict(path=path, ratios=[], decision='abstain', reasons=list(path['reasons']))
    if not path['supported']:
        return result
    stations, distances = path['stations'], path['path_distances']
    for i in range(1, len(stations)-1):
        left, center, right = (stations[j]['height'] for j in (i-1,i,i+1))
        a, b = distances[i]-distances[i-1], distances[i+1]-distances[i]
        second = 2*((right-center)/b-(center-left)/a)/(a+b)
        transverse = sum(stations[i]['sides'])
        result['ratios'].append(abs(second)*256**2/transverse)
    maximum = max(result['ratios'])
    result['decision'] = 'support' if maximum <= .25 else 'reject' if maximum >= .5 else 'abstain'
    result['reasons'] = [] if maximum <= .25 else ['longitudinal curvature comparable to transverse confinement']
    return result


def track(sample, origin, axis, sign):
    return assess(g['track'](sample,origin,axis,sign))


FAMILIES = ('straight','curve','linear','quadratic','sinusoidal','slope','isolated',
            'saddle','crossing','parallel','gap','elongated_isolated','shallow_saddle',
            'strong_nonlinear','asymmetric')
POSITIVE = {'straight','curve','linear','quadratic','sinusoidal','strong_nonlinear','asymmetric'}


def analytical(shape, degrees, translation, sign):
    angle=math.radians(degrees); co,si=math.cos(angle),math.sin(angle)
    def sample(x,z):
        x-=translation[0]; z-=translation[1]
        u,v=x*co+z*si,-x*si+z*co
        value=-.004*v*v
        if shape=='curve': value=-.004*(v-.0003*u*u)**2
        if shape=='linear': value+=2*u
        if shape=='quadratic': value+=.0004*u*u+2*u
        if shape=='sinusoidal': value+=60*math.sin(u/512)+u
        if shape=='slope': value=2*v
        if shape=='isolated': value-=.004*u*u
        if shape=='saddle': value+=.004*u*u
        if shape=='crossing': value=-.004*min(v*v,u*u)
        if shape=='parallel': value=-.004*min((v-192)**2,(v+192)**2)
        if shape=='gap' and abs(u)>200: value=.004*v*v
        if shape=='elongated_isolated': value-=.0002*u*u
        if shape=='shallow_saddle': value+=.0002*u*u
        if shape=='strong_nonlinear': value+=.004*u*u+2*u
        if shape=='asymmetric': value=-(.003 if v<0 else .005)*v*v+u
        return sign*value
    return sample,(co,si)
