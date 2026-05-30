from __future__ import annotations

import html
import json
import random
import re
from urllib.parse import urlparse

from .base import BaseScraper, RawMemeItem

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

REQUEST_TIMEOUT_MS = 45000
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".gifv", ".webp"}
SUBREDDITS_P0 = ["reactiongifs", "AdviceAnimals"]
SUBREDDITS_P1 = ["memes"]
SUBREDDITS_P2 = ["dankmemes"]


def clean_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clean_url(url: str | None) -> str:
    if not url:
        return ""
    value = html.unescape(url).strip()
    if value.startswith("//"):
        value = f"https:{value}"
    return value


def normalize_media_url(url: str | None) -> str:
    value = clean_url(url)
    if value.lower().endswith(".gifv"):
        value = f"{value[:-5]}.gif"
    return value


def has_supported_extension(url: str) -> bool:
    if not url:
        return False
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def preview_image_url(post: dict) -> str:
    preview = post.get("preview") or {}
    images = preview.get("images") or []
    if not images:
        return ""
    source = images[0].get("source") or {}
    return normalize_media_url(source.get("url"))


class RedditScraper(BaseScraper):
    source_platform = "reddit"

    def scrape(self, limit: int = 5) -> list[RawMemeItem]:
        if sync_playwright is None:
            raise RuntimeError("Playwright is not installed.")

        per_subreddit_limit = max(limit, 1)
        subreddit_pool = SUBREDDITS_P0 + SUBREDDITS_P1
        selected_subreddits = random.sample(subreddit_pool, k=min(3, len(subreddit_pool)))
        fetch_paths = [
            f"/r/{subreddit}.json?sort=top&t=day&limit={max(per_subreddit_limit, 5)}"
            for subreddit in selected_subreddits
        ]

        results = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not self.headed)
            page = browser.new_page(
                viewport={"width": 1440, "height": 1200},
                user_agent=DEFAULT_USER_AGENT,
            )
            try:
                page.goto("https://www.reddit.com/", wait_until="load", timeout=REQUEST_TIMEOUT_MS)
                page.wait_for_timeout(3000)
                for fetch_path in fetch_paths:
                    result = page.evaluate(
                        """
                        async (path) => {
                          const response = await fetch(path, { headers: { "Accept": "application/json" } });
                          return { status: response.status, text: await response.text() };
                        }
                        """,
                        fetch_path,
                    )
                    results.append((fetch_path, result))
            finally:
                browser.close()

        items: list[RawMemeItem] = []
        seen_native_ids: set[str] = set()
        for fetch_path, result in results:
            status = int((result or {}).get("status") or 0)
            if status != 200:
                raise RuntimeError(f"Reddit request failed for {fetch_path}: HTTP {status}")
            payload = json.loads((result or {}).get("text") or "{}")

            children = ((payload or {}).get("data") or {}).get("children") or []
            subreddit_count = 0
            for child in children:
                post = (child or {}).get("data") or {}
                image_dest = normalize_media_url(post.get("url_overridden_by_dest"))
                if not has_supported_extension(image_dest):
                    continue

                native_id = clean_text(post.get("id")) or clean_text(post.get("name"))
                if not native_id or native_id in seen_native_ids:
                    continue
                seen_native_ids.add(native_id)

                permalink = post.get("permalink") or ""
                source_url = image_dest
                name = clean_text(post.get("title")) or "Reddit Meme"
                items.append(
                    RawMemeItem(
                        source_platform=self.source_platform,
                        source_url=source_url,
                        name=name,
                        description=name,
                        native_id=native_id,
                        popularity_signal={
                            "score": int(post.get("score") or 0),
                            "num_comments": int(post.get("num_comments") or 0),
                            "subreddit": clean_text(post.get("subreddit")),
                        },
                        extra={
                            "permalink": permalink,
                            "url_overridden_by_dest": image_dest,
                            "post_url": normalize_media_url(post.get("url")),
                            "subreddit": clean_text(post.get("subreddit")),
                        },
                    )
                )
                subreddit_count += 1
                if subreddit_count >= per_subreddit_limit:
                    break
        return items
