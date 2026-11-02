"""Recheck raw native logs and official source/catalog inspection; export a blocked gate."""
import argparse
import json
from pathlib import Path
import runpy

h = runpy.run_path(str(Path(__file__).with_name('inspect-backend-feasibility.py')))
require, sha = h['require'], h['sha']


def export(source, inspection):
    data = json.loads((source/'feasibility.json').read_text())
    require(data['artifact_sha256'] == h['PINS'], 'Artifact pins differ')
    require(data['fixture_unchanged'] and data['shared_inputs_unchanged'], 'Shared inputs changed')
    require(data['save_launches'] == 0 and data['save_safety_accepted'] is False, 'Unjustified save acceptance')
    require(data['identical_td_classes'] == 58, 'TD API comparison differs')
    for name, value in data['source_sha256'].items():
        require(sha(h['ROOT']/'scripts'/name) == value, 'Executed source changed')
    for provider, case in data['cases'].items():
        folder = source/provider
        require(not case['timed_out'] and case['free_bytes_before'] >= 2*1024**3, 'Invalid preflight')
        require(sha(folder/'native.log') == case['log_sha256'], 'Raw native log changed')
        require(sha(folder/'compile.log') == case['compile']['log_sha256'], 'Raw compiler log changed')
        require(case['compile']['exit_code'] == 0, 'Compilation failed')
        require(sha(folder/'runtime.jar') == case['runtime_sha256'], 'Retained native runtime changed')
        text = (folder/'native.log').read_text(errors='replace')
        require(case['native_initialized'] == ('NATIVE_INITIALIZED' in text), 'Native observation differs')
        require(case['provider_added'] == ('PROVIDER_ADDED '+provider in text), 'Provider observation differs')
        require(case['model_session_created'] == ('MODEL_SESSION_CREATED' in text), 'Model observation differs')
        if provider == 'cpu':
            require(case['candidate'] and case['exit_code'] == 0 and case['model_session_created'], 'CPU control failed')
        else:
            require(not case['candidate'] and case['exit_code'] != 0 and not case['model_session_created'], 'A backend is usable; run its save matrix')
        if provider == 'cuda':
            require(case['native_initialized'] and not case['provider_added'] and 'error 126' in text, 'CUDA blocker differs')
        if provider == 'directml':
            require(not case['native_initialized'] and 'DLL) initialization routine failed' in text, 'DirectML blocker differs')
        require(all(v['machine'] == '0x8664' for v in case['native_libraries'].values()), 'Unexpected architecture')
    require(sha(source/'hardware.log') == data['hardware']['log_sha256'], 'Hardware log changed')
    release = json.loads((inspection/'release.json').read_text())
    names = {'cpu':'cpu', 'cuda':'cuda', 'directml':'windows'}
    data['official_artifacts'] = {}
    for provider, variant in names.items():
        asset, = [v for v in release['assets'] if v['name'] == f'NeoForge-terrain-diffusion-mc-2.3.0-{variant}+1.21.1.jar']
        require(asset['digest'] == 'sha256:'+h['PINS'][provider], 'Release API digest differs')
        data['official_artifacts'][provider] = {k:asset[k] for k in ('name','digest','size','browser_download_url')}
    history = json.loads((inspection/'hf-commits.json').read_text())
    require([v['id'] for v in history] == ['ad2df557eca5645f588766101cf3bc3682455c3e',
                                        'b564963e838dd741d1eab99c904f86a7888c0b7a'], 'Official ONNX history changed')
    require(json.loads((inspection/'onnx-model.json').read_text())['sha'] == history[0]['id'], 'ONNX revision differs')
    tag = json.loads((inspection/'source-tag.json').read_text())['object']['sha']
    require(tag == '8acd2b680ee248334637f8cf13f6c78ac20003da', 'TD source changed')
    catalog = json.loads((inspection/'model-repositories.json').read_text())
    repositories = {}
    for entry in catalog:
        name = entry['id'].split('/')[1]
        path = inspection/(name+('-recursive.json' if name in ('terrain-diffusion-30m','terrain-diffusion-90m','terrain-diffusion-90m-pool2') else '-tree.json'))
        tree = json.loads(path.read_text())
        repositories[entry['id']] = {'files':[v for v in tree if v['type'] == 'file']}
        if name != 'terrain-diffusion-30m-onnx':
            require(not any(v['path'].endswith('.onnx') for v in tree), 'Alternate ONNX candidate found')
    data['selection'] = {'td_source_commit':tag, 'official_onnx_history':history,
                         'official_model_catalog':repositories,
                         'scope':'Official author catalog only; no exhaustive third-party search or export certification',
                         'decision':'Blocked: no second ready-to-load official ONNX weight set; neither official GPU runtime initializes a model session here',
                         'required_matrix_context_changes':{'cuda_or_directml':['dependency','backend'], 'alternate_weights':['models']}}
    raw = [p for p in sorted(inspection.iterdir()) if p.suffix in ('.json','.java','.md','.txt','.log')]
    data['inspection_sha256'] = {p.name:sha(p) for p in raw}
    data['raw_results_sha256'] = sha(source/'feasibility.json')
    text = json.dumps(data, indent=2)+'\n'
    require('C:\\\\Users' not in text and 'C:/Users' not in text, 'Nonportable path')
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--inspection', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.write_text(export(a.source, a.inspection))
