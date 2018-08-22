import os
import tkinter as tk
from mmdps.gui import guiframe, tktools, field
from mmdps import rootconfig
from mmdps.util import run


class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)
        self.build_actions()
        self.build_widgets()
        
    def build_actions(self):
        pass

    def build_widgets(self):
        d = {'typename': 'FileEditField', 'name': 'MRIScansTxt', 'value': ''}
        self.fmriscanstxt = field.create(d)
        d = {'typename': 'BoolField', 'name': 'ConvertDicom', 'value': True}
        self.fconvertdicom = field.create(d)
        wmriscanstxt = self.fmriscanstxt.build_widget(self.mainframe)
        wconvertdicom = self.fconvertdicom.build_widget(self.mainframe)
        wrun = tktools.button(self.mainframe, 'Run', self.cb_run)
        wmriscanstxt.pack()
        wconvertdicom.pack()
        wrun.pack()
        
    def cb_run(self):
        txt = self.fmriscanstxt.value
        b = self.fconvertdicom.value
        bs = 'True' if b else 'False'
        py = os.path.join(rootconfig.path.tools, 'import_changgung.py')
        cmdlist = [py, '--mriscanstxt', txt, '--bconvert', bs]
        r = run.call_py(cmdlist, True)
        print(r)
        
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    app.pack(fill='both', expand=True)
    root.title('MMDPS Data Import')
    root.mainloop()
    
