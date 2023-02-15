import os
from pathlib import Path
from typing import List, Union


def mkdir(path: Union[str, Path]) -> Path:
    path = Path(path)
    os.makedirs(path, exist_ok=True)
    return path


def read_lines(path: Union[str, Path], strip_line_breaks: bool = True, strip_spaces: bool = False, remove_empty: bool = False) -> List[str]:
    with open(path, "r") as f:
        lines = f.readlines()

    if strip_line_breaks:
        lines = [line.rstrip("\n\r") for line in lines]
    if strip_spaces:
        lines = [line.strip() for line in lines]
    if remove_empty:
        lines = [line for line in lines if len(line) > 0]

    return lines
