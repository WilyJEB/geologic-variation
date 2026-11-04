"""Re-export retained #47--#51 evidence with original strict checks; no inference."""
import argparse
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[1]


def reexport():
    def module(name):return runpy.run_path(str(ROOT/'scripts'/name))
    def equal(name,actual):
        expected=json.loads((ROOT/'docs/evidence'/name).read_text())
        if actual!=expected:raise RuntimeError('Retained export differs: '+name)
        print('PASS strict retained re-export',name,flush=True)
    run=ROOT/'runs/acceptance'
    coarse=module('summarize-coarse-prototype.py');source=run/'coarse-prototype-2026-11-02-02'
    data=coarse['export'](source)
    data['far_cold']=coarse['cold_export'](run/'coarse-cold-2026-11-02-01')
    data['production_comparison']=coarse['production_comparison'](source,run/'anchor-candidate-2026-11-02-01/t0-new/mods/geologic-variation-0.2.2-dev.jar')
    equal('coarse-prototype-2026-11-02.json',data)
    equal('terrain-diagnostics-2026-11-03.json',module('summarize-terrain-diagnostics.py')['export'](run/'terrain-diagnostics-2026-11-03-02'))
    equal('sampling-support-2026-11-03.json',module('summarize-sampling-support.py')['export'](run/'sampling-support-2026-11-03-01'))
    # The negative exporter itself first executes and requires the unchanged rejection.
    equal('td-landforms-2026-11-03.json',module('export-negative-td-landforms.py')['export'](run/'td-landforms-2026-11-03-01'))
    print('PRESERVED FAIL: original PR51 exporter: Paired coarse drift; morphology coverage remains failed',flush=True)


if __name__=='__main__':reexport()
