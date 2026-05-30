import argparse
import ast
import json
import os
import shutil
import subprocess
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus, unquote, urlparse

import requests
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else SCRIPT_DIR
WORKSPACE = BASE_DIR
PUBLIC_DIR = BASE_DIR / 'public'
COVERS_DATA_DIR = PUBLIC_DIR / 'data' / 'covers'
COVERS_IMAGE_DIR = PUBLIC_DIR / 'images' / 'covers'
TEMP_DIR = BASE_DIR / 'temp' / 'covers'
ANALYZE_IMAGE_SCRIPT = BASE_DIR / 'inner_skills' / 'analyze_media' / 'analyze_image.py'
OUTPUT_JSON = Path(os.getenv('OUTPUT_JSON', COVERS_DATA_DIR / 'covers_candidates.json'))
SUMMARY_JSON = Path(os.getenv('SUMMARY_JSON', TEMP_DIR / 'pinterest_verify_summary.json'))
OUT_DIR = Path(os.getenv('OUT_DIR', COVERS_IMAGE_DIR))
RAW_DIR = Path(os.getenv('RAW_DIR', TEMP_DIR / 'manual'))
RUN_DATE = os.getenv('RUN_DATE', '20260528')
IMAGE_SIZE_PRIORITY = ['originals', '1200x', '736x', '564x', '474x', '236x']
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://www.pinterest.com/',
}
MIN_DOWNLOAD_SIDE = 300
DEFAULT_SCENE = 'generic_cover_template'
DEFAULT_QUERY = 'generic reusable cover template'
DEFAULT_SCENE_CN = '通用封面模板'
MATCHED_SCENE_TAGS = ['Other']
SCENE_TAGS_MAIN = [
    'Sharing Appearance Style',
    'Sharing Record',
    'Sharing Tutorial How-to',
    'Sharing Recommended Products',
    'Seeking Help / Asking Questions',
    'Socializing',
]
SCENE_TAGS_ALL = SCENE_TAGS_MAIN + ['Other']
SCENE_TAGGING_SINGLE_NOTE = '场景覆盖单一'

DEFAULT_MAX_PINS_PER_QUERY = 12
DEFAULT_MAX_INPUTS = 48




def clean_text(text: str) -> str:
    import re
    return re.sub(r'\s+', ' ', (text or '')).strip()


def scene_tagging_template():
    return {
        tag: {'match': False, 'reason': ''}
        for tag in SCENE_TAGS_MAIN
    }


def normalize_scene_tagging(raw):
    normalized = scene_tagging_template()
    if not isinstance(raw, dict):
        return normalized
    alias_map = {
        'Sharing Appearance Style': ['Sharing Appearance Style', 'appearance_style'],
        'Sharing Record': ['Sharing Record', 'sharing_record'],
        'Sharing Tutorial How-to': ['Sharing Tutorial How-to', 'tutorial_how_to', 'sharing_tutorial_how_to'],
        'Sharing Recommended Products': ['Sharing Recommended Products', 'recommended_products', 'sharing_recommended_products'],
        'Seeking Help / Asking Questions': ['Seeking Help / Asking Questions', 'seeking_help', 'asking_questions', 'seeking_help_asking_questions'],
        'Socializing': ['Socializing', 'socializing'],
    }
    for tag, aliases in alias_map.items():
        source = None
        for alias in aliases:
            if alias in raw:
                source = raw.get(alias)
                break
        if isinstance(source, dict):
            normalized[tag] = {
                'match': bool(source.get('match', False)),
                'reason': clean_text(str(source.get('reason', ''))),
            }
        elif isinstance(source, bool):
            normalized[tag] = {'match': bool(source), 'reason': ''}
    return normalized


def derive_matched_scene_tags(scene_tagging):
    normalized = normalize_scene_tagging(scene_tagging)
    matched = [tag for tag in SCENE_TAGS_MAIN if normalized.get(tag, {}).get('match')]
    matched.append('Other')
    return matched


def normalize_score_dict(raw):
    score_keys = [
        'vertical_fit',
        'photo_slot_clarity',
        'text_replaceability',
        'layout_template_quality',
        'style_distinctiveness',
        'ordinary_photo_compatibility',
        'mobile_readability',
        'generation_feasibility',
        'copyright_or_source_risk',
    ]
    normalized = {key: 0 for key in score_keys}
    if not isinstance(raw, dict):
        return normalized
    for key in score_keys:
        value = raw.get(key, 0)
        try:
            value = int(value)
        except Exception:
            value = 0
        normalized[key] = max(0, min(5, value))
    return normalized


def get_next_sequence_number(out_dir: Path, date_str: str, scene_tag: str) -> int:
    """Find the next sequence number by checking existing files in out_dir."""
    if not out_dir.exists():
        return 1
    pattern = f"CAND_{date_str}_{scene_tag}_*.png"
    existing_files = list(out_dir.glob(pattern))
    if not existing_files:
        return 1
    max_seq = 0
    for f in existing_files:
        try:
            parts = f.stem.split('_')
            if len(parts) >= 4:
                seq_str = parts[-1]
                if seq_str.isdigit():
                    max_seq = max(max_seq, int(seq_str))
        except (ValueError, IndexError):
            continue
    return max_seq + 1


def split_queries(query_text: str):
    return [clean_text(part) for part in (query_text or '').split('|') if clean_text(part)]


def normalize_pin_url(raw_url: str):
    """Normalize any Pinterest pin URL/path into canonical www.pinterest.com pin URL."""
    import re
    if not raw_url:
        return ''
    raw_url = raw_url.replace('\\u002F', '/').replace('&amp;', '&')
    raw_url = unquote(raw_url)
    match = re.search(r'(?:https?://(?:www\.)?pinterest\.[a-z.]+)?/pin/(\d{6,})/?', raw_url)
    if not match:
        return ''
    return f'https://www.pinterest.com/pin/{match.group(1)}/'


def extract_pin_urls_from_html(html: str, limit: int):
    """Extract pin URLs from browser-rendered Pinterest search HTML."""
    import re
    urls = []
    seen = set()
    patterns = [
        r'href=["\']([^"\']*/pin/\d{6,}/?[^"\']*)["\']',
        r'https?://(?:www\.)?pinterest\.[a-z.]+/pin/\d{6,}/?',
        r'/pin/\d{6,}/?',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, html):
            raw = match.group(1) if match.lastindex else match.group(0)
            pin_url = normalize_pin_url(raw)
            if not pin_url or pin_url in seen:
                continue
            seen.add(pin_url)
            urls.append(pin_url)
            if len(urls) >= limit:
                return urls
    return urls


def discover_pin_urls_with_playwright(query: str, limit: int):
    """Use Playwright only for Pinterest search URL discovery, not screenshots."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('Playwright is required for Pinterest URL discovery. Install with: pip install playwright && playwright install chromium') from exc

    search_url = f'https://www.pinterest.com/search/pins/?q={quote_plus(query)}'
    pin_urls = []
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent=REQUEST_HEADERS['User-Agent'],
            viewport={'width': 1365, 'height': 1800},
            locale='en-US',
            extra_http_headers={'Referer': REQUEST_HEADERS['Referer']},
        )
        page = context.new_page()
        try:
            page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
            try:
                page.wait_for_load_state('networkidle', timeout=20000)
            except Exception:
                pass
            for _ in range(6):
                html = page.content()
                for pin_url in extract_pin_urls_from_html(html, limit * 3):
                    if pin_url in seen:
                        continue
                    seen.add(pin_url)
                    pin_urls.append(pin_url)
                    if len(pin_urls) >= limit:
                        return pin_urls
                page.mouse.wheel(0, 1800)
                page.wait_for_timeout(1500)
        finally:
            context.close()
            browser.close()
    return pin_urls


def search_pinterest_pins(query: str, start_index: int, limit: int):
    pin_urls = discover_pin_urls_with_playwright(query, limit)
    items = []
    errors = []
    for pin_url in pin_urls:
        try:
            image_url = resolve_pin_image_url(pin_url)
        except Exception as exc:
            errors.append(f'{pin_url}: {str(exc)[:160]}')
            continue
        if not image_url:
            continue
        items.append({
            'index': start_index + len(items),
            'pin_url': pin_url,
            'image_url': image_url,
            'title': query,
            'query': query,
            'source': 'playwright_pinterest_search',
        })
        if len(items) >= limit:
            break
    if errors:
        print(f'[pin image resolve] {query}: ' + ' | '.join(errors[:3]))
    return items


def resolve_pin_image_url(pin_url: str):
    response = requests.get(pin_url, headers=REQUEST_HEADERS, timeout=45)
    response.raise_for_status()
    import re
    html = response.text
    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'https?://i\.pinimg\.com/[^"\'<>\\]+?\.(?:jpg|jpeg|png|webp)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1 if match.lastindex else 0).replace('\\u002F', '/')
    return ''


def collect_inputs_from_pinterest(query_text: str, max_pins_per_query: int, max_inputs: int):
    queries = split_queries(query_text) or [DEFAULT_QUERY]
    all_items = []
    seen_pins = set()
    errors = []
    for query in queries:
        try:
            items = search_pinterest_pins(query, len(all_items) + 1, max_pins_per_query)
        except Exception as exc:
            errors.append({'query': query, 'error': str(exc)[:300]})
            continue
        for item in items:
            if item['pin_url'] in seen_pins:
                continue
            seen_pins.add(item['pin_url'])
            item['index'] = len(all_items) + 1
            all_items.append(item)
            if len(all_items) >= max_inputs:
                return all_items, errors
    return all_items, errors


def pinterest_high_res_candidates(image_url: str):
    if not image_url:
        return []
    parsed = urlparse(image_url)
    path = parsed.path
    candidates = []
    known_parts = ['/236x/', '/474x/', '/564x/', '/736x/', '/1200x/', '/originals/']
    for size in IMAGE_SIZE_PRIORITY:
        candidate_path = path
        replaced = False
        for old in known_parts:
            if old in candidate_path:
                candidate_path = candidate_path.replace(old, f'/{size}/', 1)
                replaced = True
                break
        if not replaced:
            candidate_path = f'/{size}{candidate_path}' if not candidate_path.startswith(f'/{size}/') else candidate_path
        candidates.append(parsed._replace(path=candidate_path).geturl())
    return list(dict.fromkeys(candidates))


def download_clean_pin_image(image_url: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for candidate_url in pinterest_high_res_candidates(image_url):
        try:
            response = requests.get(candidate_url, headers=REQUEST_HEADERS, timeout=45)
            if response.status_code != 200 or not response.content:
                errors.append({'url': candidate_url, 'status': response.status_code, 'error': 'empty_or_non_200'})
                continue
            with Image.open(BytesIO(response.content)) as img:
                img = img.convert('RGB')
                width, height = img.size
                if min(width, height) < MIN_DOWNLOAD_SIDE:
                    errors.append({'url': candidate_url, 'status': response.status_code, 'error': f'image_too_small:{width}x{height}'})
                    continue
                img.save(output_path, quality=95)
                return {
                    'ok': True,
                    'path': str(output_path),
                    'resolved_url': candidate_url,
                    'width': width,
                    'height': height,
                    'attempted_urls': pinterest_high_res_candidates(image_url),
                }
        except Exception as exc:
            errors.append({'url': candidate_url, 'error': str(exc)[:200]})
    return {
        'ok': False,
        'path': str(output_path),
        'resolved_url': '',
        'width': 0,
        'height': 0,
        'attempted_urls': pinterest_high_res_candidates(image_url),
        'errors': errors,
    }


def normalize_module_observations(parsed):
    modules = parsed.get('module_observations', {}) if isinstance(parsed, dict) else {}
    if not isinstance(modules, dict):
        modules = {}
    for key in ['layout', 'style', 'background', 'color_logic', 'image_usage', 'visual_elements', 'typography_system', 'constraints', 'canvas_ratio']:
        value = modules.get(key, '')
        modules[key] = clean_text(value) if isinstance(value, str) else value

    # 跨比例适配标记
    ra = modules.get('ratio_adaptability', {})
    if not isinstance(ra, dict):
        ra = {}
    modules['ratio_adaptability'] = {
        'can_adapt_to_3_4': bool(ra.get('can_adapt_to_3_4', False)),
        'adaptation_note': clean_text(str(ra.get('adaptation_note', '')))
    }

    # 强制补全 constraints 完整性保护规则
    constraints = modules.get('constraints', '')
    required_rules = [
        "人像（identity）：不改变脸部特征、肤色、发型，身份保持稳定",
        "产品（image_integrity - product）：Logo/形状/材质完整保留，不可遮挡或重绘",
        "美食（image_integrity - food）：主体形态与可食用质感完整保留",
        "建筑/风景（image_integrity - scene）：主要结构关系不被破坏"
    ]
    missing = []
    for rule in required_rules:
        label = rule.split('（')[0]
        if label not in constraints:
            missing.append(rule)
    if missing:
        if constraints and not constraints.endswith(('。', '；', ';', '.')):
            constraints += '；'
        constraints = (constraints + ' ' + '；'.join(missing)).strip()
        modules['constraints'] = constraints

    return modules


def classify_aspect_ratio(width, height):
    if not width or not height:
        return 'unknown'
    ratio = width / height
    targets = {'9:16': 9/16, '3:4': 3/4, '1:1': 1.0}
    best = min(targets.items(), key=lambda kv: abs(ratio - kv[1]))
    return best[0] if abs(ratio - best[1]) <= 0.08 else 'unknown'


def get_image_size(path: str):
    with Image.open(path) as img:
        return img.size


def extract_balanced_json(text: str):
    marker = '"results"'
    idx = text.find(marker)
    if idx == -1:
        return None
    start = text.rfind('{', 0, idx)
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return None


def parse_vlm_output(text: str):
    text = (text or '').strip()
    candidates = []
    if text:
        candidates.append(text)
    snippet = extract_balanced_json(text)
    if snippet:
        candidates.append(snippet)
    if "AimeToolResultText(result=" in text:
        tool_idx = text.find("AimeToolResultText(result=")
        inner = text[tool_idx + len("AimeToolResultText(result="):]
        if inner.endswith(')'):
            inner = inner[:-1]
        try:
            candidates.append(str(ast.literal_eval(inner)))
        except Exception:
            import re
            match = re.search(r"AimeToolResultText\(result=(['\"])([\s\S]*)\1\)", text)
            if match:
                candidates.append(match.group(2))
    for candidate in list(candidates):
        if '```' in candidate:
            import re
            blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', candidate)
            candidates.extend(blocks)
    seen = set()
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            data = json.loads(candidate)
        except Exception:
            try:
                data = ast.literal_eval(candidate)
            except Exception:
                continue
        if hasattr(data, 'result'):
            nested = parse_vlm_output(str(getattr(data, 'result', '')))
            if nested:
                return nested
        if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list) and data['results']:
            return data['results'][0]
        if isinstance(data, list) and data:
            return data[0]
    return None


def default_vlm_result(reason='vlm_failed'):
    return {
        'accept': False,
        'has_design_layer': False,
        'has_multi_cover_units': False,
        'contains_real_photo': False,
        'reason': reason,
        'detected_text': '',
        'style_summary': '',
        'visual_clarity': 'low',
        'style_transfer_value': 'low',
        'designer_description': '',
        'reference_assessment': {
            'observations': {
                'text_image_hierarchy': '',
                'visual_focus': '',
                'style_tone': '',
                'element_density': '',
                'obvious_design_flaws': '',
            },
            'reference_value': 'low',
            'reference_reason': '',
        },
        'canvas_ratio': '',
        'background_material': '',
        'background_color_tone': '',
        'image_subject_usage': '',
        'image_slot_count': '',
        'image_slot_size_relation': '',
        'layout_structure': '',
        'layer_order': '',
        'text_system_style': '',
        'text_zone_position': '',
        'title_subtitle_hierarchy': '',
        'decoration_elements': [],
        'decoration_count_total': '',
        'style_label': [],
        'scene_classification': {},
        'scene_tagging': scene_tagging_template(),
        'score': normalize_score_dict({}),
        'total_score': 0,
        'review_decision': 'exclude',
        'module_observations': {
            'layout': '',
            'style': '',
            'background': '',
            'color_logic': '',
            'image_usage': '',
            'visual_elements': '',
            'typography_system': '',
            'constraints': '',
        },
        'raw_response_preview': '',
    }


def normalize_reference_assessment(parsed):
    assessment = parsed.get('reference_assessment', {}) if isinstance(parsed, dict) else {}
    if not isinstance(assessment, dict):
        assessment = {}
    observations = assessment.get('observations', {})
    if not isinstance(observations, dict):
        observations = {}
    normalized_observations = {
        'text_image_hierarchy': clean_text(str(observations.get('text_image_hierarchy', ''))),
        'visual_focus': clean_text(str(observations.get('visual_focus', ''))),
        'style_tone': clean_text(str(observations.get('style_tone', ''))),
        'element_density': clean_text(str(observations.get('element_density', ''))),
        'obvious_design_flaws': clean_text(str(observations.get('obvious_design_flaws', ''))),
    }
    reference_value = assessment.get('reference_value', 'low')
    if reference_value not in {'high', 'medium', 'low'}:
        reference_value = 'low'
    return {
        'observations': normalized_observations,
        'reference_value': reference_value,
        'reference_reason': clean_text(str(assessment.get('reference_reason', ''))),
    }


def analyze_single_image(image_path: str):
    prompt = (
        '你是封面模板分析器。只分析单张干净图片的模板物理规格和参考价值，输出纯 JSON，不要 markdown，不要解释。\n\n'
        '【前置步骤：设计师视角图像描述】\n'
        '- 先用 2-3 句话，以资深平面设计师视角描述这张图的设计特点和视觉表现力。\n'
        '- 描述应关注构图、层级、风格、材质、色彩、文字与图像关系，不要复述具体地名、人名、品牌名。\n'
        '- 将该描述写入 designer_description 字段。\n\n'
        '【通用模板分析原则】\n'
        '- 不假设输入内容是风景、旅行或任何固定类别；统一用 $User_Photo 或“用户图片”引用输入主体。\n'
        '- 分析重点是可复用的版式结构、图文层级、槽位关系和视觉约束，而不是图片内容类别本身。\n\n'
        '【任务1：硬性过滤判断】\n'
        '- 必须满足（硬性条件）：竖版构图（9:16 / 3:4 / 4:5）；有明确用户照片位（通常 1-4 张，教程/好物类可放宽）；有文字排版区域（主标题/副标题/标签/引言等之一）；有可迁移的版式结构（单图/图文分区/拼贴/卡片/贴纸框等）；换成普通用户素材后仍有封面感；手机缩略图下主图和主标题清晰可读。\n'
        '- 直接排除（硬性排除）：横版；无照片位；无可替换文字；纯摄影图；纯插画；纯品牌广告/电商KV；强依赖明星、IP、品牌、特定地标；普通素材难以复现的棚拍大片。\n'
        '- has_design_layer: 是否存在版式设计层（色块背景/文字排版区域/图片面板框/装饰元素层级之一）。\n'
        '- has_multi_cover_units: 是否存在≥2个重复出现的独立封面单元（多案例拼合图/系列预览卡）。此类通常直接排除。\n'
        '- contains_real_photo: 画面中是否包含真实照片（肖像、风景、建筑、静物等真实摄影内容）。纯插画、纯文字、纯色块背景不属于真实照片。\n'
        '- accept: 只有满足硬性条件且不触发硬性排除时才为 true；否则为 false。\n'
        '- visual_clarity: high / medium / low\n'
        '- style_transfer_value: high / medium / low\n\n'
        '【任务2：按优质封面抓取标准打分】\n'
        '- 必须输出 score 对象，包含 9 个字段：vertical_fit、photo_slot_clarity、text_replaceability、layout_template_quality、style_distinctiveness、ordinary_photo_compatibility、mobile_readability、generation_feasibility、copyright_or_source_risk。\n'
        '- 前 8 项各 0-5 分，满分 40；copyright_or_source_risk 也是 0-5 分，但不计入 total_score，且越低越好。\n'
        '- total_score = 前 8 项求和。\n'
        '- review_decision 只能是 pass / review / exclude。规则：total_score >= 32 且 copyright_or_source_risk <= 2 时 pass；total_score 在 24-31 或 copyright_or_source_risk = 3 时 review；total_score < 24 或 copyright_or_source_risk >= 4 时 exclude。\n\n'
        '【任务3：7 类场景标签逐一独立判断】\n'
        '- 必须输出 scene_tagging 对象，对以下 6 个主场景逐一独立判断，每类都输出 {"match": true/false, "reason": "简短说明"}：Sharing Appearance Style、Sharing Record、Sharing Tutorial How-to、Sharing Recommended Products、Seeking Help / Asking Questions、Socializing。\n'
        '- Other 不需要模型判断，后处理时自动附加。\n'
        '- 这 6 类判断必须相互独立，允许多选，不允许只给一个 primary_scene 替代。\n'
        '- scene_classification 仍可保留，但只作为中文摘要，不替代 scene_tagging。\n\n'
        '【任务4：综合参考价值判断与分模块观察】\n'
        '- 输出 reference_assessment 对象，包含 observations、reference_value、reference_reason。\n'
        '- observations 是描述性观测对象，必须包含：\n'
        '  - text_image_hierarchy: 图文层级关系是否清晰，文字与图片是否形成可复用结构\n'
        '  - visual_focus: 视觉重心位置、动线与主次关系\n'
        '  - style_tone: 整体风格调性与设计完成度\n'
        '  - element_density: 元素密度、留白、复杂度是否适合复用\n'
        '  - obvious_design_flaws: 是否有明显设计败笔，如层级混乱、低质拼贴、文字不可读、主体被严重遮挡；没有则说明“无明显设计败笔”\n'
        '- reference_value: high / medium / low。high=设计完成度高，可直接提炼结构和风格逻辑；medium=有局部参考价值但整体完成度一般；low=设计感弱，缺乏可提炼的结构或风格。\n'
        '- reference_reason: 用 1-2 句说明综合判断依据。\n'
        '- 必须输出 module_observations，包含以下模块：\n'
        '- layout: 画布比例、主视觉位置、网格/分割/叠压关系、视觉动线\n'
        '- canvas_ratio: 原始画布比例（如 9:16 / 3:4 / 1:1）\n'
        '- ratio_adaptability: 判断该模板是否可以跨比例适配到 3:4，输出为对象 {"can_adapt_to_3_4": true/false, "adaptation_note": "简短说明"}\n'
        '- style: 整体风格、情绪、年代感、设计语汇\n'
        '- background: 背景材质、纹理、空间层级\n'
        '- color_logic: 主色/辅助色/强调色，以及配色逻辑\n'
        '- image_usage: 照片槽位数量、裁切方式、边框/阴影/叠放方式\n'
        '- visual_elements: 装饰元素类型、数量、位置与作用\n'
        '- typography_system: 字体类型、标题/副标题层级、文字区位置、排版节奏\n'
        '- constraints: 复用为 AI 封面模板时必须遵守/避免的限制，禁止写入原图具体地名、人名、品牌名；必须补充不同主体类型的完整性保护规则：人像保持脸部/身份稳定，产品保持 Logo/形状/材质完整，美食保持主体形态与可食用质感，建筑/风景保持主要结构关系不被破坏\n\n'
        '【任务5：模板物理规格提取】（仅在 accept=true 时填写，否则留空字符串）\n'
        '- canvas_ratio: 画布比例\n'
        '- background_material: 纯色块/纸张纹理/渐变/照片模糊底/混合\n'
        '- background_color_tone: 背景颜色倾向的自然语言描述\n'
        '- image_subject_usage: 全屏背景/局部裁切槽位/抠图叠加/带边框槽位/混合\n'
        '- image_slot_count: 整数，仅计真实用户图片槽位\n'
        '- image_slot_size_relation: 各用户图片槽位尺寸关系描述\n'
        '- layout_structure: 上下分割/左右分割/全屏/多格/不规则叠压\n'
        '- layer_order: 从下到上描述各层叠压关系\n'
        '- text_system_style: 手写草书/粗衬线/细衬线/无衬线极简/混合\n'
        '- text_zone_position: 文字区位置描述\n'
        '- title_subtitle_hierarchy: 标题层级描述\n'
        '- decoration_elements: 装饰元素列表，格式 [{"type":"xxx","count":N}]\n'
        '- decoration_count_total: 整数\n'
        '- style_label: 视觉风格标签数组，可多选：Y2K/日系清新/法式优雅/Editorial/复古胶片/极简主义/其他\n\n'
        '【重要禁止项】normalized_prompt 与 constraints 中禁止出现原图的具体文字（地名、人名、品牌名等）。\n\n'
        '输出格式：\n'
        '{"results":[{"index":1,"accept":true,"has_design_layer":true,"has_multi_cover_units":false,"contains_real_photo":true,"visual_clarity":"high","style_transfer_value":"high","designer_description":"...","score":{"vertical_fit":5,"photo_slot_clarity":4,"text_replaceability":4,"layout_template_quality":5,"style_distinctiveness":4,"ordinary_photo_compatibility":4,"mobile_readability":4,"generation_feasibility":4,"copyright_or_source_risk":1},"total_score":34,"review_decision":"pass","reference_assessment":{"observations":{"text_image_hierarchy":"...","visual_focus":"...","style_tone":"...","element_density":"...","obvious_design_flaws":"..."},"reference_value":"high","reference_reason":"..."},"scene_classification":{"primary_scene":"观点表达&社交情绪","confidence":"high","reason":"..."},"scene_tagging":{"Sharing Appearance Style":{"match":false,"reason":"..."},"Sharing Record":{"match":false,"reason":"..."},"Sharing Tutorial How-to":{"match":false,"reason":"..."},"Sharing Recommended Products":{"match":false,"reason":"..."},"Seeking Help / Asking Questions":{"match":true,"reason":"问题式大标题和求助语气明显。"},"Socializing":{"match":false,"reason":"..."}},"module_observations":{"layout":"...","canvas_ratio":"9:16","ratio_adaptability":{"can_adapt_to_3_4":true,"adaptation_note":"..."},"style":"...","background":"...","color_logic":"...","image_usage":"...","visual_elements":"...","typography_system":"...","constraints":"..."},"canvas_ratio":"9:16","background_material":"纸张纹理","background_color_tone":"...","image_subject_usage":"带边框槽位","image_slot_count":2,"image_slot_size_relation":"...","layout_structure":"上下分割","layer_order":"...","text_system_style":"手写草书","text_zone_position":"...","title_subtitle_hierarchy":"...","decoration_elements":[{"type":"撕纸边缘","count":1}],"decoration_count_total":3,"style_label":["复古胶片","日系清新"]}]} '
        
    )
    payload = {'paths': [image_path], 'task': prompt}
    last_text = ''
    for attempt in range(3):
        proc = subprocess.run(
            ['python3', str(ANALYZE_IMAGE_SCRIPT), json.dumps(payload, ensure_ascii=False)],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
        )
        last_text = (proc.stdout or '') if proc.returncode == 0 else ((proc.stdout or '') + ' ' + (proc.stderr or ''))
        if proc.returncode == 0:
            parsed = parse_vlm_output(last_text)
            if parsed:
                result = default_vlm_result()
                result.update({
                    'accept': bool(parsed.get('accept', False)),
                    'has_design_layer': bool(parsed.get('has_design_layer', parsed.get('accept', False))),
                    'has_multi_cover_units': bool(parsed.get('has_multi_cover_units', False)),
                    'contains_real_photo': bool(parsed.get('contains_real_photo', False)),
                    'reason': clean_text(parsed.get('reason', '')),
                    'detected_text': clean_text(parsed.get('detected_text', '')),
                    'style_summary': clean_text(parsed.get('style_summary', '')),
                    'visual_clarity': parsed.get('visual_clarity', 'medium') if parsed.get('visual_clarity') in {'high', 'medium', 'low'} else 'medium',
                    'style_transfer_value': parsed.get('style_transfer_value', 'medium') if parsed.get('style_transfer_value') in {'high', 'medium', 'low'} else 'medium',
                    'designer_description': clean_text(str(parsed.get('designer_description', ''))),
                    'reference_assessment': normalize_reference_assessment(parsed),
                    'canvas_ratio': clean_text(str(parsed.get('canvas_ratio', ''))),
                    'background_material': clean_text(str(parsed.get('background_material', ''))),
                    'background_color_tone': clean_text(str(parsed.get('background_color_tone', ''))),
                    'image_subject_usage': clean_text(str(parsed.get('image_subject_usage', parsed.get('photo_usage', '')))),
                    'image_slot_count': parsed.get('image_slot_count', parsed.get('photo_panel_count', '')),
                    'image_slot_size_relation': clean_text(str(parsed.get('image_slot_size_relation', parsed.get('photo_panel_size_relation', '')))),
                    'layout_structure': clean_text(str(parsed.get('layout_structure', ''))),
                    'layer_order': clean_text(str(parsed.get('layer_order', ''))),
                    'text_system_style': clean_text(str(parsed.get('text_system_style', ''))),
                    'text_zone_position': clean_text(str(parsed.get('text_zone_position', ''))),
                    'title_subtitle_hierarchy': clean_text(str(parsed.get('title_subtitle_hierarchy', ''))),
                    'decoration_elements': parsed.get('decoration_elements', []) if isinstance(parsed.get('decoration_elements', []), list) else [],
                    'decoration_count_total': parsed.get('decoration_count_total', ''),
                    'style_label': parsed.get('style_label', []) if isinstance(parsed.get('style_label', []), list) else [],
                    'scene_classification': parsed.get('scene_classification', {}) if isinstance(parsed.get('scene_classification', {}), dict) else {},
                    'scene_tagging': normalize_scene_tagging(parsed.get('scene_tagging', {})),
                    'score': normalize_score_dict(parsed.get('score', {})),
                    'total_score': max(0, min(40, int(parsed.get('total_score', 0) or 0))),
                    'review_decision': parsed.get('review_decision', 'exclude') if parsed.get('review_decision') in {'pass', 'review', 'exclude'} else 'exclude',
                    'module_observations': normalize_module_observations(parsed),
                    'raw_response_preview': clean_text(last_text)[:500],
                })
                return result
        time.sleep(6 * (attempt + 1))
    result = default_vlm_result('vlm_parse_failed')
    result['raw_response_preview'] = clean_text(last_text)[:500]
    return result


def format_decoration_elements(elements):
    if not isinstance(elements, list) or not elements:
        return 'none'
    parts = []
    for item in elements:
        if not isinstance(item, dict):
            continue
        t = clean_text(str(item.get('type', '')))
        c = item.get('count', '')
        if t:
            parts.append(f'{t} x{c}')
    return ', '.join(parts) if parts else 'none'


def build_structured_normalized_prompt(vlm, fallback_ratio='unknown'):
    canvas_ratio = vlm.get('canvas_ratio') or fallback_ratio
    background_material = vlm.get('background_material') or '混合'
    background_color_tone = vlm.get('background_color_tone') or 'neutral light tone'
    image_subject_usage = vlm.get('image_subject_usage') or '混合'
    image_slot_count = vlm.get('image_slot_count') if vlm.get('image_slot_count') != '' else 'unknown'
    image_slot_size_relation = vlm.get('image_slot_size_relation') or 'slot size relation unspecified'
    layout_structure = vlm.get('layout_structure') or '不规则叠压'
    layer_order = vlm.get('layer_order') or 'background → photo panels → typography → decorations'
    text_system_style = vlm.get('text_system_style') or '混合'
    text_zone_position = vlm.get('text_zone_position') or 'position unspecified'
    title_subtitle_hierarchy = vlm.get('title_subtitle_hierarchy') or 'title/subtitle hierarchy unspecified'
    decoration_count_total = vlm.get('decoration_count_total') if vlm.get('decoration_count_total') != '' else 'unknown'
    decoration_desc = format_decoration_elements(vlm.get('decoration_elements', []))
    style_label = ', '.join(vlm.get('style_label', [])) if isinstance(vlm.get('style_label', []), list) and vlm.get('style_label') else '其他'
    return (
        f'A vertical {canvas_ratio} cover template. '
        f'Background: {background_material}, {background_color_tone}. '
        f'Main user image: {image_subject_usage}, {image_slot_count} slot(s), {image_slot_size_relation}. '
        f'Layout: {layout_structure}. '
        f'Layer order (bottom to top): {layer_order}. '
        f'Typography: {text_system_style}, {text_zone_position}; {title_subtitle_hierarchy}. '
        f'Decorations ({decoration_count_total} elements): {decoration_desc}. '
        f'Style: {style_label}.'
    )


def build_candidate_record(item, final_path, width, height, scene_tags=None, cand_id='candidate_001'):
    vlm = item['vlm']
    matched_scene_tags = derive_matched_scene_tags(vlm.get('scene_tagging', {}))
    public_image_url = f"/images/covers/{final_path.name}"
    risk_notes = []
    if min(width, height) < 900:
        risk_notes.append('low_resolution')
    if vlm.get('reason'):
        risk_notes.append(f"vlm_note:{vlm['reason'][:120]}")
    non_other_tags = [tag for tag in matched_scene_tags if tag != 'Other']
    if len(non_other_tags) == 1:
        risk_notes.append(SCENE_TAGGING_SINGLE_NOTE)
    score = normalize_score_dict(vlm.get('score', {}))
    total_score = sum(score[key] for key in score if key != 'copyright_or_source_risk')
    review_decision = vlm.get('review_decision', 'exclude')
    if review_decision not in {'pass', 'review', 'exclude'}:
        review_decision = 'exclude'
    return {
        'id': cand_id,
        'source': {
            'platform': 'Pinterest',
            'url': item['pin_url'],
            'source_type': 'weak_text_plus_image',
        },
        'image': {
            'url': public_image_url,
            'width': width,
            'height': height,
            'aspect_ratio': classify_aspect_ratio(width, height),
        },
        'raw_text': item['title'],
        'raw_prompt': None,
        'normalized_prompt': build_structured_normalized_prompt(vlm, classify_aspect_ratio(width, height)),
        'prompt_generation_method': 'vision_reverse_prompt',
        'matched_scene_tags': matched_scene_tags,
        'quality_notes': {
            'visual_clarity': vlm.get('visual_clarity', 'medium'),
            'prompt_completeness': 'high' if vlm.get('canvas_ratio') or vlm.get('layout_structure') else 'medium',
            'style_transfer_value': vlm.get('style_transfer_value', 'medium'),
            'reference_value': vlm.get('reference_assessment', {}).get('reference_value', 'low'),
            'reference_reason': vlm.get('reference_assessment', {}).get('reference_reason', ''),
        },
        'designer_description': vlm.get('designer_description', ''),
        'reference_assessment': vlm.get('reference_assessment', {}),
        'module_observations': vlm.get('module_observations', {}),
        'scene_classification': vlm.get('scene_classification', {}),
        'scene_tagging': normalize_scene_tagging(vlm.get('scene_tagging', {})),
        'score': score,
        'total_score': total_score,
        'review_decision': review_decision,
        'risk_notes': risk_notes,
    }


def parse_args():
    parser = argparse.ArgumentParser(description='Verify Pinterest images as reusable cover templates.')
    parser.add_argument('--scene', default=DEFAULT_SCENE, help='Generic scene/template key used in output filenames.')
    parser.add_argument('--query', default=DEFAULT_QUERY, help='External query or search intent label for summary metadata.')
    parser.add_argument('--scene-cn', default=DEFAULT_SCENE_CN, help='Chinese display name for the template scenario.')
    parser.add_argument('--matched-scene-tags', default=','.join(MATCHED_SCENE_TAGS), help='Comma-separated generic tags for accepted candidates.')
    parser.add_argument('--max-pins-per-query', type=int, default=DEFAULT_MAX_PINS_PER_QUERY, help='Max Pinterest pins to parse per query.')
    parser.add_argument('--max-inputs', type=int, default=DEFAULT_MAX_INPUTS, help='Max total Pinterest pins to verify for this scene.')
    parser.add_argument('--target-accept-count', type=int, default=4, help='Stop VLM filtering early once this many accepted candidates are collected.')
    return parser.parse_args()


def main():
    args = parse_args()
    scene = clean_text(args.scene) or DEFAULT_SCENE
    query = clean_text(args.query) or DEFAULT_QUERY
    scene_cn = clean_text(args.scene_cn) or DEFAULT_SCENE_CN
    scene_tags = [clean_text(tag) for tag in args.matched_scene_tags.split(',') if clean_text(tag)] or MATCHED_SCENE_TAGS
    target_accept_count = max(1, int(args.target_accept_count))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        'run_date': RUN_DATE,
        'query': query,
        'queries': split_queries(query),
        'scene': scene,
        'scene_cn': scene_cn,
        'target_accept_count': target_accept_count,
        'mode': 'playwright_pinterest_url_discovery_requests_cdn_download_structured_spec_compare',
        'checked': [],
        'search_errors': [],
        'discovered_input_count': 0,
        'final_candidate_count': 0,
        'stopped_early': False,
        'prompt_compare': {},
    }
    all_accepted = []
    inputs, search_errors = collect_inputs_from_pinterest(
        query,
        max(1, args.max_pins_per_query),
        max(1, args.max_inputs),
    )
    summary['search_errors'] = search_errors
    summary['discovered_input_count'] = len(inputs)

    if not inputs:
        summary['status'] = 'no_pinterest_inputs_found'
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(all_accepted, f, ensure_ascii=False, indent=2)
        with open(SUMMARY_JSON, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    for item in inputs:
        if len(all_accepted) >= target_accept_count:
            summary['stopped_early'] = True
            break

        local_input = RAW_DIR / f'{scene}_input_{item["index"]}.jpg'
        if not item.get('image_url'):
            try:
                item['image_url'] = resolve_pin_image_url(item.get('pin_url', ''))
            except Exception as exc:
                summary['checked'].append({
                    'index': item['index'],
                    'pin_url': item.get('pin_url', ''),
                    'image_url': '',
                    'status': 'fetch_failed',
                    'error': f'resolve_pin_image_url_failed:{str(exc)[:200]}',
                    'query': item.get('query', ''),
                })
                continue
        download_result = download_clean_pin_image(item.get('image_url', ''), local_input)
        if not download_result.get('ok'):
            summary['checked'].append({
                'index': item['index'],
                'pin_url': item['pin_url'],
                'image_url': item.get('image_url', ''),
                'status': 'fetch_failed',
                'error': 'download_clean_pin_image_failed',
                'download_result': download_result,
            })
            continue
        item['local_input'] = download_result['path']
        item['resolved_image_url'] = download_result['resolved_url']
        local_input = Path(download_result['path'])

        width, height = get_image_size(str(local_input))
        vlm = analyze_single_image(str(local_input))
        item['vlm'] = vlm

        reference_assessment = vlm.get('reference_assessment', {}) if isinstance(vlm.get('reference_assessment', {}), dict) else {}
        reference_value = reference_assessment.get('reference_value', 'low')
        status = 'rejected'
        rejection_reason = None
        final_path = ''
        if vlm.get('has_multi_cover_units'):
            rejection_reason = 'multi_cover_units'
        elif not vlm.get('has_design_layer'):
            rejection_reason = 'no_design_layer'
        elif not vlm.get('contains_real_photo'):
            rejection_reason = 'no_real_photo'
        elif reference_value == 'low':
            rejection_reason = 'low_reference_value'
        elif reference_value not in {'high', 'medium'}:
            rejection_reason = 'invalid_reference_value'
        elif not vlm.get('accept'):
            rejection_reason = 'vlm_rejected'
        else:
            scene_tag = scene.replace('_cover_template', '')
            seq_num = get_next_sequence_number(OUT_DIR, RUN_DATE, scene_tag)
            cand_id = f"CAND_{RUN_DATE}_{scene_tag}_{seq_num:03d}"
            final_path = OUT_DIR / f"{cand_id}.png"
            shutil.copyfile(local_input, final_path)
            accepted_record = build_candidate_record(item, final_path, width, height, scene_tags, cand_id=cand_id)
            all_accepted.append(accepted_record)
            summary['final_candidate_count'] += 1
            status = 'accepted'
            summary['prompt_compare'] = {
                'old_normalized_prompt': item.get('old_normalized_prompt', ''),
                'new_normalized_prompt': accepted_record['normalized_prompt'],
            }

        summary['checked'].append({
            'index': item['index'],
            'pin_url': item['pin_url'],
            'image_url': item['image_url'],
            'resolved_image_url': item.get('resolved_image_url', ''),
            'local_input': str(local_input),
            'final_path': str(final_path),
            'status': status,
            'width': width,
            'height': height,
            'has_design_layer': vlm.get('has_design_layer', False),
            'has_multi_cover_units': vlm.get('has_multi_cover_units', False),
            'contains_real_photo': vlm.get('contains_real_photo', False),
            'visual_clarity': vlm.get('visual_clarity', ''),
            'style_transfer_value': vlm.get('style_transfer_value', ''),
            'designer_description': vlm.get('designer_description', ''),
            'reference_assessment': reference_assessment,
            'reference_value': reference_value,
            'reference_reason': reference_assessment.get('reference_reason', ''),
            'reason': vlm.get('reason', ''),
            'canvas_ratio': vlm.get('canvas_ratio', ''),
            'background_material': vlm.get('background_material', ''),
            'background_color_tone': vlm.get('background_color_tone', ''),
            'image_subject_usage': vlm.get('image_subject_usage', ''),
            'image_slot_count': vlm.get('image_slot_count', ''),
            'image_slot_size_relation': vlm.get('image_slot_size_relation', ''),
            'layout_structure': vlm.get('layout_structure', ''),
            'layer_order': vlm.get('layer_order', ''),
            'text_system_style': vlm.get('text_system_style', ''),
            'text_zone_position': vlm.get('text_zone_position', ''),
            'title_subtitle_hierarchy': vlm.get('title_subtitle_hierarchy', ''),
            'decoration_elements': vlm.get('decoration_elements', []),
            'decoration_count_total': vlm.get('decoration_count_total', ''),
            'style_label': vlm.get('style_label', []),
            'module_observations': vlm.get('module_observations', {}),
            'scene_classification': vlm.get('scene_classification', {}),
            'raw_response_preview': vlm.get('raw_response_preview', ''),
            'rejection_reason': rejection_reason,
        })

        if len(all_accepted) >= target_accept_count:
            summary['stopped_early'] = True
            break

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_accepted, f, ensure_ascii=False, indent=2)
    with open(SUMMARY_JSON, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()