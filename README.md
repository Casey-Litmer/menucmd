# MenuCMD
```commandline
pip install menucmd
```
-----------------------------------------------------------------------------------------------------
MenuCMD is a library designed to easily create simple command line menus in a functional programming style.
The main goal is to separate function definitions from the way they are composed via user input.
It is currently the underlying basis of *PyTools4Windows (WIP)*.

This module can be used in several ways:

- as a debugging tool
- as a dedicated command line application interface
- as a framework for delayed function evaluation

Separating navigation from function definitions allows the user to repurpose a program to run automatically
inside a dedicated control flow without relying on user input. 

Other features such as lazy evaluation with the `Bind` class can also be used independently of the menu 
interface.

MenuCMD also comes with a simple domain-specific language associated with .mcmd files.


---
## Sections: 
### 1. Hello World
   - Initializing a Menu
     - `name`
   - Menu Item Format
   - Writing Arguments
   - Running 'Hello World'
### 2. Multiple Menus
   - Defining Two Menus
   - Exit Key Behaviour
      - `exit_to`
      - `exit_key`
      - `exit_message`
      - `empty_message`
   - Adding More Entries
   - `end_to`
   - Serializing 'None'-type Returns
### 3. Function Composition
   - `Menu.result` Type
   - Using Past Results 
     - `result[n]`
     - `result` attributes
     - `result.expand()`
   - `arg_to`
### 4. Lazy Evaluation via Bind
   - Using the `Bind` Class
   - Binding Functions and Kwargs
   - Calling a `Bind` Object
   - Note on Menu Composition
   - `Bind().fix()`
### 5. Menu Methods
   - `clear`
   - `delete`
   - `insert`
   - `append`
   - `ch_exit`
   - Menu Object Indexing
### 6. Other Menu Attributes
   - `Menu.kwargs`
   - `escape_to` and `Menu.escape`
   - `Menu.self`
   - `Menu.id`
   - Matching Keywords
### 7. MCMDlang
   - Formatting
   - `build_menus`
### 8. Builtins
   - In-line Functions
   - Builtin Menus
   - Dynamic Menus (WIP)


----
# Getting Started


1). Hello World
-

-----
### Initializing a Menu

Start by importing the `Menu` class. 

```
from menucmd import Menu
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
from menucmd import Menu

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

In addition to the items you add, all menus will automatically add an *exit key* at the end of the list which
will break out of the menu by default.  (This behaviour can be changed with the menu initialization)

When there is no more code to be run after the menu breaks, the program ends.

---
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
The behaviour of the *exit key* can be changed with three keyword arguments
in a menu initiliazation:
```commandline
#exit_to : a function to be called on exit
#exit_key : the key to press (default 'e')
#exit_message : the message displayed on the menu (default 'exit')
```
----
To change the *exit key* behaviour to return to **menu1**, for example, 
we can change the `exit_to` tag in the definition of **menu2** and the message it displays:

```commandline
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu", exit_to = menu1, exit_message = "to menu1")
```

This will call **menu1** when the *exit key* is pressed or when **menu2** is empty.

*Additionally, you can change the `empty_message` keyword argument to change what message is displayed:*

```commandline
Menu(empty_message = "No more functions to run!")
```

------
### Adding More Entries

Let's add some entries to **menu2**:

```commandline
from menucmd import Menu

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
### 'end_to'

The default behaviour of a `None`-type return of the function chain can be changed
with the `end_to` keyword:
```commandline
#end_to : function to be called when the last function of a chain returns None
```

*By default, if the **last** function in a chain returns
`None`, the current menu will open **itself** after all functions are executed.*

If `end_to` has any arguments, it will run with the argument passed in the menu call.

----
### Serializing 'None'-type Returns

The `print` function always returns `None`, so if you want all of the items in menu2 to return to menu1, you can 
set   
`end_to` = **menu1**,  and neglect chaining **menu1** at the end of the entry.

```commandline
from menucmd import Menu

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

---
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

You can also substitute `result` for function types if the previous return type is a `function`.

```
#func1: *args1 -> function

(func1, (*args1), result, (*args2))  =>  (func1(*args1))(*args2)  
```

--------
### Using Past Results

The `result` object can also be indexed to retrieve all past results in a chain.

By default, `result` is indexed at -1, which signifies the previous return value.
```
result := result[-1]
```

The indexing is 1-based in the scope of function chains, where `result[0]` is the initial argument 
passed to the menu.  

If you want the first result in the chain, write `result[1]`.\
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
(func1, (), func2, (result[-1],), func3, (result[1],), func4, (result[-2],))
      |           |                   |                  |
      V           |                   |                  |
  result[1] = 1   V                   |                  |
             result[2] = 2            V                  |
                                  result[3] = 2          V
                                                     result[4] = 8    


menu(arg)  => result[0] = arg_to(arg)
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
        print, result[2]  
    ))                     #result[2] prints the second result (= result[-3])
)


#Run
menu1()
```
-------
### Result Tags

When indexing a large number of results, it can quickly become confusing what each positional index refers to.  
Instead of using `result[n]`, you can create attributes on the fly which is analogous to declaring variables.

```commandline
("n", "square a number", (
    input, "number: ", 
    float, result, 
    lambda n: n**2, result[-1].NUMBER, 
    print, result.SQUARED, 
    print, result.NUMBER  
))
```
The first time you declare a **tag**, it will be associated with the result from the previous function.  All following
results with that **tag** will point to the first stored value, overwriting positional indexing.  In the above example, 
the second `result.NUMBER` does not need to specify position **[2]** because the value from the first reference to `NUMBER`  
is retrieved instead.

*The stored memory for tagged results resets on each function chain execution, so the attribute namespace exists 
**within each menu item!***

-------
### Result.expand()

In standard python, a `list` or `tuple` can be expanded into a function's argument field with the `*` notation.
In menucmd function composition, `result` objects can be marked for expansion with the `expand` method.

For example:
```commandline
# func1: () -> (val1, val2, val3)              Returns a tuple of three values
# func2: val1 -> val2 -> val3 -> val4          Accepts 3 arguments

(
    func1, (),
    func2, result.expand(),
    print, result,
    ...
)


# Equivalent to:

func2(*func1())
```

*It does not matter what order **indeces**, **tags**, or **methods** are specified in!* \
`result[n].expand().TAG` evaluates the 
same as `result.TAG[n].expand()` or any other permutation.

---
### 'arg_to'

The `arg_to` tag accepts a function that acts on the input to a menu call, effectively serving
as an "opening gambit" to each function chain.  This prooves to be an efficient way to serialize the first
step in function composition for all menu options.

```commandline
#arg_to : function that takes an argument on menu call and returns result[0] to be used
          as the first value the function chain.
```

For example, taking the square of the menu input and adding some number:

```commandline
square_number = lambda x: x**2

menu = Menu(arg_to = square_number)

menu.append(
    ("1", "add 1", (
        lambda x: x + 1, result,         #result[-1] = result[0] (post arg_to)
        print, result
    )),
    ("2", "double", (
        lambda x: x * 2, result,         #||
        print, result
    ))
)

menu(2)                #run menu with argument '2'
```

yields:

```commandline
Choose Action
[1]- add 1
[2]- add 2
[e]- exit
1
5

Choose Action
[1]- add 1
[2]- add 2
[e]- exit
2
8
```

---
4). Lazy Evaluation via Bind
-
-------
### Using the Bind Class

The `Bind` class allows lazy evaluation of functions.  If the arguments defined in a menu item are not determined yet,
or a previous result must be converted before the menu substitutes its value, the `Bind` class will hold off evaluating a 
function until it needs to.

Start by importing `Bind` into a convenient namespace:
```commandline
from menucmd import Menu, Bind as B
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

By default, if you don't use `Bind` in a menu item, and set the internal **args** to `result`, Python will attempt
to evaluate **func3(result)** before the item is even appended to the menu.  But **result** *doesn't exist yet!*

A different way to approach the square number entry is to bind `float` with `result` and use it as the argument
to the squaring function:

```commandline
from menucmd import Menu, Bind as B

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
---
### Calling a Bind Object
Outside of integrated menu usage, a `Bind` object can be called with no arguments and it will return its function
evaluated with its arguments.

```commandline
lazy_func = B(func, *args)

lazy_func() -> func(*args)
```
Additionally, `Bind` supports currying outside of the arguments that are already bound inside of it.
Calling a `Bind` object with additional args/kwargs will result in the following:
```commandline
B(func, *args1, **kwargs1)(*args2, **kwargs2)  ->  func(*args1, *args2, **kwargs1, **kwargs2)
```

---
### Note on Menu Composition

`Menu` objects accept one argument on call which is passed to `result[0]`* in the function chain. Since 
menus can also call other menus, it allows them to pass information between eachother.

**see `arg_to` in Section 3.*

For example, you can call a new menu with the previous `result` in a chain:
```commandline
(
    func, arg,
    other_menu, result
)
```
To keep the composition of menu arguments the same for *most* common use cases, the `end_to`,
`exit_to`, and `escape_to` functions take `result[0]` as their argument (if they have any).

The motivation for this is that menu arguments can be seen as internal states and for those functions
that the menu defaults to on a particular behaviour, they should ideally maintain the original 'state'
of the current menu. *

This can be changed by binding a menu to a particular value as follows:
```commandline
menuA = Menu()
menuB = Menu(end_to = B(menuA, arg))
```
This will overwrite the default behaviour of evaluating `end_to` with `result[0]`.

This is especially useful if any of the `*_to` functions are not `Menu` objects, but
functions that trigger a different part of a program.

**In future updates I might add more monadic behaviours to menu composition but this seems 
to be sufficient for now.*

---
### 'Bind().fix()'
The `fix` method toggles the `Bind` object's currying behaviour if you don't want it accumulating additional
arguments.

This is primarily used when using `Bind` in `arg_to`, `end_to`, and `exit_to` with ad-hoc polymorphic functions.

For example:
```commandline
#Print 'hi' on run
menu = Menu(arg_to = B(print, "hi"))

menu("x")  # yeilds >> "hi x"
menu()     # yeilds >> "hi None"  (by default)
```
This is because `print` is a polymorphic function, and the argument passed to the menu call
will append to the arguments in `Bind`.

The solution:
```commandline
menu = Menu(arg_to = B(print, "hi").fix()) 

menu("x")  # yeilds >> "hi"
menu()     # yeilds >> "hi" 
```
This will prevent the menu argument from being passed to any function `f(*args)`.

---
5). Menu Methods
-
---
### clear()
```commandline
menu.clear()
```
Removes all items from a menu except for the *exit key*.

---
### delete()
```commandline
menu.delete(n, k = 1)
```
Deletes **k** menu items starting from position **n**.  
Does not index the *exit key*.

---
### insert ()
```commandline
menu.insert(n, *items)
```
Same format as `append` but allows the user to insert menu items at position **n**. \
Does not index the *exit key*.

---
### append ()
```commandline
menu.append(*items)
```
(covered in section 1) 

---
### ch_exit ()
```commandline
menu.ch_exit(exit_to = None, exit_key = None, exit_message = None)
```
Use this function to change attributes of the *exit key*.  Since the `Menu` class handles
exit information differently than user defined items, it will not work to directly change 
these attributes.

The `ch_exit` method will update the *exit key* and only make changes to the parameters 
that are not left empty.

---
### Menu Object Indexing
```commandline
menu[n]  ->  ("key", "message", (func1, args1, func2, args2,...))

menu[a:b:c]  ->  Menu
```

`Menu` objects can be indexed and sliced like a `list` or a `tuple`.  
Returns a *menu item* for a single index. \
Returns a *new menu* with new item list when sliced.

---
6). Other Menu Attributes
-
-----
### Menu.kwargs

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


---
### 'escape_to' and 'Menu.escape'


The `escape` type allows for manually breaking from a menu before a chain completes.  

```commandline
escape = Menu.escape
```

If *any* function in the chain returns `escape`, no functions following will be executed and the 
menu will instead run its `escape_to` attribute.

By default, if a function in a chain returns `escape`, the menu will run itself. To change the
behaviour of this, use the `escape_to` argument.
```commandline
# escape_to : a function to be called on manual escape

#Breaks to a different menu on escape return
menu_B = Menu(escape_to = menu_A)
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
        check_if_empty, result,    #if empty return escape -> escape_to()
        print, "reversed:", 
        print, B(lambda s: s[::-1], result[-2])
    ))
)
```

While this module is designed to allow complete independence of menu structures and functions, 
the manual escape is the one exception to the rule.  Although, in some cases, this can 
be avoided with the builtin `escape_on` and `f_escape` functions covered in *Section 5)*.


----
### Menu.self

The `Menu.self` object is similar to `Menu.result`.  All uses of `Menu.self` will be replaced with the
menu's **self** reference on function chain execution.  

For example:
```commandline
menu.append(
    ("x", "print this menu's name!", (
        print, B(lambda x:x.name, Menu.self)
    )
)
```


----
### Menu.id

Shorthand for the identity morphism `lambda x:x`.  This is an arbitrary function to use in function chains
made soley for the purpose of elegence.  

*It has nothing to do with `menu.id` where **menu** is an instance of `Menu`!*

 

----
### Using Matching Keywords

If a menu's *exit_to*, *end_to*, and/or *escape_to* attributes are the same, you can optionally 
use matching keywords to avoid writing the arguments multiple times.

For example, instead of writing
```commandline
menu1 = Menu()

menu2 = Menu(exit_to= menu1, end_to= menu1, escape_to= menu1)

menu3 = Menu(exit_to= menu2, end_to= menu1, escape_to= menu1)
```

you can use the `Menu.exit_to` and `Menu.end_to` keyword objects:

```commandline
menu1 = Menu()

menu2 = Menu(exit_to= menu1, end_to= Menu.exit_to, escape_to= Menu.exit_to)

menu3 = Menu(exit_to= menu2, end_to= menu1, escape_to= Menu.end_to)
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

---
7). MCMDlang
-
------
MenuCMD also comes with a simple dsl that abstracts away the menu creation process in `main()`.  While it 
cannot create dynamic menus, it can access any function that does using the python method of appending items.

---

### Formatting:
- Indents need not be proper tabs, as long as they are four spaces.
- Menu id, function references, and function calls are written without quotes.
- Comments are one line only!  They will not be removed at the end of a line.
- Blank lines do not matter.


Example .mcmd file:
```commandline
### in menus.mcmd ###

Menu:
    name: Main Menu
    id: main_menu
    exit_key: 'e'
    exit_message: 'exit'
    
    # <- This is a comment
    
    Item:            # <- This is NOT a comment!
        key: 'x'
        message: 'Hello World!'
        func: input("your name: ")
        func: print(B(lambda x: f"Hello {x}!", result))
        
    Item:
        key: 'y'
        message: 'Go to menu2' 
        func: menu2()
        
Menu:
    name: 'Second Menu'
    id: menu2
    exit_to: main_menu
    
    Item:
        key: 'z'
        message: 'Goodbye World!'
        func: print("Goodbye World!")
```

---
### build_menus

Then import `build_menus`, and run in `main()`:

```commandline
from menucmd.dsl import build_menus

def main():
    #Build menus from mcmd
    menus = build_menus("menus.mcmd")
    
    #Populate namespace 
    main_menu = menus.main_menu
    menu2 = menus.menu2
    
    #Run
    main_menu()
```

`build_menus` will automatically import the scope from where you imported it and create pointers between menus
extracted from the `id` field under the `Menu` declaration.  The object it returns can be hashed by ids 
as a dictionary, or return menus from attributes: 

`menus['menu_id'] = menu.menu_id`

In addtion, the following shorthand refs are included in MCMDlang by default:
- `result` = `Menu.result`
- `B` = `Bind`
- All builtins

---
8). Builtins
-
------

So far, this tutorial has approached creating menus as separate entities from the functions they compose.
While this is an intended feature of the module, you may still use menus within functions.  menucmd has a number
of builtin functions to create template menus and to make in-line composition easier.  

 


## In-line Functions

These functions are designed to be composed in menu item function chains to control command flow.

-----
### escape_on (x, value)
```
Returns an escape if the two arguments are equal, or both Truthy or both Falsy.
Otherwise, returns value.
```
Use this to break function chain execution on an equality condition.  For example, to *escape* the menu on
empty input write:
```commandline
(
input, "input", 
escape_on, ("", result),      #if result == "" return escape -> escape_to()
print, "your input:", 
print, result[-2]
)
```
This will bypass the print statements if the user inputs an empty string and the menu calls `escape_to`.

-----
### f_escape (*args, **kwargs)
```
Polymorphic in-line escape function.
```
This function takes any **args** and **kwargs** and returns an `escape` object.




-----
### f_end (*args, **kwargs)
```commandline
Polymorphic in-line None return (end)
```
This function takes any **args** and **kwargs** and returns `None`. \
*Put this at the end of a function chain to evoke `end_to`.*

----
### f_switch (n, funcs)
```commandline
Returns a lazy function of type (Any index -> function)
```
Takes an **index** and a `list`, `tuple`, or `dict` of functions and returns a 
`Bind` object with an argument that indexes each function.

Use this if you want a previous result to change which function runs next.
```commandline
functions = (func1, func2, func3)

...
(
    input, ("choose a function (0-2) "), 
    f_switch(result, functions), (*args)
)
...
```
Since `f_switch` returns a `Bind` object that subsequently returns a `function`, be sure to ***call***
it in the function slot.  Whatever function it indexes upon evaluating `result`, 
will then be evaluated with **args**.

*If any function takes fewer arguments than provided, it will neglect the right-most arguments first!*

-----
## Builtin Menus

These functions construct temporary menus that determine their returns.  Optionally, all menu **kwargs**
can be passed through them to change the behaviour and appearance of the menus they invoke.

*Avoid changing the `exit_to` keyword argument as it will change the return type of the functions!*

------

### yesno_ver (yes = True, no = False, yes_message = "yes", **kwargs)
```commandline
Simple yes/no verification returning bool by default
Use yes and no tags to specify otherwise
```
Asks the user a yes/no question, and returns the bool of the result by default.

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
### edit_list (entries, **kwargs)
```commandline
Delete items in a list/tuple/dict/set; returns updated list/tuple/dict/set
```
Takes a `list`, `tuple`, `dict`, or `set` and displays a menu of numbered items to delete.  Upon each selection, the menu
will display itself again with the item removed.  It will only return the updated collection
upon pressing the *exit key*.


```commandline
L = ['a','b','c','d','e']

L = edit_list(L, name = "ed")

print(L)
```
 V V V V V V V 
```commandline
Edit List
[1]- a
[2]- b
[3]- c
[4]- d
[5]- e
[e]- exit
1

Edit List
[1]- b
[2]- c
[3]- d
[4]- e
[e]- exit
3

Edit List
[1]- b
[2]- c
[3]- e
[e]- exit
3

Edit List
[1]- b
[2]- c
[e]- exit
e
['b', 'c']
```

---
### choose_item (entries, exit_val = None, **kwargs)
```commandline
Pick and return an element from a list/tuple/dict/set.
Returns (key, value) pair for dict.
On exit key, return 'exit_val' (None by default)
```
Exactly the same as `edit_list` except it returns a single value selected by the user.

---
### choose_items (entries, **kwargs)
```commandline
Pick and return mutiple elements from a list/tuple/dict/set.
```
The inverse of `edit_list`.  Returns a struct of all selected items.

---

## Dynamic Menus (WIP)

Functions here will be used for changing properties of currently existing menus between their composition.

More functionality will be added in the next update!

----
### dynamic_wrapper (dyn_func, *args, **kwargs)
```commandline
(WIP)
Intended as a wrapper for arg_to (for now)

Usage: Menu(arg_to = dynamic_wrapper(dyn_func, *args, **kwargs))

Takes a func dyn_func: (menu_id, arg, *args, **kwargs) -> arg -> result[0]

Example:
def dyn_func(menu_id, arg, *items):
    menu_id.clear()
    menu_id.append(*items)
    return arg

dyn_func must refer to the menu in its first argument, the menu argument for its second,
and can take any additional *args/**kwargs.
It is intended for arbitrary use of menu methods to dynamically change the menu on run.
```

A function passed to `arg_to` during menu initialization cannot reference the menu itself.
This is because it has no **self** argument like a typical method found in a class.  `dynamic_wrapper`
remedies this by automatically passing the id of menu into the function's first argument.  

This allows the user to create functions that use the `Menu` methods without having to
specify a predefined menu.



