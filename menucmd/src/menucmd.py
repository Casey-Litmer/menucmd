import sys;
from copy import copy;
from macrolibs.typemacros import tupler, dict_union;
from macrolibs.typemacros import replace_value_nested, copy_type, maybe_type;
from .global_objs import MenuEscape;
from .result import Result;
from .trampoline import MenuManager;



#==================================================================================
#Menu Class

class Menu():
    #Matching Keywords
    exit_to = object();  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object();   #

    #Keyword Objects
    result = Result(-1);
    escape = MenuEscape;
    self = object();

    __END__ = type("Menu.__END__", (object,), {});  #Terminal Object
    id = lambda x:x;                                #Identity morphism

    #Kwargs Wrapper
    class kwargs(dict):
        pass;

    #==================================================================================
    def __init__(self,
                 name = "Choose Action",
                 exit_to = lambda: Menu.__END__,
                 end_to = None,
                 escape_to = None,
                 arg_to = lambda x:x,
                 exit_key = "e",
                 exit_message = "exit",
                 empty_message = "--*No Entries*--",
                 exit_on_empty = True                  #TODO: ADD TO DOCS
                 ):
        #Pass parameters
        self.name = name;
        self.empty_message = empty_message;
        self.exit_on_empty = exit_on_empty;
        self.exit_to, self.exit_key, self.exit_message = exit_to, exit_key, exit_message;

        #Replace self references in arg_to if it is a Bind.Wrapper object
        self.arg_to = replace_value_nested(tupler(arg_to), Menu.self, self)[0];

        #Define breakpoints and then switch out matching keywords (if any)
        self.end_to = self if end_to is None else end_to;
        self.escape_to = self if escape_to is None else escape_to;
        self.apply_matching_keywords();

        #Init menu data
        self.menu_item_list = [];         #de jure list of items
        self.menu_display_list = [];      #["[key]- message"]
        self.menu = {};                   #{"key":(function-arg chain)}

        #Set exit option
        self.exit = ();
        self.ch_exit();

        #Tracked attributes for current result chain
        self.tracked_attributes = {};

    #==================================================================================
    def __call__(self, arg = None):
        """Runs menu with 'arg' asking for user input.
        Selection runs the item's function chain where each nth function has
        access to Menu.result[0 -> n]; (n in [0,1,2...])

        Menu.result[0] == arg
        """
        #Reset tracked attributes
        self.tracked_attributes= {};

        #List state logic
        if not self.menu_display_list[:-1] and self.exit_on_empty:
            #Exit on empty menu
            print(self.empty_message);
            selection = self.exit_key;
        
        #Print Menu And Get Input
        else:
            show = f"\n{self.name}\n" + "\n".join(self.menu_display_list) + "\n";
            print(show, end='');
            printed_lines = show.count('\n') + 1;
            selection = input(); 
            
            #Clear previous menu
            Menu.clear_lines(printed_lines);

        return MenuManager.manage_call(self, arg, selection);

        #Maybe do this in the future for None returns:
        #maybe_arg(self.replace_keywords(self.end_to, (), results)[0])(arg)
        #
        #It doesn't make sense to have two refs to result[0] = arg
        #but built-in behaviour switching via Bind based on past results might be better than
        #using inline functions to switch between a result return and a None return

    #==================================================================================
    def replace_keywords(self, func, args: tuple, results: list) -> tuple:
        """Replaces all inline self references with the current menu.
        Replaces all Menu.result objects with function results from the chain.

        Returns a tuple in the form (func, args, kwargs).

        'args' may also include all kwargs distinguished by the Menu.kwargs wrapper.
        """
        #Replace self reference
        func = replace_value_nested(tupler(func), Menu.self, self)[0];
        args = replace_value_nested(tupler(args), Menu.self, self);

        #Tuple type to 'de-tuple'
        expanded = copy_type(tuple, "expanded");

        #Replace Result Keywords by Attribute
        for tag, val in self.tracked_attributes.items():
            func = replace_value_nested(tupler(func), Result(0).__getattr__(tag), val)[0];
            args = replace_value_nested(tupler(args), Result(0).__getattr__(tag).expand(), maybe_type(expanded, val));
            args = replace_value_nested(tupler(args), Result(0).__getattr__(tag), val);

        #Replace Result Keywords by Position
        N = len(results);
        for n in range(-N, N):
            #Detect if a result has an attribute and add first declaration to tracked attributes
            def track_attr(R, value):
                if R.__attr__ is not None and R.__attr__ not in self.tracked_attributes.keys():
                    self.tracked_attributes[R.__attr__] = value;
                return value;
            func = replace_value_nested(tupler(func), Result(n), results[n], callback= track_attr)[0];
            args = replace_value_nested(tupler(args), Result(n).expand(), maybe_type(expanded, results[n]), callback= track_attr);
            args = replace_value_nested(tupler(args), Result(n), results[n], callback= track_attr);

        #Separate args/kwargs
        kwargs = dict_union(tupler(x for x in args if isinstance(x, Menu.kwargs)));
        args = tupler(x for x in args if not isinstance(x, Menu.kwargs));

        #'Uninterprets' tupler for expanded results.  Allows inline notation for (*args) ~ result.expand()
        args = Menu.expand_in_place(args, expanded);

        return (func, args, kwargs);

    @staticmethod
    def expand_in_place(A: tuple | list, expand_type: type):
        """Recursively expand all marked tuples/lists in a data structure
        (a, [b, expanded((c, d))]) -> (a, [b, c, d])
        """
        new = type(A)();
        for x in A:
            #Append all elements if marked as 'expanded'
            if isinstance(x, expand_type):
                new += type(A)(x);
            #Run in nesting (recursion)
            elif isinstance(x, tuple | list):
                new += type(A)(((Menu.expand_in_place(x, expand_type)),));
            #Do nothing
            else:
                new += type(A)((x,));
        return new;

    #==================================================================================

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            new_menu = copy(self); new_menu.clear();
            new_menu.append(*self.menu_item_list[:-1][idx]);
            return new_menu;
        return self.menu_item_list[idx];

    def append(self, *data):
        """
        Append data to menu in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))
        --*{forces exit key to the end of the list}*--
        """
        self.menu_display_list = self.menu_display_list[:-1];
        self.menu_item_list = self.menu_item_list[:-1];
        menu_item_keys = list(map(lambda it: it[0], self.menu_item_list));

        for item in data + (self.exit,):
            if item[0] not in menu_item_keys:
                menu_item_keys.append(item[0]);
                self.menu_item_list.append(item);
                self.update_menu(item);

    def clear(self):
        """Clears all items from the menu"""
        self.menu_item_list, self.menu_display_list = [], [];
        self.menu = {};
        self.update_menu(self.exit);

    def insert(self, n: int, *data):
        """Insert data at position n in the form:
        ('key', 'message', (func1, (*args1), func2, (*args2),...))"""
        _data = self.menu_item_list[:-1][:n] + [*data] + self.menu_item_list[:-1][n:];
        self.clear();
        self.append(*_data);

    def delete(self, n: int, k: int = 1):
        """Delete k menu entries starting at position n"""
        _data = self.menu_item_list[:-1][:n] + self.menu_item_list[:-1][n+k:];
        self.clear();
        self.append(*_data);

    def update_menu(self, data):
        """Updates menu lists"""
        self.menu_display_list.append(f"[{data[0]}]- {data[1]}");
        self.menu[data[0]] = data[2];

    def ch_exit(self, exit_to = None, exit_key = None, exit_message = None) -> None:
        """Changes the properties of the exit key and appends it to the list"""
        self.exit_to = exit_to if exit_to else self.exit_to;
        self.exit_key = exit_key if exit_key else self.exit_key;
        self.exit_message = exit_message if exit_message else self.exit_message;
        self.exit = (self.exit_key, self.exit_message, (self.exit_to, ()));        #will attempt to fill in argument with arg
        self.append();

    def apply_matching_keywords(self):
        """Apply matching keywords for end_to and escape_to in order"""
        self.end_to = self.exit_to if self.end_to is Menu.exit_to else self.end_to;
        self.escape_to = self.exit_to if self.escape_to is Menu.exit_to else self.escape_to;
        self.escape_to = self.end_to if self.escape_to is Menu.end_to else self.escape_to;

    @staticmethod
    def clear_lines(printed_lines: int) -> None:
        """Clears previous menu from terminal"""
        for _ in range(printed_lines):
            sys.stdout.write("\x1b[1A");  #Move cursor up
            sys.stdout.write("\x1b[2K");  #Clear line
        sys.stdout.flush();