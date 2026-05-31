#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent.parent
MEME_DATA_DIR = BASE_DIR / "public" / "data" / "meme"
MEME_JSON = MEME_DATA_DIR / "meme_candidates.json"
MEME_DEV_JSON = MEME_DATA_DIR / "meme_candidates_dev.json"
LOG_PATH = BASE_DIR / "public" / "data" / "meme" / "enrich_memes_run.log"

MODEL_ID = "gemini-3.1-fl"
NODE_ID = "memeAiScreening"
MODEL_INFO_ID = "gemini_flash_lite"
POLL_LABEL = "meme_ai_screening"
POLL_TIMEOUT_SECONDS = 120
ELIGIBLE_STATUS = {"", "scraped", "pending"}
SCORE_KEYS = [
    "emotion_clarity_score",
    "social_usability_score",
    "subject_focus_score",
    "visual_simplicity_score",
    "recognizability_64px_score",
    "meme_popularity_score",
    "meme_versatility_score",
]
CORE_SCORE_KEYS = [
    "emotion_clarity_score",
    "subject_focus_score",
    "recognizability_64px_score",
]

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_stickers as crate

LOG_LINES: List[str] = []


def log(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    LOG_LINES.append(line)


def flush_log() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(LOG_LINES) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_meme_json(env: str = "prod") -> Path:
    env_value = (env or "prod").strip().lower()
    if env_value == "prod":
        return MEME_JSON
    if env_value == "dev":
        return MEME_DEV_JSON
    raise ValueError(f"Unsupported env: {env}. Use prod or dev.")


def load_candidates(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"找不到 meme 数据文件：{path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"last_updated": utc_now(), "source": "giphy_trending", "items": data}
    if not isinstance(data, dict):
        raise TypeError(f"Unsupported JSON root type: {type(data).__name__}")
    data.setdefault("items", [])
    if not isinstance(data["items"], list):
        raise TypeError("meme_candidates.json field items must be a list")
    return data


def normalize_status(value: Any) -> str:
    return str(value or "").strip().lower()


def item_label(item: Dict[str, Any]) -> str:
    for key in ("short_name", "title", "name", "id", "frame"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Unnamed Meme"


def eligible_for_scoring(item: Dict[str, Any]) -> bool:
    if not isinstance(item, dict):
        return False
    ai_decision = item.get("ai_decision")
    if isinstance(ai_decision, str) and ai_decision.strip():
        return False
    status = normalize_status(item.get("status"))
    return status in ELIGIBLE_STATUS


def is_http_url(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def resolve_local_image_path(item: Dict[str, Any]) -> Optional[Path]:
    for key in ("frame_png_path", "raw_image_path"):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            continue
        raw = value.strip()
        if raw.startswith("/"):
            path = BASE_DIR / "public" / raw.lstrip("/")
        else:
            path = BASE_DIR / raw
        if path.exists():
            return path
    return None


def resolve_remote_image_url(item: Dict[str, Any]) -> Optional[str]:
    for key in ("raw_image_url", "cover_url", "gif_url", "final_sticker_url"):
        value = item.get(key)
        if is_http_url(value):
            return str(value).strip()
    return None


def prepare_image_inputs(item: Dict[str, Any]) -> Tuple[List[str], str]:
    local_path = resolve_local_image_path(item)
    if local_path is not None:
        try:
            uploaded_url = crate.upload_file_to_crate(local_path)
            return [uploaded_url], f"uploaded:{local_path.name}"
        except Exception as exc:
            log(f"      ⚠️ 本地图片上传失败，降级为文本评分：{local_path} | {exc}")
    remote_url = resolve_remote_image_url(item)
    if remote_url:
        return [remote_url], remote_url
    return [], "text_only"


def compact_item(item: Dict[str, Any], image_source: str) -> Dict[str, Any]:
    return {
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "name": item.get("name", ""),
        "description": item.get("description", ""),
        "short_name": item.get("short_name", ""),
        "status": item.get("status", ""),
        "source_url": item.get("source_url", ""),
        "gif_url": item.get("gif_url", ""),
        "frame": item.get("frame", ""),
        "image_source": image_source,
    }


def build_prompt(item: Dict[str, Any], image_source: str) -> str:
    candidate_payload = json.dumps(compact_item(item, image_source), ensure_ascii=False, indent=2)
    prompt = (
        "你是热梗 meme 候选的 AI 筛选评审器。请结合候选的文本信息，以及可见图片内容（如果本次提供了图片），按下面 SOP 严格评分。\n\n"
        "【评分维度】每项必须输出 1-5 的整数：\n"
        "1. emotion_clarity_score：情绪/动作是否能被一眼读懂——夸张的动作或表情可以加分，微妙表情必须配合明确的肢体语言才能得高分；纯靠细微眼神/嘴角变化传递情绪的得低分\n"
        "2. social_usability_score：这个表情在 TikTok 任意社交场景（评论区、Story 回复、Thought 内心独白、DM 私信）下，用户是否能快速理解并自发使用？\n"
        "3. subject_focus_score：主体是否单一且突出\n"
        "4. visual_simplicity_score：背景是否干净，文字叠加是否少，构图是否简单\n"
        "5. recognizability_64px_score：缩到 64x64 后是否仍可识别情绪\n"
        "6. meme_popularity_score：梗文化传播力：用户看到这个表情，是否会忍不住想发出去？是否具备在 TikTok 社交场景中自发传播的潜力？\n"
        "7. meme_versatility_score：这个梗能否被用在多种互动场景（评论、Story 回复、DM 聊天、斗图对战）？是否足够通用，让不同用户都能找到使用场景？\n\n"
        "【核心判断】\n"
        "核心问题：用户看到这个，会不会忍不住想发出去？Meme Emoji 的差异化不是更多情绪，而是让用户能用梗说话——具备文化传播力和玩梗潜力。\n\n"
        "【素材类型加权规则】\n"
        "- 动物/拟人动物类（如 doge、grumpy cat）：天然加分，优先入选\n"
        "- 鬼畜/魔性动画类（如 Nyan Cat、Bad Apple）：魔性感本身是记忆点，优先入选\n"
        "- 真人夸张表情/动作（极度崩溃、嘴张很大等）：正常入选\n"
        "- 真人微表情（轻微眼神、嘴角变化等）：降权处理，除非动作辅助明确情绪\n\n"
        "【硬过滤】满足任一即 hard_filter_hit=true：\n"
        "- 已有卡通 IP 角色（迪士尼/皮克斯人物、Pokemon、Sanrio 等知名 IP 形象）→ 直接 reject，版权风险\n"
        "- 纯风景、品牌、产品类，无情绪主体\n"
        "- 多人群体镜头，无突出表情焦点\n"
        "- 大量文字叠加，影响视觉转译\n"
        "- 强政治、宗教、争议性人物\n"
        "- 完全依赖音频或视频才能理解\n\n"
        "【风险评级】\n"
        "- high：强政治、宗教、争议性人物\n"
        "- medium：非敏感但存在一定转译难度的内容\n"
        "- low：动物、虚拟角色、真实人物、公众人物等非硬过滤素材，只按情绪/传播力判断；已有卡通 IP 角色命中硬过滤直接 reject\n\n"
        "【决策规则】\n"
        "- 如果命中硬过滤，ai_decision 必须是 reject\n"
        "- 如果 risk_level 是 high，ai_decision 必须是 reject\n"
        "- 如果 emotion_clarity_score、subject_focus_score、recognizability_64px_score 任一小于 3，ai_decision 必须是 reject\n"
        "- 真实人物/公众人物不触发人工复核，直接按情绪明确度、可转译性、传播力判断；已有卡通 IP 角色直接 reject\n"
        "- 其余情况，ai_decision 必须是 accept\n\n"
        "【输出要求】\n"
        "- 只输出一个 JSON 对象，不要 markdown，不要解释，不要代码块\n"
        "- short_name 是一个 ≤8 个英文单词的简短标题，要能概括这个 meme 的核心情绪/场景，适合作为 emoji 展示标签\n"
        "- emotion 用简短中文，例如 开心、崩溃、无语、尴尬、得意、震惊、困惑、委屈 等\n"
        "- visual_features 输出 2-6 个简短中文短语数组\n"
        "- risk_level 只能是 low、medium、high\n"
        "- ai_decision 只能是 accept、reject\n"
        "- risk_note 和 ai_reason 用中文短句，简洁但明确\n"
        "- 如果没有提供图片或图片信息不足，请基于文本尽量判断，但不要编造看不到的细节\n\n"
        "【候选信息】\n"
        + candidate_payload
        + "\n\n【返回 JSON 模板】\n"
        + "{\n"
        + "  \"short_name\": \"Confused Reaction\",\n"
        + "  \"emotion\": \"困惑\",\n"
        + "  \"visual_features\": [\"表情夸张\", \"主体单一\"],\n"
        + "  \"emotion_clarity_score\": 4,\n"
        + "  \"social_usability_score\": 4,\n"
        + "  \"subject_focus_score\": 4,\n"
        + "  \"visual_simplicity_score\": 3,\n"
        + "  \"recognizability_64px_score\": 4,\n"
        + "  \"meme_popularity_score\": 4,\n"
        + "  \"meme_versatility_score\": 4,\n"
        + "  \"risk_level\": \"low\",\n"
        + "  \"risk_note\": \"无明显风险，按情绪和传播力判断\",\n"
        + "  \"hard_filter_hit\": false,\n"
        + "  \"hard_filter_reason\": \"\",\n"
        + "  \"ai_decision\": \"accept\",\n"
        + "  \"ai_reason\": \"情绪明确，主体集中，具备玩梗传播力\"\n"
        + "}"
    )
    return prompt


def build_scoring_node(prompt: str) -> Dict[str, Any]:
    return {
        "id": NODE_ID,
        "type": "note",
        "position": {"x": 780, "y": 40},
        "selected": False,
        "dragging": False,
        "width": 360,
        "height": 560,
        "resizing": False,
        "extent": "parent",
        "parentId": crate.GROUP_ID,
        "measured": {"width": 360, "height": 560},
        "data": {
            "title": "meme_ai_screening",
            "version": 2,
            "text": "",
            "input": {"prompt": prompt},
            "modelInfo": {"modelId": MODEL_INFO_ID},
            "output": {"text": ""},
            "_running": False,
            "_hovering": False,
            "_waitingForUpstream": False,
        },
    }


def extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise ValueError("LLM 返回为空")
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except Exception:
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError(f"无法从 LLM 输出中解析 JSON：{text[:500]}")


def sanitize_text(value: Any, default: str = "") -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text or default


def normalize_visual_features(value: Any) -> List[str]:
    if isinstance(value, list):
        raw_list = value
    else:
        raw_list = re.split(r"[，,、；;\n]+", str(value or ""))
    features: List[str] = []
    seen = set()
    for item in raw_list:
        text = sanitize_text(item)
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        features.append(text)
        if len(features) >= 6:
            break
    if not features:
        return ["信息不足"]
    return features


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except Exception:
        score = 1
    return max(1, min(5, score))


def normalize_short_name(value: Any, fallback: str = "Meme Reaction") -> str:
    text = sanitize_text(value) or sanitize_text(fallback) or "Meme Reaction"
    text = re.sub(r"[^A-Za-z0-9 \'-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()[:8]
    result = " ".join(words).strip(" -_\'")
    return result or "Meme Reaction"


def normalize_risk_level(value: Any) -> str:
    text = sanitize_text(value).lower()
    if text in {"low", "medium", "high"}:
        return text
    return "medium"


def bool_from_any(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = sanitize_text(value).lower()
    return text in {"1", "true", "yes", "y", "hit"}


def derive_ai_decision(assessment: Dict[str, Any], hard_filter_hit: bool) -> str:
    if hard_filter_hit:
        return "reject"
    if assessment["risk_level"] == "high":
        return "reject"
    for key in CORE_SCORE_KEYS:
        if assessment[key] < 3:
            return "reject"
    return "accept"


def default_ai_reason(assessment: Dict[str, Any], hard_filter_hit: bool, hard_filter_reason: str) -> str:
    if hard_filter_hit:
        return hard_filter_reason or "命中硬过滤规则，不适合进入后续流程"
    if assessment["risk_level"] == "high":
        return "存在高风险敏感人物或争议属性，直接拒绝"
    if any(assessment[key] < 3 for key in CORE_SCORE_KEYS):
        return "核心识别维度过低，不适合作为 Meme Emoji"
    return "情绪明确，主体突出，具备玩梗传播力和社交使用潜力"


def normalize_assessment(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    assessment: Dict[str, Any] = {
        "short_name": normalize_short_name(payload.get("short_name")),
        "emotion": sanitize_text(payload.get("emotion"), "待判断"),
        "visual_features": normalize_visual_features(payload.get("visual_features")),
        "risk_level": normalize_risk_level(payload.get("risk_level")),
        "risk_note": sanitize_text(payload.get("risk_note"), "待补充"),
    }
    for key in SCORE_KEYS:
        assessment[key] = clamp_score(payload.get(key))

    hard_filter_hit = bool_from_any(payload.get("hard_filter_hit"))
    hard_filter_reason = sanitize_text(payload.get("hard_filter_reason"))
    assessment["ai_decision"] = derive_ai_decision(assessment, hard_filter_hit)
    assessment["ai_reason"] = sanitize_text(payload.get("ai_reason")) or default_ai_reason(assessment, hard_filter_hit, hard_filter_reason)
    meta = {
        "hard_filter_hit": hard_filter_hit,
        "hard_filter_reason": hard_filter_reason,
    }
    return assessment, meta


def derive_status(ai_decision: str) -> str:
    if ai_decision == "accept":
        return "pending"
    if ai_decision == "reject":
        return "rejected"
    return "rejected"


def ensure_crate_token() -> None:
    latest_token = crate.get_jwt_token()
    if latest_token:
        crate.JWT_TOKEN = latest_token
    if not sanitize_text(crate.JWT_TOKEN):
        raise RuntimeError("未能获取可用的 Crate JWT Token")


def run_llm_screening(item: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    image_inputs, image_source = prepare_image_inputs(item)
    prompt = build_prompt(item, image_source)
    parameters: Dict[str, Any] = {"prompt": prompt}
    if image_inputs:
        parameters["images"] = image_inputs
    submit_meta = crate.submit_node(MODEL_ID, NODE_ID, build_scoring_node(prompt), parameters)
    old_timeout = getattr(crate, "POLL_TIMEOUT_SECONDS", None)
    crate.POLL_TIMEOUT_SECONDS = POLL_TIMEOUT_SECONDS
    try:
        raw_text, raw_payload = crate.poll_result(submit_meta, "text", POLL_LABEL)
    finally:
        if old_timeout is not None:
            crate.POLL_TIMEOUT_SECONDS = old_timeout
    parsed = extract_json_object(raw_text)
    assessment, model_meta = normalize_assessment(parsed)
    runtime_meta = {
        "image_source": image_source,
        "submit_meta": submit_meta,
        "raw_payload": raw_payload,
        "raw_text": raw_text,
        "hard_filter_hit": model_meta["hard_filter_hit"],
        "hard_filter_reason": model_meta["hard_filter_reason"],
    }
    return assessment, runtime_meta


def apply_assessment(item: Dict[str, Any], assessment: Dict[str, Any]) -> None:
    for key, value in assessment.items():
        item[key] = value
    item["status"] = derive_status(assessment["ai_decision"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score meme candidates with AI screening SOP")
    parser.add_argument("--dry-run", action="store_true", help="只打印评分结果，不写入 JSON")
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少条，0 表示不限制")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod", help="数据环境：prod 读写正式 JSON，dev 读写测试 JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        log("开始进行 meme AI 筛选评分")
        meme_json = resolve_meme_json(args.env)
        data = load_candidates(meme_json)
        items = data["items"]
        targets = [item for item in items if eligible_for_scoring(item)]
        if args.limit > 0:
            targets = targets[: args.limit]
        log(f"读取现有数据：{meme_json}，env={args.env}，共有 {len(items)} 条，待处理 {len(targets)} 条")

        if not targets:
            log("没有需要评分的条目")
            return 0

        ensure_crate_token()

        previews: List[Dict[str, Any]] = []
        failed_items: List[Dict[str, Any]] = []
        processed_count = 0

        for index, item in enumerate(targets, start=1):
            label = item_label(item)
            log(f"评估 {index}/{len(targets)}：{label}")
            try:
                assessment, runtime_meta = run_llm_screening(item)
                preview = {
                    "label": label,
                    "status": derive_status(assessment["ai_decision"]),
                    **assessment,
                    "image_source": runtime_meta["image_source"],
                }
                previews.append(preview)
                if not args.dry_run:
                    apply_assessment(item, assessment)
                processed_count += 1
                log(
                    "      ✅ 决策="
                    + assessment["ai_decision"]
                    + " | 风险="
                    + assessment["risk_level"]
                    + " | 核心分="
                    + "/".join(str(assessment[key]) for key in CORE_SCORE_KEYS)
                    + " | 情绪="
                    + assessment["emotion"]
                )
            except Exception as exc:
                failed_items.append({"label": label, "error": str(exc)})
                log(f"      ❌ 评分失败：{label} | {type(exc).__name__}: {exc}")
                if not args.dry_run:
                    item["status"] = "rejected"
                    item["reject_reason"] = f"screening_error: {type(exc).__name__}"

            if not args.dry_run:
                data["last_updated"] = utc_now()
                meme_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if args.dry_run:
            print(json.dumps({"scored_items": previews, "failed_items": failed_items}, ensure_ascii=False, indent=2))
            log("dry-run 模式：未写入文件")
        else:
            log(f"写入完成：{meme_json} | 成功处理 {processed_count} 条，失败并标记 rejected {len(failed_items)} 条")

        # Partial per-item screening failures are handled above and marked rejected.
        # If the enrich pass reaches this point, the pipeline should continue.
        return 0
    except Exception as exc:
        log(f"ERROR {type(exc).__name__}: {exc}")
        return 1
    finally:
        flush_log()


if __name__ == "__main__":
    sys.exit(main())
