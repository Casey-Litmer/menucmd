from dataclasses import dataclass, fields
from typing import Any, Optional


@dataclass 
class BaseData:
    def __iter__(self):
        for f in fields(self):
            yield getattr(self, f.name)


@dataclass
class Return(BaseData):
    val: Optional[Any] = None
    code: Optional[str] = None
    menu: Optional[str] = None
    err: Optional[Any] = None
    

@dataclass
class MenuEvalScope(BaseData):
    chain: list
    arg: Any
    tracked_attributes: dict
