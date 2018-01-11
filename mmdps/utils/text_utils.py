import csv

def get_list_from_txt(txt):
	linelist = []
	with open(txt) as f:
		linelist = [line.strip() for line in f]
	return linelist

def get_scan_name_date(scan):
	l = scan.split('_')
	return l[0], l[1]

def get_scan_name(scan):
	name, date = get_scan_name_date(scan)
	return name

def get_scan_date(scan):
	name, date = get_scan_name_date(scan)
	return date
	
def get_groups(caselist):
	groups = []
	prevname = None
	curgrp = []
	for case in caselist:
		name = get_scan_name(case)
		if name == prevname:
			curgrp.append(case)
		else:
			if curgrp:
				groups.append(curgrp)
			curgrp = [case]
			prevname = name
	groups.append(curgrp)
	return groups


