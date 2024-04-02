"""add_parent_path - """

__version__ = '0.1.11'
__author__ = 'fx-kirin <fx.kirin@gmail.com>'
__all__ = ['add_parent_path']

import sys
import inspect
from pathlib import Path


def add_parent_path(count=1, child_path=None, insert_to_front: bool = True):
    caller_file_path = Path(inspect.stack()[1][1]).absolute()
    import_file_path = caller_file_path.parents[count]
    if isinstance(child_path, str):
        child_path = Path(child_path)

    if child_path:
        import_file_path = import_file_path / child_path

    import_file_path = str(import_file_path)
    return add_sys_path_temporarily(import_file_path, insert_to_front)


def add_sys_path_temporarily(import_file_path, insert_to_front: bool = True):
    if import_file_path not in sys.path:
        if insert_to_front:
            sys.path.insert(0, import_file_path)
        else:
            sys.path.append(import_file_path)
        return AddParentPath(import_file_path, True)
    else:
        return AddParentPath(import_file_path, False)


class AddParentPath(object):
    def __init__(self, import_file_path, is_imported):
        self.import_file_path = import_file_path
        self.is_imported = is_imported

    def __enter__(self):
        pass

    def __exit__(self, ex_type, ex_value, trace):
        if self.is_imported:
            if self.import_file_path in sys.path:
                sys.path.remove(self.import_file_path)