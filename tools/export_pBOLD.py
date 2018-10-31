import argparse
import os
import shutil

from mmdps.util import loadsave, path


class ExportBOLD:
    def __init__(self, preprocessedfolder, mriscans, exportfolder):
        self.preprocessedfolder = preprocessedfolder
        self.exportfolder = exportfolder
        self.mriscans = mriscans

    def run_mriscan(self, mriscan):
        src = os.path.join(self.preprocessedfolder, mriscan, 'Filtered_4DVolume.nii')
        if os.path.isfile(src):
            dst = os.path.join(self.exportfolder, mriscan, 'pBOLD.nii')
            path.makedirs_file(dst)
            shutil.copy2(src, dst)
            print(mriscan, 'OK')
        else:
            print(mriscan, 'not found', src)
            
    def run(self):
        for mriscan in self.mriscans:
            self.run_mriscan(mriscan)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy preprocessed BOLD to processing folder')
    parser.add_argument('--mriscanstxt', required=True, help='mriscans list in txt file')
    parser.add_argument('--outfolder', required=True, help='pBOLD output folder for all mriscans')
    args = parser.parse_args()
    exp = ExportBOLD(r'E:\DataProcessing\BOLDPreprocess\Data\FunRawARWSDCF',
                     loadsave.load_txt(args.mriscanstxt),
                     args.outfolder)
    exp.run()
    
    


    
