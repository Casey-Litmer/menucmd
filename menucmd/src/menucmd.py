from macrolibs.typemacros import tupler, dict_union, list_union, replace_value_nested, maybe_arg
from copy import copy
from typing import Any


#----------------------------------------------------------------------------------------------------------------------
#Keyword Types

#How to generic type cover like this instead of writing these out?
#is there a simpler way to (hint) 'typeclass' these?
class Result():
    def __init__(self, n: int):
        self.n = n
    def __getitem__(self, n: int):
        return Result(n)
    def __repr__(self):
        return f"<class Result[{self.n}]>"
    def __eq__(self, other):
        return isinstance(other, Result) and self.n == other.n


class Escape():
    here = object()  #Tells the menu to escape with its initial argument

    def __init__(self, x = None):
        self.val = x
    def __getitem__(self, x):
        return Escape(x)
    def __repr__(self):
        return f"<class Escape[{self.val}]>"
    def __eq__(self, other):
        return isinstance(other, Escape) and self.val == other.val


#----------------------------------------------------------------------------------------------------------------------
#Menu Class

class Menu():
    #Matching Keywords
    exit_to = object()  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object()   #

    #Keyword Objects
    result = Result(-1)
    escape = Escape()
    self = object()
    end = lambda: None   #force end_to function

    __END__ = type("Menu.__END__", (object,), {})  #Terminal Object
    id = lambda x:x                                #Identity morphism

    #Kwargs Wrapper
    class kwargs(dict):
        pass


    def __init__(self,
                 name = "Choose Action",
                 exit_to = lambda: Menu.__END__,
                 end_to = None,
                 escape_to = None,
                 arg_to = lambda x:x,
                 exit_key = "e",
                 exit_message = "exit",
                 empty_message = "--*No Entries*--"
                 ):
        #Pass parameters
        self.name = name
        self.empty_message = empty_message
        self.exit_to, self.exit_key, self.exit_message = exit_to, exit_key, exit_message
        self.arg_to = replace_value_nested(tupler(arg_to), Menu.self, self)[0]

        #Break point matching heirarchy
        self.end_to = self if end_to is None else \
            (self.exit_to if end_to is Menu.exit_to else end_to)
        self.escape_to = self if escape_to is None else \
            (self.exit_to if escape_to is Menu.exit_to else
             (self.end_to if escape_to is Menu.end_to else escape_to))

        #Init menu data
        self.menu_item_list = []         #de jure list of items
        self.menu_display_list = []      #["[key]- message"]
        self.menu = {}                   #{"key":(function-arg chain)}

        #Set exit option
        self.exit = ()
        self.ch_exit()


    def __call__(self, arg = None):
        """Runs menu with 'arg' asking for user input.
        Selection runs the item's function chain where each nth function has
        access to Menu.result[0 -> n]; (n in [0,1,2...])

        Menu.result[0] == arg
        """
        #Evaluate arg_to and add 0th result
        result = maybe_arg(self.arg_to)(arg)  #arg_to = B(print, "hello") for example.  Make clear in docs that Bind.wrapper can be called without args
        results = [result]  #TODO change in docs to be 1-based, 0 being from the menu call itself

        #List state logic
        if not self.menu_display_list[:-1]:
            #Exit on empty menu
            print(self.empty_message)
            selection = self.exit_key
        else:
            #Print Menu And Get Input
            show = f"\n{self.name}\n" + "\n".join(self.menu_display_list) + "\n"
            selection = input(show)

        #Refresh Menu On Invalid Input
        if selection not in self.menu.keys():
            print("--*Invalid Selection*--")
            return self(arg)

        #Select Item
        switch = self.menu[selection]

        #Exit menu
        if selection == self.exit_key:
            return maybe_arg(switch[0])(arg)

        #Evaluate Function Chain
        while len(switch) >= 2:
            #Get func/args pair
            func = switch[0]
            args = tupler(switch[1])

            #Replace Results and Separate args/kwargs
            func, args, kwargs = self.replace_keywords(func, args, results)

            #Evaluate Function
            result = Bind.lazy_eval(func, args, kwargs)

            #Manual escape
            if isinstance(result, Escape):
                return maybe_arg(self.escape_to)(arg)

            #End Loop
            results.append(result)
            switch = switch[2:]

        #Go to end_to if final value is None
        return result if result is not None else \
            maybe_arg(self.replace_keywords(self.end_to, (), results)[0])(arg)  #TODO update docs


    def replace_keywords(self, func, args: tuple, results: list) -> tuple:
        """Replaces all inline self references with the current menu.
        Replaces all Menu.result objects with function results from the chain.
        Returns a tuple in the form (func, args, kwargs).
        The input args also includes all kwargs distinguished by the Menu.kwargs wrapper.
        """
        #Replace self reference
        func = replace_value_nested(tupler(func), Menu.self, self)[0]
        args = replace_value_nested(tupler(args), Menu.self, self)

        #Replace Result Keywords
        N = len(results)
        for n in range(-N, N):
            func = replace_value_nested(tupler(func), Result(n), results[n])[0]
            args = replace_value_nested(tupler(args), Result(n), results[n])

        #Separate args/kwargs
        kwargs = dict_union(tupler(x for x in args if isinstance(x, Menu.kwargs)))
        args = tupler(x for x in args if not isinstance(x, Menu.kwargs))

        return (func, args, kwargs)


    def __getitem__(self, idx):
        if isinstance(idx, slice):
            new_menu = copy(self); new_menu.clear()
            new_menu.append(*self.menu_item_list[:-1][idx])

            return new_menu

        return self.menu_item_list[idx]


    def append(self, *data):
        """
        Append data to menu in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))
        --*{forces exit key to the end of the list}*--
        """
        self.menu_display_list = self.menu_display_list[:-1]
        self.menu_item_list = self.menu_item_list[:-1]

        for n in data + (self.exit,):
            self.menu_item_list = list_union(self.menu_item_list, [n])
            self.update_menu(n)


    def clear(self):
        """Clears all items from the menu"""
        self.menu_item_list, self.menu_display_list = [], []
        self.menu = {}
        self.update_menu(self.exit)


    def insert(self, n: int, *data):
        """Insert data at position n in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))"""
        _data = self.menu_item_list[:-1][:n] + [*data] + self.menu_item_list[:-1][n:]
        self.clear()
        self.append(*_data)


    def delete(self, n: int, k: int = 1):
        """Delete k menu entries starting at position n"""
        _data = self.menu_item_list[:-1][:n] + self.menu_item_list[:-1][n+k:]
        self.clear()
        self.append(*_data)


    def update_menu(self, data):
        """Updates menu lists"""
        self.menu_display_list = list_union(self.menu_display_list, [f"[{data[0]}]- {data[1]}"])
        self.menu[data[0]] = data[2]


    def ch_exit(self, exit_to = False, exit_key = False, exit_message = False) -> None:
        """Changes the properties of the exit key and appends it to the list
        :return: None
        """
        self.exit_to = exit_to if exit_to else self.exit_to
        self.exit_key = exit_key if exit_key else self.exit_key
        self.exit_message = exit_message if exit_message else self.exit_message

        self.exit = (self.exit_key, self.exit_message, (self.exit_to, ())) #will attempt to fill in argument with arg
        self.append()



#----------------------------------------------------------------------------------------------------------------------
#Lazy Evaluation

class Bind():
    """
    Used for delayed evaluation.
    Creates a callable list of function / argument pairs in the form:
    [<function>, (args), {kwargs}]  ->  function(*args, **kwargs)

    Calling a Bind object with additional args/kwargs will append (curry) them to its initial args/kwargs.

    Bind(func, args1, kwargs1)(args2, kwargs2) -> func(*args1, *args2, **kwargs1, **kwargs2)
    """
    class Wrapper(list):
        def __call__(self, *args, **kwargs):
            return Bind.lazy_eval(self[0], self[1] + args, self[2] | kwargs)


    def __new__(cls, func, *args, **kwargs) -> Wrapper:
        return cls.Wrapper([func, args, kwargs])


    @staticmethod
    def lazy_eval(func, args = (), kwargs = {}):
        """Depth-first evaluation of nested function/argument bindings."""
        func = func() if isinstance(func, Bind.Wrapper) else func
        args = tupler(arg() if isinstance(arg, Bind.Wrapper) else arg for arg in tupler(args))
        kwargs = {k: v() if isinstance(v, Bind.Wrapper) else v for k, v in kwargs.items()}

        return func(*args, **kwargs)



#----------------------------------------------------------------------------------------------------------------------
#In-Line Functions

def escape_on(x, value):
    """Returns an escape if the two arguments are equal.
    Otherwise, returns value."""
    return Menu.escape if x == value else value


def f_escape(*args, **kwargs) -> Menu.escape:
    """Polymorphic in-line escape function."""   #terminal morphism in Hom(*,escape)
    return Menu.escape


def f_switch(n: int, funcs: tuple) -> Bind.Wrapper:
    """Returns a lazy function of type (int -> function)"""
    return Bind(lambda b: funcs[b], n)


#----------------------------------------------------------------------------------------------------------------------
#Builtin Menus

#TODO add yes/no tags to docs
def yesno_ver(yes = True, no = False, **kwargs) -> bool | Any:
    """Simple yes/no verification returning bool be default
    Use yes and no tags to specify otherwise"""
    kwargs_ = ({"name":"Are you sure?", "exit_message":"cancel"} | kwargs |
               {"exit_to":lambda: no, "end_to":lambda: None})
    menu = Menu(**kwargs_)
    menu.append(("x", "yes", (lambda: yes, ())))

    return menu()


def edit_list(entries: list | tuple, **kwargs) -> list | tuple:
    """Delete items in a list/tuple; returns updated list/tuple"""
    kwargs_ = {"name":"Edit List"} | kwargs | {"exit_to":lambda: entries}
    menu = Menu(**kwargs_)
    for n, entry in enumerate(entries):
        menu.append((str(n), str(entry), (edit_list, (entries[:n] + entries[n+1:], Menu.kwargs(kwargs)))))

    return menu()


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
        menu_id.append(*items)
        return arg

    dyn_func must refer to the menu in its first argument, the menu argument for its second,
    and can take any additional *args/**kwargs.
    It is intended for arbitrary use of menu methods to dynamically change the menu on run.
    """
    return Bind(lambda menu_id, arg: dyn_func(menu_id, arg, *args, **kwargs), Menu.self)

