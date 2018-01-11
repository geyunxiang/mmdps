import os
import shutil
import glob

def copy_out(srcfolder, peoplelist, destfolder, pattern):
	for person in peoplelist:
		personfolder = os.path.join(srcfolder, person)
		files = glob.glob(os.path.join(personfolder, pattern))
		print(files)
		destpersonfolder = os.path.join(destfolder, person)
		if not os.path.isdir(destpersonfolder):
			os.mkdir(destpersonfolder)
		for file in files:
			shutil.copy2(file, destpersonfolder)

def copy_out_all_people(srcfolder, destfolder, pattern):
	folders = os.listdir(srcfolder)
	copy_out(srcfolder, folders, destfolder, pattern)
	
	
if __name__ == '__main__':
	copy_out(r'F:\BiShe\模块文档\Processing\bold\data',
			['gaohongping_20161214', 'gaohongping_20170122', 'lirongsheng_20170125'],
			r'F:\BiShe\模块文档\Processing\bold\net',
			'bold_net/*.csv')
