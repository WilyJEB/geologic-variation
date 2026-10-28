"""Opt-in disposable production-server acceptance. Requires the separate runtime probe.

Never points a server at the template: only level metadata is copied to a NEW folder.
Worlds, models, logs and full machine paths stay under the ignored output directory.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def nbt_read(raw):
    stream = io.BytesIO(raw)
    def read(fmt):
        return struct.unpack('>' + fmt, stream.read(struct.calcsize('>' + fmt)))[0]
    def string():
        return stream.read(read('H')).decode('utf-8')
    def payload(kind):
        if kind in (1, 2, 3, 4, 5, 6):
            return read({1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}[kind])
        if kind == 7:
            return stream.read(read('i'))
        if kind == 8:
            return string()
        if kind == 9:
            subtype, count = read('B'), read('i')
            return (subtype, [payload(subtype) for _ in range(count)])
        if kind == 10:
            result = {}
            while (subtype := read('B')):
                name = string()
                result[name] = (subtype, payload(subtype))
            return result
        if kind in (11, 12):
            return [read('i' if kind == 11 else 'q') for _ in range(read('i'))]
        raise ValueError(f'Unsupported NBT type {kind}')
    kind = read('B')
    name = string()
    return kind, name, payload(kind)


def nbt_write(tag):
    out = io.BytesIO()
    def write(fmt, value):
        out.write(struct.pack('>' + fmt, value))
    def string(value):
        raw = value.encode('utf-8')
        write('H', len(raw))
        out.write(raw)
    def payload(kind, value):
        if kind in (1, 2, 3, 4, 5, 6):
            write({1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}[kind], value)
        elif kind == 7:
            write('i', len(value))
            out.write(value)
        elif kind == 8:
            string(value)
        elif kind == 9:
            subtype, items = value
            write('B', subtype)
            write('i', len(items))
            for item in items:
                payload(subtype, item)
        elif kind == 10:
            for name, (subtype, item) in value.items():
                write('B', subtype)
                string(name)
                payload(subtype, item)
            write('B', 0)
        elif kind in (11, 12):
            write('i', len(value))
            for item in value:
                write('i' if kind == 11 else 'q', item)
        else:
            raise ValueError(kind)
    kind, name, value = tag
    write('B', kind)
    string(name)
    payload(kind, value)
    return out.getvalue()


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


MASK = (1 << 64) - 1


def mix(value):
    value &= MASK
    value = ((value ^ (value >> 30)) * 0xbf58476d1ce4e5b9) & MASK
    value = ((value ^ (value >> 27)) * 0x94d049bb133111eb) & MASK
    return value ^ (value >> 31)


def province(seed, scale, x, z):
    """Target selection only; runtime probe independently reports actual Java results."""
    spacing = 2048 * scale
    best = None
    for gz in range(z // spacing - 1, z // spacing + 2):
        for gx in range(x // spacing - 1, x // spacing + 2):
            mz = mix(gz)
            identity = mix(seed ^ mix(gx) ^ (((mz << 29) | (mz >> 35)) & MASK))
            unit = lambda n: (mix(n) >> 11) / (1 << 53)
            ax = int((gx + .25 + unit(identity) * .5) * spacing // 1)
            az = int((gz + .25 + unit(identity ^ 0x72bd) * .5) * spacing // 1)
            candidate = ((x - ax)**2 + (z - az)**2, gx, gz, ax, az)
            if best is None or candidate[0] < best[0]:
                best = candidate
    return best[1:]


def targets(seed, scale):
    z = -1024 * scale
    old_x = -4096 * scale
    old = province(seed, scale, old_x, z)[:2]
    boundaries = []
    for x in range(old_x + 16, 4096 * scale, 16):
        new = province(seed, scale, x, z)[:2]
        if new != old:
            edge = next(q for q in range(x - 15, x + 1) if province(seed, scale, q, z)[:2] != old)
            boundaries.append(edge)
        old = new
    if not boundaries:
        raise RuntimeError('No province boundary found')
    # Closest boundary to the independently observed land near native (-508,-1027).
    edge = min(boundaries, key=lambda x: abs(x + 508 * scale))
    chunks = sorted({((edge-1)//16,z//16),(edge//16,z//16),
                     (edge//16-1,z//16),(edge//16+1,z//16),
                     ((-508*scale)//16,(-1027*scale)//16)})
    return {'edge': [edge,z], 'chunks': chunks, 'region_points': [[edge-1,z],[edge,z]]}


class Server:
    def __init__(self, args, name, addon=True, scale=1, vanilla=False, probe=True):
        self.args = args
        self.path = args.output / name
        self.path.mkdir(parents=True, exist_ok=False)
        self.password = os.urandom(18).hex()
        for folder in ('mods', 'config', 'world/data', 'terrain-diffusion-models'):
            (self.path / folder).mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.td, self.path / 'mods' / args.td.name)
        if addon:
            shutil.copy2(args.addon, self.path / 'mods' / args.addon.name)
        if probe:
            shutil.copy2(args.probe, self.path / 'mods' / args.probe.name)
        for model in args.models.iterdir():
            if model.is_file():
                os.link(model, self.path / 'terrain-diffusion-models' / model.name)
        (self.path / 'eula.txt').write_text('eula=true\n')
        (self.path / 'server.properties').write_text(
            'server-ip=127.0.0.1\nserver-port=25587\nonline-mode=false\n'
            'enable-rcon=true\nrcon.port=25588\nrcon.password=' + self.password + '\n'
            'max-players=1\nview-distance=2\nsimulation-distance=2\nmax-tick-time=-1\n'
            'spawn-protection=0\nlevel-name=world\n')
        shutil.copy2(ROOT / 'runs/server/config/terrain-diffusion-mc.properties', self.path / 'config/terrain-diffusion-mc.properties')
        # Metadata-only deterministic fixture: never copy chunks between different scales.
        tag = nbt_read(gzip.decompress((args.template / 'level.dat').read_bytes()))
        data = tag[2]['Data'][1]
        self.seed = data['WorldGenSettings'][1]['seed'][1]
        data['GameRules'][1].update({name: (8, value) for name, value in {
            'spawnChunkRadius': '0', 'randomTickSpeed': '0', 'doMobSpawning': 'false',
            'doWeatherCycle': 'false', 'doDaylightCycle': 'false'}.items()})
        data.pop('Player', None)
        if vanilla:
            dims = data['WorldGenSettings'][1]['dimensions'][1]
            dims['minecraft:overworld'][1]['generator'] = (10, {
                'type': (8, 'minecraft:noise'), 'settings': (8, 'minecraft:overworld'),
                'biome_source': (10, {'type': (8, 'minecraft:multi_noise'), 'preset': (8, 'minecraft:overworld')})})
        (self.path / 'world/level.dat').write_bytes(gzip.compress(nbt_write(tag), mtime=0))
        scale_tag = nbt_read(gzip.decompress((args.template / 'data/terrain_diffusion_world_settings.dat').read_bytes()))
        scale_tag[2]['data'][1]['scale'] = (3, scale)
        (self.path / 'world/data/terrain_diffusion_world_settings.dat').write_bytes(gzip.compress(nbt_write(scale_tag), mtime=0))
        if addon and not vanilla:
            snapshot = (args.template / 'data/geologic_variation-geology.properties').read_text()
            snapshot = re.sub(r'^scale=\d+$', f'scale={scale}', snapshot, flags=re.M)
            (self.path / 'world/data/geologic_variation-geology.properties').write_text(snapshot)
        self.start_count = 0

    def start(self):
        self.start_count += 1
        argfile = self.args.runtime / 'libraries/net/neoforged/neoforge/21.1.251/win_args.txt'
        lib = (self.args.runtime / 'libraries').as_posix()
        launch = argfile.read_text().replace('libraries/', lib + '/').replace('-DlibraryDirectory=libraries', '-DlibraryDirectory=' + lib)
        (self.path / 'launch-args.txt').write_text(launch)
        self.console = (self.path / f'console-{self.start_count}.log').open('w')
        self.process = subprocess.Popen([str(self.args.java), '-Xms2G', '-Xmx6G', '@launch-args.txt', '--nogui'],
            cwd=self.path, stdin=subprocess.PIPE, stdout=self.console, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        deadline = time.monotonic() + 360
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f'{self.path.name} server exited {self.process.returncode}; inspect console')
            log = (self.path / f'console-{self.start_count}.log').read_text(errors='replace')
            if 'Done (' in log and 'RCON running on' in log:
                self.command('tick freeze')
                return
            time.sleep(1)
        raise TimeoutError(f'{self.path.name} did not start')

    def command(self, command):
        def exact(sock, count):
            buf = b''
            while len(buf) < count:
                part = sock.recv(count - len(buf))
                if not part:
                    raise EOFError('RCON closed')
                buf += part
            return buf
        def packet(sock, kind, body, ident):
            raw = struct.pack('<ii', ident, kind) + body.encode() + b'\0\0'
            sock.sendall(struct.pack('<i', len(raw)) + raw)
        def reply(sock):
            size = struct.unpack('<i', exact(sock, 4))[0]
            raw = exact(sock, size)
            return struct.unpack('<ii', raw[:8]), raw[8:-2].decode()
        with socket.create_connection(('127.0.0.1', 25588), timeout=300) as sock:
            packet(sock, 3, self.password, 1)
            assert reply(sock)[0] == (1, 2), 'RCON authentication failed'
            packet(sock, 2, command, 2)
            head, body = reply(sock)
            assert head[0] == 2
        if command.startswith('acceptance '):
            if not body.startswith('ACCEPTANCE '):
                raise RuntimeError(f'Probe failed: {body}')
            result = json.loads(body[len('ACCEPTANCE '):].strip())
            print(self.path.name, command, round(result.get('generation_ms', result.get('wall_ms', 0)), 2), flush=True)
            return result
        return body

    def stop(self):
        self.command('save-all flush')
        self.command('stop')
        self.process.wait(timeout=90)
        self.console.close()
        if self.process.returncode:
            raise RuntimeError(f'Server shutdown failed: {self.process.returncode}')


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {'addon_sha256': sha(args.addon), 'td_sha256': sha(args.td), 'probe_sha256': sha(args.probe)}
    (args.output / 'artifacts.json').write_text(json.dumps(metadata, indent=2))
    if args.mode == 'smoke':
        server = Server(args, 'packaged-smoke', scale=2, probe=False)
        # Use the already verified disposable world for interactive packaged client acceptance.
        shutil.copytree(args.template, server.path / 'world', dirs_exist_ok=True)
        try:
            server.start()
            print('PACKAGED SERVER READY: join 127.0.0.1:25587; create STOP in the case directory to save and stop.', flush=True)
            while not (server.path / 'STOP').exists() and server.process.poll() is None:
                time.sleep(1)
            if not (server.path / 'STOP').exists():
                raise RuntimeError('Packaged smoke server exited before the requested STOP')
        finally:
            if hasattr(server,'process') and server.process.poll() is None:
                server.stop()
        return
    if args.mode == 'gating':
        results = []
        for addon in (False, True):
            server = Server(args, 'gating-' + ('addon' if addon else 'td-only'), addon=addon, vanilla=True)
            try:
                server.start()
                chunks = [server.command(f'acceptance chunk {dimension} 0 0')
                          for dimension in ('overworld', 'the_nether', 'the_end')]
                server.stop()
            finally:
                if hasattr(server, 'process') and server.process.poll() is None:
                    server.stop()
            assert not (server.path / 'world/data/geologic_variation-geology.properties').exists()
            assert all(not any(k.startswith('geologic_variation:') for k in c['counts']) for c in chunks)
            results.append(chunks)
        assert [c['blocks_sha256'] for c in results[0]] == [c['blocks_sha256'] for c in results[1]], 'Dimension gating mismatch'
        (args.output / 'gating-results.json').write_text(json.dumps(results, indent=2))
        print('COMPLETED gating', flush=True)
        return
    results = []
    reproducibility = args.mode in ('reproducibility', 'order-control')
    scales = [1, 6] if args.mode == 'reproducibility' else ([6] if args.mode == 'order-control' else [1])
    for scale in scales:
        for trial in range(2 if reproducibility else 3):
            arms = [args.mode == 'reproducibility'] if reproducibility else ([False, True] if trial % 2 == 0 else [True, False])
            for addon in arms:
                name = f'{args.mode}-s{scale}-t{trial}-' + ('addon' if addon else 'td-only')
                server = Server(args, name, addon=addon, scale=scale)
                plan = targets(server.seed, scale)
                order = list(plan['chunks'])
                if reproducibility and trial == 1:
                    order.reverse()
                item = {'name': name, 'scale': scale, 'addon': addon, 'trial': trial, 'plan': plan, 'chunks': [], 'regions': []}
                try:
                    server.start()
                    if args.mode == 'performance':
                        item['prepare'] = server.command('acceptance prepare')
                    for x, z in order:
                        item['chunks'].append(server.command(f'acceptance chunk overworld {x} {z}'))
                    x, z = order[0]
                    item['warm_chunk'] = server.command(f'acceptance chunk overworld {x} {z}')
                    if addon:
                        for x, z in plan['region_points']:
                            item['regions'].append(server.command(f'acceptance region {x} {z}'))
                        # A separate remote province exercises simultaneous cold misses.
                        if args.mode == 'performance':
                            x, z = 4096 * scale, 4096 * scale
                            item['concurrent'] = server.command(f'acceptance concurrent {x} {z}')
                            item['warm_region'] = server.command(f'acceptance region {x} {z}')
                            item['cache_policy'] = server.command('acceptance cache-policy')
                    server.stop()
                    snapshot = server.path / 'world/data/geologic_variation-geology.properties'
                    if addon:
                        item['snapshot_before'] = sha(snapshot)
                    if reproducibility:
                        server.start()
                        item['reopened'] = [server.command(f'acceptance chunk overworld {x} {z}') for x, z in order]
                        # Fresh neighboring column, generated only after a full process restart.
                        x, z = min(plan['chunks'])
                        item['neighbor'] = server.command(f'acceptance chunk overworld {x} {z-1}')
                        server.stop()
                        if addon:
                            item['snapshot_after'] = sha(snapshot)
                            assert item['snapshot_before'] == item['snapshot_after'], 'Snapshot changed on reopen'
                finally:
                    if hasattr(server, 'process') and server.process.poll() is None:
                        try:
                            server.stop()
                        except Exception:
                            server.process.terminate()
                            server.process.wait(timeout=30)
                results.append(item)
                (args.output / f'{args.mode}-results.json').write_text(json.dumps(results, indent=2))
    if args.mode == 'reproducibility':
        for scale in scales:
            pair = [r for r in results if r['scale'] == scale]
            keyed = lambda rows: {(c['x'], c['z']): c['geology_sha256'] for c in rows}
            assert keyed(pair[0]['chunks']) == keyed(pair[1]['chunks']), f'Traversal mismatch at scale {scale}'
            for row in pair:
                assert keyed(row['chunks']) == keyed(row['reopened']), 'Reopen mismatch'
                assert any(any(k.startswith('geologic_variation:') for k in c['counts']) for c in row['chunks']), 'Empty geology samples cannot establish block reproducibility'
            assert [r['region'] for r in pair[0]['regions']] == [r['region'] for r in pair[1]['regions']], 'Region result mismatch'
            assert pair[0]['neighbor']['geology_sha256'] == pair[1]['neighbor']['geology_sha256'], 'Neighbor mismatch'
    print('COMPLETED', args.mode, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['smoke', 'reproducibility', 'performance', 'gating', 'order-control'])
    parser.add_argument('--java', type=Path, required=True)
    parser.add_argument('--td', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, default=ROOT / 'runs/acceptance/runtime')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--models', type=Path, default=ROOT / 'runs/server/terrain-diffusion-models')
    parser.add_argument('--template', type=Path, default=ROOT / 'runs/server/world')
    parser.add_argument('--addon', type=Path, default=ROOT / 'build/libs/geologic-variation-0.2.2-dev.jar')
    parser.add_argument('--probe', type=Path, default=ROOT / 'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar')
    args = parser.parse_args()
    for name in ('java', 'td', 'runtime', 'output', 'models', 'template', 'addon', 'probe'):
        setattr(args, name, getattr(args, name).resolve())
    run(args)
