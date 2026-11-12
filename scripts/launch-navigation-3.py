"""PREPARATION ONLY until separately authorized. No work happens on import.

--check-only is an installed-profile/network preflight: do not run it during
preparation. --launch requires a separately supplied authorization record and
runs that same preflight immediately before exclusive allocation. No retries.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runs/acceptance/td-navigation-3'
GAME = OUTPUT / 'td-navigation-2/attempt-01'  # exact reused JAR's guarded suffix
FREEZE = ROOT / 'docs/td-navigation-3-hashes.json'
JAR_MEMBER = 'raw/final-compile-only.jar'
CAPS = dict(startup=180, wall=1200, working_set=6*1024**3,
            output_bytes=2*1024**3, free=4*1024**3,
            td_requests=0, model_calls=0, provider_initializations=0, windows=0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def append(path, value):
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, sort_keys=True)+'\n'); stream.flush()
        os.fsync(stream.fileno())


def frozen():
    record = json.loads(FREEZE.read_text())
    for name, expected in record['files'].items():
        require(sha((ROOT/name).read_bytes()) == expected, 'Frozen bytes changed: '+name)
    return record


def artifact():
    import zipfile
    with zipfile.ZipFile(ROOT/'docs/evidence/td-navigation-supplement.zip') as archive:
        return archive.read(JAR_MEMBER)


def context():
    import getpass
    import ctypes
    session_id=ctypes.c_ulong()
    if os.name=='nt':
        require(ctypes.windll.kernel32.ProcessIdToSessionId(os.getpid(),ctypes.byref(session_id)),
                'Cannot identify Windows session')
    return dict(account=getpass.getuser(), computer=os.environ.get('COMPUTERNAME'),
                session=os.environ.get('SESSIONNAME'), session_id=session_id.value,
                python=str(Path(os.sys.executable).resolve()),
                java='C:/Program Files/Java/jdk-21/bin/java.exe')


def old_state():
    state = {}
    for n in (1, 2):
        root = ROOT/f'runs/acceptance/td-navigation-{n}'
        state[str(n)] = dict(ledger=sha((root/'ledger.json').read_bytes()),
                            directories=sorted(p.name for p in root.glob('attempt-*')))
    return state


def authorization(record, named_context, command):
    require(record['explicit_client_launch_authorized'] is True, 'Explicit client approval missing')
    require(record['human_present'] is True and record['human_available_through_quit'] is True,
            'Present human required through capture and quit')
    require(record['contract'] == 'navigation-3' and record['attempts_including_failure'] == 1,
            'Wrong authorization budget')
    require(record['context'] == named_context and record['observed_context'] == context(),
            'Execution context differs')
    require(record['command'] == command, 'Authorized command differs')
    require(record['manifest_sha256'] == sha(FREEZE.read_bytes()), 'Approval manifest differs')
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    pushed = subprocess.check_output(['git','rev-parse','origin/codex/retained-navigation'],cwd=ROOT,text=True).strip()
    require(record['pushed_commit'] == head == pushed, 'Approval must identify pushed current commit')
    require(record['permission_mode'] in ('restricted', 'separately-approved'), 'Name permission mode')
    require(0 <= time.time()-record['human_confirmation_unix'] <= 60, 'Human confirmation stale')


def preflight():
    """Only called with explicit check or launch flags, never by offline tests."""
    require(os.sys.flags.optimize==0,'Optimized Python disables historical assertions')
    record = frozen()
    before = old_state()
    require(not OUTPUT.exists(), 'Single slot already consumed or root exists; no reconciliation can reset it')
    # Reuse the frozen installed-library/nested-JAR/JVM-injection guards verbatim.
    legacy = runpy.run_path(str(ROOT/'scripts/launch-retained-navigation-supplement.py'))
    require(legacy['JAR'].read_bytes() == artifact(), 'Installed diagnostic artifact differs from portable exact bytes')
    legacy['main'](check=True)
    pinned=json.loads((ROOT/'docs/td-navigation-3-installed-inputs.json').read_text())
    for name,h in pinned['historical_dependency_hashes'].items():
        require(sha(Path(name).read_bytes())==h,'Pinned dependency differs: '+name)
    require(before == old_state(), 'Historical allocation state changed')
    require(not OUTPUT.exists(), 'Preflight allocated a root')
    shared = {}
    for folder in (legacy['META']/'assets', legacy['META']/'natives'/'1.21.1-21.1.251'):
        for p in sorted(folder.rglob('*')):
            require(not p.is_symlink(), 'Redirected shared input')
            if p.is_file():
                shared[str(p)] = sha(p.read_bytes())
    require(shared==pinned['shared'],'Shared asset/native set or hash differs')
    require(sha(legacy['JAVA'].read_bytes())==pinned['java_sha256'],'Java bytes differ')
    return dict(timestamp=time.time(), context=context(), old_state=before, shared=shared,
                manifest_sha256=sha(FREEZE.read_bytes()), artifact_sha256=sha(artifact()),
                java_sha256=sha(legacy['JAVA'].read_bytes()), files=record['files'])


def allocate(output, approval, ready):
    # Exclusive mkdir is the single-use tombstone, even if ledger write fails.
    # No attempt/root deletion, replacement or reopening path exists.
    for parent in (output, *output.parents):
        require(not parent.is_symlink() and not parent.is_junction(), 'Redirected allocation path')
    output.mkdir(exist_ok=False)
    row = dict(contract='navigation-3', attempts_used=1, attempts_remaining=0,
               charged_seconds=1200, status='allocated-before-spawn', finalized=False,
               approval=approval, preflight=ready, allocated_unix=time.time())
    with (output/'ledger.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(row, indent=2)+'\n'); stream.flush(); os.fsync(stream.fileno())
    return row


def command(game):
    legacy = runpy.run_path(str(ROOT/'scripts/launch-retained-navigation-supplement.py'))
    meta, manifest_path = legacy['META'], legacy['MANIFEST']
    manifest = json.loads(manifest_path.read_text())
    allowed = runpy.run_path(str(ROOT/'scripts/launch-acceptance-client.py'))['allowed']
    paths = []
    supplied = set()
    for lib in manifest['libraries']:
        art = lib.get('downloads', {}).get('artifact')
        if art and art.get('path'):
            p = meta/'libraries'/art['path']
            if p.is_file():
                supplied.add(p)
            if lib.get('include_in_classpath', True) and allowed(lib.get('rules')):
                paths.append(p)
    paths.append(manifest_path.with_suffix('.jar')); supplied.update(paths)
    shutil.copytree(meta/'natives'/manifest['id'], game/'natives')
    (game/'mods').mkdir()
    (game/'mods/retained-navigation-1.jar').write_bytes(artifact())
    (game/'options.txt').write_text('version:3955\nguiScale:2\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\nonboardAccessibility:false\nmaxFps:30\n')
    values = dict(auth_player_name='RetainedNav', auth_uuid='00000000-0000-3000-8000-000000000001',
                  auth_access_token='0', clientid='0', auth_xuid='0', user_type='legacy',
                  version_name=manifest['id'], version_type='release', game_directory=str(game),
                  assets_root=str(meta/'assets'), assets_index_name=manifest['assetIndex']['id'],
                  natives_directory=str(game/'natives'), library_directory=str(meta/'libraries'),
                  launcher_name='retained-display-only', launcher_version='1',
                  classpath=os.pathsep.join(map(str, paths)), classpath_separator=os.pathsep)
    def expand(value):
        for k, v in values.items():
            value = value.replace('${'+k+'}', v)
        require('${' not in value, 'Unknown launch placeholder')
        return value
    def args(entries):
        result = []
        for entry in entries:
            if isinstance(entry, str):
                result.append(expand(entry))
            elif allowed(entry.get('rules')):
                v = entry['value']
                result.extend(map(expand, v if isinstance(v, list) else [v]))
        return result
    cmd = [str(legacy['JAVA']), '-Xms512m', '-Xmx2g', '-XX:-HeapDumpOnOutOfMemoryError',
           '-Xlog:class+load=info:file=class-load.log', '-Dgeology.probe.retainedMap=true',
           '-Dretained.navigation.root='+str(game)]
    cmd += args(manifest['arguments']['jvm']) + [manifest['mainClass']] + args(manifest['arguments']['game'])
    cmd += ['--width', '1600', '--height', '1000']
    require(not any('quickplay' in s.lower() for s in cmd), 'Quickplay forbidden')
    dump(game/'dependencies.json', {str(p):sha(p.read_bytes()) for p in sorted(supplied)})
    shutil.copy2(manifest_path, game/'installed-manifest.json')
    dump(game/'command.json', cmd)
    return cmd


def cap_check(sample, has_position):
    for key in ('wall', 'working_set', 'output_bytes'):
        require(sample[key] <= CAPS[key], 'Cap exceeded: '+key)
    require(sample['free'] >= CAPS['free'], 'Free-space cap')
    require(sample['wall'] <= CAPS['startup'] or has_position, 'Startup cap')
    for key in ('td_requests', 'model_calls', 'provider_initializations', 'windows'):
        require(sample[key] == 0, 'Zero execution cap: '+key)


def safe_inventory(output):
    result = {}
    for path in sorted(output.rglob('*')):
        require(not path.is_symlink() and not path.is_junction() and path.resolve().is_relative_to(output.resolve()), 'Redirected output')
        if path.is_file():
            name = path.relative_to(output).as_posix()
            if '/saves/' in name:
                require('/saves/navigation-only/' in name, 'Unexpected save')
            result[name] = dict(bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
    return result


def run_attempt(output, row, prepare, job_factory, immutable_check):
    """Dependency injection is for fixture tests; CLI always uses fixed functions."""
    started = time.monotonic()-max(0,time.time()-row['allocated_unix'])
    job = None; known = {}; failure = None
    row['status'] = 'failed'; row['acceptance'] = 'INCOMPLETE'
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Stop requested; attempt consumed')
    previous = {s: signal.signal(s, interrupted) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        game, cmd = prepare()
        immutable_check()
        cap_check(dict(wall=time.monotonic()-started,working_set=0,
                       output_bytes=sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),
                       free=shutil.disk_usage(output).free,td_requests=0,model_calls=0,
                       provider_initializations=0,windows=0),False)
        job = job_factory()
        first = job.start(cmd, game)
        for identity in first:
            known[str(identity['ProcessId'])+':'+str(identity['CreationDate'])] = identity
        append(output/'processes.jsonl', dict(timestamp=time.time(), kind='suspended-parent', identities=first))
        while True:
            sampled_at=time.monotonic()
            pids = job.pids()
            identities = job.identities(pids)
            require({v['ProcessId'] for v in identities} == set(pids), 'Unresolved live job identity')
            for identity in identities:
                require(identity.get('CreationDate') and identity.get('CommandLine'), 'Missing process identity fields')
                key = str(identity['ProcessId'])+':'+str(identity['CreationDate'])
                known[key] = identity
            append(output/'processes.jsonl', dict(timestamp=time.time(), job_pids=pids, identities=identities))
            console = (game/'console.log').read_text(errors='replace') if (game/'console.log').exists() else ''
            sample = dict(wall=time.monotonic()-started,
                          working_set=sum(int(v['WorkingSetSize']) for v in identities),
                          output_bytes=sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),
                          free=shutil.disk_usage(output).free,
                          td_requests=0, model_calls=0, provider_initializations=0, windows=0,
                          zero_basis='structural executable exclusion, not measured TD counters')
            sample['has_position']='RETAINED_NAV position' in console
            append(output/'monitor.jsonl', sample)
            cap_check(sample, 'RETAINED_NAV position' in console)
            safe_paths(game)
            if (output/'STOP').exists():
                raise ValueError('Human/collector stop')
            if sample['wall'] >= 960:
                (output/'SHUTDOWN-REQUIRED').touch(exist_ok=True)
            code = job.exit_code()
            if code is not None:
                require(not pids, 'Descendant survives parent exit')
                row['exit_code'] = code
                require(code == 0, 'Nonzero exit')
                row['status'] = 'exited-evidence-pending'
                break
            time.sleep(max(0,1-(time.monotonic()-sampled_at)))
    except BaseException as error:
        failure = repr(error); row['failure'] = failure
    finally:
        for s in previous:
            signal.signal(s, signal.SIG_IGN)
        # Persist each independent failure; cleanup/finalization errors cannot
        # prevent the one-slot tombstone or erase earlier partial output.
        errors = []
        if job:
            try:
                for identity in getattr(job,'initial_identities',[]):
                    known[str(identity['ProcessId'])+':'+str(identity['CreationDate'])]=identity
                dump(output/'spawn-details.json',getattr(job,'start_details',{}))
                dump(output/'cleanup.json', job.cleanup(known))
            except BaseException as error:
                errors.append('cleanup: '+repr(error))
            finally:
                try:
                    job.close()
                except BaseException as error:
                    errors.append('job close: '+repr(error))
        try:
            immutable_check()
            row['immutable_inputs_unchanged'] = True
        except BaseException as error:
            errors.append('immutable: '+repr(error))
        row.update(finalized=not errors, finalization_errors=errors,
                   elapsed=time.monotonic()-started, charged_seconds=1200,
                   attempts_remaining=0)
        if row['elapsed'] > CAPS['wall']:
            errors.append('wall cap including cleanup exceeded')
            row['finalized'] = False
        dump(output/'ledger.json', row)
        try:
            dump(output/'inventory.json', safe_inventory(output))
        except BaseException as error:
            row['finalized'] = False; row['finalization_errors'].append('inventory: '+repr(error))
            dump(output/'ledger.json', row)
        row['final_resources']=dict(wall=time.monotonic()-started,
            output_bytes=sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),
            free=shutil.disk_usage(output).free)
        for key in ('wall','output_bytes'):
            if row['final_resources'][key]>CAPS[key]:
                row['finalized']=False;errors.append('final cap: '+key)
        if row['final_resources']['free']<CAPS['free']:
            row['finalized']=False;errors.append('final free-space cap')
        dump(output/'ledger.json',row)
        # Ledger changed after the first inventory; take a consistent final
        # snapshot without recursively hashing inventory.json itself.
        try:
            final_inventory=safe_inventory(output);final_inventory.pop('inventory.json',None)
            dump(output/'inventory.json',final_inventory)
        except BaseException as error:
            row['finalized']=False;errors.append('final inventory: '+repr(error));dump(output/'ledger.json',row)
        for s, handler in previous.items():
            signal.signal(s, handler)
    return row


def safe_paths(game):
    for p in game.rglob('*'):
        require(not p.is_symlink() and not p.is_junction() and p.resolve().is_relative_to(game.resolve()), 'Redirected game path')
        if p.is_relative_to(game/'saves'):
            require(p == game/'saves' or p.relative_to(game/'saves').parts[0] == 'navigation-only', 'Unexpected save path')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-only', action='store_true')
    mode.add_argument('--launch', action='store_true')
    parser.add_argument('--authorization', type=Path)
    parser.add_argument('--context')
    args = parser.parse_args()
    if args.check_only:
        print(json.dumps(preflight(), indent=2)); return
    require(args.authorization is not None and args.context, 'Authorization record and named context required')
    approval = json.loads(args.authorization.read_text())
    exact = [str(Path(os.sys.executable).resolve()), str(Path(__file__).resolve()), *os.sys.argv[1:]]
    authorization(approval, args.context, exact)
    ready = preflight()
    authorization(approval, args.context, exact)  # human confirmation must still be fresh
    require(time.time()-ready['timestamp'] <= 5, 'Immediate preflight expired')
    require(ready['context'] == context(), 'Context changed after preflight')
    frozen()
    require(ready['old_state'] == old_state(), 'Historical state changed before allocation')
    require(time.time()-ready['timestamp'] <= 5, 'Immediate preflight expired before allocation')
    row = allocate(OUTPUT, approval, ready)
    def prepare():
        GAME.mkdir(parents=True, exist_ok=False)
        executed = OUTPUT/'executed'; executed.mkdir()
        for name in [*ready['files'], 'docs/td-navigation-3-hashes.json']:
            target = executed/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, target)
        (executed/'retained-navigation-1.jar').write_bytes(artifact())
        return GAME, command(GAME)
    def unchanged():
        frozen()
        require(ready['old_state'] == old_state(), 'Historical root changed')
        checks = {}
        inputs = {**ready['shared'], **json.loads((GAME/'dependencies.json').read_text()),
                  ready['context']['java']:ready['java_sha256']}
        for p, h in inputs.items():
            checks[p] = sha(Path(p).read_bytes())
        dump(OUTPUT/'shared-post.json', checks)
        for p,h in inputs.items():
            require(checks[p] == h, 'Shared input changed: '+p)
    job_factory = runpy.run_path(str(ROOT/'scripts/navigation-process.py'))['Job']
    result = run_attempt(OUTPUT, row, prepare, job_factory, unchanged)
    print(json.dumps(result, indent=2))
    require(result['status'] == 'exited-evidence-pending' and result['finalized'], 'Failed attempt; no replacement')


if __name__ == '__main__':
    main()
