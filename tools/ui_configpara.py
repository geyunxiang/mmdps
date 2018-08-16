import os
import tkinter as tk
from mmdps.gui import guiframe, tktools
from mmdps.proc import paraconfigfield
from mmdps.util.loadsave import load_json_ordered, save_json_ordered

class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)
        self.build_actions()

    def setup(self, connector):
        self.connector = connector

    def open_configfile(self, configfile):
        if not os.path.isfile(configfile):
            print('cannot open file {}'.format(configfile))
            return
        configdict = load_json_ordered(configfile)
        self.rootfield = self.connector.config_to_field(configdict)
        self.mainfieldwidget = self.rootfield.build_widget(self.mainframe)
        self.set_mainwidget(self.mainfieldwidget)
        self.mainfieldwidget.pack()
        
    def build_actions(self):
        self.add_action('Open', self.cb_menu_Open)
        self.add_action('Save', self.cb_menu_Save)
        self.add_action('Dump', self.cb_menu_Dump)

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
    
def main(configfile=None):
    root = tk.Tk()
    app = Application(root)
    connector = paraconfigfield.ParaConfigFieldConnector()
    app.setup(connector)
    if configfile:
        app.open_configfile(configfile)
    app.pack(fill='both', expand=True)
    root.title('MMDPS ConfigPara')
    root.mainloop()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        main()
    else:
        configfile = sys.argv[1]
        main(configfile)
        
    