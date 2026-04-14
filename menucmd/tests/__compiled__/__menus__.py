from menucmd import *

result = Menu.result
kwargs = Menu.kwargs
self = Menu.self
B = Bind
C = Colors

from menucmd.tests.testing_utils import *
from menucmd.builtins import *
from menucmd.cfgutil import *

Menu.set_global_colors(colors = MenuColors(key='\x1b[94m\x1b[1m', dash=None, message=None, name=None, empty_message='\x1b[31m\x1b[5m', invalid_key=None))
Menu.set_global_colors(exit_colors = ItemColors(key='\x1b[31m', dash=None, message=None))

main_menu = Menu(
    name = "Hub",
    exit_key = "x",
)
lazy_menu = Menu(
    name = "Lazy Eval",
    exit_to = to_menu(main_menu),
)
builtin_menu = Menu(
    name = "Builtins",
    exit_to = to_menu(main_menu),
    colors = MenuColors(
        key = C.CYAN + C.BOLD,
    ),
)
dynamic_menu = Menu(
    name = "Dynamic Menus",
    exit_to = to_menu(main_menu),
    colors = MenuColors(
        key = C.CYAN + C.BOLD,
    ),
)
menu_A = Menu(
    name = "Menu_A",
    exit_to = to_menu(lazy_menu),
    end_to = Menu.exit_to,
    colors = MenuColors(
        key = C.RED,
        message = C.FAINT,
    ),
)
menu_B = Menu(
    name = "Menu_B",
    exit_to = to_menu(dynamic_menu),
    escape_to = Menu.exit_to,
    colors = MenuColors(
        key = C.RED,
        message = C.FAINT,
    ),
)
config_menu = Menu(
    name = "Config Menus",
    arg_to = cfg.get_config(),
    exit_to = to_menu(main_menu),
    colors = MenuColors(
        key = C.GREEN + C.BOLD,
    ),
)

main_menu.append(
    Item(
        key = 'e',
        message = 'Test Lazy Eval',
        funcs = [
            (open_menu , (lazy_menu,)),
        ]
    ),
    Item(
        key = 'b',
        message = 'Test Builtins',
        funcs = [
            (open_menu, (builtin_menu,)),
        ]
    ),
    Item(
        key = 'd',
        message = 'Test Dynamic Menus',
        funcs = [
            (open_menu, (dynamic_menu,)),
        ]
    ),
    Item(
        key = 'c',
        message = 'Test Config Menus',
        funcs = [
            (open_menu, (config_menu,)),
        ]
    ),
)
lazy_menu.append(
    Item(
        key = 's',
        message = 'Square Number',
        funcs = [
            (input, ("Number: ",)),
            (B, (lambda x: float(x) ** 2, result,)),
            (print, (result,)),
        ]
    ),
    Item(
        key = 'c',
        message = 'Shuffle Cards',
        colors = ItemColors(
            key = C.YELLOW + C.BOLD,
        ),
        funcs = [
            (shuffle_cards, ()),
            (pick_card, (B(int,B(input, "Choose Card (0-51): ")), result,)),
            (print, (result,)),
        ]
    ),
    Item(
        key = 'm',
        message = 'Menu Composition',
        funcs = [
            (input, ("string for menu_A: ",)),
            (open_menu, (menu_A, result,)),
        ]
    ),
    Item(
        key = 'i',
        message = 'Iterator Test',
        funcs = [
            (input, ("list of 3 (separated by spaces): ",)),
            (tuple, (B(lambda x: x.split(), result),)),
            (print, ("result call: ", result.expand(),)),
            (print, (B(lambda x, y, z: x+y+z, result[-2].expand()),)),
        ]
    ),
    Item(
        key = 'a',
        message = 'Attribute Test',
        funcs = [
            (input, ("integer 1: ",)),
            (int, (result[-1].INT1,)),
            (input, ("integer 2: ",)),
            (int, (result[-1].INT2,)),
            (print, (result.INT1, result.INT2,)),
            (print, ("INT1 : ", result.INT1[-1000000].INT1[314198].INT2.INT1,)),
            (tuple, ((result.INT1, result.INT2),)),
            (print, ("expanded ", result[-1].EXP.expand(),)),
            (print, ("expanded (tagged)", result.EXP.expand(),)),
        ]
    ),
)
builtin_menu.append(
    Item(
        key = 'l',
        message = 'Edit List',
        funcs = [
            (input, ("List items (separated by spaces): ",)),
            (edit_list, (B(lambda s: s.split(), result), kwargs(name = "Delete Items"),)),
            (print, ("New string:\n", B(" ".join, result),)),
        ]
    ),
    Item(
        key = 'c',
        message = 'Choose Item',
        funcs = [
            (input, ("List items (separated by spaces): ",)),
            (choose_item, (B(lambda s: s.split(), result), kwargs(name = "Choose Item"),)),
            (print, ("New string:\n", result,)),
        ]
    ),
    Item(
        key = 'v',
        message = 'Confirmation',
        funcs = [
            (yesno_ver, (kwargs(name = "Delete system32?", exit_message = "no"),)),
            (f_switch(result, (f_escape, yesno_ver)), (kwargs(name ="Are you really sure?", exit_message = "no"),)),
            (f_switch(result, (f_escape, yesno_ver)), (kwargs(name = "Are you not sure?", exit_message = "no"),)),
            (f_switch(result, (yesno_ver, f_escape)), (kwargs(name = "Are you sure you are not sure?", exit_message = "wtf?"),)),
            (print, (B(lambda b: "crisis averted!" if b else "deleting...\nsystem32 cannot be deleted!", result),)),
        ]
    ),
)
dynamic_menu.append(
    Item(
        key = 'x',
        message = 'test keyword function compositions',
        funcs = [
            ((lambda: 0), ()),
            (open_menu, (menu_B, result,)),
        ]
    ),
    Item(
        key = 's',
        message = 'Menu.self usage: insert new item here',
        funcs = [
            (Menu.insert, (self, 0, Item(key="*", message="Nice Job!", funcs=[(open_menu, (main_menu, "*"))], colors=ItemColors(key=C.GREEN + C.BOLD)),)),
        ]
    ),
)
menu_A.append(
    Item(
        key = 'm',
        message = 'reverse and print',
        funcs = [
            ((lambda s: s[::-1]), (result,)),
            (print, (result,)),
        ]
    ),
)
menu_B.append(
    Item(
        key = 's',
        message = 'test escape_to',
        funcs = [
            (escape_on, (result, 3,)),
            (print, (result,)),
            (menu_B, (B(lambda n: n+1, result[-2]),)),
        ]
    ),
)
config_menu.append(
    Item(
        key = '$',
        message = 'Settings',
        funcs = [
            (cfg.open_settings_menu, (result.CONFIG, kwargs(name = "Settings"),)),
        ]
    ),
    Item(
        key = '#',
        message = 'Show Command History',
        colors = ItemColors(
            key = C.CYAN + C.BOLD,
        ),
        funcs = [
            (cfg.get_command_history, (result.CONFIG, kwargs(colors=MenuColors(key=C.CYAN + C.BOLD)),)),
            (print, (result.COMMAND,)),
        ]
    ),
    Item(
        key = 'z',
        message = 'Clear Command History',
        funcs = [
            (cfg.clear_command_history, (result.CONFIG,)),
            (print, ("Command History Cleared",)),
            (cfg.save_config, (result.CONFIG,)),
        ]
    ),
    Item(
        key = 'x',
        message = 'Run Command',
        funcs = [
            (run_command, ()),
            (cfg.add_to_history, (result[0].CONFIG, result.COMMAND,)),
            (cfg.save_config, (result.CONFIG,)),
        ]
    ),
)
