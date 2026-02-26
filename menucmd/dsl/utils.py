from ..builtins.builtins import *
import inspect
from .menu_dict import MenuDict


# SHORTHANDS
result = Menu.result
kwargs = Menu.kwargs
self = Menu.self
B = Bind


def convert_static_attr_types(static_attrs: dict) -> None:
    """Converts Non-String types"""
    for key, val in static_attrs.items():
        if key not in { 'Colors' }:
            static_attrs[key] = eval(val)

    if static_attrs.get('Colors'):
        # Rename key for menu args
        static_attrs['colors'] = convert_colors(static_attrs['Colors'], "Menu")
        del static_attrs['Colors']


def convert_colors(colors: dict, block: str) -> MenuColors | ItemColors:
    """Evaluates ANSI color schemes"""
    scheme = {'Menu': MenuColors, 'Item': ItemColors}[block]
    return scheme(**dict([k, eval(v)] for k, v in colors.items()))


def retrieve_globals(target_globals):
    """Adds globals from where the .mcmd file is loaded."""
    caller_globals = inspect.stack()[3].frame.f_globals
    target_globals.update(caller_globals)


def cannonize_menu_ids(menus: MenuDict, target_globals):
    """Adds menu to global scope"""
    for menu_id, menu in menus.items():
        target_globals[menu_id] = menu