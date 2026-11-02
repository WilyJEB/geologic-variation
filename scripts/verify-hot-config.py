"""Bounded real file-watcher reload in two fresh, continuing CPU fixture copies."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import time

live = runpy.run_path(str(Path(__file__).with_name('verify-live-context.py')))
h = live['helpers']; runtime = h['runtime']; ROOT = runtime['ROOT']; require = h['require']
EXPECTED = 'GeologySettings[provinceSpacingBlocks=4096, oceanCeilingMetres=-300.0, lowlandCeilingMetres=700.0, mountainFloorMetres=1900.0, gentleReliefMetres=350.0, ruggedReliefMetres=650.0]'


def manifest(world):
    return {p.relative_to(world).as_posix(): runtime['sha'](p) for p in sorted(world.rglob('*')) if p.is_file()}


def run(args):
    require(runtime['sha'](args.td) == '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8', 'TD pin mismatch')
    require(runtime['sha'](args.addon) == '39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226', 'Production addon changed')
    fixture_before = manifest(args.fixture)
    require(fixture_before[h['SNAPSHOT'].as_posix()] == 'c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d', 'Unverified fixture snapshot')
    args.output.mkdir(parents=True, exist_ok=False)
    result = {'source_baseline': '127e36f8f35718916b56deae1712086909f54168', 'cases': []}
    for route in ('cached', 'uncached'):
        free = shutil.disk_usage(args.output).free
        require(free >= 2 * 1024**3, 'Need 2 GiB free before launch')
        server = runtime['Server'](args, route, scale=1, link_td=True)
        world = server.path / 'world'
        shutil.copytree(args.fixture, world, dirs_exist_ok=True)
        snapshot = (world / h['SNAPSHOT']).read_bytes()
        try:
            server.start(); pid = server.process.pid
            before = h['observe'](server)
            require('models=64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' in before['settings']['context'], 'Model pin mismatch')
            require('backend=CPU/Windows 11/amd64' in before['settings']['context'], 'Backend mismatch')
            require(before['settings']['active'] == before['settings']['requested'], 'Initial proposals differ')
            require(any(k.startswith('geologic_variation:') and v > 0 for k,v in before['chunk']['counts'].items()), 'Empty geology sample')
            server.command('save-all flush')
            preserved = h['preserve'](world); terrain_before = live['terrain'](world)
            require(terrain_before, 'Empty persisted terrain')
            server.command('acceptance reload-cache clear')
            primed = server.command('acceptance reload-cache query')
            require(primed['entries_before'] == 0 and primed['entries_after'] == 1 and primed['region'] == before['region'], 'Cache priming failed')
            if route == 'uncached':
                cleared = server.command('acceptance reload-cache clear')
                require(cleared['entries_after'] == 0, 'Cache not empty')
            initial_events = server.command('acceptance reload-events')['events']
            require(not initial_events, 'Unexpected reload before edit')
            config = server.path / 'config/geologic_variation-common.toml'
            config_before = runtime['sha'](config)
            cursor = len(h['log'](server).read_text(errors='replace'))
            h['edited_config'](server)  # External disk edit, with the original server still running.
            deadline = time.monotonic() + 30
            events = []
            while time.monotonic() < deadline:
                require(server.process.poll() is None, 'Server exited during reload')
                events = server.command('acceptance reload-events')['events']
                if events:
                    break
                time.sleep(.25)
            require(events, 'No actual Reloading event within 30 seconds')
            require(all(e['event'] == 'net.neoforged.fml.event.config.ModConfigEvent$Reloading'
                        and e['type'] == 'COMMON' and e['file'] == config.name and e['spec_matches']
                        and e['watcher_stack'] and e['requested'] == EXPECTED for e in events), 'Unexpected reload source or proposals')
            suffix = h['log'](server).read_text(errors='replace')[cursor:]
            require("Saved world settings remain active; edits apply only to new worlds." in suffix, 'Missing live saved-settings warning')
            after_settings = server.command('acceptance settings')
            require(after_settings == {**before['settings'], 'requested': EXPECTED}, 'Saved active settings/context changed')
            queried = server.command('acceptance reload-cache query')
            require(queried['entries_before'] == (1 if route == 'cached' else 0), 'Wrong post-reload cache precondition')
            require(queried['entries_after'] == 1 and queried['region'] == before['region'], 'Geology changed')
            require(queried['thread'] == 'Server thread', 'Wrong query thread')
            require(queried['heightmap_calls'] == 0 if route == 'cached' else queried['heightmap_calls'] > 0, 'Cache route not exercised')
            after = h['observe'](server)
            require(after['chunk']['blocks_sha256'] == before['chunk']['blocks_sha256'] and after['region'] == before['region'], 'Live blocks/geology changed')
            require(server.process.pid == pid and server.process.poll() is None, 'Not a continuing process')
            require((world / h['SNAPSHOT']).read_bytes() == snapshot, 'Live snapshot bytes changed')
            server.stop(); h['storage_ok'](server)
            saved = h['preserve'](world); terrain_saved = live['terrain'](world)
            require(terrain_before == terrain_saved and (world / h['SNAPSHOT']).read_bytes() == snapshot, 'Saved terrain/coverage/snapshot changed')
            h['cleanup_cache'](server)
            require(shutil.disk_usage(args.output).free >= 2 * 1024**3, 'Need 2 GiB before reopen')
            server.start(); reopened = h['observe'](server)
            reopen_pid = server.process.pid
            require(reopened['settings'] == after_settings and reopened['region'] == before['region'], 'Reopen settings/geology changed')
            require(reopened['chunk']['blocks_sha256'] == before['chunk']['blocks_sha256'], 'Reopen blocks changed')
            server.stop(); h['storage_ok'](server)
            final = h['preserve'](world); terrain_final = live['terrain'](world)
            require(terrain_before == terrain_final and (world / h['SNAPSHOT']).read_bytes() == snapshot, 'Reopen terrain/coverage/snapshot changed')
            item = {'name': route, 'free_bytes_before': free, 'pids': [pid, reopen_pid], 'exit_code': server.process.returncode,
                    'before': before, 'after': after, 'reopened': reopened, 'events': events, 'primed': primed, 'query': queried,
                    'config_before_sha256': config_before, 'config_after_sha256': runtime['sha'](config),
                    'preserved_before': preserved, 'preserved_saved': saved, 'preserved_reopened': final,
                    'terrain_before': terrain_before, 'terrain_saved': terrain_saved, 'terrain_reopened': terrain_final,
                    'artifacts': {p.name: runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))},
                    'logs': {p.name: runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))}}
            result['cases'].append(item)
            require(manifest(args.fixture) == fixture_before, 'Source fixture changed')
            result['fixture_unchanged'] = True
            (args.output/'hot-config-results.json').write_text(json.dumps(result, indent=2)+'\n')
            print('PASSED actual hot reload', route, flush=True)
        finally:
            try:
                h['close'](server)
            finally:
                if hasattr(server, 'process') and server.process.poll() is None:
                    server.process.kill(); server.process.wait(timeout=30)
                if hasattr(server, 'console') and not server.console.closed:
                    server.console.close()
                h['cleanup_cache'](server)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('java', 'td', 'output', 'fixture'):
        p.add_argument('--'+name, type=Path, required=True)
    for name, default in {'runtime':'runs/acceptance/runtime', 'models':'runs/server/terrain-diffusion-models',
                          'template':'runs/server/world', 'addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                          'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        p.add_argument('--'+name, type=Path, default=ROOT/default)
    args = p.parse_args()
    for name,value in vars(args).items():
        setattr(args,name,value.resolve())
    run(args)
