import os
import tkinter as tk
from mmdps.gui import guiframe, tktools, field
from mmdps import rootconfig
from mmdps.util import run
from mmdps.remote_service import batchget, apicore

class Application(guiframe.MainWindow):
	def __init__(self, master=None, **kw):
		guiframe.MainWindow.__init__(self, master, **kw)
		self.build_actions()
		self.build_widgets()

	def setup(self, api):
		self.api = api

	def build_actions(self):
		pass

	def build_widgets(self):
		d = {'typename': 'FileEditField', 'name': 'MRIScansTxt', 'value': ''}
		self.fmriscanstxt = field.create(d)
		d = {'typename': 'ComboboxField', 'name': 'ModalFile', 'value': 'T1.nii.gz', 'values':
			 ['T1.nii.gz', 'T2.nii.gz', 'BOLD.nii.gz', 'pBOLD.nii.gz', 'DWI.nii.gz', 'DWI.bval', 'DWI.bvec']}
		self.fmodal = field.create(d)
		d = {'typename': 'FolderField', 'name': 'OutMainFolder', 'value': '.'}
		self.foutfolder = field.create(d)
		wmriscanstxt = self.fmriscanstxt.build_widget(self.mainframe)
		wmodal = self.fmodal.build_widget(self.mainframe)
		woutfolder = self.foutfolder.build_widget(self.mainframe)
		wrun = tktools.button(self.mainframe, 'Run', self.cb_run)
		wmriscanstxt.pack()
		wmodal.pack()
		woutfolder.pack()
		wrun.pack()

	def cb_run(self):
		txt = self.fmriscanstxt.value
		modal = self.fmodal.value
		outfolder = self.foutfolder.value
		bg = batchget.BatchGet(self.api, txt, modal, outfolder)
		bg.run()
		print('batch get end')

if __name__ == '__main__':
	root = tk.Tk()
	app = Application(root)
	api = apicore.ApiCore(rootconfig.server.api, ('mmdpdata', '123'))
	app.setup(api)
	app.pack(fill='both', expand=True)
	root.title('MMDPS BatchGet')
	root.mainloop()
