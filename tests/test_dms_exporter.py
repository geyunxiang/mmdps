from mmdps.dms import exporter
exp = exporter.MRIScanTableExporter('Y:/Data/MRIData/', 'E:/Results/test_exporter.csv')
exp.run()
