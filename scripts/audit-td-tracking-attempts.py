"""Portable accounting of excluded development attempts; never coverage acceptance."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def audit():
    rows=[]
    for suffix,reason in [('01','sandbox denied immutable hardlink before launch'),
                          ('02','excluded: patch responses missing from transcript; manually stopped, hung shutdown terminated'),
                          ('03','frozen 512 MiB disk-reserve guard stopped after first patch band; normal shutdown')]:
        folder=ROOT/f'runs/acceptance/td-tracking-2026-11-04-{suffix}'
        files=list(folder.glob('seed*/console-1.log'))
        item=dict(attempt=folder.relative_to(ROOT).as_posix(),accepted=False,reason=reason,
            fresh_seeds_inspected=False,logs={},raw_acceptance=[])
        for file in files:
            text=file.read_text(errors='replace');item['logs'][file.relative_to(folder).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
            item['raw_acceptance'] += [json.loads(line.split('ACCEPTANCE ',1)[1]) for line in text.splitlines() if 'ACCEPTANCE {' in line]
            item['completed_model_return_log_rows']=text.count('TD_MODEL_RETURN')
            item['model_return_rows_are_not_new_window_counts']=True
            item['new_window_total']=None
            item['new_window_total_reason']='No final counter snapshot; do not infer new windows from model-return rows'
        rows.append(item)
    return dict(attempts=rows,interpretation='Excluded development attempts, no held-out validation or morphology acceptance')


if __name__=='__main__':
    (ROOT/'docs/evidence/td-tracking-attempts.json').write_text(json.dumps(audit(),indent=2)+'\n')
