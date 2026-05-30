import json
import os
import sys
import urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

JSON_PATH = Path('/Users/bytedance/AICover_2.0/public/data/meme_candidates.json')
OUT_PATH = Path('/Users/bytedance/AICover_2.0/public/overview.png')
CELL = 300
PAD_X = 24
PAD_Y = 20
TEXT_H = 54
ROW_GAP = 20
COL_GAP = 28
BG = (250, 250, 250)
CARD_BG = (255, 255, 255)
TEXT = (30, 30, 30)
MUTED = (90, 90, 90)

SOURCE_KEYS = ['reference_image', 'reference_image_url', 'source_url', 'image_url', 'meme_url', 'original_url', 'original_image_url', 'url', 'src', 'thumbnail_url']
STICKER_KEYS = ['sticker_url', 'generated_sticker_url', 'generated_url', 'output_url', 'result_url', 'sticker_image_url', 'emoji_sticker_url']
TITLE_KEYS = ['title', 'name']

def load_font(size):
    candidates = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT = load_font(18)
FONT_SMALL = load_font(15)

def pick(item, keys):
    candidates = [item]
    if isinstance(item.get('stickers'), dict):
        candidates.append(item.get('stickers'))
    for obj in candidates:
        for k in keys:
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return k, v.strip()
    return None, None

def open_image(url_or_path):
    if not url_or_path:
        return None
    try:
        if url_or_path.startswith(('http://', 'https://')):
            req = urllib.request.Request(url_or_path, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            return Image.open(BytesIO(data)).convert('RGBA')
        p = Path(url_or_path)
        if not p.is_absolute():
            candidates = [Path('/Users/bytedance/AICover_2.0/public') / p, Path('/Users/bytedance/AICover_2.0') / p, JSON_PATH.parent / p]
            p = next((c for c in candidates if c.exists()), candidates[0])
        return Image.open(p).convert('RGBA')
    except Exception as e:
        print(f'WARN image load failed: {url_or_path} | {e}', file=sys.stderr)
        return None

def fit_square(img):
    canvas = Image.new('RGBA', (CELL, CELL), (238, 238, 238, 255))
    if img is None:
        d = ImageDraw.Draw(canvas)
        msg = '图片加载失败'
        bbox = d.textbbox((0, 0), msg, font=FONT)
        d.text(((CELL-(bbox[2]-bbox[0]))/2, (CELL-(bbox[3]-bbox[1]))/2), msg, fill=(160, 60, 60), font=FONT)
        return canvas.convert('RGB')
    img.thumbnail((CELL, CELL), Image.LANCZOS)
    x = (CELL - img.width) // 2
    y = (CELL - img.height) // 2
    canvas.alpha_composite(img, (x, y))
    return canvas.convert('RGB')

def ellipsize(s, max_px, font):
    d = ImageDraw.Draw(Image.new('RGB', (1,1)))
    if d.textlength(s, font=font) <= max_px:
        return s
    suffix = '…'
    while s and d.textlength(s + suffix, font=font) > max_px:
        s = s[:-1]
    return s + suffix if s else suffix

def main():
    data = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    if isinstance(data, dict):
        for key in ['items', 'data', 'candidates', 'memes', 'results']:
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise TypeError('JSON 顶层或常见容器字段不是列表')

    completed = []
    for item in data:
        if isinstance(item, dict) and item.get('status') in ('completed', 'generated'):
            title_key, title = pick(item, TITLE_KEYS)
            src_key, src_url = pick(item, SOURCE_KEYS)
            sticker_key, sticker_url = pick(item, STICKER_KEYS)
            completed.append({
                'item': item,
                'id': item.get('id', ''),
                'title': title or '',
                'source_key': src_key,
                'source_url': src_url,
                'sticker_key': sticker_key,
                'sticker_url': sticker_url,
                'field_names': sorted(item.keys()),
            })

    print(f'completed_or_generated_count: {len(completed)}')
    for idx, row in enumerate(completed, 1):
        print(f'[{idx}] id={row["id"]} title={row["title"]}')
        print(f'    source_field={row["source_key"]} source_url={row["source_url"]}')
        print(f'    sticker_field={row["sticker_key"]} sticker_url={row["sticker_url"]}')
        print(f'    fields={row["field_names"]}')

    if not completed:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new('RGB', (900, 180), BG)
        d = ImageDraw.Draw(img)
        d.text((30, 70), '没有找到 status 为 completed 的条目', fill=TEXT, font=FONT)
        img.save(OUT_PATH)
        return

    width = PAD_X * 2 + CELL * 2 + COL_GAP
    row_h = CELL + TEXT_H + ROW_GAP
    height = PAD_Y * 2 + row_h * len(completed) - ROW_GAP
    out = Image.new('RGB', (width, height), BG)
    draw = ImageDraw.Draw(out)

    for i, row in enumerate(completed):
        y = PAD_Y + i * row_h
        draw.rounded_rectangle((PAD_X-10, y-10, width-PAD_X+10, y+CELL+TEXT_H+4), radius=14, fill=CARD_BG)
        left = fit_square(open_image(row['source_url']))
        right = fit_square(open_image(row['sticker_url']))
        out.paste(left, (PAD_X, y))
        out.paste(right, (PAD_X + CELL + COL_GAP, y))
        label = f'id: {row["id"]}   title: {row["title"]}'
        label = ellipsize(label, width - PAD_X*2 - 8, FONT)
        draw.text((PAD_X, y + CELL + 10), label, fill=TEXT, font=FONT)
        field_label = f'原图字段: {row["source_key"] or 未找到}  |  贴纸字段: {row["sticker_key"] or 未找到}'
        field_label = ellipsize(field_label, width - PAD_X*2 - 8, FONT_SMALL)
        draw.text((PAD_X, y + CELL + 34), field_label, fill=MUTED, font=FONT_SMALL)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_PATH)
    print(f'overview_saved: {OUT_PATH}')

if __name__ == '__main__':
    main()
