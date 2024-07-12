from MenuCMD import Menu, Item, edit_list, yesno_ver, f_escape, f_switch
from MenuCMD import Bind as B
from MenuCMD import Menu, Item, edit_list, yesno_ver, f_escape, f_switch
from MenuCMD import Bind as B
import numpy as np


def main():
    result = Menu.result
    kwargs = Menu.kwargs

    main_menu = Menu(name = "Hub", exit_key = "x")
    lazy_menu = Menu(name = "Lazy Eval", exit_to = main_menu)
    builtin_menu = Menu(name = "Builtins", exit_to = main_menu)


    main_menu.append(
        ("e", "Test Lazy Eval", (lazy_menu, (),)),
        ("b", "Test Builtins", (builtin_menu, (),)),
        ("r", "Test code printout", (
            get_code, (),
            print, B("".join, B(lambda r: r[:20],result)),
            input, (),
            get_code, (),
            print, B("".join, B(lambda r: r[20:40],result)),
            input, (),
            get_code, (),
            print, B("".join, B(lambda r: r[40:60], result)),
            input, (),
            get_code, (),
            print, B("".join, B(lambda r: r[60:80], result)),
            input, (),
            get_code, (),
            print, B("".join, B(lambda r: r[80:], result)),
        ))
    )
#
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

        ("v", "Cards2", (
            shuffle_cards, (),
            pick_card, (B(int, B(input, "Choose Card (0-51): ")), result),
            print, (result),
        )),

        ("r", "Result Memory", (
            input, "++n: ", int, result, print, "Partial Sums:"
            ) + sum([(sum, [result[-2*j-2] for j in range(u+1)], print, result) for u in range(10)], start = ())
        )

    )
#
    builtin_menu.append(
        ("l", "Edit List", (
            input, ("List items (separated by spaces): "),
            edit_list, (B(lambda s: s.split(), result), kwargs(name = "Delete Items")),
            print, ("New string:\n", B(" ".join, result)),
        )),

        ("v", "Confirmation", (
            yesno_ver, kwargs(name = "Delete system32?", exit_message = "no"),
            f_switch(result, (f_escape, yesno_ver)), kwargs(name ="Are you really sure?", exit_message = "no"),
            f_switch(result, (f_escape, yesno_ver)), kwargs(name = "Are you not sure?", exit_message = "no"),
            f_switch(result, (yesno_ver, f_escape)), kwargs(name = "Are you sure you are not sure?", exit_message = "no"),
            print, B(lambda b: "crisis averted!" if b else "deleting...\nsystem32 cannot be deleted!", result)
        )),
    )

    main_menu()


#---------------------------------------------------------------------------------------------------------------

def shuffle_cards() -> np.array:
    suites = np.array([x for x in range(4)])
    numbers = np.array([x for x in range(13)])
    deck = np.array(np.meshgrid(suites, numbers)).T.reshape(-1, 2)
    np.random.shuffle(deck)

    return deck


def pick_card(n: int, deck: np.array) -> str:
    display_suite = {0:"Clubs", 1:"Spades", 2:"Hearts", 3:"Diamonds"}
    display_number = {0:"Ace"} | {v:str(v+1) for v in range(1,9)} | {10:"Jack", 11:"Queen", 12:"King"}

    return display_number[deck[n][1]] + " of " + display_suite[deck[n][0]]


#------------------------------------------------------------------------------------------------------------

def get_code() -> list[str]:
    with open("menutesting.py", "r") as code:
        lines = code.readlines()
    code.close()

    return lines



#################################################################################################################

if __name__ == "__main__":
    main()