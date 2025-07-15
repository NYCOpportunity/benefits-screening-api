"""
Import all rule modules to ensure they register themselves with the registry.

This module automatically imports all rule modules so their @register_rule
decorators execute and the rules get added to the registry.
"""

# Import all rule modules here so their @register_rule decorators execute
from . import example_rule

# Add imports for any new rule modules here as they are created
# from . import snap_rule
# from . import medicaid_rule
# etc.