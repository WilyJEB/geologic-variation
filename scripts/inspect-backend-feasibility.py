"""Bounded native preflight of pinned official TD distributions; never opens a save.

Successful session creation only selects a candidate for a subsequent save-safety
matrix. Native/provider failure is a blocked gate, never geology rejection.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'cpu': '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8',
    'cuda': '97ff25936fdf79b9cabbf8b68dc5d02fd15938437e08069c4005619f695161ad',
    'directml': '64422a53d395666ed0774a8904823b7c96688b5ce82a0026326c3e823f7e99dd',
}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def files(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def bounded(command, cwd, logfile, timeout=120):
    started = time.monotonic()
    with logfile.open('wb') as log:
        process = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=30)
    return {'pid': process.pid, 'exit_code': process.returncode, 'timed_out': timed_out,
            'elapsed_seconds': round(time.monotonic() - started, 3), 'log_sha256': sha(logfile)}


def run(args):
    require(os.name == 'nt', 'This feasibility report targets Windows')
    artifacts = {k: getattr(args, k) for k in PINS}
    original_artifacts = {k: sha(p) for k, p in artifacts.items()}
    require(original_artifacts == PINS, 'Official artifact pins differ')
    with zipfile.ZipFile(args.cpu) as jar:
        manifest = json.loads(jar.read('model-assets-manifest.json'))
        classes = {n: hashlib.sha256(jar.read(n)).hexdigest() for n in jar.namelist()
                   if n.endswith('.class') and 'terraindiffusionmc/' in n}
    assets = {k: sha(args.models / k) for k in manifest['assets']}
    require(assets == {k: v['sha256'] for k, v in manifest['assets'].items()}, 'Model provenance differs')
    fixture = files(args.fixture)
    require(fixture['data/geologic_variation-geology.properties'] ==
            'c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d', 'Fixture pin differs')
    args.output.mkdir(parents=True, exist_ok=False)
    result = {'kind': 'native feasibility, not save-safety acceptance', 'artifact_sha256': PINS,
              'manifest': manifest, 'asset_sha256': assets, 'fixture_files': len(fixture),
              'fixture_manifest_sha256': digest(fixture), 'cases': {}}
    result['hardware'] = bounded(['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv'],
                                 args.output, args.output / 'hardware.log', 15)
    result['hardware']['text'] = (args.output / 'hardware.log').read_text().strip()
    result['cuda_dlls_on_path'] = {n: any((Path(folder.strip('"'))/n).is_file() for folder in os.get_exec_path()) for n in
                                 ('cudart64_12.dll', 'cublas64_12.dll', 'cudnn64_9.dll')}
    for provider, artifact in artifacts.items():
        case = args.output / provider
        case.mkdir()
        free = shutil.disk_usage(case).free
        require(free >= 2 * 1024**3, 'Need 2 GiB free before native launch')
        with zipfile.ZipFile(artifact) as jar:
            require(json.loads(jar.read('model-assets-manifest.json')) == manifest, 'Manifest differs')
            require(all(hashlib.sha256(jar.read(n)).hexdigest() == v for n, v in classes.items()), 'TD APIs differ')
            nested = [n for n in jar.namelist() if n.endswith('.jar') and 'onnxruntime' in n]
            require(len(nested) == 1, 'Ambiguous ONNX runtime')
            raw = jar.read(nested[0])
        runtime = case / 'runtime.jar'
        runtime.write_bytes(raw)
        native = {}
        with zipfile.ZipFile(io.BytesIO(raw)) as jar:
            for name in jar.namelist():
                if '/win-x64/' in name and name.endswith('.dll'):
                    data = jar.read(name)
                    require(data[:2] == b'MZ', 'Native library is not PE')
                    offset = struct.unpack_from('<I', data, 60)[0]
                    require(data[offset:offset+4] == b'PE\0\0', 'Invalid PE header')
                    native[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                                    'machine': hex(struct.unpack_from('<H', data, offset+4)[0])}
        compiled = bounded([str(args.java.with_name('javac.exe')), '-cp', str(runtime), '-d', str(case),
                            str(ROOT / 'scripts/BackendPreflight.java')], case, case / 'compile.log', 30)
        require(compiled['exit_code'] == 0 and not compiled['timed_out'], 'Preflight compilation failed')
        temp = case / 'tmp'
        temp.mkdir()
        observed = bounded([str(args.java), '-Xmx2G', '-Djava.io.tmpdir=' + str(temp), '-cp',
                            str(case) + os.pathsep + str(runtime), 'BackendPreflight', provider,
                            str(args.models / 'coarse_model.onnx')], case, case / 'native.log')
        text = (case / 'native.log').read_text(errors='replace')
        # Keep raw logs locally; the portable excerpt removes local absolute paths.
        portable = text.replace(str(ROOT), '<workspace>').replace(ROOT.as_posix(), '<workspace>')
        observed.update(free_bytes_before=free, runtime_entry=nested[0], runtime_sha256=sha(runtime),
                        native_libraries=native, compile=compiled, log_excerpt=portable,
                        native_initialized='NATIVE_INITIALIZED' in text,
                        provider_added='PROVIDER_ADDED ' + provider in text,
                        model_session_created='MODEL_SESSION_CREATED' in text)
        observed['candidate'] = observed['exit_code'] == 0 and not observed['timed_out'] and observed['model_session_created']
        result['cases'][provider] = observed
        print(provider, 'candidate' if observed['candidate'] else 'unavailable', flush=True)
    require(files(args.fixture) == fixture, 'Original fixture changed')
    require({k: sha(args.models/k) for k in assets} == assets, 'Shared model changed')
    require({k: sha(p) for k, p in artifacts.items()} == original_artifacts, 'Artifact changed')
    result.update(fixture_unchanged=True, shared_inputs_unchanged=True, identical_td_classes=len(classes),
                  save_launches=0, save_safety_accepted=False,
                  source_sha256={n: sha(ROOT/'scripts'/n) for n in
                                 ('BackendPreflight.java', 'inspect-backend-feasibility.py')})
    require(result['cases']['cpu']['candidate'], 'CPU native control failed; environment report is inconclusive')
    (args.output/'feasibility.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('java', 'cpu', 'cuda', 'directml', 'models', 'fixture', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    for name, value in vars(a).items():
        setattr(a, name, value.resolve())
    run(a)
