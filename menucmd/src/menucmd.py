from .macrolib.typemacros import tupler, dict_union, replace_value_nested, maybe_arg
from copy import copy


#----------------------------------------------------------------------------------------------------------------------
#Keyword Types

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
    __NULL__ = object()
    here = object()  #Tells the menu to escape with its initial argument

    def __init__(self, x = __NULL__):
        self.val = x if x is not Escape.__NULL__ else None
    def __getitem__(self, x):
        return Escape(x)
    def __repr__(self):
        return f"<class Escape[{self.val}]>"
    def __eq__(self, other):
        return isinstance(other, Escape) and self.val == other.val


#----------------------------------------------------------------------------------------------------------------------
#Menu Class

class Menu():
    #Keyword Objects
    result = Result(-1)
    escape = Escape()
    __END__ = type("Menu.__END__", (object,), {})  #Terminal Object

    #Matching Keywords
    exit_to = object()  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object()

    #Kwargs Wrapper
    class kwargs(dict):
        pass


    def __init__(self,
                 name = "Choose Action",
                 exit_to = lambda: Menu.__END__,
                 end_to = None,
                 arg_to = lambda x: x,
                 return_to = lambda x: x,
                 escape_to = None,
                 exit_key = "e",
                 exit_message = "exit",
                 empty_message = "--*No Entries*--"
                 ):
        #Pass parameters
        self.name = name
        self.exit_to, self.exit_key, self.exit_message = exit_to, exit_key, exit_message

        #Depreciated
        self.arg_to = arg_to
        self.return_to = return_to
        #

        self.empty_message = empty_message

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


    #TODO
    #compose end_to and exit_to with arg
    def __call__(self, arg = None):
        """Runs menu and entry function chain"""

        #Exit On Empty Menu
        if not self.menu_display_list[:-1]:
            print(self.empty_message)
            return maybe_arg(self.exit_to)(arg)

        #Print Menu And Get Input
        show = f"\n{self.name}\n" + "\n".join(self.menu_display_list) + "\n"
        selection = input(show)

        #Refresh Menu On Invalid Input
        if selection not in self.menu.keys():
            print("--*Invalid Selection*--")
            return self(arg)

        #Select Item
        switch = self.menu[selection]

        #Evaluate arg_to if not exit_key
        #result = maybe_arg(self.arg_to)(arg) \
        #    if selection != self.exit[0] else arg
        result = arg
        results = [result]    #TODO change in docs to be 1-based, 0 being from the menu call itself

        #Evaluate Function Chain
        while len(switch) >= 2:
            #Get func/args pair
            func = switch[0]
            args = tupler(switch[1])

            #Replace Result Keywords
            N = len(results)
            for n in range(-N, N):
                func = replace_value_nested(tupler(func), Result(n), results[n])[0]
                args = replace_value_nested(tupler(args), Result(n), results[n])

            #Separate args/kwargs
            kwargs = dict_union(tupler(x for x in args if isinstance(x, Menu.kwargs)))
            args = tupler(x for x in args if not isinstance(x, Menu.kwargs))

            #Evaluate Function
            result = Bind.lazy_eval(func, args, kwargs)

            #Manual escape
            if isinstance(result, Escape):
                ESC = result[arg] if result.val == self.escape.here else result  #does this need value mapping?
                return maybe_arg(self.escape_to)(ESC.val)

            #End Loop
            results.append(result)
            switch = switch[2:]

        #Evaluate return_to if not exit key
        #result = maybe_arg(self.return_to)(result) if selection != self.exit[0] else result

        #Go to end_to if final value is None
        return result if result is not None else maybe_arg(self.end_to)(arg)


    def __getitem__(self, idx):
        if isinstance(idx, slice):
            new_menu = copy(self); new_menu.clear()
            new_menu.append(*self.menu_item_list[idx])

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
            self.menu_item_list.append(n)
            self.update_menu(n)



    def clear(self):
        """Clears all items from the menu"""
        self.menu_item_list, self.menu_display_list = [], []
        self.menu = {}
        self.update_menu(self.exit)


    def insert(self, n: int, *data):
        """Insert data at position n in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))"""
        _data = self.menu_item_list[:n] + [*data] + self.menu_item_list[n:]
        self.clear()
        self.append(*_data)


    def delete(self, n: int, k: int = 1):
        """Delete k menu entries starting at position n"""
        _data = self.menu_item_list[:n] + self.menu_item_list[n+k:]
        self.clear()
        self.append(*_data)


    def update_menu(self, data):
        """Updates menu lists"""
        self.menu_display_list.append(f"[{data[0]}]- {data[1]}")
        self.menu[data[0]] = data[2]


    #Use this to change properties of the exit item
    def ch_exit(self, exit_to = False, exit_key = False, exit_message = False) -> None:
        self.exit_to = exit_to if exit_to else self.exit_to
        self.exit_key = exit_key if exit_to else self.exit_to
        self.exit_message = exit_message if exit_message else self.exit_message

        self.exit = (self.exit_key, self.exit_message, (self.exit_to, Menu.result))
        self.delete(-1)
        self.update_menu(self.exit)




#----------------------------------------------------------------------------------------------------------------------
#Lazy Evaluation

class Bind():
    """
    Used for delayed evaluation.
    Creates a callable list of function / argument pairs in the form:
    [<function>, (args), {kwargs}]  ->  function(*args, **kwargs)
    """
    class Wrapper(list):
        def __call__(self):
            return Bind.lazy_eval(self[0], self[1], self[2])


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
    return Menu.escape[value] if x == value else value


def f_escape(*args, **kwargs) -> Menu.escape:
    """Polymorphic in-line escape function."""   #terminal morphism in Hom(*,escape)
    return Menu.escape


def f_switch(n: int, funcs: tuple) -> Bind.Wrapper:
    """Returns a lazy function of type (int -> function)"""
    return Bind(lambda b: funcs[b], n)



#----------------------------------------------------------------------------------------------------------------------
#Builtin Menus

def yesno_ver(**kwargs) -> bool:
    """Simple yes/no verification returning bool"""
    kwargs_ = {"name":"Are you sure?", "exit_message":"cancel"} | kwargs | {"exit_to":lambda: False}
    menu = Menu(**kwargs_)
    menu.append(("x", "yes", (lambda: True, ())))

    return menu()


def edit_list(entries: list | tuple, **kwargs) -> list | tuple:
    """Delete items in a list/tuple; returns updated list/tuple"""
    kwargs_ = {"name":"Edit List"} | kwargs | {"exit_to":lambda: entries}
    menu = Menu(**kwargs_)
    for n, entry in enumerate(entries):
        menu.append((str(n), str(entry), (edit_list, (entries[:n] + entries[n+1:], Menu.kwargs(kwargs)))))

    return menu()

