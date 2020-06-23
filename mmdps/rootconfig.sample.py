"""
root config for mmdps.

Important tools and paths configurations.
Manual edit required when moving mmdps around.
win32 and Linux platform can co-exist.
"""

import os
import sys

if sys.platform == 'win32':
	# matlab path
	matlab_bin = 'C:/Program Files/MATLAB/R2016b/bin/matlab.exe'
	class path:
		"""important paths and tools config."""
		# the mmdps package folder
		pyroot = os.path.dirname(os.path.abspath(__file__))
		# the root MMDPS folder
		root = os.path.abspath(os.path.join(pyroot, '..'))
		tools = os.path.join(root, 'tools')
		proc = os.path.join(pyroot, 'proc')
		dms = os.path.join(pyroot, 'dms')
		atlas = os.path.join(root, 'atlas')
		data = os.path.join(root, 'data')
		bnvdata = os.path.join(data, 'bnv')
		# text editor to edit text files
		texteditor = 'D:/Program Files/Microsoft VS Code/bin/code.cmd'
		python = sys.executable
		pythonw = 'D:/app/Python/Python35/pythonw.exe'
		# nii viewer to view nii file
		niiviewer = 'D:/Program Files (x86)/mricron/mricron.exe'
		# dicom to nifti converter, it's in mricron-gl distribution. Use custom compiled pigz if hangs.
		# dcm2nii = 'D:/Software/mricrogl/dcm2niix.exe'
		dcm2nii = 'E:/PC/mricron/dcm2nii.exe'
		# circos executable path
		circos = 'E:/PC/circos-0.69-6/bin/circos.exe'
		# feature root
		feature_root = 'Z:/ChangGungFeatures/'

	class server:
		"""server address configs"""
		# api server address, flask
		api = 'http://127.0.0.1:5000'
		# storage server address, nginx
		storage = 'https://101.6.69.210'
		# feature server address, nginx
		featurestorage = 'https://127.0.0.1'

	class dms:
		"""for data import and static mridata server."""
		# data import working folder, scores go here
		folder_working = r'F:/MMDPSoftware/mmdps/tools/import_changgung'
		# data import dicom folder
		folder_dicom = r'F:/MMDPDatabase/data_dicom'
		# data import raw nifti folder, niftis converted from dicom go here
		folder_rawnii = r'F:/MMDPDatabase/data_rawnii'
		# the mri data folder
		folder_mridata = r'F:/MMDPDatabase/Data/MRIData'
		# the mmdpdb file path
		mmdpdb_filepath = 'I:/MMDPDatabase/mmdpdb.db'
		# CD driver path
		CD_dicom_path = 'G:/DICOM/'
		# MongoDB host address
		mongo_host = 'localhost'

else:
	matlab_bin = '/usr/local/bin/matlab'
	class path:
		pyroot = os.path.dirname(os.path.abspath(__file__))
		root = os.path.abspath(os.path.join(pyroot, '..'))
		tools = os.path.join(root, 'tools')
		proc = os.path.join(pyroot, 'proc')
		atlas = os.path.join(root, 'atlas')
		data = os.path.join(root, 'data')
		bnvdata = os.path.join(data, 'bnv')
		texteditor = '/usr/local/bin/matlab'
		python = sys.executable
		niiviewer = '/usr/local/bin/mricron'
		dcm2nii = ''
		# feature root
		feature_root = ''

	class server:
		api = 'http://127.0.0.1:5000'
		storage = 'https://101.6.69.229'
		featurestorage = 'https://127.0.0.1'

	class dms:
		folder_working = r'F:/MMDPSoftware/mmdps/tools/import_changgung'
		folder_dicom = r'F:/MMDPDatabase/data_dicom'
		folder_rawnii = r'F:/MMDPDatabase/data_rawnii'
		folder_mridata = r'F:/MMDPDatabase/Data/MRIData'
		mmdpdb_filepath = ''
