from dataclasses import dataclass
from typing import Optional


@dataclass
class BlogMessage:
    id: Optional[int]
    title: str
    content: str
