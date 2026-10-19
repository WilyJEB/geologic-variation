"""Generate deterministic masonry resources from the pinned Minecraft 1.21.1 templates.
Run after gradlew build. Use --check in CI to verify committed outputs and references.
No textures are copied: models temporarily reference Minecraft's built-in textures.
"""
import argparse
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'src/main/resources'
MOD = 'geologic_variation'
VANILLA = ROOT / 'build/moddev/artifacts/neoforge-21.1.251-client-extra-aka-minecraft-resources.jar'
# Texture order: natural, cobbled, polished, bricks. These are replaceable placeholders.
TEXTURES = {
    'limestone': ['calcite', 'cobblestone', 'smooth_sandstone', 'stone_bricks'],
    'slate': ['deepslate', 'cobbled_deepslate', 'polished_deepslate', 'deepslate_bricks'],
    'quartzite': ['diorite', 'cobblestone', 'polished_diorite', 'stone_bricks'],
    'gabbro': ['polished_blackstone', 'blackstone', 'polished_blackstone', 'polished_blackstone_bricks'],
}
LAYERS = dict((name.lower(), layer.lower()) for name, layer in re.findall(
    r'([A-Z]+)\(Layer\.([A-Z]+)\)',
    (ROOT / 'src/main/java/dev/wilyjeb/geology/domain/Provinces.java').read_text()))
assert set(TEXTURES) == set(LAYERS), 'Each registered stone needs an asset plan'
assert set(LAYERS.values()) <= {'surface', 'deep'}
OUTPUT = {}
BLOCKS = set()
RECIPES = {}
TEXTURE_PLAN = []

def emit(path, data):
    assert path not in OUTPUT, f'Duplicate output: {path}'
    OUTPUT[path] = data

def tag(namespace, kind, name, values):
    emit(f'data/{namespace}/tags/{kind}/{name}.json', {'replace': False, 'values': values})

def model(name):
    return f'{MOD}:block/{name}'

def item(name):
    return f'{MOD}:{name}'

def recipe(name, data, ingredient):
    emit(f'data/{MOD}/recipe/{name}.json', data)
    RECIPES[name] = data
    # Inventory-triggered recipe book unlocks, including stonecutting and smelting.
    predicate = {'items': ingredient['item']} if 'item' in ingredient else {'items': '#' + ingredient['tag']}
    emit(f'data/{MOD}/advancement/recipes/building_blocks/{name}.json', {
        'parent': 'minecraft:recipes/root',
        'criteria': {
            'has_material': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [predicate]}},
            'has_the_recipe': {'trigger': 'minecraft:recipe_unlocked', 'conditions': {'recipe': item(name)}},
        },
        'requirements': [['has_material', 'has_the_recipe']],
        'rewards': {'recipes': [item(name)]},
    })

def shaped(name, source, pattern, count):
    ing = {'item': item(source)}
    recipe(name, {'type': 'minecraft:crafting_shaped', 'category': 'building',
                 'pattern': pattern, 'key': {'#': ing}, 'result': {'id': item(name), 'count': count}}, ing)

def cutting(target, source, count=1):
    ing = {'item': item(source)}
    recipe(f'{target}_from_{source}_stonecutting', {'type': 'minecraft:stonecutting',
           'ingredient': ing, 'result': {'id': item(target), 'count': count}}, ing)

def remap(data, replacements):
    if isinstance(data, str):
        return replacements.get(data, data)
    if isinstance(data, list):
        return [remap(v, replacements) for v in data]
    if isinstance(data, dict):
        return {k: remap(v, replacements) for k, v in data.items()}
    return data

with zipfile.ZipFile(VANILLA) as vanilla:
    def template(path):
        return json.loads(vanilla.read(path))

    natural, cobbled, surface, deep, polished, bricks = [], [], [], [], [], []
    stairs, slabs, walls = [], [], []
    translations = {}
    for stone, textures in TEXTURES.items():
        natural.append(item(stone))
        cobbled.append(item('cobbled_' + stone))
        (surface if LAYERS[stone] == 'surface' else deep).append(item(stone))
        polished.append(item('polished_' + stone))
        bricks.append(item(stone + '_bricks'))
        forms = [stone, 'cobbled_' + stone, 'polished_' + stone, stone + '_bricks']
        family = []
        for form in forms:
            prefix = form[:-1] if form.endswith('_bricks') else form
            family.extend(item(name) for name in (form, prefix + '_stairs', prefix + '_slab', prefix + '_wall'))
        for kind in ('block', 'item'):
            tag(MOD, kind, 'families/' + stone, family)
        for base, tex in zip(forms, textures):
            TEXTURE_PLAN.append({'block': base, 'layer': LAYERS[stone],
                                 'planned_texture': f'assets/{MOD}/textures/block/{base}.png',
                                 'placeholder': f'minecraft:block/{tex}'})
            texture = tex if ':' in tex else 'minecraft:block/' + tex
            prefix = base[:-1] if base.endswith('_bricks') else base
            parts = [(base, None), (prefix + '_stairs', 'stairs'),
                     (prefix + '_slab', 'slab'), (prefix + '_wall', 'wall')]
            for name, shape in parts:
                BLOCKS.add(name)
                translations['block.' + MOD + '.' + name] = name.replace('_', ' ').title()
                emit(f'assets/{MOD}/models/item/{name}.json', {
                    'parent': model(name + '_inventory' if shape == 'wall' else name)})
                loot_source = 'stone' if name == stone else 'cobblestone_slab' if shape == 'slab' else 'cobblestone'
                loot = template(f'data/minecraft/loot_table/blocks/{loot_source}.json')
                loot = remap(loot, {'minecraft:stone': item(stone), 'minecraft:cobblestone': item('cobbled_' + stone) if name == stone else item(name),
                                   'minecraft:cobblestone_slab': item(name)})
                loot.pop('random_sequence', None)
                emit(f'data/{MOD}/loot_table/blocks/{name}.json', loot)
                if shape is None:
                    emit(f'assets/{MOD}/blockstates/{name}.json', {'variants': {'': {'model': model(name)}}})
                    emit(f'assets/{MOD}/models/block/{name}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': texture}})
                    continue
                {'stairs': stairs, 'slab': slabs, 'wall': walls}[shape].append(item(name))
                source = 'cobblestone_' + shape
                suffixes = {'stairs': ['', '_inner', '_outer'], 'slab': ['', '_top'],
                            'wall': ['_post', '_side', '_side_tall', '_inventory']}[shape]
                mapping = {model_src: model_dst for model_src, model_dst in
                           [('minecraft:block/' + source + suffix, model(name + suffix)) for suffix in suffixes]}
                mapping['minecraft:block/cobblestone'] = model(base)
                state = remap(template(f'assets/minecraft/blockstates/{source}.json'), mapping)
                emit(f'assets/{MOD}/blockstates/{name}.json', state)
                for suffix in suffixes:
                    data = template(f'assets/minecraft/models/block/{source}{suffix}.json')
                    data['textures'] = {k: texture for k in data['textures']}
                    emit(f'assets/{MOD}/models/block/{name}{suffix}.json', data)
                shaped(name, base, {'stairs': ['#  ', '## ', '###'], 'slab': ['###'], 'wall': ['###', '###']}[shape],
                       {'stairs': 4, 'slab': 6, 'wall': 6}[shape])
                cutting(name, base, 2 if shape == 'slab' else 1)
                # Vanilla-style direct cutting from natural rock into every finish and shape.
                if base != stone:
                    cutting(name, stone, 2 if shape == 'slab' else 1)
            if base in ('polished_' + stone, stone + '_bricks'):
                shaped(base, stone if base.startswith('polished_') else 'polished_' + stone, ['##', '##'], 4)
                cutting(base, stone)
        ing = {'item': item('cobbled_' + stone)}
        recipe(stone + '_from_smelting', {'type': 'minecraft:smelting', 'category': 'blocks',
               'ingredient': ing, 'result': {'id': item(stone)}, 'experience': 0.1, 'cookingtime': 200}, ing)
        # Makes cobble variants accessible without losing a Silk Touch tool's enchantment.
        ing = {'item': item(stone)}
        recipe('cobbled_' + stone, {'type': 'minecraft:crafting_shapeless', 'category': 'building',
               'ingredients': [ing], 'result': {'id': item('cobbled_' + stone), 'count': 1}}, ing)

    # One-way compatibility recipes cover vanilla/mod recipes that require exact vanilla IDs.
    for name, source, result in [('vanilla_cobblestone', 'cobblestones', 'cobblestone'), ('vanilla_stone', 'natural_stones', 'stone')]:
        ing = {'tag': MOD + ':' + source}
        recipe(name, {'type': 'minecraft:crafting_shapeless', 'category': 'building',
                     'ingredients': [ing], 'result': {'id': 'minecraft:' + result, 'count': 1}}, ing)

    all_ids = [item(b) for b in sorted(BLOCKS)]
    for kind in ('block', 'item'):
        tag(MOD, kind, 'natural_stones', natural)
        tag(MOD, kind, 'surface_stones', surface)
        tag(MOD, kind, 'deep_stones', deep)
        tag(MOD, kind, 'cobblestones', cobbled)
        tag(MOD, kind, 'polished_stones', polished)
        tag(MOD, kind, 'stone_bricks', bricks)
        tag('c', kind, 'stones', ['#' + MOD + ':natural_stones'])
        tag('c', kind, 'cobblestones', ['#' + MOD + ':cobblestones'])
        tag('c', kind, 'cobblestones/normal', [item('cobbled_' + s) for s in TEXTURES if LAYERS[s] == 'surface'])
        tag('c', kind, 'cobblestones/deepslate', [item('cobbled_' + s) for s in TEXTURES if LAYERS[s] == 'deep'])
        tag('minecraft', kind, 'stairs', stairs)
        tag('minecraft', kind, 'slabs', slabs)
        tag('minecraft', kind, 'walls', walls)
    tag('minecraft', 'block', 'mineable/pickaxe', all_ids)
    tag('minecraft', 'block', 'base_stone_overworld', ['#' + MOD + ':natural_stones'])
    tag('minecraft', 'block', 'stone_ore_replaceables', ['#' + MOD + ':surface_stones'])
    tag('minecraft', 'block', 'deepslate_ore_replaceables', ['#' + MOD + ':deep_stones'])
    tag('minecraft', 'block', 'overworld_carver_replaceables', ['#' + MOD + ':natural_stones'])
    tag('minecraft', 'block', 'stone_bricks', ['#' + MOD + ':stone_bricks'])
    tag('minecraft', 'item', 'stone_crafting_materials', ['#' + MOD + ':cobblestones'])
    tag('minecraft', 'item', 'stone_tool_materials', ['#' + MOD + ':cobblestones'])
    emit(f'assets/{MOD}/lang/en_us.json', translations)

    # Validate all model, texture, local recipe ingredient/output and loot item references.
    def walk(data):
        if isinstance(data, dict):
            for value in data.values(): yield from walk(value)
        elif isinstance(data, list):
            for value in data: yield from walk(value)
        elif isinstance(data, str): yield data
    for path, data in OUTPUT.items():
        if '/models/' in path or '/blockstates/' in path:
            for value in walk(data):
                if value.startswith(MOD + ':block/') and value not in data.get('textures', {}).values():
                    assert f'assets/{MOD}/models/block/{value.split("/")[-1]}.json' in OUTPUT, (path, value)
                if value.startswith(MOD + ':block/') and '/models/' in path and value in data.get('textures', {}).values():
                    assert (RES / f'assets/{MOD}/textures/{value.split(":")[1]}.png').exists(), (path, value)
                if value.startswith('minecraft:block/'):
                    relative = value.split(':')[1]
                    assert f'assets/minecraft/models/{relative}.json' in vanilla.namelist() or f'assets/minecraft/textures/{relative}.png' in vanilla.namelist(), (path, value)
        if '/recipe/' in path or '/loot_table/' in path:
            for value in walk(data):
                if value.startswith(MOD + ':'):
                    assert value.split(':')[1] in BLOCKS or f'data/{MOD}/tags/item/{value.split(":")[1]}.json' in OUTPUT, (path, value)
                if value.startswith('#' + MOD + ':'):
                    assert f'data/{MOD}/tags/item/{value.split(":")[1]}.json' in OUTPUT, (path, value)
    assert len(BLOCKS) == len(TEXTURES) * 16
    for path, data in OUTPUT.items():
        if '/tags/' in path:
            kind = path.split('/tags/')[1].split('/')[0]
            for value in data['values']:
                if value.startswith('#' + MOD + ':'):
                    assert f'data/{MOD}/tags/{kind}/{value.split(":")[1]}.json' in OUTPUT, (path, value)
                elif value.startswith(MOD + ':'):
                    assert value.split(':')[1] in BLOCKS, (path, value)
    # Keep decorative pieces out of fuel/tool/cobble inputs; full natural cubes only host ores.
    assert set(cobbled).isdisjoint(stairs + slabs + walls + bricks + polished)
    assert set(natural).isdisjoint(cobbled + polished + bricks)
    # Exercise the actual vanilla furnace/tool recipe inputs against the merged tag graph.
    def members(identifier, seen=()):
        assert identifier not in seen, f'Tag cycle: {identifier}'
        ns, name = identifier.split(':')
        path = f'data/{ns}/tags/item/{name}.json'
        values = []
        if path in vanilla.namelist(): values.extend(template(path)['values'])
        if path in OUTPUT: values.extend(OUTPUT[path]['values'])
        result = set()
        for value in values:
            if isinstance(value, dict): value = value['id']
            result.update(members(value[1:], seen + (identifier,)) if value.startswith('#') else [value])
        return result
    for recipe_id, symbol in [('furnace', '#'), ('stone_pickaxe', 'X')]:
        ingredient = template(f'data/minecraft/recipe/{recipe_id}.json')['key'][symbol]['tag']
        accepted = members(ingredient)
        assert set(cobbled) <= accepted, f'{recipe_id} rejects regional cobblestone'
        assert accepted.isdisjoint(stairs + slabs + walls + bricks + polished), f'{recipe_id} consumes decorations'

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
parser.add_argument('--jar', type=Path, help='Also verify every generated resource is packaged in this JAR')
args = parser.parse_args()
failures = []
for path, data in OUTPUT.items():
    target = RES / path
    if args.check:
        if not target.exists() or json.loads(target.read_text()) != data: failures.append(path)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
manifest = ROOT / 'docs/stone-assets.json'
if args.check:
    if not manifest.exists() or json.loads(manifest.read_text()) != TEXTURE_PLAN: failures.append(str(manifest))
else:
    manifest.write_text(json.dumps(TEXTURE_PLAN, indent=2) + '\n', encoding='utf-8')
if args.jar:
    with zipfile.ZipFile(args.jar) as packaged:
        for path, data in OUTPUT.items():
            if path not in packaged.namelist() or json.loads(packaged.read(path)) != data:
                failures.append('JAR:' + path)
        metadata = packaged.read('META-INF/neoforge.mods.toml').decode()
        version = re.search(r"^version = '([^']+)'", (ROOT / 'build.gradle').read_text(), re.M)[1]
        assert f'version="{version}"' in metadata, 'Artifact/mod metadata version mismatch'
        assert not any(n.startswith('com/github/xandergos/') for n in packaged.namelist()), 'Terrain Diffusion must remain external'
if failures:
    raise SystemExit('Missing/stale generated resources:\n' + '\n'.join(failures))
print(f'{"Checked" if args.check else "Generated"} {len(BLOCKS)} blocks, {len(RECIPES)} recipes, {len(OUTPUT)} JSON resources; references and layer tags valid.')