from mmdps.dms import storage


if __name__ == '__main__':
    auth = ('mmdpdata', '123')
    urlbase = 'https://166.111.66.184/'
    datastore = storage.HTTPStorage(urlbase, auth)
    datastore.get_file_progress('MRIData/chenyifan_20150923/BOLD.nii.gz', 'testget/BOLD.nii.gz')

    
