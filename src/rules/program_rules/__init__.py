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
from . import S2R008
from . import S2R009
from . import S2R012
from . import S2R013
from . import S2R014
from . import S2R016
from . import S2R017
from . import S2R018
from . import S2R019
from . import S2R021
from . import S2R022
from . import S2R023
from . import S2R024
from . import S2R026
from . import S2R027
from . import S2R028
from . import S2R029
from . import S2R030
from . import S2R031
from . import S2R032
from . import S2R033
from . import S2R034
from . import S2R035
from . import S2R036
from . import S2R038
from . import S2R039
from . import S2R040
from . import S2R043
from . import S2R045
from . import S2R046
from . import S2R047
from . import S2R053
from . import S2R054
from . import S2R055
from . import S2R056

# Add imports for any new rule modules here as they are created