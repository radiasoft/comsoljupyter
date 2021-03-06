# -*- coding: utf-8 -*-

"""
:copyright: Copyright (c) 2016 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import flask

app = flask.Flask(__name__)


def cleanup():
    import comsoljupyter.web.orm
    comsoljupyter.web.orm.cleanup()

    import comsoljupyter.web.http
    comsoljupyter.web.http.cleanup()


def init(state_path, jupyterhub_base_url):
    import comsoljupyter.web.orm
    comsoljupyter.web.orm.init(state_path)

    import comsoljupyter.web.http
    comsoljupyter.web.http.init(state_path, jupyterhub_base_url)


def run(port, jupyterhub_base_url, state_path, debug=False):
    init(state_path, jupyterhub_base_url)
    app.run(host='0.0.0.0', port=port, debug=debug)
