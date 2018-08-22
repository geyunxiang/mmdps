import os
import tkinter as tk
from mmdps.gui import guiframe, tktools, field
from mmdps.util.loadsave import load_json_ordered, save_json_ordered
from mmdps.proc import para


class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)
        self.build_actions()
        self.build_widgets()
        
    def build_actions(self):
        pass

    def build_widgets(self):
        d = {'typename': 'FileEditField', 'name': 'ParaConfig', 'value': ''}
        self.fpara = field.create(d)
        d = {'typename': 'StringField', 'name': 'ProjectPathVar', 'value': '.'}
        self.fpath = field.create(d)
        wpara = self.fpara.build_widget(self.mainframe)
        wpath = self.fpath.build_widget(self.mainframe)
        wrun = tktools.button(self.mainframe, 'Run', self.cb_run)
        wpara.pack()
        wpath.pack()
        wrun.pack()
        
    def cb_run(self):
        paraconf = self.fpara.value
        pathconf = self.fpath.value
        os.environ['MMDPS_PROJECTPATH'] = pathconf
        j = para.load(load_json_ordered(paraconf))
        j.run()
        
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    app.pack(fill='both', expand=True)
    root.title('MMDPS RunPara')
    root.mainloop()
    
