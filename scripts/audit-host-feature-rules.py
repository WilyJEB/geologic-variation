"""Inventory configured feature targets in the exact installed vanilla/TD resources."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def rules(value, path=''):
    if isinstance(value,dict):
        if 'predicate_type' in value:
            yield {'path':path,**value}
        for key,item in value.items():
            yield from rules(item,path+'/'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value):
            yield from rules(item,path+'/'+str(i))


def host_states(value,path=''):
    if isinstance(value,dict):
        if value.get('Name') in ('minecraft:stone','minecraft:deepslate'):
            yield {'path':path,'state':value}
        for key,item in value.items():
            yield from host_states(item,path+'/'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value):
            yield from host_states(item,path+'/'+str(i))


def audit(jars):
    resources = {}
    artifacts = {}
    for jar in jars:
        with jar.open('rb') as handle:
            artifacts[jar.name] = hashlib.file_digest(handle,'sha256').hexdigest()
        with zipfile.ZipFile(jar) as archive:
            for name in archive.namelist():
                if '/worldgen/configured_feature/' in name and name.endswith('.json'):
                    resources[name] = (jar.name,json.loads(archive.read(name)))
    entries, providers = [], []
    for name,(jar,value) in sorted(resources.items()):
        targets = list(rules(value))
        relevant = [r for r in targets if r.get('block') in ('minecraft:stone','minecraft:deepslate')
                    or r.get('tag') in ('minecraft:stone_ore_replaceables','minecraft:deepslate_ore_replaceables','minecraft:base_stone_overworld')]
        if relevant:
            entries.append({'resource':name,'artifact':jar,'type':value.get('type'),'rules':relevant})
        states = list(host_states(value))
        if states:
            providers.append({'resource':name,'artifact':jar,'type':value.get('type'),'host_states':states})
    if not entries:
        raise ValueError('No relevant feature targets found; check the supplied resource JARs')
    return {'artifacts':artifacts,'features':entries,'configured_host_states':providers}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jars',type=Path,nargs='+',help='Resource JARs in override order')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(audit(args.jars),indent=2)+'\n')
