from .menucmd import *
from macrolibs.typemacros import dict_compliment, type_compliment
from typing import Any, Iterator

#----------------------------------------------------------------------------------------------------------------------
#In-Line Functions

def escape_on(x, value):
    """Returns Menu.escape if the two arguments are equal.
    Otherwise, return x."""
    return Menu.escape if x == value else x


def f_escape(*args, **kwargs) -> Menu.escape:
    """Polymorphic in-line escape function."""   #terminal morphism in Hom(*,escape)
    return Menu.escape

def f_end(*args, **kwargs) -> None:
    """Polymorphic in-line None return (end)"""  #terminal morphism in Hom(*, None)
    return None


def f_switch(n: int | str | Any, funcs: list | tuple | dict) -> Bind.Wrapper:
    """Returns a lazy function of type (Any index -> function)"""
    return Bind(lambda b: maybe_arg(funcs[b]), n)



#----------------------------------------------------------------------------------------------------------------------
#Builtin Menus

def yesno_ver(yes = True, no = False, yes_message = "yes", **kwargs) -> bool | Any:
    """Simple yes/no verification returning bool by default
    Use yes and no tags to specify otherwise.
    """
    kwargs_ = ({"name":"Are you sure?", "exit_message":"cancel"} | kwargs |
               {"exit_to":lambda: no, "end_to":lambda: None})
    menu = Menu(**kwargs_)

    menu.append(("x", yes_message, (lambda: yes, ())))

    return menu()


def edit_list(entries: list | tuple | dict | set, display_as = lambda x:x, **kwargs) -> list | tuple | dict | set:
    """Delete items in a list/tuple/dict/set; returns updated list/tuple/dict/set"""

    kwargs_ = {"name":"Edit List"} | kwargs | {"exit_to":lambda: entries}
    menu = Menu(**kwargs_)

    if isinstance(entries, list | tuple | set):
        for n, entry in enumerate(entries):
            menu.append((str(n+1), display_as(str(entry)),
                         (edit_list, (entries[:n] + entries[n+1:], Menu.kwargs(display_as=display_as, **kwargs)))))

    elif isinstance(entries, dict):
        for n, (k, v) in enumerate(entries.items()):
            menu.append((str(n+1), f"{k}:{display_as(str(v))}",
                         (edit_list, (dict_compliment(entries, {k:v}), Menu.kwargs(display_as=display_as, **kwargs)))))
    else:
        raise TypeError

    return type(entries)(menu())


def choose_item(entries: list | tuple | dict | set, exit_val = None, display_as = lambda x:x, **kwargs) -> list | tuple | dict | set:
    """Pick and return an element from a list/tuple/dict/set.
    Returns (key, value) pair for dict.
    On exit key, return 'exit_val' (None by default)
    """
    kwargs_ = {"name": "Choose Item"} | kwargs | {"exit_to": lambda: exit_val}
    menu = Menu(**kwargs_)

    if isinstance(entries, list | tuple | set):
        for n, entry in enumerate(entries):
            menu.append((str(n+1), display_as(str(entry)), (Menu.id, entries[n])))

    elif isinstance(entries, dict):
        for n, (k, v) in enumerate(entries.items()):
            menu.append((str(n+1), f"{k}:{display_as(str(v))}", (Menu.id, ((k, v),))))
    else:
        raise TypeError

    return menu()


def choose_items(entries: list | tuple | dict | set, display_as = lambda x:x, **kwargs) -> list | tuple | dict | set:
    """Pick and return mutiple elements from a list/tuple/dict/set."""
    return type_compliment(entries, edit_list(entries, display_as = display_as, **kwargs))


#----------------------------------------------------------------------------------------------------------------------
#Dynamic Menus

#WIP
def dynamic_wrapper(dyn_func, *args, **kwargs) -> Bind.Wrapper:
    """WIP
    Intended as a wrapper for arg_to (for now)

    Usage: Menu(arg_to = dynamic_wrapper(dyn_func, *args, **kwargs))

    Takes a func dyn_func: (menu_id, arg, *args, **kwargs) -> arg -> result[0]

    Example:
    def dyn_func(menu_id, arg, *items):
        menu_id.clear()
        menu_id.append(*items)
        return arg

    dyn_func must refer to the menu in its first argument, the menu argument for its second,
    and can take any additional *args/**kwargs.
    It is intended for arbitrary use of menu methods to dynamically change the menu on run.
    """
    return Bind(lambda menu_id, arg: dyn_func(menu_id, arg, *args, **kwargs), Menu.self)
