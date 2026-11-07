"""Render one retained field. Requires matplotlib==3.10.7; never queries TD."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def render(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon, Rectangle
    with zipfile.ZipFile(ROOT/'docs/evidence/td-pressure-visual.zip') as z:
        data_bytes=z.read('visual-data.json')
        d=json.loads(data_bytes)
    h=np.array(d['elevations'])
    x=d['x0']+np.arange(49)*64; y=d['z0']+np.arange(49)*64
    xx,yy=np.meshgrid(x,y)
    diff=np.array([[np.nan if v is None else v for v in row]
                   for row in d['max_four_neighbor_difference_metres']])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axes=plt.subplots(1,3,figsize=(16,8.5))
    fig.subplots_adjust(left=.055,right=.965,top=.83,bottom=.30,wspace=.50)
    fig.suptitle('Can connected geology visibly respond to this landscape?\n'
                 f'Retained development field · seed {d["seed"]} · no new TD execution',fontsize=17)
    titles=['1  Retained terrain + actual support','2  Finite-support evidence','3  CONCEPT ONLY: connected contact']
    for ax,title in zip(axes,titles):
        ax.set_title(title,fontsize=12,pad=12)
        ax.set_aspect('equal');ax.set_xlabel('native x (pixels)');ax.set_ylabel('native z (pixels)')
        ax.set_xlim(x[0]-96,x[-1]+96);ax.set_ylim(y[0]-96,y[-1]+96)
        ax.tick_params(labelsize=8);ax.ticklabel_format(style='plain',useOffset=False)
    # Every color mark is a sampled point, not a manufactured full-resolution map.
    a=axes[0].scatter(xx,yy,c=h,cmap='terrain',s=5,marker='s',vmin=h.min(),vmax=h.max())
    fig.colorbar(a,cax=axes[0].inset_axes([1.03,0,.04,1]),label='retained elevation (metres)')
    b=axes[1].scatter(xx,yy,c=diff,cmap='magma',s=5,marker='s',vmin=0,vmax=np.nanmax(diff))
    axes[1].scatter(np.r_[xx[0],xx[-1],xx[1:-1,0],xx[1:-1,-1]],
                    np.r_[yy[0],yy[-1],yy[1:-1,0],yy[1:-1,-1]],
                    c='#9b9b9b',s=5,marker='s')
    fig.colorbar(b,cax=axes[1].inset_axes([1.03,0,.04,1]),label='max |Δh| to four neighbours (metres)')
    axes[2].scatter(xx,yy,c=h,cmap='Greys',s=5,marker='s',alpha=.65)
    cx=x[24];cy=y[24]
    path=np.array(d['conceptual_contact_native_offsets'])+np.array([cx,cy])
    # Deliberately authored domains: no terrain threshold, classifier or confidence.
    left=np.vstack(([x[0],y[-1]], [x[0],y[0]], [x[-1],y[0]], path[::-1], [x[0],y[-1]]))
    axes[2].add_patch(Polygon(left,facecolor='#31aaa2',edgecolor='none',alpha=.18))
    axes[2].plot(path[:,0],path[:,1],'--',color='#b34286',lw=3)
    axes[2].text(x[3],y[10],'History A?\nInherited domain',color='#075c59',fontsize=10)
    axes[2].text(x[27],y[39],'History B?\nAdjacent domain',color='#73305d',fontsize=10)
    for ax in axes:
        ax.add_patch(Rectangle((x[0],y[0]),3073,3073,fill=False,lw=1.4,edgecolor='#202020'))
        ax.add_patch(Rectangle((x[0],y[0]),3072,3072,fill=False,hatch='///',
                              edgecolor=(.25,.25,.25,.13),lw=0))
    footers=[
        '2,401 retained points; original query = 3,073² pixels.\nBox = query support; heights in white gaps were not\nretained here. Exterior unknown; colours are elevations.',
        'Four observed neighbours, each 64 pixels away.\nGrey boundary lacks a complete stencil. No extrema\nor confidence inferred; between-point error unknown.',
        'Dashed line and tinted region are authored hypotheses.\nThey illustrate one coherent contact related by eye to\nthe relief; no geological history was recovered.'
    ]
    for ax,footer in zip(axes,footers):
        ax.text(0,-.20,footer,transform=ax.transAxes,fontsize=9,va='top',linespacing=1.5)
    fig.supxlabel('Hatching across ALL panels = geological interpretation abstains everywhere. '
                  'Sparse observations do not establish continuous geometry.\n'
                  'The intended player gain is a recognizable connected boundary; this figure is a design illustration, not gameplay acceptance.',
                  fontsize=11)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=160,metadata={'Software':'matplotlib '+matplotlib.__version__})
    plt.close(fig)
    manifest=dict(png_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        visual_data_sha256=hashlib.sha256(data_bytes).hexdigest(),
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        matplotlib=matplotlib.__version__,numpy=np.__version__,
        dimensions=[2560,1360],computed_geometry_confirmed=False,
        conceptual_annotations=True)
    output.with_name(output.stem+'-image.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);render(p.parse_args().output)
