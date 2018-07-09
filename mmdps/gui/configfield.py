"""config and field.

Field is the whole primitive gui elements and associated data.
Config is the human more readable config dict.
This module ease their interchange.
"""

from collections import OrderedDict
from .. import gui


class ConfigFieldConnector:
    """Base class for config and field interchange.
    
    You can provide your own implementation.
    """
    def __init__(self):
        pass

    def config_to_field(self, config):
        """convert config to field."""
        pass

    def field_to_config(self, field):
        """convert field to config."""
        pass
    
def find_by_name(children, name):
    """find child in children by name."""
    for child in children:
        if child.name == name:
            return child
    return None

class DefaultSimpleConnector(ConfigFieldConnector):
    """The default config field connector.
    
    Configured use a initdict. 
    """
    def __init__(self, initdict):
        """Use initdict to configure the connector. See builtin ui for example."""
        super().__init__()
        self.initdict = initdict

    def default_config(self):
        """return default config."""
        rootfield = gui.field.load(self.initdict)
        return self.field_to_config(rootfield)
    
    def config_to_field(self, config):
        """overrided config to field."""
        rootfield = gui.field.load(self.initdict)
        children = rootfield.children
        for name in config:
            child = find_by_name(children, name)
            if child is None:
                raise Exception('{} not exist in children'.format(name))
            child.value = config[name]
        return rootfield

    def field_to_config(self, field):
        """overrided field to config."""
        if field is None:
            return self.default_config()
        children = field.children
        config = OrderedDict()
        for child in children:
            config[child.name] = child.value
        return config
    
    
