from mmdps.dms import converter

if __name__ == '__main__':
    mriscan = 'yinbaosheng_20180103'
    infolder = 'F:/BiShe/playground/importer/data_dicom/' + mriscan
    outfolder = 'F:/BiShe/playground/importer/data_rawnii/' + mriscan
    converter.convert_dicom(infolder, outfolder)
