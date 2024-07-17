from macrolib.typemacros import tupler, dict_union, replace_value_nested



#----------------------------------------------------------------------------------------------------------------------
#Result Class

class Result():
    def __init__(self, n: int):
        self.n = n
    def __getitem__(self, n: int):
        return Result(n)
    def __repr__(self):
        return f"<class Result[{self.n}]>"
    def __eq__(self, other):
        return isinstance(other, Result) and self.n == other.n


#----------------------------------------------------------------------------------------------------------------------
#Menu Class

class Menu():
    #Keyword Objects
    result = Result(-1)
    escape = object()
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
                 escape_to = None,
                 exit_key = "e",
                 exit_message = "exit",
                 empty_message = "--*No Entries*--"
                 ):
        #Pass parameters
        self.name = name
        self.exit_to = exit_to
        self.empty_message = empty_message

        #Break point matching heirarchy
        self.end_to = self if end_to is None else \
            (self.exit_to if end_to is Menu.exit_to else end_to)
        self.escape_to = self if escape_to is None else \
            (self.exit_to if escape_to is Menu.exit_to else
             (self.end_to if escape_to is Menu.end_to else escape_to))

        #Init menu data
        self.menu_display_list = []      #["[key]- message"]
        self.menu = {}                   #{"key":(function-arg chain)}

        #Set exit option
        self.exit = (exit_key, exit_message, (exit_to, ()))
        self.update_menu(self.exit)


    def __call__(self):
        """Runs menu and entry function chain"""
        #Exit On Empty Menu
        if not self.menu_display_list[:-1]:
            print(self.empty_message)
            return self.exit_to()

        #Print Menu And Get Input
        show = f"\n{self.name}\n" + "\n".join(self.menu_display_list) + "\n"
        selection = input(show)

        #Refresh Menu On Invalid Input
        if selection not in self.menu.keys():
            print("--*Invalid Selection*--")
            return self()

        #Select Item
        switch = self.menu[selection]

        #Evaluate Function Chain
        result = None
        results = []
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
            if result is Menu.escape:
                return self.escape_to()

            #End Loop
            results.append(result)
            switch = switch[2:]

        #Go to end_to if last result is None
        return result if result is not None else self.end_to()


    def append(self,*data):
        """
        Append data to menu in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))
        --*{forces exit key to the end of the list}*--
        """
        self.menu_display_list = self.menu_display_list[:-1]
        for n in data + (self.exit,):
            self.update_menu(n)


    def update_menu(self, data):
        """Updates menu lists"""
        self.menu_display_list.append(f"[{data[0]}]- {data[1]}")
        self.menu[data[0]] = data[2]



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
    def lazy_eval(func, args, kwargs):
        """Depth-first evaluation of nested function/argument bindings."""
        func = func() if isinstance(func, Bind.Wrapper) else func
        args = tupler(x() if isinstance(x, Bind.Wrapper) else x for x in args)
        kwargs = {k: v() if isinstance(v, Bind.Wrapper) else v for k, v in kwargs.items()}

        return func(*args, **kwargs)



#----------------------------------------------------------------------------------------------------------------------
#In-Line Functions

def escape_on(x, value):
    """Returns an escape if the two arguments are equal, or both Truthy or both Falsy.
    Otherwise, returns value."""
    return Menu.escape if x == value or bool(x) == bool(value) else value


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
