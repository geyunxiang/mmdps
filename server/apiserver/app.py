from eve import Eve
from eve.auth import BasicAuth, requires_auth
from flask import Response, abort, g, current_app, request
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from mmdps.dms.tables import Base, MRIScan
from mmdps.dms import mridata
import users

class SimpleAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        return users.check_user(username, password)

app = Eve(validator=ValidatorSQL, data=SQL, auth=SimpleAuth)

# bind sqlalchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base

# mridata server
accessor_urlbase = app.config['MY_STORAGE_URLBASE']
accessor_auth = app.config['MY_STORAGE_AUTH']
mridataaccessor = mridata.MRIDataAccessor(accessor_urlbase, accessor_auth)

# feature server
accessor_feature_urlbase = app.config['MY_FEATURE_STORAGE_URLBASE']
accessor_feature_auth = app.config['MY_FEATURE_STORAGE_AUTH']
accessor_feature_root = app.config['MY_FEATURE_ROOT']
featureaccessor = mridata.FeatureDataAccessor(accessor_feature_urlbase, accessor_feature_auth, accessor_feature_root)

@app.route('/mriscans/<_id>/get/<_modal>')
@requires_auth('mriscans')
def get_mriscan_data(_id, _modal):
    username = request.authorization.username
    print(username, _id, _modal)
    mriscan = db.session.query(MRIScan).get(_id)
    folder = mriscan.get_folder()
    if not users.check_fetch_data(username, folder, _modal):
        abort(403)
        return 
    it, r = mridataaccessor.get_iter_r(folder, _modal)
    if r.status_code != 200:
        abort(404)
        return
    return Response(it, content_type=r.headers['Content-Type'])

@app.route('/features/mriscans/<_id>/<path:file>')
@requires_auth('mriscans')
def get_mriscan_feature_data(_id, file):
    username = request.authorization.username
    print(username, _id, file)
    mriscan = db.session.query(MRIScan).get(_id)
    folder = mriscan.get_folder()
    it, r = featureaccessor.get_iter_r_mriscan(folder, file)
    if r.status_code != 200:
        abort(404)
        return
    return Response(it, content_type=r.headers['Content-Type'])


    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    
