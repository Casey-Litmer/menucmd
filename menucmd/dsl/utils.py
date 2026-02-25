from ..src.builtins import *
import inspect
from .menu_dict import MenuDict


# SHORTHANDS
result = Menu.result
kwargs = Menu.kwargs
self = Menu.self
B = Bind


def convert_attr_types(static_attrs: dict) -> None:
    """Converts Non-String types"""
    if static_attrs.get('clear_readout'):
        static_attrs['clear_readout'] = {'True': True, 'False': False}[static_attrs['clear_readout']]
    if static_attrs.get('arg_to_first'):
        static_attrs['arg_to_first'] = {'True': True, 'False': False}[static_attrs['arg_to_first']]


def retrieve_globals(target_globals):
    """Adds globals from where the .mcmd file is loaded."""
    caller_globals = inspect.stack()[3].frame.f_globals
    target_globals.update(caller_globals)


def cannonize_menu_ids(menus: MenuDict, target_globals):
    """Adds menu to global scope"""
    for menu_id, menu in menus.items():
        target_globals[menu_id] = menu