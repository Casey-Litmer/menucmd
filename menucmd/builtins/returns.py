from ..src.menu_return import Return
from ..src.menucmd import Menu


def open_menu(menu: str, arg = None):
    """Open menu in func chain"""
    return Return(val = arg, code = "MENU", menu = menu)

def to_menu(menu: str):
    """Open menu in Menu.*_to functions"""
    return lambda arg: Return(val = arg, code = "MENU", menu = menu)

to_self = lambda arg: Return(arg, code="CONT")