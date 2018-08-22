import sys
import os

from mmdps.util.fileop import gz_unzip


def nii_to_hdrimg(niifile):
    '''NIFTI 1 only.'''
    if not os.path.isfile(niifile):
        print('cannot open niifile', niifile)
        return None
    if not (niifile[-4:] == '.nii' or niifile[-7:] == '.nii.gz'):
        print('niifile should be .nii or .nii.gz\n')
        return None
    if niifile[-3:] == '.gz':
        niifile = gz_unzip(niifile)
    file, ext = os.path.splitext(niifile)
    hdrfile = file + '.hdr'
    imgfile = file + '.img'
    with open(niifile, 'rb') as fnii,\
         open(hdrfile, 'wb') as fhdr,\
         open(imgfile, 'wb') as fimg:
        hdrdata = bytearray(fnii.read(348))
        hdrdata[345] = 0x69 # n+1 to ni1
        hdrdata[0x6C] = 0x00 # vol_offset to 0
        hdrdata[0x6D] = 0x00
        hdrdata[0x6E] = 0x00
        hdrdata[0x6F] = 0x00
        
        fhdr.write(hdrdata)
        fnii.read(4)
        while True:
            data = fnii.read(10**6)
            if data == b'':
                break
            fimg.write(data)
            
    return hdrfile

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python nii_to_hdrimg.py thenifitifile.nii')
        sys.exit(-1)
    
    b = nii_to_hdrimg(sys.argv[1])
    if b is None:
        print('Error')
        sys.exit(-2)

        
    
