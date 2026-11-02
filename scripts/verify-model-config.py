"""Real supported custom TD config substitution in a NEW verified fixture copy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import zipfile

hot = runpy.run_path(str(Path(__file__).with_name('verify-hot-config.py')))
h = hot['h']; runtime = h['runtime']; require = h['require']; ROOT = runtime['ROOT']
CPU = '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8'
FIELDS = {'generator','seed','scale','tileSize','dependency','models','backend'}
ASSET = 'world_pipeline_config.json'


def context(text):
    require(text.startswith('GenerationContext[') and text.endswith(']'), 'Invalid context')
    result = dict(part.split('=', 1) for part in text[18:-1].split(', '))
    require(set(result) == FIELDS, 'Incomplete context')
    return result


def snapshot(path):
    result = dict(line.split('=', 1) for line in path.read_text().splitlines() if line and not line.startswith('#'))
    require(set(result) == FIELDS | {'schema','provinceSpacingBlocks','oceanCeilingMetres','lowlandCeilingMetres',
                                    'mountainFloorMetres','gentleReliefMetres','ruggedReliefMetres'}, 'Incomplete snapshot')
    require(result['schema'] == '2', 'Wrong schema')
    return result


def aggregate(assets):
    return hashlib.sha256(''.join(f'{k}={assets[k]};' for k in sorted(assets)).encode()).hexdigest()


def run(args):
    require(runtime['sha'](args.td) == CPU, 'Wrong official CPU artifact')
    require(runtime['sha'](args.addon) == '39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226', 'Addon changed')
    fixture = hot['manifest'](args.fixture)
    require(fixture[h['SNAPSHOT'].as_posix()] == 'c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d', 'Unverified fixture')
    with zipfile.ZipFile(args.td) as jar:
        manifest = json.loads(jar.read('model-assets-manifest.json'))
    shared = {k: runtime['sha'](args.models/k) for k in manifest['assets']}
    require(shared == {k:v['sha256'] for k,v in manifest['assets'].items()}, 'Shared assets lack official provenance')
    args.output.mkdir(parents=True, exist_ok=False)
    result = {'source_baseline':'2b9d07a049a62129827446f7061e2a16deeb3223', 'manifest':manifest,
              'derivation':{'asset':ASSET,'field':'residual_mean','original':0.0,'alternate':1.0,
                            'kind':'test-derived custom config, not an official alternate model'}, 'launches':[]}
    server = runtime['Server'](args, 'model-config', scale=1, link_td=True)
    world = server.path/'world'
    shutil.copytree(args.fixture, world, dirs_exist_ok=True)
    config = server.path/'config/terrain-diffusion-mc.properties'
    config.write_text(config.read_text().replace('validate_model=true','validate_model=false').replace('inference.device=gpu','inference.device=cpu'))
    # Detach the only writable asset BEFORE any write; other assets remain immutable links.
    asset = server.path/'terrain-diffusion-models'/ASSET
    original_bytes = asset.read_bytes(); asset.unlink(); asset.write_bytes(original_bytes)
    alternate_bytes = original_bytes.replace(b'"residual_mean": 0.0', b'"residual_mean": 1.0')
    require(alternate_bytes != original_bytes, 'Derivation did not change input')
    a,b = json.loads(original_bytes),json.loads(alternate_bytes)
    require([k for k in a if a[k] != b[k]] == ['residual_mean'] and b['residual_mean'] == 1.0, 'Unexpected semantic edit')
    alternate = {**shared, ASSET:hashlib.sha256(alternate_bytes).hexdigest()}
    inputs = lambda: {'mods':hot['manifest'](server.path/'mods'), 'config':hot['manifest'](server.path/'config'),
                      'assets':{k:runtime['sha'](server.path/'terrain-diffusion-models'/k) for k in shared}}
    state = lambda: {'preserved':h['preserve'](world), 'terrain':hot['live']['terrain'](world),
                     'snapshot_fields':snapshot(world/h['SNAPSHOT'])}
    def launch():
        free = shutil.disk_usage(args.output).free
        require(free >= 2*1024**3, 'Need 2 GiB free before launch')
        result['launches'].append({'free_bytes_before':free})
    def launched():
        result['launches'][-1].update(pid=server.process.pid,exit_code=server.process.returncode)
    def stop():
        server.stop(); h['storage_ok'](server); launched(); h['cleanup_cache'](server)
    def loaded(value):
        text = h['log'](server).read_text(errors='replace')
        require(re.findall(r'TD_MODEL_CONFIG residual_mean=([\d.]+) native_resolution=30.0 latent_compression=8',text) == [str(value)], 'Actual loaded config differs')
        require('Terrain diffusion inference: CPU' in text and 'Stopping server' in text, 'Missing native CPU initialization/shutdown')
        require('without SHA validation (validate_model=false)' in text, 'Custom-input mechanism not observed')
    try:
        launch(); server.start(); before = h['observe'](server); stop(); loaded(0.0)
        original = state(); original_inputs = inputs(); saved = context(before['settings']['context'])
        require({k:original['snapshot_fields'][k] for k in FIELDS} == saved, 'Snapshot/runtime differs')
        require(saved['models'] == aggregate(shared) == '64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9', 'Original identity differs')
        require(saved['dependency'] == CPU and saved['backend'] == 'CPU/Windows 11/amd64', 'Wrong environment')
        require(original['terrain'] == hot['live']['terrain'](args.fixture), 'Control changed stored terrain')
        require(original['preserved']['snapshot'] == fixture[h['SNAPSHOT'].as_posix()], 'Control changed snapshot')
        require(any(k.startswith('geologic_variation:') and v for k,v in before['chunk']['counts'].items()), 'Empty geology')
        asset.write_bytes(alternate_bytes); changed = inputs()
        require(changed == {**original_inputs,'assets':alternate}, 'Other inputs changed')
        launch(); rejection = h['rejected'](server, 'Incompatible geology generation context', 'models'); launched(); loaded(1.0)
        require(set(rejection['saved_context']) == set(rejection['runtime_context']) == FIELDS, 'Incomplete rejection')
        require(rejection['saved_context'] == saved and rejection['runtime_context'] == {**saved,'models':aggregate(alternate)}, 'Unexpected runtime identity')
        rejected_state = state()
        require(original['preserved']['snapshot'] == rejected_state['preserved']['snapshot'] and original['terrain'] == rejected_state['terrain'], 'Rejection altered snapshot/terrain')
        h['cleanup_cache'](server)
        asset.write_bytes(original_bytes)
        require(inputs() == original_inputs, 'Inputs not exactly restored')
        launch(); server.start(); reopened = h['observe'](server); stop(); loaded(0.0)
        final = state()
        require(before['settings'] == reopened['settings'] and before['region'] == reopened['region'], 'Restored settings/geology differs')
        require(before['chunk']['blocks_sha256'] == reopened['chunk']['blocks_sha256'], 'Restored blocks differ')
        require(original['terrain'] == final['terrain'] and original['preserved']['snapshot'] == final['preserved']['snapshot'], 'Reopen altered persisted terrain/snapshot')
        require(hot['manifest'](args.fixture) == fixture, 'Source fixture changed')
        require({k:runtime['sha'](args.models/k) for k in shared} == shared and runtime['sha'](args.td) == CPU, 'Shared input changed')
        result.update(before=before,reopened=reopened,rejection=rejection,before_state=original,rejected_state=rejected_state,
                      final_state=final,original_inputs=original_inputs,substituted_inputs=changed,restored_inputs=inputs(),
                      fixture_unchanged=True,shared_inputs_unchanged=True,
                      logs={p.name:runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))})
        (args.output/'model-config-results.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASSED supported model-config rejection and exact restoration/reopen',flush=True)
    finally:
        try:
            h['close'](server)
        finally:
            if hasattr(server,'process') and server.process.poll() is None:
                server.process.kill(); server.process.wait(timeout=30)
            if hasattr(server,'console') and not server.console.closed: server.console.close()
            h['cleanup_cache'](server)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('java','td','fixture','output'): p.add_argument('--'+name,type=Path,required=True)
    for name,default in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                         'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                         'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        p.add_argument('--'+name,type=Path,default=ROOT/default)
    a=p.parse_args()
    for name,value in vars(a).items(): setattr(a,name,value.resolve())
    run(a)
