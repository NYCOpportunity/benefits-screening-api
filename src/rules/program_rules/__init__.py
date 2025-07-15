"""
Import all rule modules to ensure they register themselves with the registry.

This module automatically imports all rule modules so their @register_rule
decorators execute and the rules get added to the registry.
"""

# Import all rule modules here so their @register_rule decorators execute
from . import example_rule
from . import S2R001
from . import S2R003
from . import S2R004
from . import S2R005
from . import S2R006
from . import S2R007
from . import S2R010
from . import S2R011
from . import S2R015
from . import S2R025
from . import S2R037
from . import S2R085

# Add imports for any new rule modules here as they are created