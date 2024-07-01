import os, sys
import subprocess as sp
from macrolib.jsonmacros import *
from MenuCMD import Menu


CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.json")
print("CONFIG_PATH:   " + CONFIG_PATH)
CONFIG_DEFAULT = {"outpath":os.getcwd(), "cwd":os.getcwd()}


def main():
    result = Menu.result

    Main_Menu = Menu(name = "Pyinstaller")
    Batch_Menu = Menu(name = "Batch", exit_to = Main_Menu)
    Settings_Menu = Menu(name = "Settings", exit_to = Main_Menu, end_to = Menu.exit_to)
    Continue = Menu(name = "Batch Another File?", exit_message = "close program")


    Main_Menu.append(
        ("b", "Batch a Script", (Batch_Menu, ())),
        ("s", "Settings", (show_paths, (), Settings_Menu, ()))
    )

    Batch_Menu.append(
        ("b", "Batch", (batch, (), Continue, ())),
        ("o", "Batch + open directory", (batch, (), open_dir, (result), Continue, ())),
    )

    Settings_Menu.append(
        ("w", "Change Working Directory", (save_path, ("cwd"))),
        ("d", "Change Output Directory", (save_path, ("outpath"))),
    )

    Continue.append(
        ("x", "yes", (Batch_Menu, ()))
    )


    Main_Menu()

#---------------------------------------------------------------------------------------------------------------------

def batch() -> str | None:
    config = open_json(CONFIG_PATH, default = CONFIG_DEFAULT)

    script = input("Python File Path: ")

    if not script:
        return Menu.escape

    full_path = os.path.join(config["cwd"], script)
    script_path = full_path if os.path.exists(full_path) else script

    if not os.path.exists(script_path):
        print("\n--*File Not Found*--")
        return Menu.escape

    exe_name = input("(leave empty to use name of .py file)\nExe Name: ")
    exe_name = exe_name.strip(".exe") if exe_name else os.path.basename(script).strip(".py")

    outpath = os.path.join(config["outpath"], exe_name)

    script_path = change_relative_path_behaviour(script_path, config["outpath"])

    print("Compiling...")

    out = sp.run(["pyinstaller", script_path, "--name", exe_name,
                  "--distpath", outpath, "--specpath", outpath, "--onefile"],
                 capture_output = True, text = True)

    print(out.stdout)
    print(out.stderr)

    os.rmdir(script_path)

    return outpath


def open_dir(dir: str) -> None:
    sp.run(["explorer.exe", dir])


def show_paths() -> None:
    config = open_json(CONFIG_PATH, default = CONFIG_DEFAULT)
    print("\n")
    print("Working Directory:  " + config["cwd"])
    print("Output Directory:  " + config["outpath"])


def save_path(inorout: str) -> None:
    config = open_json(CONFIG_PATH, default = CONFIG_DEFAULT)

    new_path = input("\n('cwd' for current directory)\n" +
                     {"cwd":"Working","outpath":"Output"}[inorout] + " Directory: ")

    new_path = os.getcwd() if new_path == "cwd" else new_path

    config[inorout] = new_path if new_path else config[inorout]

    if not os.path.exists(config[inorout]):
        print("\n--*Directory Not Found*--")
        return save_path(inorout)

    save_json(config, CONFIG_PATH)



def change_relative_path_behaviour(python_script_path: str, exe_dir: str) -> str:
    monkey_patch = "\n".join([
        "import os",
        "cmd_dir = os.getcwd()",
        f"os.chdir({exe_dir})",
        "def modify_chdir(C):",
        "\tdef chdir(path):",
        "\t\tos.getcwd = lambda: path",
        "\t\treturn C(path)",
        "\treturn inner",
        "os.chdir = modify_chdir(os.chdir)",
        "os.getcwd = lambda: cmd_dir",
        "\n"
    ])

    with open(python_script_path, "r") as script:
        lines = script.readlines()
    script.close()

    temp_script_path = "_" + python_script_path

    with open(temp_script_path, "w") as temp_script:
        temp_script.write(monkey_patch + "\n".join(lines))
    temp_script.close()

    return temp_script_path

#######################################################################################################################

if __name__ == "__main__":
    main()