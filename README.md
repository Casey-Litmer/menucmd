```
B(func1, B(func2, B(func3, value)))
# First evaluates B(func3, value)
# Then evaluates B(func2, func3(value))
# Finally evaluates B(func1, func2(func3(value)))
```

-------
### Bind With Currying

By default, `Bind` supports currying—you can add more call-time arguments when invoking the wrapper.

Example with a polymorphic function (`print`):

```python
printer = B(print, "Message:")
printer("hello")   # Prints: Message: hello  (additional arg appended)
```

Lock the bound arguments with `.fix()` to prevent appending call-time args:

```python
printer_fixed = B(print, "Message:").fix()
printer_fixed("hello")  # Prints: Message:  ("hello" ignored)
```

`.fix()` makes the wrapper ignore any additional call-time args; use it when you want to ensure no further arguments are appended.
### 3. Function Composition
   - Using the `Result` Object
   - Accessing Previous Results
   - Named Result References
   - Expanding Results with `expand()`
   - Transform Initial Input: `arg_to`
### 4. Lazy Evaluation via Bind
   - When and Why to Use Bind
   - Using the `Bind` Class
   - Bind With Currying and `.fix()`
   - Passing Data Between Menus
### 5. Menu Methods
   - `append()`, `insert()`, `delete()`, `clear()`
   - `ch_exit()`
   - Menu Indexing and Slicing
### 6. Other Menu Attributes
   - `Menu.kwargs`
   - Early Exit: `escape` and `escape_to`
   - Reference to Current Menu: `Menu.self`
   - Control Display Clearing: `clear_readout`
   - Keyword Shortcuts: `exit_to`, `end_to`, `escape_to`
### 7. MCMDlang (DSL)
   - Formatting Rules
   - build_menus
### 8. Builtins
   - In-line Functions: `escape_on`, `f_escape`, `f_end`, `f_switch`
   - Builtin Menus: `yesno_ver`, `choose_item`, `choose_items`, `edit_list`
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
Menu items are tuples with three parts: `(key, message, function_chain)`

```
("key", "display message", (func1, arg1, func2, arg2, ...))
```

- **key**: Key to press to select this item (e.g., "x", "1", "a")
- **message**: Text displayed in the menu
- **function_chain**: Functions alternate with their arguments, executed left-to-right

-----
### Writing Function Arguments
Functions execute left-to-right with their arguments:

```
(func1, arg1, func2, arg2)
# Executes as: result = func2(arg2) applied to result from func1(arg1)
```

**Single vs. multiple arguments:**
- One argument: `(func, arg)` or `(func, (arg,))` both work
- Multiple: `(func, (arg1, arg2))` - must use tuple
- Tuple as argument: `(func, (my_tuple,))` - wrap with comma to distinguish from multiple args

-------

**Example:** Print a message when user presses "x":
```python
menu.append(
    ("x", "print greeting", (print, "Hello World!"))
)
```

You can add multiple items at once:
```python
menu.append(
    ("x", "say hello", (print, "Hello!")),
    ("y", "say goodbye", (print, "Goodbye!")),
)
```

----
### Running 'Hello World'
Now all that's left is to run the menu by calling it with no arguments.

```python
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
Inputting 'x' will print the desired text, returning to the menu:
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

```python
#Create New Menus
menu1 = Menu(name = "First Menu")
menu2 = Menu(name = "Second Menu")
```
Then, add another entry to **menu1** that runs **menu2** with no arguments:

```python
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
### `exit_to`, `exit_key`, `exit_message`: Exit Key Control

Control what happens when the user presses the exit key:

```python
# Change which key exits (default is 'e')
menu = Menu(exit_key='q')

# Change the exit message shown on menu
menu = Menu(exit_message='quit')

# Change what happens when exiting (default returns from menu)
menu = Menu(exit_to=other_menu)  # Go to other_menu instead
```
Adding an entry to **menu2** and setting its `exit_to` will return to `menu1` when the user exits **menu2**. A concise example:

```python
menu1 = Menu(name="First Menu")
menu2 = Menu(name="Second Menu", exit_to=menu1, exit_message="to menu1")

menu1.append(
    ("a", "open menu2", (menu2, ())),
)

menu2.append(("b", "say goodbye", (print, "Goodbye!")))

menu1()
```

When the user selects `a` then exits from `menu2`, control returns to `menu1` because of `exit_to=menu1`.

### Passing Data Between Menus

Menus can call other menus and pass data via `result`. To send the current menu argument into another menu, pass `result` as the argument when calling that menu:

```python
menu_a = Menu(name="Menu A")
menu_b = Menu(name="Menu B")

menu_a.append(
    ("open_b", "go to Menu B", (
        input, "Your name: ",
        menu_b, result  # Pass name to menu_b
    ))
)

menu_b.append(
    ("greet", "say hello", (
        print, ("Hello", result),  # result[0] = name from menu_a (after arg_to)
        menu_a, result  # Return to menu_a with same name
    ))
)
```

---
### `end_to`: Controlling End Behavior

By default, after a function chain completes, the menu calls itself when the chain's last function returns `None`.  Change this with `end_to`:

```python
menu = Menu(end_to=other_menu)  # After chain, open other_menu
```

**Practical example:** Create a simple info display that returns to the main menu:

```python
main_menu = Menu(name="Main")
info_menu = Menu(name="Info", end_to=main_menu)

info_menu.append(
    ("show", "show info", (
        print, "This is information"
        # After print returns None, end_to=main_menu triggers
    ))
)

main_menu.append(
    ("info", "view info", (info_menu, ()))
)
```

If the menu does not invoke `end_to`, it will return the *last return* in the chain directly.  This allows menus to compose like functions.  You can either use `end_to` to open another menu (commonly after a print statement), or transform the `None` value into something else for the return.

---
3). Function Composition
-
--------
### Using the Result Object

When you chain functions, you often need the output of one function as input to the next. That's what `result` does.

`result` is a special placeholder that gets replaced with the output of the previous function during execution.

**Simple example:** Get number → convert to int → square it → print:

```python
result = Menu.result

menu = Menu(name = "Square a Number")
menu.append(
    ("n", "square a number", (
        input, "Enter number: ",
        int, result,           # Convert string to int
        lambda x: x**2, result,  # Square it
        print, result            # Print result
    ))
)
```

When you run this and enter "5":
- `input()` returns "5"
- `int("5")` returns 5
- `lambda x: x**2` receives 5 and returns 25
- `print(25)` displays the result

--------
### Accessing Previous Results

By default, `result` refers to the immediately previous output (equivalent to `result[-1]`).

To access earlier results in the chain, use indexing:
- `result[0]` - the initial menu argument **(after `arg_to`)*
- `result[1]` - first function output
- `result[2]` - second function output  
- `result[-1]` - most recent output (same as `result`)
- `result[-2]` - output before last

**Example:** Ask for a number, double it, then print both the original and doubled:

```python
menu.append(
    ("d", "double a number", (
        input, "Number: ",
        int, result,                    # result[2] = 5
        lambda x: x * 2, result,        # result[3] = 10
        print, "Original:", result[2],  # or result[-2]
        print, "Doubled:", result[3]    # or result[-2]
    ))
)
```
-------
### Named Result References

Instead of remembering which index is which, you can name results as you go. This makes complex chains much more readable:

```python
menu.append(
    ("n", "square a number", (
        input, "number: ", 
        int, result,
        lambda x: x**2, result.num,      # Name prev result 'num'
        lambda x: x, result.squared      # Name prev result 'squared'
        print, "Number:", result.num,
        print, "Squared:", result.squared
    ))
)
```

Notes on naming:
- The first time you use a name (e.g. `result.num`) it captures the *previous* function's result.
- If you want to name the initial menu argument (`result[0]`), use an identity function like `Menu.id` or `lambda x: x` and then name that result.

*Names are scoped to each menu item—each time an item runs, the names reset.*

-------
### Expanding Results with `expand()`

When a function returns multiple values (tuple or list), you can "unpack" them as separate arguments using `expand()`:

```python
# Without expand: a_func receives the tuple as one argument
(func_returns_tuple, (), a_func, result)

# With expand: a_func receives each tuple element as separate arguments  
(func_returns_tuple, (), a_func, result.expand())

# When evaluated, this is equivalent to: 
a_func(*func_returns_tuple())
```

**Example:**
```python
def get_coordinates():
    return (10, 20)

menu.append(
    ("p", "print coordinates", (
        get_coordinates, (),
        lambda x, y: print(f"X: {x}, Y: {y}"), result.expand()
    ))
)
```

This passes `10` and `20` as separate arguments instead of passing the tuple `(10, 20)` as one argument.

---
### `arg_to`: Transform Initial Menu Input

The `arg_to` parameter transforms the input passed to a menu before function chains execute. This is useful when you want to preprocess the menu argument for multiple items.

```python
# Every chain receives result[0] = square of the input
menu = Menu(arg_to = lambda x: x**2)

menu.append(
    ("1", "add 1", (
        lambda x: x + 1, result,
        print, result
    )),
    ("2", "double", (
        lambda x: x * 2, result,
        print, result
    ))
)

menu(2)  # Both items now operate on 4 (2 squared)
```

Without `arg_to`, you'd need to square the input in every single chain.

---
4). Lazy Evaluation via Bind
-
-------
### When and Why to Use Bind

Normally, when you write `lambda x: x**2`, Python evaluates it immediately if you try to use its result as an argument elsewhere. With `Bind`, you can wrap a function and its arguments to delay evaluation until later—when you actually need the result.

**Problem without Bind:**
```python
menu.append(
    ("x", "square a number", (
        input, "number: ",
        # result doesn't exist yet, but Python tries to call float(result)
        lambda x: x**2, float(result),  # This fails!
        print, result
    ))
)
```

**Solution with Bind:**
```python
from menucmd import Menu, Bind as B

menu.append(
    ("x", "square a number", (
        input, "number: ",
        # Bind delays float(result) evaluation
        lambda x: x**2, B(float, result),  
        print, result
    ))
)
```

Now `float(result)` only executes after `result` exists.

-------
### Using the Bind Class

A `Bind` object holds a function and arguments, evaluating them only when needed:

```python
B(func, *args, **kwargs)
```

Inside a menu chain, `Bind` objects are automatically evaluated. Outside of menus, call them with `()`:

```python
lazy_func = B(print, "Hello")
lazy_func()  # Now it prints
```

**Nesting Bind objects** - each level gets its deepest value first:

```python
B(func1, B(func2, B(func3, value)))
# First evaluates B(func3, value)
# Then evaluates B(func2, func3(value))
# Finally evaluates B(func1, func2(func3(value)))
```

-------
### Bind With Currying

By default, a `Bind` wrapper accepts extra call-time arguments which are appended to the bound arguments.

```python
printer = B(print, "Message:")
printer("hello")    # Prints: Message: hello  (additional arg appended)
printer("a", "b") # Prints: Message: a b
```

If you want to lock the bound arguments so later call-time arguments are ignored, use `.fix()`:

```python
printer_fixed = B(print, "Message:").fix()
printer_fixed("hello")  # Prints: Message:  ("hello" ignored)
```

`.fix()` toggles the wrapper into a fixed state so additional call-time args are ignored. This is useful when binding polymorphic functions (like `print`) or when you want a wrapper to always behave identically regardless of later calls.

5). Menu Methods
-
---
### `append()`, `insert()`, `delete()`, `clear()`

Modify menu contents after creation:

```python
menu.append(item1, item2, ...)        # Add items
menu.insert(0, item)                  # Insert at position 0 (first item)
menu.delete(0, k=2)                   # Delete 2 items starting at position 0
menu.clear()                          # Remove all items (keeps exit key)
```

*Note: These don't count the exit key in their position indexing.*

### `ch_exit()`

Change exit key properties after creation:

```python
menu.ch_exit(exit_key="q", exit_message="quit", exit_to=other_menu)
```

Only specified parameters are updated; omit any you don't want to change.

### Menu Indexing and Slicing

Access and slice menu items like lists:

```python
menu[0]        # Get first item
menu[1:3]      # Slice items 1-2, returns new Menu
menu[0] = new_item  # Replace item
```

---
6). Other Menu Attributes
-
-----
### Menu.kwargs

When a function needs keyword arguments, wrap them with `Menu.kwargs` (which is just a dict):

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

menu.append(
    ("g", "greet", (
        input, "Name: ",
        greet, (result, Menu.kwargs(greeting="Hi"))
    ))
)
```

Both syntaxes work:
```python
Menu.kwargs(greeting="Hi")
Menu.kwargs({"greeting": "Hi"})
```


---
### `escape` and `escape_to`: Early Exit from a Chain

Sometimes you want a function in the chain to abort execution and exit early. Use `Menu.escape` to signal this:

```python
def validate_input(text):
    if len(text) < 3:
        return Menu.escape  # Abort chain and go to escape_to
    return text

menu.append(
    ("enter", "enter text", (
        input, "Text (3+ chars): ",
        validate_input, result,
        print, "You entered:", result
    ))
)
```

By default, `escape` re-runs the current menu. Change this with `escape_to`:

```python
menu_a = Menu()
menu_b = Menu(escape_to=menu_a)  # On escape, return to menu_a instead

menu_b.append(
    ("enter", "enter text", (
        input, "Text (3+ chars): ",
        validate_input, result,
        print, "You entered:", result
    ))
)
```

#### Built-in escape helpers:

- `escape_on(value1, value2)` - returns `escape` if the two values are equal
- `f_escape(*args, **kwargs)` - always returns `escape` (useful in chains)

**Example with escape_on:**
```python
menu.append(
    ("enter", "guess a number", (
        input, "Guess: ",
        escape_on, (result, "0"),  # Treat "0" as cancel
        int, result,
        print, "Your guess:", result
    ))
)
```


----
### Menu.self: Reference to the Current Menu

Use `Menu.self` to get a reference to the menu itself inside a function chain:

```python
menu = Menu(name="Main Menu")
menu.append(
    ("count", "show item count", (
        lambda m: len(m.menu_item_list), Menu.self,
        print, result
    ))
)
```

This is useful for introspection or passing the menu to another function.


----
### `clear_readout`

Controls whether the menu display is cleared from the terminal after user input.

```python
menu = Menu(clear_readout=False)  # Keep menu history in terminal
```

By default (`clear_readout=True`), each menu clears the previous output, showing only the current menu.

---
### `exit_to`, `end_to`, `escape_to`: Keyword Shortcuts

When multiple `*_to` parameters tie to the same menu, use shortcuts:

```python
menu_home = Menu()

# Instead of:
submenu = Menu(exit_to=menu_home, end_to=menu_home, escape_to=menu_home)

# Use:
submenu = Menu(exit_to=menu_home, end_to=Menu.exit_to, escape_to=Menu.exit_to)
```

`Menu.exit_to` copies the `exit_to` value. `Menu.end_to` copies `end_to`. This reduces repetition in complex menu hierarchies.

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
```txt
### in menus.mcmd ###

Menu:
    name: "Main Menu"
    id: main_menu
    exit_key: "e"
    exit_message: "exit"
    
    # <- This is a comment
    
    Item:                # <- This is NOT a comment!
        key: "x"
        message: "Hello World!"
        func: input("your name: ")
        func: print(B(lambda x: f"Hello {x}!", result))
        
    Item:
        key: "y"
        message: "Go to menu2" 
        func: menu2()
        
Menu:
    name: "Second Menu"
    id: menu2
    exit_to: main_menu
    
    Item:
        key: "z"
        message: "Goodbye World!"
        func: print("Goodbye World!")
```

---
### build_menus

Then import `build_menus`, and run in `main()`:

```python
from menucmd.dsl import build_menus

def main():
    #Build menus from mcmd
    menus = build_menus("menus.mcmd")
    
    #Populate namespace 
    main_menu = menus["main_menu"]
    menu2 = menus["menu2"]
    
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
- `kwargs` = `Menu.kwargs`
- `self` = `Menu.self`
- All builtins

---
8). Builtins
-
------

So far, this tutorial has approached creating menus as separate entities from the functions they compose.
While this is an intended feature of the module, you may still use menus within functions.  menucmd has a number
of builtin functions to create template menus and to make in-line composition easier.  

 


## In-line Functions

Utility functions to control execution flow within function chains.

-----
### escape_on(value1, value2)

Returns `escape` if the values are equal, otherwise returns `value1`. Useful for escaping on specific input:

```python
menu.append(
    ("input", "enter something", (
        input, "Enter text (q to quit): ",
        escape_on, (result, "q"),  # Escape if user enters "q"
        print, "You entered:", result,
        print, result
    ))
)
```

-----
### f_escape(*args, **kwargs)

Always returns `escape` regardless of arguments. Useful for unconditionally ending a chain.




-----
### f_end(*args, **kwargs)

Always returns `None`, triggering `end_to` behavior. Useful to explicitly end a chain:

```python
menu.append(
    ("x", "Manual End", (
        input, "Pick a number",
        f_end, ()  # Explicitly trigger end_to
    ))
)
```

---
### f_switch(index, func_list)

Pick which function to run based on a previous result:

```python
menu.append(
    ("choose", "pick operation", (
        input, "1=add, 2=times: ",
        f_switch(result, [lambda x,y: x+y, lambda x,y: x*y]), 
        (5, 3), # < Arguments for the selected function
        print, result
    ))
)
```

-----
## Builtin Menus

Ready-made menu templates for common interactions. All accept optional `**kwargs` to customize the menu (e.g., `name="Custom Name"`).

---
### yesno_ver(yes=True, no=False, yes_message="yes", **kwargs)

Simple yes/no dialog:

```python
if yesno_ver():
    print("User said yes!")
else:
    print("User said no!")
```

Returns the `yes` parameter on yes, `no` parameter on no (customize with keyword args).

---
### choose_item(entries, exit_val=None, **kwargs)

Let user select one item from a list/tuple/dict/set:

```python
options = ["Red", "Green", "Blue"]
choice = choose_item(options)
if choice != None:
    print(f"You chose: {choice}")
```

Returns the selected item, or `exit_val` (default `None`) if user exits.

---
### choose_items(entries, **kwargs)

Let user select multiple items (inverse of `edit_list`):

```python
options = ["Python", "JavaScript", "Rust"]
selected = choose_items(options)
print(f"You selected: {selected}")
```

Returns a collection of all selected items.

---
### edit_list(entries, **kwargs)

Let user remove items from a list/tuple/dict/set by interactively selecting them:

```python
items = ["apple", "banana", "cherry"]
remaining = edit_list(items)
print(f"Remaining items: {remaining}")
```

Displays the collection as a menu, removes selected items, shows menu again until exit.
---

## Dynamic Menus (WIP)

Advanced feature for dynamically modifying menus during execution. This section is under development; use the static menu patterns above for production code.



