from dataclasses import dataclass
from .ansi_scheme import ItemColors
from typing import Optional, Any


@dataclass
class Item():
    key: str
    message: str
    funcs: list[tuple[Any, Any]]
    colors: Optional[ItemColors] = None
