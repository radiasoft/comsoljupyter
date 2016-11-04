from comsoljupyter.web import app
import flask_login
import flask_sqlalchemy
import werkzeug.exceptions

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = flask_sqlalchemy.SQLAlchemy(app)

class User(db.Model, flask_login.UserMixin):
    password = db.Column(db.String(80))
    username = db.Column(db.String(80), primary_key=True)

    def __init__(self, username, password):
        self.password = password
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.username

def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def add_username(username, password):
    u = User(username, password)
    db.session.add(u)
    db.session.commit()
    return u
