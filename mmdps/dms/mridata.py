"""Access mridata storage and featuredata storage.

The mridata storage and featuredata storage are both served by a static server.
"""

# from . import storage
import storage

# Modal to file mapping
ModalFileDict = {
    'T1': 'T1.nii.gz',
    'T2': 'T2.nii.gz',
    'BOLD': 'BOLD.nii.gz',
    'DWI': 'DWI.nii.gz'
}


class MRIDataAccessor:
    """Access mridata static server."""
    def __init__(self, urlbase, auth):
        """Specify urlbase and user auth information."""
        self.httpstorage = storage.HTTPStorage(urlbase, auth)

    def build_uri(self, mriscanfolder, modal):
        """Build full uri form scan and modal."""
        modalfile = self.modal_to_file(modal)    
        return 'MRIData/{}/{}'.format(mriscanfolder, modalfile)
    
    def get_iter_r(self, mriscanfolder, modal):
        """Get iter and request object for non-blocking download."""
        uri = self.build_uri(mriscanfolder, modal)
        it, r = self.httpstorage.get_file_iter_r(uri)
        return it, r
    
    def modal_to_file(self, modal):
        """Map modal to file."""
        return ModalFileDict.get(modal, modal)
    
        
class FeatureDataAccessor:
    """Access featuredata static server."""
    def __init__(self, urlbase, auth, featureroot='FeatureData'):
        """Specify urlbase and user auth information, and feature root folder."""
        self.httpstorage = storage.HTTPStorage(urlbase, auth)
        self.featureroot = featureroot

    def build_uri(self, mriscanfolder, filepath):
        """Build feature uri by mriscan and feature file."""
        return '{}/{}/{}'.format(self.featureroot, mriscanfolder, filepath)
    
    def get_iter_r_mriscan(self, mriscanfolder, filepath):
        """Get iter and requests object for non-blocking downloading."""
        uri = self.build_uri(mriscanfolder, filepath)
        it, r = self.httpstorage.get_file_iter_r(uri)
        return it, r
    
