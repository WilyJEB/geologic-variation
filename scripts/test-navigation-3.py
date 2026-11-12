"""Offline fixtures only. Never invokes installed-profile preflight or native Job."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import subprocess
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
L = runpy.run_path(str(ROOT/'scripts/launch-navigation-3.py'))
R = runpy.run_path(str(ROOT/'scripts/replay-navigation-3.py'))


class FakeJob:
    def __init__(self, survivor=False, spawn_error=False, interrupted=False):
        self.survivor=survivor; self.spawn_error=spawn_error; self.interrupted=interrupted
        self.closed=False; self.cleaned=False
        self.identity=dict(ProcessId=101,ParentProcessId=99,CreationDate='fixture-parent',
                           CommandLine='offline fake only',WorkingSetSize='1')
        self.child=dict(ProcessId=102,ParentProcessId=101,CreationDate='fixture-child',
                        CommandLine='offline fake child',WorkingSetSize='1')
    def start(self,cmd,cwd):
        if self.spawn_error:
            raise OSError('fixture spawn failed')
        return [self.identity]
    def pids(self):
        if self.interrupted:
            raise KeyboardInterrupt('fixture interruption')
        return [102] if self.survivor else []
    def identities(self,pids):
        return [self.child] if pids else []
    def exit_code(self):
        return 0
    def cleanup(self,known):
        self.cleaned=True
        return dict(forced=self.survivor,job_empty=True,remaining_job_pids=[],
                    checks=[dict(identity=v,absent=True) for v in known.values()])
    def close(self):
        self.closed=True


class Preparation(unittest.TestCase):
    def complete_fixture(self):
        # Synthetic acceptance-path fixture exists only in memory. It is never
        # published as client evidence and never invokes native APIs.
        prepared=R['members'](ROOT/'docs/evidence/td-navigation-3-preparation.zip')
        data={'executed/'+n:b for n,b in prepared.items() if not n.startswith('artifact/')}
        data['executed/retained-navigation-1.jar']=prepared['artifact/retained-navigation-1.jar']
        digest=L['sha'](prepared['docs/td-navigation-3-hashes.json'])
        game='td-navigation-2/attempt-01/'
        data[game+'mods/retained-navigation-1.jar']=prepared['artifact/retained-navigation-1.jar']
        data[game+'dependencies.json']=b'{"fixture-shared":"abc"}'
        data['shared-post.json']=b'{"fixture-shared":"abc"}'
        data[game+'class-load.log']=b'fixture allowed classes'
        data[game+'logs/debug.log']='\n'.join('Mixing '+g+' from retained-navigation.mixins.json' for g in ('SaveBarrier','WorldBarrier','TitleOnly','Hud','LanBarrier','Keys')).encode()
        lines=['RETAINED_NAV guard fresh save fixture','RETAINED_NAV guard fresh integrated server',
               'RETAINED_NAV guard local attachment','RETAINED_NAV guard rejected ../continuing',
               'RETAINED_NAV guard rejected other-world']
        positions=[]
        def pos(x,z,scale):
            import math
            positions.append((x,z,scale))
            lines.append(f'RETAINED_NAV position {x:.6f} {z:.6f} scale {scale} block {math.floor(x)} {math.floor(z)} chunk {math.floor(x)//16} {math.floor(z)//16} support site')
        movement=[]
        for i,(x,z) in enumerate(R['ROUTE']):
            lines.append('RETAINED_NAV route '+str(i)); scale=6 if i==6 else 1
            pos(x,z,scale)
            if i in (0,6):
                a=len(positions)-1; pos(x,z+20,scale)
                movement.append(dict(sequence=len(movement),unix=10+len(movement),kind='human-movement',
                    actor='human',observation='SYNTHETIC OFFLINE FIXTURE',scale=scale,released=True,
                    held_seconds=2,holds=[dict(seconds=2,released=True,unix=10+len(movement))],
                    before_position_index=a,after_position_index=a+1,before_image='fixture.png',after_image='fixture.png'))
        lines+=['Stopping server','Stopping!']
        data[game+'console.log']='\n'.join(lines).encode()
        identity=dict(ProcessId=101,ParentProcessId=99,CreationDate='fixture',CommandLine='offline',WorkingSetSize=1)
        data['processes.jsonl']=(json.dumps(dict(kind='suspended-parent',timestamp=1,identities=[identity]))+'\n').encode()
        data['cleanup.json']=json.dumps(dict(job_empty=True,remaining_job_pids=[],forced=False,
                  checks=[dict(identity=identity,absent=True)])).encode()
        data['monitor.jsonl']=(json.dumps(dict(wall=20,has_position=True,working_set=1,output_bytes=1,free=5*1024**3,
                  td_requests=0,model_calls=0,provider_initializations=0,windows=0))+'\n').encode()
        data['fixture.png']=b'\x89PNG\r\n\x1a\nSYNTHETIC NONIMAGE FIXTURE - NOT LIVE EVIDENCE'
        actions=dict(execution_kind='actual-client',actual_observations=['SYNTHETIC FIXTURE'],computed_checks={},
                     visual_judgment='SYNTHETIC FIXTURE',reviewer_confirmed_all_visual_checks=True,events=movement,
                     checks={n:dict(result='pass',observation='SYNTHETIC FIXTURE',evidence=[dict(path='fixture.png',sha256=L['sha'](data['fixture.png']))]) for n in R['CHECKS']})
        for name,roles in R['CAPTURE_ROLES'].items():
            refs=[]
            for role in roles:
                path=name+'-'+role+'.png';data[path]=data['fixture.png']
                refs.append(dict(role=role,path=path,sha256=L['sha'](data[path])))
            actions['checks'][name]['evidence']=refs
            if name.startswith('configuration_'):
                actions['checks'][name]['observed_configuration']=[1600,1000,2] if '1600' in name else [1200,900,1]
        data['actions.json']=json.dumps(actions).encode()
        data['ledger.json']=json.dumps(dict(attempts_used=1,attempts_remaining=0,charged_seconds=1200,
                    finalized=True,status='exited-evidence-pending',exit_code=0,immutable_inputs_unchanged=True,
                    preflight=dict(manifest_sha256=digest),approval=dict(manifest_sha256=digest))).encode()
        self.reinventory(data)
        return data

    def reinventory(self,data):
        data['inventory.json']=json.dumps({n:dict(bytes=len(b),sha256=L['sha'](b)) for n,b in data.items() if n!='inventory.json'}).encode()

    def test_complete_synthetic_path_and_every_required_row(self):
        data=self.complete_fixture()
        self.assertEqual(R['runtime'](data)['acceptance'],'COMPLETE')
        for name in R['CHECKS']:
            bad=dict(data); actions=json.loads(bad['actions.json']); del actions['checks'][name]
            bad['actions.json']=json.dumps(actions).encode(); self.reinventory(bad)
            with self.subTest(name=name):
                self.assertEqual(R['runtime'](bad)['acceptance'],'INCOMPLETE')

    def test_decimal_offset_cannot_pass(self):
        data=self.complete_fixture(); n='td-navigation-2/attempt-01/console.log'
        data[n]=data[n].replace(b'2944.000000',b'2944.500000')
        self.reinventory(data)
        result=R['runtime'](data)
        self.assertEqual(result['acceptance'],'INCOMPLETE');self.assertIn('exact route 0',result['unmet'])

    def test_teleport_and_unreleased_movement_reject(self):
        for corruption in ('teleport','release','overshoot','missing-image','additional-hold'):
            data=self.complete_fixture(); actions=json.loads(data['actions.json'])
            e=actions['events'][0]
            if corruption=='release':e['released']=False
            elif corruption=='additional-hold':e['holds'].append(dict(seconds=2,released=True,unix=11))
            elif corruption=='missing-image':e['after_image']='missing.png'
            else:
                n='td-navigation-2/attempt-01/console.log'
                if corruption=='teleport':data[n]=data[n].replace(b'RETAINED_NAV position 2944.000000 13844',b'RETAINED_NAV route 0\nRETAINED_NAV position 2944.000000 13844')
                else:data[n]=data[n].replace(b'13844.000000',b'13864.000000').replace(b'block 2944 13844 chunk 184 865',b'block 2944 13864 chunk 184 866')
            data['actions.json']=json.dumps(actions).encode();self.reinventory(data)
            with self.subTest(corruption=corruption),self.assertRaises((ValueError,KeyError)):
                R['runtime'](data)

    def test_cleanup_and_visual_corruption_incomplete(self):
        for corruption in ('forced','survivor','identity-missing','visual-negative','finalization','missing-finalization'):
            data=self.complete_fixture()
            if corruption in ('forced','survivor','identity-missing'):
                cleanup=json.loads(data['cleanup.json'])
                if corruption=='forced':cleanup['forced']=True
                if corruption=='survivor':cleanup['remaining_job_pids']=[102]
                if corruption=='identity-missing':cleanup['checks']=[]
                data['cleanup.json']=json.dumps(cleanup).encode()
            elif corruption=='visual-negative':
                actions=json.loads(data['actions.json']);actions['reviewer_confirmed_all_visual_checks']=False
                actions['checks']['token_second_half']['result']='unmet'; data['actions.json']=json.dumps(actions).encode()
            elif corruption=='missing-finalization':del data['ledger.json']
            else:
                ledger=json.loads(data['ledger.json']);ledger['finalized']=False;data['ledger.json']=json.dumps(ledger).encode()
            self.reinventory(data)
            with self.subTest(corruption=corruption):
                self.assertEqual(R['runtime'](data)['acceptance'],'INCOMPLETE')

    def test_portable_exact(self):
        data=R['members'](ROOT/'docs/evidence/td-navigation-3-preparation.zip')
        self.assertEqual(R['preparation'](data,True)['runtime_acceptance'],'INCOMPLETE')

    def test_preparation_corruptions(self):
        original=R['members'](ROOT/'docs/evidence/td-navigation-3-preparation.zip')
        for name in ('scripts/launch-navigation-3.py','artifact/retained-navigation-1.jar',
                     'src/runtimeProbe/resources/retained-map.tsv',
                     'docs/td-navigation-3-protocol.md'):
            with self.subTest(name=name):
                data=dict(original); data[name]+=b'corrupt'
                with self.assertRaises(ValueError):
                    R['preparation'](data)

    def test_no_allocation(self):
        self.assertFalse(L['OUTPUT'].exists())

    def test_single_slot_even_missing_ledger(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            out=Path(tmp)/'fixture'
            row=L['allocate'](out,{},{}); self.assertEqual(row['attempts_remaining'],0)
            (out/'ledger.json').unlink()  # fixture-only hard-termination simulation
            with self.assertRaises(FileExistsError):
                L['allocate'](out,{},{})

    @patch('subprocess.check_output',return_value='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n')
    def test_authorization_rejects_missing_and_stale(self,git):
        record=dict(explicit_client_launch_authorized=False)
        with self.assertRaises(ValueError):
            L['authorization'](record,'fixture',[])
        context=L['context']()
        record=dict(explicit_client_launch_authorized=True,human_present=True,
                    human_available_through_quit=True,contract='navigation-3',attempts_including_failure=1,
                    context='fixture',observed_context=context,command=[],
                    manifest_sha256=L['sha'](L['FREEZE'].read_bytes()),permission_mode='restricted',
                    human_confirmation_unix=0,
                    pushed_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        with self.assertRaisesRegex(ValueError,'stale'):
            L['authorization'](record,'fixture',[])
        for key,value in [('human_present',False),('context','other'),('command',['other']),
                          ('manifest_sha256','wrong'),('attempts_including_failure',2)]:
            bad=copy.deepcopy(record); bad[key]=value
            with self.assertRaises(ValueError):
                L['authorization'](bad,'fixture',[])

    def test_caps(self):
        sample=dict(wall=1,working_set=1,output_bytes=1,free=5*1024**3,
                    td_requests=0,model_calls=0,provider_initializations=0,windows=0)
        L['cap_check'](sample,False)
        changes=dict(wall=1201,working_set=6*1024**3+1,output_bytes=2*1024**3+1,
                     free=4*1024**3-1,td_requests=1,model_calls=1,provider_initializations=1,windows=1)
        for key,value in changes.items():
            with self.subTest(key=key),self.assertRaises(ValueError):
                L['cap_check']({**sample,key:value},False)
        with self.assertRaisesRegex(ValueError,'Startup'):
            L['cap_check']({**sample,'wall':181},False)

    def exercise(self,job,prepare_error=False,immutable_error=False):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            output=Path(tmp)/'fixture'; row=L['allocate'](output,{},{}); game=output/'game'
            def prepare():
                if prepare_error:
                    raise ValueError('fixture setup error')
                game.mkdir(); (game/'console.log').write_text('Stopping server\nStopping!\n')
                return game,['offline mock, never spawn']
            def unchanged():
                if immutable_error:
                    raise ValueError('immutable fixture changed')
            result=L['run_attempt'](output,row,prepare,lambda:job,unchanged)
            self.assertEqual(result['attempts_remaining'],0)
            self.assertEqual(result['charged_seconds'],1200)
            self.assertEqual(result['acceptance'],'INCOMPLETE')
            self.assertTrue((output/'inventory.json').exists())
            return copy.deepcopy(result), json.loads((output/'cleanup.json').read_text()) if (output/'cleanup.json').exists() else None

    def test_spawn_failure_consumes(self):
        job=FakeJob(spawn_error=True); row,_=self.exercise(job)
        self.assertIn('spawn failed',row['failure']); self.assertTrue(job.cleaned and job.closed)

    def test_setup_failure_consumes(self):
        row,_=self.exercise(FakeJob(),prepare_error=True)
        self.assertIn('setup error',row['failure'])

    def test_interrupt_retains(self):
        job=FakeJob(interrupted=True); row,_=self.exercise(job)
        self.assertIn('KeyboardInterrupt',row['failure']); self.assertTrue(job.cleaned)

    def test_surviving_descendant(self):
        job=FakeJob(survivor=True); row,cleanup=self.exercise(job)
        self.assertIn('Descendant survives',row['failure'])
        self.assertTrue(cleanup['forced']); self.assertEqual(len(cleanup['checks']),2)

    def test_immutable_failure(self):
        row,_=self.exercise(FakeJob(),immutable_error=True)
        self.assertFalse(row['finalized']); self.assertIn('immutable',row['finalization_errors'][0])

    def test_exit_zero_pending(self):
        row,_=self.exercise(FakeJob())
        self.assertEqual(row['status'],'exited-evidence-pending')
        self.assertEqual(row['acceptance'],'INCOMPLETE')

    def test_cleanup_error_retained(self):
        job=FakeJob(); job.cleanup=lambda known: (_ for _ in ()).throw(ValueError('fixture cleanup error'))
        row,_=self.exercise(job)
        self.assertFalse(row['finalized']); self.assertTrue(job.closed)

    def test_save_isolation(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            game=Path(tmp); (game/'saves/continuing').mkdir(parents=True)
            with self.assertRaises(ValueError):
                L['safe_paths'](game)

    def test_forbidden_nested_jar(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('ai/onnx/runtime.class',b'fixture')
        outer=io.BytesIO()
        with zipfile.ZipFile(outer,'w') as z:
            z.writestr('nested.jar',stream.getvalue())
        scan=runpy.run_path(str(ROOT/'scripts/export-navigation-supplement.py'))['scan']
        with self.assertRaises(AssertionError):
            scan(outer.getvalue())

    def test_runtime_missing_finalization_and_evidence(self):
        base={'ledger.json':json.dumps(dict(attempts_used=1,attempts_remaining=0,charged_seconds=1200)).encode()}
        result=R['runtime'](base)
        self.assertEqual(result['acceptance'],'INCOMPLETE'); self.assertIn('finalization',result['unmet'])
        self.assertIn('complete checklist',result['unmet'])

    def test_runtime_inventory_corruption(self):
        data={'ledger.json':json.dumps(dict(attempts_used=1,attempts_remaining=0,charged_seconds=1200)).encode(),
              'inventory.json':json.dumps({'image.png':dict(bytes=2,sha256='wrong')}).encode(),
              'image.png':b'xx'}
        with self.assertRaisesRegex(ValueError,'Inventory mismatch'):
            R['runtime'](data)

    def test_runtime_forbidden_load_and_save(self):
        for name,value in [('td-navigation-2/attempt-01/class-load.log',b'ai.onnx.runtime'),
                           ('td-navigation-2/attempt-01/saves/continuing/level.dat',b'fixture')]:
            data={'ledger.json':json.dumps(dict(attempts_used=1,attempts_remaining=0,charged_seconds=1200)).encode(),name:value}
            with self.assertRaises(ValueError):
                R['runtime'](data)

    def test_no_execution_on_import(self):
        with patch('subprocess.Popen',side_effect=AssertionError('spawn forbidden')),patch('socket.socket',side_effect=AssertionError('network forbidden')):
            runpy.run_path(str(ROOT/'scripts/launch-navigation-3.py'))


if __name__=='__main__':
    unittest.main()
