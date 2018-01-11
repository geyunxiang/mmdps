import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk
import glob
import os


class Application(ttk.Frame):
	def __init__(self, master=None, **kw):
		super().__init__(master, **kw)
		self.build_selector()
		self.master = master
		
	def init(self, default, brief):
		self.confirmed = False
		self.result = default
		self.entry_str.set(default)
		self.brief_str.set(brief)
		
	def build_selector(self):
		self.entry = ttk.Entry(self)
		self.entry_str = tk.StringVar()
		self.entry['textvariable'] = self.entry_str

		self.brief = ttk.Label(self)
		self.brief_str = tk.StringVar()
		self.brief['textvariable'] = self.brief_str
		
		self.select = ttk.Button(self, text='Select...',
								 command=self.cb_select)
		self.confirm = ttk.Button(self, text='Confirm',
								  command=self.cb_confirm)
		packoptions = {'side': 'top', 'fill': 'both', 'expand': True}

		self.brief.pack(**packoptions)
		self.entry.pack(**packoptions)
		self.select.pack(**packoptions)
		self.confirm.pack(**packoptions)
		
	def cb_select(self):
		f = tk.filedialog.askdirectory(initialdir=self.result)
		if f:
			self.entry_str.set(f)
			print(f)
			
	def cb_confirm(self):
		self.confirmed = True
		self.result = self.entry_str.get()
		self.master.destroy()

def select_folder(default, title='select folder', brief='folder:'):
	'''Select a folder, return None if canceled.
	'''
	root = tk.Tk()
	root.title(title)
	app = Application(master=root)
	app.init(default, brief)
	app.pack(**{'side':'top', 'fill':'both', 'expand':True})
	root.mainloop()
	if app.confirmed:
		return app.result
	else:
		return None


if __name__ == '__main__':
	res = select_folder('C:/Windows', 'Select folder',
						"Select folder which contains each person's folder.\n"
						"Scripts should run in each folder.")
	print(res)

	
	

