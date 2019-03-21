"""
This script connects to an existing database, add group relationship
and commit the changes
"""
from mmdps.dms import mmdpdb
from mmdps.proc import group_manager
from mmdps.util import loadsave

def test_getAllGroups(groupManager):
	print(groupManager.getAllGroups())

def test_newGroupByScans(groupManager):
	scans = loadsave.load_txt('E:/Changgung works/20180409_tDCS_14/score_info/control_scanlist-2.txt')
	groupManager.newGroupByScans('test control 2', scans)
	return

def test_newGroupByNames(groupManager):
	# names = loadsave.load_txt('E:/Changgung works/20180409_tDCS_14/score_info/control_namelist.txt')
	groupManager.newGroupByNames('test name 5', ['guojiye'], 5)

def test_deleteGroupByName(groupManager):
	groupManager.deleteGroupByName('test multi 2')

def test_multipleScanMultipleGroup(groupManager):
	groupManager.newGroupByScans('test multi 1', ['chenhua_20150711', 'cuichenhao_20180704'])
	groupManager.newGroupByScans('test multi 2', ['chenhua_20150711', 'daihuachen_20170927'])

def main():
	db = mmdpdb.MMDPDatabase()
	groupManager = group_manager.DatabaseGroupManager(db)
	test_getAllGroups(groupManager)

	test_deleteGroupByName(groupManager)
	# test_newGroupByScans(groupManager)
	# test_newGroupByNames(groupManager)
	# test_multipleScanMultipleGroup(groupManager)

	test_getAllGroups(groupManager)
	# scans = groupManager.getScansInGroup('test name 5')
	# for scan in scans:
	# 	print(scan.filename)
	
	return 0

if __name__ == '__main__':
	main()
