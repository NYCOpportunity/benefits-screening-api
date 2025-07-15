"""Dynamic module importer for the *rules* package.

When the `rules` package is imported, this code automatically imports all
sub-modules (except those starting with an underscore) so that any rule classes
contained therein can register themselves with the central registry.

Developers can add new rule modules (e.g. `snap_rule.py`, `wic_rule.py`), and
as long as they reside in this package they will be imported and therefore
registered at runtime.
"""

from importlib import import_module
from pkgutil import iter_modules

# Import every sub-module in this package.  This triggers their module-level
# registration code (see `registry.register_rule`).
for module_info in iter_modules(__path__):
    name = module_info.name
    if not name.startswith("_"):
        import_module(f"{__name__}.{name}")
