import tkinter as tk
from mmdps.gui import guiframe, tktools, field
from mmdps.util.loadsave import load_json_ordered
from mmdps.proc import job
# import runjob


class RunJobApplication(guiframe.MainWindow):
	def __init__(self, master=None, **kw):
		guiframe.MainWindow.__init__(self, master, **kw)
		self.build_actions()
		self.build_widgets()

	def build_actions(self):
		pass

	def build_widgets(self):
		d = {'typename': 'FileEditField', 'name': 'JobConfig', 'value': ''}
		self.fjob = field.create(d)
		d = {'typename': 'FolderField', 'name': 'Folder', 'value': '.'}
		self.ffolder = field.create(d)
		wjob = self.fjob.build_widget(self.mainframe)
		wfolder = self.ffolder.build_widget(self.mainframe)
		wrun = tktools.button(self.mainframe, 'Run', self.cb_runjob)
		wjob.pack()
		wfolder.pack()
		wrun.pack()

	def cb_runjob(self):
		jobconf = self.fjob.value
		folderconf = self.ffolder.value
		j = job.load(load_json_ordered(jobconf))
		runjob.runjob(j, folderconf)

def runjob(job, folder=None):
	if folder:
		with job.ChangeDirectory(folder):
			return job.run()
	else:
		return job.run()

if __name__ == '__main__':
	root = tk.Tk()
	root.geometry('800x600')
	app = RunJobApplication(root)
	app.pack(fill='both', expand=True)
	root.title('MMDPS RunJob')
	root.mainloop()
