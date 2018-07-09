"""Parallel config field connector.

This connector use the default simple connector.
The config is in paraconfigfield.json.
"""

import os
from collections import OrderedDict
from ..util.loadsave import load_json_ordered
from .. import gui

ThisDir = os.path.dirname(os.path.abspath(__file__))

class ParaConfigFieldConnector(gui.configfield.DefaultSimpleConnector):
    """Parallel config field connector, for configpara in GUI."""
    # the config field dict
    ParaConfigField = load_json_ordered(os.path.join(ThisDir, 'paraconfigfield.json'))
    
    def __init__(self):
        """Init the connector using config dict."""
        super().__init__(self.ParaConfigField)

    
