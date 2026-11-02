"""Validate and export portable #9 startup evidence from completed disposable cases."""
import argparse
import hashlib
import json
from pathlib import Path


def require(value,message):
    if not value:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def summarize(root):
    result=json.loads((root/'context-results.json').read_text())
    require({c['name'] for c in result['cases']}=={'seed','scale','schema1','missing','malformed'},'Incomplete case set')
    baseline=result['baseline'];before=baseline['before'];after=baseline['after_config_edit']
    require(before['settings']['owner_matches'] and after['settings']['owner_matches'],'Invalid baseline owner')
    require(any(k.startswith('geologic_variation:') and v>0 for k,v in before['chunk']['counts'].items()),'Empty regional block sample')
    require(before['settings']['active']==after['settings']['active'],'Active settings changed')
    require(before['settings']['requested']!=after['settings']['requested'],'Config edit not exercised')
    require(before['settings']['context']==after['settings']['context'],'Context changed')
    require(before['chunk']['blocks_sha256']==after['chunk']['blocks_sha256'],'Existing blocks changed')
    require(before['region']==after['region'],'Region identity changed')
    for name,hashes in [('baseline',baseline['logs'])]+[(c['name'],c['logs']) for c in result['cases']]:
        for log,digest in hashes.items():
            require(sha(root/name/log)==digest,'Raw log hash changed')
    for case in result['cases']:
        require(case['artifacts']==baseline['artifacts'],'Case artifacts changed')
        require(case['before_rejection']['regions'],'No existing region files exercised')
        require(case['before_rejection']==case['after_rejection'],'Rejection modified snapshot/region files')
        require(case['rejection']['process_exited'] and not case['rejection']['ready'],'Rejection did not exit before Ready')
        require(case['restored_snapshot_sha256']==baseline['snapshot_sha256'],'Restored snapshot differs')
        require(case['restored']['settings']['active']==before['settings']['active'],'Restoration settings differ')
        require(case['restored']['settings']['requested']==after['settings']['requested'],'Edited config was not retained for recovery')
        require(case['restored']['settings']['context']==before['settings']['context'],'Restoration context differs')
        require(case['restored']['settings']['owner_matches'],'Restoration owner differs')
        require(case['restored']['chunk']['blocks_sha256']==before['chunk']['blocks_sha256'],'Restoration blocks differ')
        require(case['restored']['region']==before['region'],'Restoration region differs')
        if case['name'] in ('seed','scale'):
            require(case['rejection']['changed_context_fields']==[case['name']],'Mismatch was not independent')
        if case['name']=='missing':
            require(case['after_rejection']['snapshot'] is None,'Missing snapshot was recreated')
    text=json.dumps(result,indent=2)+'\n'
    require(all(s not in text for s in ('addon_origin','union:/','C:/Users/','rcon.password')),'Nonportable/private evidence')
    return text


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(summarize(args.root))
    print('Validated five startup cases, config isolation, preservation, restoration and log hashes')
