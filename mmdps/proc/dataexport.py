"""Export all features to feature database.

Use this exporter to export features from where calculated to feature database.
"""


import os
import shutil

from mmdps.proc import atlas
from mmdps.util.loadsave import load_json_ordered, save_json_ordered, load_txt, save_txt
from mmdps.util import path




class MRIScanProcMRIScanAtlasExporter:
    """The feature exporter for mriscan processing.
    
    Only export for one mriscan and one atlas.
    """
    def __init__(self, mriscan, atlasname, mainconfig, dataconfig):
        """Init the exporter."""
        self.mriscan = mriscan
        self.atlasname = atlasname
        self.mainconfig = mainconfig
        self.dataconfig = dataconfig
        self.outputrootfolder = self.mainconfig['outputfolder']
        self.inputfolders = self.mainconfig['inputfolders']
        
    def fullinfolder(self, modal, *p):
        """full file for input folder."""
        if self.atlasname:
            return os.path.join(self.inputfolders[modal], self.mriscan, self.atlasname, *p)
        else:
            return os.path.join(self.inputfolders[modal], self.mriscan, *p)

    def fulloutfolder(self, *p):
        """full file for output folder."""
        if self.atlasname:
            return os.path.join(self.outputrootfolder, self.mriscan, self.atlasname, *p)
        else:
            return os.path.join(self.outputrootfolder, self.mriscan, *p)
        
    def run_feature(self, featurename, featureconfig):
        """Export one feature."""
        modal = featureconfig['modal']
        files = featureconfig.get('files')
        if files is None:
            files = [featureconfig.get('file')]
        for file in files:
            filesrc = self.fullinfolder(modal, file)
            if not os.path.isfile(filesrc):
                print('==Not Exist:', filesrc)
                continue
            name, ext = path.splitext(filesrc)
            filedst = self.fulloutfolder(featurename + ext)
            path.makedirs_file(filedst)
            #print('Copy:', filesrc, filedst)
            shutil.copy2(filesrc, filedst)
            
    def run(self):
        """Export all features."""
        if self.atlasname:
            # atlased
            for netname, netconf in self.dataconfig['nets'].items():
                self.run_feature(netname, netconf)
            for attrname, attrconf in self.dataconfig['attrs'].items():
                self.run_feature(attrname, attrconf)
        else:
            # unatlased
            for filename, fileconf in self.dataconfig['unatlased'].items():
                self.run_feature(filename, fileconf)
        
class MRIScanProcExporter:
    """The feature exporter.

    Export features in all mriscans.
    """
    def __init__(self, mainconfig, dataconfig):
        """Init the exporter using mainconfig and dataconfig."""
        self.mainconfig = mainconfig
        self.dataconfig = dataconfig
        self.atlases = load_txt(mainconfig['atlaslist'])
        self.mriscans = load_txt(mainconfig['scanslist'])

    def run_mriscan_atlas(self, mriscan, atlasname):
        """Run one mriscan and one atlas to export."""
        atlas_exporter = MRIScanProcMRIScanAtlasExporter(mriscan, atlasname, self.mainconfig, self.dataconfig)
        atlas_exporter.run()        
        
    def run(self):
        """Run the export."""
        for atlasname in self.atlases:
            # atlased
            for mriscan in self.mriscans:
                self.run_mriscan_atlas(mriscan, atlasname)
        if 'unatlased' in self.dataconfig:
            # unatlased
            for mriscan in self.mriscans:
                self.run_mriscan_atlas(mriscan, None)

def create_by_files(mainconfigfile, dataconfigfile):
    """Create exporter by config files."""
    mainconfig = load_json_ordered(mainconfigfile)
    dataconfig = load_json_ordered(dataconfigfile)
    return MRIScanProcExporter(mainconfig, dataconfig)

def create_by_folder(atlasobj, configsfolder):
    """Create exporter by folder, which should includes the config files."""
    mainconfigfile = os.path.join(configsfolder, 'export_mainconf.json')
    dataconfigfile = os.path.join(configsfolder, 'export_dataconf.json')
    return create_by_files(mainconfigfile, dataconfigfile)
    
    
