"""Portable FAILED navigation-1 verification. Never launches a client or TD."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import runpy
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'runs/acceptance/td-navigation-1'
STEM=ROOT/'docs/evidence/td-navigation'
BASE=runpy.run_path(str(ROOT/'scripts/export-retained-client.py'))

def sha(b): return hashlib.sha256(b).hexdigest()

def audit(m):
    assert b'BUILD SUCCESSFUL' in m['raw/final-build.log'].replace(b'\x00',b'')
    with zipfile.ZipFile(io.BytesIO(m['raw/final-compile-only.jar'])) as jar:
        assert 'dev/wilyjeb/retainedclient/mixin/Keys.class' in jar.namelist()
    with zipfile.ZipFile(io.BytesIO(m['raw/attempt-02/executed/retained-navigation-1.jar'])) as jar:
        assert 'dev/wilyjeb/retainedclient/mixin/Keys.class' not in jar.namelist()
    ledger=json.loads(m['raw/ledger.json'])
    assert len(ledger)==2 and ledger[0]['status']=='failed-login-interrupted' and ledger[1]['status']=='exit-0'
    assert all(0<v['elapsed']<=1200 for v in ledger) and sum(v['elapsed'] for v in ledger)<=2400
    result=[];maximum=0
    for i in (1,2):
        pre=f'raw/attempt-{i:02}/'
        console=m[pre+'console.log'].decode(errors='replace')
        loaded=m[pre+'class-load.log'].decode(errors='replace').lower()
        assert not any(s in loaded for s in ('terraindiffusion','terrain_diffusion','terrain-diffusion','onnxruntime','ai.onnx','dev.wilyjeb.geology.domain.','dev.wilyjeb.geology.world.'))
        inv=json.loads(m[pre+'inventory.json'])
        assert all(n.startswith('saves/navigation-only/') for n in inv if n.startswith('saves/'))
        assert [n for n in inv if n.startswith('mods/')]==['mods/retained-navigation-1.jar']
        assert any(n=='saves/navigation-only/level.dat' for n in inv)
        for f,h in {'RetainedMap.java':'59573cb79b24c1c1526018a237cfa0d3331f9fdc59311b0afbea7c6f54b69407','RetainedMapScreen.java':'e2e674602aea6004144fa18a0f30bc365475757b88cea388d378db7ca52bb3d2','retained-map.tsv':'ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872'}.items():
            assert sha(m[pre+'executed/'+f])==h
        assert 'RETAINED_NAV guard rejected ../continuing' in console
        assert 'RETAINED_NAV guard rejected other-world' in console
        assert 'RETAINED_NAV guard fresh integrated server' in console
        debug=m[pre+'logs/debug.log'].decode(errors='replace')
        for guard in ('SaveBarrier','WorldBarrier','TitleOnly','Hud','LanBarrier'):
            assert 'Mixing '+guard+' from retained-navigation.mixins.json' in debug
        for row in m[pre+'monitor.jsonl'].decode().splitlines():
            s=json.loads(row);assert s['elapsed']<=1200 and s['working_set']<=6*1024**3 and s['output_bytes']<=2*1024**3 and s['free']>=4*1024**3
            maximum=max(maximum,s['working_set'])
        if i==1:
            assert 'String too big (was 18 characters, max 16)' in console
            assert 'RETAINED_NAV position' not in console
            result.append('FAILED local login: synthetic name exceeds 16 characters')
        else:
            assert 'RETAINED_NAV guard local attachment' in console
            assert 'RETAINED_NAV position' in console and 'RETAINED_NAV panel' in console
            assert 'RETAINED_NAV route ' not in console
            assert 'RETAINED_NAV overlay ' not in console
            assert 'Stopping server' in console
            result.append('FAILED movement/controls acceptance; HUD rendered, panel worked from title; normal exit')
        with zipfile.ZipFile(io.BytesIO(m[pre+'executed/retained-navigation-1.jar'])) as jar:
            assert sha(jar.read('retained-map.tsv'))=='ab7168c07af32e981601d2e2fecb7a8457ec3607e68e2dec0731a6c86a67b872'
        shots=('title','failure') if i==1 else ('title','entry','hud-controls-failed','after-world-no-reopen','panel-cover','panel-return-title')
        for shot in shots: assert m[pre+shot+'.jpg'].startswith(b'\xff\xd8\xff')
    actions=json.loads(m['actions.json']);assert actions['acceptance']=='FAILED' and actions['new_launches_allowed']==0
    post=json.loads(m['raw/post-checks.json'])
    assert all(post[f'attempt-{i:02}']['match'] and post[f'attempt-{i:02}']['dependency_hash_checks']==129 for i in (1,2))
    assert post['viewer_repairs']=={
        'docs/td-region-viewer.html':'79b49d7f5b4425cb43a7c232f09fe388966cd6abd1ee7a047e2a789bf7263660',
        'scripts/build-td-region-preview.py':'5cbe8a855f22f150500d6e7af2bd6906fe4dea3dc5d711e34883d19fcc7c8658'}
    return dict(contract='navigation-1',acceptance='FAILED',outcomes=result,attempts=2,
        charged_seconds=sum(v['elapsed'] for v in ledger),maximum_sampled_working_set=maximum,
        td_executed=False,movement_verified=False,final_event_adapter='compile-only',
        actual_configurations=[[1600,1000,2]],old_evidence='reused; not runtime rerun')

def collect():
    m={}
    for p in sorted(RAW.rglob('*')):
        if p.is_file() and 'natives' not in p.relative_to(RAW).parts:m['raw/'+p.relative_to(RAW).as_posix()]=p.read_bytes()
    for p in sorted((ROOT/'diagnostics/retained-navigation').rglob('*')):
        if p.is_file() and not any(s in p.parts for s in ('build','.gradle')):m[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    for name in ('scripts/launch-retained-navigation.py','scripts/export-retained-navigation.py','scripts/test-retained-navigation.py','docs/td-navigation-protocol.md'):
        m[name]=(ROOT/name).read_bytes()
    m['actions.json']=(ROOT/'docs/evidence/td-navigation-actions.json').read_bytes()
    return m

def export(strict=False):
    m=collect();r=audit(m);data=BASE['encode'](m)
    r.update(archive_sha256=sha(data),members={n:sha(b) for n,b in sorted(m.items())})
    for suffix,b in (('.zip',data),('.json',(json.dumps(r,indent=2,sort_keys=True)+'\n').encode())):
        p=STEM.with_suffix(suffix)
        if strict:assert p.read_bytes()==b,p
        else:p.write_bytes(b)
    for name in ('entry','hud-controls-failed','panel-cover'):
        b=m['raw/attempt-02/'+name+'.jpg'];p=ROOT/('docs/evidence/td-navigation-'+name+'.jpg')
        if strict:assert p.read_bytes()==b
        else:p.write_bytes(b)
    print('PASS portable failed-navigation evidence'+(' strict' if strict else ''))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--strict',action='store_true');export(p.parse_args().strict)
