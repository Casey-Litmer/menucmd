from dataclasses import dataclass
from typing import Any, Optional



@dataclass
class Return:
    val: Optional[Any] = None
    code: Optional[str] = None
    menu: Optional[str] = None
    err: Optional[Any] = None
    
    def __iter__(self):
        return iter((self.val, self.code, self.menu, self.err))
    

