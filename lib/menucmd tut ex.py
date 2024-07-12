from MenuCMD import Menu, Bind as B

def main():
    #Create New Menu
    result = Menu.result

    menu1 = Menu(name = "Function Composition")

    #Add Items
    menu1.append(
        ("n", "square a number", (
          input, "number ", float, result, lambda n: n**2, result, print, result
        )),
        ("m", "square a number (bind result)", (
            input, "number ", squared, B(float, result), print, result
        )),

    )

    #Run Menu
    menu1()



def squared(n: float) -> float:
    return n**2



if __name__ == "__main__":
    main()