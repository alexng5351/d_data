#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
sys.setrecursionlimit(10000)
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


JWT_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJwYWFzLnBhc3Nwb3J0LmF1dGgiLCJleHAiOjE3ODAwNDQwMjcsImlhdCI6MTc4MDA0MDM2NywidXNlcm5hbWUiOiJuZ2NoZWVjaG9uZyIsInR5cGUiOiJwZXJzb25fYWNjb3VudCIsInJlZ2lvbiI6ImkxOG4iLCJ0cnVzdGVkIjp0cnVlLCJ1dWlkIjoiYjFlYTg2NDEtOThjMC00NWRkLTliZjgtZjBlY2U0OWMzODc2Iiwic2l0ZSI6ImkxOG4iLCJieXRlY2xvdWRfdGVuYW50X2lkIjoiYnl0ZWRhbmNlIiwiYnl0ZWNsb3VkX3RlbmFudF9pZF9vcmciOiJieXRlZGFuY2UiLCJzY29wZSI6ImJ5dGVkYW5jZSIsInNlcXVlbmNlIjoiRGVzaWduIiwib3JnYW5pemF0aW9uIjoiVGlrVG9rLURlc2lnbi1DcmVhdGl2ZSIsIndvcmtfY291bnRyeSI6IkNITiIsImF2YXRhcl91cmwiOiJodHRwczovL3MxNi1pbWZpbGUtc2cuZmVpc2h1Y2RuLmNvbS9zdGF0aWMtcmVzb3VyY2UvdjEvdjNfMDB0Zl81YjAxODQ2YS1iNTNiLTRhZTQtOWQwNS01Y2FhMzFmODI5aHV-P2ltYWdlX3NpemU9bm9vcFx1MDAyNmN1dF90eXBlPVx1MDAyNnF1YWxpdHk9XHUwMDI2Zm9ybWF0PXBuZ1x1MDAyNnN0aWNrZXJfZm9ybWF0PS53ZWJwIiwiZW1haWwiOiJuZ2NoZWVjaG9uZ0BieXRlZGFuY2UuY29tIiwiZW1wbG95ZWVfaWQiOjgxNTM4MzYsIm5ld19lbXBsb3llZV9pZCI6ODE1MzgzNiwib2dfbGltaXQiOiJsaW1pdCIsImlzc3VlX3NvdXJjZSI6InNzb19jb29raWUifQ.mDLxYJCJ7Pw35hkO0HLapp8OfL1g_Fl4H6LXGcVqkypwzNROS3IslKHQDPkrYqcE44TdagNWJAhBvgE17Zw5b-Q1tDhyiw4UPdSCAKvNc4TCD0l6OBYaXrsaasianhPvCMF_ZFEpMl6M-e2FP6G9y3hDHuk6YTfyrAqm4S3I5qw'
CRATE_KEY = "wk_2e25d1fb37d8a769bdb821fa38eec238147ccbd97f87b4928fd981b12f4b3648"
PROJECT_ID = "7641896827951777799"
GROUP_ID = "group-ESV1Jw7"

def get_jwt_token() -> str:
    """自动获取字节云 JWT Token"""
    cmds = [
        "bytedcli --json --site i18n-tt auth get-bytecloud-jwt-token | jq -r .data.jwt",
        "/Users/bytedance/Meme_Emoji_Generator/node_modules/.bin/bytedcli --json --site i18n-tt auth get-bytecloud-jwt-token | jq -r .data.jwt"
    ]
    for cmd in cmds:
        try:
            import subprocess
            result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
            if result and result != "null" and not result.startswith("Error"):
                return result
        except Exception:
            continue
    return ""

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRAME_DIR = BASE_DIR / "public" / "images" / "meme" / "frames"
STICKER_DIR = BASE_DIR / "public" / "images" / "meme" / "stickers"
RESULTS_JSON = BASE_DIR / "public" / "data" / "meme" / "frame_generation_results.json"
MEME_DATA_DIR = BASE_DIR / "public" / "data" / "meme"
MEME_CANDIDATES_JSON = MEME_DATA_DIR / "meme_candidates.json"
MEME_CANDIDATES_DEV_JSON = MEME_DATA_DIR / "meme_candidates_dev.json"
LOG_PATH = BASE_DIR / "public" / "data" / "meme" / "frame_generation_run.log"

UPLOAD_URL = "https://crate.tiktok-row.net/api/tos/upload_file"
SAVE_DRAFT_URL = "https://crate.tiktok-row.net/api/canvasFlow/saveDraft"
SUBMIT_URL = "https://crate.tiktok-row.net/api/v1/generation/submit"
BATCH_QUERY_URL = "https://crate.tiktok-row.net/api/v1/generation/batch-query"
GENERATION_DETAIL_URL_TEMPLATE = "https://crate.tiktok-row.net/api/v1/generation/{identifier}"

EMOJI_STYLE_REFERENCE_IMAGE_URL = "https://lf-crate.ibytedtos.com/obj/tt-crate-aigc-tool-prod-us/aigc_tool/files/avs6sf7kq9yceiji4x4ry9t5o.png"

MEME_REF_NODE_ID = "AfetCXq"
EMOJI_STYLE_NODE_ID = "bLeFGPI"
TEXT_PROMPT_NODE_ID = "c9h4ELH"
IMAGE_GENERATE_NODE_ID = "IPCchh5"
REMOVE_BG_NODE_ID = "lXTkw9W"

TEXT_PROMPT_MODEL_ID = "gemini-3.1-fl"
IMAGE_GENERATE_MODEL_ID = "nano-banana2"
REMOVE_BG_MODEL_ID = "saliency_seg"

POLL_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 3
REQUEST_TIMEOUT_SECONDS = 60
REQUEST_RETRY_COUNT = 3
RETRY_BACKOFF_SECONDS = 2

TEXT_PROMPT_INSTRUCTION = """请分析图1，并基于图1和图2生成中文生图提示词。

规则：

1. 图像参考关系
- 图1是内容参考：只提取 meme 的核心内容、表情、姿态、道具和识别特征。
- 图2是风格参考：只参考 TikTok emoji 的 2.5D 图标风格。

2. 先判断图1的取景范围
- 头像 / 头肩 / 半身 / 全身
- 最终生成图必须严格继承图1的取景范围。
- 如果图1只有头部或脸部，不要补充脖子、肩膀、身体、手臂或衣服。
- 如果图1是头肩，只保留头、脖子和肩部，不要补充手臂或完整身体。
- 只有当图1中身体、手势、道具或全身姿态是核心识别特征时，才生成半身或全身。

3. 判断角色类型
- 非人类角色：保留原始体色和物种特征，只做 2.5D emoji 风格化。
- 人类角色：转为黄色 emoji 化人类卡通角色，不要写实，不要半写实，不要变成普通圆形 emoji 脸。
- 人类角色需要保留图1中已经出现的人类特征，例如头型、耳朵、发型、脸部轮廓、脖子、肩部、手势或服饰，但不要新增图1没有出现的身体结构。

4. 提炼 meme 核心特征
提炼 3–5 个最重要的视觉识别特征，可包括：
- 眼神、眉毛、嘴型、表情强度
- 身体姿态、手势、动作方向
- 道具、配件、符号
- 构图关系和 meme 反应感
不要只关注脸部；如果道具、身体或构图是识别关键，必须保留。

5. 生图提示词要求
- 开头说明：以图1作为内容参考，以图2作为风格参考。
- 明确说明取景范围：头像 / 头肩 / 半身 / 全身。
- 保留图1的核心 meme 识别特征。
- 风格参考图2：2.5D emoji 图标风格，柔和矢量渐变，轻微立体感，圆润简洁，表情夸张，高辨识度，无写实纹理。
- 构图：主体占画面 75%–80%，四周均匀留白，主体不切边，1:1 正方形构图，白色背景。
- 不要照抄图1，只保留 meme 的识别逻辑和关键视觉特征。

负向约束：
无写实纹理，无皮毛细节，无褶皱，无写实阴影，无深色投影，无镜面高光，无反光，无描边，无复杂背景，主体不切边，不要写实人像，不要半写实脸，不要真实五官比例，不要真实鼻梁、真实嘴唇、真实牙齿，不要肖像感，不要新增图1没有出现的身体结构。

只输出最终中文生图提示词，不需要解释。"""

LOG_LINES: List[str] = []


def log(message: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    LOG_LINES.append(line)


def flush_log() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(LOG_LINES) + "\n", encoding="utf-8")


def save_results(data: Dict[str, Any]) -> None:
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_http_url(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def request_json(method: str, url: str, *, headers: Optional[Dict[str, str]] = None, json_body: Optional[Dict[str, Any]] = None, files: Any = None) -> Any:
    last_error: Optional[Exception] = None
    for attempt in range(1, REQUEST_RETRY_COUNT + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                files=files,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            try:
                payload = response.json()
            except Exception:
                payload = {"raw_text": response.text}
            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}: {payload}")
            if isinstance(payload, dict) and payload.get("statusCode") not in (None, 0):
                raise RuntimeError(f"API statusCode={payload.get('statusCode')}: {payload.get('message') or payload}")
            return payload
        except Exception as exc:
            last_error = exc
            log(f"      请求失败 [{attempt}/{REQUEST_RETRY_COUNT}] {method} {url}: {exc}")
            if attempt < REQUEST_RETRY_COUNT:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"请求最终失败: {method} {url}: {last_error}")


def upload_file_to_crate(file_path: Path) -> str:
    headers = {"x-jwt-token": JWT_TOKEN}
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    with file_path.open("rb") as file_obj:
        payload = request_json(
            "POST",
            UPLOAD_URL,
            headers=headers,
            files={"file": (file_path.name, file_obj, content_type)},
        )
    for candidate in (
        payload.get("data", {}).get("url") if isinstance(payload, dict) else None,
        payload.get("url") if isinstance(payload, dict) else None,
    ):
        if is_http_url(candidate):
            return candidate
    raise RuntimeError(f"上传成功但未拿到内部 URL: {payload}")


def crop_to_square(image_url: str) -> str:
    """下载图片，居中裁切成正方形，保存到本地并返回相对路径；如果已经是 1:1 则原样返回原 URL。"""
    from PIL import Image
    import io

    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content))
    w, h = img.size

    if w == h:
        return image_url

    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img_cropped = img.crop((left, top, left + size, top + size))

    STICKER_DIR.mkdir(parents=True, exist_ok=True)
    source_name = Path(image_url.split("?", 1)[0]).name or f"sticker_{uuid.uuid4().hex}"
    stem = Path(source_name).stem or f"sticker_{uuid.uuid4().hex}"
    output_path = STICKER_DIR / f"{stem}_square.png"
    img_cropped.save(output_path, format="PNG")
    return str(output_path.relative_to(BASE_DIR))


def build_text_prompt_node() -> Dict[str, Any]:
    return {
        "id": TEXT_PROMPT_NODE_ID,
        "type": "note",
        "position": {"x": 780, "y": 40},
        "selected": False,
        "dragging": False,
        "width": 320,
        "height": 700,
        "resizing": False,
        "extent": "parent",
        "parentId": GROUP_ID,
        "measured": {"width": 320, "height": 700},
        "data": {
            "title": "text_prompt",
            "version": 2,
            "text": "",
            "input": {"prompt": TEXT_PROMPT_INSTRUCTION},
            "modelInfo": {"modelId": "gemini_flash_lite"},
            "output": {"optimizedPrompt": ""},
            "_running": False,
            "_hovering": False,
            "_waitingForUpstream": False,
        },
    }


def build_image_generate_node(optimized_prompt: str) -> Dict[str, Any]:
    return {
        "id": IMAGE_GENERATE_NODE_ID,
        "type": "image",
        "position": {"x": 1180, "y": 240},
        "selected": False,
        "dragging": False,
        "extent": "parent",
        "parentId": GROUP_ID,
        "measured": {"width": 324, "height": 324},
        "data": {
            "title": "image_generate",
            "version": 2,
            "displayRatio": 1,
            "modelInfo": {"modelId": IMAGE_GENERATE_MODEL_ID, "modelIds": [IMAGE_GENERATE_MODEL_ID]},
            "input": {"prompt": optimized_prompt, "aspectRatio": "1:1"},
            "generationType": "background-fusion",
            "frozen": False,
            "_running": False,
            "_hovering": False,
            "_waitingForUpstream": False,
        },
    }


def build_remove_bg_node(source_image_url: str) -> Dict[str, Any]:
    return {
        "id": REMOVE_BG_NODE_ID,
        "type": "image",
        "position": {"x": 1560, "y": 240},
        "selected": False,
        "dragging": False,
        "parentId": GROUP_ID,
        "extent": "parent",
        "measured": {"width": 324, "height": 324},
        "data": {
            "title": "image_remove_bg",
            "version": 2,
            "displayRatio": 1,
            "modelInfo": {"modelId": REMOVE_BG_MODEL_ID, "modelIds": [REMOVE_BG_MODEL_ID]},
            "input": {"aspectRatio": 1, "uploadUrl": [source_image_url]},
            "generationType": "image-segmentation",
            "_running": False,
            "_hovering": False,
            "_waitingForUpstream": False,
        },
    }


def build_save_draft_graph(meme_reference_internal_url: str) -> Dict[str, Any]:
    return {
        "nodes": [
            {
                "id": GROUP_ID,
                "type": "group",
                "position": {"x": 760, "y": 0},
                "style": {"width": 2044, "height": 784},
                "selected": True,
                "width": 1944,
                "height": 784,
                "resizing": False,
                "dragging": False,
                "data": {
                    "version": 2,
                    "title": "Meme-to-Emoji Sticker Generator",
                    "workflowConfig": {
                        "inputs": [
                            {"nodeId": MEME_REF_NODE_ID, "key": "meme_reference_image"},
                            {"nodeId": EMOJI_STYLE_NODE_ID, "key": "emoji_style_reference_image"},
                        ],
                        "outputs": [
                            {"nodeId": IMAGE_GENERATE_NODE_ID, "key": "image_generate"},
                            {"nodeId": REMOVE_BG_NODE_ID, "key": "image_remove_bg"},
                            {"nodeId": TEXT_PROMPT_NODE_ID, "key": "text_prompt"},
                        ],
                    },
                    "variableConfig": {"variables": []},
                },
            },
            {
                "id": MEME_REF_NODE_ID,
                "type": "staticImage",
                "position": {"x": 240, "y": 40},
                "selected": False,
                "dragging": False,
                "parentId": GROUP_ID,
                "extent": "parent",
                "data": {
                    "title": "meme_reference_image",
                    "version": 2,
                    "displayRatio": 1,
                    "output": {"imageUrl": meme_reference_internal_url, "aspectRatio": 1},
                },
            },
            {
                "id": EMOJI_STYLE_NODE_ID,
                "type": "staticImage",
                "position": {"x": 40, "y": 420},
                "selected": False,
                "dragging": False,
                "parentId": GROUP_ID,
                "extent": "parent",
                "data": {
                    "title": "emoji_style_reference_image",
                    "version": 2,
                    "displayRatio": 1.97,
                    "output": {"imageUrl": EMOJI_STYLE_REFERENCE_IMAGE_URL, "aspectRatio": 1.97},
                },
            },
            build_text_prompt_node(),
            build_image_generate_node(""),
            build_remove_bg_node(""),
        ],
        "edges": [
            {"id": "AfetCXq-c9h4ELH", "type": "custom", "source": MEME_REF_NODE_ID, "sourceHandle": "source", "target": TEXT_PROMPT_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True, "data": {"version": 2, "title": "New Edge"}},
            {"id": "bLeFGPI-c9h4ELH", "type": "custom", "source": EMOJI_STYLE_NODE_ID, "sourceHandle": "source", "target": TEXT_PROMPT_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True, "data": {"version": 2, "title": "New Edge"}},
            {"id": "ctF0aq5", "type": "custom", "source": TEXT_PROMPT_NODE_ID, "sourceHandle": "source", "target": IMAGE_GENERATE_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True},
            {"id": "ckCCvbl", "type": "custom", "source": MEME_REF_NODE_ID, "sourceHandle": "source", "target": IMAGE_GENERATE_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True, "data": {"version": 2, "title": "New Edge"}},
            {"id": "8Uijs7z", "type": "custom", "source": EMOJI_STYLE_NODE_ID, "sourceHandle": "source", "target": IMAGE_GENERATE_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True, "data": {"version": 2, "title": "New Edge"}},
            {"id": "uegkWdQ", "type": "custom", "source": IMAGE_GENERATE_NODE_ID, "sourceHandle": "source", "target": REMOVE_BG_NODE_ID, "targetHandle": "target", "selected": False, "selectable": True},
        ],
        "version": 2,
        "viewport": {"x": -271.56555258095034, "y": 217.64657472533145, "zoom": 0.5393033978236561},
    }


def save_draft_graph(meme_reference_internal_url: str) -> None:
    body = {
        "projectId": PROJECT_ID,
        "graph": json.dumps(build_save_draft_graph(meme_reference_internal_url), ensure_ascii=False),
    }
    request_json("POST", SAVE_DRAFT_URL, headers={"X-Crate-Key": CRATE_KEY, "X-Jwt-Token": JWT_TOKEN, "Content-Type": "application/json"}, json_body=body)
    log("      saveDraft success")


def extract_task_id(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        for key in ("taskId", "task_id", "id"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for nested_key in ("data", "result"):
            nested = payload.get(nested_key)
            task_id = extract_task_id(nested)
            if task_id:
                return task_id
    return None


def extract_run_instance_id(payload: Any) -> Optional[str]:
    stack = [payload]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if not isinstance(current, dict):
            continue
        current_id = id(current)
        if current_id in seen:
            continue
        seen.add(current_id)
        for key in ("runInstanceId", "run_instance_id", "requestId", "request_id"):
            value = current.get(key)
            if isinstance(value, str) and value:
                return value
        for nested_key in ("data", "result"):
            nested = current.get(nested_key)
            if isinstance(nested, dict):
                stack.append(nested)
    return None


def submit_node(model_id: str, node_id: str, node_payload: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    request_id = str(uuid.uuid4())
    payload = {
        "modelId": model_id,
        "nodeId": node_id,
        "nodeStr": json.dumps(node_payload, ensure_ascii=False, separators=(",", ":")),
        "parameters": parameters,
        "projectId": PROJECT_ID,
        "requestId": request_id,
    }
    response_payload = request_json(
        "POST",
        SUBMIT_URL,
        headers={"X-Crate-Key": CRATE_KEY, "X-Jwt-Token": JWT_TOKEN, "Content-Type": "application/json"},
        json_body=payload,
    )
    task_id = extract_task_id(response_payload)
    run_instance_id = extract_run_instance_id(response_payload)
    log(f"      submit {node_id} success | requestId={request_id} | taskId={task_id or '-'} | ref={run_instance_id or '-'}")
    return {
        "request_id": request_id,
        "task_id": task_id,
        "run_instance_id": run_instance_id,
        "response": response_payload,
    }


def extract_task_infos(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        for container in (payload, payload.get("data") if isinstance(payload.get("data"), dict) else None):
            if not isinstance(container, dict):
                continue
            task_infos = container.get("taskInfos") or container.get("task_infos")
            if isinstance(task_infos, list):
                return [item for item in task_infos if isinstance(item, dict)]
            task_info = container.get("taskInfo") or container.get("task_info")
            if isinstance(task_info, dict):
                return [task_info]
        return [payload]
    return []


def normalize_status(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"success", "succeeded", "completed", "done", "finish", "finished", "2"}:
        return "success"
    if text in {"failed", "error", "failure", "3", "cancelled", "canceled"}:
        return "failed"
    return "running"


def extract_status(payload: Any) -> str:
    infos = extract_task_infos(payload)
    for info in infos:
        for key in ("task_status", "status", "state"):
            if key in info:
                return normalize_status(info.get(key))
        if extract_text_result(info) or extract_image_result(info):
            return "success"
    return "running"


def extract_error_message(payload: Any) -> str:
    stack = [payload]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if not isinstance(current, dict):
            continue
        current_id = id(current)
        if current_id in seen:
            continue
        seen.add(current_id)
        error = current.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error.get("msg")
            if isinstance(message, str) and message.strip():
                return message.strip()
            stack.append(error)
        for key in ("message", "msg"):
            value = current.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        stack.extend(extract_task_infos(current))
    return ""


def extract_text_result(payload: Any) -> Optional[str]:
    infos = extract_task_infos(payload)
    for info in infos:
        results = info.get("results")
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    content = item.get("content")
                    if isinstance(content, str) and content.strip() and not is_http_url(content.strip()):
                        return content.strip()
        output = info.get("output")
        if isinstance(output, dict):
            value = output.get("optimizedPrompt") or output.get("text")
            if isinstance(value, str) and value.strip():
                return value.strip()
        data = info.get("data")
        if isinstance(data, dict):
            value = data.get("optimizedPrompt") or data.get("text")
            if isinstance(value, str) and value.strip():
                return value.strip()
        direct = info.get("optimizedPrompt")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()
    return None


def extract_image_result(payload: Any) -> Optional[str]:
    infos = extract_task_infos(payload)
    for info in infos:
        results = info.get("results")
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    content = item.get("content")
                    if is_http_url(content):
                        return content
        output = info.get("output")
        if isinstance(output, dict):
            for key in ("imageUrl", "url", "uri"):
                value = output.get(key)
                if is_http_url(value):
                    return value
            urls = output.get("urls")
            if isinstance(urls, list):
                for value in urls:
                    if is_http_url(value):
                        return value
            image = output.get("image")
            if isinstance(image, dict):
                value = image.get("url")
                if is_http_url(value):
                    return value
        data = info.get("data")
        if isinstance(data, dict):
            image = data.get("image")
            if isinstance(image, dict) and is_http_url(image.get("url")):
                return image.get("url")
    return None


def poll_by_batch_query(task_id: str) -> Any:
    return request_json(
        "POST",
        BATCH_QUERY_URL,
        headers={"X-Crate-Key": CRATE_KEY, "X-Jwt-Token": JWT_TOKEN, "Content-Type": "application/json"},
        json_body={"taskIds": [task_id]},
    )


def poll_by_detail(identifier: str) -> Any:
    return request_json(
        "GET",
        GENERATION_DETAIL_URL_TEMPLATE.format(identifier=identifier),
        headers={"X-Crate-Key": CRATE_KEY, "X-Jwt-Token": JWT_TOKEN, "Accept": "application/json"},
    )


def poll_result(submit_meta: Dict[str, Any], result_kind: str, label: str) -> Tuple[str, Any]:
    identifiers: List[Tuple[str, str]] = []
    if submit_meta.get("task_id"):
        identifiers.append(("task_id", submit_meta["task_id"]))
    if submit_meta.get("run_instance_id"):
        identifiers.append(("run_instance_id", submit_meta["run_instance_id"]))
    if not identifiers:
        raise RuntimeError(f"{label} submit 后没有可轮询标识: {submit_meta}")

    start = time.time()
    attempt = 0
    last_error = ""
    while time.time() - start <= POLL_TIMEOUT_SECONDS:
        attempt += 1
        for ident_type, ident in identifiers:
            try:
                payload = poll_by_batch_query(ident) if ident_type == "task_id" else poll_by_detail(ident)
            except Exception as exc:
                last_error = str(exc)
                continue
            result_value = extract_text_result(payload) if result_kind == "text" else extract_image_result(payload)
            if result_value:
                return result_value, payload
            status = extract_status(payload)
            if status == "failed":
                raise RuntimeError(extract_error_message(payload) or f"{label} 任务失败")
        log(f"      ⏳ 等待 {label} 结果... 第 {attempt} 次轮询")
        time.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(f"{label} 轮询超时，最后错误: {last_error or '-'}")


def submit_text_prompt(meme_internal_url: str) -> Dict[str, Any]:
    return submit_node(
        TEXT_PROMPT_MODEL_ID,
        TEXT_PROMPT_NODE_ID,
        build_text_prompt_node(),
        {
            "images": [meme_internal_url, EMOJI_STYLE_REFERENCE_IMAGE_URL],
            "prompt": TEXT_PROMPT_INSTRUCTION,
        },
    )


def submit_image_generate(meme_internal_url: str, optimized_prompt: str) -> Dict[str, Any]:
    return submit_node(
        IMAGE_GENERATE_MODEL_ID,
        IMAGE_GENERATE_NODE_ID,
        build_image_generate_node(optimized_prompt),
        {
            "images": [meme_internal_url, EMOJI_STYLE_REFERENCE_IMAGE_URL],
            "prompt": optimized_prompt,
            "aspectRatio": "1:1",
            "generationType": "background-fusion",
        },
    )


def submit_remove_bg(image_url: str) -> Dict[str, Any]:
    return submit_node(
        REMOVE_BG_MODEL_ID,
        REMOVE_BG_NODE_ID,
        build_remove_bg_node(image_url),
        {
            "images": [image_url],
            "aspectRatio": 1,
        },
    )


def process_frame(frame_path: Path, *, full_pipeline: bool) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "frame": frame_path.name,
        "file_path": str(frame_path),
        "mode": "full_pipeline" if full_pipeline else "text_only",
        "internal_url": None,
        "optimizedPrompt": None,
        "image_generate_url": None,
        "status": "running",
        "error": None,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        log(f"🚀 开始处理 {frame_path.name} | mode={result['mode']}")
        internal_url = upload_file_to_crate(frame_path)
        result["internal_url"] = internal_url
        log(f"      上传成功: {internal_url}")

        save_draft_graph(internal_url)

        text_submit = submit_text_prompt(internal_url)
        optimized_prompt, text_payload = poll_result(text_submit, "text", f"{frame_path.name} text_prompt")
        result["optimizedPrompt"] = optimized_prompt
        result["text_submit"] = {k: v for k, v in text_submit.items() if k != "response"}
        result["text_poll_status"] = extract_status(text_payload)
        log(f"      ✅ text_prompt 成功: {optimized_prompt}")

        if not full_pipeline:
            result["status"] = "text_prompt_completed"
            return result

        generated_variants: List[Dict[str, Any]] = []
        variant_errors: List[Dict[str, Any]] = []
        for variant_idx in range(3):
            variant_no = variant_idx + 1
            try:
                log(f"      🎲 开始生成变体 {variant_no}/3")
                image_submit = submit_image_generate(internal_url, optimized_prompt)
                image_url, image_payload = poll_result(image_submit, "image", f"{frame_path.name} image_generate variant {variant_no}")
                log(f"      ✅ image_generate 变体 {variant_no}/3 成功: {image_url}")

                remove_bg_submit = submit_remove_bg(image_url)
                final_url, final_payload = poll_result(remove_bg_submit, "image", f"{frame_path.name} image_remove_bg variant {variant_no}")
                log(f"      ✅ image_remove_bg 变体 {variant_no}/3 成功: {final_url}")

                generated_square_path = crop_to_square(image_url)
                removed_bg_square_path = crop_to_square(final_url)
                square_image_path = removed_bg_square_path
                log(f"      ✂️ 1:1 后处理完成 变体 {variant_no}/3: generated={generated_square_path}, removed_bg={removed_bg_square_path}")

                variant_result = {
                    "url": image_url,
                    "removed_bg_url": final_url,
                }
                generated_variants.append(variant_result)
            except Exception as exc:
                error_message = f"{type(exc).__name__}: {exc}"
                variant_errors.append({
                    "variant_idx": variant_idx,
                    "error": error_message,
                })
                log(f"      ❌ 变体 {variant_no}/3 生成失败: {error_message}")

        result["generated_variants"] = generated_variants
        result["variant_errors"] = variant_errors
        if generated_variants:
            result["image_generate_url"] = generated_variants[0].get("url")
            result["status"] = "full_pipeline_completed"
            log(f"      ✅ {frame_path.name} 完成 {len(generated_variants)}/3 张变体")
        else:
            result["status"] = "failed"
            result["error"] = "3 张变体全部生成失败"
            log(f"      ❌ {frame_path.name} 3 张变体全部生成失败")
        return result
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = str(exc)
        log(f"      ❌ {frame_path.name} 失败: {exc}")
        return result
    finally:
        result["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get_frames() -> List[Path]:
    if not FRAME_DIR.exists():
        raise FileNotFoundError(f"找不到 frames 目录: {FRAME_DIR}")
    frames = sorted(path for path in FRAME_DIR.iterdir() if path.is_file())
    if not frames:
        raise FileNotFoundError(f"frames 目录为空: {FRAME_DIR}")
    return frames


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_meme_candidates_json(env: str = "prod") -> Path:
    env_value = (env or "prod").strip().lower()
    if env_value == "prod":
        return MEME_CANDIDATES_JSON
    if env_value == "dev":
        return MEME_CANDIDATES_DEV_JSON
    raise ValueError(f"Unsupported env: {env}. Use prod or dev.")


def load_meme_candidates(json_path: Path) -> Dict[str, Any]:
    if not json_path.exists():
        raise FileNotFoundError(f"找不到 meme candidates JSON: {json_path}")
    with json_path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict):
        raise ValueError("meme_candidates.json 顶层必须是对象")
    candidates = data.get("candidates") or data.get("items")
    if not isinstance(candidates, list):
        raise ValueError("meme_candidates.json 缺少 candidates/items 列表")
    return data


def save_meme_candidates(data: Dict[str, Any], json_path: Path) -> None:
    data["last_updated"] = utc_now_iso()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate meme stickers from pending candidates")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod", help="数据环境：prod 读写正式 JSON，dev 读写测试 JSON")
    parser.add_argument("--limit", type=int, default=5, help="每次最多生图的条数，默认 5 条")
    return parser.parse_args()


def resolve_frame_path(frame_png_path: Any) -> Optional[Path]:
    if not isinstance(frame_png_path, str) or not frame_png_path.strip():
        return None
    value = frame_png_path.strip()
    if value.startswith("/images/meme/frames/"):
        return FRAME_DIR / Path(value).name
    raw_path = Path(value)
    if raw_path.is_absolute():
        return raw_path
    candidate = BASE_DIR / raw_path
    if candidate.exists():
        return candidate
    return FRAME_DIR / raw_path.name


def pending_candidate_frames(candidates_data: Dict[str, Any]) -> List[Tuple[Dict[str, Any], Path]]:
    pending: List[Tuple[Dict[str, Any], Path]] = []
    skipped_statuses = {"rejected", "needs_review", "generated", "completed"}
    for idx, item in enumerate(candidates_data.get("candidates") or candidates_data.get("items", []), start=1):
        if item.get("status") != "pending":
            log(f"⏭️ 跳过：{item.get('short_name') or item.get('name') or item.get('frame')} | status={item.get('status')}（只处理 status:pending）")
        if not isinstance(item, dict):
            log(f"⚠️ warning: 第 {idx} 条候选不是对象，跳过")
            continue
        status = item.get("status")
        if status in skipped_statuses:
            continue
        if status != "pending":
            continue
        frame_png_path = item.get("frame_png_path")
        frame_path = resolve_frame_path(frame_png_path)
        if frame_path is None:
            log(f"⚠️ warning: 第 {idx} 条 pending 候选缺少 frame_png_path，跳过")
            continue
        if not frame_path.exists() or not frame_path.is_file():
            log(f"⚠️ warning: 第 {idx} 条 pending 候选的 frame 文件不存在: {frame_path}，跳过")
            continue
        pending.append((item, frame_path))
    return pending


def main() -> int:
    global JWT_TOKEN
    args = parse_args()
    meme_json = resolve_meme_candidates_json(args.env)
    log(f"数据环境：{args.env}，目标 JSON：{meme_json}")
    new_token = get_jwt_token()
    if new_token:
        JWT_TOKEN = new_token
        log("✅ 成功自动获取最新的 JWT Token")
    else:
        log("⚠️ 自动获取 JWT Token 失败，将使用脚本中硬编码的 Token 作为备选")
    run_summary: Dict[str, Any] = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_mode": "pending_candidates_only",
        "frames": [],
    }
    try:
        candidates_data = load_meme_candidates(meme_json)
        pending_frames = pending_candidate_frames(candidates_data)
        if args.limit and args.limit > 0:
            pending_frames = pending_frames[:args.limit]
            log(f"📌 --limit={args.limit}，本次最多处理 {len(pending_frames)} 条")
        if not pending_frames:
            log("✅ 没有 status == pending 且 frame 文件有效的候选条目，本次无需生图")
            save_results(run_summary)
            flush_log()
            return 0

        log(f"📁 发现待生图 pending 候选 {len(pending_frames)} 条: {[frame.name for _, frame in pending_frames]}")
        for candidate, frame_path in pending_frames:
            try:
                result = process_frame(frame_path, full_pipeline=True)
                run_summary["frames"].append(result)
                generated_variants = result.get("generated_variants") or []
                if generated_variants:
                    candidate["status"] = "generated"
                    candidate["generated_at"] = utc_now_iso()
                    candidate.pop("generate_error", None)
                    candidate["generated_variants"] = [
                        {
                            "url": item.get("url"),
                            "removed_bg_url": item.get("removed_bg_url"),
                        }
                        for item in generated_variants
                        if item.get("url")
                    ]
                    log(f"✅ 已生成并回写 status=generated: {frame_path.name} | variants={len(generated_variants)}/3")
                else:
                    candidate["status"] = "generate_failed"
                    candidate["generate_error"] = result.get("error") or "3 张变体全部生成失败"
                    log(f"❌ {frame_path.name} 3 张变体全部失败，已回写 status=generate_failed")
            except Exception as exc:
                error_message = f"{type(exc).__name__}: {exc}"
                log(f"❌ 生图失败：{candidate.get('frame_filename', candidate.get('id', '?'))} | {error_message}")
                candidate["status"] = "generate_failed"
                candidate["generate_error"] = error_message
                run_summary["frames"].append({
                    "frame": frame_path.name,
                    "status": "generate_failed",
                    "error": error_message,
                })
            save_results(run_summary)
            save_meme_candidates(candidates_data, meme_json)
            flush_log()

        success_count = sum(1 for item in run_summary["frames"] if item.get("generated_variants"))
        failed_count = sum(1 for item in run_summary["frames"] if item.get("status") == "generate_failed")
        log(f"✅ 完成：成功 {success_count}/{len(run_summary['frames'])} 个 pending 候选，失败 {failed_count} 个（已标记 generate_failed）")
        save_results(run_summary)
        save_meme_candidates(candidates_data, meme_json)
        flush_log()
        return 0
    except Exception as exc:
        run_summary["error"] = str(exc)
        log(f"❌ 运行失败: {exc}")
        save_results(run_summary)
        flush_log()
        return 1


if __name__ == "__main__":
    sys.exit(main())
