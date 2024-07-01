import os, json
import MenuCMD as mc


CONFIG_PATH = "config.json"


def main():
    #
    menu = input("""
    Choose Action:
    [o]- open windows on startup (clears list)
    [x]- open windows on startup (1-time)
    [a]- add more windows
    [b]- add more windows (1 time)
    [c]- clear list
    [e]- exit
    """)
    switch = {
        "o": (create_bat, (main, False, True)),
        "x": (create_bat, (main, True ,True)),
        "a": (create_bat, (main, False, False)),
        "b": (create_bat, (main, True, False)),
        "c": (clear_bat, (main,)),
        "e": (lambda: 0, ())
    }[menu]
    result = switch[0](*switch[1])
    return result




def clear_bat(return_to):
    settings = open_json(CONFIG_PATH)
    #
    if settings["paths"]:
        menu = input("""
    Choose Action:
    [s]- delete one
    [x]- delete all
    [e]- exit
    """)
        if menu == "s":
            paths = settings["paths"]
            print("\n" + " "*4 + "Delete:")
            n = input("\n".join([f"    [{u}]- '{path}'" for u, path in enumerate(paths)]) + "\n    ")
            try:
                if int(n) not in range(len(paths)):
                    raise ValueError
                path = paths[:int(n)] + paths[int(n) + 1:]
                settings["paths"] = path
                save_json(path, CONFIG_PATH)
                #/\/\/\/\/\/\/\/\/#
                #@echo off + paths !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Make into a function!
            except ValueError:
                print("Invalid Selection")
        elif menu == "x":
            settings["paths"] = []
            save_json([], CONFIG_PATH)
            #/\/\/\/\/\/\/\/\/#
            #@echo off       !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        elif menu == "e":
            pass
    else:
        print("No Saved Windows")

    with open(CONFIG_PATH, "w") as file:
        json.dump(settings, file)
    file.close()
    #
    return return_to()


def create_bat(return_to, Onetime, Overwrite):
    settings = open_json(CONFIG_PATH)
    paths = []
    _in = input("Path: ")
    while _in.strip() != "":
       paths.append(_in)
       _in = input("Path: ")
    if not paths:
        return return_to()

    if not Overwrite:
        paths = list_union(paths, settings["paths"])
    #
    settings["paths"] = paths
    save_json(settings,CONFIG_PATH)
        #/\/\/\/\/\/\/\/\/\/# json vs batch out
    text = "@echo off\n" + "\n".join(["start explorer.exe " + f'"{path}"' for path in paths])
    print(text)
    out_path = "open_windows.bat"
    #
    with open(out_path, "w") as file:
        file.write(text)
    file.close()

    ###UPDATE REGISTRY###
    #TODO NEXT!!!~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    return return_to()

#---------------------------------------------------------------------------------------------------------------------#

def default_config():
    return {
        "paths": [],
    }

def open_json(path, default = default_config):
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
def list_union(a, b):
    return list(set(a).union(set(b)))

#######################################################################################################################

if __name__ == "__main__":
    main()