#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import sys
import time

from meme_scrapers import (
    FRAMES_DIR,
    MEME_JSON,
    resolve_meme_json,
    GiphyScraper,
    RedditScraper,
    dedup_items,
    load_candidates,
    next_index,
    normalize_item,
    process_media,
    save_candidates,
)

SCRAPER_REGISTRY = {
    "giphy": GiphyScraper,
    "reddit": RedditScraper,
}
DEFAULT_LIMIT = 10
DEFAULT_PLATFORMS = "giphy,reddit"
COOLDOWN_DAYS = 7


def log(message: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape meme candidates from Giphy and Reddit")
    parser.add_argument("--platforms", default=DEFAULT_PLATFORMS, help="逗号分隔的平台列表，默认 giphy,reddit")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"每个平台抓取数量，默认 {DEFAULT_LIMIT}")
    parser.add_argument("--dry-run", action="store_true", help="不写 JSON，只打印抓到的条目")
    parser.add_argument("--skip-media", action="store_true", help="跳过下载和截帧")
    parser.add_argument("--headed", action="store_true", help="以可视浏览器模式运行，便于调试")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod", help="数据环境：prod 写正式 JSON，dev 写测试 JSON")
    return parser.parse_args()


def parse_platforms(raw_value: str) -> list[str]:
    platforms = [part.strip().lower() for part in (raw_value or "").split(",") if part.strip()]
    if not platforms:
        platforms = parse_platforms(DEFAULT_PLATFORMS)
    unsupported = [platform for platform in platforms if platform not in SCRAPER_REGISTRY]
    if unsupported:
        raise ValueError(f"Unsupported platforms: {', '.join(unsupported)}")
    return platforms


def build_scraper(platform: str, headed: bool):
    return SCRAPER_REGISTRY[platform](headed=headed)


def preview_payload(items: list[dict], platforms: list[str]) -> dict:
    return {
        "platforms": platforms,
        "count": len(items),
        "items": [
            {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "source_url": item.get("source_url", ""),
            }
            for item in items
        ],
    }


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def apply_cooldown(existing_items: list[dict], normalized_items: list[dict]) -> tuple[list[dict], int, int]:
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    cooldown_threshold = now - timedelta(days=COOLDOWN_DAYS)
    existing_by_native_id = {
        item.get("native_id"): item
        for item in existing_items
        if item.get("native_id")
    }

    new_items: list[dict] = []
    skipped_count = 0
    refreshed_count = 0
    for item in normalized_items:
        native_id = item.get("native_id")
        existing_item = existing_by_native_id.get(native_id)
        if not native_id or existing_item is None:
            item["status"] = item.get("status") or "scraped"
            item["last_seen_at"] = item.get("last_seen_at") or now_iso
            new_items.append(item)
            continue

        last_seen_at = parse_timestamp(existing_item.get("last_seen_at"))
        if last_seen_at and last_seen_at >= cooldown_threshold:
            skipped_count += 1
            continue

        existing_item["last_seen_at"] = now_iso
        refreshed_count += 1

    return new_items, skipped_count, refreshed_count


def main() -> int:
    args = parse_args()
    try:
        platforms = parse_platforms(args.platforms)
        limit = max(args.limit, 1)
        meme_json = resolve_meme_json(args.env)
        log(f"数据环境：{args.env}，目标 JSON：{meme_json}")
        existing_data = load_candidates(meme_json)
        existing_items = list(existing_data.get("items", []))
        start_index = next_index(existing_items)

        raw_items = []
        for platform in platforms:
            log(f"开始抓取 {platform}（limit={limit}）")
            scraper = build_scraper(platform, headed=args.headed)
            platform_items = scraper.scrape(limit=limit)
            raw_items.extend(platform_items)
            log(f"{platform} 抓取完成：{len(platform_items)} 条")

        normalized_items = [normalize_item(raw, start_index + index) for index, raw in enumerate(raw_items)]
        deduped_items = dedup_items(existing_items, normalized_items)
        new_items, cooldown_skipped_count, refreshed_count = apply_cooldown(existing_items, deduped_items)
        for offset, item in enumerate(new_items):
            item["index"] = start_index + offset

        log(
            f"normalize 完成：{len(normalized_items)} 条；基础去重后 {len(deduped_items)} 条；"
            f"冷却期跳过 {cooldown_skipped_count} 条；刷新 last_seen_at {refreshed_count} 条；新增 {len(new_items)} 条"
        )

        if args.dry_run:
            print(json.dumps(preview_payload(normalized_items[:limit], platforms), ensure_ascii=False, indent=2))
            log("dry-run 模式：未写入 JSON，未下载媒体")
            return 0

        processed_items = new_items
        if args.skip_media:
            log("skip-media 模式：跳过下载与截帧")
        else:
            FRAMES_DIR.mkdir(parents=True, exist_ok=True)
            processed_items = [process_media(item, FRAMES_DIR) for item in new_items]
            log(f"媒体处理完成：{len(processed_items)} 条")

        existing_data["items"] = existing_items + processed_items
        existing_data["source"] = ",".join(platforms)
        save_candidates(existing_data, meme_json)
        log(f"写入完成：{meme_json}")
        return 0
    except Exception as exc:
        log(f"ERROR {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
