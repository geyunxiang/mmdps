"""Interface that could be used by apps that consume the RESTful API.

Can be used by Python apps to access the RESTful API.
Such as the webapp server and Python GUI app.
"""


import shutil
import requests
from ..util.path import makedirs_file
from ..util import clock


def name_date(s):
    l = s.split('_')
    return l[0], l[1]

class ApiCore:
    """Access the RESTful API.

    Use requests to send and receive information.
    """
    def __init__(self, urlbase, auth):
        """Construct the accessor, provided the urlbase for the server and user auth information."""
        if urlbase[-1] == '/':
            urlbase = urlbase[0:-1]
        self._urlbase = urlbase
        self._auth = auth
        self._reqparams = {'auth': self._auth, 'verify': False}
        self._feature_reqparams = self._reqparams

    def feature_full_url(self, urlpath):
        return self._urlbase + '/features' + urlpath

    def feature_get(self, urlpath):
        """Get the specified feature."""
        return requests.get(self.feature_full_url(urlpath), **self._feature_reqparams)
    
    def full_url(self, urlpath):
        return self._urlbase + urlpath

    def getdict(self, urlpath):
        """Get dict constructed from the json the server returned."""
        r = self.get(urlpath)
        if r.status_code != 200:
            return None
        return r.json()
    
    def get(self, urlpath):
        """Raw get, return what the requests.get would return."""
        return requests.get(self.full_url(urlpath), **self._reqparams)

    def getobjdict(self, tablename, objid):
        """Get the object dict in table."""
        urlpath = '/{}/{}'.format(tablename, objid)
        return self.getdict(urlpath)
    
    def gettabledict(self, tablename):
        """Get the table dict."""
        urlpath = '/' + tablename
        return self.getdict(urlpath)
    
    def valid(self):
        """Test server connection."""
        if self.getdict('') is None:
            return False
        return True
    
    def download(self, urlpath, outfilepath):
        """Blocking download file to outfilepath."""
        makedirs_file(outfilepath)
        print(urlpath)
        r = requests.get(self.full_url(urlpath), stream=True, **self._reqparams)
        if r.status_code != 200:
            print('Download not allowed or file not exist')
            return False
        with open(outfilepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            print('Download OK')
        return True
        
    def get_mriscan_data_iter_r(self, mriscan_id, modal):
        """Get iterator and request object for downloading data, non-blocking."""
        urlpath = '/mriscans/{}/get/{}'.format(mriscan_id, modal)
        r = requests.get(self.full_url(urlpath), stream=True, **self._reqparams)
        if r.status_code != 200:
            return None, r
        it = r.iter_content(chunk_size=10*2**20)
        return it, r

    def get_person_by_name(self, name):
        """Get person object or people list by person name."""
        print(name)
        urlpath = '/people?where={{"name":"{}"}}'.format(name)
        resd = self.getdict(urlpath)
        res = resd['_items']
        if len(res) == 1:
            return res[0]
        elif len(res) == 0:
            print('Not Found')
            return None
        else:
            print('Found multiple', len(res))
            return res
        
            
    def get_mriscan_by_namedate(self, namedate):
        """Get mriscan dict by name_date."""
        personname, scandate = name_date(namedate)
        persond = self.get_person_by_name(personname)
        mriscan_ids = persond['mriscans']
        for mriscan_id in mriscan_ids:
            mriscand = self.getobjdict('mriscans', mriscan_id)
            if clock.iso_to_simple(mriscand['date']) == scandate:
                return mriscand
        return None
    
    def get_namedate_by_mriscanid(self, mriscan_id):
        """Get name_date by mriscan id."""
        mriscand = self.getobjdict('mriscans', mriscan_id)
        person_id = mriscand['person']
        persond = self.getobjdict('people', person_id)
        name = persond['name']
        date = clock.iso_to_simple(mriscand['date'])
        return name + '_' + date
    
        
