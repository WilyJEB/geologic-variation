"""Portable navigation-3 replay. Preparation and runtime evidence are distinct."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ('entry_setup', 'movement_scale1', 'movement_scale6', 'hud_toggle',
          'panel_return', 'seven_site_route', 'panel_pr58_pr59', 'exposure',
          'cover_west', 'cover_east', 'token_first_half', 'token_second_half',
          'configuration_1600_1000_gui2', 'configuration_1200_900_gui1',
          'scale_arithmetic', 'normal_shutdown', 'isolation', 'pid_tree_cleanup')
ROUTE = ((2944.,13824.), (2688.,10880.), (5760.,10880.), (2720.,10912.),
         (5760.,13952.), (5761.,13953.), (17664.,82944.))
CAPTURE_ROLES = dict(movement_scale1=('before','after'),movement_scale6=('before','after'),
    hud_toggle=('off','on'),panel_return=('hud-before','panel','hud-return'),
    panel_pr58_pr59=('pr58','pr59'),
    configuration_1600_1000_gui2=('settings','hud','panel','return'),
    configuration_1200_900_gui1=('settings','hud','panel','return'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate archive member')
        require(all(not Path(n).is_absolute() and '..' not in Path(n).parts and '\\' not in n for n in names), 'Unsafe member')
        return {n:archive.read(n) for n in names}


def preparation(data, strict=False):
    frozen = json.loads(data['docs/td-navigation-3-hashes.json'])
    for name, h in frozen['files'].items():
        require(sha(data[name]) == h, 'Prepared bytes differ: '+name)
        if strict and (ROOT/name).exists():
            require((ROOT/name).read_bytes() == data[name], 'Checkout differs: '+name)
    jar = data['artifact/retained-navigation-1.jar']
    require(sha(jar) == frozen['artifact_sha256'], 'Artifact differs')
    base = runpy.run_path(str(ROOT/'scripts/export-navigation-supplement.py'))
    base['scan'](jar)
    historical = members(io.BytesIO(data['docs/evidence/td-navigation-supplement.zip']))
    require(jar == historical['raw/final-compile-only.jar'], 'Must reuse exact decimal artifact')
    with zipfile.ZipFile(io.BytesIO(jar)) as archive:
        require(sha(archive.read('retained-map.tsv')) == frozen['files']['src/runtimeProbe/resources/retained-map.tsv'], 'Retained records changed')
    require(frozen['runtime_root_created'] is False and frozen['execution_authorized'] is False,
            'Preparation cannot allocate or authorize execution')
    return dict(mode='preparation', exact_bytes=True, runtime_acceptance='INCOMPLETE',
                native_process_api='offline mocks only; runtime-unverified')


def runtime(data):
    if 'ledger.json' not in data:
        return dict(mode='runtime',acceptance='INCOMPLETE',attempts_remaining=0,
                    unmet=['missing pre-spawn ledger; root tombstone consumes sole slot'])
    ledger = json.loads(data['ledger.json'])
    require(ledger['attempts_used'] == 1 and ledger['attempts_remaining'] == 0
            and ledger['charged_seconds'] == 1200, 'One-slot accounting')
    # Every partial package is replayable. Missing evidence returns incomplete;
    # contradictory/corrupt evidence raises rather than being silently waived.
    unmet = []
    def need(ok, name):
        if not ok:
            unmet.append(name)
    need(ledger.get('finalized') is True, 'finalization')
    need(ledger.get('status') == 'exited-evidence-pending' and ledger.get('exit_code') == 0, 'normal client exit')
    need(ledger.get('immutable_inputs_unchanged') is True, 'immutable recheck')
    executed = {n[len('executed/'):]:b for n,b in data.items() if n.startswith('executed/')}
    if 'docs/td-navigation-3-hashes.json' in executed:
        executed['artifact/retained-navigation-1.jar'] = executed['retained-navigation-1.jar']
        preparation(executed)
        digest=sha(executed['docs/td-navigation-3-hashes.json'])
        require(ledger.get('preflight',{}).get('manifest_sha256')==digest
                and ledger.get('approval',{}).get('manifest_sha256')==digest, 'Executed approval/preflight freeze differs')
    else:
        need(False, 'complete executed sources and artifact')
    inventory = json.loads(data.get('inventory.json', b'{}'))
    for name, row in inventory.items():
        if name == 'inventory.json':
            continue
        require(name in data and len(data[name]) == row['bytes'] and sha(data[name]) == row['sha256'], 'Inventory mismatch: '+name)
    need(bool(inventory), 'complete inventory')
    need(set(data)-{'inventory.json'} == set(inventory)-{'inventory.json'},'inventory covers every retained file')
    game = 'td-navigation-2/attempt-01/'
    dependencies = json.loads(data.get(game+'dependencies.json', b'{}'))
    preflight = ledger.get('preflight', {})
    inputs = {**preflight.get('shared', {}), **dependencies}
    if preflight.get('java_sha256'):
        inputs[preflight['context']['java']] = preflight['java_sha256']
    post = json.loads(data.get('shared-post.json', b'{}'))
    need(bool(inputs) and post == inputs, 'exact shared input hashes')
    if executed.get('retained-navigation-1.jar'):
        require(data.get(game+'mods/retained-navigation-1.jar') == executed['retained-navigation-1.jar'], 'Executed mod differs')
    console = data.get(game+'console.log', b'').decode(errors='replace')
    for token in ('guard fresh save ', 'guard fresh integrated server', 'guard local attachment',
                  'guard rejected ../continuing', 'guard rejected other-world', 'Stopping server', 'Stopping!'):
        need(token in console, token)
    need('FATAL' not in console and 'Exception' not in console, 'no runtime error')
    for n in data:
        if '/saves/' in n:
            require(n.startswith(game+'saves/navigation-only/'), 'Unexpected save root')
    debug=data.get(game+'logs/debug.log',b'').decode(errors='replace')
    for guard in ('SaveBarrier','WorldBarrier','TitleOnly','Hud','LanBarrier','Keys'):
        need('Mixing '+guard+' from retained-navigation.mixins.json' in debug, 'applied guard '+guard)
    loaded = data.get(game+'class-load.log', b'').decode(errors='replace').lower()
    forbid = runpy.run_path(str(ROOT/'scripts/export-navigation-supplement.py'))['FORBIDDEN']
    require(not any(s in loaded for s in forbid), 'Forbidden loaded class')
    need(bool(loaded), 'class load log')
    for n, b in data.items():
        if n.endswith('.jar'):
            runpy.run_path(str(ROOT/'scripts/export-navigation-supplement.py'))['scan'](b)
    samples = [json.loads(line) for line in data.get('monitor.jsonl', b'').splitlines()]
    need(bool(samples), 'monitor')
    caps = runpy.run_path(str(ROOT/'scripts/launch-navigation-3.py'))['cap_check']
    for s in samples:
        caps(s, s.get('has_position',False))
    cleanup = json.loads(data.get('cleanup.json', b'{}'))
    need(cleanup.get('job_empty') is True and not cleanup.get('remaining_job_pids')
         and cleanup.get('forced') is False and bool(cleanup.get('checks'))
         and all(c['absent'] for c in cleanup.get('checks', [])), 'normal shutdown and exact tree absence')
    process_rows = [json.loads(line) for line in data.get('processes.jsonl', b'').splitlines()]
    known = {(i['ProcessId'], str(i['CreationDate'])) for r in process_rows for i in r.get('identities', [])}
    checked = {(c['identity']['ProcessId'], str(c['identity']['CreationDate'])) for c in cleanup.get('checks', [])}
    need(bool(known) and known == checked, 'every observed process identity queried')
    pattern = r'RETAINED_NAV position (\S+) (\S+) scale (\d+) block (-?\d+) (-?\d+) chunk (-?\d+) (-?\d+) support (\w+)'
    positions = []
    for m in re.finditer(pattern, console):
        x,z = map(float,m.group(1,2)); scale,bx,bz,cx,cz = map(int,m.group(3,4,5,6,7))
        require(math.isfinite(x) and math.isfinite(z) and scale in (1,6), 'Position arithmetic')
        require((bx,bz,cx,cz) == (math.floor(x),math.floor(z),math.floor(x)//16,math.floor(z)//16), 'Floor/chunk arithmetic')
        positions.append(dict(x=x,z=z,scale=scale,support=m.group(8),offset=m.start()))
    for i, (x,z) in enumerate(ROUTE):
        route = console.find('RETAINED_NAV route '+str(i))
        next_route = console.find('RETAINED_NAV route ', route+1) if route >= 0 else -1
        need(route >= 0 and any(p['x']==x and p['z']==z and p['scale']==(6 if i==6 else 1)
             and p['offset']>route and (next_route<0 or p['offset']<next_route) for p in positions), 'exact route '+str(i))
    actions = json.loads(data.get('actions.json', b'{}'))
    need(actions.get('execution_kind') == 'actual-client', 'actual-client evidence')
    rows = actions.get('checks', {})
    need(set(rows) == set(CHECKS), 'complete checklist')
    for name in CHECKS:
        row = rows.get(name, {})
        need(row.get('result') == 'pass' and bool(row.get('observation'))
             and bool(row.get('evidence')), name)
        for ref in row.get('evidence', []):
            require(ref['path'] in data and sha(data[ref['path']]) == ref['sha256'], 'Action reference hash')
        if name not in ('scale_arithmetic', 'normal_shutdown', 'isolation', 'pid_tree_cleanup'):
            need(any(ref['path'].lower().endswith(('.png','.jpg','.jpeg')) for ref in row.get('evidence', [])), 'image '+name)
        roles=CAPTURE_ROLES.get(name,())
        images={ref.get('role'):ref['path'] for ref in row.get('evidence',[])
                if ref['path'].lower().endswith(('.png','.jpg','.jpeg'))}
        need(all(role in images for role in roles) and len({images.get(role) for role in roles})==len(roles), 'capture roles '+name)
        if name.startswith('configuration_'):
            expected=[1600,1000,2] if name=='configuration_1600_1000_gui2' else [1200,900,1]
            need(row.get('observed_configuration')==expected,'observed settings '+name)
    events = actions.get('events', [])
    need(bool(actions.get('actual_observations')) and isinstance(actions.get('computed_checks'),dict), 'separate observations and computed checks')
    for i,e in enumerate(events):
        require(e.get('sequence') == i and isinstance(e.get('unix'),(int,float))
                and e.get('actor') in ('human','agent','collector') and bool(e.get('observation')), 'Complete ordered action sequence')
        if i:
            require(e['unix'] >= events[i-1]['unix'], 'Action timestamp order')
    for scale in (1,6):
        movement = [e for e in events if e.get('kind')=='human-movement' and e.get('scale')==scale]
        need(len(movement)==1, 'human movement scale'+str(scale))
        for e in movement:
            require(e['released'] is True and e['held_seconds'] <= 4 and e['held_seconds']>0, 'Bounded release')
            holds=e.get('holds',[])
            require(bool(holds) and e.get('actor')=='human', 'Explicit human handoff/holds')
            for i,hold in enumerate(holds):
                require(hold['released'] is True and 0 < hold['seconds'] <= (4 if i==0 else 1), 'Bounded additional hold')
            a,b = (positions[e[k]] for k in ('before_position_index','after_position_index'))
            require(a['scale']==b['scale']==scale and 16 <= math.dist((a['x'],a['z']),(b['x'],b['z'])) <= 32, 'Movement bounds')
            require('RETAINED_NAV route ' not in console[a['offset']:b['offset']], 'Teleport is not movement')
            require(all(math.dist((a['x'],a['z']),(p['x'],p['z'])) <=32 for p in positions[e['before_position_index']:e['after_position_index']+1]), 'Movement overshoot')
            if scale==1:
                require((math.floor(a['x'])//16,math.floor(a['z'])//16)!=(math.floor(b['x'])//16,math.floor(b['z'])//16), 'Chunk crossing')
            for key in ('before_image','after_image'):
                image = data[e[key]]
                require(image.startswith(b'\x89PNG\r\n\x1a\n') or image.startswith(b'\xff\xd8\xff'), 'Actual image format')
    need(isinstance(actions.get('visual_judgment'),str) and bool(actions.get('visual_judgment')), 'separate visual judgment')
    need(actions.get('reviewer_confirmed_all_visual_checks') is True, 'human visual review')
    return dict(mode='runtime', acceptance='COMPLETE' if not unmet else 'INCOMPLETE', unmet=unmet,
                computed=dict(side=[3073,18438],spacing=[64,384],spacing_chunks=[4,24],
                              along_x_width=[2048,12288],width_chunks=[128,768]),
                visual_judgment=actions.get('visual_judgment'), attempts_remaining=0)


def export_runtime(output, destination):
    require(output.resolve() == (ROOT/'runs/acceptance/td-navigation-3').resolve(), 'Wrong runtime root')
    data = {p.relative_to(output).as_posix():p.read_bytes() for p in output.rglob('*') if p.is_file()}
    result = runtime(data)
    encode = runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))['encode']
    destination.write_bytes(encode(data))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('archive', type=Path)
    p.add_argument('--runtime', action='store_true')
    p.add_argument('--strict', action='store_true')
    p.add_argument('--export-runtime',type=Path,help='package complete runtime root into this external ZIP')
    a = p.parse_args()
    if a.export_runtime:
        require(not a.export_runtime.resolve().is_relative_to(a.archive.resolve()),'Archive must be outside runtime root')
        print(json.dumps(export_runtime(a.archive,a.export_runtime),indent=2))
    else:
        data = members(a.archive)
        print(json.dumps(runtime(data) if a.runtime else preparation(data,a.strict), indent=2))
