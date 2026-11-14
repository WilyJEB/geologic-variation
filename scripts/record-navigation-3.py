"""Record actual actions after an authorized allocation. Never allocates/spawns.

Use --event with an external JSON event (including timestamps/actor/handoffs),
or --check with hash-addressed paths ALREADY captured inside the runtime root.
Screenshots must come from actual supported capture tools, never this script.
--visual records human judgment; --reviewer confirms human visual review.
"""
import argparse
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]
L=runpy.run_path(str(ROOT/'scripts/launch-navigation-3.py'))
R=runpy.run_path(str(ROOT/'scripts/replay-navigation-3.py'))


def record(args):
    output=L['OUTPUT']
    L['require'](output.is_dir() and (output/'ledger.json').is_file(), 'No allocated attempt; cannot record')
    ledger=json.loads((output/'ledger.json').read_text())
    L['require'](ledger['attempts_used']==1 and ledger['attempts_remaining']==0, 'Wrong budget')
    path=output/'actions.json'
    actions=json.loads(path.read_text()) if path.exists() else dict(execution_kind='actual-client',
        actual_observations=[],computed_checks={},visual_judgment='',reviewer_confirmed_all_visual_checks=False,
        events=[],checks={n:dict(result='not-observed',observation='',evidence=[]) for n in R['CHECKS']})
    if args.event:
        event=json.loads(args.event.read_text())
        L['require'](event['sequence']==len(actions['events']), 'Event sequence must be complete')
        actions['events'].append(event)
        actions['actual_observations'].append(event['observation'])
    if args.check:
        refs=[]
        for reference in args.evidence:
            role,name=reference.split('=',1) if '=' in reference else ('capture',reference)
            p=output/name
            L['require'](p.resolve().is_relative_to(output.resolve()) and p.is_file(), 'Evidence must exist inside attempt')
            refs.append(dict(role=role,path=p.relative_to(output).as_posix(),sha256=L['sha'](p.read_bytes())))
        actions['checks'][args.check]=dict(result=args.result,observation=args.observation,evidence=refs)
        if args.configuration:
            actions['checks'][args.check]['observed_configuration']=args.configuration
    if args.visual:
        actions['visual_judgment']=args.visual
    if args.reviewer:
        actions['reviewer_confirmed_all_visual_checks']=True
        actions['reviewer']=args.reviewer
    L['dump'](path,actions)
    # Inventory is a final snapshot, refreshed after recording/capture; exclude
    # itself so no impossible recursive self-hash is introduced.
    inventory=L['safe_inventory'](output); inventory.pop('inventory.json',None)
    L['dump'](output/'inventory.json',inventory)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--event',type=Path)
    p.add_argument('--check',choices=R['CHECKS'])
    p.add_argument('--result',choices=('pass','unmet','not-observed'),default='not-observed')
    p.add_argument('--observation',default='')
    p.add_argument('--evidence',nargs='*',default=[])
    p.add_argument('--configuration',nargs=3,type=int,metavar=('WIDTH','HEIGHT','GUI'))
    p.add_argument('--visual')
    p.add_argument('--reviewer')
    record(p.parse_args())
