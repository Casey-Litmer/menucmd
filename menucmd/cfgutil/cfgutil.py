from os import getcwd
from macrolibs.filemacros import open_json, save_json
from macrolibs.typemacros import list_union
from typing import Callable
from dataclasses import asdict
from menucmd import Colors as C, Menu, Item, ItemColors, MenuColors
from menucmd.builtins import choose_item, f_end
from .dataclasses import *
from .ansi_scheme import ConfigColors

#==================================================================================
# Config Utils
#==================================================================================


class MenuConfig:
    def __init__(self, 
                 config_path: str,
                 default_config: BaseData,
                 colors: ConfigColors = ConfigColors(),
                ):
        self.config_path = config_path
        self.default_config = default_config
        self.colors = colors

    #==================================================================================
    # Config Load / Save
    #==================================================================================

    def get_config(self, callback = None):
        """
        Returns a wrapper function that retrieves the config from the 
        json file and applies a callback if provided.  Primarily used 
        for arg_to.
        """
        def wrapper(config: BaseData | None = None):
            if not config:
                _ConfigType = type(self.default_config)
                json = open_json(self.config_path, asdict(self.default_config))
                config = callback(config) if callback else _ConfigType(**json)
            return config
        return wrapper


    def save_config(self, config: BaseData, callback: Callable | None = None):
        """Saves config to json file."""
        json = asdict(callback(config) if callback is not None else config)
        save_json(json, self.config_path)

    #==================================================================================
    # Settings
    #==================================================================================
    
    def open_settings_menu(self, 
                      config: BaseData,
                      name = "Settings", 
                      exit_to = f_end,
                      colors = MenuColors(),
                      exclude_from_list = [],
                      **kwargs
                      ):
        """Returns a menu of settings based on the config struct provided."""
        _colors = self._merge_colors()
        colors = colors.merge(MenuColors(
            key = _colors.settings_color,
            message = _colors.message_color,
            invalid_key = _colors.error_color
        ))

        _kwargs = dict(kwargs)
        _kwargs.pop("arg_to", None)

        menu = Menu(
            name = name, 
            arg_to = self._show_settings(exclude_from_list),
            exit_to = exit_to,
            colors = colors,
            **_kwargs,
        )

        if isinstance(config, HistoryData):
            menu.append(
                Item(
                    key = "h", 
                    message = "Command History Length",
                    funcs = [
                        (self._change_history_length, (Menu.result.CONFIG)),
                        (self.save_config, (Menu.result.CONFIG)),
                    ]
                )
            )
        
        if isinstance(config, DirectoryData):
            menu.append(*[
                Item(
                    key = key, 
                    message = name,
                    funcs = [
                        (self.change_directory, (Menu.result.CONFIG, name)),
                        (self.save_config, (Menu.result.CONFIG)),
                    ]
                ) for name, (key, _) in config.dirs.items()
            ])

        return menu(config)
    

    def settings_item(self, 
                      menu_name = "Settings",
                      key = "$",
                      message = "Settings", 
                      colors: ItemColors = ItemColors(),
                      menu_colors: MenuColors = MenuColors(),
                      display_as = None,
                     ) -> Item:
        """Returns a menu item for accessing settings."""

        _colors = self._merge_colors()
        colors = colors.merge(ItemColors(
            key = _colors.settings_color,
        ))

        return Item(
            key = key, 
            message = message,
            colors = colors,
            funcs = [
                (
                    self.open_settings_menu, 
                    (
                        Menu.result.CONFIG, 
                        Menu.kwargs(
                            name = menu_name, 
                            colors = menu_colors,
                            display_as = display_as,
                        )
                    )
                ),
            ],
        )
    

    def _show_settings(self, exclude_from_list: list[str]):
        def wrapper (config: BaseData) -> BaseData:
            """Takes config struct, prints directories and returns struct."""
            c_settings = self._merge_colors().settings_color
            print('\n')

            if isinstance(config, HistoryData) and "history_length" not in exclude_from_list:
                print(f"{c_settings}Max History Length:{C.END} {config.history_length}")
            
            if isinstance(config, DirectoryData):
                for name, (_, path) in config.dirs.items():
                    if name not in exclude_from_list:
                        print(f"{c_settings}{name}:{C.END} {path}")

            return config
        return wrapper
    

    #==================================================================================
    # Command History
    #==================================================================================

    def add_to_history(self, config: HistoryData, command, compare_as = None):
        """Adds a command to the history."""
        # Add to history
        config.history.append(command)

        # Automatic flattening comparison for commands as BaseData
        if not compare_as:
            compare_as = lambda x: x
            if isinstance(command, BaseData):
                compare_as = asdict

        # Flatten and limit command history
        config.history = list_union([config.history], compare_as=compare_as)
        config.history = config.history[:config.history_length]


    def clear_history(self, config: HistoryData):
        """Clears command history in config."""
        config.history = []


    def get_history(self, 
                    config: HistoryData, 
                    colors: MenuColors = MenuColors(),
                    empty_message = "History is empty.",
                    exit_val = Menu.escape,
                    **kwargs) -> str | object:
        """Returns a menu of command history to choose from. Returns Menu.escape on exit."""
        _colors = self._merge_colors()   
        colors = colors.merge(MenuColors(
            key = _colors.history_color,
            message = _colors.message_color,
            invalid_key = _colors.error_color
        ))

        # Choose command
        return choose_item(
            config.history, 
            exit_val = exit_val, 
            empty_message = empty_message,
            colors = colors,
            **kwargs,
        )
    

    def history_item(self, 
                      callback = None,
                      menu_name = "History",
                      key = "#",
                      message = "History", 
                      colors: ItemColors = ItemColors(),
                      menu_colors: MenuColors = MenuColors(),
                      display_as = None,
                     ) -> Item:
        """
        Returns an item for selecting from history.  Use callback to do something with the selection.  
        The Item returns "None" by default.
        """
        _colors = self._merge_colors()
        colors = colors.merge(ItemColors(
            key = _colors.history_color,
        ))

        _callback = f_end if callback is None else callback

        return Item(
            key = key, 
            message = message,
            colors = colors,
            funcs = [
                (
                    self.get_history, 
                    (
                        Menu.result.CONFIG, 
                        Menu.kwargs(
                            name = menu_name, 
                            colors = menu_colors,
                            display_as = display_as,
                        )
                    )
                ),
                (_callback, Menu.result),
            ],
        )
    

    def _change_history_length(self, config: HistoryData):
        """Update config history length."""
        _colors = self._merge_colors()

        while new_length := input(f"{_colors.settings_color}New Length:{C.END} "):
            if not new_length.strip():
                return
            if not new_length.strip().isdigit():
                print(f"{_colors.error_color}{new_length} is not a postive number.{C.END}")
                continue
            config.history_length = int(new_length)
            break

    #==================================================================================
    # Directories
    #==================================================================================

    def change_directory(self, config: DirectoryData, name: str):
        """
        Update config paths.  
        Takes the config struct and stores the user input into the corresponding key.
        """
        _colors = self._merge_colors()

        # Get new dir
        print(f"{_colors.message_color}('cwd' for current directory){C.END}")
        new_dir = input(f"{_colors.settings_color}New {config.dirs[name][0]}:{C.END} ").strip()
        
        # Return on empty
        if not new_dir:
            return
        
        # Substitute cwd
        new_dir = getcwd() if new_dir == "cwd" else new_dir

        # Update config
        if name in config.dirs.keys():
            config.dirs[name] = (config.dirs[name][0], new_dir)
        else:
            raise KeyError(f"{name} does not exist on {config}")

    #==================================================================================
    # Util
    #==================================================================================
    
    def _merge_colors(self):
        """Merge config colors with current menu colors"""
        return ConfigColors(
            message_color = self.colors.message_color if self.colors.message_color else Menu.current_colors.message,
            error_color = self.colors.error_color if self.colors.error_color else Menu.current_colors.invalid_key,
            history_color = self.colors.history_color if self.colors.history_color else Menu.current_colors.key,
            settings_color = self.colors.settings_color if self.colors.settings_color else Menu.current_colors.key,
        )