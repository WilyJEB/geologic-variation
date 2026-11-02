"""Alternating paired CPU trials, exact sample/reopen checks, NEW bounded fixtures."""
import argparse
import json
from pathlib import Path
import re
import runpy
import shutil

live = runpy.run_path(str(Path(__file__).with_name('verify-live-context.py')))
h = live['helpers']; r = h['runtime']; require = h['require']


def measure(server, command):
    before = server.command('acceptance metrics')
    value = server.command(command)
    after = server.command('acceptance metrics')
    return {'value': value, 'delta': {k: after[k]-before[k] for k in before}}


def manifest(path):
    return {p.name: r['sha'](p) for p in sorted(path.iterdir()) if p.is_file()}


def sampler_run(args):
    require(shutil.disk_usage(args.output).free>=2*1024**3,'Need 2 GiB free')
    args.addon=args.candidate
    server=r['Server'](args,'sampler',link_td=True)
    try:
        server.start(); prepare=server.command('acceptance prepare')
        require(prepare['backend']=='CPU','CPU required')
        values=[server.command(f'acceptance sampler-cost {x} {z}') for x,z in [(-1024,-1536),(512,-1024)]]
        server.stop();h['storage_ok'](server)
        return {'prepare':prepare,'samples':values,'artifacts':manifest(server.path/'mods'),
                'logs':{p.name:r['sha'](p) for p in server.path.glob('console-*.log')},'exit_code':server.process.returncode}
    finally:
        try:h['close'](server)
        finally:
            if hasattr(server,'process') and server.process.poll() is None:
                server.process.kill();server.process.wait(timeout=30)
            h['cleanup_cache'](server)


def run(args):
    require(r['sha'](args.td) == '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8', 'CPU pin')
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = manifest(args.models)
    template = {p.relative_to(args.template).as_posix(): r['sha'](p) for p in args.template.rglob('*') if p.is_file()}
    result = {'mode': args.mode, 'models': inputs, 'cases': []}
    result['sources'] = {p.name:r['sha'](p) for p in [Path(__file__),Path(__file__).with_name('runtime-acceptance.py')]}
    if args.sampler_only:
        result['sampler']=sampler_run(args)
        require(inputs==manifest(args.models),'Shared models changed')
        require(template=={p.relative_to(args.template).as_posix():r['sha'](p) for p in args.template.rglob('*') if p.is_file()},'Template changed')
        result['shared_inputs_unchanged']=True
        (args.output/'sampler-results.json').write_text(json.dumps(result,indent=2)+'\n')
        return
    for trial in range(args.trial_start,args.trial_start+args.trials):
        arms = ['td', 'old'] if args.mode == 'baseline' else ['td', 'old', 'new']
        if trial % 2: arms.reverse()
        for arm in arms:
            free = shutil.disk_usage(args.output).free
            require(free >= 2*1024**3, 'Need 2 GiB free before launch')
            args.addon = args.baseline if arm != 'new' else args.candidate
            server = r['Server'](args, f't{trial}-{arm}', addon=arm != 'td', link_td=True)
            item = {'trial': trial, 'arm': arm, 'free_bytes': free, 'chunks': [], 'regions': []}
            try:
                server.start()
                item['prepare'] = server.command('acceptance prepare')
                require(item['prepare']['backend'] == 'CPU', 'Wrong backend')
                plan = r['targets'](server.seed, 1)
                item['plan'] = plan
                for x,z in plan['chunks']:
                    item['chunks'].append(measure(server, f'acceptance chunk overworld {x} {z}'))
                x,z = plan['chunks'][0]
                item['warm_chunk'] = measure(server, f'acceptance chunk overworld {x} {z}')
                if arm != 'td':
                    item['settings'] = server.command('acceptance settings')
                    require('models=64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' in item['settings']['context'], 'Model context')
                    for x,z in plan['region_points']:
                        item['regions'].append(measure(server, f'acceptance region {x} {z}'))
                    item['cold_region'] = measure(server, 'acceptance region 8192 8192')
                    item['warm_region'] = measure(server, 'acceptance region 8192 8192')
                    item['concurrent'] = measure(server, 'acceptance concurrent 4096 4096')
                    if args.mode == 'candidate' and arm == 'new' and trial == 0:
                        item['elevation_checks'] = [server.command(f'acceptance elevation-check {x} {z}')
                                                   for x,z in [(-1024,-1536),(512,-1024)]]
                server.stop(); h['storage_ok'](server)
                world = server.path/'world'
                item['terrain_before'] = live['terrain'](world)
                item['snapshot_before'] = h['preserve'](world)['snapshot']
                item['region_files_before'] = h['preserve'](world)['regions']
                h['cleanup_cache'](server)
                # Reopen every addon case, independently from timing the fresh route.
                if arm != 'td':
                    require(shutil.disk_usage(args.output).free >= 2*1024**3, 'Need 2 GiB before reopen')
                    server.start()
                    item['reopened'] = [server.command(f'acceptance chunk overworld {x} {z}') for x,z in plan['chunks']]
                    item['reopened_regions'] = [server.command(f'acceptance region {x} {z}') for x,z in plan['region_points']]
                    server.stop(); h['storage_ok'](server)
                    item['terrain_after'] = live['terrain'](world)
                    item['snapshot_after'] = h['preserve'](world)['snapshot']
                    item['region_files_after'] = h['preserve'](world)['regions']
                    require(item['terrain_before'] == item['terrain_after'], 'Persisted terrain/status/coverage changed')
                    require(item['snapshot_before'] == item['snapshot_after'], 'Snapshot changed')
                    require([c['value']['blocks_sha256'] for c in item['chunks']] == [c['blocks_sha256'] for c in item['reopened']], 'Reopened complete blocks changed')
                    require([c['value']['region'] for c in item['regions']] == [c['region'] for c in item['reopened_regions']], 'Reopened identities changed')
                    h['cleanup_cache'](server)
                item['artifacts'] = manifest(server.path/'mods')
                item['logs'] = {p.name:r['sha'](p) for p in server.path.glob('console-*.log')}
                text = (server.path/'console-1.log').read_text(errors='replace')
                item['td_uncached_requests'] = len(re.findall('uncached region requested:', text))
                item['td_logged_windows'] = [int(n) for n in re.findall(r'\((\d+) newly computed windows\)', text)]
                item['exit_code'] = server.process.returncode
                result['cases'].append(item)
                (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
            finally:
                try: h['close'](server)
                finally:
                    if hasattr(server,'process') and server.process.poll() is None:
                        server.process.kill(); server.process.wait(timeout=30)
                    if hasattr(server,'console') and not server.console.closed: server.console.close()
    require(inputs == manifest(args.models), 'Shared models changed')
    require(template == {p.relative_to(args.template).as_posix():r['sha'](p) for p in args.template.rglob('*') if p.is_file()}, 'Template changed')
    result['shared_inputs_unchanged'] = True
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['baseline','candidate'])
    p.add_argument('--trials',type=int,default=3)
    p.add_argument('--trial-start',type=int,default=0)
    p.add_argument('--sampler-only',action='store_true')
    for name in ('java','td','baseline','candidate','output'):
        p.add_argument('--'+name,type=Path,required=name != 'candidate')
    for name,default in [('runtime','runs/acceptance/runtime'),('models','runs/server/terrain-diffusion-models'),('template','runs/server/world'),('probe','build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar')]:
        p.add_argument('--'+name,type=Path,default=r['ROOT']/default)
    args=p.parse_args()
    run(args)
