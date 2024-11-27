from macrolibs.typemacros import tupler, dict_union, list_union, tuple_union
from macrolibs.typemacros import replace_value_nested, maybe_arg, copy_type, maybe_type
from copy import copy


#----------------------------------------------------------------------------------------------------------------------
#Result Type

class Result():
    def __init__(self, n: int):
        self.__n__ = n
        self.__attr__ = None

    def __getitem__(self, n: int):
        return type(self)(n).__getattr__(self.__attr__)

    def __repr__(self):
        return f"<class Result[{self.__n__}]>"

    def __eq__(self, other):
        """Compare by attribute if both self and other have attributes"""
        if self.__attr__ is not None and hasattr(other, "__attr__") and other.__attr__ is not None:
            return type(self) == type(other) and self.__attr__ == other.__attr__
        else:
            return type(self) == type(other) and self.__n__ == other.__n__

    def expand(self):
        """Type to replace and expand in place.   *result <=> result.expand()"""
        return copy_type(type(self), "expand")(self.__n__).__getattr__(self.__attr__)

    def __getattr__(self, tag):
        """Index by attribute first.  If no attribute, index by index"""
        new_result = type(self)(self.__n__)
        new_result.__attr__ = tag
        return new_result


#----------------------------------------------------------------------------------------------------------------------
#Menu Class

class Menu():
    #Matching Keywords
    exit_to = object()  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object()   #

    #Keyword Objects
    result = Result(-1)
    escape = object()
    self = object()

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

        #Replace self references in arg_to if it is a Bind.Wrapper object
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

        #Tracked attributes for current result chain
        self.tracked_attributes = {}


    def __call__(self, arg = None):
        """Runs menu with 'arg' asking for user input.
        Selection runs the item's function chain where each nth function has
        access to Menu.result[0 -> n]; (n in [0,1,2...])

        Menu.result[0] == arg
        """
        #Reset tracked attributes
        self.tracked_attributes = {}

        #Evaluate arg_to and add 0th result
        result = maybe_arg(self.arg_to)(arg)
        results = [result]

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

        #Exit menu if exit_key pressed
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
            if result is Menu.escape:
                return maybe_arg(self.escape_to)(arg)

            #End Loop
            results.append(result)
            switch = switch[2:]

        #Go to end_to if final value is None
        return result if result is not None else maybe_arg(self.end_to)(arg)

        #Maybe do this in the future for None returns:
        #maybe_arg(self.replace_keywords(self.end_to, (), results)[0])(arg)
        #
        #It doesn't make sense to have two refs to result[0] = arg
        #but built-in behaviour switching via Bind based on past results might be better than
        #using inline functions to switch between a result return and a None return


    def replace_keywords(self, func, args: tuple, results: list) -> tuple:
        """Replaces all inline self references with the current menu.
        Replaces all Menu.result objects with function results from the chain.

        Returns a tuple in the form (func, args, kwargs).

        'args' may also include all kwargs distinguished by the Menu.kwargs wrapper.
        """
        #Replace self reference
        func = replace_value_nested(tupler(func), Menu.self, self)[0]
        args = replace_value_nested(tupler(args), Menu.self, self)

        #Tuple type to 'de-tuple'
        expanded = copy_type(tuple, "expanded")

        #Replace Result Keywords by Attribute
        for tag, val in self.tracked_attributes.items():
            func = replace_value_nested(tupler(func), Result(0).__getattr__(tag), val)[0]
            args = replace_value_nested(tupler(args), Result(0).__getattr__(tag).expand(), maybe_type(expanded, val))
            args = replace_value_nested(tupler(args), Result(0).__getattr__(tag), val)

        #Replace Result Keywords by Position
        N = len(results)
        for n in range(-N, N):

            #Detect if a result has an attribute and add first declaration to tracked attributes
            def track_attr(R, value):
                if R.__attr__ is not None and R.__attr__ not in self.tracked_attributes.keys():
                    self.tracked_attributes[R.__attr__] = value
                return value

            func = replace_value_nested(tupler(func), Result(n), results[n], callback= track_attr)[0]
            args = replace_value_nested(tupler(args), Result(n).expand(), maybe_type(expanded, results[n]), callback= track_attr)
            args = replace_value_nested(tupler(args), Result(n), results[n], callback= track_attr)


        #Separate args/kwargs
        kwargs = dict_union(tupler(x for x in args if isinstance(x, Menu.kwargs)))
        args = tupler(x for x in args if not isinstance(x, Menu.kwargs))

        #'Uninterprets' tupler for expanded results.  Allows inline notation for (*args) ~ result.expand()
        args = Menu.expand_in_place(args, expanded)

        return (func, args, kwargs)


    @staticmethod
    def expand_in_place(A: tuple | list, expand_type: type):
        """Recursively expand all marked tuples/lists in a data structure
        (a, [b, expanded((c, d))]) -> (a, [b, c, d])
        """
        new = type(A)()

        for x in A:
            #Append all elements if marked as 'expanded'
            if isinstance(x, expand_type):
                new += type(A)(x)
            #Run in nesting (recursion)
            elif isinstance(x, tuple | list):
                new += type(A)(((Menu.expand_in_place(x, expand_type)),))
            #Do nothing
            else:
                new += type(A)((x,))

        return new


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


    def ch_exit(self, exit_to = None, exit_key = None, exit_message = None) -> None:
        """Changes the properties of the exit key and appends it to the list
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

    - Calling a Bind object with additional args/kwargs will append (curry) them to its initial args/kwargs.

      Bind(func, args1, kwargs1)(args2, kwargs2) -> func(*args1, *args2, **kwargs1, **kwargs2)

    - Use Bind(func, *args, **kwargs).fix() to toggle currying.
    """
    class Wrapper(list):
        def __init__(self, data = ()):
            super().__init__(data)
            self.fixed = False

        def __call__(self, *args, **kwargs):
            if self.fixed:
                return Bind.lazy_eval(self[0], self[1], self[2])
            else:
                return Bind.lazy_eval(self[0], self[1] + args, self[2] | kwargs)

        def fix(self):
            self.fixed = not self.fixed
            return self

    def __new__(cls, func, *args, **kwargs) -> Wrapper:
        return cls.Wrapper([func, args, kwargs])


    @staticmethod
    def lazy_eval(func, args = (), kwargs = {}):
        """Depth-first evaluation of nested function/argument bindings."""
        func = func() if isinstance(func, Bind.Wrapper) else func
        args = tupler(arg() if isinstance(arg, Bind.Wrapper) else arg for arg in tupler(args))
        kwargs = {k: v() if isinstance(v, Bind.Wrapper) else v for k, v in kwargs.items()}

        return func(*args, **kwargs)

"""""
Do this to evaluate Binds recursively through ALL data structures, not just immediate Bind nestings.
This might not be the best usage because the user cannot use Bind objects in a data structure without evaluating
everything at the same time.  Adding a keyword argument to change the desired behaviour might be the right course
but for menucmd, it does not matter.

    
    def lazy_eval(func, args = (), kwargs = {}):
        func = func() if isinstance(func, Bind.Wrapper) else func

        def r_eval(data):
            if isinstance(data, Bind.Wrapper):
                return data()
            elif isinstance(data, list | tuple):
                return type(data)(r_eval(x) for x in data)
            else:
                return data

        args = tupler(r_eval(arg) for arg in tupler(args))
        kwargs = {k:r_eval(v) for k, v in kwargs.items()}
    
        return func(*args, **kwargs)
"""""
