"""field is the main gui constructs.

Field is a tree structure, based on anytree.
One field can represent a simple string and corresponding text input
widget.
One field can also represent a tree root, with various widgets as leaves.
The change in gui will cause change in the value stored in field.
"""

import sys
import os
from collections import OrderedDict
import subprocess

import tkinter as tk
from anytree import Node

# from . import tktools
# from .. import rootconfig
# from ..util import fileop, path
import tktools
from mmdps import rootconfig
from mmdps.util import fileop, path

class ConnectFieldVar:
    """Field and tkvar connector."""
    def __init__(self, field, var):
        """The field and tkvar to be connected use tk trace."""
        self._field = field
        self._var = var
        self._var.set(field.value)
        self._var.trace('w', self.cb_var_change)
        
    def cb_var_change(self, *args):
        """Callback called by tk to set new value in GUI to value in field."""
        self._field.value = self._var.get()

class Field(Node):
    """Base field."""
    def __init__(self, name, value=None, parent=None, **kwargs):
        """Specify name, value and parent. other params will pass to Node."""
        super().__init__(name, parent=parent, value=value, typename=type(self).__name__, **kwargs)

    @classmethod
    def from_dict(cls, d, parent=None):
        """Construct a field from dict."""
        value = d.get('value', None)
        o = cls(d['name'], value, parent=parent)
        return o
    
    def to_dict(self):
        """Serialize the field to a dict."""
        d = OrderedDict()
        d['typename'] = self.typename
        d['name'] = self.name
        d['value'] = self.value
        return d

    def to_config(self):
        """To config."""
        return self.name, self.value
    
class CompositeField(Field):
    """A composite field can contains many children fields.
    
    The composite field can be child itself.
    """
    def __init__(self, name, value=None, parent=None):
        """Init the composite field."""
        super().__init__(name, value, parent)
        
    def build_widget(self, master):
        """Build the field widget. In this case build all children in this composite field."""
        w = tktools.labelframe(master, self.name)
        for field in self.children:
            wc = field.build_widget(w)
            wc.pack(fill='x')
        return w

    @classmethod
    def from_dict(cls, d, parent=None):
        """Construct from dict."""
        value = d.get('value', None)
        o = cls(d['name'], value, parent=parent)
        children = d['children']
        for child in children:
            c = create(child, o)
        return o

    def to_dict(self):
        """Serialize to dict."""
        d = super().to_dict()
        childrenlist = []
        for childo in self.children:
            childd = childo.to_dict()
            childrenlist.append(childd)
        d['children'] = childrenlist
        return d

    def to_config(self):
        """To config."""
        valuedict = OrderedDict()
        for childo in self.children:
            cname, cvalue = childo.to_config()
            valuedict[cname] = cvalue
        return self.name, valuedict
    
class IntField(Field):
    """Int field represents a integer."""
    def __init__(self, name, value, parent=None):
        """Init a int field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the int widget."""
        w, tkvar, frame = tktools.labeled_widget(master, self.name, tktools.entry, vartype=int)
        ConnectFieldVar(self, tkvar)
        return frame

class BoolField(Field):
    """Bool field represents a boolean."""
    def __init__(self, name, value, parent=None):
        """Init bool field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget."""
        w, tkvar, frame = tktools.labeled_widget(master, self.name, tktools.checkbutton)
        ConnectFieldVar(self, tkvar)
        return frame


class FloatField(Field):
    """Float fields represents a float value."""
    def __init__(self, name, value, parent=None):
        """Init the float field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget."""
        w, tkvar, frame = tktools.labeled_widget(master, self.name, tktools.entry, vartype=float)
        ConnectFieldVar(self, tkvar)
        return frame

class StringField(Field):
    """String field represents a string."""
    def __init__(self, name, value, parent=None):
        """Init the string field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget."""
        w, tkvar, frame = tktools.labeled_widget(master, self.name, tktools.entry)
        ConnectFieldVar(self, tkvar)
        return frame

class FolderField(Field):
    """Folder field represents a folder selection."""
    def __init__(self, name, value, parent=None):
        """Init the folder field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget.

        It is composed by entry and select button.
        """
        row = tktools.frame(master)
        label = tktools.label(row, self.name)
        entry, tkvar = tktools.entry(row)
        btn = tktools.button(row, 'Select', self.cb_button_Select)
        ConnectFieldVar(self, tkvar)
        label.pack(side='left')
        btn.pack(side='right')
        entry.pack(side='right')
        self._tkvar = tkvar
        return row
    
    def cb_button_Select(self):
        """Select the folder."""
        resname = tktools.askdirectory()
        if resname:
            self._tkvar.set(resname)

class FileField(Field):
    """File field represents a file selection."""
    def __init__(self, name, value, parent=None):
        """Init the file field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget.

        It is composed by entry and select button.
        """
        row = tktools.frame(master)
        label = tktools.label(row, self.name)
        entry, tkvar = tktools.entry(row)
        btn = tktools.button(row, 'Select', self.cb_button_Select)
        ConnectFieldVar(self, tkvar)
        label.pack(side='left')
        btn.pack(side='right')
        entry.pack(side='right')
        self._tkvar = tkvar
        return row
    
    def cb_button_Select(self):
        """Select the file."""
        resname = tktools.askopenfilename()
        if resname:
            self._tkvar.set(resname)

class FileEditField(Field):
    """File edit field represents a editable file selection."""
    def __init__(self, name, value, parent=None):
        """Init the file edit field."""
        super().__init__(name, value, parent)

    def build_widget(self, master):
        """Build the widget.
        
        It is composed by entry, select button and edit button.
        The edit program used is configured by fileop module.
        """
        row = tktools.frame(master)
        label = tktools.label(row, self.name)
        entry, tkvar = tktools.entry(row)
        btn = tktools.button(row, 'Select', self.cb_button_Select)
        btnedit = tktools.button(row, 'Edit', self.cb_button_Edit)        
        ConnectFieldVar(self, tkvar)
        label.pack(side='left')
        btnedit.pack(side='right')
        btn.pack(side='right')
        entry.pack(side='right')
        self._tkvar = tkvar
        return row

    def cb_button_Select(self):
        """Select the file."""
        resname = tktools.askopenfilename()
        if resname:
            self._tkvar.set(resname)

    def cb_button_Edit(self):
        """Edit the file.

        Use fileop.edit to launch the proper edit program, by file ext and file name.
        """
        filepath = self.value
        fileop.edit(path.fullfile(filepath))

        
class FileJobConfigField(FileEditField):
    """File job config field represents a config file, edited by ui_configjob.py."""
    def __init__(self, name, value, parent=None):
        """Init the file job config field."""
        super().__init__(name, value ,parent)

    def cb_button_Edit(self):
        """Edit with ui_configjob.py."""
        config = self.value
        configeditor = os.path.join(rootconfig.path.tools, 'ui_configjob.py')
        subprocess.Popen([sys.executable, configeditor, config])
        
class ComboboxField(Field):
    """Combobox field represents a combobox selection."""
    def __init__(self, name, value=None, values=None, parent=None):
        """Init the combobox field.
        
        The value is current selection. the values is all possible selections.
        """
        if values is None:
            values = ['A']
        if value is None:
            value = values[0]
        super().__init__(name, value, parent)
        self.values = values

    def build_widget(self, master):
        """Build the combobox widget."""
        w, tkvar, frame = tktools.labeled_widget(master, self.name, tktools.combobox, self.value, self.values)
        ConnectFieldVar(self, tkvar)
        return frame

    @classmethod
    def from_dict(cls, d, parent=None):
        """Override construction method."""
        o = cls(d['name'], d['value'], d['values'], parent=parent)
        return o

    def to_dict(self):
        """Override serialize to dict, because it needs to save values, not only value."""
        d = super().to_dict()
        d['values'] = self.values
        return d

    
# All useable field classes should be registered here.
FieldClasses = [Field, CompositeField, IntField, BoolField, FloatField, StringField,
                FolderField, FileField, FileEditField, ComboboxField, FileJobConfigField]

# field classes, mapped by class name.
FieldClassesDict = {C.__name__: C for C in FieldClasses}

def create(d, parent=None):
    # Create a field, configured by dict.
    typename = d['typename']
    C = FieldClassesDict[typename]
    o = C.from_dict(d, parent)
    return o

def dump(field):
    # Dump field info.
    return field.to_dict()

def load(d):
    # Load a field, configured by dict.
    return create(d)
     
def setbyname(children, name, newvalue):
    # Set value by name in children.
    for child in children:
        if name == child.name:
            child.value = newvalue
            
