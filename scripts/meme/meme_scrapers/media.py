from __future__ import annotations

import math
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageSequence, ImageStat

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def download_media(url: str, dest_path: Path) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        dest_path.write_bytes(response.read())
    return dest_path


def detect_media_type(file_path: Path) -> dict[str, object]:
    with Image.open(file_path) as image:
        n_frames = int(getattr(image, "n_frames", 1) or 1)
        is_animated = bool(getattr(image, "is_animated", False) or n_frames > 1)
        fmt = (image.format or file_path.suffix.lstrip(".") or "unknown").upper()
    return {"is_animated": is_animated, "n_frames": n_frames, "format": fmt}


def _frame_score(image: Image.Image) -> float:
    rgba = image.convert("RGBA")
    sample = rgba.copy()
    sample.thumbnail((160, 160))
    alpha = sample.getchannel("A")
    alpha_values = list(alpha.getdata())
    total_pixels = max(len(alpha_values), 1)
    opaque_pixels = sum(1 for value in alpha_values if value > 0)
    opaque_ratio = opaque_pixels / total_pixels
    if opaque_ratio < 0.01:
        return -1.0

    mask = alpha.point(lambda value: 255 if value > 0 else 0)
    rgb = sample.convert("RGB")
    stat = ImageStat.Stat(rgb, mask=mask)
    variance = sum(stat.var) / max(len(stat.var), 1)
    return (opaque_ratio * 1000.0) + math.sqrt(max(variance, 0.0))


def extract_best_frame(input_path: Path, output_path: Path) -> dict[str, object]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        frame_count = min(int(getattr(image, "n_frames", 1) or 1), 20)
        canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
        best_frame_index = 0
        best_score = float("-inf")
        best_frame = None
        fallback_frame = None

        for frame_index, frame in enumerate(ImageSequence.Iterator(image)):
            if frame_index >= frame_count:
                break
            composed = Image.alpha_composite(canvas, frame.convert("RGBA"))
            if fallback_frame is None:
                fallback_frame = composed.copy()
            score = _frame_score(composed)
            if score > best_score:
                best_score = score
                best_frame_index = frame_index
                best_frame = composed.copy()
            canvas = composed

        selected = best_frame or fallback_frame or image.convert("RGBA")
        selected.save(output_path, format="PNG")
    return {"selected_frame": best_frame_index, "output_path": str(output_path)}


def _suffix_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix else ".bin"


def process_media(item: dict, frames_dir: Path) -> dict:
    updated = dict(item)
    item_id = updated.get("id", "meme")
    output_path = frames_dir / f"{item_id}.png"
    updated["frame_png_path"] = f"/images/meme/frames/{item_id}.png"
    if output_path.exists():
        return updated

    media_url = updated.get("raw_gif_url") or updated.get("raw_image_url")
    if not media_url:
        return updated

    download_dir = frames_dir / ".downloads"
    download_path = download_dir / f"{item_id}{_suffix_from_url(str(media_url))}"

    try:
        download_media(str(media_url), download_path)
        media_info = detect_media_type(download_path)
        updated["media_type"] = "animated" if media_info["is_animated"] else "static"

        if media_info["is_animated"]:
            extract_best_frame(download_path, output_path)
        else:
            with Image.open(download_path) as image:
                image.convert("RGBA").save(output_path, format="PNG")
    finally:
        if download_path.exists():
            download_path.unlink()
    return updated
