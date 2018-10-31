import os, shutil, argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--rootfolder', help='The root folder to search for logs', required=True)
	args = parser.parse_args()

	if not os.path.isdir(args.rootfolder):
		print('Please input a directory path, {} does not seem to be an existing directory.'.format(args.rootfolder))
		exit()
	
	for dirpath, dirnames, filenames in os.walk(args.rootfolder):
		if os.path.split(dirpath)[1] != 'log':
			continue
		for filename in filenames:
			if filename[:4] == 'log_':
				os.remove(os.path.join(dirpath, filename))
