import nibabel as nib
import numpy as np
import json
import os
from collections import OrderedDict

def create_template_jdict(tempfolder, tempname):
	# get nii info
	img = nib.load(os.path.join(tempfolder, tempname+'.nii'))
	data = img.get_data()
	data = np.nan_to_num(data)
	unique, unique_count = np.unique(data, return_counts=True)
	print(unique)
	unique = unique[1:]
	unique_count = unique_count[1:]
	region_count = unique.size

	# fill json dict
	jdict = OrderedDict()
	jdict['name'] = tempname
	jdict['brief'] = 'Brain template ' + tempname
	jdict['count'] = region_count
	jdict['ticks'] = ['B'+str(int(r)) for r in unique.tolist()]
	jdict['plotindexes'] = list(range(region_count))
	jdict['regions'] = unique.astype('int').tolist()
	jdict['region_counts'] = unique_count.tolist()
	return jdict

def create_template_json(tempfolder, tempname):
	jfolder = 'created_json'
	jdict = create_template_jdict(tempfolder, tempname)
	jname = 'created_'+tempname+'.json'
	if not os.path.isdir(jfolder):
		os.mkdir(jfolder)
	jpath = os.path.join(jfolder, jname)
	with open(jpath, 'w') as f:
		json.dump(jdict, f, sort_keys=True, ensure_ascii=False)

if __name__ == '__main__':
	#tempname = 'brodmann_lr_3'
	#tempname = 'aal_1'
	#tempname = 'brodmann_lrce_3'
	#tempname = 'aal_3'
	#tempname = 'aal_2'
	#create_template_json('bnatlas', 'bnatlas_1')
	# create_template_json('aal2', 'aal2_1')
	# create_template_json('aal2', 'aal2_2')
	# create_template_json('aal2', 'aal2_3')
	create_template_json('aal3', 'aal3_2')
