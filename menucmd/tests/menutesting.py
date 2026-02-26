from menucmd import *
from menucmd import Bind as B
from menucmd.builtins import *
from menucmd.tests.testing_utils import *


def main():
    result = Menu.result
    kwargs = Menu.kwargs

    main_menu = Menu(name = "Hub", exit_key = "x", colors=MenuColors(key=Colors.LIGHT_BLUE + Colors.BOLD), exit_colors=ItemColors(key=Colors.RED))
    lazy_menu = Menu(name = "Lazy Eval", exit_to = main_menu, colors=MenuColors(key=Colors.LIGHT_BLUE + Colors.BOLD))
    builtin_menu = Menu(name = "Builtins", exit_to = main_menu, colors=MenuColors(key=Colors.CYAN  + Colors.BOLD))
    dynamic_menu = Menu(name = "Dynamic Menus", exit_to = main_menu, colors=MenuColors(key=Colors.CYAN + Colors.BOLD))

    menu_A = Menu(name="Menu_A", exit_to = lazy_menu, end_to = Menu.exit_to, colors=MenuColors(key=Colors.RED, message=Colors.FAINT))
    menu_B = Menu(name="Menu_B", exit_to = dynamic_menu, escape_to = Menu.exit_to, colors=MenuColors(key=Colors.RED, message=Colors.FAINT))

    main_menu.append(
        Item(key="e", message="Test Lazy Eval", funcs=[(lazy_menu, ())]),
        Item(key="b", message="Test Builtins", funcs=[(builtin_menu, ())]),
        Item(key="d", message="Test Dynamic Menus", funcs=[(dynamic_menu, ())]),
    )

    lazy_menu.append(
        Item(key='s', message='Square Number', funcs=[
            (input, ("Number: ")),
            (lambda x: x**2, B(float, result)),
            (print, (result)),
        ]),
        Item(key="c", message="Cards", funcs=[
            (shuffle_cards, ()),
            (pick_card, (B(int,B(input, "Choose Card (0-51): ")), result)),
            (print, (result)),
        ]),
        Item(key="m", message="menu composition", funcs=[
            (input, "string for menu_A: "), 
            (menu_A, result)
        ]),
        Item(key="i", message="iterator test", funcs=[
            (input, "list of 3 (separated by spaces)"), 
            (tuple, B(lambda x:x.split(), result)),
            (print, ("result call: ", result.expand())),
            (print, B(lambda x, y, z: x+y+z, result[-2].expand())),
        ]),
        Item(key="a", message="Attribute test",funcs=[
            (input, "integer 1: "), (int, result[-1].INT1),
            (input, "integer 2: "), (int, result[-1].INT2),
            (print, (result.INT1, result.INT2)),
            (print, ("INT1 : ", result.INT1[-1000000].INT1[314198].INT2.INT1)),
            (tuple, ((result.INT1, result.INT2),)),
            (print, ("expanded ", result[-1].EXP.expand())),
            (print, ("expanded (tagged)", result.EXP.expand()))
        ])
    )

    builtin_menu.append(
        Item(key="l", message="Edit List", funcs=[
            (input, ("List items (separated by spaces): ")),
            (edit_list, (B(lambda s: s.split(), result), kwargs(name = "Delete Items"))),
            (print, ("New string:\n", B(" ".join, result))),
        ]),
        Item(key="c", message="Choose Item", funcs=[
            (input, ("List items (separated by spaces): ")),
            (choose_item, (B(lambda s: s.split(), result), kwargs(name="Choose Item"))),
            (print, ("New string:\n", result)),
        ]),
        Item(key="v", message="Confirmation", funcs=[
            (yesno_ver, kwargs(name = "Delete system32?", exit_message = "no")),
            (f_switch(result, (f_escape, yesno_ver)), kwargs(name ="Are you really sure?", exit_message = "no")),
            (f_switch(result, (f_escape, yesno_ver)), kwargs(name = "Are you not sure?", exit_message = "no")),
            (f_switch(result, (yesno_ver, f_escape)), kwargs(name = "Are you sure you are not sure?", exit_message = "wtf?")),
            (print, B(lambda b: "crisis averted!" if b else "deleting...\nsystem32 cannot be deleted!", result))
        ]),
    )

    dynamic_menu.append(
        Item(key="x", message="test keyword function compositions", funcs=[
            (lambda: 0, ()),
            (menu_B, result),
        ]),
        Item(key="s", message="Menu.self usage: insert new item here", funcs=[
            (Menu.insert, (Menu.self, 0, 
                Item(key="*", message="Nice Job!", funcs=[(main_menu, "*")], 
                     colors=ItemColors(key=Colors.RED + Colors.BOLD)
                )
                # LIMITATION:
                # In order to have dynamic reference to other menus, the functions
                # must be defined in the same scope as the menus.  If you wanted to 
                # abstract the above out, it would therefore be impossible.
                # In the future there needs to be a global menu reference interface
                # as well as in the DSL!!
            )),
        ])
    )

    #==================================================================================
  
    menu_A.append(
        Item(key="m", message="reverse and print", funcs=[
            (lambda s: s[::-1], result),
            (print, result)
        ])
    )

    menu_B.append(
        Item(key="s", message="test escape_to", funcs=[
            (escape_on, (result, 3)),
            (print, result),
            (menu_B, B(lambda n: n+1, result[-2]))
        ])
    )

    #==================================================================================

    # Run
    main_menu()


#################################################################################################################

if __name__ == "__main__":
    main()