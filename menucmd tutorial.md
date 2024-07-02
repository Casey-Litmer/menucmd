

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
*Note on Syntax:*

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
("x", "hello world program", (print, "Hello World",))
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




-----------------------------------------------------------------------------------------------------
    









