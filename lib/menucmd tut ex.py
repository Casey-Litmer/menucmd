import sys
print(sys.path)
from MenuCMD import Menu

#Create New Menu
menu1 = Menu(name = "First Menu")

#Add an Item
menu1.append(
    ("x", "hello world program", (
      print, "hello world!"
    ))
)

menu1()