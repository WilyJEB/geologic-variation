"""Finite coordinate/cache model. Never loads Java, ONNX or a Minecraft world.

Only the four pinned tensor layouts and serial provider paths are represented.
Values are deliberately absent: matching counters cannot establish matching bits.
"""
from collections import OrderedDict, Counter
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 104857600
# channels, spatial size, spatial stride, dependencies (stage,size,stride,offset)
STAGES = {
    'coarse': (7, 64, 48, ()),
    'init': (6, 64, 32, (('coarse', 4, 1, -1),)),
    'step': (6, 64, 32, (('init', 64, 32, 0), ('coarse', 4, 1, -1))),
    'residual': (2, 256, 192, (('step', 32, 24, 0),)),
}


def ceildiv(a, b):
    return -((-a)//b)


def windows(bounds, size, stride):
    r, c, R, C = bounds
    return [(i, j) for i in range(ceildiv(r-size+1, stride), (R-1)//stride+1)
            for j in range(ceildiv(c-size+1, stride), (C-1)//stride+1)]


def depbounds(key, size, stride, offset):
    i, j = key
    return (i*stride+offset, j*stride+offset,
            i*stride+offset+size, j*stride+offset+size)


class Model:
    def __init__(self):
        self.cache = {s: OrderedDict() for s in STAGES}
        self.count = Counter()
        self.batches = []
        self.evictions = []
        self.provider = OrderedDict()
        self.ordinal = -1

    @property
    def total(self):
        return sum(self.count.values())

    def ensure(self, stage, ranges):
        _, size, stride, deps = STAGES[stage]
        cache = self.cache[stage]
        # containsKey does NOT promote access order; insertion-order dedup does.
        pending = list(dict.fromkeys(k for b in ranges for k in windows(b, size, stride)
                                     if k not in cache))
        if not pending:
            return
        for dep, ds, dt, do in deps:
            self.ensure(dep, [depbounds(k, ds, dt, do) for k in pending])
        batchsize = 4 if stage in ('init', 'step') else 1
        for start in range(0, len(pending), batchsize):
            batch = pending[start:start+batchsize]
            # Dependency-major, then batch-member order, with getSlice eviction.
            for dep, ds, dt, do in deps:
                for k in batch:
                    self.slice(dep, depbounds(k, ds, dt, do))
            self.batches.append(dict(request=self.ordinal, stage=stage, keys=batch))
            for k in batch:
                if k not in cache:
                    cache[k] = True
                    self.count[stage] += 1
                cache.move_to_end(k)

    def slice(self, stage, bounds):
        self.ensure(stage, [bounds])
        channels, size, stride, _ = STAGES[stage]
        cache = self.cache[stage]
        for k in windows(bounds, size, stride):
            if k in cache:
                cache.move_to_end(k)
        removed = []
        while len(cache)*channels*size*size*4 > LIMIT and len(cache) > 1:
            removed.append(cache.popitem(last=False)[0])
        if removed:
            self.evictions.append(dict(request=self.ordinal, stage=stage, keys=removed))

    def pipeline(self, bounds, climate=False):
        r, c, R, C = bounds
        # sigma=5 -> kernel11 -> low-resolution pad6 -> native pad48; lc=8.
        padded = ((r-48)//8*8, (c-48)//8*8, ceildiv(R+48, 8)*8, ceildiv(C+48, 8)*8)
        self.slice('residual', padded)
        self.slice('step', tuple(x//8 for x in padded))
        if climate:
            self.slice('coarse', (r//256-8, c//256-8, ceildiv(R, 256)+8, ceildiv(C, 256)+8))

    def request(self, request, scale):
        self.ordinal = request['ordinal']
        b = tuple(request['bounds'])
        api = request['api']
        if api == 'getPipelineCoarse':
            self.slice('coarse', b)
        elif api == 'getPipelineData':
            self.pipeline(b, request['withClimate'])
        else:
            assert api == 'fetchHeightmap' and scale == 6
            if b in self.provider:
                self.provider.move_to_end(b)
                return
            r, c, R, C = b
            self.pipeline((r//scale-2, c//scale-2, ceildiv(R, scale)+2, ceildiv(C, scale)+2), True)
            self.provider[b] = True
            # Pinned hysteresis: >64+4 removes eight oldest, not a 64-entry LRU.
            if len(self.provider) > 68:
                for _ in range(8):
                    self.provider.popitem(last=False)


def replay(case):
    model = Model()
    # Source-derived startup candidate, NOT a historically observed internal trace.
    # RuntimeProbe's startup getter is [0,0,1,1]; four measured windows constrain it.
    model.slice('coarse', (0, 0, 1, 1))
    assert model.total == case['initial_metrics']['computed_windows'] == 4
    checks, targets, snapshots = [], [], []
    requests = case['requests']
    for event, entry in enumerate(case['events_through_last_target']):
        rs = [r for r in requests if r['event'] == event]
        before = model.total
        for r in rs:
            if any(t['ordinal'] == r['ordinal'] for t in case['targets']):
                snapshots.append(dict(ordinal=r['ordinal'], count_before=model.total,
                                      cache={s:list(c) for s,c in model.cache.items()}))
            model.request(r, case['scale'])
            if any(t['ordinal'] == r['ordinal'] for t in case['targets']):
                targets.append(dict(ordinal=r['ordinal'], count_after=model.total,
                    batches=[b for b in model.batches if b['request']==r['ordinal']]))
        value = entry['result']
        if ('delta' in value and 'computed_windows' in value['delta']) or entry['command']=='acceptance metrics':
            delta = 'delta' in value
            observed = value['delta']['computed_windows'] if delta else value['computed_windows']
            predicted = model.total-before if delta else model.total
            check = dict(event=event, kind='command_delta' if delta else 'absolute',
                         observed=observed, predicted=predicted, passed=observed==predicted)
            checks.append(check)
            if observed != predicted:
                return dict(scale=case['scale'], startup='source-derived candidate; internal trace unavailable',
                    counter_checks=checks, counter_gate=False, stopped_at_first_mismatch=True,
                    targets=targets, snapshots=snapshots, batches=model.batches, evictions=model.evictions,
                    final_count=model.total, stage_counts=dict(model.count))
    return dict(scale=case['scale'], startup='source-derived candidate; internal trace unavailable',
        counter_checks=checks, counter_gate=all(c['passed'] for c in checks),
        stopped_at_first_mismatch=False, targets=targets, snapshots=snapshots,
        batches=model.batches, evictions=model.evictions, final_count=model.total, stage_counts=dict(model.count))


def evaluate(read):
    reconstruction = json.loads(read('reconstruction.json'))
    controls = []
    for label in ('pr53', 'pr54'):
        for case in json.loads(read(label+'-results.json'))['cases']:
            m = Model(); m.slice('coarse', (0,0,1,1))
            checks = []
            for event, entry in enumerate(case['events']):
                value = entry['result']
                for b in value.get('requests', []):
                    m.ordinal = event; m.pipeline(b)
                if entry['command'] == 'acceptance metrics':
                    observed = value['computed_windows']
                    checks.append(dict(event=event, observed=observed, predicted=m.total,
                                       passed=observed==m.total))
                    if observed != m.total:
                        break
            controls.append(dict(history=label, case=case['index'], checks=checks,
                                 counter_gate=all(c['passed'] for c in checks)))
            if not controls[-1]['counter_gate']:
                break
        if not controls[-1]['counter_gate']:
            break
    cases = []
    if all(c['counter_gate'] for c in controls):
        for case in reconstruction['cases']:
            cases.append(replay(case))
            if not cases[-1]['counter_gate']:
                break
    reduction = None
    if len(cases)==2 and all(c['counter_gate'] for c in cases) and all(c['counter_gate'] for c in controls):
        # Exactly one candidate, no automated minimization or fitting search:
        # second patch then A, omitting all intervening mixed requests.
        original = reconstruction['cases'][0]
        prefix = [original['requests'][90], original['requests'][326]]
        reduced = Model(); reduced.slice('coarse',(0,0,1,1))
        for request in prefix:
            reduced.request(request,1)
        predicted = [b for b in reduced.batches if b['request']==326 and b['stage'] in ('init','step')]
        historical = [[b for b in c['targets'][0]['batches'] if b['stage'] in ('init','step')] for c in cases]
        # Compare keys/stage, not differing public ordinal labels.
        signature = lambda bs: [(b['stage'],b['keys']) for b in bs]
        reduction = dict(public_ordinals=[90,326], predicted_target_batches=predicted,
            preserves_either_full_prefix_target_grouping=any(signature(predicted)==signature(bs) for bs in historical),
            total_windows=reduced.total, note='One offline candidate only; no pressure-prefix search')
    return dict(cases=cases, controls=controls, reduction=reduction, new_td_launches=0, runtime_experiment_justified=False,
                historical_assertion_passed=False, historical_indices_and_ulps=None,
                geometry_adoption=False, numerical_cause_established=False)


def export():
    path = ROOT/'docs/evidence/td-window-history.zip'
    old = ROOT/'docs/evidence/td-observation-history.zip'
    with zipfile.ZipFile(old) as z:
        contents = {n:z.read(n) for n in ('reconstruction.json', 'pr53-results.json', 'pr54-results.json',
                    'pinned-provider-javap.txt', 'pinned-tensor-javap.txt')}
    contents['result.json'] = (json.dumps(evaluate(contents.__getitem__), indent=2)+'\n').encode()
    for name in ('scripts/model-td-window-history.py', 'scripts/test-td-window-history.py',
                 'scripts/reexport-td-window-history.py',
                 'docs/td-window-history-protocol.md'):
        contents['sources/'+name] = (ROOT/name).read_bytes()
    for name in ('pinned-layout-javap.txt', 'world_pipeline_config.json', 'source-rules.json'):
        contents[name] = (ROOT/'runs/acceptance/td-window-history-offline'/name).read_bytes()
    source = ROOT/'upstream/td-standalone/common/src/main/java/com/github/xandergos/terraindiffusionmc'
    for name,digest in json.loads(contents['source-rules.json'])['source_hashes'].items():
        raw = (source/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==digest
        contents['upstream-source/'+name] = raw
    import subprocess
    contents['startup-RuntimeProbe.java'] = subprocess.check_output(
        ['git','cat-file','--filters','6c5f105:src/runtimeProbe/java/dev/wilyjeb/geology/probe/RuntimeProbe.java'], cwd=ROOT)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    summary = dict(archive_sha256=sha(path.read_bytes()), input_archive_sha256=sha(old.read_bytes()),
                   members={n:sha(b) for n,b in contents.items()},
                   **{k:v for k,v in json.loads(contents['result.json']).items() if k!='cases'},
                   cases=[{k:v for k,v in c.items() if k not in ('batches','evictions','snapshots','targets')}
                          for c in json.loads(contents['result.json'])['cases']])
    (ROOT/'docs/evidence/td-window-history.json').write_text(json.dumps(summary, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    print(json.dumps(export(), indent=2))
