from ..src.builtins import *
from macrolibs.typemacros import dict_intersect, dict_compliment
import inspect
from .lines_to_dict import lines_to_dict


#SHORTHANDS
result = Menu.result
B = Bind
kwargs = Menu.kwargs

#Output type
class MenuDict(dict):
    """
    Dictionary of menu objects that can be additionally referenced by attributes:
    menu_dict['menu_id'] = menu_dict.menu_id
    """
    def __init__(self, menus: list):
        for menu in menus:
            self.__setattr__(menu.ID, menu)

        self.menus = {menu.ID:menu for menu in menus}

    def __getitem__(self, item):
        return self.menus[item]
    def __iter__(self):
        return iter(self.menus)
    def __repr__(self):
        return f"<Menus {self.menus}>"
    def keys(self):
        return self.menus.keys()
    def values(self):
        return self.menus.values()
    def items(self):
        return self.menus.items()

#-----------------------------------------------------------------------------------

def build_menus(file: str) -> MenuDict:
    """Convert .mcmd file to attributable dict of menus"""

    #Get text
    with open(file) as f:
        lines = f.readlines()
    f.close()

    #Covert to dict
    struct_ = lines_to_dict(lines)
    #Convert to MenuDict
    menus = dict_to_obs(struct_)

    return menus

#------------------------------------------------------------------------------------

def dict_to_obs(struct_: dict) -> MenuDict:
    """
    Converts the dictionary structure to a MenuDict object.
    First initializes the menus with their static attributes, introduces the menus into the global
    scope referenced by their ids, and then appends their items and '*_to' callbacks after converting
    them to literals.
    """
    menus = []

    #blank dict with only static attribute names
    STATIC_ATTRS = {
        "ID": '',
        "name": '',
        "empty_message": '',
        "exit_message": '',
        "exit_key": ''
    }

    #Initlialize all menus with only static attributes to a dict indexed by 'ID'
    for menu_id, attrs in struct_.items():
        #compare all attributes defined in dsl script, and only feed into Menu if it intersects with the blank dict
        static_attrs = dict_intersect(attrs, STATIC_ATTRS)

        #Create Menu
        menu = Menu(**static_attrs)

        #Add id
        setattr(menu, "ID", menu_id)

        #Add to list
        menus.append(menu)

    #Convert list to attributable dict:  {menu_id: Menu}
    menus = MenuDict(menus)

    #Add menu ids to global pointers and retrieve caller globals
    cannonize_menu_ids(menus)
    retrieve_globals()

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


def retrieve_globals():
    """Adds globals from where the .mcmd file is loaded."""
    caller_globals = inspect.stack()[3].frame.f_globals
    globals().update(caller_globals)


def cannonize_menu_ids(menus: MenuDict):
    """Adds menu to global scope"""
    for menu_id, menu in menus.items():
        globals()[menu_id] = menu


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