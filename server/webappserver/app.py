import flask
import flask_login

import users
from mmdps import rootconfig
from mmdps.dms import apicore
from mmdps.util import clock
import features

# app
app = flask.Flask(__name__)
app.secret_key = 'zlijijjefs'

# flask_login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users.users:
        return
    user = User()
    user.id = username
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if users.check_user(username, password):
            user = User()
            user.id = username
            flask_login.login_user(user)
            auth = (username, password)
            flask.session['my_api_args'] = [rootconfig.server.api, auth]
            return flask.redirect(flask.url_for('index'))
        flask.flash('Username or password not valid.')
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flask.flash('You logged out just now.')
    return flask.redirect(flask.url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(flask.url_for('login'))


@app.route('/')
@flask_login.login_required
def index():
    return flask.render_template('index.html')

def getapi():
    return apicore.ApiCore(*flask.session['my_api_args'])

@app.route('/info', methods=['GET', 'POST'])
@flask_login.login_required
def info():
    api = getapi()
    if flask.request.method == 'POST':
        filterstr = flask.request.form['filterstr']
        peopleres = api.getdict('/people?where={{"name":"like(\\"%{}%\\")"}}&projection={{"name":1}}'.format(filterstr))
    else:
        peopleres = api.getdict('/people?projection={"name":1}')
    people = peopleres['_items']
    return flask.render_template('info.html', people=people)

@app.route('/info/<int:person_id>')
@flask_login.login_required
def info_person(person_id):
    api = getapi()
    person = api.getobjdict('people', person_id)
    mriscans = [api.getobjdict('mriscans', mriscan_id) for mriscan_id in person['mriscans']]
    groups = [api.getobjdict('groups', group_id) for group_id in person['groups']]
    motionscores = [api.getobjdict('motionscores', motionscore_id) for motionscore_id in person['motionscores']]
    strokescores = [api.getobjdict('strokescores', strokescore_id) for strokescore_id in person['strokescores']]
    return flask.render_template('info_person.html', person=person, mriscans=mriscans, groups=groups, motionscores=motionscores, strokescores=strokescores)

@app.route('/mriscans/<int:mriscan_id>/get/<modal>')
@flask_login.login_required
def get_mriscan_data(mriscan_id, modal):
    api = getapi()
    it, r = api.get_mriscan_data_iter_r(mriscan_id, modal)
    if r.status_code != 200:
        flask.abort(r.status_code)
        return
    return flask.Response(it, content_type=r.headers['Content-Type'])
    
def build_feature_url(mriscan_id, atlasname, featurename):
    api = getapi()
    url = api.feature_full_url('/mriscans/{}/{}/{}'.format(mriscan_id, atlasname, featurename))
    return url

@app.route('/result')
@flask_login.login_required
def result():
    return flask.render_template('result.html')

@app.route('/result/mriscans/<int:mriscan_id>')
@flask_login.login_required
def result_mriscan(mriscan_id):
    api = getapi()
    namedate = api.get_namedate_by_mriscanid(mriscan_id)
    featuredict = features.Features
    atlases = features.Atlases
    
    return flask.render_template('result_mriscan.html', namedate=namedate, mriscan_id=mriscan_id,
                                 fea=featuredict, atlases=atlases, build_feature_url=build_feature_url)




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004, debug=True)
