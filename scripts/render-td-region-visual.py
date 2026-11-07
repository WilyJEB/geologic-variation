"""Static inspection of the frozen result; no alternative design or terrain query."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def render():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon, Rectangle
    with zipfile.ZipFile(ROOT/'docs/evidence/td-region-visual.zip') as z:
        d = json.loads(z.read('result.json'))
    x = 2688+np.arange(49)*64
    zz = 10880+np.arange(49)*64
    xx, yy = np.meshgrid(x, zz)
    colors = ['#8dd0c0', '#efc588', '#b9b4dd', '#d9afa4']
    fig, axes = plt.subplots(1, 2, figsize=(14, 9))
    fig.subplots_adjust(top=.80, bottom=.29, left=.08, right=.94, wspace=.22)
    fig.suptitle('One retained field / one fixed regional comparison\n'
                 'Conceptual histories and contacts; interpretation abstains everywhere', fontsize=17)
    for panel, ax in enumerate(axes):
        w = np.array([r['displacement'] for r in d['rows']]) if panel else np.zeros(49)
        for n, h in enumerate(d['histories']):
            i, j = h['id']
            za, zb = d['phases'][1]+j*2048, d['phases'][1]+(j+1)*2048
            zs = np.array([za]+[z for z in zz if za < z < zb]+[zb])
            ws = np.interp(zs, zz, w, left=0, right=0)
            left = d['phases'][0]+i*2048
            points = np.vstack((np.column_stack((left+ws, zs)),
                                np.column_stack((left+2048+ws[::-1], zs[::-1]))))
            ax.add_patch(Polygon(points, color=colors[n], alpha=.33, lw=0))
        pts = ax.scatter(xx, yy, c=d['computed_descriptors']['elevations'], s=8,
                         cmap='viridis', vmin=-4861.288, vmax=2960.9873)
        for i in range(-1, 5):
            ax.plot(d['phases'][0]+i*2048+w, zz, '--', c='#283945', lw=2)
        for j in range(3, 9):
            ax.axhline(d['phases'][1]+j*2048, ls='--', c='#283945', lw=2)
        grid = np.array(d['terrain_illustration_ids' if panel else 'seed_only_ids'])
        for h in d['histories']:
            mask = np.all(grid == h['id'], axis=2)
            if mask.any():
                ax.text(xx[mask].mean(), yy[mask].mean(), f"{tuple(h['id'])}\n{h['inherited']} → {h['overprint']}",
                        ha='center', va='center', fontsize=11,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=.86))
        ax.add_patch(Rectangle((2688,10880),3073,3073,fill=False,hatch='///',
                              edgecolor=(.25,.3,.3,.16),lw=1))
        ax.set_xlim(2688, 5761); ax.set_ylim(13953, 10880); ax.set_aspect('equal')
        ax.set_title(['Seed-only connected layout', 'Terrain-informed contact ILLUSTRATION'][panel], pad=14)
        ax.set_xlabel('native x →'); ax.set_ylabel('native z → (down)')
        ax.ticklabel_format(useOffset=False, style='plain')
    fig.colorbar(pts, ax=axes, shrink=.72, pad=.02, label='retained point elevation (m)')
    fig.text(.08,.10,'Dots: 2,401 actual retained sites. White gaps: no portable heights. Dashed lines/tints: invented contacts/history.\n'
             'Original query [z10880,x2688,z13953,x5761): 3,073² pixels; only 49×49 values retained at spacing64.\n'
             'Hatching: geological interpretation abstains everywhere. Unknown observation error; no recovered geology.\n'
             'Both: 4 IDs, one sampled component each. Right: 149/2,401 labels changed; maximum displacement256 native pixels.\n'
             'Connectivity follows the construction; recognizability in Minecraft remains untested.',fontsize=11,linespacing=1.6)
    fig.savefig(ROOT/'docs/evidence/td-region-visual.png', dpi=150,
                metadata={'Software':'matplotlib '+matplotlib.__version__})
    plt.close(fig)
    manifest = dict(png_sha256=hashlib.sha256((ROOT/'docs/evidence/td-region-visual.png').read_bytes()).hexdigest(),
                    result_sha256=hashlib.sha256((json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()).hexdigest(),
                    renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    matplotlib=matplotlib.__version__, numpy=np.__version__, dimensions=[2100,1350],
                    same_comparison=True, browser_interaction_verified=False)
    (ROOT/'docs/evidence/td-region-visual-image.json').write_bytes((json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())


if __name__ == '__main__':
    render()
