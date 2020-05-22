"""GUI tools management.

"""

import os
import sys
# from ..gui import tktools
# from ..util.loadsave import load_json
# from .. import rootconfig
# from ..util import run
# from . import path
from mmdps.gui import tktools
from mmdps.util.loadsave import load_json
from mmdps import rootconfig
from mmdps.util import run, path

class Tool:
	"""Represents one GUI tool."""
	def __init__(self, name, pyui, argv = None):
		"""Init use tool name and python ui scripts."""
		self.name = name
		self.pyui = pyui
		self.argv = argv

	def opentool(self, *argv):
		"""Open the gui tool."""
		pyui = path.fullfile(self.pyui)
		assert pyui
		cmdlist = [pyui]
		if self.argv is not None:
			cmdlist.extend([self.argv])
		cmdlist.extend(argv)
		# print('opentool cmdlist: ', cmdlist)
		run.popen_py(cmdlist, sys.platform == 'win32')

	def build_widget(self, master=None):
		"""Build the tool button."""
		return tktools.button(master, self.name, self.opentool)

class ToolManager:
	"""Manages all gui tools."""
	def __init__(self):
		"""Init manager."""
		pass

	def load(self, config):
		"""Load all tools in config."""
		toolconfigs = config['tools']
		self._tools = []
		self._toolsdict = {}
		for toolconfig in toolconfigs:
			toolname = toolconfig['name']
			pyui = toolconfig['pyui']
			tool = Tool(toolname, pyui, toolconfig.get('argv', None))
			self._tools.append(tool)
			self._toolsdict[toolname.lower()] = tool

	def find(self, toolname):
		"""Find the tool by name."""
		toolname = toolname.lower()
		tool = self._toolsdict.get(toolname, None)
		return tool

	def get(self, toolname):
		"""Get the tool by name."""
		return self._toolsdict[toolname.lower()]

	@property
	def tools(self):
		"""All tools."""
		return self._tools

def get_default_manager():
	"""Get the default tool manager, configured using tools_config.json."""
	toolsconffile = os.path.join(rootconfig.path.tools, 'ui_programs', 'tools_config.json')
	toolsconf = load_json(toolsconffile)
	manager = ToolManager()
	manager.load(toolsconf)
	return manager
