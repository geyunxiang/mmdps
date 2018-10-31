import os
import sys
import argparse
import logging
from mmdps.dms import converter, importer, dbgen
from mmdps.util.loadsave import load_txt
from mmdps import rootconfig
from mmdps.util import clock

logging.basicConfig(filename='import_changgung.log', level=logging.DEBUG)
logging.info('New Run: {}'.format(clock.now()))

class ChanggungNiftiGetter(converter.NiftiGetter):
    def __init__(self, niftifolder):
        super().__init__(niftifolder)

    def get_T1(self):
        return self.fnmatch_one('*OSag_3D_T1BRAVO*.nii.gz')

    def get_T2(self):
        return self.fnmatch_one('*OAx_T2_PROPELLER*.nii.gz')

    def get_BOLD(self):
        return self.fnmatch_one('*BOLD-rest*.nii.gz')

    def get_DWI(self):
        nii = self.fnmatch_one('*DTI_24_Directions*.nii.gz')
        bval = self.fnmatch_one('*DTI_24_Directions*.bval')
        bvec = self.fnmatch_one('*DTI_24_Directions*.bvec')
        dwifiles = (nii, bval, bvec)
        if all(dwifiles):
            return dwifiles
        else:
            return None
    
def apppath(s):
    return os.path.join(WORKING_FOLDER, s)

class ChanggungConverter:
    def __init__(self, dcmmainfolder, niftimainfolder, mriscantxt):
        self.dcmmainfolder = dcmmainfolder
        self.niftimainfolder = niftimainfolder
        self.mriscans = load_txt(mriscantxt)

    def convert_mriscan(self, mriscan):
        dcmfolder = os.path.join(self.dcmmainfolder, mriscan)
        niftifolder = os.path.join(self.niftimainfolder, mriscan)
        ret = converter.convert_dicom_to_nifti(dcmfolder, niftifolder)
        return ret
        
    def run(self):
        for mriscan in self.mriscans:
            ret = self.convert_mriscan(mriscan)
            if ret == 0:
                logging.info('{} convert completed'.format(mriscan))
            else:
                logging.warning('{} convert failed, {}'.format(mriscan, ret))
            
if __name__ == '__main__':
    print('...')
    parser = argparse.ArgumentParser()
    parser.add_argument('--mriscanstxt', help='a txt file contain mriscan folder names.', required=True, default='')
    parser.add_argument('--bconvert', help='convert dicom to rawnii or not', default='True')
    args = parser.parse_args()

    mriscanstxt = args.mriscanstxt
    
    if args.mriscanstxt == '':
        # change this if with out arguments
        mriscanstxt = r'F:\MMDPDatabase\new_data_dicom\changgeng_20180430.txt'
        
    # do dcm2nii or not
    bconvert = args.bconvert == 'True'

    print(mriscanstxt, bconvert)


    # Working folder
    WORKING_FOLDER = rootconfig.dms.folder_working
    # DICOM main folder
    indcmmainfolder = rootconfig.dms.folder_dicom
    # Raw NIfTI main folder
    inoutniftimainfolder = rootconfig.dms.folder_rawnii
    # MRIData main folder
    outmainfolder = rootconfig.dms.folder_mridata

    if bconvert:
        cvt = ChanggungConverter(indcmmainfolder, inoutniftimainfolder, mriscanstxt)
        cvt.run()
    
    csv_motionscores = None
    csv_strokescores = None
    groupconflist = []
##    csv_motionscores = apppath('rawtable/scipatient_motionscores.csv')
##    csv_strokescores = apppath('rawtable/jixieshou_BCI+Jixieshou_scores.csv')
##    groupconflist = [('normal', 'Healthy normal people.', apppath('rawtable/normal_peopleorder.txt')),
##         ('scipatient', 'SCI patients.', apppath('rawtable/patient_peopleorder.txt')),
##         ('strokepatient', 'Stroke patients.', apppath('rawtable/jixieshou.txt'))]

    db = dbgen.DatabaseGenerator(
        apppath('rawtable/ChanggengMRITable.csv'),
        apppath('mmdpdb.db'),
        csv_motionscores,
        csv_strokescores,
        groupconflist
        )
    cls_niftigetter = ChanggungNiftiGetter
    imp = importer.MRIScanImporter(inoutniftimainfolder, outmainfolder, mriscanstxt, db, cls_niftigetter)
    imp.run()

    
