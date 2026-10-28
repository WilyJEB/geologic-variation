"""Compare final saved block states from two disposable acceptance worlds."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import runpy
import zlib

read_nbt = runpy.run_path(str(Path(__file__).with_name('runtime-acceptance.py')))['nbt_read']


def plain(kind, value):
    if kind == 10:
        return {name: plain(t, v) for name, (t, v) in value.items()}
    if kind == 9:
        subtype, entries = value
        return [plain(subtype, v) for v in entries]
    return value


def blocks(world, x, z):
    raw = (world / 'region' / f'r.{x//32}.{z//32}.mca').read_bytes()
    slot = (x % 32) + (z % 32) * 32
    offset = int.from_bytes(raw[slot*4:slot*4+3], 'big') * 4096
    if not offset:
        raise ValueError(f'Missing chunk {x},{z}')
    size = int.from_bytes(raw[offset:offset+4], 'big')
    codec = raw[offset+4]
    data = raw[offset+5:offset+4+size]
    decoded = {1: gzip.decompress, 2: zlib.decompress, 3: lambda b: b}[codec](data)
    kind, _, value = read_nbt(decoded)
    chunk = plain(kind, value)
    result = {}
    for section in chunk['sections']:
        state = section.get('block_states')
        if not state:
            continue
        palette = state['palette']
        bits = max(4, (len(palette)-1).bit_length())
        per_long = 64 // bits
        for index in range(4096):
            selected = 0 if len(palette) == 1 else ((state['data'][index//per_long] & ((1<<64)-1)) >> ((index % per_long)*bits)) & ((1<<bits)-1)
            pos = (x*16+index % 16, section['Y']*16+index//256, z*16+(index//16) % 16)
            result[pos] = palette[selected]
    return result


def compare(a, b, coordinates):
    all_changes, regional_changes = Counter(), Counter()
    conflicts, examples = [], []
    for x, z in coordinates:
        left, right = blocks(a, x, z), blocks(b, x, z)
        assert left.keys() == right.keys(), 'Chunk vertical coverage differs'
        for pos in left:
            la, lb = left[pos], right[pos]
            if la == lb:
                continue
            pair = la['Name'], lb['Name']
            all_changes[pair] += 1
            regional = [name.startswith('geologic_variation:') for name in pair]
            if any(regional):
                regional_changes[pair] += 1
                if len(examples) < 12:
                    examples.append({'position': pos, 'left': la, 'right': lb})
            if all(regional) and pair[0] != pair[1]:
                conflicts.append({'position': pos, 'left': pair[0], 'right': pair[1]})
    return {'chunks': coordinates, 'all_changed_blocks': sum(all_changes.values()),
            'vanilla_stone_transitions': [{'left': a, 'right': b, 'count': n} for (a,b),n in sorted(all_changes.items()) if 'minecraft:stone' in (a,b)],
            'regional_changed_blocks': sum(regional_changes.values()),
            'regional_transitions': [{'left': a, 'right': b, 'count': n} for (a,b),n in sorted(regional_changes.items())],
            'palette_conflicts': conflicts, 'regional_examples': examples}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('left', type=Path)
    parser.add_argument('right', type=Path)
    parser.add_argument('--chunks', required=True, help='JSON array of [chunkX,chunkZ] pairs')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.left, args.right, json.loads(args.chunks))
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps({k:v for k,v in result.items() if k != 'regional_examples'}, indent=2))
