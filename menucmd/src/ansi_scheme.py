from dataclasses import dataclass, replace, asdict
from typing import Optional
from .colors import Colors


@dataclass
class ItemColors():
    key: Optional[str] = None
    dash: Optional[str] = None
    message: Optional[str] = None

@dataclass
class MenuColors(ItemColors):
    name: Optional[str] = Colors.BOLD
    empty_message: Optional[str] = Colors.WHITE
    invalid_key: Optional[str] = Colors.LIGHT_RED + Colors.ITALIC

    # Global Item Defaults
    key: Optional[str] = Colors.BLINK + Colors.BOLD
    dash: Optional[str] = Colors.BOLD
    message: Optional[str] = Colors.ITALIC

    
    def merge(self, other: Optional[ItemColors]) -> "MenuColors":
        if other is None:
            return self
        return replace(self, **{k: v for k, v in asdict(other).items() if v is not None})
