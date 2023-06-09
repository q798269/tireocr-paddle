# SPDX-License-Identifier: Apache-2.0

import importlib
import inspect
import sys
import pkgutil
from typing import Dict, Text
from types import ModuleType


def collect_sample_implementations() -> Dict[Text, Text]:
    dict: Dict[Text, Text] = {}
    _recursive_scan(sys.modules[__name__], dict)
    return dict


def _recursive_scan(package: ModuleType, dict: Dict[Text, Text]) -> None:
    pkg_dir = package.__path__  # type: ignore
    module_location = package.__name__
    for _module_loader, name, ispkg in pkgutil.iter_modules(pkg_dir):  # type: ignore
        module_name = "{}.{}".format(module_location, name)  # Module/package
        module = importlib.import_module(module_name)
        dict[name] = inspect.getsource(module)
        if ispkg:
            _recursive_scan(module, dict)
