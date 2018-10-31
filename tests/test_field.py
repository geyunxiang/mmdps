import json

from collections import OrderedDict
from anytree import RenderTree
from anytree.exporter import DictExporter, JsonExporter


from mmdps.gui import field

def export(rootfield):
    return rootfield.to_dict()

def import_(d):
    return field.create(d)
    
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
    
    renderer = RenderTree(comp)
    print(renderer)
    print(renderer.by_attr('value'))

    exporter = DictExporter(dictcls=OrderedDict)
    print(exporter.export(comp))
    
    exporterj = JsonExporter()
    jstr = exporterj.export(comp)
    
##    d = json.loads(jstr)
##    importer = field.FieldImporter()
##    comp2 = importer.import_(d)
##    print(RenderTree(comp2)) 

    print('=====')
    
    d = field.dump(comp)
    print(d)
    comp2 = field.load(d)
    renderer2 = RenderTree(comp2)
    print(renderer2)
    
