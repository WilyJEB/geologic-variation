"""Unmodified historical strict exporters in an exact historical source checkout.

Collection used a temporary opt-in SamplingDiagnostic hook; final packaging
restores its historical source and uses a separate mixin. Historical exporters
also require their executed probe artifacts. Reconstruct the original checkout
without swapping live files or weakening assertions. Raw runs are read through a
junction; this script never recursively traverses/removes that junction.
"""
import argparse
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE='1c31c0ffc07ff1a2a1fe03613061eb369fec3489'


def run(output):
    output=output.resolve();assert output.is_relative_to(ROOT/'runs/acceptance')
    output.mkdir(parents=True,exist_ok=False)
    raw=subprocess.check_output(['git','archive','--format=zip',BASE],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for name in z.namelist():assert (output/name).resolve().is_relative_to(output)
        z.extractall(output)
    # Reconstruct exact Windows checkout bytes, not normalized Git blob bytes.
    for p in (output/'scripts').glob('*.py'):
        name=p.relative_to(output).as_posix()
        p.write_bytes(subprocess.check_output(['git','cat-file','--filters',BASE+':'+name],cwd=ROOT))
    quote=lambda p:"'"+str(p).replace("'","''")+"'"
    subprocess.run(['powershell','-NoProfile','-Command',
        'New-Item -ItemType Junction -Path '+quote(output/'runs')+' -Value '+quote(ROOT/'runs')+' | Out-Null'],check=True)
    old=ROOT/'runs/acceptance/td-numerics-2026-11-04-02/cpu-0/mods'
    for folder,pattern in (('build/libs','geologic-variation-*.jar'),('build/runtime-probe','geology-runtime-probe-*.jar')):
        target=output/folder;target.mkdir(parents=True,exist_ok=True)
        files=list(old.glob(pattern));assert len(files)==1;shutil.copy2(files[0],target/files[0].name)
    def module(name):return runpy.run_path(str(output/'scripts'/name))
    def equal(name,actual):
        assert json.loads(json.dumps(actual))==json.loads((output/'docs/evidence'/name).read_text()),name
        print('PASS strict historical re-export',name,flush=True)
    module('reexport-retained-terrain.py')['reexport']()
    equal('td-tracking-negative.json',module('export-negative-td-tracking.py')['export'](ROOT/'runs/acceptance/td-tracking-2026-11-04-04'))
    print('PRESERVED FAIL: PR52 Actual matching native support changed',flush=True)
    numerical=module('export-td-numerics.py')
    # Keep the archive outside the reconstructed committed evidence.
    actual=numerical['export'](ROOT/'runs/acceptance/td-numerics-2026-11-04-02',output/'reexport-numerics.zip')
    equal('td-numerics.json',actual)
    equal('td-geometry-arc.json',module('calibrate-td-geometry.py')['export']())
    equal('td-geometry-sensitivity.json',module('audit-td-geometry-sensitivity.py')['export']())
    (output/'strict-reexport.json').write_text(json.dumps(dict(base=BASE,passed=True,
        current_checkout=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        unchanged_assertions=True,failed_pr51_pr52_assertions_preserved=True),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);run(p.parse_args().output)
