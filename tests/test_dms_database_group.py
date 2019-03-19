"""
This script connects to an existing database, add group relationship
and commit the changes
"""
from mmdps.dms import tables
from mmdps.util import loadsave
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def main():
	dbfile = 'E:/mmdpdb.db'
	engine = create_engine('sqlite:///' + dbfile)
	sessionManager = sessionmaker(bind = engine)
	session = sessionManager()
	db_group = tables.Group(name = 'test', description = 'test desc')
	session.add(db_group)
	names = loadsave.load_txt('E:/Changgung works/20180409_tDCS_14/score_info/control_namelist.txt')
	for name in names:
		person = session.query(tables.Person).filter_by(name = name).one()
		db_group.people.append(person)
	scans = loadsave.load_txt('E:/Changgung works/20180409_tDCS_14/score_info/control_scanlist-2.txt')
	for scan in scans:
		db_scan = session.query(tables.MRIScan).filter_by(filename = scan).one()
		db_group.scans.append(db_scan)
	session.commit()

if __name__ == '__main__':
	main()