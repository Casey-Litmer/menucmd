from macrolibs.typemacros import copy_type
from menucmd import Bind

expanded = copy_type(tuple, "expanded")

def expand_in_place(A: tuple | list, expand_type: type):
    """Recursively expand all marked tuples/lists in a data structure
    (a, (b, expanded((c, d)))) -> (a, (b, c, d))
    """
    new = type(A)()

    for x in A:
        if isinstance(x, expand_type):
            new += tuple(x)

        elif isinstance(x, tuple | list):
            new += (type(x)(expand_in_place(x, expand_type)),)

        else:
            new += type(A)((x,))

    return new





A = (1,2, [3,4], (5,6), Bind(lambda a,b:None, expanded((8,9))))

print(expand_in_place(A, expanded))

"""""
A = (a, (b, c), d)

eip(A, ()) -> 

"""""