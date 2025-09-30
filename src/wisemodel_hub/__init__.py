import importlib
import logging
import os
import sys
from typing import TYPE_CHECKING


__version__ = "v0.4.2"

# 配置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# WARNING: any comment added in this dictionary definition will be lost when
# re-generating the file !
_SUBMOD_ATTRS = {
    "auth": [
        "get_local_token",
        "login",
        "notebook_login",
    ],
    "downloader": [
        "download_with_git",
        "file_download",
        "lfs_file_download",
        "snapshot_download",
    ],
    "uploader": [
        "push_to_hub",
        "upload_file",
        "upload_with_git",
    ],
}


def _attach(package_name, submodules=None, submod_attrs=None):
    """Attach lazily loaded submodules, functions, or other attributes.

    Typically, modules import submodules and attributes as follows:

    ```py
    import mysubmodule
    import anothersubmodule

    from .foo import someattr
    ```

    The idea is to replace a package's `__getattr__`, `__dir__`, and
    `__all__`, such that all imports work exactly the way they would
    with normal imports, except that the import occurs upon first use.

    The typical way to call this function, replacing the above imports, is:

    ```python
    __getattr__, __dir__, __all__ = lazy.attach(
        __name__,
        ['mysubmodule', 'anothersubmodule'],
        {'foo': ['someattr']}
    )
    ```
    This functionality requires Python 3.7 or higher.

    Args:
        package_name (`str`):
            Typically use `__name__`.
        submodules (`set`):
            List of submodules to attach.
        submod_attrs (`dict`):
            Dictionary of submodule -> list of attributes / functions.
            These attributes are imported as they are used.

    Returns:
        __getattr__, __dir__, __all__

    """
    if submod_attrs is None:
        submod_attrs = {}

    if submodules is None:
        submodules = set()
    else:
        submodules = set(submodules)

    attr_to_modules = {attr: mod for mod, attrs in submod_attrs.items() for attr in attrs}

    __all__ = list(submodules | attr_to_modules.keys())

    def __getattr__(name):
        if name in submodules:
            try:
                return importlib.import_module(f"{package_name}.{name}")
            except Exception as e:
                print(f"Error importing {package_name}.{name}: {e}")
                raise
        elif name in attr_to_modules:
            submod_path = f"{package_name}.{attr_to_modules[name]}"
            try:
                submod = importlib.import_module(submod_path)
            except Exception as e:
                print(f"Error importing {submod_path}: {e}")
                raise
            attr = getattr(submod, name)

            # If the attribute lives in a file (module) with the same
            # name as the attribute, ensure that the attribute and *not*
            # the module is accessible on the package.
            if name == attr_to_modules[name]:
                pkg = sys.modules[package_name]
                pkg.__dict__[name] = attr

            return attr
        else:
            raise AttributeError(f"No {package_name} attribute {name}")

    def __dir__():
        return __all__

    return __getattr__, __dir__, list(__all__)


__getattr__, __dir__, __all__ = _attach(__name__, submodules=[], submod_attrs=_SUBMOD_ATTRS)

if os.environ.get("EAGER_IMPORT", ""):
    for attr in __all__:
        __getattr__(attr)

# WARNING: any content below this statement is generated automatically. Any manual edit
# will be lost when re-generating this file !
#
# To update the static imports, please run the following command and commit the changes.
# ```
# # Use script
# python utils/check_static_imports.py --update-file
#
# # Or run style on codebase
# make style
# ```
if TYPE_CHECKING:  # pragma: no cover
    from .auth import (
        get_local_token,  # noqa: F401
        login,  # noqa: F401
        notebook_login,  # noqa: F401
    )
    from .downloader import (
        download_with_git,  # noqa: F401
        file_download,  # noqa: F401
        lfs_file_download,  # noqa: F401
        snapshot_download,  # noqa: F401
    )
    from .uploader import (
        push_to_hub,  # noqa: F401
        upload_file,  # noqa: F401
        upload_with_git,  # noqa: F401
    )
