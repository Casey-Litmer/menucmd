

Getting Started
-
-----------------------------------------------------------------------------------------------------
1). Hello World
-

Start by importing the Menu object. 

```
from MenuCMD import Menu
```

Create a new menu with a custom name.

```
#Create New Menu
menu1 = Menu(name = "First Menu")
```

You can add one or more items to a menu with the append method.  
An item is composed of a key, a message, and a function/argument chain
contained in a tuple. 

```
("key", "message", (func1, (*args1), func2, (*args2),))
```
______________________
**Note on Syntax:*

If there is only one argument to a function, you can drop the tuple notation (x,) 
and simply write x.
This works unless the argument is itself a tuple.  It is generally best practice to
keep the singleton tuple notation but is not strictly necessary.


When the user selects an item, func1 will run with args1, then func2 will run with args2
If a function only has one argument, you can simply write the pair as (func1, arg1).
Arg1 will automatically be wrapped as a tuple*.  

*If arg1 is a tuple, write (arg1,) -otherwise its contents will be interpreted as separate arguments.
____________________________

The item for the hello world program will be the following:
```commandline
("x", "hello world program", (print, "hello world",))
```
This will display "hello world program" on the menu, and run print with argument "Hello World"
when the user inputs "x".

To append item(s) to a menu:

```
#Add an Item
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    )),
    item2,
    item3,...
)
```
(All menu items will appear in the order of appension)

Now all that's left is to run the menu by calling it with no arguments.

```
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")

#Add an Item
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    ))
)

menu1()
```

The result should look like:
```commandline
First Menu
[x]- hello world program
[e]- exit

```
and inputing 'x' will print the desired text, returning to the menu
```commandline
First Menu
[x]- hello world program
[e]- exit
x
hello world!

First Menu
[x]- hello world program
[e]- exit
```

All menus will automatically add an exit key at the end of the list which
will break out of the menu by default.  (this behaviour can be changed with the menu initialization)

-----------------------------------------------------------------------------------------------------
2). Multiple Menus
-
Menus can open other menus by running them as functions.

First create a new menu instance in the same way as menu1:

```commandline
#Create New Menus
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu")
```

Then add an entry in menu1 that runs menu2 with no arguments:

```commandline
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    )),
    ("a", "menu2", (
        menu2, ()
    ))
)
```

If we run the code and navigate to menu2, the following will happen:

```commandline
First Menu
[x]- hello world program
[a]- menu2
[e]- exit
a
--*No Entries*--

Process finished with exit code 0
```

We defined no entries for menu2 so it automatically exits the program as the
menu1 call is complete.  This is the same result as pressing the exit key.


The behaviour of the exit key can be changed with three keyword arguments
in a menu initiliazation:
```commandline
exit_to : #a function to be called on exit
exit_key : #the key to press (default 'e')
exit_message : #the message displayed on the menu (default 'exit')
```
To change the exit key behaviour to return to menu1, for example, 
we can change the 'exit_to' tag in the definition of menu2, as well as
the key to press and the message it displays:

```commandline
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", exit_to = menu1, exit_key = "m", exit_message = "to menu1")
```

This will call menu1 when the exit key is pressed or when menu2 is empty.

Let's add some entries to menu2:

```commandline
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", exit_to = menu1, exit_key = "m", exit_message = "to menu1")

#Add Items
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    )),
    ("a", "menu2", (
        menu2, ()
    ))
)

menu2.append(
    ("b", "happy b-day", (
        print, "happy birthday!"
    )),
    ("c", "merry christmas", (
        print, "merry christmas!", menu1, ()
    )),
)

#Run Menu
menu1()
```
Pressing 'b' will print the line and return to menu2 but pressing 'c'
will print the line and return to menu1.  This is because it runs print with "merry christmas!"
first, and menu1 with () after.  

*By default, if the last function in a chain returns
None, the current menu will open itself after all functions are executed.*

The default behaviour of a None-type return of the function chain can be changed
with the end_to keyword:
```commandline
end_to : #function to be called when the last function of a chain returns None
```

print returns None, so if you want all of the options to return to menu1, you can 
set:  *end_to = menu1*,  and neglect chaining menu1 at the end of the entry.

```commandline
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", 
    exit_to = menu1, exit_key = "m", exit_message = "to menu1",
    end_to = menu1
    )

#Add Items
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    )),
    ("a", "menu2", (
        menu2, ()
    ))
)

menu2.append(
    ("b", "happy b-day", (
        print, "happy birthday!"
    )),
    ("c", "merry christmas", (
        print, "merry christmas!"
    )),
)

#Run Menu
menu1()
```

This will not work for all functions, but for very simple programs where the last function
always returns None, the end_to tag is a simple way to serialize menu behaviour.

----------------------------------------------
3). Function Composition
-



