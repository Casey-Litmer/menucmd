import os
from typing import Optional, Any
from macrolibs.filemacros import get_script_dir
from ..dsl import build_menus, MenuDict
from ..src.colors import Colors
from ..src.menu_return import Return
from ..tests.testing_utils import *


DEBUG_C = {
    'name': Colors.LIGHT_BLUE,
    'result': Colors.FAINT + Colors.ITALIC
}

#==================================================================================

class MenuManager:

    def __init__(self,
                 mcmd: str,
                 base_menu: str,
                 debug: bool = False
                 ):
        self.mcmd = mcmd
        self.base_menu = base_menu
        self.menus = MenuManager.load_mcmd(mcmd)

        self.debug = debug


    def __call__(self, arg: Optional[Any] = None):
        menu = self.menus[self.base_menu]
        _menu = self.base_menu

        while True:

            result = menu(arg)

            if self.debug:
                print(f'{DEBUG_C['name']}RESULT:{Colors.END+ DEBUG_C['result']}', result, Colors.END)
                print(f'    {DEBUG_C['name']}from menu:{Colors.END+ DEBUG_C['result']}', _menu, Colors.END)

            if isinstance(result, Return):
                _val, _code, _menu, _err = tuple(result)
                
                match _err:
                    case None:
                        pass
                match _code:
                    case None:
                        return _val
                    case 'END':
                        return result
                    case 'CONT':
                        # menu runs itself with new value
                        arg = _val
                    case 'MENU':
                        # runs other menu with new value
                        menu = self.menus.get(_menu)
                        if not menu:
                            raise ReferenceError(f'{_menu} does not exist')
                        arg = _val
                    case _:
                        return _val
            else: 
                return result
                
    #==================================================================================     
    # Debug
    #==================================================================================     


            
    #==================================================================================
    # Utils
    #==================================================================================

    @staticmethod
    def load_mcmd(file_name: str) -> MenuDict:
        return build_menus(os.path.join(get_script_dir(), file_name))
        
    
    