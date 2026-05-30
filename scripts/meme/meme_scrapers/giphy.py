from __future__ import annotations

import random
import re
from typing import Any
from urllib.parse import quote, urlparse

from .base import BaseScraper, RawMemeItem

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

GIPHY_REACTIONS_URL = "https://giphy.com/reactions"
GIPHY_TRENDING_URL = "https://giphy.com/categories/memes"
GIPHY_EXPLORE_URL = "https://giphy.com/explore/meme"
REQUEST_TIMEOUT_MS = 45000
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
EMOTION_KEYWORDS = [
    # P0 - 高频核心情绪
    "laughing", "lol reaction", "dying laughing",
    "shocked", "mind blown", "oh my god reaction",
    "awkward", "cringe", "embarrassed",
    "eye roll", "ugh reaction", "not impressed",
    # P1 - 常用情绪
    "crying", "devastated", "sobbing",
    "smug", "deal with it", "proud",
    "confused", "what reaction", "huh",
    "excited", "can't wait", "hyped",
    "heart eyes", "love it", "cute reaction",
    # P2 - 补充情绪
    "bored", "whatever", "over it",
    "nervous", "stressed", "anxiety",
    "you got this", "cheering", "supportive",
    # 梗文化/反应类
    "reaction meme", "when you realize", "plot twist reaction",
    "relatable", "mood", "same energy",
    # 社交怼人/暗讽
    "side eye", "shade", "judging you", "blank stare", "unimpressed",
    # 胜利/主角能量
    "slay", "main character", "iconic", "dramatic reaction",
    # 自嘲/认同
    "self-deprecating", "humble brag", "conflicted",
]


def clean_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_media_url(url: str | None) -> str:
    if not url:
        return ""
    value = url.strip()
    if value.startswith("//"):
        value = f"https:{value}"
    return value


def title_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    last = path.split("/")[-1] if path else ""
    parts = [part for part in last.split("-") if part]
    if len(parts) > 1 and re.fullmatch(r"[A-Za-z0-9]{5,}", parts[-1] or ""):
        parts = parts[:-1]
    return clean_text(" ".join(part.capitalize() for part in parts)) or "Giphy Meme"


def giphy_direct_url(giphy_id: str, variant: str = "giphy.gif") -> str:
    return f"https://media.giphy.com/media/{giphy_id}/{variant}" if giphy_id else ""


def giphy_native_id_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    if "/media/" in path:
        token = path.split("/media/", 1)[1].split("/", 1)[0]
    else:
        parts = path.split("-")
        token = parts[-1] if parts else ""
    token = re.sub(r"[^A-Za-z0-9]", "", token)
    if token and len(token) >= 5:
        return token
    fallback = re.sub(r"[^a-zA-Z0-9]+", "_", url.lower()).strip("_")
    return (fallback or "giphy_meme")[-48:]


def extract_giphy_nodes(page: Any, limit: int) -> list[dict[str, str]]:
    api_items: list[dict[str, str]] = []

    def capture_response(response: Any) -> None:
        try:
            url = response.url
            if "api.giphy.com" not in url or response.status >= 400:
                return
            payload = response.json()
            data = payload.get("data", [])
            if isinstance(data, dict):
                data = [data]
            for entry in data or []:
                if not isinstance(entry, dict):
                    continue
                native_id = clean_text(entry.get("id"))
                images = entry.get("images") or {}
                source_url = normalize_media_url(
                    ((images.get("original") or {}).get("url"))
                    or ((images.get("downsized") or {}).get("url"))
                )
                if not source_url and native_id:
                    source_url = giphy_direct_url(native_id)
                if not source_url:
                    continue
                api_items.append(
                    {
                        "source_url": source_url,
                        "cover_url": normalize_media_url(((images.get("fixed_width_small") or {}).get("url")) or source_url),
                        "title": clean_text(entry.get("title")) or "Giphy Meme",
                        "native_id": native_id or giphy_native_id_from_url(source_url),
                    }
                )
        except Exception:
            return

    page.on("response", capture_response)
    page.wait_for_load_state("networkidle", timeout=REQUEST_TIMEOUT_MS)
    for _ in range(4):
        page.mouse.wheel(0, 1800)
        page.wait_for_timeout(900)

    raw_items = page.evaluate(
        """
        (limit) => {
          const nodes = Array.from(document.querySelectorAll('a[href*="/gifs/"], a[href*="/stickers/"], img[src*="giphy.com/media"], img[src*="media.giphy.com/media"]'));
          const items = [];
          const seen = new Set();
          for (const node of nodes) {
            const anchor = node.tagName === "A" ? node : node.closest("a");
            const image = node.tagName === "IMG" ? node : (anchor?.querySelector("img") || node.querySelector?.("img"));
            let href = anchor?.href || "";
            const cover = image?.currentSrc || image?.src || image?.getAttribute("data-src") || "";
            if (!href && cover) {
              const match = cover.match(/\/media\/([^\/]+)\//);
              if (match) href = "https://giphy.com/gifs/" + match[1];
            }
            const idMatch = (cover || href).match(/\/media\/([^\/]+)\//);
            const directUrl = idMatch ? `https://media.giphy.com/media/${idMatch[1]}/giphy.gif` : "";
            if (!href || seen.has(href)) continue;
            if (!href.includes("/gifs/") && !href.includes("/stickers/") && !directUrl) continue;
            const title = (image?.alt || anchor?.getAttribute("aria-label") || anchor?.getAttribute("title") || anchor?.textContent || "").trim();
            seen.add(href);
            items.push({ source_url: directUrl || cover || href, title, cover_url: cover });
            if (items.length >= limit) break;
          }
          return items;
        }
        """,
        limit,
    )

    merged_raw_items = [*api_items, *(raw_items or [])]
    items: list[dict[str, str]] = []
    seen_native_ids: set[str] = set()
    for raw in merged_raw_items:
        source_url = normalize_media_url(raw.get("source_url"))
        native_id = clean_text(raw.get("native_id")) or giphy_native_id_from_url(source_url)
        if not source_url and native_id:
            source_url = giphy_direct_url(native_id)
        if not source_url or not native_id or native_id in seen_native_ids:
            continue
        if "media.giphy.com/media" not in source_url:
            source_url = giphy_direct_url(native_id)
        seen_native_ids.add(native_id)
        cover_url = normalize_media_url(raw.get("cover_url")) or giphy_direct_url(native_id, "giphy_s.gif")
        title = clean_text(raw.get("title")) or title_from_url(source_url)
        items.append(
            {
                "source_url": source_url,
                "cover_url": cover_url,
                "title": title,
                "native_id": native_id,
                "page_url": f"https://giphy.com/gifs/{native_id}",
            }
        )
    return items


class GiphyScraper(BaseScraper):
    source_platform = "giphy"

    def _scrape_urls(self, urls: list[str], limit: int) -> list[dict[str, str]]:
        if sync_playwright is None:
            raise RuntimeError("Playwright is not installed.")

        extracted: list[dict[str, str]] = []
        seen_native_ids: set[str] = set()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not self.headed)
            page = browser.new_page(
                viewport={"width": 1440, "height": 1200},
                user_agent=DEFAULT_USER_AGENT,
            )
            try:
                for url in urls:
                    page.goto(url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT_MS)
                    for item in extract_giphy_nodes(page, limit=max(limit, 1)):
                        native_id = item.get("native_id", "")
                        if not native_id or native_id in seen_native_ids:
                            continue
                        seen_native_ids.add(native_id)
                        extracted.append(item)
                        if len(extracted) >= max(limit, 1):
                            return extracted
            finally:
                browser.close()
        return extracted

    def _to_raw_items(self, items: list[dict[str, str]], limit: int) -> list[RawMemeItem]:
        return [
            RawMemeItem(
                source_platform=self.source_platform,
                source_url=item["source_url"],
                name=item["title"],
                description=item["title"],
                native_id=item["native_id"],
                page_url=item.get("page_url", ""),
                popularity_signal={},
                extra={
                    "cover_url": item.get("cover_url", ""),
                    **({"emotion_keyword": item["emotion_keyword"]} if item.get("emotion_keyword") else {}),
                    **({"giphy_source": item["giphy_source"]} if item.get("giphy_source") else {}),
                },
            )
            for item in items[: max(limit, 1)]
        ]

    def scrape_reactions(self, limit: int = 50) -> list[RawMemeItem]:
        items = self._scrape_urls([GIPHY_REACTIONS_URL], limit=max(limit, 1))
        for item in items:
            item["giphy_source"] = "reactions"
        return self._to_raw_items(items, limit)

    def scrape_trending(self, limit: int = 20) -> list[RawMemeItem]:
        items = self._scrape_urls([GIPHY_TRENDING_URL, GIPHY_EXPLORE_URL], limit=max(limit, 1))
        for item in items:
            item["giphy_source"] = "trending"
        return self._to_raw_items(items, limit)

    def scrape_by_keywords(
        self,
        keywords: list[str] | None = None,
        limit_per_keyword: int = 5,
    ) -> list[RawMemeItem]:
        if sync_playwright is None:
            raise RuntimeError("Playwright is not installed.")

        search_keywords = keywords or random.sample(EMOTION_KEYWORDS, k=min(3, len(EMOTION_KEYWORDS)))
        extracted: list[dict[str, str]] = []
        seen_native_ids: set[str] = set()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not self.headed)
            page = browser.new_page(
                viewport={"width": 1440, "height": 1200},
                user_agent=DEFAULT_USER_AGENT,
            )
            try:
                for keyword in search_keywords:
                    url = f"https://giphy.com/search/{quote(keyword)}"
                    page.goto(url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT_MS)
                    keyword_count = 0
                    for item in extract_giphy_nodes(page, limit=max(limit_per_keyword * 2, 1)):
                        native_id = item.get("native_id", "")
                        if not native_id or native_id in seen_native_ids:
                            continue
                        seen_native_ids.add(native_id)
                        item["emotion_keyword"] = keyword
                        item["giphy_source"] = "keywords"
                        extracted.append(item)
                        keyword_count += 1
                        if keyword_count >= max(limit_per_keyword, 1):
                            break
            finally:
                browser.close()

        return self._to_raw_items(extracted, len(extracted))

    def scrape(self, limit: int, sources: list[str] | None = None) -> list[RawMemeItem]:
        selected_sources = sources or ["reactions", "trending", "keywords"]
        items: list[RawMemeItem] = []
        seen_native_ids: set[str] = set()

        for source in selected_sources:
            if source == "reactions":
                source_items = self.scrape_reactions(limit=limit)
            elif source == "trending":
                source_items = self.scrape_trending(limit=20)
            elif source == "keywords":
                source_items = self.scrape_by_keywords()
            else:
                continue

            for item in source_items:
                if item.native_id in seen_native_ids:
                    continue
                seen_native_ids.add(item.native_id)
                items.append(item)
                if len(items) >= max(limit, 1):
                    return items

        return items[: max(limit, 1)]
