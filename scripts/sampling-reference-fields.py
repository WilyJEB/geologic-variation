"""Known elongated morphology stress controls; no TD inference or geological truth."""
import math
from functools import lru_cache
from pathlib import Path
import runpy
import statistics

r=runpy.run_path(str(Path(__file__).with_name('runtime-acceptance.py')))


def experiment():
    # Fixed independent controls, not fitted to the TD results. Negative centers,
    # 16:1 length/width, opposite signs, and both axial orientations.
    output=[]
    for seed in (-1550453200536840819,20261103):
        for kind,sign,wx,wz in [('ridge_x',1,2048,128),('basin_z',-1,128,2048)]:
            cx,cz=-1024,-512;offset=-400 if sign==1 else 400;amplitude=1600*sign
            @lru_cache(maxsize=256)
            def axis_mean(index,center,width):
                return sum(math.exp(-((p-center)/width)**2/2) for p in range(index*256,(index+1)*256))/256
            def cell(row,col):
                return offset+amplitude*axis_mean(col,cx,wx)*axis_mean(row,cz,wz)
            def point(x,z):return offset+amplitude*math.exp(-((x-cx)/wx)**2/2-((z-cz)/wz)**2/2)
            rows=[]
            # Two-dimensional long-axis coverage, including shoulders and center.
            for along in range(-8,9,2):
                for across in (-2,-1,0,1,2):
                    x=cx+(along if wx>wz else across)*256+127
                    z=cz+(across if wx>wz else along)*256+127
                    p=r['province'](seed,1,x,z);sx=x//256*256;sz=z//256*256
                    truth=statistics.mean(point(sx+c*255//4,sz+a*255//4) for a in range(5) for c in range(5))
                    positions={'province_anchor':(p[2]//256,p[3]//256),'target':(x//256,z//256),
                               'fixed_grid_4':(x//1024*4+2,z//1024*4+2)}
                    rows.append({'x':x,'z':z,'target_tile_25_mean':truth,'policies':{
                        name:{'row':colrow[1],'col':colrow[0],'cell_mean':cell(colrow[1],colrow[0]),
                              'absolute_target_tile_error':abs(cell(colrow[1],colrow[0])-truth),
                              'sign_agrees':(cell(colrow[1],colrow[0])<0)==(truth<0)}
                        for name,colrow in positions.items()}})
            output.append({'seed':seed,'kind':kind,'center':[cx,cz],'sigma_native_pixels':[wx,wz],
                'amplitude_metres':amplitude,'datum_offset_metres':offset,'observations':rows,
                'summary':{name:{'n':len(rows),'mean_absolute_target_tile_error_metres':statistics.mean(v['policies'][name]['absolute_target_tile_error'] for v in rows),
                    'sign_agreements':sum(v['policies'][name]['sign_agrees'] for v in rows),
                    'representative_cells':len({(v['policies'][name]['row'],v['policies'][name]['col']) for v in rows})}
                    for name in positions}})
    return {'purpose':'Known elongated morphological stress controls, not TD accuracy, geology, requests or performance',
            'formula':'offset + amplitude * exp(-0.5*((x-cx)/sigma_x)^2 -0.5*((z-cz)/sigma_z)^2)',
            'fine_truth':'25 exact point values in target-containing 256-pixel tile; coarse uses complete 65536-pixel discrete cell mean',
            'cases':output}
