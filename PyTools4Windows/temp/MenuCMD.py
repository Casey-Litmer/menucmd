from macrolib.typemacros import tupler, dict_union



#TODO:
#make a search funtion to parse through data structures for keywords like Menu.result
#should be relatively simple (famous last words much?)
#
#more complicated would be to introduce something akin to lazy evaluation for embedding keywords into function args
#maybe start by using some constructor like:  Menu.Entry("key", "message", (func, (*args),..))
#and have it lazily evaluate all of the contents???
#
#
#also find common menu patterns and add more macros/builtins for them



class Menu():
    result = object()
    escape = object()
    __END__ = object()

    exit_to = object()  #Use as keyword for end_to to match exit_to:  Menu(end_to = Menu.exit_to)
    end_to = object()

    class kwargs(dict):
        pass
    class bundle(str): #in testing
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
        self.name = name
        self.exit_to = exit_to

        self.end_to = self if end_to is None else \
            (self.exit_to if end_to is Menu.exit_to else end_to)

        self.escape_to = self if escape_to is None else \
            (self.exit_to if escape_to is Menu.exit_to else
             (self.end_to if escape_to is Menu.end_to else escape_to))

        self.empty_message = empty_message

        self.menu_display_list = []
        self.menu = {}

        self.exit = (exit_key, exit_message, (exit_to, ()))
        self.update_menu(self.exit)



    def __call__(self):
        if not self.menu_display_list[:-1]:
            print(self.empty_message)
            return self.exit_to()

        show = f"\n{self.name}\n" + "\n".join(self.menu_display_list) + "\n"
        selection = input(show)

        if selection not in self.menu.keys():
            print("--*Invalid Selection*--")
            return self()

        switch = self.menu[selection]

        result = None
        while len(switch) >= 2:
            func = switch[0] if switch[0] is not Menu.result else result

            args = tupler(x if x != Menu.result else result for x in tupler(switch[1])
                          if not isinstance(x, Menu.kwargs))
            kwargs = dict_union(tupler(x for x in tupler(switch[1]) if isinstance(x, Menu.kwargs)))

            for key in kwargs:
                if kwargs[key] == Menu.result:
                    kwargs[key] = result

            result = func(*args, **kwargs)
            switch = switch[2:]

            if result == Menu.escape:
                return self.escape_to()

        return result if result is not None else self.end_to()


    def append(self,*data):
        self.menu_display_list = self.menu_display_list[:-1]
        for n in data + (self.exit,):
            self.update_menu(n)


    def update_menu(self,data):
        self.menu_display_list.append(self.display(data))
        self.menu[data[0]] = data[2]


    @staticmethod
    def display(data):
       return f"[{data[0]}]- {data[1]}"


    #Testing
    def cumulate_monad(self, *channels):
        def decorator(func):
            def wrapper(*args, **kwargs):
                _result = func(*args, **kwargs)
                for n, key in enumerate(channels):
                    self.bundle[key] = tupler(_result)[n]
                return _result
            return wrapper
        return decorator


#----------------------------------------------------------------------------------------------------------------------
#Builtins

def yesno_ver() -> bool:
    menu = Menu(name = "Are you sure?", exit_to = lambda: False, exit_message = "cancel")
    menu.append(("x", "yes", (lambda: True, ())))

    return menu()


def yesno_continue(continue_to, **kwargs):
    menu = Menu(name = "Continue?", exit_to = lambda: Menu.__END__, exit_message = "no", **kwargs)
    menu.append(("x", "yes", (continue_to, ())))

    return menu()


def edit_list(entries: list | tuple, **kwargs) -> list | tuple:
    menu = Menu(**kwargs, exit_to = lambda: entries)

    for n, entry in enumerate(entries):
        menu.append((str(n), str(entry), (edit_list, (entries[:n] + entries[n+1:], Menu.kwargs(kwargs)))))

    return menu()




"""""

kwargs = Menu.kwargs
result = Menu.result

menu1 = Menu(name = "menu1")
menu2 = Menu(name = "menu2", exit_to = menu1)
menu3 = Menu(exit_to = menu1)


#Find a way to allow the bundle monad to statically toggle what menu lists appear.  May not be possible
#("menu key", (return values to toggle entry off on next menu call,))
@menu1.cumulate_monad(("a", (0,)))
def test(cutoff):
    return cutoff


menu1.append(
    ("x", "delete something", (yesno_ver, (), menu1, ())),
    ("a", "go to other menu", (menu2, ())),

)

menu2.append(
    ("h", "say hello", (print, ("hello",))),
    ("a", "go to menu3", (menu3, ())),
)


menu1()

"""""