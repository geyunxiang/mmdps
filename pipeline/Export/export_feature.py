import argparse
import feature_export
from mmdps.util import loadsave

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--modal', help = 'specific modal to export', default = None)
	parser.add_argument('--folder', help = 'folder that stores the specified modal', default = None)
	parser.add_argument('--database', help = 'whether export features to MMDPDatabase (MongoDB Database)', default = False)
	parser.add_argument('--datasource', help = 'datasource for MMDPDatabase', default = None)
	args = parser.parse_args()
	print('Export modal:', args.modal)
	print('Export search folder:', args.folder)

	feature_export.check_modal(args.modal, 'export_mainconf.json')
	data_config = loadsave.load_json('export_dataconf.json')
	main_config = loadsave.load_json('export_mainconf.json')

	if args.modal is not None and args.folder is None:
		print('Will search default folder for %s' % (args.modal))
	elif args.modal is None and args.folder is not None:
		print('Will search %s for all modalities' % (args.folder))
	elif args.modal is None and args.folder is None:
		print('Will search default folder for all modalities')
	else:
		print('Will search %s for %s' % (args.folder, args.modal))
	if args.database and args.datasource is None:
		raise Exception('Datasource unknown')
	elif args.database:
		print('Will export to database. datasource = %s' % (args.datasource))

	exporter = feature_export.MRIScanProcExporter(main_config, data_config, args.modal, args.folder, args.database, args.datasource)
	exporter.run()
	print('Feature export completed.')
