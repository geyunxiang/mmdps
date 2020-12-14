import tkinter as tk

class MainApplication(tk.Frame):
	def __init__(self, warning = False):
		self.root = tk.Tk()
		self.root.title('Authentication')
		self.root.geometry('400x200')
		tk.Frame.__init__(self, self.root)
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.terminate = False
		self.create_widgets(warning)
		self.root.mainloop()

	def create_widgets(self, warning):
		if warning:
			self.warningLabel = tk.Label(self.root, text="Incorrect username or password!", fg = 'red').grid(row=0, column=1)
		else:
			self.warningLabel = tk.Label(self.root, text="").grid(row=0, column=0)
		#username label and text entry box
		self.usernameLabel = tk.Label(self.root, text="User Name").grid(row=1, column=0)
		self._username = tk.StringVar()
		# self.usernameEntry = tk.Entry(self.root, textvariable=self._username).grid(row=1, column=1)
		self.usernameEntry = tk.Entry(self.root, textvariable=self._username)
		self.usernameEntry.grid(row=1, column=1)
		self.usernameEntry.focus()

		#password label and password entry box
		self.passwordLabel = tk.Label(self.root,text="Password").grid(row=2, column=0)  
		self._password = tk.StringVar()
		self.passwordEntry = tk.Entry(self.root, textvariable=self._password, show='*').grid(row=2, column=1)

		#login button
		self.loginButton = tk.Button(self.root, text="Login", command = self.cb_login).grid(row=4, column=0)
		self.root.bind('<Return>', self.cb_login)

	def cb_login(self, *args):
		self.root.destroy()

	def on_closing(self):
		"""
		If user closes the window by clicking X, all program should exit
		"""
		self.terminate = True
		self.root.destroy()

	def password(self):
		return self._password.get()

	def username(self):
		return self._username.get()

if __name__ == '__main__':
	app = MainApplication()
	print(app.username(), app.password())
