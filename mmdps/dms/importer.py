"""Importer to import new data to database.

Copy raw nifti files to database and rename to proper file name.
Update database.
"""

import os
import shutil
from . import converter, exporter
from ..util.loadsave import load_txt
from ..util import path


class MRIScanImporter:
    """MRIScan importer."""
    def __init__(self, inmainfolder, outmainfolder, mriscanstxt, db=None, cls_niftigetter=converter.NiftiGetter):
        """Import from inmainfolder to outmainfolder, for mriscans from mriscanstxt.
        update database db. Use NiftiGetter class from cls_niftigetter.
        """
        self.inmainfolder = inmainfolder
        self.outmainfolder = outmainfolder
        self.mriscans = load_txt(mriscanstxt)
        self.db = db
        self.cls_niftigetter = cls_niftigetter

    def copy_nifti_one_modal(self, outfolder, getfunc, newname):
        """Copy one modal."""
        path_Modal = getfunc()
        if path_Modal is None:
            return
        if type(path_Modal) == str:
            shutil.copy2(path_Modal, os.path.join(outfolder, newname))
        else:
            for curfile in path_Modal:
                if curfile[-7:] == '.nii.gz':
                    curnewname = newname + '.nii.gz'
                else:
                    _, ext = os.path.splitext(curfile)
                    curnewname = newname + ext
                shutil.copy2(curfile, os.path.join(outfolder, curnewname))
                
    def copy_nifti_one(self, mriscan):
        """Copy all modals for one mriscan."""
        infolder = os.path.join(self.inmainfolder, mriscan)
        outfolder = os.path.join(self.outmainfolder, mriscan)
        path.makedirs(outfolder)
        niftigetter = self.cls_niftigetter(infolder)
        self.copy_nifti_one_modal(outfolder, niftigetter.get_T1, 'T1.nii.gz')
        self.copy_nifti_one_modal(outfolder, niftigetter.get_T2, 'T2.nii.gz')
        self.copy_nifti_one_modal(outfolder, niftigetter.get_BOLD, 'BOLD.nii.gz')
        self.copy_nifti_one_modal(outfolder, niftigetter.get_DWI, 'DWI')
        self.copy_nifti_one_modal(outfolder, niftigetter.get_ScanInfo, 'scan_info.json')
		
    def copy_nifti(self):
        """Copy all modals for all mriscans."""
        for mriscan in self.mriscans:
            self.copy_nifti_one(mriscan)

    def update_db(self):
        """Update database
        TODO: better not use simple re-generate.
        """
        exp = exporter.MRIScanTableExporter(self.outmainfolder, self.db.mritablecsv)
        exp.run()
        self.db.run()
    
    def run(self):
        """Run. Copy nifti files and update database."""
        self.copy_nifti()
        self.update_db()
        
