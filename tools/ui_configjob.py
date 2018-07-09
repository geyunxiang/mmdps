import os
import tkinter as tk
from mmdps.gui import guiframe, tktools
from mmdps.proc import jobconfigfield
from mmdps.util.loadsave import load_json_ordered, save_json_ordered

class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)
        self.build_actions()
        
    def setup(self, connector):
        self.connector = connector
        self.rootfield = None
        
    def load_configdict(self, configdict):
        self.rootfield = self.connector.config_to_field(configdict)
        self.mainfieldwidget = self.rootfield.build_widget(self.mainframe)
        self.set_mainwidget(self.mainfieldwidget)
        self.mainfieldwidget.pack()
        
    def open_configfile(self, configfile):
        if not os.path.isfile(configfile):
            print('cannot open file {}'.format(configfile))
            return
        configdict = load_json_ordered(configfile)
        self.load_configdict(configdict)
        
    def build_actions(self):
        self.add_action('Open', self.cb_menu_Open)
        self.add_action('Save', self.cb_menu_Save)
        self.add_action('Dump', self.cb_menu_Dump)
        self.add_action('Add', self.cb_menu_Add)
        self.add_action('Remove', self.cb_menu_Remove)
        
    def cb_menu_Open(self):
        resname = tktools.askopenfilename()
        if resname:
            self.open_configfile(resname)

    def cb_menu_Save(self):
        resname = tktools.asksaveasfilename()
        if resname:
            d = self.connector.field_to_config(self.rootfield)
            save_json_ordered(resname, d)
            print('Saved to {}'.format(resname))
    
    def cb_menu_Dump(self):
        d = self.connector.field_to_config(self.rootfield)
        print(d)

    def cb_menu_Add(self):
        if self.rootfield is None:
            d = self.connector.field_to_config(None)
            print(d)
        else:
            d = self.connector.field_to_config(self.rootfield)
            if len(d['config']) == 0:
                d = self.connector.field_to_config(None)
            else:
                lastone = d['config'][-1]
                d['config'].append(lastone.copy())
        self.load_configdict(d)

    def cb_menu_Remove(self):
        d = self.connector.field_to_config(self.rootfield)
        if len(d['config']) > 0:
            del d['config'][-1]
            self.load_configdict(d)
        
def main(configfile=None):
    root = tk.Tk()
    app = Application(root)
    connector = jobconfigfield.JobConfigFieldConnector()
    app.setup(connector)
    if configfile:
        app.open_configfile(configfile)
    app.pack(fill='both', expand=True)
    root.title('MMDPS ConfigJob')
    root.mainloop()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        main()
    else:
        configfile = sys.argv[1]
        main(configfile)
        
    
