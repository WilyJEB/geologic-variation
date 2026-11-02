"""Actual official TD artifact substitution and exact restoration in a NEW fixture copy."""
import argparse
import json
import os
from pathlib import Path
import runpy
import shutil
import time
import zipfile

hot = runpy.run_path(str(Path(__file__).with_name('verify-hot-config.py')))
h = hot['h']; runtime = h['runtime']; require = h['require']; ROOT = runtime['ROOT']
CPU = '3212b53cc1af656e37fb73511aa64f9623ea38e274705d102ce7cd9944092fe8'
ALT = '97ff25936fdf79b9cabbf8b68dc5d02fd15938437e08069c4005619f695161ad'
URL = 'https://github.com/xandergos/terrain-diffusion-mc/releases/download/2.3.0-preview/NeoForge-terrain-diffusion-mc-2.3.0-cuda%2B1.21.1.jar'


def run(args):
    require(runtime['sha'](args.td) == CPU and runtime['sha'](args.alternate) == ALT, 'Official artifact pins differ')
    require(runtime['sha'](args.addon) == '39d8f6781752e70490674dbeacbfe8579f95382de0902f20516a595ed02bb226', 'Addon changed')
    with zipfile.ZipFile(args.td) as a, zipfile.ZipFile(args.alternate) as b:
        classes = [n for n in a.namelist() if n.endswith('.class') and 'terraindiffusionmc/' in n]
        require(all(a.read(n) == b.read(n) for n in classes), 'TD classes differ')
        require(a.read('model-assets-manifest.json') == b.read('model-assets-manifest.json'), 'Manifest differs')
    fixture = hot['manifest'](args.fixture)
    require(fixture[h['SNAPSHOT'].as_posix()] == 'c0237cad6358d979a8514086850cd23d1b31266b044876e7f7301f4e029a9e2d', 'Unverified fixture')
    args.output.mkdir(parents=True, exist_ok=False)
    server = runtime['Server'](args, 'artifact', scale=1, link_td=True)
    world = server.path/'world'
    shutil.copytree(args.fixture, world, dirs_exist_ok=True)
    config = server.path/'config/terrain-diffusion-mc.properties'
    config.write_text(config.read_text().replace('inference.device=gpu', 'inference.device=cpu'))
    models = hot['manifest'](server.path/'terrain-diffusion-models')
    inputs = lambda: {'mods':{p.name:runtime['sha'](p) for p in sorted((server.path/'mods').glob('*.jar'))},
                      'config':hot['manifest'](server.path/'config')}
    result = {'source_baseline':'236ee9420ae0df923792107266be600963964e79', 'official_alternate_url':URL,
              'identical_td_classes':len(classes), 'identical_model_manifest':True, 'launches':[]}
    def space():
        free = shutil.disk_usage(args.output).free
        require(free >= 2*1024**3, 'Need 2 GiB free before launch')
        return free
    def state():
        return {'preserved':h['preserve'](world), 'terrain':hot['live']['terrain'](world)}
    def stop():
        server.stop(); h['storage_ok'](server); h['cleanup_cache'](server)
    try:
        free = space(); server.start(); before = h['observe'](server)
        result['launches'].append({'pid':server.process.pid,'free_bytes_before':free})
        require('backend=CPU/Windows 11/amd64' in before['settings']['context'], 'Not CPU')
        require('models=64fe6b1af2462a8a53edca28d72b96cf2a6e9534d0be475c90028cb5939601d9' in before['settings']['context'], 'Model pin differs')
        require(any(k.startswith('geologic_variation:') and v for k,v in before['chunk']['counts'].items()), 'Empty sample')
        stop(); original = state(); original_inputs = inputs()
        require(original['terrain'] == hot['live']['terrain'](args.fixture), 'Baseline terrain differs from fixture')
        require(original['preserved']['snapshot'] == fixture[h['SNAPSHOT'].as_posix()], 'Baseline snapshot changed')
        td = server.path/'mods'/args.td.name
        alternate = server.path/'mods'/args.alternate.name
        td.unlink(); os.link(args.alternate, alternate)
        changed_inputs = inputs()
        require(changed_inputs['config'] == original_inputs['config'], 'Config changed')
        free = space(); started = time.monotonic()
        rejection = h['rejected'](server, 'Incompatible geology generation context', 'dependency')
        result['launches'].append({'pid':server.process.pid,'free_bytes_before':free,'elapsed_seconds':time.monotonic()-started})
        require(rejection['saved_context']['dependency'] == CPU and rejection['runtime_context']['dependency'] == ALT, 'Wrong artifact diagnostic')
        require(set(rejection['saved_context']) == set(rejection['runtime_context']) == {'generator','seed','scale','tileSize','dependency','models','backend'}, 'Incomplete diagnostic')
        text = h['log'](server).read_text(errors='replace')
        require('Stopping server' in text and 'Terrain diffusion inference: CPU' in text, 'Missing CPU resolution/shutdown')
        rejected_state = state(); require(original == rejected_state, 'Rejection changed snapshot/terrain/region bytes')
        h['cleanup_cache'](server)
        alternate.unlink(); os.link(args.td, td)
        require(inputs() == original_inputs, 'Runtime inputs not exactly restored')
        free = space(); server.start(); reopened = h['observe'](server)
        result['launches'].append({'pid':server.process.pid,'free_bytes_before':free})
        require(before['settings'] == reopened['settings'] and before['region'] == reopened['region'], 'Reopen context/settings/geology differs')
        require(before['chunk']['blocks_sha256'] == reopened['chunk']['blocks_sha256'], 'Reopen blocks differ')
        stop(); final = state()
        require(original['terrain'] == final['terrain'] and original['preserved']['snapshot'] == final['preserved']['snapshot'], 'Reopen persisted terrain/snapshot differs')
        require(hot['manifest'](args.fixture) == fixture, 'Source fixture changed')
        require(hot['manifest'](server.path/'terrain-diffusion-models') == models, 'Model inputs changed')
        result.update(before=before,reopened=reopened,rejection=rejection,before_state=original,rejected_state=rejected_state,
                      final_state=final,original_inputs=original_inputs,substituted_inputs=changed_inputs,
                      restored_inputs=inputs(),fixture_unchanged=True,models_unchanged=True,exit_code=server.process.returncode,
                      logs={p.name:runtime['sha'](p) for p in sorted(server.path.glob('console-*.log'))})
        (args.output/'artifact-results.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASSED official artifact rejection and exact restoration/reopen',flush=True)
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
    for name in ('java','td','alternate','fixture','output'): p.add_argument('--'+name,type=Path,required=True)
    for name,default in {'runtime':'runs/acceptance/runtime','models':'runs/server/terrain-diffusion-models',
                         'template':'runs/server/world','addon':'build/libs/geologic-variation-0.2.2-dev.jar',
                         'probe':'build/runtime-probe/geology-runtime-probe-0.2.2-dev.jar'}.items():
        p.add_argument('--'+name,type=Path,default=ROOT/default)
    a=p.parse_args()
    for name,value in vars(a).items(): setattr(a,name,value.resolve())
    run(a)
