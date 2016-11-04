from comsoljupyter.web import app, orm

app.secret_key = 'super secret string'  # Change this!

import flask
import flask_login

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(username):
    return orm.get_user_by_username(username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    username = flask.request.form['username']
    password = flask.request.form['password']

    user = user_loader(username)
    if user is not None and user.check_password(password):
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'

@app.route('/create', methods=['GET', 'POST'])
def create():
    if flask.request.method == 'GET':
        return '''
               <form action='create' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    username = flask.request.form['username']
    password = flask.request.form['password']

    orm.add_username(username, password)

    return 'Ok'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.username

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
