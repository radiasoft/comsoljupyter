import flask

app = flask.Flask(__name__)

import comsoljupyter.web.http
from comsoljupyter.web.orm import db

def run():
    db.create_all()
    app.run()
