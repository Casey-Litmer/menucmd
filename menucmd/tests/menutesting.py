from menucmd import *
from menucmd import Bind as B
from utils import *


def main():
    result = Menu.result
    kwargs = Menu.kwargs

    main_menu = Menu(name = "Hub", exit_key = "x")
    lazy_menu = Menu(name = "Lazy Eval", exit_to = main_menu)
    builtin_menu = Menu(name = "Builtins", exit_to = main_menu)
    dynamic_menu = Menu(name = "Dynamic Menus", exit_to = main_menu)

    menu_A = Menu(name="Menu_A", exit_to = lazy_menu, end_to = Menu.exit_to)
    menu_B = Menu(name="Menu_B", exit_to = dynamic_menu, escape_to = Menu.exit_to)

    main_menu.append(
        ("e", "Test Lazy Eval", (lazy_menu, ())),
        ("b", "Test Builtins", (builtin_menu, (),)),
        ("d", "Test Dynamic Menus", (dynamic_menu, (),)),
    )

    lazy_menu.append(
        ("s", "Square Number", (
            input, ("Number: "),
            lambda x: x**2, B(float, result),
            print, (result),
        )),

        ("c", "Cards", (
            shuffle_cards, (),
            pick_card, (B(int,B(input, "Choose Card (0-51): ")), result),
            print, (result),
        )),

        ("m", "menu composition", (
            input, "string for menu_A: ", menu_A, result
        )),

        ("i", "iterator test", (
            input, "list of 3 (separated by spaces)", tuple, B(lambda x:x.split(), result),
            print, ("result call: ", result.expand()),
            print, B(lambda x, y, z: x+y+z, result[-2].expand()),
        )),
        ("a", "Attribute test",(
            input, "integer 1: ", int, result[-1].INT1,
            input, "integer 2: ", int, result[-1].INT2,
            print, (result.INT1, result.INT2),
            print, ("INT1 : ", result.INT1[-1000000].INT1[314198].INT2.INT1),
            tuple, ((result.INT1, result.INT2),),
            print, ("expanded ", result[-1].EXP.expand()),
            print, ("expanded (tagged)", result.EXP.expand())
        ))
    )

    builtin_menu.append(
        ("l", "Edit List", (
            input, ("List items (separated by spaces): "),
            edit_list, (B(lambda s: s.split(), result), kwargs(name = "Delete Items")),
            print, ("New string:\n", B(" ".join, result)),
        )),

        ("c", "Choose Item", (
            input, ("List items (separated by spaces): "),
            choose_item, (B(lambda s: s.split(), result), kwargs(name="Choose Item")),
            print, ("New string:\n", result),
        )),

        ("v", "Confirmation", (
            yesno_ver, kwargs(name = "Delete system32?", exit_message = "no"),
            f_switch(result, (f_escape, yesno_ver)), kwargs(name ="Are you really sure?", exit_message = "no"),
            f_switch(result, (f_escape, yesno_ver)), kwargs(name = "Are you not sure?", exit_message = "no"),
            f_switch(result, (yesno_ver, f_escape)), kwargs(name = "Are you sure you are not sure?", exit_message = "wtf?"),
            print, B(lambda b: "crisis averted!" if b else "deleting...\nsystem32 cannot be deleted!", result)
        )),
    )

    dynamic_menu.append(
        ("x", "test keyword function compositions", (
            lambda: 0, (),
            menu_B, result,
        )),

        ("s", "Menu.self usage: insert new item here", (
            Menu.insert, (Menu.self, 0, ("*", "Nice Job!", (main_menu, "*"))),
        ))

        #("d", "open this menu but with exit_to end program", (
        #    dynamic_menu, 1
        #))

        #("n", "test notebook diagram", (
        #    M0, (0),
        #    print, result
        #))
    )

    #==================================================================================
  
    menu_A.append(
        ("m", "reverse and print", (
            lambda s: s[::-1], result, print, result
        ))
    )

    menu_B.append(
        ("s", "test escape_to", (
            escape_on, (result, 3),
            print, result,
            menu_B, B(lambda n: n+1, result[-2])
        ))
    )

    #==================================================================================

    # Run
    main_menu()


#################################################################################################################

if __name__ == "__main__":
    main()