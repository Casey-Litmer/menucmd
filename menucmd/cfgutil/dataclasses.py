from dataclasses import dataclass, field
from typing import Any



@dataclass
class BaseData:
    pass


@dataclass
class CommandHistoryData(BaseData):
    command_history: list[Any] = field(default_factory=list)
    history_length: int = 6


@dataclass
class DirectoryData(BaseData):
    dirs: dict[str, tuple[str, str]] = field(default_factory=dict)


