from menucmd.dsl import build_menus
from menucmd.tests.testing_utils import *
import os


def main():
    path = os.path.join(os.path.dirname(__file__), 'dsltesting.mcmd')

    menus = build_menus(
        path, 
        compile_to_py = True,
        imports = {
            "menucmd.tests.testing_utils" : ['*'],
        }
    )

    menus['main_menu']()

#################################################################################################################

if __name__ == "__main__":
    main()