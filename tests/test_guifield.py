import tkinter as tk
from collections import OrderedDict
from anytree import RenderTree
from anytree.exporter import DictExporter, JsonExporter


from mmdps.gui import field, guifield

def print_tree(node):
    renderer = RenderTree(node)
    print(renderer)
    
if __name__ == '__main__':
    comp = field.CompositeField('TheComp')
    inta = field.IntField('a', 10, comp)
    intb = field.IntField('b', 20, comp)
    boolc = field.BoolField('c', True, comp)
    boold = field.BoolField('d', False, comp)
    floate = field.FloatField('e', 3.14, comp)
    compchild = field.CompositeField('ChildComp', None, comp)
    folder = field.FolderField('fo', '', compchild)
    file = field.FileField('fi', '', compchild)
    strg = field.StringField('g', 'abc', compchild)
    comboh = field.ComboboxField('h', 'T1', ['T1', 'T2', 'BOLD', 'DWI'], comp)
    
    

    exporter = DictExporter(dictcls=OrderedDict)
    print(exporter.export(comp))
    
    exporterj = JsonExporter()
    print(exporterj.export(comp))

    print_tree(comp)

    root = tk.Tk()
    w = comp.build_widget(root)
    w.pack(fill='x')

    
    
