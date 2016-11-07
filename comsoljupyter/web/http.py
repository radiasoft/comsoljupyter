from comsoljupyter.web import app, orm

app.secret_key = 'super secret string'  # Change this!

import flask
import flask_login

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

PASS_FORM = '''
<form action="login" method="POST">
    <input type="text" name="username" id="username" placeholder="username" />
    <input type="password" name="password" id="password" placeholder="password" />
    <input type="submit" name="submit" />
</form>
'''

COMSOL_LINK = '''
<p>Logged in as: {0}</p>
<p>Open <a href="/goto-comsol" target="_blank">Comsol</a></p>
'''

@app.route('/goto-comsol')
@flask_login.login_required
def get_comsol_session():
    pass

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
    return COMSOL_LINK.format(flask_login.current_user.username)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@login_manager.user_loader
def user_loader(username):
    return orm.get_user_by_username(username)
