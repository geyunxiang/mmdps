import tkinter as tk

from mmdps.proc import job
from mmdps.util.loadsave import load_json_ordered, save_json_ordered
from mmdps import gui

class JobConfigField:
    ConfigField = load_json_ordered('jobconfigfield.json')
    def __init__(self):
        pass

    def config_to_field(self, config):
        field = gui.field.load(self.ConfigField)
        children = field.children
        children[0].value = config['typename']
        children[1].value = config.get('cmd', '')
        jobconfig = config.get('config', '')
        if type(jobconfig) is str:
            children[2].value = jobconfig
        else:
            children[2] = gui.field.CompositeField('batch')
            for batchconfig in jobconfig:
                curfield = self.config_to_field(batchconfig)
                curfield.parent = children[2]
        children[3].value = config.get('argv', [])
        children[4].value = config.get('wd', '.')
        return field
    
    def field_to_config(self, field):
        pass
    
class BatchJobConfigField:
    JobConfigField = load_json_ordered('jobconfigfield.json')
    def __init__(self):
        pass

    def config_to_field(self, config):
        assert config['typename'] == 'BatchJob'
        jobconfigs = config.get('config')
        rootfield = gui.field.CompositeField('Batch')
        for jobconfig in jobconfigs:
            field = gui.field.create(self.JobConfigField, rootfield)
            field.name = jobconfig['name']
            children = field.children
            children[0].value = jobconfig['typename']
            children[1].value = jobconfig.get('cmd', '')
            subconfig = jobconfig.get('config', '')
            print(subconfig)
            if type(subconfig) is not str:
                raise Exception('Nested BatchJob GUI not supported')
            children[2].value = subconfig
            children[3].value = jobconfig.get('argv', [])
            children[4].value = jobconfig.get('wd', '.')
        return rootfield
    
if __name__ == '__main__':
    connector = BatchJobConfigField()
    #jobconfigfile = 'config_job.json'
    jobconfigfile = 'config_alljob.json'
    
    config = load_json_ordered(jobconfigfile)
    field = connector.config_to_field(config)
    # modify field
    root = tk.Tk()
    w = field.build_widget(root)
    w.pack()
    
    configout = connector.field_to_config(field)
    
