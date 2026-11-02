"""Stage-isolated #5/#6 production checks. Uses NEW disposable worlds only."""
import argparse
import json
from pathlib import Path
import runpy

runtime = runpy.run_path(str(Path(__file__).with_name('runtime-acceptance.py')))
ROOT = runtime['ROOT']


def run(args):
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    if args.fixture_only:
        server = runtime['Server'](args,'host-fixtures',addon=True,scale=1)
        try:
            server.start()
            results = {name:server.command('acceptance '+name) for name in ('hosts','ore-order')}
            server.stop()
            results['artifacts'] = {p.name:runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))}
            results['logs'] = {p.name:runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))}
            (args.output/'fixture-results.json').write_text(json.dumps(results,indent=2)+'\n')
        finally:
            if hasattr(server,'process') and server.process.poll() is None:
                server.stop()
        return
    for scale in (1, 6):
        for trial in (0, 1):
            for addon in (False, True):
                name = f'stages-s{scale}-t{trial}-' + ('addon' if addon else 'td-only')
                server = runtime['Server'](args, name, addon=addon, scale=scale)
                plan = runtime['targets'](server.seed, scale)
                order = list(plan['chunks'])
                if trial:
                    order.reverse()
                row = {'name': name, 'scale': scale, 'trial': trial, 'addon': addon, 'plan': plan,
                       'artifacts': {p.name: runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))},
                       'stages': {}}
                try:
                    server.start()
                    for stage in ('surface', 'carvers', 'full'):
                        row['stages'][stage] = [server.command(f'acceptance stage {stage} {x} {z}') for x,z in order]
                    if addon:
                        row['regions'] = [server.command(f'acceptance region {x} {z}') for x,z in plan['region_points']]
                    server.stop()
                    row['logs'] = {p.name: runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))}
                finally:
                    if hasattr(server,'process') and server.process.poll() is None:
                        server.stop()
                results.append(row)
                (args.output/'stage-results.json').write_text(json.dumps(results,indent=2)+'\n')
    comparisons = []
    keyed = lambda rows,field: {(c['x'],c['z']):c[field] for c in rows}
    for scale in (1,6):
        rows = [r for r in results if r['scale']==scale]
        for stage in ('surface','carvers','full'):
            arms = {}
            for addon in (False,True):
                pair = [r for r in rows if r['addon']==addon]
                arms['addon' if addon else 'td_only'] = {
                    'full_states_equal': keyed(pair[0]['stages'][stage],'blocks_sha256')==keyed(pair[1]['stages'][stage],'blocks_sha256'),
                    'regional_positions_equal': keyed(pair[0]['stages'][stage],'geology_sha256')==keyed(pair[1]['stages'][stage],'geology_sha256')}
            normalized = []
            for trial in (0,1):
                pair = [r for r in rows if r['trial']==trial]
                normalized.append(keyed(pair[0]['stages'][stage],'normalized_sha256')==keyed(pair[1]['stages'][stage],'normalized_sha256'))
            comparisons.append({'scale':scale,'stage':stage,'traversal':arms,'normalized_addon_vs_td_only':normalized})
    (args.output/'comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    print(json.dumps(comparisons,indent=2))
    for row in comparisons:
        if row['stage']!='full' and (not all(row['normalized_addon_vs_td_only']) or
            not all(arm['full_states_equal'] for arm in row['traversal'].values())):
            raise RuntimeError(f"Surface/carver contract failed: {row}")
    for row in results:
        if row['addon'] and any(not any(name.startswith('geologic_variation:') for name in c['counts'])
                                for c in row['stages']['surface']):
            raise RuntimeError('Empty regional sample cannot certify host replacement')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--td',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--fixture-only',action='store_true',help='Run destructive host/ore-order fixtures without the stage matrix')
    parser.add_argument('--runtime',type=Path,default=ROOT/'runs/acceptance/runtime')
    parser.add_argument('--models',type=Path,default=ROOT/'runs/server/terrain-diffusion-models')
    parser.add_argument('--template',type=Path,default=ROOT/'runs/server/world')
    parser.add_argument('--addon',type=Path,default=ROOT/'build/libs/geologic-variation-0.2.2-dev.jar')
    parser.add_argument('--probe',type=Path,default=ROOT/'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar')
    args = parser.parse_args()
    for name,value in vars(args).items():
        if isinstance(value,Path):
            setattr(args,name,value.resolve())
    run(args)
