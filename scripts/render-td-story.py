"""Static rendering of exact frozen results; not an HTML screenshot."""
import json
from pathlib import Path
import runpy
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def render():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    import numpy as np
    S=runpy.run_path(str(ROOT/'scripts/build-td-story.py'))
    with zipfile.ZipFile(ROOT/'docs/evidence/td-story.zip') as z:
        d=json.loads(z.read('result.json'));b=json.loads(z.read('input/pr58-result.json'))
        h=json.loads(z.read('input/visual-data.json'))['elevations']
    fig,axes=plt.subplots(1,2,figsize=(14,8))
    fig.subplots_adjust(top=.82,bottom=.23,wspace=.23)
    fig.suptitle('Terrain-informed history / one retained field\nConceptual bands and events; geological interpretation abstains',fontsize=17)
    xx,zz=np.meshgrid(2688+64*np.arange(49),10880+64*np.arange(49))
    colors=['#83c9b5','#dab88b','#afa7d3','#d5a6b3']
    for n,ax in enumerate(axes):
        grid=d['ids'] if n else b['terrain_illustration_ids']
        records=d['histories'] if n else b['histories']
        for k,v in enumerate(records):
            if n:
                i=v['id'];coords=[(S['contact'](i,z,d['a']),z) for z in [10880,13953]]+[(S['contact'](i+1,z,d['a']),z) for z in [13953,10880]]
            else:
                i,j=v['id'];za=b['phases'][1]+j*2048;zb=za+2048
                zs=[za]+[r['z'] for r in b['rows'] if za<r['z']<zb]+[zb]
                left=b['phases'][0]+i*2048
                coords=[(left+S['B']['warp'](z,b['rows']),z) for z in zs]+[(left+2048+S['B']['warp'](z,b['rows']),z) for z in reversed(zs)]
            ax.add_patch(Polygon(coords,facecolor=colors[k%4],alpha=.35,edgecolor='#263b49',linestyle='--',lw=2))
            mask=np.array([[cell==([v['id']] if n else v['id']) for cell in row] for row in grid])
            label=str(v['id'])+ ('\n'+v['authored_event'].replace(' / ','\n') if n else '\n'+v['inherited']+' → '+v['overprint'])
            ax.text(max(3150,min(5300,xx[mask].mean())),zz[mask].mean(),label,ha='center',fontsize=9,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
        pts=ax.scatter(xx,zz,c=h,s=7,cmap='viridis',zorder=1)
        ax.set(xlim=(2688,5761),ylim=(13953,10880),xlabel='native x',ylabel='native z',aspect='equal',title=['Unchanged PR58 terrain illustration','One terrain-informed band history'][n])
    fig.colorbar(pts,ax=axes,shrink=.6,label='Actual retained point elevation (m)')
    fig.text(.07,.11,'2,401 observed sites. White gaps: no retained heights; geometry/error unknown.\nOriginal half-open query: x[2688,5761), z[10880,13953); 9,440,928 values unavailable.\nNew bands: 3 IDs, one sampled component each; slope clamp active.\nSurface/deep share inherited band tokens; stripping/cover and tilt are authored alternatives.',fontsize=11)
    path=ROOT/'docs/evidence/td-story.png';fig.savefig(path,dpi=150);plt.close(fig)
    manifest=dict(png_sha256=S['sha'](path.read_bytes()),result_sha256=S['sha'](S['encoded'](d)),
                  renderer_sha256=S['sha'](Path(__file__).read_bytes()),matplotlib=matplotlib.__version__,
                  numpy=np.__version__,dimensions=[2100,1200],browser_interaction_verified=False)
    (ROOT/'docs/evidence/td-story-image.json').write_bytes(S['encoded'](manifest))
    print(path)


if __name__=='__main__':render()
