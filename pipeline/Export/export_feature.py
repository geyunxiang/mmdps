import feature_export
from mmdps.util import path

if __name__ == '__main__':
	exporter = feature_export.create_by_files('export_mainconf.json', 'export_dataconf.json')
	exporter.run()
	print('Feature export completed.')
