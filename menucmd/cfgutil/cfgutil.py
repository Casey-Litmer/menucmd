from os import getcwd
from macrolibs.filemacros import open_json, save_json
from macrolibs.typemacros import list_union
from typing import Callable
from dataclasses import asdict
from menucmd import Colors as C, Menu, Item, ItemColors
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
    # Configs
    #==================================================================================

    def get_config(self, callback = None):
        """
        Returns a wrapper function that retrieves the config from the 
        json file and applies a callback if provided.
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
                      exclude_from_list = [],
                      **kwargs
                      ):
        """"""
        menu = Menu(
            name = name, 
            arg_to = self._show_settings(exclude_from_list),
            exit_to = f_end,
            end_to = Menu.exit_to,
            **kwargs,
        )

        if isinstance(config, CommandHistoryData):
            menu.append(
                Item(
                    key = "h", 
                    message = "Command History Length",
                    colors = ItemColors(),
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
                    colors = ItemColors(),
                    funcs = [
                        (self.change_directory, (Menu.result.CONFIG, name)),
                        (self.save_config, (Menu.result.CONFIG)),
                    ]
                ) for name, (key, _) in config.dirs.items()
            ])

        return menu(config)
    

    def _show_settings(self, exclude_from_list: list[str]):
        def wrapper (config: BaseData) -> BaseData:
            """Takes config struct, prints directories and returns struct."""
            c_settings = self._merge_colors().settings_color
            print('\n')

            if isinstance(config, CommandHistoryData) and "history_length" not in exclude_from_list:
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

    def add_to_history(self, config: CommandHistoryData, command, compare_as = None):
        """"""
        # Add to history
        config.command_history.append(command)

        # Automatic flattening comparison for commands as BaseData
        if not compare_as:
            compare_as = lambda x: x
            if isinstance(command, BaseData):
                compare_as = asdict

        # Flatten and limit command history
        config.command_history = list_union([config.command_history], compare_as=compare_as)
        config.command_history = config.command_history[:config.history_length]


    def clear_command_history(self, config: CommandHistoryData):
        """"""
        config.command_history = []


    def get_command_history(self, config: CommandHistoryData, callback: Callable | None = None, **kwargs) -> str | object:
        """"""
        c_message = self._merge_colors().message_color   
        command_history = config.command_history
        
        display_as = callback if callback is not None \
            else lambda x: f"{c_message}{x}{C.END}"
        
        # Choose command
        return choose_item(
            command_history, 
            exit_val = Menu.escape, 
            display_as = display_as,
            empty_message= "Command history is empty.",
            **kwargs,
        )
    
    def _change_history_length(self, config: CommandHistoryData):
        """
        """
        merged_colors = self._merge_colors()
        c_settings = merged_colors.settings_color
        c_error = merged_colors.error_color

        while new_length := input(f"{c_settings}New Length:{C.END} "):
            if not new_length.strip():
                return
            if not new_length.strip().isdigit():
                print(f"{c_error}{new_length} is not a postive number.{C.END}")
                continue
            config.history_length = int(new_length)
            break

    #==================================================================================
    # Directories
    #==================================================================================

    def change_directory(self, config: DirectoryData, key: str):
        """
        Update config paths.  
        Takes the config struct and stores the user input into the corresponding key.
        """
        merged_colors = self._merge_colors()
        c_settings = merged_colors.settings_color
        c_message = merged_colors.message_color

        # Get new dir
        print(f"{c_message}('cwd' for current directory){C.END}")
        new_dir = input(f"{c_settings}{({'cwd':'Working Directory: ', 'outpath':'Output Directory: '})[key]}{C.END}").strip()
        
        # Return on empty
        if not new_dir:
            return
        
        # Substitute cwd
        new_dir = getcwd() if new_dir == "cwd" else new_dir

        # Update config
        if key in config.dirs.keys():
            config.dirs[key] = (config.dirs[key][0], new_dir)
        else:
            raise KeyError(f"{key} does not exist on {config}")

    #==================================================================================
    # Util
    #==================================================================================
    
    def _merge_colors(self):
        return ConfigColors(
            message_color = self.colors.message_color if self.colors.message_color else Menu.colors.message,
            settings_color = self.colors.settings_color if self.colors.settings_color else Menu.colors.key,
            error_color = self.colors.error_color if self.colors.error_color else Menu.colors.invalid_key,
        )