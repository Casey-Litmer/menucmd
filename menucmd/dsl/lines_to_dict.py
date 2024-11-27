import re


def lines_to_dict(lines: list[str]) -> dict:
    """
    Converts list of lines to dictionary structure to be further parsed:
    {
    'id':{
        'name':'menu_name',
        'arg_to': 'func_arg_to',
        'exit_to': 'func_exit_to',
        'exit_key': 'e', ...
        'Items': [
                ['key', 'message', 'func1(args)', 'func2(args)'], ...
            ]
        }, ...
    }
    """
    #Remove empty lines and comments and get list
    lines  = [line for line in lines if line.strip() and not line.strip()[:1] == '#']

    struct_ = {}
    menu_id = ''
    menu_dict = {}
    item_list = []
    func_list = []
    item_key = ''
    item_message = ''

    #'a:b:c' -> ('a', 'b:c')
    split_pattern = r"([^:]+):([^:]+.*)"

    #Iterate in reverse so "Menu:" and "Item:" compile aggregated data
    for line in reversed(lines):

        #Add menu to struct_
        if line.strip() == "Menu:":
            if not menu_id:
                raise AttributeError("Missing Menu 'id' field in {file}")

            struct_[menu_id] = menu_dict | {"Items":item_list}

            #Reset Tracked Structures
            menu_id = ''
            menu_dict = {}
            item_list = []

        #Add item to item_list
        elif line.strip().startswith("Item:"):
            if not item_key:
                raise AttributeError("Missing Item 'key' field in {file}")
            if not item_message:
                raise AttributeError("Missing Item 'message' field in {file}")

            item_list.append([item_key, item_message] + list(reversed(func_list)))

            func_list = []
            item_key = ''
            item_message = ''

        elif line.startswith(' ' * 8):
            #Construct menu item
            split_col = re.match(split_pattern, line.strip()).groups()
            name = split_col[0].strip()
            val = split_col[1].strip()

            if name == "key":
                item_key = val
            elif name == "message":
                item_message = val
            elif name == "func":
                func_list.append(val)

        elif line.startswith(' ' * 4):
            #Set attribute to menu_dict
            split_col = re.match(split_pattern, line.strip()).groups()
            name = split_col[0].strip()
            val = split_col[1].strip()

            if name == "id":
                #Set menu_id to hash menu_dict in struct_
                menu_id = val
            else:
                #Otherwise, set the attribute
                menu_dict[name] = val

    return struct_