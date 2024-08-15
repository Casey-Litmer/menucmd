from menucmd import Menu, Bind as B, f_escape


result = Menu.result

M0 = Menu(name= "M0", exit_to= lambda x: -x, return_to = lambda x: 2*x)
M2 = Menu(name= "M2", exit_to= M0)
M1 = Menu(name= "M1", exit_to= lambda: 99, return_to= M2, escape_to= lambda x: 199)


M0.append(
    ("x", "main", (
        print, ("result[0] = ", result),
        print, "add 1 to menu input, and open M1",
        lambda x: x+1, result[0],
        M1, result
    ))
)

M1.append(
    ("x", "go to M2", (
        print, ("result[0] = ", result),
        print, "add 1 to menu input.  (will not go to M2 if result is None)",
        lambda x: x+1, result[0]
    )),
#
    ("z", "escape", (
        print, ("result[0] = ", result),
        print, "add 1 to menu input, then escape",
        lambda x: x+1, result[0],
        f_escape, ()
    )),
)

M2.append(
    ("x", "add 1 to menu input, call M0 with 0", (
        print, ("result[0] = ", result),
        lambda x: x+1, result[0],
        M0, 0
    ))
)