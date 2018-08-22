import os
import sys
import subprocess
import tkinter as tk
from mmdps.gui import guiframe, tktools
from mmdps.util.loadsave import load_json
from mmdps.util import toolman

class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)

    def setup(self, toolsmanager):
        self.toolsmanager = toolsmanager
        self.build_widgets()

    def build_widgets(self):
        tools = self.toolsmanager.tools
        for tool in tools:
            w = tool.build_widget(self.mainframe)
            w.pack(fill='x', expand=True)



if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)

    manager = toolman.get_default_manager()
    
    app.setup(manager)
    app.pack(fill='both', expand=True)
    root.title('MMDPS Main')
    root.mainloop()
    
