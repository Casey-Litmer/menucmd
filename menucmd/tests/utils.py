import numpy as np
import numpy.typing as npt


def shuffle_cards() -> npt.NDArray:
    suites = np.array([x for x in range(4)])
    numbers = np.array([x for x in range(13)])
    deck = np.array(np.meshgrid(suites, numbers)).T.reshape(-1, 2)
    np.random.shuffle(deck)
    return deck

def pick_card(n: int, deck: npt.NDArray) -> str:
    display_suite = {0:"Clubs", 1:"Spades", 2:"Hearts", 3:"Diamonds"}
    display_number = {0:"Ace"} | {v:str(v+1) for v in range(1,10)} | {10:"Jack", 11:"Queen", 12:"King"}
    return display_number[deck[n][1]] + " of " + display_suite[deck[n][0]]

def get_code() -> list[str]:
    with open("menutesting.py", "r") as code:
        lines = code.readlines()
    code.close()
    return lines