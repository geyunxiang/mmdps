import requests, datetime

from mmdps.dms import mmdpdb, tables
from mmdps.util import loadsave

api_url_root = 'https://brainpercep.com/api'
service_id = 'MMDPS_PMAR'
MAGIC_USERNAME_KEY = 'PMAR_USER_NAME'
MAGIC_TOKEN_KEY = 'PMAR_TOKEN'

def store_token(token):
	try:
		import keyring
		# the service is just a namespace for your app
		keyring.set_password(service_id, MAGIC_TOKEN_KEY, token)
	except ModuleNotFoundError:
		print('Module keyring not found. Cannot store token')
		return

def get_token():
	try:
		import keyring
		return keyring.get_password(service_id, MAGIC_TOKEN_KEY)
	except ModuleNotFoundError:
		print('Module keyring not found. Cannot restore token')
		return None

def authenticate(update = False):
	if not update:
		token = get_token()
		if token is not None:
			return token
	from mmdps.gui import auth_pop_window
	app = auth_pop_window.MainApplication()
	if app.terminate:
		exit()
	username = app.username()
	password = app.password()
	while True:
		try:
			json_dict = {'username': username, 'password': password}
			resp = requests.post(api_url_root + '/token-auth/', json = json_dict)
			if not response_ok(resp):
				print(resp.json())
				raise Exception('POST /token-auth/ {}'.format(resp.status_code))
			token = resp.json()['token']
			store_token(token)
			return token
		except Exception:
			app = auth_pop_window.MainApplication(True)
			if app.terminate:
				exit()
			username = app.username()
			password = app.password()

def response_ok(resp):
	if resp.status_code == 200 or resp.status_code == 201:
		return True
	return False

def search_patients(**kwargs):
	# 1. authenticate
	token = authenticate()

	# 2. search patient
	json_dict = kwargs
	resp = requests.post(api_url_root + '/patients/search/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
	if not response_ok(resp):
		print(resp.headers)
		print(resp.status_code)
		print(resp.json())
		token = authenticate(True)
		resp = requests.post(api_url_root + '/patients/search/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
		# raise Exception('POST /patients/search/ {}'.format(resp.status_code))
	# print(resp.json())
	return resp.json()

def add_patient(name, birthday, sex, rec_id):
	token = authenticate()
	json_dict = {'name': name, 'birthday': birthday, 'sex': sex, 'rec_id': rec_id, 'hospital': 3}
	resp = requests.post(api_url_root + '/patients/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
	while not response_ok(resp):
		print(resp.json())
		token = authenticate(True)
		resp = requests.post(api_url_root + '/patients/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
	return resp.json()

def edit_patient(patient_id, **kwargs):
	token = authenticate()
	json_dict = kwargs
	resp = requests.patch(api_url_root + '/patients/%d/' % patient_id, json = json_dict, headers = {'Authorization': 'JWT ' + token})
	if not response_ok(resp):
		print(resp.headers)
		print(resp.status_code)
		print(resp.json())
		token = authenticate(True)
		resp = requests.post(api_url_root + '/patients/search/', json = json_dict, headers = {'Authorization': 'JWT ' + token})

def add_scan(patient_id, date, scan_type = 'MRI'):
	token = authenticate()
	json_dict = {'rec_date': date, 'patient': patient_id, 'type': scan_type}
	resp = requests.post(api_url_root + '/exams/mriscan/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
	if not response_ok(resp):
		print(resp.headers)
		print(resp.status_code)
		print(resp.json())
		token = authenticate(True)
		resp = requests.post(api_url_root + '/exams/mriscan/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
		# raise Exception('POST /patients/search/ {}'.format(resp.status_code))
	return resp.json()

def add_patient_test():
	# 1. authenticate
	token = authenticate()

	# 2. add patient
	json_dict = {'name': '患者1', "birthday": "1995-02-20", 'sex': 'M', 'rec_id': "000001", 'diagnosis': '脑卒中-脑出血', 'injured_part': '下丘脑左动脉之类的地方', 'intervention': '常规训练', 'additional_diagnosis': '这是一段测试文字', 'hospital': 3}
	resp = requests.post(api_url_root + '/patients/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
	print(resp.headers)
	if not response_ok(resp):
		print(resp.json())
		raise Exception('POST /patients/ {}'.format(resp.status_code))
	print(resp.json())

def get_patient_record_dict():
	ret = dict() # key = name_en
	for line in loadsave.load_csv_to_list('I:/Changgung_patient_name_record.csv'):
		if line['name_en'] not in ret:
			ret[line['name_en']] = line
	return ret

def get_patient_diagnosis_dict():
	ret = dict() # key = name_en
	for line in loadsave.load_csv_to_list('I:/Changgung_patient_name_disease.csv'):
		if line['name_en'] not in ret:
			ret[line['name_en']] = line
	return ret

def get_patient_record(patient_record, patient_name):
	record_dict = patient_record.get(patient_name, None)
	if record_dict is None:
		return None, None, None
	else:
		return record_dict['name_zh'], record_dict['record_id'], record_dict

def get_diagnosis(patient_diagnosis, patient_name):
	diagnosis_dict = patient_diagnosis.get(patient_name, None)
	if diagnosis_dict is None:
		return None, None, None, None
	else:
		disease = diagnosis_dict['disease']
		lesion = diagnosis_dict['lesion_location']
		if disease == 'CS' and lesion.find('出血') != -1:
			disease = '脑卒中-脑出血'
		elif disease == 'CS':
			disease = '脑卒中-其他'
		elif disease == '脑出血':
			disease = '脑卒中-脑出血'
		elif disease == '脑梗死':
			disease = '脑卒中-脑梗死'
		elif disease == 'SCI' or disease == '脊髓损伤':
			disease = '脊髓损伤-其他'
		return disease, lesion, diagnosis_dict['comments'], diagnosis_dict

def fetch_local_patient_info():
	patient_record = get_patient_record_dict()
	patient_diagnosis = get_patient_diagnosis_dict()

	base_datetime = datetime.datetime(year = 2010, month = 1, day = 1)
	# parse_str = '%Y-%m-%d %H:%M:%S'

	token = authenticate()

	sdb = mmdpdb.SQLiteDB()
	session = sdb.new_session()
	patient_list = session.query(tables.Person).all()

	patient_list = patient_list[10:]

	for patient in patient_list:
		if patient.birth is None:
			continue
		# birth_datetime = datetime.datetime.strptime(patient.birth, parse_str)
		birth_datetime = patient.birth
		if birth_datetime > base_datetime:
			birth_datetime = None
			birthday_str = None
		else:
			birthday_str = birth_datetime.strftime('%Y-%m-%d')
		# print(patient.name)
		
		name_zh, record_id, _ = get_patient_record(patient_record, patient.name)
		disease, lesion, comments, _ = get_diagnosis(patient_diagnosis, patient.name)
		
		if record_id is None:
			# print(patient.name, 'record_dict', record_dict, 'diagnosis_dict', diagnosis_dict)
			continue
		print('name: %s\t, sex: %s, 病历号: %s, birthday: %s\t, 诊断: %s\t, 损伤部位: %s, 补充诊断: %s，干预方案: %s' % (name_zh, patient.gender, record_id, birthday_str, disease, lesion, comments, None))
		ret = search_patients(name_zh)
		if len(ret) != 0:
			continue
		if birthday_str is None:
			birthday_str = '2019-01-01'
		sex = patient.gender
		if sex == 'U':
			sex = 'O'
		json_dict = {'name': name_zh, "birthday": birthday_str, 'sex': sex, 'rec_id': record_id, 'diagnosis': disease, 'injured_part': lesion, 'intervention': '常规训练', 'additional_diagnosis': '无', 'hospital': 3}
		resp = requests.post(api_url_root + '/patients/', json = json_dict, headers = {'Authorization': 'JWT ' + token})
		if not response_ok(resp):
			print(resp.json())
			raise Exception('POST /patients/ {}'.format(resp.status_code))

def update_patient_scan():
	scan_dict = loadsave.load_csv_to_dict('I:/new_data_mapping.csv', 'en')
	for name, data_dict in scan_dict.items():
		if data_dict['en'] != 'wangguojun':
			continue
		scan = name + '_' + data_dict['date']
		scan_info = loadsave.load_json('X:/MRIData/%s/scan_info.json' % scan)
		print(scan, data_dict['zh'], data_dict['id'], scan_info['Patient']['ID'], scan_info['Patient']['Birth'], scan_info['Patient']['Gender'])
		search_res = search_patients(name = data_dict['zh'])
		print(search_res)
		if len(search_res) < 1:
			# new patient
			search_res = add_patient(data_dict['zh'], scan_info['Patient']['Birth'], scan_info['Patient']['Gender'], scan_info['Patient']['ID'])
		else:
			assert len(search_res) == 1
			search_res = search_res[0]
		add_scan(search_res['id'], scan_info['StudyDate'].replace(' ', 'T'))

if __name__ == '__main__':
	print(search_patients(name = '林清水'))
