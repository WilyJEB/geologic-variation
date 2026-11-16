"""Presentation-only exact-site atlas; read pinned retained archives, no UI runtime."""
import argparse
import html
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/td-site-atlas.html'
READER = runpy.run_path(str(Path(__file__).with_name('build-td-region-explainer.py')))


def build(blobs=None):
    archives, story, baseline, _ = READER['load'](blobs)
    heights = json.loads(archives['td-story']['input/visual-data.json'])['elevations']
    histories = {v['id']: v for v in story['histories']}
    old = {tuple(v['id']): v for v in baseline['histories']}
    maps = re.findall(r'<svg\b.*?</svg>', archives['td-story']['viewer.html'].decode(), re.S)
    if len(maps) != 2:
        raise ValueError('Expected two retained maps')
    panels = []
    for title, svg in zip(('PR58 terrain illustration', 'PR59 authored story'), maps):
        ordinal = [0]
        def link(match):
            r, c = divmod(ordinal[0], 49)
            ordinal[0] += 1
            return f'<a href="#site-{r}-{c}" aria-label="Exact site row {r}, column {c}">{match[0]}</a>'
        svg = re.sub(r'<circle\b.*?</circle>', link, svg, flags=re.S)
        if ordinal[0] != 2401:
            raise ValueError('Expected 2401 exact retained points')
        panels.append(f'<section><h2>{title}</h2>{svg}</section>')
    rows = []
    for r, row in enumerate(heights):
        for c, height in enumerate(row):
            h = histories[story['ids'][r][c][0]]
            prior = old[tuple(baseline['terrain_illustration_ids'][r][c])]
            if not h['token'] == h['surface_history'] == h['deep_history']:
                raise ValueError('Shared history mismatch')
            values = (f'r{r},c{c}', f'{2688+64*c}, {10880+64*r}', str(height),
                      str(h['mean_contrast_metres']),
                      f"{h['id']} / {h['substrate']}", h['authored_event'],
                      f"{prior['id']} / {prior['inherited']} / {prior['overprint']}", 'Abstain; error unknown')
            cells = ''.join('<td>'+html.escape(v)+'</td>' for v in values)
            rows.append(f'<tr id="site-{r}-{c}">{cells}<td><a href="#maps">Maps</a></td></tr>')
    summaries = ''.join('<li>'+html.escape(f"ID {v['id']}: {v['observed_sites']} sites; mean contrast {v['mean_contrast_metres']} m; authored {v['authored_event']}")+'</li>' for v in story['histories'])
    provenance = html.escape(json.dumps(dict(archive_sha256=READER['PINS'],
        result_sha256={k: READER['sha'](v['result.json']) for k,v in archives.items()},
        regional={k: story[k] for k in ('mean_elevation', 'gx', 'gz', 'slope_ratio', 'a', 'clamp_active')},
        histories=story['histories']), indent=2))
    return ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Retained landscape: exact-site atlas</title>
<style>body{font:17px/1.5 system-ui;margin:24px;color:#20343e;background:#fcfbf6}main{max-width:1400px;margin:auto}.maps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}svg{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:16px}td,th{padding:10px;border:1px solid #aabbb7;text-align:left;vertical-align:top}tr:target{background:#ffe5a8}a{color:#194e89}a:focus-visible{outline:3px solid #925027}pre{white-space:pre-wrap;overflow-wrap:anywhere}.table{overflow-x:auto}.finding{border-left:5px solid #925027;padding:14px;background:#f6eadc}@media(max-width:850px){.maps{grid-template-columns:1fr}}</style><main>
<h1>Retained landscape: exact-site atlas</h1>
<p>Offline explanation prototype. Select a saved dot to reach its exact table record, or use browser Find for r46,c4, r0,c0 or any row/column. No scripts or external resources are required. Map-link behavior and readability have not been observed in a browser.</p>
<p>Small coloured dots are 2,401 saved TD elevations, blue low to orange high, at native spacing 64. White gaps have no retained heights. Dashed lines and tinted areas are invented regions, not observed geological contacts. Native x2688..5760, z10880..13952; seed 8675309. The original half-open footprint extends to x5761,z13953. Its 9,440,928 missing values, exterior terrain and observation error remain unknown. Native elevation metres are not Minecraft Y.</p>
<div class="maps" id="maps">'''+''.join(panels)+'''</div>
<h2>How landscape informs this authored story</h2>
<p>The plane fitted across the whole retained field slopes down with x and up with z. PR59 uses the ratio of those regional trends to orient bands, with an active authored clamp at -0.5. Seeded phase and chosen width also shape them. These are regional summaries, not local slopes or measured geological dip. Seed chooses inherited identity and abstract substrate A/B; band mean relative to the field mean chooses an invented exposure or cover event. No rock, age, erosion or subsurface interface is inferred.</p><ul>'''+summaries+'''</ul>
<p class="finding">PR59 did not establish better landscape-related contacts. Straight bands cross curved relief. IDs -2 and -1 share cover preservation despite different identities and history tokens; their contact has no demonstrated geological necessity. PR58 retains an arbitrary horizontal seam. Neither construction establishes player benefit.</p>
<h2>Exact observations alongside separate regional and authored records</h2>
<p>Only the elevation column is the observation at that exact site. Contrast is the band mean minus the whole-field mean, not that site's elevation or error bound. Surface event and deep substrate reference the same archived history token (below); no depth or cover thickness is observed. Geological interpretation abstains everywhere. Between-site requests return no observation; this atlas offers no interpolation or nearest-site selection.</p>
<div class="table"><table><caption>All retained sites, row-major order; full saved numeric precision</caption><thead><tr>'''+''.join('<th scope="col">'+v+'</th>' for v in ('Site','Native x, z','Exact elevation (m)','Regional contrast (m)','Seeded ID / substrate','Authored surface event','PR58 ID / invented tags','Geology / error','Return'))+'''</tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div>
<h2>Provenance and unknowns</h2><p>This presentation changes no diagnostics, terrain, production generation or saves. Geology-1 is unchanged; #9/#11 remain open. Historical failures and exhausted budgets remain failed/exhausted. Source checks do not establish rendered readability, player comprehension or Minecraft acceptance. Dedicated-launcher preparation stays deferred; both contract proposals stay unapproved.</p><pre>'''+provenance+'''</pre></main></html>\n''').encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = build()
    if args.check:
        if OUTPUT.read_text(encoding='utf-8').encode() != data:
            raise SystemExit('Atlas differs from deterministic rebuild')
        print('Atlas rebuild matches')
    else:
        OUTPUT.write_bytes(data)
        print(OUTPUT)
