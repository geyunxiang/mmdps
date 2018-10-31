from mmdps.dms import apicore


if __name__ == '__main__':
    urlbase = 'http://127.0.0.1:5000/'
    auth = ('mmdpdata', '123')
    api = apicore.ApiCore(urlbase, auth)
    
