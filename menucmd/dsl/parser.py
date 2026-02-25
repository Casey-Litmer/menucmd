from ..src.builtins import *
from .menu_dict import MenuDict
from .lines_to_dict import lines_to_dict
from .dict_to_objs import dict_to_objs

#==================================================================================

def build_menus(file: str) -> MenuDict:
    """Convert .mcmd file to attributable dict of menus"""

    #Get text
    with open(file) as f:
        lines = f.readlines()
    f.close()

    #Covert to dict
    struct_ = lines_to_dict(lines)
    #Convert to MenuDict
    menus = dict_to_objs(struct_)

    return menus