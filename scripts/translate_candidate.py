import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
PUBLIC_DIR = BASE_DIR / "public"
COVERS_DATA_DIR = PUBLIC_DIR / "data" / "covers"

SCENE = os.getenv("SCENE", "covers")
SCENE_DIR = Path(os.getenv("SCENE_DIR", COVERS_DATA_DIR))
INPUT_CANDIDATES = Path(os.getenv("INPUT_CANDIDATES", COVERS_DATA_DIR / "covers_candidates.json"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", COVERS_DATA_DIR / "templates"))
OUTPUT_SUMMARY = Path(os.getenv("OUTPUT_SUMMARY", COVERS_DATA_DIR / "templates_output.json"))

SECTION_LABELS = [
    "Background",
    "Main user image",
    "Layout",
    "Layer order",
    "Typography",
    "Decorations",
    "Style",
]

SECTION_PATTERNS = {
    "Background": r"Background:\s*",
    "Main user image": r"Main user image:\s*",
    "Layout": r"Layout:\s*",
    "Layer order": r"Layer order:\s*",
    "Typography": r"Typography:\s*",
    "Decorations": r"Decorations(?:\s*\([^)]*\))?:\s*",
    "Style": r"Style:\s*",
}

PHRASE_MAP = {
    "$User_Photo": "the input photo",
    "从下至上": "from bottom to top",
    "全屏背景": "full-bleed background",
    "全屏用户图片层": "full-bleed photo layer",
    "局部暗化蒙版层": "localized dark mask layer",
    "红色装饰线与图标层": "red accent line and icon layer",
    "文字排版层": "text layout layer",
    "左上角Logo层": "top-left logo layer",
    "画面左侧": "left-side area",
    "左下角": "bottom-left area",
    "右下方": "lower-right area",
    "右上方偏中": "upper-right quote area",
    "左侧边缘": "left edge",
    "顶部分类标签": "top category label",
    "红底白字": "white text on a red label",
    "主标题": "main title",
    "副标题": "sub title",
    "正文说明": "body copy",
    "特大号粗体": "extra-large bold",
    "中号常规体": "medium regular",
    "无衬线极简": "minimal sans-serif",
    "全屏叠压": "full-bleed overlay",
    "不规则叠压": "irregular overlay",
    "左右分割": "left-right split",
    "上下分割": "top-bottom split",
    "居中全屏": "centered hero layout",
    "照片模糊底/混合": "blurred photo blend",
    "黑白灰无彩色": "monochrome black-white-gray",
    "底部偏暗": "darker at the bottom",
    "混合": "mixed",
    "灰蓝色调渐变": "gray-blue gradient",
    "模糊背景层全屏放大铺满": "a blurred background layer enlarged to fill the canvas",
    "前景抠图层占据画面约60%居中偏下": "a foreground cut-out subject covering about sixty percent of the canvas, centered slightly low",
    "纯色背景": "solid-color background",
    "模糊人像暗纹": "blurred portrait texture",
    "左上卷边效果": "top-left page-curl effect",
    "左侧上半部实心大字": "solid oversized type in the upper-left",
    "居中人物抠图主体": "centered cut-out portrait",
    "左侧下半部线框大字": "outline oversized type in the lower-left",
    "右侧引言文字及背景色块": "right-side quote block with a highlight panel",
    "底部Logo及说明文字": "bottom logo and supporting copy",
    "装饰性标题": "decorative headline",
    "核心引文": "core quote",
    "引文普通部分": "supporting quote copy",
    "署名信息": "attribution line",
    "页面卷边效果": "page-curl effect",
    "引号图标": "quote icon",
    "文字高亮底色块": "text highlight block",
    "纸张纹理": "paper texture",
    "浅灰白色": "light off-white",
    "抠图叠加": "cut-out overlay",
    "单图": "single image",
    "占据右半幅画面并延伸至底部": "occupying the right half and extending to the bottom edge",
    "浅色纹理背景": "light textured background",
    "右侧亮色圆形色块": "bright circular color block on the right",
    "引言文本及大号引号": "quote copy with oversized quotation marks",
    "画面左侧垂直居中区域": "vertically centered area on the left",
    "引导符号": "introductory quote mark",
    "核心观点": "core statement",
    "来源/署名": "source or attribution",
    "双色大写粗体": "two-tone uppercase bold",
    "常规无衬线细体": "regular lightweight sans-serif",
    "大号双引号": "oversized quotation marks",
    "纯色正圆形色块": "solid circular color block",
    "纯色块": "solid color field",
    "浅灰中性底色": "light neutral gray base",
    "带边框槽位": "framed panel",
    "上下等大": "two equally sized panels",
    "底层浅灰背景边框": "light-gray outer frame",
    "中层上下两个等大的图片槽位": "two equal image panels stacked vertically",
    "顶层左侧文字区与右侧UI投票贴纸": "left text block with a right-side poll widget",
    "画面左侧，垂直居中跨越上下图片分割线": "left side, vertically centered across the split line",
    "单一主标题分三行排版": "a single headline arranged in three lines",
    "UI互动投票贴纸": "interactive poll widget",
    "复古胶片": "vintage film",
    "极简主义": "minimalist",
    "现代商业": "modern commercial",
    "其他": "other",
    "现代": "modern",
    "商务": "business",
    "杂志风": "magazine-style",
    "Editorial": "editorial",
    "全大写": "all caps",
    "局部": "localized",
    "标签": "label",
    "线框": "outline",
    "大字": "oversized type",
    "居中": "centered",
    "左侧": "left-side",
    "右侧": "right-side",
    "顶部": "top",
    "底部": "bottom",
    "全屏": "full-bleed",
    "主体": "subject",
    "人像": "portrait",
    "抠图": "cut-out",
    "留白": "negative space",
    "装饰": "decorative",
    "色块": "color block",
    "线条": "lines",
    "图标": "icon",
    "引导线": "guide line",
    "垂直分割/引导线": "vertical guide line",
    "矩形色块标签": "rectangular label block",
    "圆形角标Logo": "circular corner logo",
    "双引号": "quotation marks",
    "大号": "large-size",
    "小号": "small-size",
    "粗体": "bold",
    "常规体": "regular",
    "渐变": "gradient",
    "卷边": "curled corner",
    "高亮": "highlight",
    "纸质": "paper-like",
    "颗粒": "grain",
    "纯白": "pure white",
    "纯红": "pure red",
    "黑白": "black and white",
    "灰度": "grayscale",
}

GENERIC_PROHIBITED_ELEMENTS = [
    "watermarks",
    "platform logos",
    "QR codes",
    "unreadable micro text",
    "third-party brand marks",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))



def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")



def first_non_empty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""



def extract_numeric_suffix(value: str) -> str:
    match = re.search(r"(\d+)$", value or "")
    return match.group(1).zfill(3) if match else "000"



def template_name(candidate_id: str) -> str:
    return f"candidates_{extract_numeric_suffix(candidate_id)}"



def cleanup_text(text: str) -> str:
    text = (text or "").replace("\u00a0", " ")
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("，", ", ").replace("。", ". ")
    text = text.replace("；", "; ").replace("：", ": ")
    text = text.replace("、", ", ").replace("“", '"').replace("”", '"')
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .;")



def is_meaningful_text(text: str) -> bool:
    words = re.findall(r"[A-Za-z]{3,}", text or "")
    return len(words) >= 3



def normalize_punctuation(text: str) -> str:
    text = re.sub(r"\(\s*\)", "", text or "")
    text = re.sub(r"\s*([,:;])\s*", r"\1 ", text)
    text = re.sub(r"\s*\.\s*", ". ", text)
    text = re.sub(r"(^|\s)[,:;.-]+(?=\s|$)", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip(" ,:;.-")



def translate_fragment(text: str) -> str:
    result = cleanup_text(text)
    for src in sorted(PHRASE_MAP, key=len, reverse=True):
        result = result.replace(src, PHRASE_MAP[src])
    result = re.sub(r"\s*->\s*", " -> ", result)
    result = re.sub(r"\s*,\s*", ", ", result)
    result = re.sub(r"\s*;\s*", "; ", result)
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r"[\u4e00-\u9fff]+", " ", result)
    result = normalize_punctuation(result)
    if result:
        result = result[0].upper() + result[1:]
    return result



def extract_prompt_sections(prompt: str) -> Dict[str, str]:
    prompt = prompt or ""
    located_sections: List[tuple[str, int, int]] = []
    for label in SECTION_LABELS:
        match = re.search(SECTION_PATTERNS[label], prompt, flags=re.IGNORECASE)
        if match:
            located_sections.append((label, match.start(), match.end()))
    located_sections.sort(key=lambda item: item[1])

    sections: Dict[str, str] = {}
    for index, (label, _start, content_start) in enumerate(located_sections):
        next_start = located_sections[index + 1][1] if index + 1 < len(located_sections) else len(prompt)
        value = cleanup_text(prompt[content_start:next_start])
        sections[label] = value.rstrip(".")
    return sections



def infer_canvas_ratio(item: Dict[str, Any], prompt: str) -> str:
    if isinstance(item.get("image"), dict) and item["image"].get("aspect_ratio"):
        return str(item["image"]["aspect_ratio"])
    module_ratio = item.get("module_observations", {}).get("canvas_ratio")
    if module_ratio:
        return str(module_ratio)
    match = re.search(r"vertical\s+([0-9]+:[0-9]+)", prompt or "", flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return "9:16"



def infer_layout_type(layout_text: str, image_text: str, decorations_text: str) -> str:
    merged = f"{layout_text} {image_text} {decorations_text}".lower()
    if any(token in merged for token in ["left-right split", "left right split", "right half", "left-side", "right-side"]):
        return "asymmetric split"
    if any(token in merged for token in ["top-bottom split", "stacked vertically", "upper and lower", "two equally sized panels"]):
        return "stacked split"
    if any(token in merged for token in ["clipboard", "centered hero", "centered enclosed", "central panel", "wrapped around"]):
        return "centered container"
    if any(token in merged for token in ["irregular overlay", "page-curl", "outline oversized type", "solid oversized type"]):
        return "irregular layered overlay"
    if any(token in merged for token in ["collage", "halftone", "cut-out overlay"]):
        return "collage composition"
    return "full-bleed editorial"



def parse_panel_count(image_text: str) -> int:
    match = re.search(r"(\d+)\s*slot\(s\)", image_text or "", flags=re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)))
    if "two equally sized panels" in (image_text or "").lower():
        return 2
    return 1



def infer_panel_strategy(layout_type: str, image_text: str) -> str:
    merged = f"{layout_type} {image_text}".lower()
    if any(token in merged for token in ["same input photo", "background layer", "cut-out subject", "reused", "blurred background layer"]):
        return "match_input_images"
    if any(token in merged for token in ["two equally sized panels", "split", "grid", "panel", "stacked"]):
        return "fixed_matrix"
    return "single_focus"



def infer_title_flags(typography_text: str, raw_text: str, module_text: str) -> Dict[str, bool]:
    merged = " ".join([typography_text or "", raw_text or "", module_text or ""]).lower()
    has_main_title = any(
        token in merged
        for token in [
            "main title",
            "headline",
            "core statement",
            "core quote",
            "single headline",
            "quotation",
            "quote",
            "title",
            "主标题",
        ]
    )
    has_sub_title = any(
        token in merged
        for token in [
            "sub title",
            "body copy",
            "supporting copy",
            "description",
            "body",
            "attribution",
            "source",
            "supporting quote",
            "副标题",
            "说明",
        ]
    )
    if not has_main_title and (typography_text or module_text):
        has_main_title = True
    return {
        "has_main_title": has_main_title,
        "has_sub_title": has_sub_title,
    }



def build_regions(layout_type: str, panel_count: int, has_main_title: bool, has_sub_title: bool, canvas_ratio: str) -> Dict[str, str]:
    if layout_type == "asymmetric split":
        regions = {
            "region_1": "Primary text or quote zone aligned to one side of the canvas.",
            "region_2": "Main portrait or graphic zone on the opposite side.",
            "region_3": "Accent-shape or footer-detail area supporting the split composition.",
        }
    elif layout_type == "stacked split":
        regions = {
            "region_1": "Upper panel for the first image or scenario block.",
            "region_2": "Lower panel for the second image or contrast block.",
            "region_3": "Overlay title and widget band crossing or anchoring the split line.",
        }
    elif layout_type == "centered container":
        regions = {
            "region_1": "Central board or card that carries the main content.",
            "region_2": "Surrounding decoration field framing the central board.",
            "region_3": "Micro-copy or accent zone near the edges of the main container.",
        }
    elif layout_type == "irregular layered overlay":
        regions = {
            "region_1": "Main subject layer placed near the visual center.",
            "region_2": "Oversized type layer used as a structural backdrop.",
            "region_3": "Quote block or supporting-copy zone kept in a protected reading area.",
        }
    elif layout_type == "collage composition":
        regions = {
            "region_1": "Main content panel or hero-image field near the center.",
            "region_2": "Peripheral collage-element ring used for framing and motion.",
            "region_3": "Reserved headline or callout area with controlled overlap.",
        }
    else:
        regions = {
            "region_1": "Full-bleed image or texture layer covering the entire canvas.",
            "region_2": "Protected headline zone anchored to a readable low-noise area.",
            "region_3": "Accent cluster for labels, lines, icons, or logo details.",
        }
    if panel_count > 1 and "region_4" not in regions:
        regions["region_4"] = "Secondary panel or duplicate-image treatment area used by the multi-panel structure."
    if not has_sub_title:
        regions.pop("region_4", None)
    return regions



def build_layout(layout_type: str, canvas_ratio: str, layout_text: str, layer_text: str, panel_count: int, title_flags: Dict[str, bool]) -> Dict[str, Any]:
    description = translate_fragment(layout_text) or f"A {layout_type} layout adapted to a {canvas_ratio} vertical canvas."
    layer_summary = translate_fragment(layer_text)
    invariants = [
        "Preserve the primary reading order between subject, headline, and accent elements.",
        "Keep the protected text area readable after image replacement or ratio adaptation.",
    ]
    if panel_count > 1:
        invariants.append("Keep the panel count and panel relationship stable when reusing the template.")
    if "split" in layout_type:
        invariants.append("Maintain the split balance instead of letting one side visually collapse.")
    if "overlay" in layout_type:
        invariants.append("Keep the subject-layer overlap hierarchy intact.")
    flow = layer_summary or "The eye lands on the dominant visual anchor first, then moves to the headline, then to the supporting details."
    return {
        "type": layout_type,
        "description": description,
        "geometry": {
            "canvas_ratio": canvas_ratio,
            "regions": build_regions(layout_type, panel_count, title_flags["has_main_title"], title_flags["has_sub_title"], canvas_ratio),
            "safe_margins": "Keep enough breathing room around the outer edges for mobile-safe cropping and UI overlays.",
            "overlap_rules": "Allow only purposeful overlap between subject, oversized type, and accent elements; never block the main facial area or the protected text zone.",
        },
        "flow": flow,
        "invariants": invariants,
    }



def build_style(style_text: str, layout_type: str) -> Dict[str, Any]:
    translated = translate_fragment(style_text)
    lowered = (translated or "").lower()
    if "editorial" in lowered:
        name = "Editorial"
    elif "business" in lowered:
        name = "Modern Business"
    elif "minimal" in lowered:
        name = "Minimalist"
    elif "collage" in lowered:
        name = "Collage"
    else:
        name = "Structured Cover"
    description = translated or f"A {layout_type} cover system with a clear hierarchy and reusable visual rhythm."
    signatures = []
    if "editorial" in lowered:
        signatures.append("Magazine-like hierarchy with strong headline control")
    if "minimal" in lowered:
        signatures.append("Reduced visual noise and deliberate negative space")
    if "business" in lowered:
        signatures.append("Professional contrast and disciplined graphic alignment")
    if "vintage" in lowered or "film" in lowered:
        signatures.append("Retro texture or analog-style finishing details")
    if not signatures:
        signatures = [
            "Reusable cover structure with a clear subject-first hierarchy",
            "Graphic accents support the title without overwhelming the main image",
        ]
    mood = "confident and expressive"
    if "minimal" in lowered:
        mood = "clean and restrained"
    elif "business" in lowered:
        mood = "professional and credible"
    elif "collage" in lowered or "vintage" in lowered:
        mood = "bold and playful"
    return {
        "name": name,
        "description": description,
        "visual_signature": signatures,
        "mood": mood,
    }



def build_background(background_text: str, color_logic_text: str, layout_type: str) -> Dict[str, Any]:
    translated_bg = translate_fragment(background_text)
    translated_color = translate_fragment(color_logic_text)
    lowered = f"{translated_bg} {translated_color}".lower()
    texture = None
    effects = None
    if any(token in lowered for token in ["paper", "grain", "texture"]):
        texture = "Allow subtle paper, grain, or print-like texture when it supports the original tone."
    if any(token in lowered for token in ["gradient", "blur", "mask", "curl"]):
        effects = "Use gradient, blur, or soft masking only to improve hierarchy and readability."
    palette_logic = translated_color if is_meaningful_text(translated_color) else "Keep the background palette quieter than the subject and use accent color only for structured emphasis."
    base = translated_bg if is_meaningful_text(translated_bg) else f"Background treatment that supports the {layout_type} composition without weakening the reading path."
    return {
        "base": base,
        "texture": texture,
        "effects": effects,
        "palette_logic": palette_logic,
        "integrity_rule": "Do not let background texture, blur, or pattern compete with the protected title area.",
        "constraints": "Avoid noisy imagery, harsh clipping, or background detail that makes the cover hard to read on mobile.",
    }



def build_color_logic(color_logic_text: str, background_text: str) -> Dict[str, Any]:
    translated = translate_fragment(color_logic_text)
    lowered = f"{translated} {translate_fragment(background_text)}".lower()
    if "monochrome" in lowered or "black-white-gray" in lowered:
        strategy = "monochrome_base_with_single_accent"
        accent = "Introduce one accent color only when it is already part of the template language."
    elif "blue" in lowered or "red" in lowered or "yellow" in lowered:
        strategy = "neutral_base_plus_accent"
        accent = "Use one or two accent colors taken from the reference composition for labels, lines, or emphasis blocks."
    else:
        strategy = "reference_palette_extraction"
        accent = "Extract restrained accent colors from the reference and keep them secondary to readability."
    description = translated if is_meaningful_text(translated) else "Build color contrast from the reference so the headline, subject, and supporting accents remain clearly separated."
    return {
        "strategy": strategy,
        "description": description,
        "rules": {
            "background_base_color": "Start from the dominant low-noise background tone and keep it stable across adaptations.",
            "text_contrast_color": "Use a high-contrast text color that stays readable against the protected text zone.",
            "accent_colors": accent,
        },
    }



def build_image_usage(image_text: str, layout_type: str, panel_count: int) -> Dict[str, Any]:
    translated = translate_fragment(image_text)
    strategy = infer_panel_strategy(layout_type, translated)
    lowered = translated.lower()
    allow_duplication = strategy == "match_input_images" or any(token in lowered for token in ["same input photo", "background layer", "blurred", "duplicate"])
    max_usage_per_input_image = 2 if allow_duplication else 1
    layout_mapping: Dict[str, str] = {}
    if strategy == "fixed_matrix" and panel_count > 1:
        for index in range(1, panel_count + 1):
            layout_mapping[f"input_image_{index}"] = f"Map to panel region {index}."
    elif strategy == "match_input_images":
        layout_mapping["input_image_1"] = "Map to the hero-subject region and, when needed, to one secondary treated layer such as a blurred or enlarged background version."
    else:
        layout_mapping["input_image_1"] = "Map to the main focus region of the template."
    return {
        "panel_count_strategy": strategy,
        "fixed_panel_count": panel_count,
        "allow_panel_duplication": allow_duplication,
        "max_usage_per_input_image": max_usage_per_input_image,
        "layout_mapping": layout_mapping,
        "adaptation_rule": translated or "Scale and crop with subject-first logic, preserving the most important facial or object features.",
        "integrity_rule": "Allow cropping, masking, and tonal adaptation, but do not invent new body parts, distort the subject, or alter the authentic structure of the image.",
    }



def extract_visual_tokens(*texts: str) -> List[str]:
    merged = ", ".join(filter(None, texts))
    translated = translate_fragment(merged).lower()
    candidate_tokens = [token.strip(" .") for token in re.split(r"[,;/]| x\d+|->", translated) if token.strip()]
    seen = set()
    ordered: List[str] = []
    for token in candidate_tokens:
        if token not in seen:
            ordered.append(token)
            seen.add(token)
    return ordered



def classify_visual_elements(tokens: List[str]) -> Dict[str, Any]:
    stickers: List[str] = []
    doodles: List[str] = []
    ui_widgets: List[str] = []
    decorations: List[str] = []
    for token in tokens:
        if any(key in token for key in ["poll", "ui", "widget", "button", "sticker option"]):
            ui_widgets.append(token)
        elif any(key in token for key in ["doodle", "hand-drawn", "lightning", "wave", "sketch"]):
            doodles.append(token)
        elif any(key in token for key in ["label", "badge", "tag", "tape", "sticker"]):
            stickers.append(token)
        elif any(key in token for key in ["quote", "logo", "line", "icon", "border", "frame", "circle", "block", "curl", "clip", "halftone", "magnifier", "shadow"]):
            decorations.append(token)
    return {
        "stickers": [value for value in stickers if value],
        "doodles": [value for value in doodles if value] or None,
        "ui_widgets": [value for value in ui_widgets if value],
        "decorations": [value for value in decorations if value],
    }



def build_typography(typography_text: str, title_flags: Dict[str, bool], layout_type: str) -> Dict[str, Any]:
    translated = translate_fragment(typography_text)
    lowered = translated.lower()
    font_logic = translated if is_meaningful_text(translated) else "Use a clear headline-first type system with strong hierarchy and mobile readability."
    main_position = "Place the main title in the highest-attention zone that does not damage the subject silhouette."
    sub_position = "Place the sub title near the main title as a supporting block, or keep it in a lighter secondary information strip."
    if "left" in lowered:
        main_position = "Anchor the main title to the left-side reading zone with consistent alignment."
        sub_position = "Keep the sub title near the left-side title stack or in a nearby footer block."
    elif "bottom-left" in lowered:
        main_position = "Anchor the main title to the protected bottom-left reading area."
        sub_position = "Keep the sub title directly below or above the main title inside the same protected block."
    elif "center" in lowered:
        main_position = "Place the main title near the center or central-card zone while protecting the subject focus."
        sub_position = "Place the sub title around the central composition as supporting copy with lower weight."
    main_style = "Use the strongest size and weight contrast in the system for the headline."
    sub_style = "Use a lighter size, weight, or density than the main title while keeping alignment consistent."
    if "all caps" in lowered:
        main_style = "Use a bold all-caps or strongly emphasized headline treatment that matches the reference rhythm."
    return {
        "global_rules": {
            "font_logic": font_logic,
            "language_rule": "All template descriptions and placeholder logic must stay in English unless a multilingual template is explicitly required by input.",
            "readability_rule": "Keep headline and supporting copy readable at mobile cover size with strong contrast and controlled line length.",
        },
        "main_title": {
            "text": "{main_title}",
            "position": main_position,
            "style": main_style,
            "constraints": "Do not let the main title cover eyes, key product marks, or the most important subject silhouette.",
        },
        "sub_title": {
            "text": "{sub_title}",
            "position": sub_position,
            "style": sub_style,
            "constraints": "If the reference has a weak or optional sub-title system, keep this area compact and secondary rather than forcing long copy.",
        },
        "tag_label": None,
        "other_text_blocks": [],
    }



def build_constraints(constraints_text: str, layout_type: str, style_name: str) -> Dict[str, Any]:
    translated = translate_fragment(constraints_text)
    composition = "Preserve the structural relationship between subject, title area, panels, and accent anchors when adapting the template."
    if "split" in layout_type:
        composition = "Preserve the split geometry, the balance between the two sides or panels, and the protected reading area."
    elif "overlay" in layout_type:
        composition = "Preserve the front-back layer order and keep intentional overlap readable and believable."
    elif "container" in layout_type:
        composition = "Preserve the central container and keep surrounding collage or framing elements from invading the core content zone."
    image_integrity = (
        "Protect image authenticity: allow cropping, masking, layout fitting, and color adaptation, but do not invent anatomy, distort the main subject, or redraw real-world structures in a misleading way."
    )
    identity = (
        "For portraits, keep facial structure, skin tone logic, hairstyle silhouette, and recognizability stable; do not bind the template to a specific celebrity or public figure."
    )
    rendering = f"Maintain the {style_name.lower()} finish as a high-quality cover treatment; avoid cheap collage artifacts, muddy edges, low-resolution output, or random decorative clutter."
    if not translated:
        translated = "Keep protected text space readable, preserve subject integrity, and maintain the reference hierarchy during adaptation."
    return {
        "identity": identity,
        "image_integrity": image_integrity,
        "language": "Keep copy in a clean English character set by default, avoid garbled characters, and do not copy literal text seen in the reference image into the template spec.",
        "composition": composition,
        "rendering": rendering,
        "prohibited_elements": GENERIC_PROHIBITED_ELEMENTS,
    }



def build_description(scene_tags: List[str], style_name: str, layout_type: str, image_usage: Dict[str, Any], visual_elements: Dict[str, Any]) -> str:
    usable_scene_tags = [tag for tag in scene_tags if tag != "Other"]
    scene_phrase = ", ".join(usable_scene_tags[:2]) if usable_scene_tags else "cover reuse"
    panel_phrase = "single-image focus"
    if image_usage["panel_count_strategy"] == "fixed_matrix":
        panel_phrase = f"{image_usage['fixed_panel_count']}-panel composition"
    elif image_usage["panel_count_strategy"] == "match_input_images":
        panel_phrase = "reused-input layered image treatment"
    decoration_count = len(visual_elements["stickers"]) + len(visual_elements["ui_widgets"]) + len(visual_elements["decorations"]) + (len(visual_elements["doodles"]) if visual_elements["doodles"] else 0)
    decoration_phrase = "with restrained accents"
    if decoration_count >= 3:
        decoration_phrase = "with explicit decorative anchors"
    return (
        f"A reusable {style_name.lower()} cover template for {scene_phrase} content. "
        f"It uses a {layout_type} structure with a {panel_phrase} and {decoration_phrase}."
    )



def translate_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    prompt_text = first_non_empty(
        item.get("prompt"),
        item.get("normalized_prompt"),
        item.get("raw_prompt"),
        item.get("raw_text"),
    )
    prompt_sections = extract_prompt_sections(prompt_text)
    layout_text = prompt_sections.get("Layout", item.get("module_observations", {}).get("layout", ""))
    layer_text = prompt_sections.get("Layer order", "")
    background_text = prompt_sections.get("Background", item.get("module_observations", {}).get("background", ""))
    image_text = prompt_sections.get("Main user image", item.get("module_observations", {}).get("image_usage", ""))
    typography_text = prompt_sections.get("Typography", item.get("module_observations", {}).get("typography_system", ""))
    decorations_text = prompt_sections.get("Decorations", item.get("module_observations", {}).get("visual_elements", ""))
    style_text = prompt_sections.get("Style", item.get("module_observations", {}).get("style", ""))
    color_logic_text = item.get("module_observations", {}).get("color_logic", "") or background_text
    constraints_text = item.get("module_observations", {}).get("constraints", "")

    candidate_name = template_name(str(item.get("id", "")))
    scene_tags = item.get("matched_scene_tags", []) or []
    canvas_ratio = infer_canvas_ratio(item, prompt_text)
    title_flags = infer_title_flags(typography_text, item.get("raw_text", ""), item.get("module_observations", {}).get("typography_system", ""))
    layout_type = infer_layout_type(translate_fragment(layout_text), translate_fragment(image_text), translate_fragment(decorations_text))
    panel_count = parse_panel_count(translate_fragment(image_text))
    layout = build_layout(layout_type, canvas_ratio, layout_text, layer_text, panel_count, title_flags)
    style = build_style(style_text, layout_type)
    background = build_background(background_text, color_logic_text, layout_type)
    color_logic = build_color_logic(color_logic_text, background_text)
    image_usage = build_image_usage(image_text, layout_type, panel_count)
    visual_tokens = extract_visual_tokens(decorations_text, item.get("module_observations", {}).get("visual_elements", ""))
    visual_elements = classify_visual_elements(visual_tokens)
    typography_system = build_typography(typography_text, title_flags, layout_type)
    constraints = build_constraints(constraints_text, layout_type, style["name"])
    description = build_description(scene_tags, style["name"], layout_type, image_usage, visual_elements)

    return {
        "name": candidate_name,
        "description": description,
        "has_main_title": title_flags["has_main_title"],
        "has_sub_title": title_flags["has_sub_title"],
        "template_info_tags": scene_tags,
        "layout": layout,
        "style": style,
        "background": background,
        "color_logic": color_logic,
        "image_usage": image_usage,
        "visual_elements": visual_elements,
        "typography_system": typography_system,
        "constraints": constraints,
    }



def cleanup_previous_outputs(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for file_path in output_dir.glob("candidates_*.json"):
        file_path.unlink()



def validate_output(record: Dict[str, Any]) -> None:
    required_top_fields = [
        "name",
        "description",
        "has_main_title",
        "has_sub_title",
        "template_info_tags",
        "layout",
        "style",
        "background",
        "color_logic",
        "image_usage",
        "visual_elements",
        "typography_system",
        "constraints",
    ]
    missing = [field for field in required_top_fields if field not in record]
    if missing:
        raise ValueError(f"missing required fields: {missing}")



def main() -> None:
    items = load_json(INPUT_CANDIDATES)
    if not isinstance(items, list):
        raise ValueError("Input candidates file must be a JSON array.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_previous_outputs(OUTPUT_DIR)

    outputs: List[Dict[str, Any]] = []
    for item in sorted(items, key=lambda value: extract_numeric_suffix(str(value.get("id", "")))):
        record = translate_candidate(item)
        validate_output(record)
        file_path = OUTPUT_DIR / f"{record['name']}.json"
        write_json(file_path, record)
        outputs.append(record)

    write_json(OUTPUT_SUMMARY, outputs)
    print(json.dumps({
        "input_file": str(INPUT_CANDIDATES),
        "output_dir": str(OUTPUT_DIR),
        "summary_file": str(OUTPUT_SUMMARY),
        "count": len(outputs),
    }, ensure_ascii=False))



if __name__ == "__main__":
    main()