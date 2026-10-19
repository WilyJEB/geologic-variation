"""Validate the design catalog without enabling it in the mod."""
import json
from pathlib import Path
import re
from urllib.parse import urlparse
root = Path(__file__).resolve().parents[1]
folder = root / 'planning/geology'
def read(name): return json.loads((folder / name).read_text(encoding='utf-8'))
sources = read('sources.json')['sources']
rocks = read('rock-catalog.json')
minerals = read('mineral-systems.json')
assert not rocks['runtime_enabled'] and not minerals['runtime_enabled']
ids = [rock['id'] for rock in rocks['rocks']]
assert len(ids) == len(set(ids)) == 8
for layer, template in [('surface', 'minecraft:stone'), ('deep', 'minecraft:deepslate')]:
    entries = [r for r in rocks['rocks'] if r['layer'] == layer]
    assert len(entries) == 4
    assert all(r['material_template'] == template for r in entries)
    assert rocks['vanilla_candidates'][layer] == template
surface = [r for r in rocks['rocks'] if r['layer'] == 'surface']
assert sorted(r['color_role'] for r in surface) == ['dark_brown', 'dark_gray', 'dark_gray', 'light']
assert rocks['legacy_only'][0]['id'] == 'quartzite' and rocks['legacy_only'][0]['registered_ids_must_remain']
contract = rocks['family_contract']
assert len(contract['finishes']) == 4 and len(contract['shapes']) == 4
assert contract['active_block_forms'] == len(ids) * 4 * 4 == 128
assert contract['active_shared_textures'] == len(ids) * 4 == 32
for source in sources.values():
    url = urlparse(source['url'])
    assert url.scheme == 'https' and any(url.hostname == d or url.hostname.endswith('.' + d) for d in ['usgs.gov', 'bgs.ac.uk'])
    assert source['access_basis'] in ['page', 'indexed_excerpt']
for rock in rocks['rocks']:
    assert rock['source_ids'] and set(rock['source_ids']) <= sources.keys()
    assert rock['formation_summary'] and rock['inferred_terrane_affinities']
    assert len(rock['art_swatches']) >= 2
    assert all(re.fullmatch(r'#[0-9A-F]{6}', c) for c in rock['art_swatches'])
profiles = minerals['profiles']
assert len(profiles) >= 10 and len({p['id'] for p in profiles}) == len(profiles)
for profile in profiles:
    assert profile['source_ids'] and set(profile['source_ids']) <= sources.keys()
    assert set(profile['palette_host_ids']) <= set(ids)
    assert profile['host_rocks'] and profile['representative_minerals'] and profile['enrichment_process']
    assert profile['required_geological_context'] and profile['candidate_game_geometry'] and profile['limitation']
    assert profile['target_elements_or_groups'] and profile['grade'] is None and profile['numeric_grade_provenance'] is None
print(f'Checked 8 proposed stones (4 per layer), 32 texture targets, {len(profiles)} mineral-system profiles and {len(sources)} primary source references; runtime remains disabled.')
