# MenuCMD

```commandline
pip install menucmd
```

MenuCMD provides a lightweight, functional‑style framework for building interactive command‑line menus.  It keeps business logic (your functions) completely separate from the navigation layer, so the same code can run both interactively and unattended.

Use it for quick debugging utilities, as a CLI frontend for scripts, or whenever you need lazy/deferred evaluation.  The package includes a simple `.mcmd` DSL to describe static menus in plain text.

---
## Sections

### 1. Hello World
   - [Initializing a Menu](#initializing-a-menu)
   - [Menu Items](#menu-items)
   - [Writing Function Arguments](#writing-function-arguments)
   - [Running 'Hello World'](#running-hello-world)

### 2. Multiple Menus
   - [Defining Two Menus](#defining-two-menus)
   - [ Exit Key Control: `exit_to`, `exit_key`, `exit_message`](#exit-key-control-exit_to-exit_key-exit_message)
   - [Passing Data Between Menus](#passing-data-between-menus)
   - [Controlling End Behavior: `end_to`](#controlling-end-behavior-end_to)

### 3. Function Composition
   - [Using the `Result` Object](#using-the-result-object)
   - [Accessing Previous Results](#accessing-previous-results)
   - [Named Result References](#named-result-references)
   - [Expanding Results with `.expand()`](#expanding-results-with-expand)
   - [Transform Initial Menu Input: `arg_to`](#transform-initial-menu-input-arg_to)
   - [Argument Order `arg_to_first`](#argument-execution-order-arg_to_first)

### 4. Lazy Evaluation via Bind
   - [When and Why to Use Bind](#when-and-why-to-use-bind)
   - [Using the `Bind` Class](#using-the-bind-class)
   - [Currying and `.fix()`](#currying-and-fix)
   - [Nested Bind Objects](#nested-bind-objects)

### 5. Menu Methods
   - [`append()`, `insert()`, `delete()`, `clear()`](#append-insert-delete-clear)
   - [`ch_exit()`](#ch_exit)
   - [Indexing and Slicing](#menu-indexing-and-slicing)

### 6. Other Menu Attributes
   - [Colors and Appearance: `MenuColors`, `ItemColors`, `Colors`, `exit_colors`](#colors-and-appearance-menucolors-itemcolors-colors-exit_colors)
   - [`Menu.kwargs`](#menukwargs)
   - [Early Exit: `escape`, `escape_to`](#early-exit-escape-escape_to)
   - [`Menu.self`](#menuself)
   - [`clear_readout`](#clear_readout)
   - [Keyword Shortcuts: `exit_to`, `end_to`, `escape_to`](#keyword-shortcuts-exit_to-end_to-escape_to)

### 7. MCMDlang (DSL)
   - [Formatting Rules](#formatting-rules)
   - [`build_menus`](#build_menus)

### 8. Builtins
   - [In-line Functions](#in-line-functions)
   - [Builtin Menus](#builtin-menus)
   - [Dynamic Menus (WIP)](#dynamic-menus-wip)

---

## 1. Hello World

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
### Menu Items
Create menu items using the `Item` class with three main parts:

```python
from menucmd import Menu, Item

Item(key="x", message="display message", funcs=[(func1, arg1), (func2, arg2), ...])
```

- **key**: Key to press to select this item (e.g., "x", "1", "a")
- **message**: Text displayed in the menu
- **funcs**: List of (function, arguments) tuples, executed left-to-right

-----
### Writing Function Arguments
In the `funcs` list, functions execute left-to-right. Each function is paired with its arguments as a tuple:

```python
funcs=[(func1, arg1), (func2, arg2)]
# Executes as: func1(args1), then func2(arg2)
```

**Single vs. multiple arguments:**
- One argument: `(func, arg)` or `(func, (arg,))` both work
- Multiple: `(func, (arg1, arg2))` - must use tuple
- Tuple as argument: `(func, (my_tuple,))` - wrap with comma to distinguish from multiple args

-------

**Example:** Print a message when user presses "x":
```python
menu.append(
    Item(key="x", message="print greeting", funcs=[(print, "Hello World!")])
)
```

You can add multiple items at once:
```python
menu.append(
    Item(key="x", message="say hello", funcs=[(print, "Hello!")]),
    Item(key="y", message="say goodbye", funcs=[(print, "Goodbye!")]),
)
```

----
### Running 'Hello World'
Now all that's left is to run the menu by calling it with no arguments.

```python
from menucmd import Menu, Item

#Create New Menu
menu1 = Menu(name="First Menu")

#Add an Item
menu1.append(
    Item(key="x", message="hello world program", funcs=[
        (print, "hello world!")
    ])
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
will break out of the menu by default.  (You can change this behaviour when initializing the menu)

When there is no more code to be run after the menu breaks, the program ends.

---

## 2. Multiple Menus

### Defining Two Menus
You can open other menus by running them as functions, letting the user navigate through a deeper menu structure.

First create a new `Menu` instance in the same way as **menu1**:

```python
#Create New Menus
menu1 = Menu(name="First Menu")
menu2 = Menu(name="Second Menu")
```
Then, add another entry to **menu1** that runs **menu2** with no arguments:

```python
menu1.append(
    Item(key="x", message="hello world program", funcs=[
        (print, "hello world!")
    ]),
    Item(key="a", message="menu2", funcs=[
        (menu2, ())
    ])
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
### Exit Key Control: `exit_to`, `exit_key`, `exit_message`

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
    Item(key="a", message="open menu2", funcs=[(menu2, ())]),
)

menu2.append(
    Item(key="b", message="say goodbye", funcs=[(print, "Goodbye!")])
)

menu1()
```

When the user selects `a` then exits from `menu2`, control returns to `menu1` because of `exit_to=menu1`.

### Passing Data Between Menus

A menu can call another and pass data via `result`. To send the current menu argument into the target menu, pass `result` as the argument when calling it:

```python
menu_a = Menu(name="Menu A")
menu_b = Menu(name="Menu B")

menu_a.append(
    Item(key="open_b", message="go to Menu B", funcs=[
        (input, "Your name: "),
        (menu_b, result)  # Pass name to menu_b
    ])
)

menu_b.append(
    Item(key="greet", message="say hello", funcs=[
        (print, ("Hello", result)),  # result[0] = name from menu_a (after arg_to)
        (menu_a, result)  # Return to menu_a with same name
    ])
)
```

---
### Controlling End Behavior: `end_to` 

By default, after a function chain completes, the menu calls itself when the chain's last function returns `None`.  Change this with `end_to`:

```python
menu = Menu(end_to=other_menu)  # After chain, open other_menu
```

**Practical example:** Create a simple info display that returns to the main menu:

```python
main_menu = Menu(name="Main")
info_menu = Menu(name="Info", end_to=main_menu)

info_menu.append(
    Item(key="show", message="show info", funcs=[
        (print, "This is information")
        # After print returns None, end_to=main_menu triggers
    ])
)

main_menu.append(
    Item(key="info", message="view info", funcs=[
        (info_menu, ())
    ])
)
```

If the menu does not invoke `end_to`, it will return the *last return* in the chain directly.  This allows menus to compose like functions.  You can either use `end_to` to open another menu (commonly after a print statement), or transform the `None` value into something else for the return.

---

## 3. Function Composition

### Using the `Result` Object

When you chain functions, you often need the output of one function as input to the next. That's what `result` does.

`result` serves as a special placeholder, replacing the output of the previous function during execution.

**Simple example:** Get number → convert to int → square it → print:

```python
from menucmd import Menu, Item
result = Menu.result

menu = Menu(name="Square a Number")
menu.append(
    Item(key="n", message="square a number", funcs=[
        (input, "Enter number: "),
        (int, result),           # Convert string to int
        (lambda x: x**2, result),  # Square it
        (print, result)            # Print result
    ])
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
    Item(key="d", message="double a number", funcs=[
        (input, "Number: "),
        (int, result),                    # result[2] = 5
        (lambda x: x * 2, result),        # result[3] = 10
        (print, ("Original:", result[2])),  # or result[-2]
        (print, ("Doubled:", result[3]))    # or result[-2]
    ])
)
```
-------
### Named Result References

Instead of remembering which index is which, you can name results as you go. This makes complex chains much more readable:

```python
menu.append(
    Item(key="n", message="square a number", funcs=[
        (input, "number: "),
        (int, result),
        (lambda x: x**2, result.num),      # Name prev result 'num'
        (lambda x: x, result.squared),     # Name prev result 'squared'
        (print, ("Number:", result.num)),
        (print, ("Squared:", result.squared))
    ])
)
```

Notes on naming:
- The first time you use a name (e.g. `result.num`) it captures the *previous* function's result.
- If you want to name the initial menu argument (`result[0]`), use an identity function like `Menu.id` or `lambda x: x` and then name that result.

*Names are scoped to each menu item—each time an item runs, the names reset.*

-------
### Expanding Results with `.expand()`

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
    Item(key="p", message="print coordinates", funcs=[
        (get_coordinates, ()),
        (lambda x, y: print(f"X: {x}, Y: {y}"), result.expand())
    ])
)
```

This passes `10` and `20` as separate arguments instead of passing the tuple `(10, 20)` as one argument.

---
### Transform Initial Menu Input: `arg_to`

The `arg_to` parameter transforms the input passed to a menu before function chains execute. This is useful when you want to preprocess the menu argument for multiple items.

A companion flag `arg_to_first` (default `True`) controls whether this transformation occurs **before** the user makes a selection or **after**. Setting it to `False` means the original argument is available during item selection, and the transformation happens only when the chosen chain runs.

```python
# Every chain receives result[0] = square of the input
menu = Menu(arg_to=lambda x: x**2)

menu.append(
    Item(key="1", message="add 1", funcs=[
        (lambda x: x + 1, result),
        (print, result)
    ]),
    Item(key="2", message="double", funcs=[
        (lambda x: x * 2, result),
        (print, result)
    ])
)

menu(2)  # Both items now operate on 4 (2 squared)
```
Without `arg_to`, you'd need to square the input in every single chain.

---

### Argument Execution Order: `arg_to_first`

Additionally you may pass the `arg_to_first` flag to control **when** the transformation runs:

```python
def menu_arg_to(x):
    print('Evaluating menu argument')
    return x**2

# show the argument being transformed only after choice
menu(arg_to=menu_arg_to, arg_to_first=False)
```

If `arg_to_first=True` (the default) the argument is squashed as soon as the menu opens,
so you'll see the print message **before** any options appear. With
`arg_to_first=False`, the raw argument is preserved while the user browses options;
the transformation (and the print) happens only when a keyed item is chosen, just
prior to executing its function chain. This allows menus to make display or
navigation decisions based on the original input.


---

## 4. Lazy Evaluation via Bind

### When and Why to Use Bind

Normally, when you write `lambda x: x**2`, Python evaluates it immediately if you try to use its result as an argument elsewhere. With `Bind`, you can wrap a function and its arguments to delay evaluation until later—when you actually need the result.

**Problem without Bind:**
```python
menu.append(
    Item(key="x", message="square a number", funcs=[
        (input, "number: "),
        # result doesn't exist yet, but Python tries to call float(result)
        (lambda x: x**2, float(result)),  # This fails!
        (print, result)
    ])
)
```

**Solution with Bind:**
```python
from menucmd import Menu, Item, Bind as B

menu.append(
    Item(key="x", message="square a number", funcs=[
        (input, "number: "),
        # Bind delays float(result) evaluation
        (lambda x: x**2, B(float, result)),
        (print, result)
    ])
)
```

Now `float(result)` only executes after `result` exists.

-------
### Using the Bind Class

A `Bind` object holds a function and arguments, evaluating them only when needed:

```python
B(func, *args, **kwargs)
```

Menus evaluate `Bind` objects automatically during a chain; outside of menus, just call them with `()`: 

```python
lazy_func = B(print, "Hello")
lazy_func()  # Now it prints
```

### Nested Bind Objects

Each level of nesting gets evaluated depth-first:

```python
B(func1, B(func2, B(func3, value)))
# First evaluates B(func3, value)
# Then evaluates B(func2, func3(value))
# Finally evaluates B(func1, func2(func3(value)))
```

-------
### Currying and `.fix()`

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

## 5. Menu Methods

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

## 6. Other Menu Attributes

### Colors and Appearance: `MenuColors`, `ItemColors`, `Colors`, `exit_colors`

Style menus and items with ANSI escape codes. Three helper classes help you do this:

- `Colors` provides a simple namespace of ANSI color/formatting codes (e.g. `Colors.RED`, `Colors.BOLD`).
- `MenuColors`: a dataclass that defines default colors for menu elements.  Instantiate it and pass via the `colors` argument when creating a `Menu`.  Its fields include:
  - `name` – the menu title line.
  - `empty_message` – text shown when the menu has no entries.
  - `invalid_selection` – message printed on bad keypress.
  - ***All fields in `ItemColors`**
- `ItemColors`: a subset of `MenuColors` that overrides colors for individual items on an attribute‑by‑attribute basis.  Its fields include:
  - `key` - the item key
  - `key_dash` - the dash between key and message
  - `message` - the item message

The `exit_colors` parameter in `Menu` also accepts an `ItemColors` instance and works in the same way as colors passed to an `Item`.

```python
from menucmd import Menu, Item, MenuColors, ItemColors, Colors

menu = Menu(colors=MenuColors(...),
            exit_colors=ItemColors(key=Colors.RED + Colors.BOLD))

menu.append(
    Item(key="a", message="blue key", funcs=[(print, "hi")]),
    Item(key="b", message="red key", funcs=[(print, "yo")],
         colors=ItemColors(key=Colors.RED))
)
```

In the example above the second item only overrides the `key` color, inheriting the other styles from `menu.colors`.

### Menu.kwargs

When a function needs keyword arguments, wrap them with `Menu.kwargs` (which is just a dict):

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

menu.append(
    Item(key="g", message="greet", funcs=[
        (input, "Name: "),
        (greet, (result, Menu.kwargs(greeting="Hi")))
    ])
)
```

Both syntaxes work:
```python
Menu.kwargs(greeting="Hi")
Menu.kwargs({"greeting": "Hi"})
```


---
### Early Exit: `escape`, `escape_to`

Sometimes you want a function in the chain to abort execution and exit early. Use `Menu.escape` to signal this:

```python
def validate_input(text):
    if len(text) < 3:
        return Menu.escape  # Abort chain and go to escape_to
    return text

menu.append(
    Item(key="enter", message="enter text", funcs=[
        (input, "Text (3+ chars): "),
        (validate_input, result),
        (print, ("You entered:", result))
    ])
)
```

By default, `escape` re-runs the current menu. Change this with `escape_to`:

```python
menu_a = Menu()
menu_b = Menu(escape_to=menu_a)  # On escape, return to menu_a instead

menu_b.append(
    Item(key="enter", message="enter text", funcs=[
        (input, "Text (3+ chars): "),
        (validate_input, result),
        (print, ("You entered:", result))
    ])
)
```

#### Built-in escape helpers:

- `escape_on(value1, value2)` - returns `escape` if the two values are equal
- `f_escape(*args, **kwargs)` - always returns `escape` (useful in chains)

**Example with escape_on:**
```python
menu.append(
    Item(key="enter", message="guess a number", funcs=[
        (input, "Guess: "),
        (escape_on, (result, "0")),  # Treat "0" as cancel
        (int, result),
        (print, ("Your guess:", result))
    ])
)
```


----
### `Menu.self`

Use `Menu.self` to get a reference to the menu itself inside a function chain:

```python
menu = Menu(name="Main Menu")
menu.append(
    Item(key="count", message="show item count", funcs=[
        (lambda m: len(m.menu_item_list), Menu.self),
        (print, result)
    ])
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
### Keyword Shortcuts: `exit_to`, `end_to`, `escape_to`

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

## 7. MCMDlang (DSL)
MenuCMD also comes with a simple dsl that abstracts away the menu creation process in `main()`.  While it 
cannot create dynamic menus, it can access any function that does using the python method of appending items.

---

### Formatting Rules:
- Indents need not be proper tabs, as long as they are four spaces.
- Menu id, function references, and function calls are written without quotes.
- Comments are one line only!  They will not be removed at the end of a line.
- Blank lines do not matter.
- You can include `Colors` and `ExitColors` blocks inside a `Menu` declaration. `ExitColors` works like an item color block but applies only to the exit key.


Example .mcmd file:
```txt
### in menus.mcmd ###

Menu:
    name: "Main Menu"
    id: main_menu
    exit_key: "e"
    exit_message: "exit"
    Colors:
        key: Colors.LIGHT_BLUE + Colors.BOLD
    ExitColors:
        key: Colors.RED + Colors.BOLD
        message: Colors.FAINT
    
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
### `build_menus`

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

`build_menus` imports the scope from where you call it and creates pointers between menus
extracted from the `id` field under the `Menu` declaration.  You can hash the returned object by ids 
as a dictionary, or return menus from attributes: 

`menus['menu_id'] = menu.menu_id`

In addtion, the following shorthand refs are included in MCMDlang by default:
- `result` = `Menu.result`
- `B` = `Bind`
- `kwargs` = `Menu.kwargs`
- `self` = `Menu.self`
- All builtins

---

## 8. Builtins

So far, this tutorial has approached creating menus as separate entities from the functions they compose.
While this is an intended feature of the module, you may still use menus within functions.  menucmd has a number
of builtin functions to create template menus and to make in-line composition easier.  

```python
from menucmd.builtins import *
```


### In-line Functions

Utility functions to control execution flow within function chains.

-----
### escape_on(value1, value2)

Returns `escape` if the values are equal, otherwise returns `value1`. Useful for escaping on specific input:

```python
menu.append(
    Item(key="input", message="enter something", funcs=[
        (input, "Enter text (q to quit): "),
        (escape_on, (result, "q")),  # Escape if user enters "q"
        (print, ("You entered:", result)),
        (print, result)
    ])
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
    Item(key="x", message="Manual End", funcs=[
        (input, "Pick a number"),
        (f_end, ())  # Explicitly trigger end_to
    ])
)
```

---
### f_switch(index, func_list)

Pick which function to run based on a previous result.  
Returns `Bind(lambda b: func_list[b], n)`.  


```python
def plus(x, y):
    return x + y

def times(x, y):
    return x * y

menu.append(
    Item(key="choose", message="pick operation", funcs=[
        (input, "1=plus, 2=times: "),
        (f_switch(result, [plus, times]), (5, 3)),
        (print, result)
    ])
)
```
*If a function in the list does not have enough arguments for what you try to curry to it (`(5, 3)` in the above example), then it will ignore those arguments.*

-----
### Builtin Menus

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

### Dynamic Menus (WIP)

Advanced feature for dynamically modifying menus during execution. This section is under development; use the static menu patterns above for production code.



