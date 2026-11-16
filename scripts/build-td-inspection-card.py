"""Independent static cards. Read only pinned archive data; no historical imports."""
import argparse
from dataclasses import asdict, dataclass
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import PIL
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = Path('C:/Windows/Fonts/arial.ttf')
FONT_SHA = 'edfbd22a3d088fc2f5d7c79b8c9c732df6dc878a60f0a80be0f92a3c7a634404'
PINS = {
    'td-story': 'fec51d36faeb1d8b99e7624c2daab5cbd2b614227c6df9527dfe0f7c7954da47',
    'td-region-visual': 'f939c32cefe3a4e4f06320c056dcf5cb33e96ab6c50dcc76cc9640f297b1f1d8',
}
RESULTS = {
    'td-story': '9caff8648cb2165bf0d0ed7c3e9fd70ce6759d28b0c891b9fd36de1551fac650',
    'td-region-visual': 'd0853fba10ca350e353d9a2786a6362d99f80363aa7b12a071d470b89e56819c',
}
INPUT_SHA = '8dc1e0a9f98edd1dc6b2ce74cc1d795c117c15feb9503b0260a5c5ef23a701d6'
SITES = ((2944, 13824), (2688, 10880), (5760, 10880))
UNSUPPORTED = ((2689, 10880), (5761, 13953))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Site:
    x: int
    z: int
    row: int
    column: int
    elevation_metres: float
    pr58: dict
    pr59: dict
    interpretation: str = 'abstain'


def load(blobs=None):
    import zipfile
    members = {}
    for name, digest in PINS.items():
        raw = (ROOT / f'docs/evidence/{name}.zip').read_bytes() if blobs is None else blobs[name]
        require(sha(raw) == digest, 'Archive mismatch: ' + name)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = ['result.json', 'input/visual-data.json']
            if name == 'td-story':
                names.append('input/pr58-result.json')
            require(all(z.namelist().count(n) == 1 for n in names), 'Missing/duplicate member')
            require(all(z.getinfo(n).file_size < 4_000_000 for n in names), 'Member size cap')
            members[name] = {n: z.read(n) for n in names}
        require(sha(members[name]['result.json']) == RESULTS[name], 'Result mismatch')
        require(sha(members[name]['input/visual-data.json']) == INPUT_SHA, 'Input mismatch')
    s = json.loads(members['td-story']['result.json'])
    b = json.loads(members['td-region-visual']['result.json'])
    d = json.loads(members['td-story']['input/visual-data.json'])
    require(members['td-story']['input/pr58-result.json'] == members['td-region-visual']['result.json'], 'Baseline mismatch')
    require(s['baseline_result_sha256'] == RESULTS['td-region-visual'], 'Baseline reference')
    require(s['input_sha256'] == b['input_sha256'] == INPUT_SHA, 'Input reference')
    require(len(d['elevations']) == 49 and all(len(r) == 49 for r in d['elevations']), 'Grid shape')
    require(s['support']['heights'] == 2401 and s['geological_interpretation'] == b['geological_interpretation'] == 'abstain everywhere', 'Abstention')
    require(s['clamp_active'] and s['a'] == -0.5, 'Active clamp')
    return s, b, d


def lookup(x, z, data):
    s, b, d = data
    if type(x) is not int or type(z) is not int:
        return None
    if (x-2688) % 64 or (z-10880) % 64:
        return None
    c, r = (x-2688)//64, (z-10880)//64
    if not (0 <= r < 49 and 0 <= c < 49):
        return None
    h = next(v for v in s['histories'] if v['id'] == s['ids'][r][c][0])
    old = next(v for v in b['histories'] if v['id'] == b['terrain_illustration_ids'][r][c])
    require(h['token'] == h['surface_history'] == h['deep_history'], 'Shared history mismatch')
    return Site(x, z, r, c, d['elevations'][r][c], old, h)


def glyphs_present(raw, text):
    """Inspect TrueType Unicode cmap; a visible .notdef mask is not glyph proof."""
    tables = {}
    for i in range(struct.unpack_from('>H', raw, 4)[0]):
        tag, _, offset, length = struct.unpack_from('>4sIII', raw, 12+16*i)
        tables[tag] = raw[offset:offset+length]
    cmap = tables[b'cmap']
    maps = []
    for i in range(struct.unpack_from('>H', cmap, 2)[0]):
        platform, encoding, off = struct.unpack_from('>HHI', cmap, 4+8*i)
        if platform == 0 or (platform == 3 and encoding in (1, 10)):
            if struct.unpack_from('>H', cmap, off)[0] == 4:
                maps.append(off)
    def has(cp):
        for off in maps:
            n = struct.unpack_from('>H', cmap, off+6)[0]//2
            ends, starts = off+14, off+16+2*n
            deltas, ranges = off+16+4*n, off+16+6*n
            for i in range(n):
                end = struct.unpack_from('>H', cmap, ends+2*i)[0]
                start = struct.unpack_from('>H', cmap, starts+2*i)[0]
                if start <= cp <= end:
                    delta = struct.unpack_from('>h', cmap, deltas+2*i)[0]
                    distance = struct.unpack_from('>H', cmap, ranges+2*i)[0]
                    if not distance:
                        return (cp+delta) % 65536 != 0
                    gid = struct.unpack_from('>H', cmap, ranges+2*i+distance+2*(cp-start))[0]
                    if gid and (gid+delta) % 65536:
                        return True
        return False
    require(all(has(ord(c)) for c in set(text) if c not in '\n\r'), 'Missing font glyph')


def renderer():
    raw = FONT.read_bytes()
    require(sha(raw) == FONT_SHA, 'Font identity mismatch')
    fonts = {size: ImageFont.truetype(str(FONT), size) for size in (16, 17, 22)}
    glyphs_present(raw, ''.join(chr(n) for n in range(32, 127)))
    return fonts


def sections(card):
    h, old = card.pr59, card.pr58
    return [
        ('Observed / exact selected site', f'r{card.row}, c{card.column}; native x{card.x}, z{card.z}\n{card.elevation_metres:.3f} TD metres (rounded: 0.001 m).\nNot Minecraft Y.'),
        ('Regional mean / not site height', f"Band minus field mean: {h['mean_contrast_metres']:+.1f} m\n({h['observed_sites']:,} sites; rounded: 0.1 m)."),
        ('Seeded abstract substrate', f"PR59 ID {h['id']}; tag {h['substrate']}. Not a rock name."),
        ('Authored history / invented', f"{h['substrate']} -> conceptual tilt ->\n{h['authored_event']}."),
        ('Conceptual surface / deep', f"Surface: {h['authored_event']}.\nDeep: inherited {h['substrate']}, ID {h['id']}.\nShared identity/history; no measured\ndepth or subsurface interface."),
        ('PR58 / unchanged, separate', f"ID {old['id']}: {old['inherited']} -> {old['overprint']}. Invented tags."),
        ('Regional trend / not local slope', '2,401 sites: down with x, up with z.\nRatio about -1.01; active tilt clamp -0.5.\nTrend influences tilt; seed/width also matter.'),
    ]


CAVEAT = ('Unknown / interpretation abstains',
          'All 2,401 sites abstain. Unknown: real rock,\nage, dip, erosion, cover thickness, true\nhistory, gaps/exterior, between-site terrain\nand observation error. No nearby cursor/\nplayer height is inferred.')
COMPARISON = ('Cards 2/3: different IDs/tokens; same cover-preservation event.\n'
              'Their contact has no demonstrated geological necessity.\n'
              'PR59 did not establish better landscape-related contacts.')
GAP = ('Unsupported / exact lookup only\n'
       'Gap (2689,10880): no observation.\n'
       'Exterior (5761,13953): no observation.\n'
       'No interpolation or nearest-site inference.')


def wrap(text, font, width):
    out = []
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split():
            require(font.getlength(word) <= width, 'Unbreakable text exceeds width')
            trial = (line+' '+word).strip()
            if font.getlength(trial) > width:
                out.append(line)
                line = word
            else:
                line = trial
        out.append(line)
    return out


def sheet(cards, width, height, fonts):
    image = Image.new('RGB', (width, height), '#f5f3ed')
    draw = ImageDraw.Draw(image)
    boxes = []
    def text_block(text, x, y, max_width, size, allocation, role):
        glyphs_present(FONT.read_bytes(), text)
        font = fonts[size]
        for line in wrap(text, font, max_width):
            # Place the actual ink's top-left at (x, y), including negative
            # glyph bearings. Keep the allocation and strict predicate intact.
            ink = draw.textbbox((0, 0), line, font=font, anchor='lt')
            origin = (x-ink[0], y-ink[1])
            bounds = list(draw.textbbox(origin, line, font=font, anchor='lt'))
            l, t, r, b = allocation
            require(l <= bounds[0] <= bounds[2] <= r and t <= bounds[1] <= bounds[3] <= b, 'Text fit failed: '+role)
            boxes.append(dict(text=line, bounds=bounds, allocation=list(allocation), size=size, role=role))
            draw.text(origin, line, font=font, fill='#20363d', anchor='lt')
            y += size+3
        return y
    text_block('Why this region?  /  independent static card prototype', 24, 12, 1120, 22, (0, 0, width, 40), 'sheet heading')
    for i, card in enumerate(cards):
        x, y = 24+384*i, 44
        rect = (x, y, x+360, y+760)
        draw.rounded_rectangle(rect, radius=10, fill='white', outline='#71868a', width=2)
        yy = text_block(f'Card {i+1} / PR59 ID {card.pr59["id"]}', x+16, y+14, 328, 22, rect, 'card title')+10
        content = (x+16, y+14, x+344, y+602)
        for title, body in sections(card):
            yy = text_block(title, x+16, yy, 328, 17, content, 'section heading')
            yy = text_block(body, x+16, yy, 328, 16, content, 'body')+8
        caveat = (x+16, y+616, x+344, y+746)
        draw.line((x+16, y+609, x+344, y+609), fill='#71868a')
        cy = text_block(CAVEAT[0], x+16, y+618, 328, 17, caveat, 'reserved caveat heading')
        text_block(CAVEAT[1], x+16, cy+3, 328, 16, caveat, 'reserved caveat')
    footer = (24, 814, 1176, 898)
    text_block(COMPARISON, 24, 816, 690, 16, footer, 'comparison')
    text_block(GAP, 744, 816, 432, 16, footer, 'unsupported')
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue(), dict(width=width, height=height, card_allocation=[360, 760], text_boxes=boxes)


def build():
    data = load()
    cards = [lookup(x, z, data) for x, z in SITES]
    require([v.pr59['id'] for v in cards] == [-3, -2, -1], 'Selected identities')
    require(cards[1].pr59['authored_event'] == cards[2].pr59['authored_event'] == 'cover preservation', 'Shared event')
    require(cards[1].pr59['token'] != cards[2].pr59['token'], 'Distinct tokens')
    fonts = renderer()
    outputs, layouts = {}, {}
    for width, height in ((1200, 900), (1600, 1000)):
        raw, layout = sheet(cards, width, height, fonts)
        name = f'td-inspection-card-{width}.png'
        outputs[name] = raw
        layouts[name] = dict(**layout, sha256=sha(raw))
    s = data[0]
    record = dict(contract='independent-static-inspection-card-1',
                  archive_sha256=PINS, result_sha256=RESULTS, input_sha256=INPUT_SHA,
                  cards=[asdict(v) for v in cards],
                  unsupported=[dict(x=x, z=z, observation=None) for x, z in UNSUPPORTED],
                  regional_summaries={k:s[k] for k in ('mean_elevation', 'gx', 'gz', 'slope_ratio', 'a', 'clamp_active')},
                  rounding=dict(site_elevation_decimal_places=3, regional_contrast_decimal_places=1, trend_ratio_decimal_places=2),
                  renderer=dict(python=sys.version, interpreter=sys.executable, pillow=PIL.__version__, font=str(FONT), font_sha256=FONT_SHA, font_family=fonts[16].getname(), glyph_check='Unicode cmap nonzero glyph IDs for all displayed characters'),
                  images=layouts, card_sections=[sections(v) for v in cards], caveat=CAVEAT,
                  comparison=COMPARISON, unsupported_display=GAP,
                  evidence_limits=dict(static_only=True, player_study=False, minecraft_acceptance=False, companion_presentation='blocked and unverified'))
    outputs['td-inspection-card.json'] = (json.dumps(record, indent=2, sort_keys=True)+'\n').encode()
    return outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = build()  # All gates complete before writing any output.
    for name, raw in outputs.items():
        path = ROOT / 'docs/evidence' / name
        if args.check:
            require(path.read_bytes() == raw, 'Output mismatch: '+name)
        else:
            path.write_bytes(raw)
    print('PASS static card data/layout/output checks; no comprehension or runtime claim')
