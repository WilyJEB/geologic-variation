"""One frozen offline pair; provenance DAGs carry no neural values."""
import hashlib
import json
from pathlib import Path
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = runpy.run_path(str(ROOT/'scripts/model-td-window-history.py'))
KEYS = [(-16,-8), (-16,-7), (-16,6), (-16,7)]
ORDINALS = {1: [85,90,*range(231,245),326,366],
            6: [85,90,*range(231,241),322,362]}


def encoded(x):
    return (json.dumps(x, sort_keys=True, separators=(',',':'))+'\n').encode()


def sha(x):
    return hashlib.sha256(x).hexdigest()


class Batches(list):
    def __init__(self, model):
        super().__init__(); self.model = model

    def append(self, batch):
        m = self.model
        reads = m.frames[-1]
        m.frames[-1] = []
        group = len(m.nodes)
        for key in batch['keys']:
            dependencies = [dict(stage=s, bounds=b, versions=vs)
                            for s,b,vs in reads]
            signature = dict(request=m.ordinal, stage=batch['stage'], key=key, batch=batch['keys'],
                reads=[dict(stage=s, bounds=b,
                    versions=[dict(key=k, fingerprint=m.nodes[v]['fingerprint'])
                              for k,v in vs]) for s,b,vs in reads])
            node = dict(id=len(m.nodes), group=group,
                        **signature, dependencies=dependencies,
                        fingerprint=sha(encoded(signature)))
            m.nodes.append(node)
            m.versions[batch['stage']][tuple(key)] = node['id']
        super().append(batch)


class Trace(FROZEN['Model']):
    def __init__(self):
        super().__init__()
        self.nodes=[]; self.frames=[]; self.slices=[]; self.checkpoints=[]
        self.versions={s:{} for s in FROZEN['STAGES']}
        self.batches=Batches(self)

    def ensure(self, stage, ranges):
        self.frames.append([])
        super().ensure(stage, ranges)
        self.frames.pop()

    def slice(self, stage, bounds):
        # Same signed intersections, assembly accesses and post-assembly eviction
        # as frozen Model.slice; version bookkeeping is observational only.
        self.ensure(stage,[bounds])
        channels,size,stride,_ = FROZEN['STAGES'][stage]
        cache=self.cache[stage]
        reads=[]
        for k in FROZEN['windows'](bounds,size,stride):
            if k in cache:
                reads.append((k,self.versions[stage][k]))
                cache.move_to_end(k)
        before=list(cache)
        removed=[]
        while len(cache)*channels*size*size*4 > FROZEN['LIMIT'] and len(cache)>1:
            removed.append(cache.popitem(last=False)[0])
        if removed:
            self.evictions.append(dict(request=self.ordinal,stage=stage,keys=removed))
        self.slices.append(dict(request=self.ordinal,stage=stage,bounds=bounds,
            reads=reads, removed=removed,
            # Full order only at eviction; normal reads encode promotion order.
            order_before_eviction=before if removed else None))
        if self.frames:
            self.frames[-1].append((stage,bounds,reads))

    def snapshot(self):
        return {s:[dict(key=k,version=self.versions[s][k]) for k in c]
                for s,c in self.cache.items()}


def trace(case, requests):
    m=Trace(); m.slice('coarse',(0,0,1,1))
    targets={t['ordinal'] for t in case['targets']}
    for q in requests:
        before=m.snapshot() if q['ordinal'] in targets else None
        m.request(q,case['scale'])
        m.checkpoints.append(dict(ordinal=q['ordinal'], total=m.total,
            sizes={s:len(c) for s,c in m.cache.items()},
            distinguishing_init=[dict(key=k, present=k in m.cache['init'],
                lru_rank=list(m.cache['init']).index(k) if k in m.cache['init'] else None)
                for k in KEYS], before_target=before,
            after_target=m.snapshot() if q['ordinal'] in targets else None))
    return m


def plain(m):
    return dict(nodes=m.nodes,slices=m.slices,checkpoints=m.checkpoints,
                batches=m.batches,evictions=m.evictions,total=m.total)


def ancestors(m, roots):
    seen=set(); pending=list(roots)
    while pending:
        v=pending.pop()
        if v in seen: continue
        seen.add(v)
        pending.extend(vv for d in m.nodes[v]['dependencies'] for _,vv in d['versions'])
    return seen


def compare(full, reduced, case):
    result=[]
    # Creation ancestry of every distinguishing-key occurrence, including
    # recomputation, and every target output (not just the differing keys).
    def creation(m):
        return [(n['request'],n['key'],n['fingerprint']) for n in m.nodes
                if n['stage']=='init' and tuple(n['key']) in KEYS]
    creation_equal=creation(full)==creation(reduced)
    for target in case['targets']:
        ordinal=target['ordinal']
        fs=next(c for c in full.checkpoints if c['ordinal']==ordinal)
        rs=next(c for c in reduced.checkpoints if c['ordinal']==ordinal)
        roots=[n['id'] for n in full.nodes if n['request']==ordinal]
        roots += [n['id'] for n in full.nodes if n['stage']=='init' and tuple(n['key']) in KEYS]
        closure=ancestors(full,roots)
        relevant={(full.nodes[v]['stage'],tuple(full.nodes[v]['key'])) for v in closure}
        relevant.update(('init',k) for k in KEYS)
        def cache_signature(m,snapshot):
            return {s:[(e['key'],m.nodes[e['version']]['fingerprint']) for e in entries
                       if (s,tuple(e['key'])) in relevant] for s,entries in snapshot.items()}
        def groups(m):
            return [(b['stage'],b['keys']) for b in m.batches if b['request']==ordinal]
        def ancestry(m):
            return [(n['stage'],n['key'],n['fingerprint']) for n in m.nodes if n['request']==ordinal]
        def eviction(m):
            return [dict(request=e['request'],stage=e['stage'],bounds=e['bounds'],
                removed=e['removed'],order=e['order_before_eviction']) for e in m.slices
                if e['request']<=ordinal and e['stage']=='init'
                and any(tuple(k) in KEYS for k in e['removed'])]
        fcache=cache_signature(full,fs['before_target'])
        rcache=cache_signature(reduced,rs['before_target'])
        checks=dict(distinguishing_creation_ancestry=creation_equal,
            target_batch_membership=groups(full)==groups(reduced),
            target_dependency_creation_ancestry=ancestry(full)==ancestry(reduced),
            relevant_membership_access_order=fcache==rcache,
            distinguishing_eviction_timing_and_context=eviction(full)==eviction(reduced))
        result.append(dict(col=target['col'],ordinal=ordinal,checks=checks,
            passed=all(checks.values()),full_target_batches=groups(full),
            reduced_target_batches=groups(reduced), relevant_pre_target_full=fcache,
            relevant_pre_target_reduced=rcache,
            full_distinguishing_evictions=eviction(full),
            reduced_distinguishing_evictions=eviction(reduced)))
    return dict(scale=case['scale'],target_comparisons=result,
                passed=all(t['passed'] for t in result))


def evaluate(read):
    old=FROZEN['evaluate'](read)
    assert all(c['counter_gate'] for c in old['controls']+old['cases']), 'Frozen counter gate'
    cases=json.loads(read('reconstruction.json'))['cases']
    traces={}; comparisons=[]; selections=[]
    for case,baseline in zip(cases,old['cases']):
        full=trace(case,case['requests'])
        assert encoded(full.batches)==encoded(baseline['batches'])
        assert encoded(full.evictions)==encoded(baseline['evictions'])
        assert full.total==baseline['final_count']
        for snap in baseline['snapshots']:
            actual=next(c['before_target'] for c in full.checkpoints if c['ordinal']==snap['ordinal'])
            assert encoded({s:[e['key'] for e in entries] for s,entries in actual.items()})==encoded(snap['cache'])
        selected=[case['requests'][i] for i in ORDINALS[case['scale']]]
        assert [r['ordinal'] for r in selected]==ORDINALS[case['scale']]
        reduced=trace(case,selected)
        comparisons.append(compare(full,reduced,case))
        selections.append(dict(scale=case['scale'],requests=selected))
        for label,m in (('full',full),('reduced',reduced)):
            traces[f'{case["scale"]}-{label}.json']=encoded(plain(m))
    passed=all(c['passed'] for c in comparisons)
    return dict(protocol='pressure-visual-1', frozen_counter_gate=True,
        trace_matches_frozen_model=True,selections=selections,comparisons=comparisons,
        reduction_passed=passed,runtime_experiment_justified=passed,
        new_td_launches=0,historical_assertion_passed=False,
        historical_indices_and_ulps=None,geometry_adoption=False,
        numerical_adoption=False),traces


def visual_data(raw):
    data=json.loads(raw)
    case=next(c for c in data['cases'] if c['scale']==1)
    attempt=case['attempts'][0]
    c=attempt['candidate']; h=[b['elevations'] for b in attempt['bands']]
    assert len(h)==49 and all(len(row)==49 for row in h)
    # Sample-to-sample differences only, no interpolated derivative/extremum.
    difference=[[None]*49 for _ in range(49)]
    for r in range(1,48):
        for col in range(1,48):
            difference[r][col]=max(abs(h[r][col]-h[r+dr][col+dc])
                                  for dr,dc in ((0,-1),(0,1),(-1,0),(1,0)))
    return dict(seed=case['seed'],candidate=c,spacing_native=64,
        x0=c['col']*256+128-1536,z0=c['row']*256+128-1536,
        query_bounds_half_open=[c['row']*256+128-1536,c['col']*256+128-1536,
                               c['row']*256+128+1537,c['col']*256+128+1537],
        original_query_samples=3073*3073,retained_point_values=49*49,
        full_patch_sha256=attempt['bands'][0]['full_float_sha256'],
        elevations=h,max_four_neighbor_difference_metres=difference,
        confirmed_geometry=False,abstained_everywhere=True,
        observation='Original 3073x3073 query; only 49x49 point elevations retained here; no continuous surface claimed',
        conceptual_contact_native_offsets=[[-1300,1000],[-700,550],[-150,100],[450,-550],[1050,-1150]],
        conceptual_origin='Authored connected synthetic-history illustration, not inferred geology')


def export():
    source=ROOT/'docs/evidence/td-window-history.zip'
    with zipfile.ZipFile(source) as z:
        result,traces=evaluate(z.read)
        members={n:z.read(n) for n in z.namelist()}
    # Nested input preserves the previous evidence byte-for-byte as authority.
    members={'inputs/td-window-history.zip':source.read_bytes(),**traces}
    raw=(ROOT/'docs/evidence/td-tracking-negative.json').read_bytes()
    members['inputs/td-tracking-negative.json']=raw
    members['visual-data.json']=encoded(visual_data(raw))
    members['result.json']=encoded(result)
    for name in ('td-pressure-visual.png','td-pressure-visual-image.json'):
        members['visual/'+name]=(ROOT/'docs/evidence'/name).read_bytes()
    image_manifest=json.loads(members['visual/td-pressure-visual-image.json'])
    assert sha(members['visual-data.json'])==image_manifest['visual_data_sha256']
    assert sha(members['visual/td-pressure-visual.png'])==image_manifest['png_sha256']
    assert sha((ROOT/'scripts/render-td-pressure-visual.py').read_bytes())==image_manifest['renderer_sha256']
    for name in ('scripts/analyze-td-pressure.py','scripts/render-td-pressure-visual.py',
                 'scripts/test-td-pressure.py','scripts/reexport-td-pressure.py',
                 'docs/td-pressure-visual-protocol.md'):
        members['sources/'+name]=(ROOT/name).read_bytes()
    path=ROOT/'docs/evidence/td-pressure-visual.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,raw in sorted(members.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,raw)
    summary=dict(archive_sha256=sha(path.read_bytes()),members={n:sha(b) for n,b in members.items()},
        result=result)
    (ROOT/'docs/evidence/td-pressure-visual.json').write_bytes(encoded(summary))
    print('Offline reduction passed:',result['reduction_passed'])
    return summary


if __name__=='__main__':
    export()
