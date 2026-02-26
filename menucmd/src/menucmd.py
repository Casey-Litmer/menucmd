import sys
from copy import copy
from macrolibs.typemacros import tupler, dict_union, list_union
from macrolibs.typemacros import replace_value_nested, maybe_arg, maybe_type
from .result import Result
from .bind import Bind
from .colors import *
from .item import Item
from .ansi_scheme import *
from colorama import just_fix_windows_console

just_fix_windows_console()

#==================================================================================
#Menu Class

class _Expand(tuple):
    """Internal wrapper to mark an iterable for expansion as function arguments."""
    pass

class _Kwargs(dict):
    """Wrapper for kwargs in menufunction composition"""
    pass

class Menu():
    #Matching Keywords
    exit_to = object()  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object()   #

    #Keyword Objects
    result = Result(-1)
    escape = object()
    self = object()
    kwargs = _Kwargs
    __END__ = type("Menu.__END__", (object,), {})  #Terminal Object
    id = lambda x:x                                #Identity morphism

    #==================================================================================

    def __init__(self,
                 name = "Choose Action",
                 invalid_key = "--*Invalid Key*--",
                 empty_message = "--*No Entries*--",
                 clear_readout = True,
                 arg_to = lambda x:x,
                 arg_to_first = True,
                 exit_to = lambda: Menu.__END__,
                 exit_key = "e",
                 exit_message = "exit",
                 colors = MenuColors(),
                 exit_colors = ItemColors(),
                 end_to = None,
                 escape_to = None,
                 #out_to = lambda x:x,
                ):
        # Menu
        self.name = name
        self.empty_message = empty_message
        self.invalid_key = invalid_key
        self.clear_readout = clear_readout

        # Arg
        self.arg_to = arg_to
        self.arg_to_first = arg_to_first

        # Exit
        self.exit_to= exit_to
        self.exit_key = exit_key
        self.exit_message =  exit_message
        
        # Colors
        self.colors = colors
        self.exit_colors = exit_colors

        #Init menu data
        self.menu_item_list: list[Item] = []         #de jure list of items
        self.menu_display_list = []                  #["[key]- message"]
        self.menu = {}                               #{"key":(function-arg chain)}

        #Define breakpoints, apply menu updates
        self.end_to = self if end_to is None else end_to
        self.escape_to = self if escape_to is None else escape_to
        self.apply_matching_keywords()
        self.replace_self_references()
        self.ch_exit()
        #TODO: group together?

        #Tracked attributes for current result chain
        self.tracked_attributes = {}

    #==================================================================================
    # Protocall
    #==================================================================================

    def __call__(self, arg = None):
        """Runs menu with 'arg' asking for user input.
        Selection runs the item's function chain where each nth function has
        access to Menu.result[0 -> n]; (n in [0,1,2...])

        Menu.result[0] == arg
        """
        #Reset tracked attributes
        self.tracked_attributes = {}

        #Evaluate arg_to and add 0th result (Before selection)
        if self.arg_to_first:
            result = maybe_arg(self.arg_to)(arg)
            results = [result]

        #List state logic
        if not self.menu_display_list[:-1]:
            #Exit on empty menu
            empty_ansi = self.colors.empty_message
            print(f"{empty_ansi}{self.empty_message}\x1b[0m")
            selection = self.exit_key
        else:
            #Print Menu And Get Input
            name_ansi = self.colors.name
            show = f"\n{name_ansi}{self.name}\x1b[0m\n" + "\n".join(self.menu_display_list) + "\n"
            print(f"{show}\x1b[0m", end='')
            printed_lines = show.count('\n') + 1
            selection = input()

            #Clear previous menu
            if self.clear_readout:
                Menu.clear_lines(printed_lines)

        #Refresh Menu On Invalid Input
        if selection not in self.menu.keys():
            invalid_ansi = self.colors.invalid_selection
            print(f"{invalid_ansi}--*Invalid Selection*--\x1b[0m")
            return self(arg)

        #Select Item
        func_chain = self.menu[selection]

        #Exit menu if exit_key pressed
        if selection == self.exit_key:
            return maybe_arg(func_chain[0][0])(arg)

        #Evaluate arg_to and add 0th result (After selection)
        if not self.arg_to_first:
            result = maybe_arg(self.arg_to)(arg)
            results = [result]

        #Evaluate Function Chain
        for pair in func_chain:
            #Get func/args pair
            func = pair[0]
            args = tupler(pair[1])

            #Replace Results and Separate args/kwargs
            func, args, kwargs = self.replace_keywords(func, args, results)

            #Evaluate Function
            result = Bind.lazy_eval(func, args, kwargs)

            #Manual escape
            if result is Menu.escape:
                return maybe_arg(self.escape_to)(arg)

            #End Loop
            results.append(result)

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

        #Replace Result Keywords by Attribute
        for tag, val in self.tracked_attributes.items():
            func = replace_value_nested(tupler(func), Result(0).__getattr__(tag), val)[0]
            args = replace_value_nested(tupler(args), Result(0).__getattr__(tag).expand(), maybe_type(_Expand, val))
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
            args = replace_value_nested(tupler(args), Result(n).expand(), maybe_type(_Expand, results[n]), callback= track_attr)
            args = replace_value_nested(tupler(args), Result(n), results[n], callback= track_attr)

        #Separate args/kwargs
        kwargs = dict_union(tupler(x for x in args if isinstance(x, Menu.kwargs)))
        args = tupler(x for x in args if not isinstance(x, Menu.kwargs))

        #'Uninterprets' tupler for expanded results.  Allows inline notation for (*args) ~ result.expand()
        args = tuple(Menu.expand_in_place(args))

        return (func, args, kwargs)

    #==================================================================================
    # API
    #==================================================================================

    def append(self, *items: Item):
        """
        Append items to menu in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))
        --*{forces exit key to the end of the list}*--
        """
        Menu.check_item_type(*items)

        self.menu_display_list = self.menu_display_list[:-1]
        self.menu_item_list = self.menu_item_list[:-1]

        for item in items + (self.exit,):
            self.menu_item_list.append(item)
            self.update_menu_lists(item)


    def clear(self):
        """Clears all items from the menu"""
        self.menu_item_list, self.menu_display_list = [], []
        self.menu = {}
        self.update_menu_lists(self.exit)


    def insert(self, n: int, *items):
        """
        Insert items at position n in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))
        """
        Menu.check_item_type(*items)

        _data = self.menu_item_list[:-1][:n] + [*items] + self.menu_item_list[:-1][n:]
        self.clear()
        self.append(*_data)


    def delete(self, n: int, k: int = 1):
        """Delete k menu entries starting at position n"""
        _data = self.menu_item_list[:-1][:n] + self.menu_item_list[:-1][n+k:]
        self.clear()
        self.append(*_data)


    def __getitem__(self, idx):
        if isinstance(idx, slice):
            new_menu = copy(self)
            new_menu.clear()
            new_menu.append(*self.menu_item_list[:-1][idx])
            return new_menu
        return self.menu_item_list[idx]
    
    #==================================================================================
    # Updates
    #==================================================================================

    def update_menu_lists(self, item: Item):
        """Updates menu lists with new Item"""
        colors = self.colors.merge(item.colors)
        key_ansi = colors.key
        dash_ansi = colors.dash
        message_ansi = colors.message

        self.menu_display_list = list_union(
            self.menu_display_list, 
            [f"{key_ansi}[{item.key}]\x1b[0m{dash_ansi}-\x1b[0m {message_ansi}{item.message}\x1b[0m"]
        )
        self.menu[item.key] = item.funcs


    def ch_exit(self, exit_to = None, exit_key = None, exit_message = None) -> None:
        """Changes the properties of the exit key and appends it to the list"""
        self.exit_to = exit_to if exit_to else self.exit_to
        self.exit_key = exit_key if exit_key else self.exit_key
        self.exit_message = exit_message if exit_message else self.exit_message
        self.exit = Item(
            key=self.exit_key, message=self.exit_message, 
            funcs=[(self.exit_to, ())], colors=self.colors.merge(self.exit_colors)
        )
        self.append()


    def apply_matching_keywords(self):
        """Apply matching keywords for end_to and escape_to in order"""
        self.end_to = self.exit_to if self.end_to is Menu.exit_to else self.end_to
        self.escape_to = self.exit_to if self.escape_to is Menu.exit_to else self.escape_to
        self.escape_to = self.end_to if self.escape_to is Menu.end_to else self.escape_to


    def replace_self_references(self):
        """Replaces Menu.self with self in builtin menu functions"""
        menu_funcs = { 'arg_to': self.arg_to, 'end_to': self.end_to, 'escape_to': self.escape_to }
        for key in menu_funcs:
            x_to = menu_funcs[key]
            replaced = self if x_to is Menu.self \
                else replace_value_nested(tupler(x_to), Menu.self, self)[0]
            setattr(self, key, replaced)

    #==================================================================================
    # Util
    #==================================================================================

    @staticmethod
    def expand_in_place(A: tuple | list):
        """Recursively expand all marked tuples/lists in a data structure
        (a, [b, expanded((c, d))]) -> (a, [b, c, d])
        """
        new = []
        for x in A:
            #Append all elements if marked as 'expanded'
            if isinstance(x, _Expand):
                new += list(x)
            #Run in nesting (recursion)
            elif isinstance(x, tuple | list):
                new += [Menu.expand_in_place(x)]
            #Do nothing
            else:
                new += [x]
        return type(A)(new)


    @staticmethod
    def clear_lines(printed_lines: int) -> None:
        """Clears previous menu from terminal"""
        if printed_lines <= 0:
            return
        #print(f"\x1b[{printed_lines}A\x1b[J", end='', flush=True)
        sys.stdout.write(f"\x1b[{printed_lines}A\x1b[J")
        sys.stdout.flush()

    #==================================================================================
    # Errors
    #==================================================================================

    @staticmethod
    def check_item_type(*items):
        for item in items:
            if not isinstance(item, Item):
                raise ValueError(f"{item} is not a valid Item")
            
        
    # Feeling a bit devilish here...
    # You really shouldn't use Menu.self in exit_to because it will create an infinite loop
    # but there are use cases with Bind in arg_to.  Screw trying to protect the fool
    # from herself I say! I will probably create much more dynamic crazy structure
    # on top of this library that will eventually find a use, but here it is
    # if it becomes a necessity:

    #def check_banned_self_references(self):
    #    banned_methods = { 'exit_to': self.exit_to }
    #    for method in banned_methods:
    #        def callback(old, _):
    #            if old == Menu.self:
    #                raise ValueError(f"Menu.self cannot be used in {method}")
    #        replace_value_nested(tupler(banned_methods[method]), Menu.self, None, callback=callback)
            