import os, json
from MenuCMD import Menu, YesNo_ver

CONFIG_PATH = "config.json"

main_menu = Menu()
clear_menu = Menu(exit_to=main_menu)


def main():
    main_menu.append(
        ("o", "open windows on startup (clears list)",
         (input_paths,(), save_files,(Menu.result), update_reg, (Menu.result, False))),
        ("x", "open windows on startup (1-time)",
         (input_paths,(), save_files, (Menu.result), update_reg, (Menu.result, True))),
        ("a", "add more windows",
         (input_paths,(), merge_paths,(Menu.result), save_files,(Menu.result), update_reg, (Menu.result, False))),
        ("b", "add more windows (1 time)",
         (input_paths,(), merge_paths,(Menu.result), save_files,(Menu.result), update_reg, (Menu.result, True))),
        ("c", "clear list", (clear_menu, ())),
    )

    clear_menu.append(
        ("s", "delete one",
         (clear, (), main_menu, ())),
        ("x", "delete all",
         (clear_all, (), main_menu, ())),
    )
    return main_menu()


def clear_all() -> None:
    settings = open_json(CONFIG_PATH)
    if not settings["paths"]:
        print("No Saved Windows")
        return None
    if YesNo_ver():
        settings["paths"] = []
        save_json(settings, CONFIG_PATH)
        #/\/\/\/\/\/\/\/\/#
        #@echo off + paths !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Make into a function!


def clear() -> None:
    settings = open_json(CONFIG_PATH)
    paths = settings["paths"]

    def delete_path(n: int):
        path = paths[:n] + paths[n + 1:]
        settings["paths"] = path
        save_json(settings, CONFIG_PATH)
        #/\/\/\/\/\/\/\/\/#
        #@echo off + paths !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Make into a function!

    delete_menu = Menu(name="Delete", empty_message="No Saved Windows")
    for u, _path in enumerate(settings["paths"]):
        delete_menu.append((str(u), _path, (delete_path, (u), clear, ())))
    return delete_menu()


def input_paths() -> list:
    paths = []
    _in = input("Path: ")
    while _in.strip() != "":
        paths.append(_in)
        _in = input("Path: ")
    if not paths:
        return Menu.escape
    return paths


def merge_paths(paths: list) -> list:
    settings = open_json(CONFIG_PATH)
    return list_union(paths, settings["paths"])


def save_files(paths: list) -> str:
    settings = open_json(CONFIG_PATH)
    settings["paths"] = paths
    save_json(settings, CONFIG_PATH)
    #/\/\/\/\/\/\/\/\/\/# json vs batch out
    text = "@echo off\n" + "\n".join(["start explorer.exe " + f'"{path}"' for path in paths])
    out_path = "open_windows.bat"
    with open(out_path, "w") as file:
        file.write(text)
    file.close()
    return out_path


def update_reg(file: str, onetime: bool) -> None:
    ###UPDATE REGISTRY###
    #TODO NEXT!!!~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #create batch file on startup to turn off possibly for OneTime???
    pass


#---------------------------------------------------------------------------------------------------------------------#

def default_config():
    return {
        "paths": [],
    }


def open_json(path, default=default_config):
    if not os.path.exists(path):
        with open(path, "x"):
            pass
    with open(path, "r") as file:
        content = file.read()
        if content.strip():
            data = json.loads(content)
        else:
            data = default()
    file.close()
    return data


def save_json(data, path):
    with open(path, "w") as file:
        json.dump(data, file)
    file.close()


##TODO: Make new library
def list_union(a: list, b: list) -> list:
    return list(set(a).union(set(b)))


#######################################################################################################################

if __name__ == "__main__":
    main()
