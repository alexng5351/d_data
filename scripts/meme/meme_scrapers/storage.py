from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MEME_DATA_DIR = BASE_DIR / "public" / "data" / "meme"
MEME_JSON = MEME_DATA_DIR / "meme_candidates.json"
MEME_DEV_JSON = MEME_DATA_DIR / "meme_candidates_dev.json"
FRAMES_DIR = BASE_DIR / "public" / "images" / "meme" / "frames"


def resolve_meme_json(env: str = "prod") -> Path:
    env_value = (env or "prod").strip().lower()
    if env_value == "prod":
        return MEME_JSON
    if env_value == "dev":
        return MEME_DEV_JSON
    raise ValueError(f"Unsupported env: {env}. Use prod or dev.")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_candidates(json_path: Path) -> dict[str, Any]:
    if not json_path.exists():
        return {"last_updated": utc_now(), "source": "meme_scrapers", "items": []}
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"last_updated": utc_now(), "source": "meme_scrapers", "items": data}
    if not isinstance(data, dict):
        raise TypeError(f"Unsupported JSON root type: {type(data).__name__}")
    items = data.get("items")
    if items is None:
        data["items"] = []
    elif not isinstance(items, list):
        raise TypeError("meme_candidates.json field items must be a list")
    return data


def save_candidates(data: dict[str, Any], json_path: Path) -> None:
    payload = dict(data)
    payload["last_updated"] = utc_now()
    payload.setdefault("items", [])
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")


def next_index(items: list) -> int:
    indexes = [item.get("index") for item in items if isinstance(item, dict) and isinstance(item.get("index"), int)]
    return (max(indexes) + 1) if indexes else 1
