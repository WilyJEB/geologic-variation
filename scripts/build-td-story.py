"""Frozen story-1, offline only, standard library. No provider imports."""
import hashlib
import html
import json
import math
from pathlib import Path
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
B = runpy.run_path(str(ROOT/'scripts/build-td-region-visual.py'))
STEM = ROOT/'docs/evidence/td-story'
sha = B['sha']
encoded = B['encoded']


def token(s):
    return hashlib.sha256(('story-1|8675309|'+s).encode()).hexdigest()


PHASE = int(token('phase')[:8], 16) % 2048


def region(x, z, a):
    return math.floor((x+a*z-PHASE)/2048)


def contact(i, z, a):
    return PHASE+2048*i-a*z


def neighborhood(i):
    return [i-1, i, i+1]


def evaluate(raw, baseline):
    d = B['load'](raw)
    assert baseline == B['evaluate'](raw), 'PR58 baseline mismatch'
    h = d['elevations']
    mean = sum(map(sum, h))/2401
    denom = sum((64*(c-24))**2 for r in range(49) for c in range(49))
    gx = sum(64*(c-24)*h[r][c] for r in range(49) for c in range(49))/denom
    gz = sum(64*(r-24)*h[r][c] for r in range(49) for c in range(49))/denom
    ratio = gz/gx if gx else None
    a = max(-.5, min(.5, ratio)) if gx else 0
    grid = [[ [region(2688+64*c,10880+64*r,a)] for c in range(49)] for r in range(49)]
    histories = []
    for i in sorted({v[0] for row in grid for v in row}):
        values = [h[r][c] for r in range(49) for c in range(49) if grid[r][c] == [i]]
        contrast = sum(values)/len(values)-mean
        event = 'greater stripping / exposure' if contrast > 0 else 'cover preservation' if contrast < 0 else 'unresolved'
        t = token(f'history|{i}')
        histories.append(dict(id=i, anchor=[PHASE+2048*(i+.5),0], token=t,
                              substrate='AB'[int(t[:2],16)%2], observed_sites=len(values),
                              mean_contrast_metres=contrast, authored_event=event,
                              surface_history=t, deep_history=t))
    return dict(contract='story-1', input_sha256=sha(raw), baseline_result_sha256=sha(encoded(baseline)),
                phase=PHASE, gx=gx,gz=gz, slope_ratio=ratio,a=a,clamp_active=ratio is not None and abs(ratio)>.5,
                mean_elevation=mean,orientation_abstains=gx==0,ids=grid,histories=histories,
                topology=B['topology'](grid),baseline_topology=baseline['topology'][1],
                observation_error=None, geological_interpretation='abstain everywhere',
                support=dict(heights=2401,regional_ids=3,query_bounds=d['query_bounds_half_open'],
                             missing_query_values=9440928,between_point_geometry='unknown'),
                production_selector=False,gameplay_acceptance=False)


def svg(d, baseline, h, new):
    # All point observations and conceptual contact geometry are embedded SVG.
    X=lambda v:40+(v-2688)/3073*520
    Z=lambda v:30+(v-10880)/3073*520
    p=['<svg viewBox="0 0 600 590" role="img" aria-label="'+('New history' if new else 'Unchanged PR58 baseline')+'">',
       '<defs><clipPath id="clip'+str(new)+'"><rect x="40" y="30" width="520" height="520"/></clipPath></defs>',
       '<rect x="40" y="30" width="520" height="520" fill="#f7f5ed"/>',
       '<g clip-path="url(#clip'+str(new)+')">']
    colors=['#83c9b5','#dab88b','#afa7d3','#d5a6b3','#99b7d2']
    if new:
        for n,v in enumerate(d['histories']):
            i=v['id']; a=d['a']
            coords=[(contact(i,10880,a),10880),(contact(i+1,10880,a),10880),
                    (contact(i+1,13953,a),13953),(contact(i,13953,a),13953)]
            p.append('<polygon class="domain" opacity=".35" fill="'+colors[n%5]+'" points="'+' '.join(f'{X(x)},{Z(z)}' for x,z in coords)+'"/>')
        for i in range(min(v['id'] for v in d['histories']),max(v['id'] for v in d['histories'])+2):
            p.append(f'<path class="contact" d="M{X(contact(i,10880,d["a"]))} 30 L{X(contact(i,13953,d["a"]))} 550"/>')
    else:
        for n,v in enumerate(baseline['histories']):
            i,j=v['id']; za=baseline['phases'][1]+j*2048; zb=za+2048
            zs=[za]+[r['z'] for r in baseline['rows'] if za<r['z']<zb]+[zb]
            l=baseline['phases'][0]+i*2048
            coords=[(l+B['warp'](z,baseline['rows']),z) for z in zs]+[(l+2048+B['warp'](z,baseline['rows']),z) for z in reversed(zs)]
            p.append('<polygon class="domain" opacity=".35" fill="'+colors[n%5]+'" points="'+' '.join(f'{X(x)},{Z(z)}' for x,z in coords)+'"/>')
        for i in range(-1,5):
            p.append('<polyline class="contact" points="'+' '.join(f'{X(baseline["phases"][0]+i*2048+r["displacement"])},{Z(r["z"])}' for r in baseline['rows'])+'"/>')
        for j in range(3,9):
            p.append(f'<path class="contact" d="M40 {Z(baseline["phases"][1]+j*2048)} H560"/>')
    lo,hi=min(map(min,h)),max(map(max,h))
    for r in range(49):
        for c in range(49):
            v=h[r][c]; identity=d['ids'][r][c] if new else baseline['terrain_illustration_ids'][r][c]
            tip=html.escape(f'x={2688+64*c}, z={10880+64*r}; elevation={v} m; ID={identity}; error unknown; geological interpretation abstains')
            p.append(f'<circle cx="{X(2688+64*c)}" cy="{Z(10880+64*r)}" r="2.1" fill="hsl({225-195*(v-lo)/(hi-lo)} 60% 36%)"><title>{tip}</title></circle>')
    records=d['histories'] if new else baseline['histories']
    grid=d['ids'] if new else baseline['terrain_illustration_ids']
    for v in records:
        key=[v['id']] if new else v['id']
        sites=[(2688+64*c,10880+64*r) for r in range(49) for c in range(49) if grid[r][c]==key]
        xx=max(3150,min(5300,sum(x for x,z in sites)/len(sites)))
        zz=sum(z for x,z in sites)/len(sites)
        label=('ID '+str(v['id'])) if new else str(v['id'])+' '+v['inherited']+' → '+v['overprint']
        p.append(f'<text x="{X(xx)}" y="{Z(zz)}" text-anchor="middle" font-size="12" font-weight="bold" paint-order="stroke" stroke="white" stroke-width="4" fill="#20343e">{html.escape(label)}</text>')
    p.append('</g><rect x="40" y="30" width="520" height="520" fill="none" stroke="#293f49" stroke-dasharray="3 3"/>')
    for v in (2688,4224,5760):
        p.append(f'<text x="{X(v)}" y="570" text-anchor="middle">{v}</text>')
    for v in (10880,12416,13952):
        p.append(f'<text x="35" y="{Z(v)}" text-anchor="end" font-size="9">{v}</text>')
    return ''.join(p)+'</svg>'


def viewer(d, baseline, h):
    rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [v['id'],v['substrate'],round(v['mean_contrast_metres'],3),v['authored_event'],v['token'][:12]])+'</tr>' for v in d['histories'])
    stats=html.escape(json.dumps(dict(baseline=d['baseline_topology'],new=d['topology']),indent=2))
    return ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Terrain-informed synthetic history</title>
<style>body{max-width:1400px;margin:32px auto;padding:0 24px;font:16px system-ui;background:#fcfbf6;color:#20343e}h1{font-size:32px}.maps{display:grid;grid-template-columns:1fr 1fr;gap:24px}svg{width:100%;background:white}.contact{fill:none;stroke:#263b49;stroke-width:2;stroke-dasharray:6 3}td,th{padding:10px;text-align:left;border-bottom:1px solid #ccd4d3}table{border-collapse:collapse}pre{white-space:pre-wrap}button{padding:9px;margin:5px}small{color:#43585e}@media(max-width:850px){.maps{grid-template-columns:1fr}}</style>
<h1>One landscape, one terrain-informed story</h1><p>Diagnostic only · geology-1 unchanged · actual geological interpretation abstains everywhere</p>
<p>Points are actual retained elevations (blue low → orange high). Tints and dashed contacts are conceptual. Blank space between points has no retained height; continuous geometry and error remain unknown. Dashed outer box is the original half-open query footprint, one native pixel beyond the final sites.</p>
<button id="toggle" hidden>Hide conceptual domains</button><div class="maps"><section><h2>Unchanged PR58 boundary illustration</h2>'''+svg(d,baseline,h,False)+'''<p>Four seeded histories; terrain bends only the vertical contacts. The horizontal seam remains fixed.</p></section><section><h2>One terrain-informed band history</h2>'''+svg(d,baseline,h,True)+'''<p>Inherited bands → conceptual tilt responding to the broad observed elevation trend → relative stripping or cover preservation responding to each band's observed elevation contrast. These are authored alternatives, not recovered events.</p></section></div>
<h2>Shared surface / deep meaning</h2><p>Each ID refers to one inherited substrate and one history token. Surface exposure or cover and deep inherited substrate reference that same record. No subsurface depth or interface has been observed. Band contacts represent inherited relationships; matching neighboring event tags do not prove a geological need for a contact.</p>
<table><tr><th>ID</th><th>Seeded substrate</th><th>Observed contrast (m)</th><th>Authored surface event</th><th>Shared surface/deep token</th></tr>'''+rows+'''</table>
<h2>Evidence, authorship and uncertainty</h2><p>Seed supplies global anchors, IDs and A/B substrate alternatives. Elevation supplies a fixed-field least-squares trend and band mean contrasts. The strip spacing, slope ratio/clamp, tilting/stripping narrative and extension between observations are authored. These observations cannot identify erosion, cover, rock type, age or tectonics. Interpretation abstains everywhere.</p>
<p>2,401 actual points; 9,440,928 original query values unavailable. Exterior support is missing. Edge neighbor stencils are incomplete at 192 points; the new whole-field descriptor uses only the 2,401 retained points. No interpolation, zero-error assumption or confirmed extremum.</p>
<p>Computed slopes gx='''+str(d['gx'])+', gz='+str(d['gz'])+'; authored a='+str(d['a'])+'; clamp active='+str(d['clamp_active'])+'''. Fixed neighborhood: at most 2,401 heights and 3 regional IDs. No joining policy for another field.</p>
<h2>Computed topology (not a quality score)</h2><pre>'''+stats+'''</pre><p>Whole bands and viewport intersections are convex. Four-neighbor sample components are independently counted above. Repeatability and connectivity do not validate the story or establish player recognition.</p>
<p><a href="../td-story.md">Report and decision</a> · <a href="../td-story-protocol.md">Frozen contract</a> · <a href="td-story.zip">Portable evidence</a></p>
<script>const b=document.getElementById('toggle');b.hidden=false;let visible=true;b.addEventListener('click',()=>{visible=!visible;document.querySelectorAll('.domain,.contact').forEach(e=>e.style.visibility=visible?'visible':'hidden');b.textContent=visible?'Hide conceptual domains':'Show conceptual domains';});</script></html>''').encode()


def export(strict=False):
    with zipfile.ZipFile(ROOT/'docs/evidence/td-region-visual.zip') as z:
        raw=z.read('input/visual-data.json'); baseline_raw=z.read('result.json')
        api={n:z.read(n) for n in z.namelist() if n.startswith('api/')}
    baseline=json.loads(baseline_raw); d=evaluate(raw,baseline)
    members=dict(api,**{'input/visual-data.json':raw,'input/pr58-result.json':baseline_raw,'result.json':encoded(d),
                       'viewer.html':viewer(d,baseline,json.loads(raw)['elevations'])})
    for name in ['scripts/build-td-story.py','scripts/test-td-story.py','scripts/test-td-story-viewer.cjs','scripts/reexport-td-story.py','scripts/render-td-story.py','docs/td-story-protocol.md']:
        members['sources/'+name]=(ROOT/name).read_bytes()
    for name in ['td-story.png','td-story-image.json']:
        members['visual/'+name]=(ROOT/'docs/evidence'/name).read_bytes()
    image=json.loads(members['visual/td-story-image.json'])
    assert image['result_sha256']==sha(members['result.json'])
    assert image['png_sha256']==sha(members['visual/td-story.png'])
    assert image['renderer_sha256']==sha(members['sources/scripts/render-td-story.py'])
    import io
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    outputs={'.zip':out.getvalue(),'.html':members['viewer.html'],'.json':encoded(dict(archive_sha256=sha(out.getvalue()),members={n:sha(b) for n,b in sorted(members.items())},result=d))}
    for ext,data in outputs.items():
        path=STEM.with_suffix(ext)
        if strict: assert path.read_bytes()==data, 'Strict story re-export mismatch: '+ext
        else: path.write_bytes(data)
    return d


if __name__=='__main__':
    print(json.dumps(export(),indent=2))
