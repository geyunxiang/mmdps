"""Batch get mridata.

Batch get multiple mridata.
All data are from the api server. Use api to access the server.
"""

import os
from ..util.loadsave import load_txt


class BatchGet:
    """Batch get mridata."""
    def __init__(self, api, mriscanstxt, modal, outmainfolder):
        """Construct by api object, mriscanstxt contains mriscans by name_date,
        modal or file name, and download the data to outmainfolder.
        """
        self.api = api
        self.mriscans = load_txt(mriscanstxt)
        self.outmainfolder = outmainfolder
        self.modal = modal

    def proc_mriscan(self, mriscan):
        """Download one mriscan."""
        mriscand = self.api.get_mriscan_by_namedate(mriscan)
        outfolder = os.path.join(self.outmainfolder, mriscan)
        outfilepath = os.path.join(outfolder, self.modal)
        if mriscand:
            mriscan_id = mriscand['id']
            self.api.download('/mriscans/{}/get/{}'.format(mriscan_id, self.modal),
                              outfilepath)
        
    def run(self):
        """Begin download."""
        for mriscan in self.mriscans:
            self.proc_mriscan(mriscan)
            
