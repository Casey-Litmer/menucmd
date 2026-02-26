from menucmd.dsl import build_menus
from menucmd.tests.testing_utils import *
import os


def main():
    path = os.path.join(os.path.dirname(__file__), 'menutesting.mcmd')
    menus = build_menus(path)

    menus['main_menu']()

#################################################################################################################

if __name__ == "__main__":
    main()