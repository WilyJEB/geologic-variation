"""Static presentation only: read two pinned archives; never execute their builders."""
import hashlib
import html
import io
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/td-region-explainer.html'
PINS = {
    'td-story': 'fec51d36faeb1d8b99e7624c2daab5cbd2b614227c6df9527dfe0f7c7954da47',
    'td-region-visual': 'f939c32cefe3a4e4f06320c056dcf5cb33e96ab6c50dcc76cc9640f297b1f1d8',
}
SITES = ((46, 4), (0, 0), (0, 48))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(blobs=None):
    archives = {}
    for name, digest in PINS.items():
        raw = (ROOT / ('docs/evidence/' + name + '.zip')).read_bytes() if blobs is None else blobs[name]
        if sha(raw) != digest:
            raise ValueError('Immutable input mismatch: ' + name)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            archives[name] = {n: z.read(n) for n in ('result.json', 'input/visual-data.json', 'viewer.html')}
            if name == 'td-story':
                archives[name]['input/pr58-result.json'] = z.read('input/pr58-result.json')
    story, baseline = archives['td-story'], archives['td-region-visual']
    assert story['input/pr58-result.json'] == baseline['result.json']
    assert story['input/visual-data.json'] == baseline['input/visual-data.json']
    s, b = json.loads(story['result.json']), json.loads(baseline['result.json'])
    assert s['baseline_result_sha256'] == sha(baseline['result.json'])
    assert s['input_sha256'] == sha(story['input/visual-data.json'])
    h = json.loads(story['input/visual-data.json'])['elevations']
    assert len(h) == 49 and all(len(row) == 49 for row in h)
    cards = []
    for r, c in SITES:
        identity = s['ids'][r][c][0]
        history = next(v for v in s['histories'] if v['id'] == identity)
        old = next(v for v in b['histories'] if v['id'] == b['terrain_illustration_ids'][r][c])
        assert history['token'] == history['surface_history'] == history['deep_history']
        cards.append(dict(row=r, column=c, x=2688+64*c, z=10880+64*r,
                          elevation_metres=h[r][c], pr59=history, pr58=old))
    assert [v['pr59']['id'] for v in cards] == [-3, -2, -1]
    return archives, s, b, cards


def observed_at(x, z, heights):
    """Exact retained sites only; gaps/exterior have no inspection record."""
    if (x-2688) % 64 or (z-10880) % 64:
        return None
    c, r = (x-2688)//64, (z-10880)//64
    return heights[r][c] if 0 <= r < 49 and 0 <= c < 49 else None


def build(blobs=None):
    archives, s, b, cards = load(blobs)
    esc = lambda value: html.escape(str(value))
    maps = re.findall(r'<svg\b.*?</svg>', archives['td-story']['viewer.html'].decode(), re.S)
    assert len(maps) == 2
    panels = []
    for n, (title, svg) in enumerate(zip(('PR58 · unchanged terrain illustration', 'PR59 · unchanged authored story'), maps)):
        markers = []
        for i, card in enumerate(cards, 1):
            x = 40+(card['x']-2688)/3073*520
            z = 30+(card['z']-10880)/3073*520
            markers.append(f'<a href="#card-{i}" aria-label="Example {i}, row {card["row"]}, column {card["column"]}"><circle class="marker" cx="{x}" cy="{z}" r="10"/><text class="number" x="{x}" y="{z+4}">{i}</text></a>')
        svg = svg.replace('</svg>', ''.join(markers)+'</svg>')
        panels.append(f'<section><h2>{title}</h2>{svg}</section>')
    content = []
    for i, v in enumerate(cards, 1):
        t, old = v['pr59'], v['pr58']
        content.append(f'''<article id="card-{i}" tabindex="0"><h2>{i} · {'Exposure' if i == 1 else 'Cover'} / ID {t['id']}</h2>
<h3>Observed here · exact retained site</h3><p>r{v['row']},c{v['column']} · native x{v['x']}, z{v['z']}<br>Elevation <strong>{v['elevation_metres']} m</strong> (TD elevation, not Minecraft Y).</p>
<h3>Regional summaries · not this point’s height</h3><p>Band mean minus field mean: <strong>{t['mean_contrast_metres']:+} m</strong>, from {t['observed_sites']} sites. Whole-field sample mean: {s['mean_elevation']} m. Whole-field planar trend: gx={s['gx']}, gz={s['gz']} m/native pixel; ratio={s['slope_ratio']}. Authored tilt a={s['a']}; ±0.5 clamp active: true.</p>
<h3>Seeded identity · invented substrate</h3><p>PR59 ID {t['id']}, tag {t['substrate']}. Seed fixes identity and substrate; A/B are abstract tags, not rock names.</p>
<h3>Authored history</h3><p>One invented history influenced by these cues: inherited substrate {t['substrate']} → conceptual tilt → <strong>{esc(t['authored_event'])}</strong>. Observed broad trend influences orientation; relative band mean influences event choice. This does not observe erosion or cover.</p>
<h3>Regional consequence · conceptual pair</h3><div class="pair"><p><b>Surface</b><br>{esc(t['authored_event'])}<br>Shared token: {t['token']}</p><p><b>Deep</b><br>Inherited substrate {t['substrate']} / ID {t['id']}<br>Shared token: {t['token']}</p></div><p>No depth scale or subsurface interface is observed.</p>
<h3>PR58 at this same site</h3><p>ID {esc(old['id'])}; {esc(old['inherited'])} → {esc(old['overprint'])}. Invented tags; a separate unchanged construction.</p><p class="token">PR58 exact history: {esc(json.dumps(old, sort_keys=True))}</p>
<h3>Unknown · interpretation abstains</h3><p>Real rock, age, dip, cover thickness, erosion and true history are unconfirmed. Between-site and exterior terrain and observation error are unknown. {'PR58 difference-mode edge stencil is unavailable here.' if v['row'] == 0 else 'No geological classification is established here.'}</p><a href="#examples">Back to examples and maps</a></article>''')
    provenance = dict(input_archive_sha256=PINS, result_sha256={k: sha(v['result.json']) for k,v in archives.items()},
                      retained_input_sha256=sha(archives['td-story']['input/visual-data.json']), cards=cards)
    return ('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Why this region? Three retained examples</title>
<style>body{max-width:1480px;margin:32px auto;padding:0 28px;font:17px/1.5 system-ui;color:#20343e;background:#fcfbf6}h1{font-size:36px;line-height:1.15}h2{font-size:23px}h3{font-size:17px;margin-bottom:4px}p{margin-top:4px}.maps{display:grid;grid-template-columns:1fr 1fr;gap:24px}svg{width:100%;background:white}.contact{fill:none;stroke:#263b49;stroke-width:2;stroke-dasharray:6 3}.marker{fill:white;stroke:#111;stroke-width:2}.number{fill:#111;text-anchor:middle;font-size:12px;font-weight:bold;pointer-events:none}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}article{border:2px solid #aabbb7;border-radius:12px;padding:20px;background:white;scroll-margin-top:16px}article:target{border:4px solid #6d4300;padding:18px}a{color:#294f83}a:focus-visible,article:focus-visible{outline:4px solid #9b5b00;outline-offset:4px}.pair{border-left:4px solid #49675f;padding-left:12px}.pair p,.token,pre{overflow-wrap:anywhere;font-size:14px}pre{white-space:pre-wrap}.finding{border-left:5px solid #925027;background:#f6eadc;padding:16px}nav a{display:inline-block;padding:10px 14px;border:1px solid;margin:4px}@media(max-width:950px){.cards{grid-template-columns:1fr}.maps{grid-template-columns:1fr}}</style></head><body>
<h1>Why this region?</h1><p>Three examples from one retained landscape · offline explanation prototype · geology-1 unchanged</p>
<p>Trace an observed cue to a seeded identity, then to an explicitly invented history. This is a conceptual inspection view, not real geological history or production selection.</p>
<nav id="examples" aria-label="Fixed examples"><a href="#card-1">1 · r46,c4 · exposure</a><a href="#card-2">2 · r0,c0 · cover</a><a href="#card-3">3 · r0,c48 · cover</a></nav>
<p><b>Map legend:</b> small coloured dots = 2,401 observed elevations, blue low → orange high; numbered white circles = the three examples; dashed lines and tinted domains = authored conceptual contacts/regions. White gaps carry no retained heights. Colour is not needed to identify examples. Dashed outer box = original half-open query footprint [z10880,x2688,z13953,x5761], one native pixel beyond the last sites. Seed 8675309; 49×49 sites, native spacing 64. 9,440,928 original query values are unavailable. No height interpolation.</p>
<div class="maps">'''+''.join(panels)+'''</div>
<p class="finding"><b>Negative contact comparison retained:</b> PR59 did not establish better landscape-related contacts. Straight oblique bands cross the curved elevation pattern; authored phase/width and the active −0.5 clamp partly control appearance. Both lower-mean bands receive cover preservation; their contact has no demonstrated geological necessity. PR58 bends vertical contacts but keeps an arbitrary horizontal seam.</p>
<div class="cards">'''+''.join(content)+'''</div>
<h2>Limits and next decision</h2><p>All 2,401 sites abstain from actual geological interpretation. Unknown error is never zero. Contact/tint geometry fills conceptual space, not missing terrain. Source/data checks do not establish browser readability, visual quality, player comprehension or live addon acceptance. No existing browser surface was available for 1200×900 / 1600×1000, keyboard-fragment or scripts-disabled rendering checks; those remain unverified. This document contains no scripts: all maps, markers, cards and caveats are static.</p>
<p>Next decision gate: review this companion’s explanatory value and readability, including the missing browser checks and player comprehension, before separately authorizing any in-addon adaptation. No live validation, adoption or merge authority follows. PR62 stays draft/unmerged; navigation-3 remains consumed/INCOMPLETE, zero remaining. #9/#11 stay open.</p>
<p>All historical failures remain failed: PR51 paired coarse drift, PR52 matching native support, PR57 pressure reduction, height/residual and #5 final-block assertions. PR54 is exhausted; final capture instrumentation is compile-only, historical arrays/indices/ULPs unknown. Geometry/support/uncertainty, numerical reproducer, multi-field joining, fresh validation (new seeds, scales 1/6, signed coordinates, contrasting terrain/multiple contacts and fixed/paired coverage), alternating paired startup/cold/warm/full-route performance, immutable versioned adoption/new-world-only selection, bidirectional continuing-save rejection, exact original-artifact restoration/reopen and complete snapshot/block/persisted-container preservation remain gated. Geology-1, continuing saves, strict production guards, immutable inputs and optional Ulti-World are unchanged.</p>
<h2>Exact provenance and three-card records</h2><p>SHA256 digests and exact archived records; retained result digests identify the unchanged constructions. No new terrain was generated.</p><pre id="provenance">'''+esc(json.dumps(provenance, indent=2, sort_keys=True))+'''</pre></body></html>''').encode('utf-8')


if __name__ == '__main__':
    import sys
    raw = build()
    if '--check' in sys.argv:
        # Git's existing Windows checkout policy converts HTML LF to CRLF.
        assert OUTPUT.read_text(encoding='utf-8').encode('utf-8') == raw, 'Companion differs from offline rebuild (LF canonical)'
    else:
        OUTPUT.write_bytes(raw)
    print('Companion LF-canonical SHA256', sha(raw))
