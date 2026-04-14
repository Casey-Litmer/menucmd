from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfigColors:
    settings_color: Optional[str] = None
    error_color: Optional[str] = None
    message_color: Optional[str] = None
    history_color: Optional[str] = None