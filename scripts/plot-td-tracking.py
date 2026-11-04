"""Nearest-neighbor fine-point diagnostic maps; no interpolated terrain or geology."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]


def plot():
    data=json.loads((ROOT/'docs/evidence/td-tracking.json').read_text())
    cases=[c for c in data['cases'] if c['scale']==1]
    image=Image.new('RGB',(1240,2140),'white');draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    draw.text((25,15),'TD fine-point patches: bounded localization and axis tracking',fill='black',font=font)
    draw.text((25,46),'64 native-pixel samples; x right, z down; per-panel gray range. No interpolation.',fill='black',font=small)
    draw.text((25,71),'Blue: straight. Orange: localized fixed axis. Magenta: tracked; shoulders dashed.',fill='black',font=small)
    colors=dict(straight='#0077cc',localized='#ef8a00',tracked='#c00090')
    for row,c in enumerate(cases):
        for col,a in enumerate(c['attempts']):
            left=35+col*610;top=155+row*650
            values=[b['elevations'] for b in a['bands']];lo=min(v for r in values for v in r);hi=max(v for r in values for v in r)
            draw.text((left,top-46),f"{c['seed']} {a['candidate']['kind']} / {c['split']}",fill='black',font=font)
            draw.text((left,top-22),f'Fine elevations {lo:.0f} .. {hi:.0f} m; 3072 x 3072 native px',fill='black',font=small)
            for z,r in enumerate(values):
                for x,v in enumerate(r):
                    gray=int(35+200*(v-lo)/max(1,hi-lo))
                    draw.rectangle((left+x*10,top+z*10,left+x*10+9,top+z*10+9),fill=(gray,gray,gray))
            ox=a['candidate']['col']*256+128-1536;oz=a['candidate']['row']*256+128-1536
            def pos(p):return (left+(p[0]-ox)/64*10+5,top+(p[1]-oz)/64*10+5)
            for mode,color in colors.items():
                run=a['diagnosis']['runs'][mode];points=[pos(p['point']) for p in run['stations']]
                if len(points)>1:draw.line(points,fill=color,width=3)
                for p in points:draw.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=color,outline='black')
                if mode=='tracked':
                    for p in run['stations']:
                        x,z=p['point'];dx,dz=p['axis'];ends=[pos((x-dz,z+dx)),pos((x+dz,z-dx))]
                        for n in range(0,20,2):
                            q=[tuple(ends[0][i]+t/20*(ends[1][i]-ends[0][i]) for i in (0,1)) for t in (n,n+1)]
                            draw.line(q,fill=color,width=1)
            x,y=left+245,top+245
            draw.line((x-8,y,x+8,y),fill='black',width=3);draw.line((x,y-8,x,y+8),fill='black',width=3)
            t=a['diagnosis']['runs']['tracked']
            draw.text((left,top+500),f"Tracked: {'SUPPORTED' if t['supported'] else 'ABSTAIN'}; {len(t['stations'])}/5 stations",fill='black',font=font)
            reasons=t['reasons'] or ['All declared point criteria pass; mean/tile gates remain separate.']
            for i,reason in enumerate(reasons[:4]):draw.text((left,top+529+22*i),reason,fill='black',font=small)
    draw.text((25,2110),'Cross: original coarse-cell center. Geometry cannot establish geological plausibility.',fill='black',font=small)
    image.save(ROOT/'docs/evidence/td-tracking.png')


if __name__=='__main__':plot()
