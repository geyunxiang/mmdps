"""Storage for database.

Access static server.
"""

import shutil
import requests
# from ..util.path import makedirs_file
from mmdps.util.path import makedirs_file

class Storage:
    """Storage base class."""
    def __init__(self):
        pass


class HTTPStorage(Storage):
    """Storage based on static HTTP server."""
    # download chunk size
    CHUNK_SIZE = 10 * 2**20
    # progress bar total length
    PROGRESSBAR_LENGTH = 50
    
    def __init__(self, urlbase, auth):
        """Init use url and auth information."""
        self._auth = auth
        if urlbase[-1] != '/':
            urlbase += '/'
        self._urlbase = urlbase
        self._reqparams = {'auth': self._auth, 'verify': False}

    def full_url(self, urlpath):
        """Construct full url."""
        return self._urlbase + urlpath

    def get(self, urlpath):
        """Call requests.get with user auth."""
        return requests.get(self.full_url(urlpath), **self._reqparams)

    def get_file(self, urlpath, localpath):
        """Get file blocking."""
        makedirs_file(localpath)
        url = self.full_url(urlpath)
        r = requests.get(url, stream=True, **self._reqparams)
        if r.status_code != 200:
            self.error(r, url)
            return False
        print('Retriving file from {} to {}  '.format(url, localpath), end='')
        with open(localpath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print('OK')
        return True
    
    def get_file_progress(self, urlpath, localpath):
        """Get file blocking, with a fancy progress bar."""
        makedirs_file(localpath)
        url = self.full_url(urlpath)
        r = requests.get(url, stream=True, **self._reqparams)
        filesize = int(r.headers['content-length'])
        if r.status_code != 200:
            self.error(r, url)
            return False
        downloadedsize = 0
        progress = 0
        print('Retriving file from {} to {}  '.format(url, localpath))
        with open(localpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=self.CHUNK_SIZE):
                if chunk:
                    downloadedsize = downloadedsize + self.CHUNK_SIZE
                    newprogress = downloadedsize * self.PROGRESSBAR_LENGTH // filesize
                    newprogress = newprogress if newprogress < self.PROGRESSBAR_LENGTH else self.PROGRESSBAR_LENGTH
                    if newprogress != progress:
                        print('#'*(newprogress-progress), end='')
                        progress = newprogress
                    f.write(chunk)
            print(' OK')
            return True

    def get_file_iter_r(self, urlpath):
        """Get iter and requests object for non-blocking download."""
        url = self.full_url(urlpath)
        print('get file iter r', url)
        r = requests.get(url, stream=True, **self._reqparams)
        if r.status_code != 200:
            self.error(r, url)
            return None, r
        return r.iter_content(chunk_size=self.CHUNK_SIZE), r
    
    def error(self, r, msg=''):
        """Report access error."""
        print('Error: status code is {}. {}'.format(r.status_code, msg))
