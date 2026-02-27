from menucmd.tests.testing_utils import *
from menucmd.trampoline.trampoline import MenuManager
import os


def main():
    path = os.path.join(os.path.dirname(__file__), 'tramptesting.mcmd')
    manager = MenuManager(mcmd=path, base_menu='main_menu', debug=True)
    manager()

#################################################################################################################

if __name__ == "__main__":
    main()