#!/usr/bin/env python3
import json, os, math, tempfile, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE=Path('/Users/bytedance/AICover_2.0')
DATA=BASE/'public/data/meme/meme_candidates_dev.json'
OUT=BASE/'output/collage_generated_dev_v2.png'
CELL=256
PAD=16
LABEL_H=36
BG=(245,245,245)
PLACEHOLDER=(210,210,210)

def load_items():
    data=json.loads(DATA.read_text())
    if isinstance(data, list): return data
    return data.get('items') or data.get('candidates') or []

def norm(p):
    if not p: return p
    if isinstance(p, str) and p.startswith('/images/'):
        return str(BASE/'public'/p.lstrip('/'))
    return p

def exists(p):
    p=norm(p)
    return bool(p) and os.path.exists(p)

def download(url, suffix='.img'):
    if not url: return None
    try:
        fd, path=tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r, open(path,'wb') as f:
            f.write(r.read())
        return path if os.path.getsize(path)>0 else None
    except Exception:
        return None

def candidate_path(obj, prefer_square=True):
    keys=[]
    if prefer_square: keys.append('square_image_path')
    keys += ['image_path','generated_image_path','path','local_path']
    for k in keys:
        if exists(obj.get(k)): return obj.get(k), 'local:'+k
    for k in ['image_url','generated_image_url','url','raw_gif_url','raw_image_url']:
        if obj.get(k):
            p=download(obj.get(k), '.png')
            if p and exists(p): return p, 'download:'+k
    return None, 'missing'

def open_fit(path, label=None, placeholder_text=None):
    canvas=Image.new('RGB',(CELL,CELL+LABEL_H),BG)
    draw=ImageDraw.Draw(canvas)
    path=norm(path)
    if path and exists(path):
        try:
            im=Image.open(path).convert('RGB')
            im.thumbnail((CELL,CELL), Image.LANCZOS)
            x=(CELL-im.width)//2; y=(CELL-im.height)//2
            canvas.paste(im,(x,y))
        except Exception:
            draw.rectangle([0,0,CELL,CELL], fill=PLACEHOLDER)
            draw.text((24,112),'图片读取失败', fill=(60,60,60))
    else:
        draw.rectangle([0,0,CELL,CELL], fill=PLACEHOLDER)
        draw.text((24,112), placeholder_text or '图片缺失', fill=(60,60,60))
    if label:
        draw.text((8,CELL+8), str(label)[:36], fill=(30,30,30))
    return canvas

def main():
    items=[x for x in load_items() if x.get('status')=='generated']
    missing=[]; cells=[]; total=0; filled=0; placeholders=0; downloads=0; fallback_image_path=0; rows_with_3_variants=0; rows_total=0
    for item in items:
        mid=item.get('id') or item.get('meme_id') or item.get('source_id') or 'unknown'
        fp=item.get('frame_path') or item.get('frame_png_path')
        if not exists(fp):
            missing.append((mid,'frame_path',fp))
            cells.append(open_fit(None, f'{mid} / reference', '参考图缺失'))
            placeholders += 1
        else:
            cells.append(open_fit(fp, f'{mid} / reference'))
            filled += 1
        total += 1
        variants=item.get('generated_variants') or []
        rows_total += 1
        if len(variants) >= 3:
            rows_with_3_variants += 1
        else:
            missing.append((mid,'generated_variants',f'count={len(variants)}'))
        for i in range(3):
            v=variants[i] if i < len(variants) and isinstance(variants[i], dict) else {}
            sp=v.get('square_image_path')
            if not exists(sp): missing.append((mid,f'variant[{i}].square_image_path',sp))
            p,src=candidate_path(v, prefer_square=True)
            if src == 'local:image_path': fallback_image_path += 1
            if src.startswith('download'): downloads += 1
            cells.append(open_fit(p, f'{mid} / v{i+1}', '生成图缺失'))
            total += 1
            filled += 1 if p else 0; placeholders += 0 if p else 1
    cols=4
    rows=max(1, math.ceil(len(cells)/cols))
    W=cols*CELL+(cols+1)*PAD
    H=rows*(CELL+LABEL_H)+(rows+1)*PAD
    collage=Image.new('RGB',(W,H),(255,255,255))
    for idx,cell in enumerate(cells):
        r,c=divmod(idx,cols)
        collage.paste(cell,(PAD+c*(CELL+PAD), PAD+r*(CELL+LABEL_H+PAD)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    collage.save(OUT)
    print(f'generated_items={len(items)}')
    print(f'total_cells={total}')
    print(f'filled_cells={filled}')
    print(f'placeholder_cells={placeholders}')
    print(f'downloads={downloads}')
    print(f'fallback_image_path={fallback_image_path}')
    print(f'rows_with_3_variants={rows_with_3_variants}/{rows_total}')
    print(f'success_rate={filled}/{total}={filled/total*100 if total else 0:.1f}%')
    print(f'output={OUT}')
    print('---missing_paths---')
    for row in missing:
        print('\t'.join(str(x) for x in row))
if __name__=='__main__': main()
