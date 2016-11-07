# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from comsoljupyter.web import app
import flask_login
import flask_sqlalchemy
import werkzeug.exceptions

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/comsolapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = flask_sqlalchemy.SQLAlchemy(app)

class ComsolCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class ComsolSession(db.Model):
    credential = db.relationship('ComsolCredentials', backref=db.backref('session', lazy='dynamic'))
    credential_id = db.Column(db.Integer, db.ForeignKey('comsol_credentials.id'),
        unique=True, nullable=False)
    cssessionid = db.Column(db.String(256), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    jsessionid = db.Column(db.String(256), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('session', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    def __init__(self, cssessionid, jsessionid, credential):
        self.jsessionid = jsessionid
        self.cssessionid = cssessionid
        self.credential = credential

class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), unique=True)

    def __init__(self, username, password):
        self.password = password
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.username

def add(obj):
    db.session.add(obj)
    db.session.commit()
    return obj

def get_unused_credentials():
    return ComsolCredentials.query.\
        outerjoin(ComsolSession).\
        filter(ComsolSession.credential_id == None).\
        first()

def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def init():
    db.create_all()
