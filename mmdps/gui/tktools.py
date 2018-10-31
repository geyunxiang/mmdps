"""tkinter tools

A wrapper for tk tools.
Use this wheneven possible.
"""

import tkinter as tk
import tkinter.filedialog

# value tyep to tkvar mapping
VarTypeMap = {str: tk.StringVar, int: tk.IntVar, bool: tk.BooleanVar, float: tk.DoubleVar}

def button(master, text, command):
    """Create a tk button."""
    w = tk.Button(master, text=text, command=command)
    return w

def label(master, text):
    """Create a tk label."""
    w = tk.Label(master, text=text)
    return w

def entry(master, vartype=str, **kw):
    """Create a tk entry."""
    tkvar = VarTypeMap[vartype]()
    w = tk.Entry(master, textvariable=tkvar, **kw)
    return w, tkvar

def checkbutton(master):
    """Create a tk check button."""
    tkvar = tk.BooleanVar()
    w = tk.Checkbutton(master, variable=tkvar)
    return w, tkvar

def combobox(master, value, values):
    """Create a tk combobox."""
    tkvar = tk.StringVar()
    tkvar.set(value)
    w = tk.OptionMenu(master, tkvar, *values)
    return w, tkvar

def listbox(master, command_select, command_popup):
    """Create a tk listbox.

    You should provide the commands to be called when list item is selected,
    or right clicked.
    """
    frame = tk.Frame(master)
    scrollbar = tk.Scrollbar(frame, orient='vertical')
    w = tk.Listbox(frame, yscrollcommand=scrollbar.set)
    w.bind('<Double-Button-1>', command_select)
    w.bind('<Return>', command_select)
    w.bind('<Button-3>', command_popup)
    scrollbar.config(command=w.yview)
    scrollbar.pack(side='right', fill='y')
    w.pack(side='left', fill='both', expand=True)
    return w, None, frame

def frame(master):
    """Create an empty tk frame."""
    w = tk.Frame(master)
    return w

def labelframe(master, text):
    """Create a labeled tk frame."""
    w = tk.LabelFrame(master, text=text, borderwidth=5)
    return w

def labeled_widget(master, labeltext, widgetclass, *args, **kwargs):
    """Create a labeled widget.
    
    The widgetclass is the widget creating functions in this module.
    The args and kwargs are passed to the widgetclass init.
    Return the actual widget, the associated tkvar, and the parent frame.
    You should pack the parent frame, not the w, the w is already packed in the frame.
    """
    frame = tk.Frame(master)
    l = label(frame, labeltext)
    l.pack(side='left')
    ret = widgetclass(frame, *args, **kwargs)
    if type(ret) == tuple:
        if len(ret) == 2:
            w, tkvar, subframe = ret[0], ret[1], ret[0]
        else:
            w, tkvar, subframe = ret[0], ret[1], ret[2]
    else:
        w, tkvar, subframe = ret[0], None, ret[0]
    subframe.pack(side='right')
    return w, tkvar, frame

def askdirectory():
    """Ask a directory."""
    return tk.filedialog.askdirectory()

def askopenfilename():
    """Ask a open filename."""
    return tk.filedialog.askopenfilename()

def asksaveasfilename():
    """Ask a save as filename."""
    return tk.filedialog.asksaveasfilename()
