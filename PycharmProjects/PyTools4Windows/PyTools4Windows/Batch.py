import os.path
import subprocess as sp
from os import *

### .py --> .exe ###
py_file = input("Python File: ")
out_path = r"C:\Users\litme\PyTools4Windows"
out_path = path.join(out_path, py_file.strip(".py")) if path.exists(out_path) else getcwd()


result = sp.run(["pyinstaller", "-y", "--distpath", out_path, "--workpath", out_path +"/build", "--specpath", out_path +"/spec", f"{py_file}"],
       text=True,
       capture_output=True
       )
print(result.stdout)
print(result.stderr)