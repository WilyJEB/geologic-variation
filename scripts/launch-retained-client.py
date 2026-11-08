"""Bounded installed-profile launcher for client-map-1. Never imports TD tooling."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runs/acceptance/td-client-map-1'
META = Path.home() / 'AppData/Roaming/ModrinthApp/meta'
MANIFEST = META / 'versions/1.21.1-21.1.251/1.21.1-21.1.251.json'
JAVA = Path('C:/Program Files/Java/jdk-21/bin/java.exe')
JAR = ROOT / 'diagnostics/retained-client/build/libs/retained-client-1.jar'
FORBIDDEN = ('terraindiffusion', 'terrain_diffusion', 'terrain-diffusion',
             'onnxruntime', 'ai/onnx', 'dev/wilyjeb/geology/domain/',
             'dev/wilyjeb/geology/world/', 'geologic_variation')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan(data, label):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if any(s in n.lower() for s in FORBIDDEN):
                raise ValueError(f'Forbidden executable resource: {label}:{n}')
            if n.endswith('.jar'):
                scan(z.read(n), label + ':' + n)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def inventory(directory):
    return {str(p.relative_to(directory)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=sha(p))
            for p in sorted(directory.rglob('*')) if p.is_file()}


def main(check=False, small=False):
    if any(os.environ.get(k) for k in ('JAVA_TOOL_OPTIONS', '_JAVA_OPTIONS', 'JDK_JAVA_OPTIONS', 'CLASSPATH')):
        raise ValueError('Inherited JVM injection is prohibited')
    manifest = json.loads(MANIFEST.read_text())
    assert sha(MANIFEST) == '706a7b7be2f110a87449f0ea090b6daf3882106f0d39acbe2c18b8a37d254924'
    assert manifest['id'] == '1.21.1-21.1.251'
    allowed = runpy.run_path(str(ROOT/'scripts/launch-acceptance-client.py'))['allowed']
    paths = []
    for lib in manifest['libraries']:
        if not lib.get('include_in_classpath', True) or not allowed(lib.get('rules')):
            continue
        art = lib.get('downloads', {}).get('artifact')
        if not art:
            continue
        p = META/'libraries'/art['path']
        assert hashlib.sha1(p.read_bytes()).hexdigest() == art['sha1'], p
        paths.append(p)
    paths.append(MANIFEST.with_suffix('.jar'))
    # Scan every library in the supplied profile as module/discovery paths may
    # include entries not on -cp. No arbitrary library/profile/mod paths accepted.
    supplied = set(paths)
    for lib in manifest['libraries']:
        art = lib.get('downloads', {}).get('artifact')
        if art and art.get('path') and (META/'libraries'/art['path']).is_file():
            p = META/'libraries'/art['path']
            assert hashlib.sha1(p.read_bytes()).hexdigest() == art['sha1'], p
            supplied.add(p)
    for p in supplied | {JAR}:
        scan(p.read_bytes(), str(p))
    with zipfile.ZipFile(JAR) as z:
        classes = [n for n in z.namelist() if n.endswith('.class')]
        prefixes = ('dev/wilyjeb/geology/probe/RetainedMap', 'dev/wilyjeb/retainedclient/')
        assert classes and all(n.startswith(prefixes) for n in classes), classes
        assert hashlib.sha256(z.read('retained-map.tsv')).hexdigest() == 'ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872'
        assert set(n for n in z.namelist() if n.endswith('mixins.json')) == {'retained-client.mixins.json'}
    if check:
        print('PASS scanned installed libraries and isolated display JAR; no client launched')
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ledger = OUTPUT/'ledger.json'
    attempts = json.loads(ledger.read_text()) if ledger.exists() else []
    assert all(v['status'] != 'allocated-before-spawn' for v in attempts), 'Previous attempt not finalized'
    assert len(attempts) < 3 and sum(v.get('elapsed', 900) for v in attempts) < 2700, 'Launch budget exhausted'
    attempt = OUTPUT/f'attempt-{len(attempts)+1:02}'
    attempt.mkdir(exist_ok=False)
    (attempt/'mods').mkdir()
    shutil.copy2(JAR, attempt/'mods'/JAR.name)
    shutil.copytree(META/'natives'/manifest['id'], attempt/'natives')
    width, height, gui = (1200, 900, 1) if small else (1600, 1000, 2)
    (attempt/'options.txt').write_text(f'version:3955\nguiScale:{gui}\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\nonboardAccessibility:false\nmaxFps:30\n')
    repl = dict(auth_player_name='RetainedDiagnostic', auth_uuid='00000000-0000-3000-8000-000000000001',
        auth_access_token='0', clientid='0', auth_xuid='0', user_type='legacy',
        version_name=manifest['id'], version_type='release', game_directory=str(attempt),
        assets_root=str(META/'assets'), assets_index_name=manifest['assetIndex']['id'],
        natives_directory=str(attempt/'natives'), library_directory=str(META/'libraries'),
        launcher_name='retained-display-only', launcher_version='1',
        classpath=os.pathsep.join(map(str, paths)), classpath_separator=os.pathsep)
    def expand(s):
        for k, v in repl.items():
            s = s.replace('${'+k+'}', v)
        assert '${' not in s, s
        return s
    def arguments(entries):
        out = []
        for e in entries:
            if isinstance(e, str):
                out.append(expand(e))
            elif allowed(e.get('rules')):
                v = e['value']
                out.extend(expand(s) for s in (v if isinstance(v, list) else [v]))
        return out
    cmd = [str(JAVA), '-Xms512m', '-Xmx2g', '-XX:-HeapDumpOnOutOfMemoryError',
           '-Xlog:class+load=info:file=class-load.log', '-Dgeology.probe.retainedMap=true']
    cmd += arguments(manifest['arguments']['jvm'])
    cmd += [manifest['mainClass']] + arguments(manifest['arguments']['game'])
    cmd += ['--width', str(width), '--height', str(height)]
    assert not any('quickPlay' in s for s in cmd)
    dump(attempt/'command.json', cmd)
    dump(attempt/'dependencies.json', {str(p):sha(p) for p in sorted(supplied)})
    shutil.copy2(MANIFEST, attempt/'installed-manifest.json')
    dump(attempt/'jar-entries.json', classes)
    source = attempt/'executed'; source.mkdir()
    for p in [ROOT/'scripts/launch-retained-client.py', ROOT/'docs/td-client-map-protocol.md',
              *sorted((ROOT/'diagnostics/retained-client').rglob('*.java')),
              ROOT/'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMap.java',
              ROOT/'src/runtimeProbe/java/dev/wilyjeb/geology/probe/RetainedMapScreen.java',
              ROOT/'src/runtimeProbe/resources/retained-map.tsv', JAR]:
        shutil.copy2(p, source/p.name)
    record = dict(attempt=len(attempts)+1, status='allocated-before-spawn', elapsed=900)
    attempts.append(record); dump(ledger, attempts)
    started = time.monotonic(); process = None; status = 'error'
    try:
        assert shutil.disk_usage(OUTPUT).free >= 4*1024**3
        with (attempt/'console.log').open('w') as log, (attempt/'monitor.jsonl').open('w') as monitor:
            process = subprocess.Popen(cmd, cwd=attempt, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
            (attempt/'pid.txt').write_text(str(process.pid))
            print(f'Client attempt {len(attempts)}/3 PID {process.pid}', flush=True)
            while process.poll() is None:
                elapsed = time.monotonic()-started
                files = list(p for p in OUTPUT.rglob('*') if p.is_file())
                used = sum(p.stat().st_size for p in files)
                # Get-Process reads only the exact spawned PID, never all Java tasks.
                mem = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                    f'(Get-Process -Id {process.pid} -ErrorAction SilentlyContinue).WorkingSet64'],
                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                working = int(mem.stdout.strip() or '0')
                sample = dict(elapsed=elapsed, working_set=working, output_bytes=used,
                              free=shutil.disk_usage(OUTPUT).free)
                monitor.write(json.dumps(sample)+'\n'); monitor.flush()
                assert elapsed <= 900 and used <= 2*1024**3 and working <= 6*1024**3 and sample['free'] >= 4*1024**3, sample
                assert not any(p.is_file() for p in (attempt/'saves').rglob('*')), 'World/save write prohibited'
                time.sleep(1)
            status = f'exit-{process.returncode}'
    finally:
        if process and process.poll() is None:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            process.wait(timeout=30)
        record.update(status=status, elapsed=time.monotonic()-started)
        dump(ledger, attempts)
        dump(attempt/'inventory.json', inventory(attempt))
    console = (attempt/'console.log').read_text(errors='replace')
    assert status == 'exit-0' and 'RETAINED_CLIENT enter panel' in console and 'FATAL' not in console, 'Client did not complete panel entry: '+status


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-only', action='store_true')
    p.add_argument('--small', action='store_true')
    a = p.parse_args(); main(a.check_only, a.small)
