

users = {
    'mmdpdata': '123',
    't1only': '123',
    'guest': '123'
}

def check_user(username, password):
    if users.get(username) == password:
        return True
    return False

def check_fetch_data(username, folder, modal):
    if username == 'mmdpdata':
        return True
    elif username == 'guest':
        return False
    elif username == 't1only':
        if modal not in ['T1', 'T1.nii.gz']:
            return False
        return True
    else:
        return False


