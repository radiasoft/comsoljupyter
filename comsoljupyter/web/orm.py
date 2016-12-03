# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import comsoljupyter.web
import flask_sqlalchemy
import pickle
import random
import uuid

comsoljupyter.web.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = flask_sqlalchemy.SQLAlchemy(comsoljupyter.web.app)


class ComsolCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    session = db.relationship('ComsolSession',
        back_populates='credential', uselist=False)
    username = db.Column(db.String(256), unique=True, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class ComsolSession(db.Model):
    _cookie_jar_pickle = db.Column(db.Text, nullable=False, unique=False)
    credential=db.relationship('ComsolCredentials', uselist=False,
        back_populates='session')
    credential_id = db.Column(db.Integer, db.ForeignKey('comsol_credentials.id'),
        unique=True, nullable=False)
    cssessionid = db.Column(db.String(256), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    jsessionid = db.Column(db.String(256), nullable=False, unique=True)
    listen_port = db.Column(db.Integer, nullable=False, unique=True)
    rsessionid = db.Column(db.String(256), nullable=False, unique=True)
    user = db.relationship('User', uselist=False, back_populates='session')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True,
        nullable=False)

    def __init__(self, user, cssessionid, jsessionid, credential, cookie_jar):
        random.seed()

        self._cookie_jar_pickle = pickle.dumps(cookie_jar)
        self.credential = credential
        self.cssessionid = cssessionid
        self.jsessionid = jsessionid
        self.listen_port = self._get_random_port()
        self.rsessionid = self._gen_session_id()
        self.user = user

    def __repr__(self):
        return \
'''ComsolSession<
    cssessionid={0.cssessionid},
    jsessionid={0.jsessionid},
    listen_port={0.listen_port}
    rsessionid={0.rsessionid},
    username={0.user.username},
>'''.format(self)

    @staticmethod
    def _gen_session_id():
        return uuid.uuid1().hex

    @staticmethod
    def _get_random_port():
        return random.sample(range(2**16-100, 2**16-1), 1).pop()

    @property
    def cookie_jar(self):
        return pickle.loads(self._cookie_jar_pickle)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session = db.relationship('ComsolSession',
        back_populates='user', uselist=False)
    username = db.Column(db.String(256), unique=True, nullable=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username


def add(obj):
    db.session.add(obj)
    db.session.commit()
    return obj


def cleanup():
    db.session.commit()


def delete(obj):
    db.session.delete(obj)
    db.session.commit()


def get_unused_credentials():
    return ComsolCredentials.query.\
        outerjoin(ComsolSession).\
        filter(ComsolSession.credential_id == None).\
        first()


def get_user_by_username(username):
    u = User.query.filter(User.username == username).first()
    if u is None:
        u = User(username)
        add(u)
    return u


def init(state_path):
    comsoljupyter.web.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/comsolapp.sqlite'.format(state_path)
    db.create_all()
