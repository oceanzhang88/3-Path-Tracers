import importlib
import os
from pathlib import Path


def import_children(path: str, module: str):
    """Import all py files in the same folder"""
    assert path.endswith("__init__.py"), "import_children should only be called from __init__.py"
    folder = Path(path).parent
    files = os.listdir(folder)
    for file in files:
        if file == "__init__.py" or not file.endswith(".py"):
            continue
        name = module + "." + os.path.splitext(file)[0]
        importlib.import_module(name)
