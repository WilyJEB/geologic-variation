"""Attribute saved coal differences to observed natural writes without hiding strict failures."""
from collections import Counter,defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).parent
compare_module=runpy.run_path(str(HERE/'compare-runtime-chunks.py'))
blocks=compare_module['blocks']
HOSTS={'minecraft:stone'}|{'geologic_variation:'+name for name in ('limestone','slate','quartzite','gabbro')}
COAL={'minecraft:coal_ore','minecraft:deepslate_coal_ore'}
COAL_HOSTS=HOSTS|{'minecraft:granite','minecraft:diorite','minecraft:andesite','minecraft:deepslate','minecraft:tuff'}


def read_case(root,row):
    path=root/row['name']
    with (path/'coal-write-trace.json').open('rb') as handle:
        if hashlib.file_digest(handle,'sha256').hexdigest()!=row['trace_sha256']:
            raise ValueError('Raw trace hash changed')
    trace=json.loads((path/'coal-write-trace.json').read_text())
    if trace['overflow'] or trace['unmatched_writes']:
        raise ValueError('Truncated or unmatched trace')
    events=trace['records']
    begin={e['placement']:e for e in events if e['event']=='begin'}
    end={e['placement']:e for e in events if e['event']=='end'}
    checks={(e['placement'],tuple(e['position']),e['target']):e for e in events if e['event']=='check'}
    writes=defaultdict(list)
    for e in events:
        if e['event']=='write':
            if e['placement'] not in begin:
                raise ValueError('Write has no captured natural source')
            writes[tuple(e['position'])].append(e)
    final={p:s for x,z in row['plan']['chunks'] for p,s in blocks(path/'world',x,z).items()}
    final_coal={p for p,s in final.items() if s['Name'] in COAL}
    coal_writes={p:ws for p,ws in writes.items() if any(e['target'] in COAL for e in ws)}
    missing={p for p in final_coal if not any(w['target']==final[p]['Name'] for w in coal_writes.get(p,[]))}
    if missing:
        raise ValueError(f'{len(missing)} final coal positions have no observed write')
    cross=[e for ws in writes.values() for e in ws
           if begin[e['placement']]['source']!=[e['position'][0]//16,e['position'][2]//16]]
    watched=set(tuple(c) for c in row['plan']['chunks'])
    rejected=[e for e in checks.values() if e['previous'] in COAL and not e['accepted']]
    summary={**row,'final_trace_summary':{k:v for k,v in trace.items() if k!='records'},
             'final_coal_positions':len(final_coal),'final_coal_without_trace':len(missing),
             'event_counts':dict(Counter(e['event'] for e in events)),
             'cross_chunk_writes':len(cross),'rejected_existing_coal':len(rejected),
             'watched_cross_chunk_writes':sum((e['position'][0]//16,e['position'][2]//16) in watched for e in cross),
             'watched_coal_cross_chunk_writes':sum(e['target'] in COAL and (e['position'][0]//16,e['position'][2]//16) in watched for e in cross),
             'state_changed_between_check_and_write':sum(checks[(e['placement'],tuple(e['position']),e['target'])]['previous']!=e['previous']
                 for ws in writes.values() for e in ws if e['target'] in COAL),
             'rejected_existing_coal_random_deltas':dict(Counter(str(e['random_after']-e['random_before']) for e in rejected)),
             'duplicate_write_positions':sum(len(ws)>1 for ws in writes.values())}
    return {'summary':summary,'begin':begin,'end':end,'checks':checks,'writes':writes,'final':final}


def chains(a,b):
    examples=[]
    for key,rejected in a['checks'].items():
        accepted=b['checks'].get(key)
        if not accepted or rejected['accepted'] or rejected['previous'] in COAL_HOSTS:
            continue
        if not accepted['accepted'] or accepted['previous'] not in COAL_HOSTS:
            continue
        place=rejected['placement'];left=a['begin'][place];right=b['begin'][place]
        if left['origin']!=right['origin'] or left['feature_seed']!=right['feature_seed'] or left['discard']!=0.5:
            continue
        if left['random_count']!=right['random_count'] or rejected['random_before']!=accepted['random_before']:
            continue
        if rejected['random_after']-rejected['random_before']!=0 or accepted['random_after']-accepted['random_before']!=1:
            continue
        blockers=[w for w in a['writes'][tuple(rejected['position'])] if w['sequence']<rejected['sequence']
                  and a['begin'][w['placement']]['source']!=left['source']]
        if not blockers:
            continue
        group,index=place.rsplit('/',1);following=group+'/'+str(int(index)+1)
        next_a,next_b=a['begin'].get(following),b['begin'].get(following)
        if not next_a or not next_b or next_a['origin']==next_b['origin']:
            continue
        downstream=[]
        for side in (a,b):
            for pos,ws in side['writes'].items():
                if pos not in a['final'] or pos not in b['final']:
                    continue
                names={a['final'][pos]['Name'],b['final'][pos]['Name']}
                if names&COAL and names&HOSTS and side['final'][pos]['Name'] in COAL and any(
                    w['placement']==following and w['target']==side['final'][pos]['Name'] for w in ws):
                    downstream.append({'position':list(pos),'left':a['final'][pos]['Name'],'right':b['final'][pos]['Name']})
        if not downstream:
            continue
        blocker=blockers[-1]
        examples.append({'placement':place,'source':left['source'],'feature_seed':left['feature_seed'],
            'same_origin':left['origin'],'position':rejected['position'],
            'blocking_write':blocker,'blocking_source':a['begin'][blocker['placement']]['source'],
            'blocked_check':rejected,'unblocked_check':accepted,
            'next_placement':following,'next_origin_blocked_run':next_a['origin'],'next_origin_other_run':next_b['origin'],
            'downstream_saved_difference_examples':downstream[:4]})
        if len(examples)==4:
            break
    return examples


def summarize(root):
    rows=json.loads((root/'trace-results.json').read_text())
    if len(rows)!=4:
        raise ValueError('Expected both traversal orders in both arms')
    cases=[read_case(root,r) for r in rows]
    comparisons=[]
    for addon in (False,True):
        a,b=[c for c in cases if c['summary']['addon']==addon]
        changed=[]
        for pos,left in a['final'].items():
            right=b['final'][pos]
            pair={left['Name'],right['Name']}
            if pair&COAL and pair&HOSTS:
                side=a if left['Name'] in COAL else b
                changed.append({'position':list(pos),'left':left['Name'],'right':right['Name'],
                    'writes':[{**e,'source':side['begin'][e['placement']]['source'],
                               'feature_seed':side['begin'][e['placement']]['feature_seed']} for e in side['writes'][pos] if e['target'] in COAL]})
        examples=chains(a,b)+chains(b,a)
        if not changed or not examples:
            raise ValueError('No natural coal differences or complete cross-chunk/random-draw chain found')
        comparisons.append({'addon':addon,'saved_blocks':compare_module['compare'](
            root/a['summary']['name']/'world',root/b['summary']['name']/'world',a['summary']['plan']['chunks']),
            'host_coal_differences':len(changed),'all_differing_coal_observed':all(c['writes'] for c in changed),
            'difference_examples':changed[:8],'natural_order_chain_examples':examples})
    return {'cases':[c['summary'] for c in cases],'comparisons':comparisons}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.root)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{'addon':c['addon'],'host_coal_differences':c['host_coal_differences'],
                      'chains':len(c['natural_order_chain_examples'])} for c in result['comparisons']],indent=2))
