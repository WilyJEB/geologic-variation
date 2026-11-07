"""Pack exact analytical queries/paths; compact summary plus deterministic ZIP."""
import hashlib
import json
from pathlib import Path
import runpy
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def export():
    e=runpy.run_path(str(ROOT/'scripts/evaluate-td-axis.py'))
    data=e['export']()
    archive=ROOT/'docs/evidence/td-axis-confinement.zip'
    names=list(data['sources'])+['scripts/export-td-axis.py']
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        contents={'analytical.json':(json.dumps(data,separators=(',',':'))+'\n').encode()}
        contents.update({'sources/'+n:(ROOT/n).read_bytes() for n in names})
        for n,raw in sorted(contents.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,raw,compresslevel=9)
    return dict(diagnostic=data['diagnostic'],sources=data['sources'],summary=data['summary'],retained=data['retained'],
        archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        archive_exporter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        fresh_td_validation=False,geological_selection='abstain',gate=data['gate'])


if __name__=='__main__':
    (ROOT/'docs/evidence/td-axis-summary.json').write_text(json.dumps(export(),indent=2)+'\n')
