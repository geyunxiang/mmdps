import csv
import datetime
from mmdps.util import loadsave, clock
from mmdps.dms.tables import Base, Person, MRIScan, Group, MRIMachine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MMDPDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///../import_changgung/mmdpdb.db')
        self.Session = sessionmaker(bind=self.engine)

    def new_session(self):
        return self.Session()

    def personname_to_id(self, personnames):
        session = self.new_session()
        personids = []
        for personname in personnames:
            person = session.query(Person).filter_by(name=personname).one()
            personids.append(person.id)
        return personids
    
class TextExporter:
    def __init__(self, mmdb, outcsvname, personnamestxt, anonymize=True):
        self.mmdb = mmdb
        self.outcsvname = outcsvname
        self.anonymize = anonymize
        self.personnames = loadsave.load_txt(personnamestxt)
        
    def run(self):
        session = self.mmdb.new_session()
        ids = self.mmdb.personname_to_id(self.personnames)
        with open(self.outcsvname, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['MRIScanID', 'PersonID', 'PatientID', 'Name', 'Gender', 'Birth', 'Weight', 'Institution', 'Manufacturer', 'ModelName', 'ScanDate', 'HasT1', 'HasT2', 'HasBOLD', 'HasDWI'])
            for personid in ids:
                person = session.query(Person).get(personid)
                birthdate = person.birth.strftime('%Y_%m_%d')
                print(person)
                if self.anonymize:
                    thepersonname = 'P{}'.format(person.id)
                    thepatientid = 'hidden'
                else:
                    thepersonname = person.name
                    thepatientid = person.patientid
                for mriscan in person.mriscans:
                    scandate = datetime.datetime.strftime(mriscan.date, '%Y_%m_%d')
                    
                    machine = mriscan.mrimachine
                    writer.writerow([mriscan.id, person.id, thepatientid, thepersonname, person.gender, birthdate, person.weight, machine.institution, machine.manufacturer, machine.modelname, scandate, mriscan.hasT1, mriscan.hasT2, mriscan.hasBOLD, mriscan.hasDWI])

                    
if __name__ == '__main__':
    mmdb = MMDPDatabase()
    exp = TextExporter(mmdb, 'exported_mmdp.csv', 'personnames.txt', False)
    exp.run()
    exp = TextExporter(mmdb, 'exported_mmdp_anonymized.csv', 'personnames.txt', True)
    exp.run()    
        
