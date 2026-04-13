from macrolibs.typemacros import dict_intersect
from .utils import *


# CONSTANTS
MENU_ATTRS = {
    "name": '',
    "clear_readout": '',
    "arg_to_first": '',
    "empty_message": '',
    "exit_message": '',
    "exit_key": '',
    "Colors": '',
    "ExitColors": '',
    "Item": '',
    "arg_to": '',
    "exit_to": '',
    "end_to": '',
    "escape_to": '',
}

DEFAULT_IMPORTS = {
    "menucmd": ["*"],
}

DEFAULT_CONSTANTS = {
    "result": "Menu.result",
    "kwargs": "Menu.kwargs",
    "self": "Menu.self",
    "B": "Bind",
    "C": "Colors",
}

#==================================================================================

def dict_to_py(struct_: dict, imports_: list[str] | dict[str, list[str]]) -> str:
    """
    Converts a dictionary structure of the dsl to a python script string.
    """
    if not "Menu" in struct_:
        raise RuntimeError("'Menu' must be present in the outer struct")
    
    # Get global scope
    retrieve_globals(globals())

    default_imports = _set_default_imports()
    constants = _set_constants()
    imports = _set_imports(imports_)
    default_colors = _set_default_colors(struct_)
    menus, items = _set_menus(struct_)

    py_text = '\n'.join([default_imports, constants, imports, default_colors, menus, items])

    return py_text

#==================================================================================

def _set_default_imports() -> str:
    """
    Returns the default imports for the compiled python script.
    """
    return ''.join([f"from {m} import {", ".join(i)}\n" for m, i in DEFAULT_IMPORTS.items()])


def _set_constants() -> str:
    """
    Returns the default constants for the compiled python script.
    """
    return ''.join([f"{k} = {v}\n" for k, v in DEFAULT_CONSTANTS.items()])


def _set_imports(imports: list[str] | dict[str, list[str]]) -> str:
    """
    Returns the imports for the compiled python script.
    """
    if isinstance(imports, list):
        return ''.join([f"from {m} import *\n" for m in imports])
    else:
        return ''.join([f"from {m} import {", ".join(i)}\n" for m, i in imports.items()])


def _set_default_colors(struct_: dict) -> str:
    """
    Returns the global color settings for the compiled python script.
    """
    colors_str = ""
    if global_colors := struct_.get("Colors"):
        colors_str += f"Menu.set_global_colors(colors = {convert_colors(global_colors, 'Menu', globals())})\n"
    if global_exit_colors := struct_.get("ExitColors"):
        colors_str += f"Menu.set_global_colors(exit_colors = {convert_colors(global_exit_colors, 'ExitColors', globals())})\n"
    return colors_str


def _set_menus(struct_: dict) -> tuple[str, str]:
    """
    Constructs the Menu() initializations and menu.append() calls for the items.
    Returns tuple(menus_str, items_str)
    """
    menus = ""
    items = ""

    for attrs in struct_["Menu"]:
        # Require id
        if not attrs.get('id'):
            raise KeyError("Menu must have an 'id' attribute")
        menu_id = attrs.get("id")

        menu_args = []
        menu_items = ""

        # Compare all attributes defined in dsl script, and only feed into Menu 
        # if it intersects with the blank dict
        static_attrs = dict_intersect(attrs, MENU_ATTRS)

        for key, val in static_attrs.items():
            if key == 'Item':
                menu_items = _set_items(val, menu_id)
            elif key == "Colors":
                colors_str = _set_colors(val, "MenuColors", 4)
                menu_args.append(f"colors = {colors_str}")
            elif key == 'ExitColors':
                colors_str = _set_colors(val, "ItemColors", 4)
                menu_args.append(f"exit_colors = {colors_str}")
            else:
                menu_args.append(f"{key} = {val}")

        menus += " " * 0 + f"{menu_id} = Menu(\n"
        menus += "".join([" " * 4 + f"{arg},\n" for arg in menu_args])
        menus += " " * 0 + ")\n"
        items += " " * 0 + f"{menu_items}"

    return menus, items


def _set_colors(colors_: dict, color_type: str, indent: int = 4) -> str:
    """
    Constructs a Color object string with specified indentation.
    """
    colors = f"{color_type}(\n"
    colors += "".join([" " * (indent + 4) + f"{key} = {val},\n" for key, val in colors_.items()])
    colors += " " * (indent + 0) + ")"
    return colors


def _set_items(items_: list, menu_id: str) -> str:
    """
    Constructs the menu.append() call string for a list of items.
    """
    items = " " * 0 + f"{menu_id}.append(\n" # adds 4 spaces later

    for item_ in items_:
        item = " " * 4 + f"Item(\n"
        item += " " * 8 + f"key = '{item_['key'][1:-1]}',\n"
        item += " " * 8 + f"message = '{item_['message'][1:-1]}',\n"

        if "Colors" in item_:
            colors_str = _set_colors(item_["Colors"], "ItemColors", 8)
            item += " " * 8 + f"colors = {colors_str},\n"
        if "ExitColors" in item_:
            colors_str = _set_colors(item_["ExitColors"], "ItemColors", 8)
            item += " " * 8 + f"exit_colors = {colors_str},\n"

        item += " " * 8 + "funcs = [\n"

        for funcargs in item_["func"]:
            func, args = parse_funcargs(funcargs)
            item += " " * 12 + f"({func}, {args}),\n"
        item += " " * 8 + "]\n"
        item += " " * 4 + "),\n"

        items += item

    items += ")\n"
    
    return items
