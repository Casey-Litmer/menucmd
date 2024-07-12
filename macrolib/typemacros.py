from types import GeneratorType
from typing import Any


#Unions
#----------------------------------------------------------------------------------------------------------------------

def list_union(a: list | tuple | list[list] | tuple[list], b: list | tuple | None = None) -> list:
    """
    If 'b' is None, the function will perform an iterative union of all lists and tuples in 'a'.
    In this case, 'a' must be a list or tuple of exclusively lists or  tuples.
    Otherwise, perform the union of 'a' and 'b'
    :param a: list or tuple (of lists or tuples)
    :param b: list or tuple
    :return: list
    """
    if b is None:
        l_union = list()
        for n in a:
            if isinstance(n, list | tuple):
                l_union = list_union(n, l_union)
            else:
                print("'a' must be a list or tuple of lists or tuples if 'b' is empty")
                raise TypeError
        return l_union
    else:
        return list(set(a) | set(b))


def tuple_union(a: list | tuple | list[tuple] | tuple[tuple], b: list | tuple | None = None) -> tuple:
    """
    If 'b' is None, the function will perform an iterative union of all lists and tuples in 'a'.
    In this case, 'a' must be a list or tuple of exclusively lists or  tuples.
    Otherwise, perform the union of 'a' and 'b'
    :param a: list or tuple (of lists or tuples)
    :param b: list or tuple
    :return: tuple
    """
    if b is None:
        t_union = tuple()
        for n in a:
            if isinstance(n, list | tuple):
                t_union = tuple_union(n, t_union)
            else:
                print("'a' must be a list or tuple of lists or tuples if 'b' is empty")
                raise TypeError
        return t_union
    else:
        return tuple(set(a) | set(b))


def dict_union(a: dict | list[dict] | tuple[dict], b: dict | None = None) -> dict:
    """
    If 'b' is None, the function will perform an iterative union of all dicts in 'a'.
    In this case, 'a' must be a list or tuple of exclusively dicts.
    Otherwise, perform the union of 'a' and 'b'
    (Leftmost keys have precedence)
    :param a: dict, list, or tuple (of dicts)
    :param b: set
    :return: dict
    """
    if b is None:
        d_union = dict()
        for n in a:
            if isinstance(n, dict):
                d_union = dict_union(n, d_union) #test switching these around
            else:
                print("'a' must be a list or tuple of dicts if 'b' is empty")
                raise TypeError
        return d_union
    else:
        return dict(a | b)


def set_union(a: set | list[set] | tuple[set], b: set | None = None) -> set:
    """
    If 'b' is None, the function will perform an iterative union of all sets in 'a'.
    In this case, 'a' must be a list or tuple of exclusively sets.
    Otherwise, perform the union of 'a' and 'b'
    :param a: set, list, or tuple (of dicts)
    :param b: set
    :return: set
    """
    if b is None:
        s_union = set()
        for n in a:
            if isinstance(n, set):
                s_union = set_union(n, s_union)
            else:
                print("'a' must be a list or tuple of sets if 'b' is empty")
                raise TypeError
        return s_union
    else:
        return set(a | b)


#Syntax Converters
#----------------------------------------------------------------------------------------------------------------------

def tupler(a) -> tuple:
    """
    Passes tuples and generator objects to tuples, and parenthesizes anything else.
    This effectively bypasses the need for a comma in defining a singleton tuple;  (a) -> (a,)
    """
    if isinstance(a, tuple | GeneratorType):
        return tuple(a)
    else:
        return (a,)


#Expansions
#----------------------------------------------------------------------------------------------------------------------

def replace_value_nested(a: list | tuple | dict | set, old_vals: tuple | Any , new_val) -> list | tuple | dict | set:
    """
    Replaces a value recursively in a data structure.  The value(s) to replace can be of any type,
    including any type of the data structures being searched through.
    :param a: list, tuple, dict, or set  (all nestings allowed)
    :param old_vals: value(s) to replace
    :param new_val: value to inject
    :return: list, tuple, dict, or set
    """
    old_vals = tupler(old_vals)

    if a in old_vals:
        return new_val
    elif isinstance(a, list):
        return type(a)(replace_value_nested(x, old_vals, new_val) for x in a)
    elif isinstance(a, tuple):
        return type(a)(replace_value_nested(x, old_vals, new_val) for x in a)
    elif isinstance(a, dict):
        return type(a)({k:replace_value_nested(v, old_vals, new_val) for k,v in a.items()})
    elif isinstance(a, set):
        return type(a)(replace_value_nested(x, old_vals, new_val) for x in a)
    else:
        return new_val if a in old_vals else a


