from ..src.menucmd import Menu

def open_menu(menu: Menu, arg = None):
    """Open menu in func chain"""
    return Menu.__RUNMENU__(menu, arg)

def open_self(arg = None): 
    return Menu.__RUNSELF__(arg)

def to_menu(menu: Menu):
    """Open menu in Menu.*_to functions"""
    return lambda arg: open_menu(menu, arg)