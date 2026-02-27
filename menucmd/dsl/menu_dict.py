

#Output type
class MenuDict(dict):
    """
    Dictionary of menu objects that can be additionally referenced by attributes:
    menu_dict['menu_id'] = menu_dict.menu_id
    """
    def __init__(self, menus: list):
        for menu in menus:
            self.__setattr__(menu._id, menu)

        self.menus = {menu._id: menu for menu in menus}

    def __getitem__(self, item):
        return self.menus[item]
    
    def get(self, item):
        return self.menus[item]
    
    def __iter__(self):
        return iter(self.menus)
    
    def __repr__(self):
        return f"<Menus {self.menus}>"
    
    def keys(self):
        return self.menus.keys()
    
    def values(self):
        return self.menus.values()
    
    def items(self):
        return self.menus.items()