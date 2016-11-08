# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter.web import app, orm, twisted, nginx_proxy
from http import HTTPStatus
import comsoljupyter
import datetime

app.secret_key = 'super secret string'  # Change this!

import flask
import flask_login

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

proxy = nginx_proxy.NginxProxy()

PASS_FORM = '''
<form action="login" method="POST">
    <input type="text" name="username" id="username" placeholder="username" />
    <input type="password" name="password" id="password" placeholder="password" />
    <input type="submit" name="submit" />
</form>
'''

COMSOL_LINK = '''
<p>Logged in as: {0}</p>
<p>Open <a href="{1}" target="_blank">Comsol</a></p>
'''

@app.route('/open-comsol')
@flask_login.login_required
def get_comsol_session():
    user = flask_login.current_user

    if user.session is None:
        creds = orm.get_unused_credentials()
        if creds is not None:
            session = twisted.get_comsol_session(user, creds)
            orm.add(session)
        else:
            flask.abort(HTTPStatus.CONFLICT.value)

    # Start Proxy Nginx and return redirect
    proxy.add_session(user.session)

    r = flask.redirect('https://comsol.radiasoft.org:{}'.format(user.session.listen_port))
    r.set_cookie(
        key=comsoljupyter.RSESSIONID,
        value=user.session.rsessionid,
        domain='.radiasoft.org',
    )

    return r

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return PASS_FORM

    username = flask.request.form['username']
    password = flask.request.form['password']

    user = user_loader(username)
    if user is not None and user.check_password(password):
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@app.route('/protected')
@flask_login.login_required
def protected():
    return COMSOL_LINK.format(
        flask_login.current_user.username,
        flask.url_for('get_comsol_session')
    )


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@login_manager.user_loader
def user_loader(username):
    return orm.get_user_by_username(username)
