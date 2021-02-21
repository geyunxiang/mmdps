import os
import numpy as np
import nibabel as nib
import subprocess 
# from mmdps.util.loadsave import load_nii, save_csvmat
from mmdps.util import path
from mmdps.util.loadsave import load_json
from mmdps.proc import atlas

INTER_ATTR_MAPPING = {
	"weighted_degree":1,
	"betweenness_centrality":2,
	"clustering_coefficients":3,
	"local_efficiency":4,
	"modularity":5,
	"small_worldness":6
}

INTRA_ATTR_MAPPING={
	"global_efficiency":1,
	"clustering_coefficients":2,
	"betweenness_centrality":3,
	"average_path_length":4,
	"modularity":5,
	"small_worldness":6
}

ATTR_PARA_COMPUTE_THRESHOLD={
	"aal":772,
	"aal2":758,
	"brodmann_lr":1465,
	"brodmann_lrce":1457,
	"bnatlas":242,
	"aicha":200
}


class InterAttrCalc:
	def __init__(self, corrPath, outfolder,json_name):
		self.corrPath = corrPath
		self.outfolder = outfolder
		self.exeName = path.fullfile("netcalc_inter_region.exe")
		self.from_json(json_name)

	def from_json(self,json_name):
		self.argsDict = load_json(json_name)
		pass
	
	def calc(self):
		if self.argsDict['if_stride']:
			threhold_depend = []
			threhold_independ = []
			for k,v in self.argsDict['calc_attr'].items():
				if v:
					if k == 'clustering_coefficients':
						threhold_depend.append(3)
					if k == 'modularity':
						threhold_depend.append(5)
					if k == 'small_worldness':
						threhold_depend.append(6)
					if k == 'weighted_degree':
						threhold_independ.append(1)
					if k == 'betweenness_centrality':
						threhold_independ.append(2)
					if k == 'local_efficiency':
						threhold_independ.append(4)
			temp_path = self.outfolder+"\\"+str(self.argsDict['netthreshold'])
			if not os.path.isdir(temp_path):
				os.mkdir(temp_path)
			cmd = self.build_cmd(attr = threhold_independ, nethold = None, out = temp_path)
			subprocess.call(cmd)
			for i in np.arange(self.argsDict['netthreshold'],self.argsDict['netthreshold_end']+self.argsDict['netthreshold_stride'],self.argsDict['netthreshold_stride']):
				temp_path = self.outfolder+"\\"+str(float('%.3f' %i))
				if not os.path.isdir(temp_path):
					os.mkdir(temp_path)
				cmd = self.build_cmd(attr = threhold_depend, nethold = float('%.3f' %i), out = temp_path)
				subprocess.call(cmd)
			pass
		else:
			temp_path = self.outfolder+"\\"+str(self.argsDict['netthreshold'])
			if not os.path.isdir(temp_path):
				os.mkdir(temp_path)
			cmd = self.build_cmd(out = temp_path)
			# os.system(cmd)
			subprocess.call(cmd)
			pass
	
	def build_cmd(self, attr = None, nethold = None, out = None):  #attr[1,2,3,4,5,6]
		cmd = [self.exeName,"-i",self.corrPath]
		if out:
			cmd.extend(["-o",out+"\\"])
		else:
			cmd.extend(["-o",self.outfolder+"\\"])

		if nethold:
			cmd.extend(["-n",str(nethold)])
		else:
			cmd.extend(["-n",str(self.argsDict['netthreshold'])])
		
		if attr:
			for i in attr:
				cmd.append("-c"+str(i))
		else:
			for k,v in self.argsDict['calc_attr'].items():
				if v:
					cmd.append("-c"+str(INTER_ATTR_MAPPING[k]))
		return cmd

class IntraAttrCalc:
	def __init__(self, niipath, atlasobj, outfolder, json_name):
		self.niipath = niipath
		self.atlasobj = atlasobj
		self.atlas_3mm_path = atlasobj.volumes['3mm']['niifile']
		self.outfolder = outfolder
		self.exeName = path.fullfile("netcalc_intra_region.exe")
		self.from_json(json_name)

	def from_json(self,json_name):
		self.argsDict = load_json(json_name)
		pass
	
	def calc(self):
		if self.argsDict['if_stride']:
			threhold_depend = []
			threhold_independ = []
			for k,v in self.argsDict['calc_attr'].items():
				if v:
					if k == 'clustering_coefficients':
						threhold_depend.append(2)
					if k == 'modularity':
						threhold_depend.append(5)
					if k == 'small_worldness':
						threhold_depend.append(6)
					if k == 'global_efficiency':
						threhold_independ.append(1)
					if k == 'betweenness_centrality':
						threhold_independ.append(3)
					if k == 'average_path_length':
						threhold_independ.append(4)
			temp_path = self.outfolder+"\\"+str(self.argsDict['netthreshold'])
			if not os.path.isdir(temp_path):
				os.mkdir(temp_path)
			cmd = self.build_cmd(attr = threhold_independ, nethold = None, out = temp_path)
			subprocess.call(cmd)
			for i in np.arange(self.argsDict['netthreshold'],self.argsDict['netthreshold_end']+self.argsDict['netthreshold_stride'],self.argsDict['netthreshold_stride']):
				temp_path = self.outfolder+"\\"+str(float('%.3f' %i))
				if not os.path.isdir(temp_path):
					os.mkdir(temp_path)
				cmd = self.build_cmd(attr = threhold_depend, nethold = float('%.3f' %i), out = temp_path)
				subprocess.call(cmd)
			pass
		else:
			temp_path = self.outfolder+"\\"+str(self.argsDict['netthreshold'])
			if not os.path.isdir(temp_path):
				os.makedirs(temp_path, exist_ok = True)
			cmd = self.build_cmd(out = temp_path)
			# os.system(cmd)
			subprocess.call(cmd)
			pass
	
	def build_cmd(self, attr = None, nethold = None, out = None):  #attr[1,2,3,4,5,6]
		cmd = [self.exeName,"-i",self.niipath,"-a",self.atlas_3mm_path]
		if out:
			cmd.extend(["-o",out+"\\"])
		else:
			cmd.extend(["-o",self.outfolder+"\\"])
		cmd.extend(["-s",str(self.argsDict['weakorstrong'])])

		if nethold:
			cmd.extend(["-n",str(nethold)])
		else:
			cmd.extend(["-n",str(self.argsDict['netthreshold'])])
		
		cmd.extend(["-p",str(ATTR_PARA_COMPUTE_THRESHOLD[self.atlasobj.name])])
		if attr:
			for i in attr:
				cmd.append("-c"+str(i))
		else:
			for k,v in self.argsDict['calc_attr'].items():
				if v:
					cmd.append("-c"+str(INTRA_ATTR_MAPPING[k]))
		return cmd



def inter_calc():
	print(os.getcwd())
	corrcoef_path = os.path.join(os.getcwd(),'bold_net','corrcoef.csv')
	outfolder = os.path.join(os.getcwd(), 'bold_net_attr_zzl')
	json_path = path.fullfile("inter_attr.json")
	print(outfolder)
	print(corrcoef_path)
	if not os.path.isdir(outfolder):
		os.mkdir(outfolder)
	inter_ac = InterAttrCalc(corrcoef_path,outfolder,json_path)
	inter_ac.calc()

def intra_calc():
	print(os.getcwd())
	atlasobj = path.curatlas()
	volumename = '3mm'

	nii_path = os.path.join(path.curparent(), 'pBOLD.nii')
	outfolder = os.path.join(os.getcwd(), 'bold_net_attr_zzl')
	json_path = path.fullfile("intra_attr.json")
	print(nii_path)
	print(outfolder)
	if not os.path.isdir(outfolder):
		os.mkdir(outfolder)
	intra_ac = IntraAttrCalc(nii_path,atlasobj,outfolder,json_path)
	intra_ac.calc()


if __name__ == '__main__':
	inter_calc()
	intra_calc()
	pass

