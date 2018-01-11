import nibabel as nib
import numpy as np
import json
import os

def create_template_jdict(tempname):
	# get nii info
	img = nib.load(tempname+'.nii')
	data = img.get_data()
	unique, unique_count = np.unique(data, return_counts=True)
	unique = unique[1:]
	unique_count = unique_count[1:]
	region_count = unique.size
	
	# fill json dict
	jdict = {}
	jdict['name'] = tempname
	jdict['brief'] = 'Brain template ' + tempname
	jdict['count'] = region_count
	jdict['ticks'] = ['B'+str(r) for r in unique.tolist()]
	jdict['plotindexes'] = list(range(region_count))
	jdict['regions'] = unique.tolist()
	jdict['region_counts'] = unique_count.tolist()
	return jdict

def create_template_json(tempname):
	jfolder = 'created_json'
	jdict = create_template_jdict(tempname)
	jname = 'created_'+tempname+'.json'
	if not os.path.isdir(jfolder):
		os.mkdir(jfolder)
	jpath = os.path.join(jfolder, jname)
	with open(jpath, 'w') as f:
		json.dump(jdict, f, sort_keys=True, ensure_ascii=False)
		
		
if __name__ == '__main__':
	#tempname = 'brodmann_lr_3'
	#tempname = 'aal_1'
	tempname = 'brodmann_lrce_1'
	#tempname = 'brodmann_lrce_3'
	#tempname = 'aal_3'
	#tempname = 'aal_2'
	create_template_json(tempname)

