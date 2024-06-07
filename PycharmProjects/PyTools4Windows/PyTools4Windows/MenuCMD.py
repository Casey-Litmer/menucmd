

#Add to Expansion Lib!!!!!!!!!d
# !!!!!!!!
def tupler(a) -> tuple:
    try:
        return tuple(a)
    except TypeError:
        return (a,)


class Menu():
    #Menu.result captures the output of the last called function in a chain to use in composition
    #return Menu.escape in a function to return to the menu from which it is called
    #
    result = object()
    escape = object()
    __END__ = object()

    def __init__(self,
                 name = "Choose Action",
                 exit_to = lambda: Menu.__END__,
                 exit_key = "e",
                 exit_message = "exit",
                 empty_message = "--*No Entries*--"
                 ):
        self.name = name
        self.exit_to = exit_to
        self.empty_message = empty_message
        self.menu_display_list = []
        self.menu = {}
        self.exit = (exit_key, exit_message, (exit_to, ()))
        self.update_menu(self.exit)


    def __call__(self):
        if not self.menu_display_list[:-1]:
            print(self.empty_message)
            return self.exit_to()
        show = f"\n{self.name}:\n" + "\n".join(self.menu_display_list) + "\n"
        selection = input(show)
        if selection not in self.menu.keys():
            print("--*Invalid Selection*--")
            return self()
        switch = self.menu[selection]
        #
        result = None
        while len(switch) >= 2:
            func = switch[0]
            args = tupler(x if x != Menu.result else result for x in tupler(switch[1]))  #compose result
            result = func(*args)
            switch = switch[2:]
            if result == Menu.escape:
                return self()
        return result if result != None else self()

    def append(self,*data):
        self.menu_display_list = self.menu_display_list[:-1]  #Removes exit; reconnects it in the loop at the end
        for n in data + (self.exit,):
            self.update_menu(n)

    def update_menu(self,data):
        self.menu_display_list.append(self.display(data))
        self.menu[data[0]] = data[2]

    def display(self, data):
       return f"[{data[0]}]- {data[1]}"


#----------------------------------------------------------------------------------------------------------------------
#Builtins
YesNo_ver = Menu(name = "Are you sure?", exit_to = lambda: False)
YesNo_ver.append(("x", "yes", (lambda: True,())))



#----------------------------------------------------------------------------------------------------------------------
"""""
A = Menu()
B = Menu(exit_to = A)
C = Menu(exit_to = A)

A.append(
    ("x", "print x, then print hello, then go to B", (print,("x"), lambda x: 2*x,(10), print,("result:",Menu.result), B,())),
          ("z", "Go to B", (B,())),
)
B.append(
    ("a","print a, then go to C", (print, ("a"), C, ())),
)


A()
"""""