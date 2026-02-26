from macrolibs.typemacros import dict_intersect, dict_compliment
from .menu_dict import MenuDict
from ..src.item import Item
from ..builtins.builtins import *
from .utils import *


# Blank dict with only static attribute names
# Init Menu with these...
STATIC_ATTRS = {
    #"ID": '',
    "name": '',
    "clear_readout": '',
    "arg_to_first": '',
    "empty_message": '',
    "exit_message": '',
    "exit_key": '',
    "Colors": '',
    "ExitColors": '',
}

#==================================================================================

def dict_to_objs(struct_: dict) -> MenuDict:
    """
    Converts the dictionary structure to a MenuDict object.
    First initializes the menus with their static attributes, introduces the menus into the global
    scope referenced by their ids, and then appends their items and '*_to' callbacks after converting
    them to literals.
    """
    menus = []

    if not "Menu" in struct_:
        raise RuntimeError("'Menu' must be present in the outer struct")

    #Initlialize all menus with only static attributes to a dict indexed by 'ID'
    for attrs in struct_["Menu"]:
        # Require id
        if not attrs.get('id'):
            raise KeyError("Menu must have an 'id' attribute")
        menu_id = attrs['id']
        
        # Compare all attributes defined in dsl script, and only feed into Menu 
        # if it intersects with the blank dict
        static_attrs = dict_intersect(attrs, STATIC_ATTRS)

        # Convert attrs types
        convert_static_attr_types(static_attrs)

        # Create Menu
        menu = Menu(**static_attrs)

        # Add id
        setattr(menu, "_id", menu_id)

        # Add to list
        menus.append(menu)

    # Convert list to attributable dict: {menu_id: Menu}
    menus = MenuDict(menus)

    #Add menu ids to global pointers and retrieve caller globals
    cannonize_menu_ids(menus, globals())
    retrieve_globals(globals())

    #Set all non-static attributes and convert 'ID' references to pointers
    for menu_id, menu, attrs in zip(menus.keys(), menus.values(), struct_["Menu"]):
        # Get all remaining attributes                            
        active_attributes = dict_compliment(attrs, STATIC_ATTRS)

        for name, attr in active_attributes.items():
            if name == "Item":
                _append_menu_items(menu, attr)
            else:
                # Adds the rest: arg_to, exit_to, etc
                setattr(menu, name, eval(attr))

        # finally, update the exit item and apply matching keywords
        menu.ch_exit()
        menu.apply_matching_keywords()

    return menus


def _append_menu_items( menu: Menu, items: list[dict],):
    """
    Converts "Item" list into Items and appends to menu.
    [{key, message, funcs, Colors}, ...] -> Item
    """
    for item in items:
        if not item.get('key'):
            raise KeyError("Item must have 'key' attribute")

        funcs = [_parse_funcargs(funcargs) for funcargs in item['func']] if item.get('func') else []
        colors = convert_colors(item['Colors'], "Item") if item.get('Colors') else None  
        
        # Append Items
        menu.append(Item(
            key=eval(item["key"]), message=eval(item["message"]), 
            funcs=funcs, colors=colors
        )) 
        

def _parse_funcargs(funcargs: str) -> tuple[Any, tuple]:
    """"func(arg1, arg2,...)" -> (func, (arg1, arg2))"""
    # Extract function.  Works with (lambda:(...))
    func_args_split = funcargs.split('(')
    n_closed_par = 0

    # Split func and args
    for n, x in enumerate(func_args_split[::-1]):
        n_closed_par += x.count(')')
        if n_closed_par == n+1:
            func_str = "(".join(func_args_split[:-n-1])
            arg_str = "(" + "(".join(func_args_split[-n-1:])

            # Eval Func
            func = eval(func_str)
            
            # Eval Args
            try:
                args = () if arg_str.strip() == "()" \
                    else eval(arg_str.strip()[:-1] + ",)")
                
            # Menu.kwargs reminder
            except SyntaxError as e:
                if '=' in arg_str and '==' not in arg_str and ':=' not in arg_str:
                    raise SyntaxError(
                        f"Invalid keyword argument syntax in '{funcargs}'.\n"
                        f"All keyword arguments must be wrapped in 'kwargs()'.\n"
                        f"      Ex: func(arg1, kwargs(key=value))"
                    ) from e
                raise SyntaxError from e

            # Return tuple
            return (func, args)

    # Parenthesis Error
    raise SyntaxError(f"Unbalanced parenthesis in '{funcargs}'")
