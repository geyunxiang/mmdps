"""GUI main frame.

This serves as the basic GUI main window.
The window can be scrolled or unscrolled.
You can add action directly to the toolbar.
"""

import tkinter as tk
# from . import tktools
import tktools

class MainWindow(tk.Frame):
    """The main window."""
    def __init__(self, master=None, scrolled=True, **kw):
        """Init the main window.
        
        Set scrolled to False if don't want the main widget to scroll.
        """
        tk.Frame.__init__(self, master, **kw)
        self.create_toolbar()
        if scrolled:
            self.create_scrolledmain()
        else:
            self.create_unscrolledmain()
        self._mainwidget = None

    def add_action(self, name, action):
        """Add an action to the toolbar."""
        w = tktools.button(self._toolbar, name, action)
        w.pack(side='left', padx=2, pady=2)

    def set_mainwidget(self, widget):
        """Set (replace) the main widget.
        
        You don't want to use this.
        """
        if self._mainwidget:
            self._mainwidget.destroy()
        self._mainwidget = widget
        self._mainwidget.pack(side='top', fill='both', expand=True)

    def create_toolbar(self):
        """Create the toolbar."""
        self._toolbar = tk.Frame(self.master, bd=1, relief='raised')
        self._toolbar.pack(side='top', fill='x')

    def create_scrolledmain(self):
        """Create scrolled main window."""
        self._canvas = tk.Canvas(self)
        self._mainframe = tk.Frame(self._canvas)
        self._vertscrollbar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vertscrollbar.set)
        self._vertscrollbar.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)
        self._canvas.create_window((0, 0), window=self._mainframe, anchor='nw', tags='self._mainframe')
        self._mainframe.bind('<Configure>', self.on_frame_configure)

    def create_unscrolledmain(self):
        """Create unscrolled main window."""
        self._mainframe = tk.Frame(self)
        self._mainframe.pack(fill='both', expand='True')

    def on_frame_configure(self, event):
        """Callback for resize."""
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    @property
    def mainframe(self):
        """The mainframe. Be sure to use this as master when adding your own widgets.

        You must use this as the master widget when adding your own widgets.
        """
        return self._mainframe
    
