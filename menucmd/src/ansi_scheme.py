from dataclasses import dataclass
from typing import Optional
from .colors import Colors


@dataclass
class AnsiConfig():
    name: Optional[str] = Colors.BOLD
    item_key: Optional[str] =  Colors.BLINK + Colors.BOLD
    item_key_dash: Optional[str] = Colors.BOLD
    item_message: Optional[str] = Colors.ITALIC
    empty_message: Optional[str] = Colors.WHITE
    invalid_selection: Optional[str] = Colors.LIGHT_RED + Colors.ITALIC

