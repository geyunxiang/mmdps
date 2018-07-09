import os
import dicom
import datetime
from collections import OrderedDict
from mmdps.util import clock, loadsave

def parse_date_space_time(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def parse_date_only(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d')

def date_only_str(dt):
    return dt.strftime('%Y-%m-%d')

class DicomInfo:
    def __init__(self, dicomfile):
        self.dicomfile = dicomfile
        self.plan = dicom.read_file(dicomfile)

    def studydate(self):
        thedate = self.plan.StudyDate
        thetime = self.plan.StudyTime
        dt = datetime.datetime.strptime(thedate + ' ' + thetime, '%Y%m%d %H%M%S')
        return str(dt)

    def institution(self):
        return str(self.plan.InstitutionName)

    def manufacturer(self):
        return str(self.plan.Manufacturer)

    def modelname(self):
        return str(self.plan.ManufacturersModelName)

    def patient(self):
        d = OrderedDict()
        try:
            d['ID'] = str(self.plan.PatientID)
        except:
            pass
        try:
            d['NameRaw'] = str(self.plan.PatientName)
        except:
            pass
        try:
            d['Name'] = d['NameRaw'].replace(' ', '').lower()
        except:
            pass
        try:
            d['Birth'] = date_only_str(datetime.datetime.strptime(self.plan.PatientsBirthDate, '%Y%m%d'))
        except:
            pass
        try:
            d['Gender'] = str(self.plan.PatientsSex)
        except:
            pass
        try:
            d['Weight'] = int(self.plan.PatientsWeight)
        except:
            pass
        try:
            d['Age'] = parse_date_space_time(self.studydate()).year - parse_date_only(d['Birth']).year
        except:
            pass
        try:
            d['AgeRaw'] = int(self.plan.PatientsAge[:-1])
        except:
            pass
        return d

    def machine(self):
        d = OrderedDict()
        d['Institution'] = self.institution()
        d['Manufacturer'] = self.manufacturer()
        d['ManufacturerModelName'] = self.modelname()
        return d
    
    def get_scan_info(self):
        d = OrderedDict()
        d['StudyDate'] = self.studydate()
        d['Machine'] = self.machine()
        d['Patient'] = self.patient()
        return d
    
    def print_core(self):
        print(self.studydate())
        print(self.institution())
        print(self.manufacturer())
        print(self.modelname())
        print(self.patient())
        
    def print_all(self):
        print(self.plan)
        
if __name__ == '__main__':
    di = DicomInfo('data_dicom/yangyubo_20180119/SE0/IM0')
    #di.print_all()
    di.print_core()
    d = di.get_scan_info()
    print()
    print(d)
    loadsave.save_json_ordered('test_scan_info.json', d)
    
    
    
