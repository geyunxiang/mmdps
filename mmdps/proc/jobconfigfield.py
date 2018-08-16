"""job config and field for configjob GUI.

This is used to construct the GUI used to config job.
The GUI itself is used to config one batch job. The joblist
in this batch job can be of any type.
"""

import os
from collections import OrderedDict
# from ..util.loadsave import load_json_ordered
# from .. import gui
from mmdps.util.loadsave import load_json_ordered
from mmdps import gui

ThisDir = os.path.dirname(os.path.abspath(__file__))

class OneJobConnector(gui.configfield.DefaultSimpleConnector):
    """Connector for one job."""
    JobConfigField = load_json_ordered(os.path.join(ThisDir, 'jobconfigfield.json'))
    def __init__(self):
        """Init the onejob connector."""
        super().__init__(self.JobConfigField)


class JobConfigFieldConnector(gui.configfield.ConfigFieldConnector):
    """Connector for batch job."""
    def __init__(self):
        """Init the connector."""
        super().__init__()
        self.jobconnector = OneJobConnector()
        
    def config_to_field(self, config):
        """Batch job config to field."""
        assert config['typename'] == 'BatchJob'
        jobconfigs = config.get('config')
        rootfield = gui.field.CompositeField('BatchJob')
        childrenfield = []
        for jobconfig in jobconfigs:
            print(jobconfig)
            field = self.jobconnector.config_to_field(jobconfig)
            childrenfield.append(field)
        rootfield.children = childrenfield
        return rootfield

    def default_config(self):
        """Get a default config."""
        rootconfig = OrderedDict()
        rootconfig['name'] = 'Config'
        rootconfig['typename'] = 'BatchJob'
        rootconfig['config'] = [self.jobconnector.field_to_config(None)]
        return rootconfig
    
    def field_to_config(self, field):
        """Field to batchjob config."""
        if field is None:
            return self.default_config()
        rootconfig = OrderedDict()
        rootconfig['name'] = field.name
        rootconfig['typename'] = 'BatchJob'
        rootfield = field
        jobfields = rootfield.children
        jobconfigs = []
        for jobfield in jobfields:
            jobconfig = self.jobconnector.field_to_config(jobfield)
            jobconfigs.append(jobconfig)
        rootconfig['config'] = jobconfigs
        return rootconfig
    
