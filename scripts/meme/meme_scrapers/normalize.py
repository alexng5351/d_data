from __future__ import annotations

import re
from datetime import datetime, timezone

from .base import RawMemeItem


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def slugify(text: str | None, fallback: str = "meme") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", (text or "").lower()).strip("_")
    return slug or fallback


def normalize_item(raw: RawMemeItem, index: int) -> dict:
    platform = clean_text(raw.source_platform).lower() or "unknown"
    native_id = clean_text(raw.native_id) or slugify(raw.source_url or raw.name, fallback=platform)
    item_id = f"{platform}_{native_id}"
    short_name = raw.extra.get("short_name") if isinstance(raw.extra, dict) else ""
    short_name = clean_text(short_name) or clean_text(raw.name)
    return {
        "id": item_id,
        "name": clean_text(raw.name),
        "short_name": short_name,
        "description": clean_text(raw.description),
        "source_platform": platform,
        "source_url": clean_text(raw.source_url),
        "page_url": clean_text(raw.page_url),
        "raw_gif_url": clean_text(raw.raw_gif_url),
        "raw_image_url": clean_text(raw.raw_image_url),
        "media_type": "unknown",
        "frame_png_path": f"/images/meme/frames/{item_id}.png",
        "popularity_signal": dict(raw.popularity_signal or {}),
        "index": index,
        "status": "scraped",
        "scraped_at": utc_now(),
    }


def dedup_items(existing: list, new_items: list) -> list:
    existing_ids = {item.get("id") for item in existing if isinstance(item.get("id"), str) and item.get("id")}
    existing_urls = {item.get("source_url") for item in existing if isinstance(item.get("source_url"), str) and item.get("source_url")}
    kept: list[dict] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for item in new_items:
        item_id = item.get("id")
        source_url = item.get("source_url")
        if item_id in existing_ids or source_url in existing_urls:
            continue
        if item_id in seen_ids or source_url in seen_urls:
            continue
        kept.append(item)
        if isinstance(item_id, str) and item_id:
            seen_ids.add(item_id)
        if isinstance(source_url, str) and source_url:
            seen_urls.add(source_url)
    return kept
