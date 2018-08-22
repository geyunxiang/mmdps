import sys
import os
import gzip

from mmdps.util.fileop import gz_zip


def hdrimg_to_nii(hdrfile):
    '''NIFTI 1 only.'''
    imgfile = hdrfile[:-4] + '.img'
    if not os.path.isfile(hdrfile) or not os.path.isfile(imgfile):
        print('cannot open hdr img files', hdrfile, imgfile)
        return None
    niifile = hdrfile[:-4] + '.nii'
    with open(hdrfile, 'rb') as fhdr,\
         open(imgfile, 'rb') as fimg,\
         open(niifile, 'wb') as fnii:
        
        hdrdata = bytearray(fhdr.read(348))
        hdrdata[345] = 0x2B # n+1 to ni1
        hdrdata[0x6C] = 0x00 # vol_offset to 0
        hdrdata[0x6D] = 0x00
        hdrdata[0x6E] = 0xB0
        hdrdata[0x6F] = 0x43
        
        fnii.write(hdrdata)
        fnii.write(b'\x00\x00\x00\x00')
        while True:
            data = fimg.read(10**6)
            if data == b'':
                break
            fnii.write(data)
    outfile = gz_zip(niifile)
    return outfile

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python hdrimg_to_nii.py thehdrfile.hdr')
        sys.exit(-1)
    
    b = hdrimg_to_nii(sys.argv[1])
    if b is None:
        print('Error')
        sys.exit(-2)

        
    
