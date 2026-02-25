from macrolibs.typemacros import dict_intersect, dict_compliment
from .menu_dict import MenuDict
from ..src.builtins import *
from .utils import *


# Blank dict with only static attribute names
# Init Menu with these...
STATIC_ATTRS = {
    "ID": '',
    "name": '',
    "clear_readout": '',
    "arg_to_first": '',
    "empty_message": '',
    "exit_message": '',
    "exit_key": ''
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

    #Initlialize all menus with only static attributes to a dict indexed by 'ID'
    for menu_id, attrs in struct_.items():
        # Compare all attributes defined in dsl script, and only feed into Menu 
        # if it intersects with the blank dict
        static_attrs = dict_intersect(attrs, STATIC_ATTRS)

        # Convert attrs types
        convert_attr_types(static_attrs)

        # Create Menu
        menu = Menu(**static_attrs)

        # Add id
        setattr(menu, "ID", menu_id)

        # Add to list
        menus.append(menu)

    # Convert list to attributable dict:  {menu_id: Menu}
    menus = MenuDict(menus)

    print(menus)

    #Add menu ids to global pointers and retrieve caller globals
    cannonize_menu_ids(menus, globals())
    retrieve_globals(globals())

    #Set all non-static attributes and convert 'ID' references to pointers
    for menu_id, menu, attrs in zip(menus.keys(), menus.values(), struct_.values()):
        #Get all remaining attributes
        active_attributes = dict_compliment(attrs, static_attrs)

        for name, attr in active_attributes.items():
            if name == "Items":
                #attr = (['key', 'message', "func1(*args)", "func2(*args),..."],...)
                append_menu_items(attr, menu)
            else:
                #Adds the rest: arg_to, exit_to, etc
                setattr(menu, name, eval(attr))

        #finally, update the exit item and apply matching keywords
        menu.ch_exit()
        menu.apply_matching_keywords()

    return menus


def append_menu_items(items: list[str], menu: Menu):
    """
    Converts "Items" list into menucmd format and appends to menu.
    (['key', 'message', "func1(arg1, arg2)", "func2(arg3, arg4)",...],...)
    -> [('key', 'message', (func1, (arg1, arg2), func2, (arg3, arg4)))]
    """
    literal_items = []

    for item in items:
        key = item[0]; message = item[1]
        funcs = ()
        for funcargs in item[2:]:
            funcs += parse_funcargs(funcargs)
        literal_items.append((key, message, tuple(funcs)))

    menu.append(*literal_items)


def parse_funcargs(funcargs: str) -> tuple[Any, tuple]:
    """
        "func(arg1, arg2,...)" -> (func, (arg1, arg2))
    """
    #Extract function.  Works with (lambda:(...))
    func_args_split = funcargs.split('(')
    func = None
    args = ()
    n_closed_par = 0

    try:
        for n, x in enumerate(func_args_split[::-1]):
            n_closed_par += x.count(')')
            if n_closed_par == n+1:
                func = eval("(".join(func_args_split[:-n-1]))
                
                # Force args to be a tuple (,) prevents double wrap reduction
                arg_str = "(" + "(".join(func_args_split[-n-1:])
                args = () if arg_str.strip() == "()" \
                    else eval(arg_str.strip()[:-1] + ",)")
                break

        if not func:
            raise SyntaxError

    except SyntaxError as e:
        raise SyntaxError(f"Unbalanced parenthesis in '{funcargs}'") from e

    return (func, args)
