import argparse, os
from mmdps.dms import feature_exporter
from mmdps.util import loadsave
from mmdps import rootconfig

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--modal', help = 'specific modal to export', default = None)
	parser.add_argument('--database', help = 'True/False. Whether export features to MMDPDatabase (MongoDB Database)', default = False)
	parser.add_argument('--datasource', help = 'datasource for MMDPDatabase', default = None)
	parser.add_argument('--force', help = 'True/False. If overwrite existing feature record', default = False)

	args = parser.parse_args()

	feature_exporter.check_modal(args.modal, os.path.join(rootconfig.path.dms, 'export_mainconf.json'))
	data_config = loadsave.load_json(os.path.join(rootconfig.path.dms, 'export_dataconf.json'))
	main_config = loadsave.load_json(os.path.join(rootconfig.path.dms, 'export_mainconf.json'))

	if args.modal is not None:
		print('Will search default folder for %s' % (args.modal))
	if args.database and args.datasource is None:
		raise Exception('Datasource unknown')
	elif args.database:
		print('Will export to database. datasource = %s' % (args.datasource))
	if args.force:
		print('Force mode. Will overwrite existing features')

	exporter = feature_exporter.MRIScanProcExporter(main_config, data_config, args.modal, args.database, args.datasource, args.force)
	exporter.run()
	print('Feature export completed.')
