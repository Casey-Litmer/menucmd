from MenuCMD import Menu, yesno_ver, edit_list
from macrolib.typemacros import list_union
from macrolib.jsonmacros import *
import winreg, os


CONFIG_PATH = "config.json"

def main():
    result = Menu.result
    kwargs = Menu.kwargs

    main_menu = Menu()
    clear_menu = Menu(exit_to = main_menu)

    main_menu.append(
        ("o", "open windows on startup (clears list)",
         (input_paths, (), save_files, (result), update_reg, (result, False))),
        ("x", "open windows on startup (1-time)",
         (input_paths, (), save_files, (result), update_reg, (result, True))),
        ("a", "add more windows",
         (input_paths, (), merge_paths, (result), save_files, (result), update_reg, (result, False))),
        ("b", "add more windows (1 time)",
         (input_paths, (), merge_paths, (result), save_files, (result), update_reg, (result, True))),
        ("c", "clear list", (clear_menu, ())),
    )

    clear_menu.append(
        ("s", "delete one",
         (clear, (), main_menu, ())),
        ("x", "delete all",
         (clear_all, (), main_menu, ())),
    )

    return main_menu()


#---------------------------------------------------------------------------------------------------------------------

def input_paths() -> list:
    paths = []
    while True:
        path = input("Path: ")
        if path.strip():
            paths.append(path)
        else:
            return paths


def merge_paths(paths: list) -> list:
    return list_union(open_json(CONFIG_PATH)["paths"], paths)


def save_files(paths: list) -> list:
    saved_paths = open_json(CONFIG_PATH)
    saved_paths["paths"] = paths

    save_json(saved_paths, CONFIG_PATH)
    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/#
    lines = list(map(lambda path: "start explorer.exe " + f"\"{path}\"", paths))
    write_bat(lines, "open_windows.bat")

    return paths


def update_reg(paths: list, onetime: bool) -> None:
    bat_file = "open_windows.bat"
    absolute_file_path = os.path.join(os.getcwd(), bat_file)

    save_reg_key(absolute_file_path, f"PyTools4Windows_{bat_file.strip(".bat")}")

    if onetime:
        r_bat_file = "remove_reg_keys.bat"
        r_absolute_file_path = os.path.join(os.getcwd(), r_bat_file)
        remove_reg_entry_bat(r_bat_file)
        save_reg_key(r_absolute_file_path, f"PyTools4Windows_{r_bat_file.strip(".bat")}")



def clear() -> None:
    config = open_json(CONFIG_PATH)
    paths = config["paths"]
    paths = edit_list(paths, name = "Delete:")
    save_files(paths)


def clear_all() -> None:
    if not open_json(CONFIG_PATH)["paths"]:
        print("--*No Entries*--")
        return None

    if yesno_ver():
        save_files([])


#---------------------------------------------------------------------------------------------------------------------

def write_bat(lines: list | tuple, file_path: str) -> None:
    text = "@echo off\n" + "\n".join(x for x in lines)

    with open(file_path, "w") as f:
        f.write(text)
    f.close()


def save_reg_key(bat_file_path: str, entry_name: str) -> str:
    safemode = False

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                         winreg.KEY_ALL_ACCESS)
    if not safemode:
        winreg.SetValueEx(key, entry_name, 0, winreg.REG_SZ, bat_file_path)
    winreg.CloseKey(key)

    return entry_name


def remove_reg_entry_bat(bat_file_path: str) -> None:
    def add_line(name):
        return "reg delete \"" + r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" + "\" " +  f"/v {name} /f"

    lines = []
    lines.append(add_line(f"PyTools4Windows_open_windows"))
    lines.append(add_line(f"PyTools4Windows_{bat_file_path.strip(".bat")}"))

    write_bat(lines, "remove_reg_keys.bat")






#######################################################################################################################

if __name__ == "__main__":
    main()