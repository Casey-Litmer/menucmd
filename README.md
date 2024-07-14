Getting Started
-
-----------------------------------------------------------------------------------------------------
MenuCMD is a library designed to easily create simple command line menus in a functional programming style.
The main goal is to separate functions from the way in which they are composed and how the user navigates them.


This module can be used in several ways:

- as a debugging tool
- as a dedicated command line application interface
- as a framework for delayed function evaluation

Separating navigation from function definitions allows the user to later repurpose a program to run automatically
without relying on user input.  What one creates as a command line interface one day, can easily be automated
the next.  

Other features such as lazy evaluation with the `Bind` class can also be used independently from the menu 
interface for your functional programming needs.

*For developers wishing to contribute to this module, a test script is included to ensure all
features work correctly between changes.  Feel free to update it as you see fit!*


1). Hello World
-

-----
### Initializing a Menu

Start by importing the `Menu` class. 

```
from MenuCMD import Menu
```

Create a new menu with a custom name.  
This is what will appear at the top of the menu when run.

```
#Create New Menu
menu1 = Menu(name = "First Menu")
```
-------
### Menu Item Format
You can add one or more items to a menu with the `append` method.  
An item is a `tuple` composed of a key, a message, and another `tuple`
containing a chain of functions and arguments. 

```
("key", "message", (func1, (*args1), func2, (*args2),))
```

-----
### Writing Arguments
When the user selects an item, **func1** will run with **args1**, then **func2** will run with **args2**.  

If a function only has one argument, you can simply write the pair as **(func1, arg1)**. \
**arg1** will automatically be wrapped as a `tuple`.  

**If **arg1** is itself a tuple, write **(arg1,)**.  Otherwise its contents will be interpreted as separate arguments!*

It is generally best practice to
keep the singleton tuple notation **(x,)** but is not strictly necessary.

-------

To add an item that prints 'hello world!' append the following:
```commandline
("x", "hello world program", (print, "Hello World!"))
```
This will display "hello world program" on the menu, and run the **print** function with argument "Hello World!"
when the user inputs "x".

To append item(s) to a menu:

```
#Add an Item
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    )),
    item2,
    item3,
    ...
)
```
*All menu items will appear in the order of appension.*

----
### Running 'Hello World'
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

#Run menu
menu1()
```

The result should look like:
```commandline
First Menu
[x]- hello world program
[e]- exit
```
Inputing 'x' will print the desired text, returning to the menu:
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

In addition to the items you add, all menus will automatically add an exit key at the end of the list which
will break out of the menu by default.  (This behaviour can be changed with the menu initialization)

When there is no more code to be run after the menu breaks, the program ends.


2). Multiple Menus
-
----
### Defining Two Menus
Menus can open other menus by running them as functions allowing the user to navigate through a deeper menu structure.

First create a new `Menu` instance in the same way as **menu1**:

```commandline
#Create New Menus
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu")
```
Then, add another entry to **menu1** that runs **menu2** with no arguments:

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

If we run the code and navigate to **menu2**, the following will happen:

```commandline
First Menu
[x]- hello world program
[a]- menu2
[e]- exit
a
--*No Entries*--

Process finished with exit code 0
```

We defined no entries for **menu2** so it automatically exits and, subsequently, the program, 
as **menu1** has no more code to run.  

*This results in the same outcome as pressing the exit key in **menu2**.*

-----------------------
### Exit Key Behaviour
The behaviour of the exit key can be changed with three keyword arguments
in a menu initiliazation:
```commandline
#exit_to : a function to be called on exit
#exit_key : the key to press (default 'e')
#exit_message : the message displayed on the menu (default 'exit')
```
----
To change the exit key behaviour to return to **menu1**, for example, 
we can change the `exit_to` tag in the definition of **menu2** and the message it displays:

```commandline
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", exit_to = menu1, exit_message = "to menu1")
```

This will call **menu1** when the exit key is pressed or when **menu2** is empty.

*Additionally, you can change the `empty_message` keyword argument to change what message is displayed:*

```commandline
Menu(empty_message = "No more functions to run!")
```

------
### Adding More Entries

Let's add some entries to **menu2**:

```commandline
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", exit_to = menu1, exit_message = "to menu1")

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
        print, "Happy Birthday!"
    )),
    ("c", "merry christmas", (
        print, "Merry Christmas!", menu1, ()
    )),
)

#Run Menu
menu1()
```
Pressing 'b' will print 'Happy Birthday!' and return to **menu2**. Pressing 'c'
will print 'Merry Christmas!' and return to **menu1**.  This is because the second item runs the `print` function 
 first, and then calls **menu1**. The first item, however, does not call **menu1** so it returns to
**menu2** automatically.


---
### End Chain Behaviour

The default behaviour of a `None`-type return of the function chain can be changed
with the `end_to` keyword:
```commandline
#end_to : function to be called when the last function of a chain returns None
```

*By default, if the **last** function in a chain returns
`None`, the current menu will open **itself** after all functions are executed.*

----
### Serializing End Returns

The `print` function always returns `None`, so if you want all of the items in menu2 to return to menu1, you can 
set   
`end_to` = **menu1**,  and neglect chaining **menu1** at the end of the entry.

```commandline
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", 
    exit_to = menu1, exit_message = "to menu1",
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

This will not work for all functions, but for very simple menus, where the last function
always returns `None`, the `end_to` tag is a simple way to serialize menu behaviour.


3). Function Composition
-
--------
### Using the Result Type
The `result` type allows the user to compose function returns in a chain.  
Let's create a menu item that asks for a
number as input, squares it, and then prints the result.

For sake of terseness, redefine the namespace of `Menu.result` above the menu declarations.
```commandline
result = Menu.result

menu1 = Menu(name = "Function Composition")
```

The first function in the chain asks the user for a number, the second function converts it to `float`, the third function
squares it, and the last function prints it.

`input -> float -> square -> print`  =>  `print(square(float(input())))`

Use the `result` object for the argument of each consecutive function in the item:

```commandline
menu1.append(
    ("n", "square a number", (
      input, "number ", 
      float, result, 
      lambda n: n**2, result, 
      print, result
    )),
)
```
When the user selects an item, the result of each function is stored into the `result` object and
retrieved when calling the next function. A function may have `result` as any of its arguments as long as the chain composes types.

You can also substitute `result` for functions if the previous return type is a `function`.

```
#func1: *args1 -> function

(func1, (*args1), result, (*args2))  =>  (func1(*args1))(*args2)  
```

--------
### Using Past Results

The `result` object can also be indexed to retrieve all past results in a chain.

By default, it is indexed at -1, which is the previous return value.
```
result := result[-1]
```

The indexing works exactly the same as a list.  

If you want the first result in the chain, write `result[0]`.\
The result before the last; `result[-2]`.\
etc...

```commandline
# func1: () -> 1
# func2: x -> x+1
# func3: x -> x*2
# func4: x -> x**3

                ._________________________________________________.               
     .__________|_________.___________________.                   |
     |          |         |                   |                   |
     |          |         V                   V                   V
(func1, (), func2, (result[-1],), func3, (result[0],), func4, (result[-2],))
      |           |                   |                  |
      V           |                   |                  |
  result[0] = 1   V                   |                  |
             result[1] = 2            V                  |
                                  result[2] = 2          V
                                                     result[3] = 8    


```

For example, if we also wanted to print the pre-squared `float` value, we can add:
```commandline
#Create Menus
result = Menu.result

menu1 = Menu(name = "Function Composition")


#Append Items
menu1.append(
    ("n", "square a number", (
      input, "number: ", 
      float, result, 
      lambda n: n**2, result, 
      print, result, 
      print, result[1]  
    )                   #result[1] prints the second result (= result[-3])
)


#Run
menu1()
```


-------
### Using the Bind Class

The `Bind` class allows lazy evaluation of functions.  If the arguments defined in a menu item are not determined yet,
or a previous result must be converted before the menu substitutes its value, the `Bind` class will hold off evaluating a 
function until it needs to.

Start by importing `Bind` into a convenient namespace:
```commandline
from MenuCMD import Menu, Bind as B
```

An object of the `Bind` class is essentially a *callable* function/argument(s) pair of the form
```commandline
B(func, *args)
```
The object takes a depth-first approach to evaluation so the deepest nested `Bind` object 
will be evaluated first, and all the way up.

```commandline
B(func1, B(func2, B(func3, *args)))

#Evaluates to:
func1(func2(func3(*args)))
```
When a menu runs its function chains, it will evaluate all nested `Bind` objects as required.

*Outside of integrated menu usage, a `Bind` object can be called with no arguments and it will return its function
evaluated with its arguments.*

```commandline
lazy_func = B(func, *args)

lazy_func() -> func(*args)
```

By default, if you don't use `Bind` in a menu item, and set the internal **args** to `result`, Python will attempt
to evaluate **func3(result)** before the item is even appended to the menu.  But **result** *doesn't exist yet!*

A different way to appraoch the square number entry is to bind `float` with `result` and use it as the argument
to the squaring function:

```commandline
from MenuCMD import Menu, Bind as B

#Create New Menu
result = Menu.result

menu1 = Menu(name = "Function Composition")


#Add Items
menu1.append(
    ("n", "square a number", (
        input, "number: ", 
        float, result, 
        lambda n: n**2, result, 
        print, result
    )),

    ("m", "square a number (bind result)", (
        input, "number: ", 
        lambda n: n**2, B(float, result), 
        print, result
    ))
)


#Run Menu
menu1()
```
This will effectively wait to evaluate the argument for lambda until `result` is known, 
and then converts it to `float`.

------
### Binding Functions and Kwargs

Additionally, `Bind` objects can be nested in both the function and arguments. 

For example, this is a completely valid `Bind` object:
```commandline
B(B(B(func1, *args1), *args2), B(func2, *args3))

#Evaluates to:
((func1(*args))(*args2))(func2(*args3))
```
If a **function** is undetermined, then it can also wait until the very last minute.

*Furthermore, `Bind` works exactly the same with keyword arguments.*
```commandline
B(func, *args, **kwargs)
```

4). Other Menu Attributes
-
-----
### Using kwargs

If a function also takes keyword arguments, use the `kwargs` wrapper from `Menu`. \
`kwargs` is simply a copy of `dict`.  You may either wrap a set of keyword arguments 
or input a dictionary:

```commandline
kwargs = Menu.kwargs
```
```
menu1.append(
    ("x", "function with kwargs", (
        func, (*args, kwargs(kw1 = "a", kw2 = "b"))
    ))    
)
```
Or
```
menu1.append(
    ("x", "function with kwargs", (
        func, (*args, kwargs({"kw1":"a", "kw2":"b"})})
    ))  
)
```
Both will evaluate to the same.  If you do not wrap a dictionary with `kwargs`, it will be 
interpreted as an argument.

----

### Using Manual Escapes

The `escape` type allows for manually breaking from a menu before a chain completes.  

```commandline
escape = Menu.escape
```

If *any* function in the chain returns `escape`, no following functions will be executed and the 
menu will instead run a different function.

By default, if an `escape` object is returned, the menu will return to itself but the behaviour 
can be changed on menu initialization:
```commandline
# escape_to : a function to be called on manual escape
```

For example, define a function that returns `escape` if its input is empty:
```commandline
def check_if_empty(x):
    if x:
        return x
    else:
        return Menu.escape
```

Then, say, if it isn't empty, print the string in reverse:

```commandline
menu2.append(
    ("x", "print if not empty", (
        input, "Input a string ", 
        check_if_empty, result,    #nothing will run after here if escape is returned
        print, "reversed:", 
        print, B(lambda s: s[::-1], result[-2])
    ))
)
```

While this module is designed to allow complete independence of menu structures and functions, 
the manual escape is the one exception to the rule.  Although, in some cases, this can 
be avoided with the builtin `escape_on` and `f_escape` functions covered in *Section 5)*.



### Using Matching Keywords

----

If a menu *exits*, *ends*, or *escapes* to the same function, you can optionally use matching
keywords to avoid writing the arguments multiple times.

For example, instead of writing
```commandline
menu1 = Menu()

menu2 = Menu(exit_to = menu1, end_to = menu1, escape_to = menu1)

menu3 = Menu(exit_to = menu2, end_to = menu1, escape_to = menu1)
```

you can use the `Menu.exit_to` and `Menu.end_to` keyword objects:

```commandline
menu1 = Menu()

menu2 = Menu(exit_to = menu1, end_to = Menu.exit_to, escape_to = Menu.exit_to)

menu3 = Menu(exit_to = menu2, end_to = menu1, escape_to = Menu.end_to)
```

Setting any of the keyword arguments to `Menu.exit_to` will mirror the value of `exit_to`, 
likewise for `Menu.end_to`.

The order of precedence for the `Menu.exit_to` and `Menu.end_to` objects is as follows:
```commandline
                           .______________.
           ._________._____|___________.  |
           |         V     |           V  V
exit_to    |       end_to  |        escape_to
   |       |         |     |
   V       |         V     |
Menu.exit_to     Menu.end_to
```

`exit_to` will always be defined first, `end_to` second, and lastly `escape_to`.  There is hence no 
*Menu.escape_to* object.

Matching keywords serve as a nifty way to serialize `Menu` parameters.

5). Builtins
-
------

So far, this tutorial has approached creating menus as separate entities from the functions they compose.
While this is an intended feature of the module, you may still use menus within functions.  MenuCMD has a number
of builtin functions to create template menus and to make in-line composition easier.  

*This list is subject to change as community members can submit their own if anyone finds any common uses or improvements for MenuCMD!* 


## In-line Functions

These functions are designed to be composed in menu item function chains to control command flow.

-----

### escape_on(x, value) -> value | Menu.escape
```
Returns an escape if the two arguments are equal, or both Truthy or both Falsy.
Otherwise, returns value.
```
Use this to break function chain execution on an equality condition.  For example, to *escape* the menu on
empty input write:
```commandline
(input, "input", escape_on, ("", result), print, "your input:", print, result[-2])
```
This will bypass the print statements if the user inputs an empty string and calls whatever `escape_to` 
is defined as.

-----
### f_escape(*args, **kwargs) -> Menu.escape
```
Polymorphic in-line escape function.
```
This function takes any **args** and **kwargs** and returns the `escape` object.

*For nerds, this can be viewed as the collection of terminal morphisms in **Hom(x, escape)***

----
### f_switch(n: int | bool, funcs: tuple[function]) -> Bind.Wrapper


```commandline
Returns a lazy function of type (int -> function)
```
Takes an `int` and a `tuple` of functions and returns a `Bind` that indexes each function.

Use this if you want a previous result to change which function runs next.
```commandline
functions = (func1, func2, func3)

(input, "choose a function (0-2) ", f_switch(result, functions), (*args))
                                         #Call f_switch
```
Since `f_switch` returns a `Bind` object that subsequently returns a `function`, be sure to *call*
it in the function slot of the chain.  Whatever function it switches to upon evaluating `result` (an integer), 
will then be evaluated with **args**, so be sure that all of the functions in the `tuple` have the same domain!


-----
## Builtin Menus

These functions construct temporary menus that determine their returns.  Optionally, all menu **kwargs**
can be passed through them to change the behaviour and appearance of the menus they invoke.

*Avoid changing the `exit_to` keyword argument as it will change the return type of the functions!*

------

### yesno_ver(**kwargs) -> bool

```commandline
Simple yes/no verification returning bool
```
Asks the user a yes/no question, and returns the bool of the result.

```commandline
yesno = yesno_ver()

print(yesno)
```
 V V V V V V V 
```commandline
Are you sure?
[x]- yes
[e]- cancel
x
True
```
```commandline
Are you sure?
[x]- yes
[e]- cancel
e
False
```

-----
### edit_list(entries: list | tuple, **kwargs) -> list | tuple
```commandline
Delete items in a list/tuple; returns updated list/tuple
```
Takes a `list` or `tuple` and displays a menu of numbered items to delete.  Upon each selection, the menu
will display itself again with the item removed and will only return the updated `list`/`tuple` when the
exit key is pressed.

```commandline
L = ['a','b','c','d','e']

L = edit_list(L)

print(L)
```
 V V V V V V V 
```commandline
Edit List
[0]- a
[1]- b
[2]- c
[3]- d
[4]- e
[e]- exit
0

Edit List
[0]- b
[1]- c
[2]- d
[3]- e
[e]- exit
2

Edit List
[0]- b
[1]- c
[2]- e
[e]- exit
2

Edit List
[0]- b
[1]- c
[e]- exit
e
['b', 'c']
```