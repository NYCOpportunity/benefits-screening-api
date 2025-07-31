"""Dynamic module importer for the *rules* package.

When the `rules` package is imported, this code automatically imports all
sub-modules (except those starting with an underscore) so that any rule classes
contained therein can register themselves with the central registry.

"""

from importlib import import_module
from pkgutil import walk_packages

# Recursively import every sub-module in the *rules* package so that any
# `@register_rule` decorators execute and add their rule classes to the
# central registry.  Modules whose *leaf* name starts with an underscore are
# considered private and are skipped.

for module_info in walk_packages(__path__, prefix=f"{__name__}."):
    full_name = module_info.name
    # Excludes `__init__.py`.
    leaf = full_name.rpartition(".")[-1]
    if leaf.startswith("_"):
        continue

    import_module(full_name)
