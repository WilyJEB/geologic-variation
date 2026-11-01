"""Launch an isolated offline test client using an already installed launcher manifest.

Reads libraries/assets only. Does not read account credentials or change the source
profile. Pair only with the loopback/offline disposable acceptance server.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import uuid


def allowed(rules):
    result = not rules
    for rule in rules or []:
        system = rule.get('os', {})
        matches = (system.get('name', 'windows') == 'windows'
                   and system.get('arch', 'x86_64') in ('amd64', 'x86_64')
                   and (not system.get('version') or re.search(system['version'], platform.version())))
        # Optional launcher features are deliberately unused in this isolated client.
        if rule.get('features'):
            matches = False
        if matches:
            result = rule['action'] == 'allow'
    return result


def launch(args):
    manifest = json.loads(args.manifest.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'mods').mkdir()
    for mod in (args.addon, args.td):
        shutil.copy2(mod, args.output / 'mods' / mod.name)
    models = args.output / 'terrain-diffusion-models'
    models.mkdir()
    for model in args.models.iterdir():
        if model.is_file():
            os.link(model, models / model.name)
    native_source = args.meta / 'natives' / manifest['id']
    shutil.copytree(native_source, args.output / 'natives')
    libraries = args.meta / 'libraries'
    classpath = []
    for library in manifest['libraries']:
        if not library.get('include_in_classpath', True) or not allowed(library.get('rules')):
            continue
        artifact = library.get('downloads', {}).get('artifact')
        if not artifact:
            continue
        path = libraries / artifact['path']
        if not path.is_file():
            raise FileNotFoundError(path)
        # Reuse only bytes matching the installed launcher's pinned manifest.
        if artifact.get('sha1'):
            with path.open('rb') as handle:
                assert hashlib.file_digest(handle, 'sha1').hexdigest() == artifact['sha1'], path
        classpath.append(str(path))
    classpath.append(str(args.manifest.with_suffix('.jar')))
    offline = bytearray(hashlib.md5(b'OfflinePlayer:Dev').digest())
    offline[6] = (offline[6] & 15) | 48
    offline[8] = (offline[8] & 63) | 128
    replacements = {
        'auth_player_name': 'Dev', 'auth_uuid': str(uuid.UUID(bytes=bytes(offline))),
        'auth_access_token': '0', 'clientid': '0', 'auth_xuid': '0', 'user_type': 'legacy',
        'version_name': manifest['id'], 'version_type': 'release', 'game_directory': str(args.output),
        'assets_root': str(args.meta / 'assets'), 'assets_index_name': manifest['assetIndex']['id'],
        'natives_directory': str(args.output / 'natives'), 'library_directory': str(libraries),
        'launcher_name': 'geology-isolated-acceptance', 'launcher_version': '1',
        'classpath': os.pathsep.join(classpath), 'classpath_separator': os.pathsep,
    }
    def expand(value):
        for name, replacement in replacements.items():
            value = value.replace('${' + name + '}', replacement)
        if '${' in value:
            raise ValueError('Unresolved launcher variable: ' + value)
        return value
    def arguments(entries):
        result = []
        for entry in entries:
            if isinstance(entry, str):
                result.append(expand(entry))
            elif allowed(entry.get('rules')):
                values = entry['value']
                result.extend(expand(v) for v in (values if isinstance(values, list) else [values]))
        return result
    command = [str(args.java), '-Xms2G', '-Xmx6G'] + arguments(manifest['arguments']['jvm'])
    command += [manifest['mainClass']] + arguments(manifest['arguments']['game'])
    command += ['--quickPlayMultiplayer', '127.0.0.1:25587']
    (args.output / 'options.txt').write_text('version:3955\nguiScale:2\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\n')
    if args.check_only:
        print('Validated isolated client libraries and launcher arguments.', flush=True)
        return
    with (args.output / 'console.log').open('w') as log:
        process = subprocess.Popen(command, cwd=args.output, stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        print('Isolated packaged client PID', process.pid, flush=True)
        raise SystemExit(process.wait())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('manifest', 'meta', 'java', 'addon', 'td', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--models',type=Path,default=Path(__file__).resolve().parents[1]/'runs/server/terrain-diffusion-models')
    args = parser.parse_args()
    for name in ('manifest', 'meta', 'java', 'addon', 'td', 'output','models'):
        setattr(args, name, getattr(args, name).resolve())
    launch(args)
