import os
import sys
import importlib.util
from macrolibs.filemacros import open_json, save_json
from menucmd.dsl.generate_spec import generate_spec
from .menu_dict import MenuDict
from .lines_to_dict import lines_to_dict
from .dict_to_objs import dict_to_objs
from .dict_to_py import dict_to_py

#==================================================================================

def build_menus(
        file: str, 
        imports: list[str] | dict[str, list[str]] = [],
        compile_to_py = False,
    ) -> MenuDict:
    """Convert .mcmd file to attributable dict of menus"""

    # Construct objects from mcmd
    if not compile_to_py:

        # Get mcmd text
        with open(file, 'r') as f:
            file_text = f.read()
            lines = file_text.splitlines()
        f.close()

        # Convert to dict
        struct_ = lines_to_dict(lines)

        # Convert to MenuDict
        menus = dict_to_objs(struct_)

    # Compile mcmd to python
    else:
        cwd = os.path.dirname(os.path.abspath(file))
        compiled_dir = os.path.join(cwd, '__compiled__')
        
        menus_py_path = os.path.join(compiled_dir, '__menus__.py')
        cache_txt_path = os.path.join(compiled_dir, '__mcmdcache__.txt')
        init_py_path = os.path.join(compiled_dir, '__init__.py')
        json_cache_path = os.path.join(compiled_dir, '__parsercache__.json')

        # Check if running as a PyInstaller bundle
        is_frozen = getattr(sys, 'frozen', False)

        if not is_frozen:
            # Get mcmd text
            with open(file, 'r') as f:
                file_text = f.read()
                lines = file_text.splitlines()
            f.close()

            os.makedirs(compiled_dir, exist_ok=True)
            cache_text = ""

            if os.path.exists(cache_txt_path):    
                with open(cache_txt_path, 'r') as f:
                    cache_text = f.read()
                f.close()

            # Recompile only if source changed during development
            if cache_text != file_text:

                # Convert to dict
                struct_ = lines_to_dict(lines)
                
                # Convert to python
                py_text = dict_to_py(struct_, imports)

                # Save files
                with open(menus_py_path, 'w') as f:
                    f.write(py_text)
                f.close()
                with open(cache_txt_path, 'w') as f:
                    f.write(file_text)
                f.close()
                with open(init_py_path, 'w') as f:
                    f.write("from .__menus__ import *")
                f.close()
                save_json(struct_, json_cache_path)

                # Generate .spec file for PyInstaller
                generate_spec(cwd, file, imports)

        # Create MenuDict from imports
        spec = importlib.util.spec_from_file_location("menus", menus_py_path)
        module = importlib.util.module_from_spec(spec) #type: ignore
        spec.loader.exec_module(module) #type: ignore

        # Retrieve and patch menus (generated classes default _id to memory address)
        menu_list = []
        for d in open_json(json_cache_path)["Menu"]:
            menu_obj = getattr(module, d["id"])
            setattr(menu_obj, "_id", d["id"])
            menu_list.append(menu_obj)
            
        menus = MenuDict(menu_list)

    return menus
