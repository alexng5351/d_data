from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawMemeItem:
    source_platform: str
    source_url: str
    name: str
    description: str = ""
    raw_image_url: str = ""
    raw_gif_url: str = ""
    native_id: str = ""
    popularity_signal: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


class BaseScraper(ABC):
    source_platform: str

    def __init__(self, headed: bool = False) -> None:
        self.headed = headed

    @abstractmethod
    def scrape(self, limit: int) -> list[RawMemeItem]:
        raise NotImplementedError
