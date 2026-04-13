import random

def shuffle_cards() -> list:
    # Create a deck of 52 pairs: (suite, number)
    deck = [[s, n] for s in range(4) for n in range(13)]
    random.shuffle(deck)
    return deck

def pick_card(n: int, deck: list) -> str:
    display_suite = {0:"Clubs", 1:"Spades", 2:"Hearts", 3:"Diamonds"}
    display_number = {0:"Ace"} | {v:str(v+1) for v in range(1,10)} | {10:"Jack", 11:"Queen", 12:"King"}
    return display_number[deck[n][1]] + " of " + display_suite[deck[n][0]]

def get_code() -> list[str]:
    with open("menutesting.py", "r") as code:
        lines = code.readlines()
    return lines