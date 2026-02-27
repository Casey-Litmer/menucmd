from dataclasses import dataclass, replace, asdict
from typing import Optional
from .colors import Colors


@dataclass
class ItemColors:
    key: Optional[str] = None
    dash: Optional[str] = None
    message: Optional[str] = None

    def merge(self, other: Optional["MenuColors | ItemColors"]) -> "ItemColors":
        if other is None:
            return self
        return replace(self, **{k: v for k, v in asdict(other).items() \
            if v is not None})


@dataclass
class MenuColors(ItemColors):
    name: Optional[str] = None
    empty_message: Optional[str] = None
    invalid_key: Optional[str] = None

    def merge(self, other: Optional["MenuColors | ItemColors"]) -> "MenuColors":
        if other is None:
            return self
        return replace(self, **{k: v for k, v in asdict(other).items() if v is not None})
